# Experimental Protocol (frozen in version control before test evaluation; not externally registered)

Status: **FROZEN** before test evaluation. All settings in `configs/experiment.yaml`.

## Splits

| Purpose | Period (UTC, hour-ending) |
|---|---|
| Training | 2019-01-01 01:00 – 2023-01-01 00:00 |
| Validation (hyper-parameters, early stopping, conformal calibration, adaptation data) | 2023; odd ISO weeks = early-stopping/selection set (VAL-ES), even ISO weeks = conformal calibration set (VAL-CAL) |
| Test (touched once, after freeze) | 2024-01-01 01:00 – 2026-01-01 00:00 |
| Rolling-origin refit | train ≤ 2023, validate 2024, test 2025 |

Data after 2025 (available up to 2026-09) are not used.

## Geographic folds (leave-regions-out)

Regions are ranked by mean demand and dealt in blocks of six; within each block the six
regions are randomly permuted (seed 20261016) and assigned to folds 0–5. This gives six
folds of eight BAs with similar size distributions. For fold f, LRO models are trained,
early-stopped and calibrated using only the 40 regions not in f; regions in f are
evaluated on the test period.

## Experiments

* **E1 Point accuracy & geographic gap (RQ1).** All point methods, h ∈ {1,6,24}.
  Geographic generalisation gap = metric(LGB-G-LRO) − metric(LGB-G-IN) on the same regions
  and hours; local-vs-global comparison LGB-L vs LGB-G-IN.
* **E2 Limited-data adaptation (RQ2).** For held-out regions: LGB-G-LRO (k=0), LGB-L-k,
  LGB-FT-k with k ∈ {1,4,13} weeks taken from the end of 2023; references LGB-L, LGB-G-IN.
* **E3 Temporal shift (RQ4).** Validation-year vs test-year error; 2024 vs 2025 error of
  frozen models; frozen vs refit (rolling origin) on 2025 for LGB-G-IN and LGB-L;
  seasonal breakdown (DJF/MAM/JJA/SON).
* **E4 Probabilistic calibration (RQ3).** QR, SCP, CQR, SCP-T4, ACI for in-region and LRO
  models, h ∈ {1,6,24}; coverage/width/interval score by region, year and season.
* **E5 Missing-data robustness (RQ4).** Test-period inputs corrupted (targets untouched):
  MCAR rates {5,10,20,40}% and random outage blocks of 24 h / 168 h covering ~10 % of
  hours; strategies: LightGBM native missing handling, causal last-observation-carried-
  forward imputation, causal weekly-seasonal imputation, and a model trained with 10 %
  MCAR augmentation. h ∈ {1,24}; LGB-G-IN and LGB-G-LRO. Corruption seeds fixed.
* **E6 Ablations (h=24, LRO).** Without calendar features; without weekly lags; without
  recent-lag block beyond lag 0–3; source-pool size {5,10,20} regions (3 random draws) vs 40.
* **E7 Computational cost (RQ5).** Training/inference time, model size, peak RSS.

## Rules

1. The test period is used only for final scoring; no model, hyper-parameter, feature or
   calibration choice depends on it.
2. All methods are scored on the identical set of (region, hour) pairs.
3. Negative and null results are reported.
4. BA-DA has a different information set (issued day-ahead with weather forecasts,
   issuance time unknown) and is reported as an operational reference only.

## Amendments after the freeze (see DECISION_LOG D9–D12)

* ACI thresholds are capped at the most extreme score seen when α_t ∉ (0,1); the share of
  capped hours is reported.
* ACI-CQR-V: ACI with γ chosen on the 2023 validation year of held-out BAs, added after the
  frozen-protocol γ = 0.005 was seen to produce very wide intervals on the test set. Reported
  alongside, not instead of, the frozen-protocol variant.
* Median-hour interval width added as a sharpness metric.
