"""Region selection and construction of the hourly balancing-authority panel.

Outputs (data/processed/):
  panel.parquet      long panel: region, time_utc (hour-ending), target, x_input, eval_ok,
                     reported, ba_forecast, imputation_code
  regions.csv        selected regions with metadata and the selection statistics

Leakage notes
-------------
* ``target`` is PUDL's screened/imputed demand. It is used only as the training label and,
  restricted to ``eval_ok`` hours (no PUDL flag, i.e. the reported value was retained), as
  the evaluation label. Imputed hours are never scored.
* ``x_input`` (the series models see as lagged inputs) is built from the *reported* demand
  with a purely causal screen (each decision uses only past values), so no future
  information enters the features. PUDL's flags are not used for inputs because the
  PUDL screening uses two-sided windows and whole-series statistics.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .common import DATA_PROCESSED, DATA_RAW, get_logger, load_config

log = get_logger("preprocess")


def load_raw(cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    ops = pd.read_parquet(DATA_RAW / "out_eia930__hourly_operations.parquet")
    bas = pd.read_parquet(DATA_RAW / "core_eia__codes_balancing_authorities.parquet")
    start, end = pd.Timestamp(cfg["data"]["start_utc"]), pd.Timestamp(cfg["data"]["end_utc"])
    ops = ops[(ops.datetime_utc >= start) & (ops.datetime_utc <= end)].copy()
    ops["balancing_authority_code_eia"] = ops["balancing_authority_code_eia"].astype(str)
    return ops, bas


def region_statistics(ops: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    start, end = pd.Timestamp(cfg["data"]["start_utc"]), pd.Timestamp(cfg["data"]["end_utc"])
    n_hours = int((end - start) / pd.Timedelta("1h")) + 1
    g = ops.groupby("balancing_authority_code_eia", observed=True)
    code = ops["demand_imputed_pudl_mwh_imputation_code"].astype(object)
    ops = ops.assign(_flag=code.notna(), _bad=(code == "bad_year"), _nonpos=ops.demand_reported_mwh <= 0)
    g = ops.groupby("balancing_authority_code_eia", observed=True)
    st = pd.DataFrame(
        {
            "rows": g.size(),
            "expected_hours": n_hours,
            "duplicate_timestamps": g.datetime_utc.apply(lambda s: int(s.duplicated().sum())),
            "reported_coverage": g.demand_reported_mwh.count() / n_hours,
            "flagged_share": g._flag.mean(),
            "bad_year_hours": g._bad.sum(),
            "nonpositive_reported_hours": g._nonpos.sum(),
            "target_coverage": g.demand_imputed_pudl_mwh.count() / n_hours,
            "ba_forecast_coverage": g.demand_forecast_mwh.count() / n_hours,
            "mean_demand_mw": g.demand_imputed_pudl_mwh.mean(),
            "first_utc": g.datetime_utc.min(),
            "last_utc": g.datetime_utc.max(),
        }
    )
    st.index.name = "region"
    return st


def select_regions(stats: pd.DataFrame, bas: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    rs = cfg["region_selection"]
    meta = bas.set_index("code")[
        ["label", "balancing_authority_region_code_eia", "report_timezone", "is_generation_only",
         "interconnect_code_eia", "balancing_authority_retirement_date"]
    ]
    df = stats.join(meta, how="left")
    active_until = pd.Timestamp(rs["must_be_active_until"])
    retire = pd.to_datetime(df.balancing_authority_retirement_date)
    reasons = pd.Series("", index=df.index)

    def add(mask, why):
        reasons[mask] = reasons[mask] + why + ";"

    if rs["exclude_generation_only"]:
        add(df.is_generation_only.fillna(False).astype(bool), "generation_only")
    add(~df.interconnect_code_eia.isin(rs["interconnects"]), "interconnect")
    add(retire.notna() & (retire < active_until), "retired")
    add(df.reported_coverage < rs["min_reported_coverage"], "coverage")
    add(df.flagged_share > rs["max_flagged_share"], "flagged_share")
    if not rs["allow_bad_year"]:
        add(df.bad_year_hours > 0, "bad_year")
    add(~(df.mean_demand_mw >= rs["min_mean_demand_mw"]), "small")
    add(df.report_timezone.isna(), "no_timezone")
    df["exclusion_reasons"] = reasons
    df["selected"] = reasons == ""
    return df


def causal_clean(x: pd.Series, cfg: dict) -> pd.Series:
    """Screen a reported series using past information only."""
    ic = cfg["input_cleaning"]
    x = x.astype(float).copy()
    if ic["nonpositive_to_nan"]:
        x[x <= 0] = np.nan
    med = x.shift(1).rolling(ic["spike_window_h"], min_periods=ic["spike_min_periods"]).median()
    spike = (x > ic["spike_high_ratio"] * med) | (x < ic["spike_low_ratio"] * med)
    x[spike.fillna(False)] = np.nan
    return x


def build_panel(ops: pd.DataFrame, regions: list[str], cfg: dict) -> pd.DataFrame:
    start, end = pd.Timestamp(cfg["data"]["start_utc"]), pd.Timestamp(cfg["data"]["end_utc"])
    idx = pd.date_range(start, end, freq="h")
    parts = []
    for r in regions:
        d = ops[ops.balancing_authority_code_eia == r].set_index("datetime_utc").sort_index()
        d = d[~d.index.duplicated(keep="first")].reindex(idx)
        code = d["demand_imputed_pudl_mwh_imputation_code"].astype(object)
        out = pd.DataFrame(
            {
                "region": r,
                "time_utc": idx,
                "reported": d["demand_reported_mwh"].to_numpy(float),
                "target": d["demand_imputed_pudl_mwh"].to_numpy(float),
                "ba_forecast": d["demand_forecast_mwh"].to_numpy(float),
                "imputation_code": code.to_numpy(),
            }
        )
        out["eval_ok"] = code.isna().to_numpy() & np.isfinite(out["target"].to_numpy())
        out["x_input"] = causal_clean(pd.Series(out["reported"].to_numpy()), cfg).to_numpy()
        parts.append(out)
    panel = pd.concat(parts, ignore_index=True)
    panel["region"] = panel["region"].astype("category")
    return panel


def main() -> None:
    cfg = load_config()
    ops, bas = load_raw(cfg)
    stats = region_statistics(ops, cfg)
    sel = select_regions(stats, bas, cfg)
    sel.to_csv(DATA_PROCESSED / "regions_all.csv")
    regions = sorted(sel.index[sel.selected])
    log.info("selected %d regions: %s", len(regions), regions)
    panel = build_panel(ops, regions, cfg)
    panel.to_parquet(DATA_PROCESSED / "panel.parquet", index=False)
    sel.loc[regions].to_csv(DATA_PROCESSED / "regions.csv")
    log.info("panel rows=%d, eval_ok share=%.4f, input NaN share=%.4f",
             len(panel), panel.eval_ok.mean(), panel.x_input.isna().mean())


if __name__ == "__main__":
    main()
