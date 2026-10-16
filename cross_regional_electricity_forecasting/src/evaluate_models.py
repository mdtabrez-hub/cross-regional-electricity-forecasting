"""Evaluation of saved predictions: point, adaptation, temporal shift, probabilistic.

Usage: python -m src.evaluate_models
Outputs: results/metrics/*.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import metrics as M
from .common import DATA_PROCESSED, METRIC_DIR, PRED_DIR, get_logger, load_config, save_json
from .conformal import aci_intervals, conformal_quantile, cqr_scores, scp_scores
from .stats import compare_methods, moving_block_bootstrap_mean

log = get_logger("evaluate")

POINT_METHODS = ["SN24", "SN168", "PERS", "RIDGE_G_IN", "RIDGE_G_LRO", "LGB_L", "LGB_G_IN", "LGB_G_LRO"]
RENAME = {"seasonal_naive_24": "SN24", "seasonal_naive_168": "SN168", "persistence": "PERS", "ba_forecast": "BA_DA"}
SEASON = {12: "DJF", 1: "DJF", 2: "DJF", 3: "MAM", 4: "MAM", 5: "MAM", 6: "JJA", 7: "JJA", 8: "JJA",
          9: "SON", 10: "SON", 11: "SON"}


def mase_scales(cfg) -> dict[str, float]:
    panel = pd.read_parquet(DATA_PROCESSED / "panel.parquet")
    sp = cfg["splits"]["train"]
    tr = panel[(panel.time_utc >= sp[0]) & (panel.time_utc <= sp[1])]
    out = {}
    for r, d in tr.groupby("region", observed=True):
        y = d.sort_values("time_utc").target.where(d.eval_ok).to_numpy(float)
        out[str(r)] = M.seasonal_naive_scale(y, 24)
    return out


def per_region_metrics(df: pd.DataFrame, methods: list[str], scales: dict, by: list[str] | None = None) -> pd.DataFrame:
    rows = []
    keys = ["region"] + (by or [])
    for key, d in df.groupby(keys, observed=True):
        key = key if isinstance(key, tuple) else (key,)
        y = d.y.to_numpy()
        for m in methods:
            row = dict(zip(keys, key))
            row.update(method=m, **M.point_metrics(y, d[m].to_numpy(), scales[str(key[0])]))
            rows.append(row)
    return pd.DataFrame(rows)


def summarise(pr: pd.DataFrame, group: list[str], metrics=("nMAE", "nRMSE", "MASE", "MAPE", "bias_pct")) -> pd.DataFrame:
    agg = {}
    for m in metrics:
        agg[f"{m}_median"] = (m, "median")
        agg[f"{m}_mean"] = (m, "mean")
        agg[f"{m}_q25"] = (m, lambda s: s.quantile(0.25))
        agg[f"{m}_q75"] = (m, lambda s: s.quantile(0.75))
    agg["n_regions"] = ("region", "nunique")
    agg["n_hours_total"] = ("n", "sum")
    return pr.groupby(group, observed=True).agg(**agg).reset_index()


def common_mask(df: pd.DataFrame, methods: list[str]) -> pd.Series:
    m = df.eval_ok & np.isfinite(df.y)
    for c in methods:
        m &= np.isfinite(df[c])
    return m


# --------------------------------------------------------------------------- point + temporal
def evaluate_point(cfg, scales, horizons):
    allpr, alltime, ba_rows, val_rows, block_rows = [], [], [], [], []
    for h in horizons:
        p = pd.read_parquet(PRED_DIR / f"point_h{h}.parquet").rename(columns=RENAME)
        te = p[p.split == "test"].copy()
        mask = common_mask(te, POINT_METHODS)
        log.info("h=%d test rows=%d common-mask rows=%d (%.4f)", h, len(te), mask.sum(), mask.mean())
        t = te[mask].copy()
        pr = per_region_metrics(t, POINT_METHODS, scales)
        pr["h"] = h
        allpr.append(pr)
        # temporal: by year and season
        start = t.time_utc - pd.Timedelta("1h")  # hour-ending timestamps -> interval start
        t["year"] = start.dt.year
        t["season"] = start.dt.month.map(SEASON)
        for by in (["year"], ["season"]):
            q = per_region_metrics(t, ["SN24", "LGB_L", "LGB_G_IN", "LGB_G_LRO"], scales, by)
            q["h"], q["by"] = h, by[0]
            q = q.rename(columns={by[0]: "period"})
            alltime.append(q)
        # validation-year error of the same models (VAL-ES was used for early stopping -> optimistic)
        v = p[p.split.isin(["val_es", "val_cal"])]
        v = v[common_mask(v, POINT_METHODS)]
        q = per_region_metrics(v, ["SN24", "LGB_L", "LGB_G_IN", "LGB_G_LRO"], scales)
        q["h"], q["period"], q["by"] = h, "2023 (validation)", "year"
        alltime.append(q)
        # BA day-ahead reference on hours where it exists
        bm = mask & np.isfinite(te.BA_DA) & (te.BA_DA > 0)
        b = te[bm]
        q = per_region_metrics(b, ["BA_DA", "LGB_G_IN", "LGB_G_LRO", "SN24"], scales)
        q["h"] = h
        ba_rows.append(q)
        # moving-block bootstrap of hourly absolute-error differentials per region
        for a_m, b_m in [("LGB_G_LRO", "LGB_G_IN"), ("LGB_G_IN", "LGB_L"), ("LGB_G_LRO", "LGB_L"),
                         ("LGB_G_LRO", "SN24"), ("LGB_G_IN", "RIDGE_G_IN")]:
            for r, d in t.sort_values("time_utc").groupby("region", observed=True):
                diff = (np.abs(d.y - d[a_m]) - np.abs(d.y - d[b_m])).to_numpy() / d.y.mean()
                mean, lo, hi = moving_block_bootstrap_mean(diff, cfg["statistics"]["block_length_h"],
                                                           cfg["statistics"]["bootstrap_reps"], cfg["seed"])
                block_rows.append({"h": h, "method_a": a_m, "method_b": b_m, "region": r, "mean_diff_nmae": mean,
                                   "ci_lo": lo, "ci_hi": hi, "a_better_sig": hi < 0, "b_better_sig": lo > 0})
    pr = pd.concat(allpr, ignore_index=True)
    pr.to_csv(METRIC_DIR / "point_metrics_by_region.csv", index=False)
    summarise(pr, ["h", "method"]).to_csv(METRIC_DIR / "point_metrics_summary.csv", index=False)
    tm = pd.concat(alltime, ignore_index=True)
    tm.to_csv(METRIC_DIR / "temporal_metrics_by_region.csv", index=False)
    summarise(tm, ["h", "by", "period", "method"]).to_csv(METRIC_DIR / "temporal_metrics_summary.csv", index=False)
    ba = pd.concat(ba_rows, ignore_index=True)
    ba.to_csv(METRIC_DIR / "ba_dayahead_by_region.csv", index=False)
    summarise(ba, ["h", "method"]).to_csv(METRIC_DIR / "ba_dayahead_summary.csv", index=False)
    blk = pd.DataFrame(block_rows)
    blk.to_csv(METRIC_DIR / "block_bootstrap_by_region.csv", index=False)
    blk.groupby(["h", "method_a", "method_b"]).agg(
        n_regions=("region", "size"), share_a_better_sig=("a_better_sig", "mean"),
        share_b_better_sig=("b_better_sig", "mean"), median_mean_diff=("mean_diff_nmae", "median")
    ).reset_index().to_csv(METRIC_DIR / "block_bootstrap_summary.csv", index=False)
    # paired tests across regions
    pairs = [("LGB_G_LRO", "LGB_G_IN"), ("LGB_G_IN", "LGB_L"), ("LGB_G_LRO", "LGB_L"), ("LGB_G_LRO", "SN24"),
             ("LGB_G_IN", "RIDGE_G_IN"), ("RIDGE_G_LRO", "RIDGE_G_IN"), ("LGB_G_LRO", "RIDGE_G_LRO"),
             ("LGB_L", "SN24")]
    tests = []
    for h in horizons:
        d = pr[pr.h == h]
        for metric in ("nMAE", "MASE", "nRMSE"):
            tt = compare_methods(d, metric, pairs, cfg["statistics"]["bootstrap_reps"], cfg["seed"])
            tt["h"] = h
            tests.append(tt)
    tests = pd.concat(tests, ignore_index=True)
    tests["p_holm_all"] = _holm_all(tests)
    tests.to_csv(METRIC_DIR / "paired_tests_point.csv", index=False)
    return pr


def _holm_all(df):
    from .stats import holm
    return holm(df["p"].fillna(1.0).to_numpy())


# --------------------------------------------------------------------------- adaptation
def evaluate_adapt(cfg, scales, horizons):
    rows, tests = [], []
    for h in horizons:
        f = PRED_DIR / f"adapt_h{h}.parquet"
        if not f.exists():
            continue
        a = pd.read_parquet(f)
        p = pd.read_parquet(PRED_DIR / f"point_h{h}.parquet")
        p = p[p.split == "test"][["region", "time_utc", "LGB_L", "LGB_G_IN", "LGB_G_LRO", "seasonal_naive_24"]]
        d = a.merge(p, on=["region", "time_utc"], how="left").rename(columns=RENAME)
        methods = ["SN24", "LGB_G_LRO"] + [c for c in d.columns if c.startswith(("LGB_L_k", "LGB_FT_k"))] + ["LGB_L", "LGB_G_IN"]
        d = d[common_mask(d, methods)]
        pr = per_region_metrics(d, methods, scales)
        pr["h"] = h
        rows.append(pr)
        pairs = [(f"LGB_FT_k{k}", "LGB_G_LRO") for k in cfg["adaptation"]["weeks"]] + \
                [(f"LGB_FT_k{k}", f"LGB_L_k{k}") for k in cfg["adaptation"]["weeks"]] + \
                [(f"LGB_L_k{k}", "LGB_G_LRO") for k in cfg["adaptation"]["weeks"]]
        tt = compare_methods(pr, "nMAE", pairs, cfg["statistics"]["bootstrap_reps"], cfg["seed"])
        tt["h"] = h
        tests.append(tt)
    if rows:
        pr = pd.concat(rows, ignore_index=True)
        pr.to_csv(METRIC_DIR / "adaptation_metrics_by_region.csv", index=False)
        summarise(pr, ["h", "method"]).to_csv(METRIC_DIR / "adaptation_metrics_summary.csv", index=False)
        pd.concat(tests, ignore_index=True).to_csv(METRIC_DIR / "paired_tests_adaptation.csv", index=False)


def evaluate_refit(cfg, scales, horizons):
    rows = []
    for h in horizons:
        f = PRED_DIR / f"refit_h{h}.parquet"
        if not f.exists():
            continue
        r = pd.read_parquet(f)
        p = pd.read_parquet(PRED_DIR / f"point_h{h}.parquet")
        p = p[p.split == "test"][["region", "time_utc", "LGB_L", "LGB_G_IN", "LGB_G_LRO"]]
        d = r.merge(p, on=["region", "time_utc"], how="left").rename(columns=RENAME)
        methods = ["SN24", "LGB_G_IN", "LGB_G_IN_refit", "LGB_L", "LGB_L_refit", "LGB_G_LRO"]
        d = d[common_mask(d, methods)]
        pr = per_region_metrics(d, methods, scales)
        pr["h"] = h
        rows.append(pr)
    if rows:
        pr = pd.concat(rows, ignore_index=True)
        pr.to_csv(METRIC_DIR / "refit_metrics_by_region.csv", index=False)
        summarise(pr, ["h", "method"]).to_csv(METRIC_DIR / "refit_metrics_summary.csv", index=False)
        tests = []
        for h in pr.h.unique():
            tt = compare_methods(pr[pr.h == h], "nMAE", [("LGB_G_IN_refit", "LGB_G_IN"), ("LGB_L_refit", "LGB_L")],
                                 cfg["statistics"]["bootstrap_reps"], cfg["seed"])
            tt["h"] = h
            tests.append(tt)
        pd.concat(tests, ignore_index=True).to_csv(METRIC_DIR / "paired_tests_refit.csv", index=False)


# --------------------------------------------------------------------------- probabilistic
def _interval_rows(d, lo, hi, alpha, label, h, setting):
    rows = []
    tmp = d.assign(lo=lo, hi=hi)
    start = tmp.time_utc - pd.Timedelta("1h")  # hour-ending timestamps -> interval start
    tmp["year"] = start.dt.year
    tmp["month"] = start.dt.to_period("M").astype(str)
    for r, g in tmp.groupby("region", observed=True):
        y = g.y.to_numpy()
        ybar = y.mean()
        base = {"region": r, "method": label, "setting": setting, "h": h, "alpha": alpha}
        rows.append({**base, "period": "all", "coverage": M.coverage(y, g.lo, g.hi),
                     "width_norm": float(np.mean(g.hi - g.lo) / ybar),
                     "interval_score_norm": M.interval_score(y, g.lo.to_numpy(), g.hi.to_numpy(), alpha) / ybar,
                     "n": len(g)})
        for yr, gy in g.groupby("year"):
            rows.append({**base, "period": str(yr), "coverage": M.coverage(gy.y, gy.lo, gy.hi),
                         "width_norm": float(np.mean(gy.hi - gy.lo) / ybar),
                         "interval_score_norm": M.interval_score(gy.y.to_numpy(), gy.lo.to_numpy(), gy.hi.to_numpy(), alpha) / ybar,
                         "n": len(gy)})
    # monthly coverage pooled over regions (for drift plots)
    monthly = tmp.groupby("month").apply(lambda g: M.coverage(g.y, g.lo, g.hi), include_groups=False)
    mrows = [{"method": label, "setting": setting, "h": h, "alpha": alpha, "month": k, "coverage": v}
             for k, v in monthly.items()]
    return rows, mrows


def evaluate_probabilistic(cfg, horizons):
    rows, mrows, pin_rows = [], [], []
    test_start = pd.Timestamp(cfg["splits"]["test"][0])
    gamma = cfg["probabilistic"]["aci_gamma"]
    tw = cfg["probabilistic"]["target_calibration_weeks"]
    for h in horizons:
        p = pd.read_parquet(PRED_DIR / f"point_h{h}.parquet")
        if "LGB_G_IN_q05" not in p:
            continue
        cal_lro = pd.read_parquet(PRED_DIR / f"lro_source_calibration_h{h}.parquet")
        for setting, pref in (("in-region", "LGB_G_IN"), ("unseen-region", "LGB_G_LRO")):
            zhat = p[pref] / p.scale
            zq = {q: p[f"{pref}_q{q:02d}"] / p.scale for q in (5, 25, 75, 95)}
            te_m = (p.split == "test") & p.eval_ok & np.isfinite(p.y) & np.isfinite(zhat)
            for q in (5, 25, 75, 95):
                te_m &= np.isfinite(zq[q])
            te = p[te_m]
            # pinball (quantile grid, tau=0.5 from the L1 point model), normalised by regional mean
            for r, g in te.groupby("region", observed=True):
                ybar = g.y.mean()
                losses = [M.pinball(g.y.to_numpy(), g[pref].to_numpy(), 0.5)] + \
                         [M.pinball(g.y.to_numpy(), g[f"{pref}_q{q:02d}"].to_numpy(), q / 100) for q in (5, 25, 75, 95)]
                pin_rows.append({"region": r, "setting": setting, "h": h, "pinball_norm": float(np.mean(losses)) / ybar})
            for alpha in cfg["probabilistic"]["alphas"]:
                lo_q, hi_q = (5, 95) if alpha == 0.1 else (25, 75)
                s = te.scale.to_numpy()
                zh, zl, zu = zhat[te_m].to_numpy(), zq[lo_q][te_m].to_numpy(), zq[hi_q][te_m].to_numpy()
                # --- QR (raw quantile regression)
                r_, m_ = _interval_rows(te, zl * s, zu * s, alpha, "QR", h, setting)
                rows += r_; mrows += m_
                # --- calibration sets
                if setting == "in-region":
                    c = p[(p.split == "val_cal") & p.eval_ok & np.isfinite(zhat)]
                    cz, czh = (c.y / c.scale).to_numpy(), zhat[c.index].to_numpy()
                    czl, czu = zq[lo_q][c.index].to_numpy(), zq[hi_q][c.index].to_numpy()
                    q_scp = {None: conformal_quantile(scp_scores(cz, czh), alpha)}
                    q_cqr = {None: conformal_quantile(cqr_scores(cz, czl, czu), alpha)}
                    cqr_cal_scores = {None: cqr_scores(cz, czl, czu)}
                    qs = np.full(len(te), q_scp[None])
                    qc = np.full(len(te), q_cqr[None])
                else:
                    qs, qc = np.empty(len(te)), np.empty(len(te))
                    q_scp, q_cqr, cqr_cal_scores = {}, {}, {}
                    folds = p.loc[te.index, "fold"].to_numpy()
                    for f in np.unique(folds):
                        cf = cal_lro[cal_lro.fold == f]
                        sc_s = scp_scores(cf.z.to_numpy(), cf.zhat.to_numpy())
                        sc_c = cqr_scores(cf.z.to_numpy(), cf[f"zq{lo_q:02d}"].to_numpy(), cf[f"zq{hi_q:02d}"].to_numpy())
                        q_scp[f], q_cqr[f] = conformal_quantile(sc_s, alpha), conformal_quantile(sc_c, alpha)
                        cqr_cal_scores[f] = sc_c
                        qs[folds == f], qc[folds == f] = q_scp[f], q_cqr[f]
                r_, m_ = _interval_rows(te, (zh - qs) * s, (zh + qs) * s, alpha, "SCP", h, setting)
                rows += r_; mrows += m_
                r_, m_ = _interval_rows(te, (zl - qc) * s, (zu + qc) * s, alpha, "CQR", h, setting)
                rows += r_; mrows += m_
                # --- SCP-T4: calibrated on the target region's own last `tw` weeks before test
                win = (p.time_utc > test_start - pd.Timedelta(weeks=tw)) & \
                      (p.time_utc <= test_start - pd.Timedelta(hours=h)) & p.split.isin(["val_es", "val_cal"]) & \
                      p.eval_ok & np.isfinite(zhat)
                qt = np.empty(len(te))
                regs = te.region.astype(str).to_numpy()
                for r in np.unique(regs):
                    cw = p[win & (p.region.astype(str) == r)]
                    qt[regs == r] = conformal_quantile(np.abs(cw.y / cw.scale - zhat[cw.index]).to_numpy(), alpha)
                r_, m_ = _interval_rows(te, (zh - qt) * s, (zh + qt) * s, alpha, "SCP-T4", h, setting)
                rows += r_; mrows += m_
                # --- ACI on CQR scores, online per region with delay h
                lo_a, hi_a = np.empty(len(te)), np.empty(len(te))
                ordered = te.assign(_i=np.arange(len(te))).sort_values(["region", "time_utc"])
                for r, g in ordered.groupby("region", observed=True):
                    ii = g._i.to_numpy()
                    key = None if setting == "in-region" else int(p.loc[g.index[0], "fold"])
                    stream = cqr_scores((g.y / g.scale).to_numpy(), zl[ii], zu[ii])
                    qa, _ = aci_intervals(cqr_cal_scores[key], stream, alpha, gamma, delay=h)
                    lo_a[ii], hi_a[ii] = (zl[ii] - qa) * s[ii], (zu[ii] + qa) * s[ii]
                r_, m_ = _interval_rows(te, lo_a, hi_a, alpha, "ACI-CQR", h, setting)
                rows += r_; mrows += m_
            log.info("h=%d %s probabilistic done", h, setting)
    if not rows:
        return
    pr = pd.DataFrame(rows)
    pr.to_csv(METRIC_DIR / "probabilistic_by_region.csv", index=False)
    nominal = 1 - pr.alpha
    pr["abs_cov_dev"] = (pr.coverage - nominal).abs()
    pr.groupby(["h", "setting", "alpha", "method", "period"]).agg(
        coverage_mean=("coverage", "mean"), coverage_median=("coverage", "median"),
        coverage_min=("coverage", "min"), coverage_max=("coverage", "max"),
        mean_abs_cov_dev=("abs_cov_dev", "mean"), share_regions_undercover_5pp=("coverage", lambda s: np.nan),
        width_norm_median=("width_norm", "median"), interval_score_norm_mean=("interval_score_norm", "mean"),
        interval_score_norm_median=("interval_score_norm", "median"), n_regions=("region", "nunique")
    ).reset_index().to_csv(METRIC_DIR / "probabilistic_summary.csv", index=False)
    # fill the under-coverage share properly
    s = pd.read_csv(METRIC_DIR / "probabilistic_summary.csv")
    under = pr.assign(u=pr.coverage < (1 - pr.alpha - 0.05)).groupby(
        ["h", "setting", "alpha", "method", "period"]).u.mean().reset_index()
    s = s.drop(columns="share_regions_undercover_5pp").merge(under.rename(columns={"u": "share_regions_undercover_5pp"}),
                                                           on=["h", "setting", "alpha", "method", "period"])
    s.to_csv(METRIC_DIR / "probabilistic_summary.csv", index=False)
    pd.DataFrame(mrows).to_csv(METRIC_DIR / "probabilistic_monthly_coverage.csv", index=False)
    pin = pd.DataFrame(pin_rows)
    pin.to_csv(METRIC_DIR / "pinball_by_region.csv", index=False)
    pin.groupby(["h", "setting"]).pinball_norm.agg(["median", "mean"]).reset_index().to_csv(
        METRIC_DIR / "pinball_summary.csv", index=False)


def main():
    cfg = load_config()
    hs = cfg["horizons"]
    scales = mase_scales(cfg)
    save_json(scales, METRIC_DIR / "mase_scales.json")
    evaluate_point(cfg, scales, hs)
    evaluate_adapt(cfg, scales, hs)
    evaluate_refit(cfg, scales, hs)
    evaluate_probabilistic(cfg, hs)
    log.info("evaluation complete")


if __name__ == "__main__":
    main()
