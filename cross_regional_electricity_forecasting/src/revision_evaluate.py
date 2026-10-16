"""Evaluation of the revision analyses (responses to the simulated internal review).

Usage: python -m src.revision_evaluate
Outputs: results/metrics/rev_*.csv
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from . import metrics as M
from .common import DATA_PROCESSED, LOG_DIR, METRIC_DIR, PRED_DIR, get_logger, load_config
from .conformal import aci_intervals, conformal_quantile, cqr_scores
from .evaluate_models import RENAME, SEASON, common_mask, per_region_metrics, summarise
from .revision_experiments import SPATIAL_BLOCKS, spatial_folds
from .stats import compare_methods

log = get_logger("rev_eval")
GAMMAS = (0.0, 0.0005, 0.001, 0.002, 0.005, 0.01)
REPS = 2000


def scales():
    return json.load(open(METRIC_DIR / "mase_scales.json"))


def regions():
    return pd.read_csv(DATA_PROCESSED / "regions.csv", index_col=0)


# ----------------------------------------------------------------------- R9 gap tails, R11 cluster bootstrap, R3 TOST
def gap_and_equivalence(cfg):
    pr = pd.read_csv(METRIC_DIR / "point_metrics_by_region.csv")
    reg = regions()
    blk = spatial_folds(reg)
    rows, eq = [], []
    rng = np.random.default_rng(cfg["seed"])
    for h in sorted(pr.h.unique()):
        piv = pr[pr.h == h].pivot(index="region", columns="method", values="nMAE")
        for a, b in [("LGB_G_LRO", "LGB_G_IN"), ("LGB_G_LRO", "LGB_L"), ("LGB_G_IN", "LGB_L")]:
            rel = (piv[a] / piv[b] - 1).dropna()
            # cluster bootstrap: resample spatial blocks (9) with replacement
            groups = {g: rel[[r for r in rel.index if blk[r] == g]].to_numpy() for g in SPATIAL_BLOCKS}
            gl = list(groups)
            boots = []
            for _ in range(REPS):
                pick = rng.choice(gl, len(gl), replace=True)
                boots.append(np.median(np.concatenate([groups[g] for g in pick])))
            lo, hi = np.percentile(boots, [2.5, 97.5])
            lo90, hi90 = np.percentile(boots, [5, 95])
            rows.append({"h": h, "method_a": a, "method_b": b, "median_rel": rel.median(), "p90_rel": rel.quantile(0.9),
                         "max_rel": rel.max(), "argmax": rel.idxmax(), "min_rel": rel.min(),
                         "share_gt_5pct": float((rel > 0.05).mean()), "share_gt_10pct": float((rel > 0.10).mean()),
                         "cluster_ci_lo": lo, "cluster_ci_hi": hi})
            if (a, b) == ("LGB_G_LRO", "LGB_L"):
                for margin in (0.01, 0.02):
                    eq.append({"h": h, "comparison": f"{a} vs {b}", "margin": margin, "median_rel": rel.median(),
                               "cluster_ci90_lo": lo90, "cluster_ci90_hi": hi90,
                               "equivalent": bool(lo90 > -margin and hi90 < margin),
                               "noninferior": bool(hi90 < margin)})
    pd.DataFrame(rows).to_csv(METRIC_DIR / "rev_gap_distribution_cluster_bootstrap.csv", index=False)
    pd.DataFrame(eq).to_csv(METRIC_DIR / "rev_equivalence_tost.csv", index=False)
    # by-year comparison of zero-shot vs local (R3)
    tm = pd.read_csv(METRIC_DIR / "temporal_metrics_by_region.csv")
    yrs = []
    for (h, per), d in tm[tm.by == "year"].groupby(["h", "period"]):
        t = compare_methods(d.rename(columns={"period": "_p"}), "nMAE", [("LGB_G_LRO", "LGB_L"), ("LGB_G_IN", "LGB_L")],
                            1000, cfg["seed"])
        t["h"], t["period"] = h, per
        yrs.append(t)
    pd.concat(yrs).to_csv(METRIC_DIR / "rev_zero_shot_vs_local_by_year.csv", index=False)


# ----------------------------------------------------------------------- R1 spatial blocking: accuracy
def spatial_accuracy(cfg):
    sc = scales()
    rows, tests = [], []
    for h in (1, 24):
        f = PRED_DIR / f"spatial_h{h}.parquet"
        if not f.exists():
            continue
        s = pd.read_parquet(f)
        s = s[s.split == "test"][["region", "time_utc", "LGB_G_LRS", "sfold"]]
        p = pd.read_parquet(PRED_DIR / f"point_h{h}.parquet")
        p = p[p.split == "test"].rename(columns=RENAME)
        d = p.merge(s, on=["region", "time_utc"])
        meths = ["SN24", "LGB_L", "LGB_G_IN", "LGB_G_LRO", "LGB_G_LRS"]
        d = d[common_mask(d, meths)]
        pr = per_region_metrics(d, meths, sc)
        pr["h"] = h
        rows.append(pr)
        t = compare_methods(pr, "nMAE", [("LGB_G_LRS", "LGB_G_IN"), ("LGB_G_LRS", "LGB_G_LRO"), ("LGB_G_LRS", "LGB_L")],
                            1000, cfg["seed"])
        t["h"] = h
        tests.append(t)
    if rows:
        pr = pd.concat(rows)
        pr.to_csv(METRIC_DIR / "rev_spatial_by_region.csv", index=False)
        summarise(pr, ["h", "method"]).to_csv(METRIC_DIR / "rev_spatial_summary.csv", index=False)
        pd.concat(tests).to_csv(METRIC_DIR / "rev_spatial_tests.csv", index=False)
        # gap tails under spatial blocking
        g = []
        for h, dd in pr.groupby("h"):
            piv = dd.pivot(index="region", columns="method", values="nMAE")
            rel = piv.LGB_G_LRS / piv.LGB_G_IN - 1
            g.append({"h": h, "median_rel": rel.median(), "p90_rel": rel.quantile(0.9), "max_rel": rel.max(),
                      "argmax": rel.idxmax(), "share_gt_5pct": float((rel > 0.05).mean()),
                      "share_gt_10pct": float((rel > 0.10).mean())})
        pd.DataFrame(g).to_csv(METRIC_DIR / "rev_spatial_gap_tails.csv", index=False)


# ----------------------------------------------------------------------- R6/R7 gamma selection on source BAs only
def select_gamma_source(cal: pd.DataFrame, fold_col: str, alpha: float, h: int, lo="zq05", hi="zq95"):
    """For each fold choose gamma using only SOURCE BAs: each source BA's VAL-CAL score stream
    (chronological, even ISO weeks of 2023) is run through ACI initialised with the pooled
    scores of the other source BAs. Criterion: mean normalised interval score."""
    sel = {}
    for f, cf in cal.groupby(fold_col):
        cf = cf.sort_values(["region", "time_utc"])
        cf = cf.assign(s=cqr_scores(cf.z.to_numpy(), cf[lo].to_numpy(), cf[hi].to_numpy()))
        score = {g: [] for g in GAMMAS}
        for r, g in cf.groupby("region"):
            init = cf.loc[cf.region != r, "s"].to_numpy()
            for gm in GAMMAS:
                q, _, _ = aci_intervals(init, g.s.to_numpy(), alpha, gm, h)
                l, u = g[lo].to_numpy() - q, g[hi].to_numpy() + q
                score[gm].append(M.interval_score(g.z.to_numpy(), l, u, alpha))
        means = {gm: float(np.mean(v)) for gm, v in score.items()}
        sel[str(f)] = (min(means, key=means.get), means)
    return sel


def interval_stats(d, lo, hi, alpha, label, setting, h):
    d = d.assign(lo=lo, hi=hi)
    assert np.isfinite(d.lo).all() and np.isfinite(d.hi).all()
    start = d.time_utc - pd.Timedelta("1h")
    d["season"] = start.dt.month.map(SEASON)
    d["hour"] = start.dt.hour
    d["decile"] = d.groupby("region", observed=True).y.transform(lambda s: pd.qcut(s, 10, labels=False, duplicates="drop"))
    d["cov"] = (d.y >= d.lo) & (d.y <= d.hi)
    per = d.groupby("region", observed=True).apply(lambda g: pd.Series({
        "coverage": g["cov"].mean(), "width_p50": float(np.median(g.hi - g.lo) / g.y.mean()),
        "IS": M.interval_score(g.y.to_numpy(), g.lo.to_numpy(), g.hi.to_numpy(), alpha) / g.y.mean()}),
        include_groups=False).reset_index()
    per["method"], per["setting"], per["h"], per["alpha"] = label, setting, h, alpha
    cond = []
    for key in ("season", "decile"):
        c = d.groupby(["region", key], observed=True)["cov"].mean().groupby(key).agg(["mean", "min"]).reset_index()
        c = c.rename(columns={key: "level", "mean": "coverage_mean_over_BAs", "min": "coverage_min_over_BAs"})
        c["by"], c["method"], c["setting"], c["h"], c["alpha"] = key, label, setting, h, alpha
        cond.append(c)
    return per, pd.concat(cond)


def calibration_revision(cfg):
    pers, conds, gsel_rows = [], [], []
    tstart = pd.Timestamp(cfg["splits"]["test"][0])
    for setting, h, file_pred, file_cal, col, fcol in [
        ("unseen (random folds)", 24, "point_h24", "lro_source_calibration_h24", "LGB_G_LRO", "fold"),
        ("unseen (random folds)", 1, "point_h1", "lro_source_calibration_h1", "LGB_G_LRO", "fold"),
        ("unseen (spatial blocks)", 24, "spatial_h24", "spatial_source_calibration_h24", "LGB_G_LRS", "sfold")]:
        if not (PRED_DIR / f"{file_pred}.parquet").exists() or f"{col}_q05" not in pd.read_parquet(
                PRED_DIR / f"{file_pred}.parquet", columns=None).columns:
            continue
        p = pd.read_parquet(PRED_DIR / f"{file_pred}.parquet")
        cal = pd.read_parquet(PRED_DIR / f"{file_cal}.parquet")
        alpha = 0.1
        sel = select_gamma_source(cal, fcol, alpha, h)
        for f, (gm, means) in sel.items():
            gsel_rows.append({"setting": setting, "h": h, "fold": f, "gamma_selected": gm,
                              **{f"src_IS_gamma_{k}": v for k, v in means.items()}})
        te = p[(p.split == "test") & p.eval_ok & np.isfinite(p[col]) & np.isfinite(p[f"{col}_q05"]) &
               np.isfinite(p[f"{col}_q95"])].sort_values(["region", "time_utc"]).copy()
        s = te.scale.to_numpy()
        zl, zu, zh = (te[f"{col}_q05"] / te.scale).to_numpy(), (te[f"{col}_q95"] / te.scale).to_numpy(), (te[col] / te.scale).to_numpy()
        z = (te.y / te.scale).to_numpy()
        folds = te[fcol].astype(str).to_numpy()
        # CQR (static, source calibrated)
        qc = np.empty(len(te))
        calsc = {}
        for f, cf in cal.groupby(fcol):
            calsc[str(f)] = cqr_scores(cf.z.to_numpy(), cf.zq05.to_numpy(), cf.zq95.to_numpy())
            qc[folds == str(f)] = conformal_quantile(calsc[str(f)], alpha)
        variants = {"CQR": ((zl - qc) * s, (zu + qc) * s)}
        # ACI variants: gamma=0 (expanding pool), pre-registered 0.005, source-selected
        regs = te.region.astype(str).to_numpy()
        for label in ("ACI-CQR (gamma=0, expanding pool)", "ACI-CQR (gamma=0.005, pre-registered)", "ACI-CQR-S (gamma source-selected)"):
            lo, hi = np.empty(len(te)), np.empty(len(te))
            for r in np.unique(regs):
                ii = np.where(regs == r)[0]
                f = folds[ii[0]]
                gm = 0.0 if "gamma=0," in label else (0.005 if "0.005" in label else sel[f][0])
                q, _, _ = aci_intervals(calsc[f], cqr_scores(z[ii], zl[ii], zu[ii]), alpha, gm, h)
                lo[ii], hi[ii] = (zl[ii] - q) * s[ii], (zu[ii] + q) * s[ii]
            variants[label] = (lo, hi)
        # rolling target calibration: SCP on the target's last 4 weeks of observed |z - zhat| (delay h)
        rs = pd.Series(np.abs(z - zh))
        lo, hi = np.empty(len(te)), np.empty(len(te))
        for r in np.unique(regs):
            ii = np.where(regs == r)[0]
            sr = rs.iloc[ii].reset_index(drop=True)
            q = sr.shift(h).rolling(672, min_periods=168).quantile(min(1.0, (1 - alpha) * (1 + 1 / 672)))
            q = q.fillna(conformal_quantile(np.abs(cal[cal[fcol].astype(str) == folds[ii[0]]].z -
                                                   cal[cal[fcol].astype(str) == folds[ii[0]]].zhat).to_numpy(), alpha))
            lo[ii], hi[ii] = (zh[ii] - q.to_numpy()) * s[ii], (zh[ii] + q.to_numpy()) * s[ii]
        variants["SCP-R4 (rolling 4-week target calibration)"] = (lo, hi)
        for label, (lo, hi) in variants.items():
            per, cond = interval_stats(te[["region", "time_utc", "y"]].copy(), lo, hi, alpha, label, setting, h)
            pers.append(per)
            conds.append(cond)
        log.info("calibration revision %s h=%d done", setting, h)
        # peak-hour diagnostics at h=24 (R20): daily peak absolute percentage error and peak coverage
        if h == 24:
            peak_metrics(te, variants, col, setting)
    per = pd.concat(pers)
    per.to_csv(METRIC_DIR / "rev_calibration_by_region.csv", index=False)
    per.assign(under=per.coverage < 0.85).groupby(["setting", "h", "method"]).agg(
        coverage_mean=("coverage", "mean"), coverage_min=("coverage", "min"), coverage_max=("coverage", "max"),
        share_under_5pp=("under", "mean"), width_p50_median=("width_p50", "median"), IS_median=("IS", "median"),
        IS_mean=("IS", "mean")).reset_index().to_csv(METRIC_DIR / "rev_calibration_summary.csv", index=False)
    pd.concat(conds).to_csv(METRIC_DIR / "rev_conditional_coverage.csv", index=False)
    pd.DataFrame(gsel_rows).to_csv(METRIC_DIR / "rev_gamma_source_selected.csv", index=False)


PEAK_ROWS = []


def peak_metrics(te, variants, col, setting):
    d = te[["region", "time_utc", "y", col, "ba_forecast"]].copy()
    d["date"] = (d.time_utc - pd.Timedelta("1h")).dt.date
    for label, (lo, hi) in variants.items():
        d[f"hi::{label}"] = hi
    idx = d.groupby(["region", "date"], observed=True).y.idxmax()
    pk = d.loc[idx]
    for r, g in pk.groupby("region", observed=True):
        row = {"setting": setting, "region": r, "n_days": len(g),
               "peak_APE_zero_shot": float(np.mean(np.abs(g[col] - g.y) / g.y)),
               "peak_APE_BA_DA": float(np.nanmean(np.abs(g.ba_forecast - g.y) / g.y)) if g.ba_forecast.notna().any() else np.nan}
        for label in variants:
            row[f"peak_above_upper::{label}"] = float(np.mean(g.y > g[f"hi::{label}"]))
        PEAK_ROWS.append(row)
    pd.DataFrame(PEAK_ROWS).to_csv(METRIC_DIR / "rev_peak_metrics_by_region.csv", index=False)


# ----------------------------------------------------------------------- R4 adaptation at several origins
def origins_eval(cfg):
    sc = scales()
    rows, tests = [], []
    for h in (24, 6):
        f = PRED_DIR / f"adapt_origins_h{h}.parquet"
        if not f.exists():
            continue
        a = pd.read_parquet(f)
        meths = ["LGB_G_LRO"] + [c for c in a.columns if c.startswith(("LGB_L_k", "LGB_FT_k"))]
        for o, d in a.groupby("origin"):
            d = d[common_mask(d, meths)]
            pr = per_region_metrics(d, meths, sc)
            pr["h"], pr["origin"] = h, o
            rows.append(pr)
            t = compare_methods(pr, "nMAE", [(m, "LGB_G_LRO") for m in meths if m != "LGB_G_LRO"], 1000, cfg["seed"])
            t["h"], t["origin"] = h, o
            tests.append(t)
    if rows:
        pr = pd.concat(rows)
        pr.to_csv(METRIC_DIR / "rev_adapt_origins_by_region.csv", index=False)
        summarise(pr, ["h", "origin", "method"]).to_csv(METRIC_DIR / "rev_adapt_origins_summary.csv", index=False)
        pd.concat(tests).to_csv(METRIC_DIR / "rev_adapt_origins_tests.csv", index=False)


# ----------------------------------------------------------------------- R12 excluded BAs
def excluded_eval(cfg):
    f = PRED_DIR / "excluded_bas.parquet"
    if not f.exists():
        return
    d = pd.read_parquet(f)
    rows = []
    for (h, r), g in d.groupby(["h", "region"], observed=True):
        g = g[g.eval_ok & np.isfinite(g.y) & np.isfinite(g.LGB_G_zero_shot) & np.isfinite(g.seasonal_naive_24)]
        row = {"h": h, "region": r, "n": len(g), "mean_mw": g.y.mean(),
               "nMAE_zero_shot": M.nmae(g.y.to_numpy(), g.LGB_G_zero_shot.to_numpy()),
               "nMAE_SN24": M.nmae(g.y.to_numpy(), g.seasonal_naive_24.to_numpy())}
        gl = g[np.isfinite(g.LGB_L)]
        row["nMAE_local"] = M.nmae(gl.y.to_numpy(), gl.LGB_L.to_numpy()) if len(gl) > 100 else np.nan
        row["nMAE_zero_shot_on_local_hours"] = M.nmae(gl.y.to_numpy(), gl.LGB_G_zero_shot.to_numpy()) if len(gl) > 100 else np.nan
        rows.append(row)
    pd.DataFrame(rows).to_csv(METRIC_DIR / "rev_excluded_bas.csv", index=False)


def main():
    cfg = load_config()
    gap_and_equivalence(cfg)
    log.info("gap/equivalence done")
    spatial_accuracy(cfg)
    origins_eval(cfg)
    excluded_eval(cfg)
    calibration_revision(cfg)
    log.info("revision evaluation complete")


if __name__ == "__main__":
    main()
