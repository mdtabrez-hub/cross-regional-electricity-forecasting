# Methodology Specification

Status: **FROZEN** before any test-period (2024–2025) evaluation. Frozen at the git commit
that first adds this file; later changes are listed in `DECISION_LOG.md`.

## 1. Forecasting problem

* Unit: a U.S. balancing authority (BA) reporting to EIA Form 930. A BA's "demand" is the
  hourly energy (MWh, numerically equal to average MW over the hour) computed by the BA as
  metered net generation minus net interchange.
* Resolution: hourly, timestamps in UTC, hour-ending convention (EIA-930/PUDL).
* Task: direct point and probabilistic forecasting of `y_t` at horizons
  `h ∈ {1, 6, 24}` hours from origin `o = t − h`, using demand observed up to `o` and
  calendar information for `t`. One model per horizon (direct strategy).
* No exogenous weather inputs are used (not available in the dataset; a stated
  limitation). All methods receive identical information sets.

## 2. Data and labels

* Source: PUDL v2026.10.0 table `out_eia930__hourly_operations` (EIA-930 with PUDL
  screening/imputation; Ruggles et al., 2020 methodology).
* Label `y_t` = `demand_imputed_pudl_mwh`. Training and scoring use only hours with no PUDL
  imputation code (`eval_ok`), i.e. retained reported values. Imputed hours are never scored.
* Model inputs `x` = reported demand after a causal screen: non-positive values → missing;
  values > 2.5× or < 0.25× the trailing 168-h median (computed on strictly earlier hours,
  ≥ 24 observations) → missing. No future information enters any input.

## 3. Region selection (pre-specified)

Included BAs: not generation-only; interconnection ∈ {Eastern, Western, ERCOT}; active
through 2025; reported-demand coverage ≥ 97 % of hours in 2019–2025; PUDL-flagged share
≤ 5 %; no PUDL "bad_year"; mean demand ≥ 200 MW; known reporting time zone. Result:
48 BAs (see `data/processed/regions.csv`).

## 4. Normalisation and features

Instance scale `s_o = mean(x_{o−167..o})` (≥ 24 non-missing values). The model target is
`z_t = y_t / s_o`; forecasts are `ŷ_t = ẑ_t · s_o`. Features (all divided by `s_o`):
24 most recent values `x_{o−k}, k=0..23`; same-hour values `x_{t−24m}` for
`m = ⌈h/24⌉, ⌈h/24⌉+1`; weekly lags `x_{t−168}, x_{t−336}`; trailing 24-h mean/min/max and
168-h standard deviation at `o`; share of missing inputs in the last 24 h. Calendar
features of the interval start in the BA's reporting time zone: hour, day of week, month,
day-of-year sine/cosine, weekend, U.S. federal holiday. No region identifier and no
absolute-level feature is used, so every model can be applied to unseen regions.

## 5. Methods

| ID | Description | Trained on |
|---|---|---|
| SN24 | Seasonal naive: `x_{t−24⌈h/24⌉}` (causally forward-filled) | – |
| SN168 | Weekly seasonal naive `x_{t−168}` | – |
| PERS | Persistence `x_{t−h}` | – |
| RIDGE-G | Ridge regression (one-hot hour/dow/month, standardised numerics), pooled | source regions |
| LGB-L | LightGBM per region (local) | target region 2019–2022 |
| LGB-G-IN | LightGBM pooled over all 48 regions ("global, in-region") | all regions 2019–2022 |
| LGB-G-LRO | LightGBM pooled, target fold held out (zero-shot unseen region) | 40 source regions |
| RIDGE-G-LRO | Ridge pooled, target fold held out | 40 source regions |
| LGB-L-k | Local LightGBM trained only on the last k weeks of 2023 of the target | k ∈ {1,4,13} weeks |
| LGB-FT-k | LGB-G-LRO continued with 200 trees (lr 0.02) on the last k weeks of target data | source + k weeks |
| BA-DA | BA's own reported day-ahead forecast (reference, not a like-for-like competitor) | – |

LightGBM point models use the L1 objective (targets the conditional median of `z`,
consistent with MAE). Hyper-parameters are chosen on the 2023 validation year only (grid
in `configs/experiment.yaml`) with early stopping on the validation year; in LRO runs the
early-stopping set contains source regions only.

Probabilistic methods (nominal 90 % and 50 % central intervals; quantiles
τ ∈ {0.05, 0.25, 0.5, 0.75, 0.95}):

* QR: LightGBM quantile models.
* SCP: split conformal on |z − ẑ| of the point model; calibration = even ISO weeks of the
  2023 validation year (VAL-CAL, never used for fitting or early stopping) of the models'
  training regions (for LRO: source regions only).
* CQR: conformalised quantile regression, same calibration set.
* SCP-T4: SCP calibrated on the last 4 weeks of 2023 of the target region (limited
  target data; for LRO this is the only target-region information used).
* ACI: adaptive conformal inference on CQR scores, online per region, γ = 0.005,
  feedback delayed by h hours, initialised with the source calibration scores.

## 6. Metrics

For region r with evaluation hours T_r (test period ∩ eval_ok ∩ all methods available):

* MAE = mean|y−ŷ|; RMSE = sqrt(mean(y−ŷ)²); nMAE = MAE / mean(y); nRMSE = RMSE / mean(y).
* MASE = MAE / mean_{t∈train}|y_t − y_{t−24}| (training-period 24-h seasonal-naive scale).
* MAPE reported only as a secondary metric (demand is strictly positive here).
* Bias% = mean(ŷ−y)/mean(y).
* Pinball loss ρ_τ(u) = max(τu, (τ−1)u), averaged over τ grid (normalised by mean(y)); this
  approximates CRPS on the quantile grid.
* Interval coverage, mean width (normalised by mean(y)), interval (Winkler) score
  IS_α = (u−l) + (2/α)(l−y)1{y<l} + (2/α)(y−u)1{y>u}.
* Calibration dispersion across regions: mean |coverage_r − (1−α)|.
* Compute: wall-clock training and inference time, model size (serialised bytes), peak RSS.

Cross-region aggregates are medians and means over regions of per-region metrics (each
region weighted equally) — not pooled MWh, which would be dominated by PJM/MISO/ERCOT.

## 7. Statistical analysis

* Paired comparison across regions: Wilcoxon signed-rank test on per-region nMAE,
  Holm-adjusted within each family of comparisons; effect size = median relative change.
* Temporal dependence: per-region moving-block bootstrap (block 168 h, 1000 replicates)
  of the mean loss differential; we report the share of regions with a 95 % CI excluding 0.
* Cross-region uncertainty: bootstrap over regions (1000 replicates) for median relative
  improvements.
* Caveat: BAs are spatially correlated (shared weather, interconnection), so region-level
  tests overstate effective sample size; results are interpreted descriptively.
