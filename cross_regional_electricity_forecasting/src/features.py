"""Leakage-resistant direct multi-horizon feature construction.

For a target hour t and horizon h the forecast origin is o = t - h. Every input feature is
computed from ``x_input`` at indices <= o (past-only) or from deterministic calendar
information about t. Inputs and the target are divided by an *instance scale*
s_o = mean(x_input[o-167 .. o]) so a single model can be shared across regions whose
demand differs by three orders of magnitude, and so that a region never seen in
training can be forecast without any region-specific statistics.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

CAL_COLS = ["hour", "dow", "month", "doy_sin", "doy_cos", "is_weekend", "is_holiday"]


def to_matrix(panel: pd.DataFrame, col: str) -> tuple[np.ndarray, list[str], pd.DatetimeIndex]:
    """Reshape a long panel (regions x identical hourly index) to an (R, N) matrix."""
    piv = panel.pivot(index="time_utc", columns="region", values=col)
    regions = list(piv.columns.astype(str))
    return piv.to_numpy(dtype=float).T, regions, piv.index


def shift(a: np.ndarray, k: int) -> np.ndarray:
    """Shift along time axis: out[:, i] = a[:, i-k] (NaN-padded). k >= 0 looks back."""
    out = np.full_like(a, np.nan)
    if k == 0:
        return a.copy()
    out[:, k:] = a[:, :-k]
    return out


def rolling_stat(a: np.ndarray, w: int, fn: str, min_obs: int = 1) -> np.ndarray:
    """Trailing window statistic including the current index (past-only)."""
    df = pd.DataFrame(a.T)
    r = df.rolling(w, min_periods=min_obs)
    res = getattr(r, fn)()
    return res.to_numpy().T


def calendar_features(times_utc: pd.DatetimeIndex, tz: str) -> pd.DataFrame:
    # EIA-930 timestamps are hour-ending; use the start of the interval for local calendar.
    start_local = (times_utc - pd.Timedelta("1h")).tz_localize("UTC").tz_convert(tz)
    local_date = start_local.tz_localize(None).normalize()
    hol = USFederalHolidayCalendar().holidays(local_date.min(), local_date.max())
    doy = start_local.dayofyear.to_numpy()
    return pd.DataFrame(
        {
            "hour": start_local.hour.to_numpy(),
            "dow": start_local.dayofweek.to_numpy(),
            "month": start_local.month.to_numpy(),
            "doy_sin": np.sin(2 * np.pi * doy / 365.25),
            "doy_cos": np.cos(2 * np.pi * doy / 365.25),
            "is_weekend": (start_local.dayofweek >= 5).astype(int),
            "is_holiday": local_date.isin(hol).astype(int),
        }
    )


class FeatureBuilder:
    def __init__(self, panel: pd.DataFrame, region_tz: dict[str, str], cfg: dict):
        self.cfg = cfg
        self.X, self.regions, self.times = to_matrix(panel, "x_input")
        self.Y, _, _ = to_matrix(panel, "target")
        self.OK, _, _ = to_matrix(panel, "eval_ok")
        self.BAF, _, _ = to_matrix(panel, "ba_forecast")
        self.OK = np.nan_to_num(self.OK, nan=0).astype(bool)
        self.cal = {r: calendar_features(self.times, region_tz[r]) for r in self.regions}

    def build(self, h: int, x: np.ndarray | None = None, row_mask_times: np.ndarray | None = None,
              regions: list[str] | None = None) -> pd.DataFrame:
        """Return a long feature frame for horizon h.

        x: optionally a corrupted copy of the input matrix (missing-data experiments).
        row_mask_times: boolean mask over self.times restricting the returned target hours.
        """
        fc = self.cfg["features"]
        X = self.X if x is None else x
        scale = rolling_stat(X, fc["scale_window_h"], "mean", fc["scale_min_obs"])
        feats: dict[str, np.ndarray] = {}
        # features indexed at origin o = t - h  -> shift by h to align with target t
        s_o = shift(scale, h)
        for k in range(fc["n_recent_lags"]):
            feats[f"lag_{k}"] = shift(X, h + k) / s_o
        m0 = math.ceil(h / 24)
        for m in (m0, m0 + 1):
            feats[f"day_lag_{m}"] = shift(X, 24 * m) / s_o
        for w in fc["weekly_lags"]:
            if w >= h:
                feats[f"week_lag_{w}"] = shift(X, w) / s_o
        feats["roll_mean_24"] = shift(rolling_stat(X, 24, "mean", 6), h) / s_o
        feats["roll_min_24"] = shift(rolling_stat(X, 24, "min", 6), h) / s_o
        feats["roll_max_24"] = shift(rolling_stat(X, 24, "max", 6), h) / s_o
        feats["roll_std_168"] = shift(rolling_stat(X, 168, "std", 24), h) / s_o
        feats["miss_frac_24"] = shift(rolling_stat(np.isnan(X).astype(float), 24, "mean", 1), h)

        R, N = X.shape
        Xf = pd.DataFrame(X.T).ffill().to_numpy().T  # causal fill used only by naive baselines
        sel_regions = self.regions if regions is None else regions
        tmask = np.ones(N, bool) if row_mask_times is None else row_mask_times
        frames = []
        for r in sel_regions:
            i = self.regions.index(r)
            d = pd.DataFrame({k: v[i, tmask] for k, v in feats.items()})
            if self.cfg["features"]["calendar"]:
                cal = self.cal[r].loc[tmask].reset_index(drop=True)
                d = pd.concat([d, cal], axis=1)
            d["region"] = r
            d["time_utc"] = self.times[tmask]
            d["scale"] = s_o[i, tmask]
            d["y"] = self.Y[i, tmask]
            d["z"] = d["y"] / d["scale"]
            d["eval_ok"] = self.OK[i, tmask]
            d["ba_forecast"] = self.BAF[i, tmask]
            d["seasonal_naive_24"] = shift(Xf[i:i + 1], 24 * m0)[0, tmask]
            d["seasonal_naive_168"] = shift(Xf[i:i + 1], 168)[0, tmask]
            d["persistence"] = shift(Xf[i:i + 1], h)[0, tmask]
            frames.append(d)
        out = pd.concat(frames, ignore_index=True)
        float_cols = [c for c in out.columns if out[c].dtype == np.float64 and c not in ("y", "scale", "ba_forecast")]
        out[float_cols] = out[float_cols].astype(np.float32)
        return out


def feature_columns(df: pd.DataFrame, drop: tuple[str, ...] = ()) -> list[str]:
    non = {"region", "time_utc", "scale", "y", "z", "eval_ok", "ba_forecast",
           "seasonal_naive_24", "seasonal_naive_168", "persistence"}
    cols = [c for c in df.columns if c not in non]
    for pat in drop:
        cols = [c for c in cols if not c.startswith(pat)]
    return cols
