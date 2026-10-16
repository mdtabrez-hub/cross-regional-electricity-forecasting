"""Export every number quoted in the manuscript from saved outputs.

Writes results/manuscript_numbers.json with keys such as
``point.h24.LGB_G_IN.nMAE_median`` (percent, 2 dp). Percent-type metrics are multiplied by
100. Each key is derived mechanically from a CSV in results/metrics or results/logs, which
lets the QA script re-derive and cross-check every quoted value.

Usage: python -m src.manuscript_numbers
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .common import DATA_META, DATA_PROCESSED, LOG_DIR, METRIC_DIR, RESULTS

PCT = ("nMAE", "nRMSE", "MAPE", "bias_pct", "coverage", "width", "interval_score", "mean_abs_cov_dev",
       "share", "median_rel_change", "rel_ci", "pinball", "input_missing")


def fmt(col: str, v):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "n/a"
    if isinstance(v, (bool, np.bool_)):
        return str(bool(v))
    if isinstance(v, (int, np.integer)):
        return f"{int(v):,}"
    if col.startswith("p") and (col == "p" or col.startswith("p_")):
        return f"{v:.2g}" if v >= 1e-4 else "<0.0001"
    if any(col.startswith(k) or k in col for k in PCT):
        return f"{100 * v:.1f}" if ("share" in col or "rel" in col or "coverage" in col) else f"{100 * v:.2f}"
    if "MASE" in col:
        return f"{v:.3f}"
    if "seconds" in col or col.endswith("_s"):
        return f"{v:.1f}"
    return f"{v:.3g}"


def flatten(df: pd.DataFrame, prefix: str, keys: list[str], out: dict):
    for _, r in df.iterrows():
        ident = ".".join(f"h{int(r[k])}" if k == "h" else str(r[k]).replace(" ", "_") for k in keys)
        for c in df.columns:
            if c in keys:
                continue
            out[f"{prefix}.{ident}.{c}"] = fmt(c, r[c])


def main():
    N = {}
    m = METRIC_DIR
    meta = json.load(open(DATA_META / "dataset_metadata.json"))
    reg = pd.read_csv(DATA_PROCESSED / "regions.csv", index_col=0)
    allreg = pd.read_csv(DATA_PROCESSED / "regions_all.csv", index_col=0)
    N["data.n_regions"] = str(meta["n_selected_regions"])
    N["data.n_bas_raw"] = str(meta["raw_table_bas"])
    N["data.n_bas_window"] = str(len(allreg))
    N["data.panel_rows"] = f"{meta['panel_rows']:,}"
    N["data.hours_per_region"] = f"{meta['study_hours_per_region']:,}"
    N["data.eval_ok_pct"] = f"{100 * meta['panel_eval_ok_share']:.2f}"
    N["data.flagged_pct"] = f"{100 * (1 - meta['panel_eval_ok_share']):.2f}"
    N["data.input_missing_pct"] = f"{100 * meta['panel_input_missing_share']:.2f}"
    N["data.min_mean_mw"] = f"{reg.mean_demand_mw.min():,.0f}"
    N["data.max_mean_mw"] = f"{reg.mean_demand_mw.max():,.0f}"
    N["data.min_mean_ba"] = reg.mean_demand_mw.idxmin()
    N["data.max_mean_ba"] = reg.mean_demand_mw.idxmax()
    N["data.ratio_max_min"] = f"{reg.mean_demand_mw.max() / reg.mean_demand_mw.min():,.0f}"
    for ic in ("eastern", "western", "ercot"):
        N[f"data.n_{ic}"] = str(int((reg.interconnect_code_eia == ic).sum()))
    N["data.n_excluded"] = str(int((~allreg.selected).sum()))

    files = [
        ("point_metrics_summary.csv", "point", ["h", "method"]),
        ("temporal_metrics_summary.csv", "temporal", ["h", "by", "period", "method"]),
        ("ba_dayahead_summary.csv", "ba", ["h", "method"]),
        ("adaptation_metrics_summary.csv", "adapt", ["h", "method"]),
        ("refit_metrics_summary.csv", "refit", ["h", "method"]),
        ("missing_data_summary.csv", "missing", ["h", "scenario", "strategy", "method"]),
        ("ablation_results.csv", "ablation", ["method"]),
        ("pinball_summary.csv", "pinball", ["h", "setting"]),
        ("block_bootstrap_summary.csv", "block", ["h", "method_a", "method_b"]),
    ]
    for fname, pref, keys in files:
        f = m / fname
        if f.exists():
            flatten(pd.read_csv(f), pref, keys, N)
    f = m / "probabilistic_summary.csv"
    if f.exists():
        p = pd.read_csv(f)
        p["nominal"] = (100 * (1 - p.alpha)).round().astype(int)
        flatten(p.drop(columns="alpha"), "prob", ["h", "setting", "nominal", "method", "period"], N)
    f = m / "aci_capped_share_by_region.csv"
    if f.exists():
        a = pd.read_csv(f)
        for (h, st, al, me), g in a.groupby(["h", "setting", "alpha", "method"]):
            N[f"acicap.h{h}.{st}.{int(round(100 * (1 - al)))}.{me}"] = f"{100 * g.capped_share.mean():.1f}"
    f = m / "aci_gamma_selected_on_validation.csv"
    if f.exists():
        for _, r in pd.read_csv(f).iterrows():
            N[f"gamma.h{int(r.h)}.{int(round(100 * (1 - r.alpha)))}"] = f"{r.gamma_selected:g}"
    for fname, pref in (("paired_tests_point.csv", "test"), ("paired_tests_adaptation.csv", "testadapt"),
                        ("paired_tests_refit.csv", "testrefit")):
        f = m / fname
        if f.exists():
            t = pd.read_csv(f)
            flatten(t, pref, ["h", "metric", "method_a", "method_b"], N)
    c = LOG_DIR / "compute_costs_point.csv"
    if c.exists():
        cc = pd.read_csv(c)
        cc["family"] = cc.model.str.replace(r"_q\d\d$", "_Q", regex=True)
        g = cc.groupby(["family", "h"]).agg(fit_seconds=("fit_seconds", "mean"), size_mb=("size_bytes", "mean"),
                                           inference_us=("inference_seconds", "sum"),
                                           n_inf=("n_inference_rows", "sum"), peak_rss_mb=("peak_rss_mb", "max")).reset_index()
        for _, r in g.iterrows():
            k = f"compute.h{int(r.h)}.{r.family.replace(' ', '_').replace('(', '').replace(')', '')}"
            N[f"{k}.fit_seconds"] = f"{r.fit_seconds:.1f}"
            N[f"{k}.size_mb"] = "n/a" if not np.isfinite(r.size_mb) else f"{r.size_mb / 1e6:.2f}"
            N[f"{k}.inference_us"] = "n/a" if not (r.n_inf > 0) else f"{1e6 * r.inference_us / r.n_inf:.2f}"
            N[f"{k}.peak_rss_mb"] = f"{r.peak_rss_mb:.0f}"
    a = LOG_DIR / "compute_costs_adapt.csv"
    if a.exists():
        aa = pd.read_csv(a)
        for _, r in aa.iterrows():
            N[f"compute.h{int(r.h)}.{r.model}.fit_seconds_per_region"] = f"{r.fit_seconds_per_region:.2f}"
    f = m / "missing_data_summary.csv"
    if f.exists():
        N["missing.min_scored_pct"] = f"{100 * pd.read_csv(f).min_coverage_of_eval_hours.min():.1f}"
    f = m / "ablation_results.csv"
    if f.exists():
        ab = pd.read_csv(f)
        pool = ab[ab.method.str.startswith("pool_")].copy()
        pool["n"] = pool.method.str.extract(r"pool_(\d+)_")[0].astype(int)
        for n, g in pool.groupby("n"):
            N[f"ablationpool.{n}.nMAE_median"] = f"{100 * g.nMAE_median.mean():.2f}"
            N[f"ablationpool.{n}.nMAE_min"] = f"{100 * g.nMAE_median.min():.2f}"
            N[f"ablationpool.{n}.nMAE_max"] = f"{100 * g.nMAE_median.max():.2f}"
    # derived: share of BAs where unseen-region model is worse than in-region (h=24)
    pr = m / "point_metrics_by_region.csv"
    if pr.exists():
        d = pd.read_csv(pr)
        for h in sorted(d.h.unique()):
            piv = d[d.h == h].pivot(index="region", columns="method", values="nMAE")
            gap = piv.LGB_G_LRO / piv.LGB_G_IN - 1
            N[f"derived.h{h}.gap_max_pct"] = f"{100 * gap.max():.1f}"
            N[f"derived.h{h}.gap_max_ba"] = gap.idxmax()
            N[f"derived.h{h}.gap_min_pct"] = f"{100 * gap.min():.1f}"
            N[f"derived.h{h}.n_lro_worse"] = str(int((gap > 0).sum()))
            N[f"derived.h{h}.n_local_better_than_global"] = str(int((piv.LGB_L < piv.LGB_G_IN).sum()))
            N[f"derived.h{h}.worst_ba_lro"] = piv.LGB_G_LRO.idxmax()
            N[f"derived.h{h}.worst_ba_lro_nmae"] = f"{100 * piv.LGB_G_LRO.max():.2f}"
            N[f"derived.h{h}.best_ba_lro"] = piv.LGB_G_LRO.idxmin()
            N[f"derived.h{h}.best_ba_lro_nmae"] = f"{100 * piv.LGB_G_LRO.min():.2f}"
            corr = np.corrcoef(np.log(reg.loc[gap.index, "mean_demand_mw"]), gap)[0, 1]
            N[f"derived.h{h}.corr_gap_logsize"] = f"{corr:.2f}"
    json.dump(N, open(RESULTS / "manuscript_numbers.json", "w"), indent=1, sort_keys=True)
    print(f"{len(N)} numbers exported")


if __name__ == "__main__":
    main()
