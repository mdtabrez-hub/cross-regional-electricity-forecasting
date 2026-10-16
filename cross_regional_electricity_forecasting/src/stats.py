"""Statistical comparison utilities respecting temporal and cross-region dependence."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def holm(pvals: np.ndarray) -> np.ndarray:
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj


def wilcoxon_paired(a: np.ndarray, b: np.ndarray) -> dict:
    """Paired Wilcoxon signed-rank on per-region metrics (a vs b); negative diff favours a."""
    d = np.asarray(a) - np.asarray(b)
    d = d[np.isfinite(d)]
    if len(d) < 5 or np.allclose(d, 0):
        return {"n": len(d), "stat": np.nan, "p": np.nan, "median_diff": float(np.median(d)) if len(d) else np.nan,
                "share_a_better": float(np.mean(d < 0)) if len(d) else np.nan}
    res = stats.wilcoxon(d, zero_method="wilcox", alternative="two-sided")
    return {"n": len(d), "stat": float(res.statistic), "p": float(res.pvalue), "median_diff": float(np.median(d)),
            "share_a_better": float(np.mean(d < 0))}


def bootstrap_median_rel(a: np.ndarray, b: np.ndarray, reps: int = 1000, seed: int = 0) -> tuple[float, float, float]:
    """Median over regions of (a/b - 1) with a percentile bootstrap CI resampling regions."""
    rel = np.asarray(a) / np.asarray(b) - 1
    rel = rel[np.isfinite(rel)]
    rng = np.random.default_rng(seed)
    boots = [np.median(rng.choice(rel, len(rel), replace=True)) for _ in range(reps)]
    return float(np.median(rel)), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def moving_block_bootstrap_mean(d: np.ndarray, block: int = 168, reps: int = 1000, seed: int = 0) -> tuple[float, float, float]:
    """Mean of a (hourly, chronologically ordered) loss differential with a moving-block
    bootstrap percentile CI (Kuensch 1989). NaNs are dropped before resampling."""
    d = np.asarray(d, float)
    d = d[np.isfinite(d)]
    n = len(d)
    if n < 2 * block:
        return float(np.mean(d)) if n else np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(n / block))
    starts_max = n - block + 1
    csum = np.r_[0.0, np.cumsum(d)]
    block_means = (csum[block:] - csum[:-block]) / block  # mean of each possible block
    means = np.empty(reps)
    for i in range(reps):
        s = rng.integers(0, starts_max, nb)
        means[i] = block_means[s].mean()
    return float(d.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def compare_methods(per_region: pd.DataFrame, metric: str, pairs: list[tuple[str, str]], reps: int, seed: int) -> pd.DataFrame:
    """per_region: rows region x method with column `metric`. Returns Holm-adjusted table."""
    rows = []
    piv = per_region.pivot(index="region", columns="method", values=metric)
    for a, b in pairs:
        if a not in piv or b not in piv:
            continue
        w = wilcoxon_paired(piv[a].to_numpy(), piv[b].to_numpy())
        med, lo, hi = bootstrap_median_rel(piv[a].to_numpy(), piv[b].to_numpy(), reps, seed)
        rows.append({"method_a": a, "method_b": b, "metric": metric, **w, "median_rel_change": med,
                     "rel_ci_lo": lo, "rel_ci_hi": hi})
    out = pd.DataFrame(rows)
    if len(out):
        out["p_holm"] = holm(out["p"].fillna(1.0).to_numpy())
    return out
