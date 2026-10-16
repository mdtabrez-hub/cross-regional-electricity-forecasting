"""Experiments added during the (simulated) internal review revision. All are logged in
DECISION_LOG.md (D14-) as post-review additions; none changes the frozen main analysis.

Usage:
    python -m src.revision_experiments spatial     # R1: spatially blocked leave-region-out folds
    python -m src.revision_experiments origins     # R4: adaptation at several onboarding origins
    python -m src.revision_experiments excluded    # R12: zero-shot on excluded small/low-quality BAs
    python -m src.revision_experiments ridge       # R5: ridge penalty selection on VAL-ES
"""
from __future__ import annotations

import argparse

import lightgbm as lgb
import numpy as np
import pandas as pd

from .common import DATA_PROCESSED, LOG_DIR, PRED_DIR, get_logger, load_config, save_json, set_seed
from .features import FeatureBuilder, feature_columns
from .models import fit_lgb, fit_ridge, predict_lgb
from .preprocess_data import build_panel, load_raw
from .train_models import MODEL_DIR, QUANTS, base_frame, chosen_params, load_builder, split_frames, truncate

log = get_logger("revision")

# Spatial blocks: EIA reporting regions; single-BA eastern regions merged with contiguous neighbours.
SPATIAL_BLOCKS = {"NW": ["NW"], "CAL": ["CAL"], "SW": ["SW"], "FLA": ["FLA"], "CAR": ["CAR"],
                  "TEX+CENT": ["TEX", "CENT"], "MIDW+MIDA": ["MIDW", "MIDA"], "SE+TEN": ["SE", "TEN"],
                  "NE+NY": ["NE", "NY"]}


def spatial_folds(reg: pd.DataFrame) -> dict[str, str]:
    inv = {code: blk for blk, codes in SPATIAL_BLOCKS.items() for code in codes}
    return {r: inv[c] for r, c in reg.balancing_authority_region_code_eia.items()}


def run_spatial(cfg, horizons=(24, 1), quantile_h=(24,)):
    fb, reg = load_builder(cfg)
    sfold = spatial_folds(reg)
    save_json(sfold, LOG_DIR / "spatial_folds.json")
    for h in horizons:
        set_seed(cfg["seed"])
        gp = chosen_params("global", h, cfg)
        df = fb.build(h)
        cols = feature_columns(df)
        tr, va_es, va_cal, te = split_frames(df, cfg)
        parts = {"test": te, "val_es": va_es, "val_cal": va_cal}
        out = pd.concat([base_frame(p, s) for s, p in parts.items()], ignore_index=True)
        allx = pd.concat(list(parts.values()), ignore_index=True)
        out["sfold"] = out.region.astype(str).map(sfold)
        out["LGB_G_LRS"] = np.nan
        cal_rows = []
        for blk in SPATIAL_BLOCKS:
            held = [r for r, b in sfold.items() if b == blk]
            src = [r for r in fb.regions if r not in held]
            m = out.region.isin(held).to_numpy()
            b = truncate(fit_lgb(tr[tr.region.isin(src)], va_es[va_es.region.isin(src)], cols, cfg, gp))
            out.loc[m, "LGB_G_LRS"] = predict_lgb(b, allx[m], cols) * allx[m].scale.to_numpy()
            sc = va_cal[va_cal.region.isin(src) & va_cal.eval_ok & np.isfinite(va_cal.z)]
            cal = pd.DataFrame({"sfold": blk, "region": sc.region.astype(str).to_numpy(),
                                "time_utc": sc.time_utc.to_numpy(), "z": sc.z.to_numpy(), "zhat": predict_lgb(b, sc, cols)})
            if h in quantile_h:
                for q in QUANTS:
                    bq = truncate(fit_lgb(tr[tr.region.isin(src)], va_es[va_es.region.isin(src)], cols, cfg, gp,
                                          objective="quantile", alpha=q))
                    tag = f"LGB_G_LRS_q{int(q * 100):02d}"
                    if tag not in out:
                        out[tag] = np.nan
                    out.loc[m, tag] = predict_lgb(bq, allx[m], cols) * allx[m].scale.to_numpy()
                    cal[f"zq{int(q * 100):02d}"] = predict_lgb(bq, sc, cols)
            cal_rows.append(cal)
            log.info("spatial h=%d block %s (%d held out) done", h, blk, len(held))
        out.to_parquet(PRED_DIR / f"spatial_h{h}.parquet")
        pd.concat(cal_rows, ignore_index=True).to_parquet(PRED_DIR / f"spatial_source_calibration_h{h}.parquet")


def run_origins(cfg, horizons=(24, 6), origins=("2024-04-01 01:00", "2024-07-01 01:00", "2024-10-01 01:00"),
                weeks=(4, 13), eval_days=365):
    """Adaptation at several onboarding origins inside the test period: adapt on the k weeks
    before the origin (labels observable at the origin), evaluate on the following year."""
    fb, _ = load_builder(cfg)
    folds = chosen_params("lro_folds")
    small = {"num_leaves": 15, "min_data_in_leaf": 10}
    ad = cfg["adaptation"]
    for h in horizons:
        df = fb.build(h)
        cols = feature_columns(df)
        outs = []
        base_models = {f: lgb.Booster(model_file=str(MODEL_DIR / f"LGB_G_LRO_f{f}_h{h}.txt")) for f in set(folds.values())}
        for o in origins:
            o = pd.Timestamp(o)
            ev = df[(df.time_utc >= o) & (df.time_utc < o + pd.Timedelta(days=eval_days))]
            res = ev[["region", "time_utc", "y", "eval_ok", "scale"]].copy()
            res["origin"] = str(o.date())
            res["LGB_G_LRO"] = np.nan
            for r in fb.regions:
                m = (res.region == r).to_numpy()
                res.loc[m, "LGB_G_LRO"] = predict_lgb(base_models[folds[r]], ev[m], cols) * ev[m].scale.to_numpy()
            for k in weeks:
                res[f"LGB_L_k{k}"], res[f"LGB_FT_k{k}"] = np.nan, np.nan
                for r in fb.regions:
                    tw = df[(df.region == r) & (df.time_utc >= o - pd.Timedelta(weeks=k)) &
                            (df.time_utc <= o - pd.Timedelta(hours=h))]
                    m = (res.region == r).to_numpy()
                    er = ev[m]
                    bl = fit_lgb(tw, None, cols, cfg, small, n_estimators=300)
                    res.loc[m, f"LGB_L_k{k}"] = predict_lgb(bl, er, cols) * er.scale.to_numpy()
                    bf = fit_lgb(tw, None, cols, cfg, {**small, "learning_rate": ad["finetune_learning_rate"]},
                                 n_estimators=ad["finetune_extra_trees"], init_model=base_models[folds[r]])
                    res.loc[m, f"LGB_FT_k{k}"] = bf.predict(er[cols]) * er.scale.to_numpy()
            outs.append(res)
            log.info("origins h=%d origin %s done", h, o.date())
        pd.concat(outs, ignore_index=True).to_parquet(PRED_DIR / f"adapt_origins_h{h}.parquet")


def run_excluded(cfg, horizons=(24, 1)):
    """Zero-shot forecasts for BAs excluded by the quality/size criteria (never used in training)."""
    ops, bas = load_raw(cfg)
    allreg = pd.read_csv(DATA_PROCESSED / "regions_all.csv", index_col=0)
    cand = allreg[(~allreg.selected) & (allreg.reported_coverage > 0.5) & allreg.report_timezone.notna()
                  & (pd.to_datetime(allreg.last_utc) >= pd.Timestamp(cfg["splits"]["test"][1]))].index.tolist()
    panel = build_panel(ops, cand, cfg)
    fbx = FeatureBuilder(panel, allreg.report_timezone.to_dict(), cfg)
    lp = None
    outs = []
    for h in horizons:
        df = fbx.build(h)
        cols = feature_columns(df)
        tr, va_es, _, te = split_frames(df, cfg)
        res = te[["region", "time_utc", "y", "eval_ok", "scale", "seasonal_naive_24"]].copy()
        res["h"] = h
        g = lgb.Booster(model_file=str(MODEL_DIR / f"LGB_G_IN_h{h}.txt"))  # trained on the 48 study BAs only
        res["LGB_G_zero_shot"] = predict_lgb(g, te, cols) * te.scale.to_numpy()
        lp = chosen_params("local", h, cfg)
        res["LGB_L"] = np.nan
        for r in cand:
            trr, var = tr[tr.region == r], va_es[va_es.region == r]
            if (trr.eval_ok.sum() < 2000) or (var.eval_ok.sum() < 200):
                continue
            b = truncate(fit_lgb(trr, var, cols, cfg, lp))
            m = (res.region == r).to_numpy()
            res.loc[m, "LGB_L"] = predict_lgb(b, te[m], cols) * te[m].scale.to_numpy()
        outs.append(res)
        log.info("excluded BAs h=%d done: %s", h, cand)
    pd.concat(outs, ignore_index=True).to_parquet(PRED_DIR / "excluded_bas.parquet")


def run_ridge(cfg, alphas=(0.01, 0.1, 1.0, 10.0, 100.0, 1000.0)):
    fb, _ = load_builder(cfg)
    df = fb.build(24)
    cols = feature_columns(df)
    tr, va_es, _, _ = split_frames(df, cfg)
    v = va_es[va_es.eval_ok & np.isfinite(va_es.z)]
    rows = []
    for a in alphas:
        m = fit_ridge(tr, cols, a)
        pred = m.predict(v[cols]) * v.scale.to_numpy()
        e = (v.y - pred).abs().groupby(v.region, observed=True).mean() / v.y.groupby(v.region, observed=True).mean()
        rows.append({"alpha": a, "val_es_median_nmae": float(e.median())})
        log.info("ridge alpha=%g val nMAE=%.5f", a, rows[-1]["val_es_median_nmae"])
    pd.DataFrame(rows).to_csv(LOG_DIR / "ridge_alpha_grid_validation.csv", index=False)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["spatial", "origins", "excluded", "ridge"])
    a = ap.parse_args(argv)
    cfg = load_config()
    set_seed(cfg["seed"])
    {"spatial": run_spatial, "origins": run_origins, "excluded": run_excluded, "ridge": run_ridge}[a.stage](cfg)


if __name__ == "__main__":
    main()
