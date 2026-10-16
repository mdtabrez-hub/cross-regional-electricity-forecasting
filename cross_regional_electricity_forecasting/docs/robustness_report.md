# Robustness Report (Agent 6)

All values are medians across 48 BAs on the 2024–2025 test period, generated from
`results/metrics/*.csv` (via `results/manuscript_numbers.json`).

## Sensitivity to horizon
| Horizon | G-IN nMAE % | G-LRO nMAE % | Local nMAE % | Geographic gap (median rel., %) | 95% CI |
|---|---|---|---|---|---|
| 1 h | 1.14 | 1.17 | 1.28 | 3.4 | [2.5, 4.6] |
| 6 h | 3.50 | 3.66 | 3.78 | 1.9 | [1.6, 2.3] |
| 24 h | 4.64 | 4.75 | 4.72 | 0.5 | [0.4, 0.7] |

## Sensitivity to region
* Largest 24-h geographic gap: GCPD (6.6%); smallest -0.2%.
* Correlation of the 24-h gap with log mean demand: -0.25 (weak).
* Zero-shot per-BA nMAE at 24 h ranges 2.47% (GCPD) to 8.55% (AECI).

## Sensitivity to season and year (h = 24 h, G-IN)
* DJF 4.76%, MAM 4.64%, JJA 4.76%, SON 4.34%.
* 2023 (validation) 4.60%, 2024 4.54%, 2025 4.67%; the seasonal-naive benchmark shows the same 2025 increase, so 2025 was harder rather than models ageing.
* Refit (train through 2023) on 2025: G-IN unchanged; local models improve (median -0.9%).

## Sensitivity to missing inputs (native NaN handling unless stated)
| Scenario | h = 1 G-IN | h = 1 G-IN (MCAR-trained) | h = 24 G-IN | h = 24 G-IN (MCAR-trained) |
|---|---|---|---|---|
| clean | 1.14 | 1.17 | 4.64 | 4.65 |
| MCAR_5 | 1.47 | 1.25 | 4.84 | 4.68 |
| MCAR_10 | 1.84 | 1.32 | 5.05 | 4.72 |
| MCAR_20 | 2.56 | 1.52 | 5.62 | 4.87 |
| MCAR_40 | 4.04 | 2.29 | 6.93 | 5.40 |
| BLOCK_24h | 1.89 | 1.71 | 5.02 | 4.94 |
| BLOCK_168h | 1.95 | 1.94 | 5.07 | 5.03 |

Minimum share of scored hours in any BA/scenario: 96.9% (instance scale undefined when < 24 of 168 hours observed).

## Calibration robustness (90% intervals, unseen BAs)
| Method | h = 24 mean cov. % | h = 24 min cov. % | h = 24 BAs under-covered > 5 pp % | h = 1 mean cov. % | h = 1 min cov. % |
|---|---|---|---|---|---|
| QR | 87.3 | 76.1 | 29.2 | 83.9 | 64.8 |
| SCP | 88.9 | 71.4 | 29.2 | 87.5 | 52.6 |
| CQR | 89.2 | 78.6 | 20.8 | 88.1 | 69.2 |
| SCP-T4 | 85.3 | 60.8 | 39.6 | 86.9 | 74.3 |
| ACI-CQR | 90.0 | 89.8 | 0.0 | 90.0 | 89.9 |
| ACI-CQR-V | 89.9 | 89.4 | 0.0 | 90.0 | 89.7 |

ACI step-size sensitivity (post hoc, test set): see `results/tables/table_7b_aci_sensitivity.md`.

## Ablations (h = 24 h, unseen BAs; median relative change vs full zero-shot model)
* No calendar features: 6.7% [5.0, 7.0]
* No weekly lags: 0.6% [0.5, 1.3]
* Recent lags 0–3 only: 0.3% [0.1, 0.4]
* Source pool 20 / 10 / 5 BAs: median nMAE 4.81 / 4.87 / 4.97% vs 4.75% with 40.
Full table: `results/metrics/ablation_results.csv`.

## Negative and null findings
* Fine-tuning on 1–13 weeks degraded accuracy at 6 h and 24 h (and at 1 h for 1–4 weeks).
* Target-calibrated SCP (4 weeks) under-covered more than source-calibrated CQR.
* Frozen-protocol ACI (γ = 0.005) produced very wide capped intervals at 24 h.
* Refitting the pooled model with an extra year brought no gain.
* Zero-shot vs local at 24 h: no significant difference (CI includes 0).
