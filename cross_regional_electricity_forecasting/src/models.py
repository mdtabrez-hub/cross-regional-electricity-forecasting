"""Model wrappers. All models predict the scale-normalised target z = y_t / s_o."""
from __future__ import annotations

import time

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

CATEGORICAL = ["hour", "dow", "month"]


def _xy(df: pd.DataFrame, cols: list[str]):
    m = df["eval_ok"].to_numpy() & np.isfinite(df["z"].to_numpy()) & np.isfinite(df["scale"].to_numpy())
    return df.loc[m, cols], df.loc[m, "z"].to_numpy()


def lgb_params(cfg: dict, overrides: dict | None = None, objective: str = "l1", alpha: float | None = None,
               seed: int = 0) -> dict:
    p = dict(cfg["lightgbm"]["fixed"])
    p.pop("n_estimators")
    p.pop("early_stopping_rounds")
    p.update(objective=objective, seed=seed, deterministic=True, force_col_wise=True)
    if alpha is not None:
        p["alpha"] = alpha
    if overrides:
        p.update(overrides)
    return p


def fit_lgb(train: pd.DataFrame, valid: pd.DataFrame | None, cols: list[str], cfg: dict,
            overrides: dict | None = None, objective: str = "l1", alpha: float | None = None,
            seed: int = 0, n_estimators: int | None = None, init_model=None):
    """Fit LightGBM on z with early stopping on ``valid`` (never on test data).

    The point objective is L1 (median of z), which targets MAE; quantile objectives are
    used for probabilistic models.
    """
    Xtr, ytr = _xy(train, cols)
    params = lgb_params(cfg, overrides, objective, alpha, seed)
    dtr = lgb.Dataset(Xtr, ytr, categorical_feature=[c for c in CATEGORICAL if c in cols], free_raw_data=True)
    n_est = n_estimators or cfg["lightgbm"]["fixed"]["n_estimators"]
    callbacks = []
    valid_sets = []
    if valid is not None:
        Xva, yva = _xy(valid, cols)
        dva = lgb.Dataset(Xva, yva, reference=dtr)
        valid_sets = [dva]
        callbacks = [lgb.early_stopping(cfg["lightgbm"]["fixed"]["early_stopping_rounds"], verbose=False)]
    t0 = time.perf_counter()
    booster = lgb.train(params, dtr, num_boost_round=n_est, valid_sets=valid_sets, callbacks=callbacks,
                        init_model=init_model)
    booster.fit_seconds = time.perf_counter() - t0
    booster.n_train_rows = len(ytr)
    return booster


def predict_lgb(booster, df: pd.DataFrame, cols: list[str]) -> np.ndarray:
    return booster.predict(df[cols], num_iteration=booster.best_iteration or None)


def model_size_bytes(booster) -> int:
    return len(booster.model_to_string().encode())


def fit_ridge(train: pd.DataFrame, cols: list[str], alpha: float = 1.0):
    Xtr, ytr = _xy(train, cols)
    num = [c for c in cols if c not in CATEGORICAL]
    cat = [c for c in CATEGORICAL if c in cols]
    pre = ColumnTransformer([
        ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), num),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
    ])
    model = make_pipeline(pre, Ridge(alpha=alpha))
    t0 = time.perf_counter()
    model.fit(Xtr, ytr)
    model.fit_seconds = time.perf_counter() - t0
    model.n_train_rows = len(ytr)
    return model
