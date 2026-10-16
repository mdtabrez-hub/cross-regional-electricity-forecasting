# Statistical and Robustness Audit (Agent 6)

Scope: experimental design, leakage, metric implementation, inference, and interpretation.
Inputs reviewed: `src/*.py`, `configs/experiment.yaml`, `results/metrics/*.csv`, `DECISION_LOG.md`.

## 1. Leakage and split validity

| Check | Finding | Verdict |
|---|---|---|
| Future information in features | Every feature uses `x` at indices ≤ origin o = t − h (shift by h then by lag); scale uses trailing window ending at o. `tests/test_pipeline.py::test_features_do_not_use_future` perturbs all inputs after o (×5) for h ∈ {1,6,24} and asserts identical features. | Pass |
| Input screening | Causal rolling median (`shift(1)`); test checks earlier decisions unchanged when the future changes. PUDL two-sided flags used only to choose scored hours, never as inputs. | Pass |
| Label imputation | Imputed hours excluded from training loss and scoring (`eval_ok`). | Pass |
| Train/validation/test overlap | Disjoint chronological spans (unit test). Lags of the first test hours reach into Dec 2023 (inputs only) — legitimate. | Pass |
| Held-out regions | LRO models fitted, early-stopped and calibrated on source BAs only (`run_point`: `trs`, `vas`, `sc` filtered by `src`). | Pass |
| Calibration independence | Conformal calibration on even ISO weeks of 2023, never used for fitting or early stopping. Ridge has no early stopping. | Pass |
| Hyper-parameter selection | Grid on odd ISO weeks of 2023 (VAL-ES) only (`hyperparameter_grid_validation.json`). | Pass |
| Adaptation windows | Last k weeks of 2023, restricted to labels observable at test start (t ≤ test_start − h). | Pass |
| ACI feedback | Score of step t − h used at step t (delay = h); unit test asserts no update before t = delay. | Pass |
| Post-freeze changes | D9–D13 logged with motivation. D10 (ACI-CQR-V) was motivated by test-set behaviour although γ is chosen on validation data: residual selection risk acknowledged in the manuscript (Threats to validity). | Pass with caveat |

## 2. Metric implementation

Unit tests check MAE, RMSE, nMAE, MASE, bias, pinball, coverage and interval score against
hand-computed values; conformal quantile finite-sample correction and ACI long-run coverage
are tested on synthetic data. MASE uses the training-period 24-h seasonal naive MAE on
unflagged labels. Interval metrics now abort on non-finite bounds (D9) — previously NaN
interval scores were silently skipped by `pandas.mean`, which would have misreported ACI.
Headline h = 24 medians are recomputed independently from raw predictions by `src/qa_checks.py`.

## 3. Fairness of comparisons

* Identical feature sets and information sets for all learned models within a horizon;
  identical scored (BA, hour) pairs for all compared methods (common mask, > 99.5% of hours).
* Learning rate differs across horizons (D13) but not across methods within a horizon.
* Local models received their own hyper-parameter grid; adaptation models used fixed,
  untuned small-tree settings (limitation, stated).
* BA day-ahead forecasts differ in information set — reported as reference only.
* Persistence equals SN24 at h = 24 by construction (reported, not double-counted in claims).

## 4. Inference

* Unit of analysis = BA (n = 48), each weighted equally; medians with IQR.
* Paired Wilcoxon signed-rank tests, Holm-adjusted over all reported point comparisons
  (8 method pairs × 3 metrics × 3 horizons = 72 tests) — conservative.
* Effect sizes: median per-BA relative change with percentile bootstrap over BAs (1000).
* Temporal dependence: per-BA moving-block bootstrap (168-h blocks) of the hourly
  normalised absolute-error differential.
* **Caveat — spatial dependence**: BAs share weather and interconnections; Wilcoxon p-values
  assume independent BAs and are therefore optimistic. Conclusions rely on effect sizes,
  consistency of sign across BAs and horizons, and block-bootstrap results rather than p-values.
* Diebold–Mariano tests were not used (block bootstrap preferred for non-normal, heavy-tailed
  hourly loss differentials); the manuscript states this.

## 5. Practical significance

* The geographic gap (≈0.5–3.4% relative; ≈0.03–0.1 percentage points of nMAE) is
  statistically clear but practically small compared with between-BA dispersion (IQR of
  nMAE ≈ 2 percentage points at 24 h) and with the weather-information gap to operator forecasts.
* Interval under-coverage of > 5 points in 20–50% of BAs is practically important for reserve sizing.
* Fine-tuning degradation (+6% to +16% relative at 24 h) is practically important and robust in sign.

## 6. Unsupported or risky statements (to avoid)

* "Zero-shot beats local" at 24 h — the CI includes zero; say "not worse".
* "ACI guarantees coverage" — guarantee is long-run and asymptotic; per-BA coverage is empirical.
* Any causal explanation for the BA-specific gaps (GCPD, MISO at 1 h) — not investigated.
* "Missing data is harmless" — only the tested corruption mechanisms and rates.
* Superiority over operator forecasts — not supported (operators are better at 24 h).

## 7. Outstanding items

* Missing-data and ablation results to be audited when available (see `robustness_report.md`).
* Spatially aware inference (e.g., cluster bootstrap by interconnection) could be added in revision.
