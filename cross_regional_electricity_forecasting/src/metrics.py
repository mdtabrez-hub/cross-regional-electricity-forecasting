"""Forecast evaluation metrics (definitions in docs/methodology_specification.md)."""
from __future__ import annotations

import numpy as np


def mae(y, f):
    return float(np.mean(np.abs(y - f)))


def rmse(y, f):
    return float(np.sqrt(np.mean((y - f) ** 2)))


def nmae(y, f):
    """MAE divided by the mean of the observed series over the same evaluation hours."""
    return mae(y, f) / float(np.mean(np.abs(y)))


def nrmse(y, f):
    return rmse(y, f) / float(np.mean(np.abs(y)))


def mase(y, f, scale):
    """MAE divided by the in-sample (training period) MAE of the 24-h seasonal naive."""
    return mae(y, f) / scale


def mape(y, f):
    return float(np.mean(np.abs((y - f) / y)))


def bias_pct(y, f):
    return float(np.mean(f - y) / np.mean(y))


def pinball(y, q, tau):
    d = y - q
    return float(np.mean(np.maximum(tau * d, (tau - 1) * d)))


def coverage(y, lo, hi):
    return float(np.mean((y >= lo) & (y <= hi)))


def interval_score(y, lo, hi, alpha):
    """Winkler/interval score (Gneiting & Raftery 2007); lower is better."""
    width = hi - lo
    below = (2 / alpha) * (lo - y) * (y < lo)
    above = (2 / alpha) * (y - hi) * (y > hi)
    return float(np.mean(width + below + above))


def seasonal_naive_scale(y_train: np.ndarray, m: int = 24) -> float:
    """Mean absolute 24-h seasonal difference on the training series (NaN-aware)."""
    d = np.abs(y_train[m:] - y_train[:-m])
    return float(np.nanmean(d))


def point_metrics(y, f, scale_mase) -> dict:
    return {
        "MAE": mae(y, f),
        "RMSE": rmse(y, f),
        "nMAE": nmae(y, f),
        "nRMSE": nrmse(y, f),
        "MASE": mase(y, f, scale_mase),
        "MAPE": mape(y, f),
        "bias_pct": bias_pct(y, f),
        "n": int(len(y)),
    }
