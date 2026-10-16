"""Experiment runner: trains all models and saves predictions (MW) for later evaluation.

Usage:
    python -m src.train_models select            # hyper-parameter grids on VAL-ES (no test data)
    python -m src.train_models point  --h 1 6 24 # E1 (+ quantile models for E4) and models for E2/E5
    python -m src.train_models adapt  --h 1 6 24 # E2 limited-target-data adaptation
    python -m src.train_models refit  --h 1 6 24 # E3 rolling-origin refit

Outputs: results/predictions/*.parquet, results/models/*.txt, results/logs/*.json
"""
from __future__ import annotations

import argparse
import json

import lightgbm as lgb
import numpy as np
import pandas as pd

from .common import (DATA_PROCESSED, LOG_DIR, PRED_DIR, RESULTS, get_logger, load_config, peak_rss_mb,
                     save_json, set_seed)
from .features import FeatureBuilder, feature_columns
from .models import fit_lgb, fit_ridge, model_size_bytes, predict_lgb

log = get_logger("train")
MODEL_DIR = RESULTS / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
QUANTS = [0.05, 0.25, 0.75, 0.95]  # tau = 0.5 is the L1 point model


# --------------------------------------------------------------------------- data helpers
def load_builder(cfg):
    panel = pd.read_parquet(DATA_PROCESSED / "panel.parquet")
    reg = pd.read_csv(DATA_PROCESSED / "regions.csv", index_col=0)
    return FeatureBuilder(panel, reg.report_timezone.to_dict(), cfg), reg


def period(df, span):
    return (df.time_utc >= pd.Timestamp(span[0])) & (df.time_utc <= pd.Timestamp(span[1]))


def split_frames(df, cfg, prefix=""):
    sp = cfg["splits"]
    tr = df[period(df, sp[prefix + "train"])]
    va = df[period(df, sp[prefix + "valid"])]
    week = va.time_utc.dt.isocalendar().week.to_numpy()
    va_es, va_cal = va[week % 2 == 1], va[week % 2 == 0]
    te = df[period(df, sp[prefix + "test"])]
    return tr, va_es, va_cal, te


def lro_folds(reg: pd.DataFrame, cfg) -> dict[str, int]:
    rng = np.random.default_rng(cfg["seed"])
    order = reg.sort_values("mean_demand_mw", ascending=False).index.tolist()
    k = cfg["lro"]["n_folds"]
    folds = {}
    for b in range(0, len(order), k):
        block = order[b:b + k]
        perm = rng.permutation(len(block))
        for j, r in zip(perm, block):
            folds[r] = int(j)
    return folds


def truncate(booster):
    """Keep only trees up to the early-stopping best iteration."""
    best = booster.best_iteration or booster.current_iteration()
    b = lgb.Booster(model_str=booster.model_to_string(num_iteration=best))
    b.fit_seconds, b.n_train_rows, b.best_iteration = booster.fit_seconds, booster.n_train_rows, best
    return b


def chosen_params(kind="global"):
    path = LOG_DIR / "selected_hyperparameters.json"
    sel = json.load(open(path))
    return sel[kind]


def record(costs, name, h, model, df_pred, cols, extra=None):
    import time

    t0 = time.perf_counter()
    _ = predict_lgb(model, df_pred, cols) if isinstance(model, lgb.Booster) else model.predict(df_pred[cols])
    inf = time.perf_counter() - t0
    row = {"model": name, "h": h, "fit_seconds": getattr(model, "fit_seconds", np.nan),
           "n_train_rows": getattr(model, "n_train_rows", np.nan), "inference_seconds": inf,
           "n_inference_rows": len(df_pred), "peak_rss_mb": peak_rss_mb(),
           "size_bytes": model_size_bytes(model) if isinstance(model, lgb.Booster) else np.nan,
           "n_trees": model.current_iteration() if isinstance(model, lgb.Booster) else np.nan}
    if extra:
        row.update(extra)
    costs.append(row)


# --------------------------------------------------------------------------- selection
def run_select(cfg):
    fb, reg = load_builder(cfg)
    df = fb.build(24)
    cols = feature_columns(df)
    tr, va_es, _, _ = split_frames(df, cfg)
    m = va_es.eval_ok & np.isfinite(va_es.z)
    v = va_es[m]
    out = {"global": [], "local": []}

    def nmae_by_region(pred):
        e = (v.y - pred).abs().groupby(v.region).mean() / v.y.groupby(v.region).mean()
        return float(e.median())

    for nl in cfg["lightgbm"]["grid"]["num_leaves"]:
        for md in cfg["lightgbm"]["grid"]["min_data_in_leaf"]:
            b = fit_lgb(tr, va_es, cols, cfg, {"num_leaves": nl, "min_data_in_leaf": md})
            s = nmae_by_region(predict_lgb(b, v, cols) * v.scale)
            out["global"].append({"num_leaves": nl, "min_data_in_leaf": md, "best_iter": b.best_iteration,
                                  "fit_seconds": b.fit_seconds, "val_es_median_nmae": s})
            log.info("global grid %s", out["global"][-1])
    for nl in cfg["lightgbm"]["local_grid"]["num_leaves"]:
        for md in cfg["lightgbm"]["local_grid"]["min_data_in_leaf"]:
            preds = pd.Series(np.nan, index=v.index)
            iters = []
            for r in fb.regions:
                b = fit_lgb(tr[tr.region == r], va_es[va_es.region == r], cols, cfg,
                            {"num_leaves": nl, "min_data_in_leaf": md, "num_threads": 4})
                vr = v[v.region == r]
                preds.loc[vr.index] = predict_lgb(b, vr, cols) * vr.scale
                iters.append(b.best_iteration)
            s = nmae_by_region(preds)
            out["local"].append({"num_leaves": nl, "min_data_in_leaf": md, "median_best_iter": float(np.median(iters)),
                                 "val_es_median_nmae": s})
            log.info("local grid %s", out["local"][-1])
    best_g = min(out["global"], key=lambda d: d["val_es_median_nmae"])
    best_l = min(out["local"], key=lambda d: d["val_es_median_nmae"])
    save_json(out, LOG_DIR / "hyperparameter_grid_validation.json")
    save_json({"global": {"num_leaves": best_g["num_leaves"], "min_data_in_leaf": best_g["min_data_in_leaf"]},
               "local": {"num_leaves": best_l["num_leaves"], "min_data_in_leaf": best_l["min_data_in_leaf"]},
               "lro_folds": lro_folds(reg, cfg)}, LOG_DIR / "selected_hyperparameters.json")


# --------------------------------------------------------------------------- E1 / E4
def base_frame(df_part, split):
    keep = ["region", "time_utc", "y", "eval_ok", "scale", "z", "ba_forecast", "seasonal_naive_24",
            "seasonal_naive_168", "persistence"]
    out = df_part[keep].copy()
    out["split"] = split
    return out


def run_point(cfg, horizons, quantile_horizons):
    fb, reg = load_builder(cfg)
    gp, lp = chosen_params("global"), chosen_params("local")
    folds = chosen_params("lro_folds")
    costs = []
    for h in horizons:
        set_seed(cfg["seed"])
        df = fb.build(h)
        cols = feature_columns(df)
        tr, va_es, va_cal, te = split_frames(df, cfg)
        parts = {"test": te, "val_es": va_es, "val_cal": va_cal}
        out = pd.concat([base_frame(p, s) for s, p in parts.items()], ignore_index=True)
        out["fold"] = out.region.map(folds)
        allx = pd.concat(list(parts.values()), ignore_index=True)  # same row order as `out`

        def put(col, values, mask=None):
            if col not in out:
                out[col] = np.nan
            if mask is None:
                out[col] = values
            else:
                out.loc[mask, col] = values

        # ---- global in-region
        b = truncate(fit_lgb(tr, va_es, cols, cfg, gp))
        b.save_model(str(MODEL_DIR / f"LGB_G_IN_h{h}.txt"))
        put("LGB_G_IN", predict_lgb(b, allx, cols) * allx.scale.to_numpy())
        record(costs, "LGB_G_IN", h, b, te, cols)
        rg = fit_ridge(tr, cols, cfg["ridge"]["alpha"])
        put("RIDGE_G_IN", rg.predict(allx[cols]) * allx.scale.to_numpy())
        record(costs, "RIDGE_G_IN", h, rg, te, cols)
        if h in quantile_horizons:
            for q in QUANTS:
                bq = truncate(fit_lgb(tr, va_es, cols, cfg, gp, objective="quantile", alpha=q))
                put(f"LGB_G_IN_q{int(q*100):02d}", predict_lgb(bq, allx, cols) * allx.scale.to_numpy())
                record(costs, f"LGB_G_IN_q{int(q*100):02d}", h, bq, te, cols)
        log.info("h=%d global in-region done", h)

        # ---- local per region
        put("LGB_L", np.nan)
        fit_s, sizes = 0.0, 0
        for r in fb.regions:
            bl = truncate(fit_lgb(tr[tr.region == r], va_es[va_es.region == r], cols, cfg, lp))
            m = (out.region == r).to_numpy()
            put("LGB_L", predict_lgb(bl, allx[m], cols) * allx[m].scale.to_numpy(), m)
            fit_s += bl.fit_seconds
            sizes += model_size_bytes(bl)
            bl.save_model(str(MODEL_DIR / f"LGB_L_{r}_h{h}.txt"))
        costs.append({"model": "LGB_L (48 models)", "h": h, "fit_seconds": fit_s, "size_bytes": sizes,
                      "n_train_rows": int(tr.eval_ok.sum()), "peak_rss_mb": peak_rss_mb()})
        log.info("h=%d local done", h)

        # ---- leave-regions-out
        src_cal = []
        for f in sorted(set(folds.values())):
            held = [r for r, k in folds.items() if k == f]
            src = [r for r in fb.regions if r not in held]
            trs, vas = tr[tr.region.isin(src)], va_es[va_es.region.isin(src)]
            m = out.region.isin(held).to_numpy()
            bf = truncate(fit_lgb(trs, vas, cols, cfg, gp))
            bf.save_model(str(MODEL_DIR / f"LGB_G_LRO_f{f}_h{h}.txt"))
            put("LGB_G_LRO", predict_lgb(bf, allx[m], cols) * allx[m].scale.to_numpy(), m)
            record(costs, "LGB_G_LRO", h, bf, te[te.region.isin(held)], cols, {"fold": f})
            rf = fit_ridge(trs, cols, cfg["ridge"]["alpha"])
            put("RIDGE_G_LRO", rf.predict(allx.loc[m, cols]) * allx[m].scale.to_numpy(), m)
            # source-region calibration scores (VAL-CAL rows of source regions only)
            sc = va_cal[va_cal.region.isin(src) & va_cal.eval_ok & np.isfinite(va_cal.z)]
            cal = pd.DataFrame({"fold": f, "region": sc.region.to_numpy(), "time_utc": sc.time_utc.to_numpy(),
                                "z": sc.z.to_numpy(), "zhat": predict_lgb(bf, sc, cols)})
            if h in quantile_horizons:
                for q in QUANTS:
                    bq = truncate(fit_lgb(trs, vas, cols, cfg, gp, objective="quantile", alpha=q))
                    tag = f"LGB_G_LRO_q{int(q*100):02d}"
                    put(tag, predict_lgb(bq, allx[m], cols) * allx[m].scale.to_numpy(), m)
                    cal[f"zq{int(q*100):02d}"] = predict_lgb(bq, sc, cols)
                    record(costs, tag, h, bq, te[te.region.isin(held)], cols, {"fold": f})
            src_cal.append(cal)
            log.info("h=%d LRO fold %d done", h, f)
        pd.concat(src_cal, ignore_index=True).to_parquet(PRED_DIR / f"lro_source_calibration_h{h}.parquet")
        out.to_parquet(PRED_DIR / f"point_h{h}.parquet")
        pd.DataFrame(costs).to_csv(LOG_DIR / "compute_costs_point.csv", index=False)
        log.info("h=%d saved predictions (%d rows)", h, len(out))


# --------------------------------------------------------------------------- E2
def run_adapt(cfg, horizons):
    fb, reg = load_builder(cfg)
    folds = chosen_params("lro_folds")
    ad = cfg["adaptation"]
    small = {"num_leaves": 15, "min_data_in_leaf": 10}
    costs = []
    test_start = pd.Timestamp(cfg["splits"]["test"][0])
    for h in horizons:
        set_seed(cfg["seed"])
        df = fb.build(h)
        cols = feature_columns(df)
        _, _, _, te = split_frames(df, cfg)
        out = base_frame(te, "test")
        for k in ad["weeks"]:
            win_start = test_start - pd.Timedelta(weeks=k)
            colL, colF = f"LGB_L_k{k}", f"LGB_FT_k{k}"
            out[colL], out[colF] = np.nan, np.nan
            fit_l, fit_f = [], []
            for r in fb.regions:
                # target window ends one horizon before the first test target, so labels are known at test start
                tw = df[(df.region == r) & (df.time_utc >= win_start) &
                        (df.time_utc <= test_start - pd.Timedelta(hours=h))]
                m = (out.region == r).to_numpy()
                ter = te[te.region == r]
                bl = fit_lgb(tw, None, cols, cfg, small, n_estimators=300)
                out.loc[m, colL] = predict_lgb(bl, ter, cols) * ter.scale.to_numpy()
                fit_l.append(bl.fit_seconds)
                base = lgb.Booster(model_file=str(MODEL_DIR / f"LGB_G_LRO_f{folds[r]}_h{h}.txt"))
                bf = fit_lgb(tw, None, cols, cfg, {**small, "learning_rate": ad["finetune_learning_rate"]},
                             n_estimators=ad["finetune_extra_trees"], init_model=base)
                out.loc[m, colF] = bf.predict(ter[cols]) * ter.scale.to_numpy()
                fit_f.append(bf.fit_seconds)
            costs += [{"model": colL, "h": h, "fit_seconds_per_region": float(np.mean(fit_l))},
                      {"model": colF, "h": h, "fit_seconds_per_region": float(np.mean(fit_f))}]
            log.info("h=%d adaptation k=%d done", h, k)
        out.to_parquet(PRED_DIR / f"adapt_h{h}.parquet")
        pd.DataFrame(costs).to_csv(LOG_DIR / "compute_costs_adapt.csv", index=False)


# --------------------------------------------------------------------------- E3 refit
def run_refit(cfg, horizons):
    fb, _ = load_builder(cfg)
    gp, lp = chosen_params("global"), chosen_params("local")
    for h in horizons:
        set_seed(cfg["seed"])
        df = fb.build(h)
        cols = feature_columns(df)
        tr, va_es, _, te = split_frames(df, cfg, prefix="refit_")
        out = base_frame(te, "test")
        b = truncate(fit_lgb(tr, va_es, cols, cfg, gp))
        out["LGB_G_IN_refit"] = predict_lgb(b, te, cols) * te.scale.to_numpy()
        out["LGB_L_refit"] = np.nan
        for r in fb.regions:
            bl = truncate(fit_lgb(tr[tr.region == r], va_es[va_es.region == r], cols, cfg, lp))
            m = (out.region == r).to_numpy()
            ter = te[te.region == r]
            out.loc[m, "LGB_L_refit"] = predict_lgb(bl, ter, cols) * ter.scale.to_numpy()
        out.to_parquet(PRED_DIR / f"refit_h{h}.parquet")
        log.info("h=%d refit done", h)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["select", "point", "adapt", "refit"])
    ap.add_argument("--h", type=int, nargs="+", default=None)
    ap.add_argument("--quantile-h", type=int, nargs="+", default=None)
    a = ap.parse_args(argv)
    cfg = load_config()
    set_seed(cfg["seed"])
    hs = a.h or cfg["horizons"]
    if a.stage == "select":
        run_select(cfg)
    elif a.stage == "point":
        run_point(cfg, hs, a.quantile_h if a.quantile_h is not None else hs)
    elif a.stage == "adapt":
        run_adapt(cfg, hs)
    elif a.stage == "refit":
        run_refit(cfg, hs)


if __name__ == "__main__":
    main()
