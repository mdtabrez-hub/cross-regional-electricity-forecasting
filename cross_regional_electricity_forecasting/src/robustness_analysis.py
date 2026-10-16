"""E5 missing-data robustness and E6 ablations.

Usage:
    python -m src.robustness_analysis missing
    python -m src.robustness_analysis ablation
    python -m src.robustness_analysis evaluate
Outputs: results/predictions/missing_h*.parquet, ablation_h24.parquet,
         results/metrics/missing_data_*.csv, ablation_results.csv
"""
from __future__ import annotations

import argparse
import zlib

import lightgbm as lgb
import numpy as np
import pandas as pd

from .common import METRIC_DIR, PRED_DIR, get_logger, load_config, save_json, set_seed
from .evaluate_models import mase_scales, per_region_metrics, summarise
from .features import CAL_COLS, feature_columns
from .models import fit_lgb, predict_lgb
from .stats import compare_methods
from .train_models import MODEL_DIR, chosen_params, load_builder, period, split_frames, truncate

log = get_logger("robustness")


# --------------------------------------------------------------------------- corruption
def mcar(X: np.ndarray, rate: float, rng) -> np.ndarray:
    Xc = X.copy()
    Xc[rng.random(X.shape) < rate] = np.nan
    return Xc


def blocks(X: np.ndarray, length: int, rate: float, rng) -> np.ndarray:
    Xc = X.copy()
    R, N = X.shape
    n_blocks = int(round(rate * N / length))
    for i in range(R):
        for s in rng.integers(0, N - length, n_blocks):
            Xc[i, s:s + length] = np.nan
    return Xc


def impute_locf(X: np.ndarray) -> np.ndarray:
    return pd.DataFrame(X.T).ffill().to_numpy().T


def impute_seasonal(X: np.ndarray, period_h: int = 168) -> np.ndarray:
    """Causal weekly-seasonal imputation: x_t <- x_{t-168} (already imputed), else x_{t-1}."""
    Xs = X.copy()
    R, N = Xs.shape
    for t in range(1, N):
        col = Xs[:, t]
        miss = np.isnan(col)
        if miss.any():
            src = Xs[:, t - period_h] if t >= period_h else Xs[:, t - 1]
            fill = np.where(np.isnan(src), Xs[:, t - 1], src)
            col[miss] = fill[miss]
    return Xs


def scenarios(cfg):
    md = cfg["missing_data"]
    sc = [("clean", None, 0.0)]
    sc += [(f"MCAR_{int(r*100)}", "mcar", r) for r in md["mcar_rates"]]
    sc += [(f"BLOCK_{L}h", "block", L) for L in md["block_lengths_h"]]
    return sc


def run_missing(cfg):
    fb, _ = load_builder(cfg)
    folds = chosen_params("lro_folds")
    md = cfg["missing_data"]
    test_mask = period(pd.DataFrame({"time_utc": fb.times}), cfg["splits"]["test"]).to_numpy()
    for h in md["horizons"]:
        set_seed(cfg["seed"])
        gp = chosen_params("global", h, cfg)
        g_in = lgb.Booster(model_file=str(MODEL_DIR / f"LGB_G_IN_h{h}.txt"))
        lro = {f: lgb.Booster(model_file=str(MODEL_DIR / f"LGB_G_LRO_f{f}_h{h}.txt")) for f in set(folds.values())}
        # model trained with MCAR augmentation of its inputs (in-region setting)
        rng_aug = np.random.default_rng(cfg["seed"] + 999)
        df_aug = fb.build(h, x=mcar(fb.X, md["augment_train_rate"], rng_aug))
        cols = feature_columns(df_aug)
        tr, va_es, _, _ = split_frames(df_aug, cfg)
        g_aug = truncate(fit_lgb(tr, va_es, cols, cfg, gp))
        del df_aug, tr, va_es
        outs = []
        for name, kind, par in scenarios(cfg):
            rng = np.random.default_rng(cfg["seed"] + zlib.crc32(name.encode()) % 10_000)
            Xc = fb.X if kind is None else (mcar(fb.X, par, rng) if kind == "mcar" else
                                             blocks(fb.X, int(par), md["block_rate"], rng))
            variants = {"native": Xc} if kind is None else \
                {"native": Xc, "locf": impute_locf(Xc), "seasonal": impute_seasonal(Xc)}
            for strat, Xv in variants.items():
                d = fb.build(h, x=Xv, row_mask_times=test_mask)
                base = d[["region", "time_utc", "y", "eval_ok", "scale"]].copy()
                base["scenario"], base["strategy"] = name, strat
                base["input_missing_share"] = float(np.isnan(Xc[:, test_mask]).mean())
                base["LGB_G_IN"] = predict_lgb(g_in, d, cols) * d.scale.to_numpy()
                base["LGB_G_LRO"] = np.nan
                for f, b in lro.items():
                    m = d.region.map(folds).to_numpy() == f
                    base.loc[m, "LGB_G_LRO"] = predict_lgb(b, d[m], cols) * d[m].scale.to_numpy()
                if strat == "native":
                    base["LGB_G_IN_AUG"] = predict_lgb(g_aug, d, cols) * d.scale.to_numpy()
                outs.append(base)
            log.info("h=%d scenario %s done", h, name)
        pd.concat(outs, ignore_index=True).to_parquet(PRED_DIR / f"missing_h{h}.parquet")


# --------------------------------------------------------------------------- ablations
def run_ablation(cfg):
    h = cfg["ablation"]["horizon"]
    fb, _ = load_builder(cfg)
    folds = chosen_params("lro_folds")
    gp = chosen_params("global", h, cfg)
    df = fb.build(h)
    full = feature_columns(df)
    tr, va_es, _, te = split_frames(df, cfg)
    variants = {
        "no_calendar": [c for c in full if c not in CAL_COLS],
        "no_weekly_lags": [c for c in full if not c.startswith("week_lag_")],
        "recent_lags_0_3_only": [c for c in full if not (c.startswith("lag_") and int(c.split("_")[1]) > 3)],
    }
    out = te[["region", "time_utc", "y", "eval_ok", "scale"]].copy()
    meta = []
    for name, cols in variants.items():
        out[name] = np.nan
        for f in sorted(set(folds.values())):
            held = [r for r, k in folds.items() if k == f]
            src = [r for r in fb.regions if r not in held]
            b = truncate(fit_lgb(tr[tr.region.isin(src)], va_es[va_es.region.isin(src)], cols, cfg, gp))
            m = out.region.isin(held).to_numpy()
            out.loc[m, name] = predict_lgb(b, te[m], cols) * te[m].scale.to_numpy()
        log.info("ablation %s done", name)
    rng = np.random.default_rng(cfg["seed"])
    for n in cfg["ablation"]["source_pool_sizes"]:
        for rep in range(cfg["ablation"]["source_pool_repeats"]):
            name = f"pool_{n}_rep{rep}"
            out[name] = np.nan
            for f in sorted(set(folds.values())):
                held = [r for r, k in folds.items() if k == f]
                src_all = [r for r in fb.regions if r not in held]
                src = list(rng.choice(src_all, n, replace=False))
                meta.append({"variant": name, "fold": f, "sources": src})
                b = truncate(fit_lgb(tr[tr.region.isin(src)], va_es[va_es.region.isin(src)], full, cfg, gp))
                m = out.region.isin(held).to_numpy()
                out.loc[m, name] = predict_lgb(b, te[m], full) * te[m].scale.to_numpy()
            log.info("ablation %s done", name)
    out.to_parquet(PRED_DIR / f"ablation_h{h}.parquet")
    save_json(meta, PRED_DIR / "ablation_source_pools.json")


# --------------------------------------------------------------------------- evaluation
def evaluate(cfg):
    scales = mase_scales(cfg)
    rows = []
    for h in cfg["missing_data"]["horizons"]:
        f = PRED_DIR / f"missing_h{h}.parquet"
        if not f.exists():
            continue
        d = pd.read_parquet(f)
        clean = d[d.scenario == "clean"]
        ok = clean.eval_ok & np.isfinite(clean.y)
        keys = set(zip(clean.region[ok].astype(str), clean.time_utc[ok]))
        d = d[[k in keys for k in zip(d.region.astype(str), d.time_utc)]]
        # common scored hours: within a scenario, every strategy/method must have a forecast
        d = d.copy()
        d["_common"] = False
        for sc, gs in d.groupby("scenario"):
            piv = gs.pivot_table(index=["region", "time_utc"], columns="strategy",
                                 values=["LGB_G_IN", "LGB_G_LRO"], observed=True)
            ok = np.isfinite(piv).all(axis=1)
            aug = gs[gs.strategy == "native"].set_index(["region", "time_utc"])["LGB_G_IN_AUG"]
            ok &= np.isfinite(aug.reindex(ok.index))
            common = set(ok.index[ok.to_numpy()])
            d.loc[gs.index, "_common"] = [k in common for k in zip(gs.region, gs.time_utc)]
        for (sc, st), g in d.groupby(["scenario", "strategy"]):
            n_all = len(g)
            g = g[g._common.astype(bool)]
            methods = [m for m in ("LGB_G_IN", "LGB_G_LRO", "LGB_G_IN_AUG") if g[m].notna().any()]
            for m in methods:
                gg = g
                pr = per_region_metrics(gg, [m], scales)
                pr["coverage_of_eval_hours"] = len(gg) / n_all
                pr["h"], pr["scenario"], pr["strategy"] = h, sc, st
                pr["input_missing_share"] = g.input_missing_share.iloc[0]
                rows.append(pr)
    if rows:
        pr = pd.concat(rows, ignore_index=True)
        pr.to_csv(METRIC_DIR / "missing_data_by_region.csv", index=False)
        s = summarise(pr, ["h", "scenario", "strategy", "method"])
        s = s.merge(pr.groupby(["h", "scenario", "strategy", "method"]).agg(
            input_missing_share=("input_missing_share", "first"),
            min_coverage_of_eval_hours=("coverage_of_eval_hours", "min")).reset_index())
        s.to_csv(METRIC_DIR / "missing_data_summary.csv", index=False)
    f = PRED_DIR / "ablation_h24.parquet"
    if f.exists():
        a = pd.read_parquet(f)
        p = pd.read_parquet(PRED_DIR / "point_h24.parquet")
        p = p[p.split == "test"][["region", "time_utc", "LGB_G_LRO", "LGB_G_IN"]]
        a = a.merge(p, on=["region", "time_utc"])
        methods = [c for c in a.columns if c not in ("region", "time_utc", "y", "eval_ok", "scale")]
        a = a[a.eval_ok & np.isfinite(a[methods]).all(axis=1)]
        pr = per_region_metrics(a, methods, scales)
        pr["h"] = 24
        pr.to_csv(METRIC_DIR / "ablation_by_region.csv", index=False)
        s = summarise(pr, ["method"])
        tests = compare_methods(pr, "nMAE", [(m, "LGB_G_LRO") for m in methods if m != "LGB_G_LRO"],
                                cfg["statistics"]["bootstrap_reps"], cfg["seed"])
        s = s.merge(tests.rename(columns={"method_a": "method"})[
            ["method", "median_rel_change", "rel_ci_lo", "rel_ci_hi", "p", "p_holm", "share_a_better"]],
            on="method", how="left")
        s.to_csv(METRIC_DIR / "ablation_results.csv", index=False)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["missing", "ablation", "evaluate"])
    a = ap.parse_args(argv)
    cfg = load_config()
    {"missing": run_missing, "ablation": run_ablation, "evaluate": evaluate}[a.stage](cfg)


if __name__ == "__main__":
    main()
