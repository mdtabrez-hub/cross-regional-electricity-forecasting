"""Conformal interval constructions on the normalised scale z = y / s_o.

* split conformal (SCP): symmetric interval zhat +/- q, q the finite-sample-corrected
  (1-alpha) quantile of |z - zhat| on a calibration set.
* conformalised quantile regression (CQR, Romano et al. 2019): [q_lo - c, q_hi + c],
  c the corrected quantile of max(q_lo - z, z - q_hi).
* adaptive conformal inference (ACI, Gibbs & Candes 2021) run online per region on top
  of a conformity-score stream, with feedback delayed by the forecast horizon h because
  the outcome for target t is only observed at time t (h hours after the forecast).
"""
from __future__ import annotations

import numpy as np


def conformal_quantile(scores: np.ndarray, alpha: float) -> float:
    scores = np.asarray(scores, float)
    scores = scores[np.isfinite(scores)]
    n = len(scores)
    if n == 0:
        return np.nan
    k = int(np.ceil((n + 1) * (1 - alpha)))
    if k > n:
        return np.inf
    return float(np.sort(scores)[k - 1])


def scp_scores(z, zhat):
    return np.abs(z - zhat)


def cqr_scores(z, qlo, qhi):
    return np.maximum(qlo - z, z - qhi)


def aci_intervals(scores_cal: np.ndarray, scores_stream: np.ndarray, alpha: float, gamma: float,
                  delay: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Online ACI over a chronologically ordered stream for one region.

    Returns per-step thresholds q_t, effective alpha_t and a boolean mask of capped steps.
    At step t the threshold is the (1 - alpha_t) empirical quantile of the calibration
    scores plus all stream scores whose outcomes are already observed (index <= t - delay).
    alpha_t is updated with the miscoverage indicator of step t - delay (outcome known at
    time t). When alpha_t leaves (0, 1) the exact ACI interval is the whole real line
    (alpha_t <= 0) or empty (alpha_t >= 1); we cap the threshold at the largest / smallest
    score seen so far so that widths and interval scores stay finite, and report the share
    of capped steps. The miscoverage update uses the capped threshold actually issued.
    """
    import bisect

    n = len(scores_stream)
    q = np.empty(n)
    a_hist = np.empty(n)
    capped = np.zeros(n, bool)
    alpha_t = alpha
    hist = list(np.sort(scores_cal[np.isfinite(scores_cal)]))
    for t in range(n):
        j = t - delay
        if j >= 0:
            s_j = scores_stream[j]
            if np.isfinite(s_j):
                err = float(s_j > q[j])
                alpha_t = alpha_t + gamma * (alpha - err)
                bisect.insort(hist, s_j)
        a_hist[t] = alpha_t
        m = len(hist)
        k = int(np.ceil((m + 1) * (1 - alpha_t))) if 0 < alpha_t < 1 else (m + 1 if alpha_t <= 0 else 0)
        if k > m:
            q[t], capped[t] = hist[-1], True
        elif k < 1:
            q[t], capped[t] = hist[0], True
        else:
            q[t] = hist[k - 1]
    return q, a_hist, capped
