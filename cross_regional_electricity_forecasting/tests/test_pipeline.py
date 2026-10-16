"""Unit tests: leakage resistance, metric definitions, conformal guarantees, splits."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import metrics as M  # noqa: E402
from src.common import load_config  # noqa: E402
from src.conformal import aci_intervals, conformal_quantile  # noqa: E402
from src.features import FeatureBuilder, feature_columns  # noqa: E402
from src.preprocess_data import causal_clean  # noqa: E402

CFG = load_config()


def synthetic_panel(n_days=40, regions=("AAA", "BBB"), seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-01-01 01:00", periods=24 * n_days, freq="h")
    parts = []
    for j, r in enumerate(regions):
        base = (j + 1) * 1000
        y = base * (1 + 0.3 * np.sin(2 * np.pi * np.arange(len(idx)) / 24)) + rng.normal(0, 10, len(idx))
        parts.append(pd.DataFrame({"region": r, "time_utc": idx, "reported": y, "target": y,
                                   "ba_forecast": y, "imputation_code": None, "eval_ok": True,
                                   "x_input": y}))
    p = pd.concat(parts, ignore_index=True)
    p["region"] = p["region"].astype("category")
    return p, {r: "America/New_York" for r in regions}


@pytest.mark.parametrize("h", [1, 6, 24])
def test_features_do_not_use_future(h):
    panel, tz = synthetic_panel()
    fb = FeatureBuilder(panel, tz, CFG)
    base = fb.build(h)
    cols = feature_columns(base) + ["scale", "seasonal_naive_24", "seasonal_naive_168", "persistence"]
    # Perturb all inputs strictly after the origin of target index t* and verify features at t* unchanged.
    t_star = 24 * 30
    origin = t_star - h
    X2 = fb.X.copy()
    X2[:, origin + 1:] *= 5.0
    pert = fb.build(h, x=X2)
    a = base[base.time_utc == fb.times[t_star]][cols].to_numpy(float)
    b = pert[pert.time_utc == fb.times[t_star]][cols].to_numpy(float)
    np.testing.assert_allclose(a, b, equal_nan=True)


def test_features_change_when_past_changes():
    panel, tz = synthetic_panel()
    fb = FeatureBuilder(panel, tz, CFG)
    base = fb.build(24)
    X2 = fb.X.copy()
    X2[:, 24 * 30 - 24] *= 2.0  # the origin value itself
    pert = fb.build(24, x=X2)
    t = fb.times[24 * 30]
    assert not np.allclose(base[base.time_utc == t]["lag_0"], pert[pert.time_utc == t]["lag_0"])


def test_target_normalisation_roundtrip():
    panel, tz = synthetic_panel()
    df = FeatureBuilder(panel, tz, CFG).build(6).dropna(subset=["z"])
    np.testing.assert_allclose(df.z * df.scale, df.y, rtol=1e-5)


def test_causal_clean_is_past_only():
    rng = np.random.default_rng(1)
    x = pd.Series(1000 + rng.normal(0, 5, 500))
    x[300] = 10000  # spike
    c = causal_clean(x, CFG)
    assert np.isnan(c[300])
    x2 = x.copy()
    x2[400:] = 1e6  # future change must not alter earlier decisions
    c2 = causal_clean(x2, CFG)
    np.testing.assert_array_equal(np.isnan(c[:400]), np.isnan(c2[:400]))
    assert np.isnan(causal_clean(pd.Series([1.0, -1.0, 0.0]), CFG)[1:]).all()


def test_point_metrics():
    y = np.array([10.0, 20.0, 30.0])
    f = np.array([12.0, 18.0, 33.0])
    assert M.mae(y, f) == pytest.approx(7 / 3)
    assert M.rmse(y, f) == pytest.approx(np.sqrt((4 + 4 + 9) / 3))
    assert M.nmae(y, f) == pytest.approx((7 / 3) / 20)
    assert M.mase(y, f, 2.0) == pytest.approx(7 / 6)
    assert M.bias_pct(y, f) == pytest.approx(1.0 / 20)  # mean(f - y) = (2 - 2 + 3) / 3 = 1


def test_pinball_and_interval_score():
    y = np.array([0.0, 1.0])
    assert M.pinball(y, np.array([1.0, 1.0]), 0.9) == pytest.approx((0.1 * 1 + 0) / 2)
    # y inside -> width only; y below lower -> width + 2/alpha*gap
    assert M.interval_score(np.array([5.0]), np.array([4.0]), np.array([6.0]), 0.1) == pytest.approx(2.0)
    assert M.interval_score(np.array([3.0]), np.array([4.0]), np.array([6.0]), 0.1) == pytest.approx(2 + 20)
    assert M.coverage(np.array([1, 5, 9.0]), np.array([0, 0, 0.0]), np.array([6, 6, 6.0])) == pytest.approx(2 / 3)


def test_seasonal_naive_scale():
    y = np.tile(np.arange(24.0), 3)
    assert M.seasonal_naive_scale(y) == 0.0
    y2 = np.arange(48.0)
    assert M.seasonal_naive_scale(y2) == pytest.approx(24.0)


def test_conformal_quantile_coverage_exchangeable():
    rng = np.random.default_rng(0)
    covs = []
    for _ in range(200):
        s = np.abs(rng.normal(size=300))
        q = conformal_quantile(s[:200], 0.1)
        covs.append(np.mean(s[200:] <= q))
    assert np.mean(covs) >= 0.89


def test_conformal_quantile_small_n_is_infinite():
    assert conformal_quantile(np.array([1.0, 2.0]), 0.1) == np.inf


def test_aci_recovers_coverage_under_shift():
    rng = np.random.default_rng(0)
    cal = np.abs(rng.normal(size=500))
    stream = np.abs(rng.normal(scale=2.0, size=6000))  # scores inflate after calibration
    q, _ = aci_intervals(cal, stream, alpha=0.1, gamma=0.01, delay=24)
    cov_static = np.mean(stream <= conformal_quantile(cal, 0.1))
    cov_aci = np.mean(stream[1000:] <= q[1000:])
    assert cov_static < 0.75
    assert abs(cov_aci - 0.9) < 0.03


def test_aci_respects_delay():
    cal = np.ones(50)
    stream = np.r_[np.full(10, 100.0), np.ones(10)]
    q, a = aci_intervals(cal, stream, alpha=0.1, gamma=0.05, delay=5)
    # alpha cannot change before the first outcome is revealed at t = delay
    assert np.all(a[:5] == 0.1)
    assert a[5] < 0.1


def test_config_splits_are_ordered_and_disjoint():
    sp = CFG["splits"]
    tr_end, va_start = pd.Timestamp(sp["train"][1]), pd.Timestamp(sp["valid"][0])
    va_end, te_start = pd.Timestamp(sp["valid"][1]), pd.Timestamp(sp["test"][0])
    assert tr_end < va_start <= va_end < te_start
