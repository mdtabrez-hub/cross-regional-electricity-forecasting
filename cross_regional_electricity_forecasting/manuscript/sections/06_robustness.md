# Robustness and ablation analysis

## Missing input observations (RQ4)

Table {tab:table_9_missing_data} and Fig. {fig:fig11_missing_data} report accuracy when test-period inputs are corrupted while labels are left intact.

**Day-ahead forecasts degrade modestly.** At $h = 24$ h, with 10% of input hours missing completely at random (MCAR), the median nMAE of G-IN rises from {{missing.h24.clean.native.LGB_G_IN.nMAE_median}}% to {{missing.h24.MCAR_10.native.LGB_G_IN.nMAE_median}}% with LightGBM's native missing-value handling. It rises to {{missing.h24.MCAR_40.native.LGB_G_IN.nMAE_median}}% when 40% of inputs are missing.

**Hour-ahead forecasts are far more sensitive,** because they rely on the most recent observation. With native handling, 10% MCAR raises the median nMAE from {{missing.h1.clean.native.LGB_G_IN.nMAE_median}}% to {{missing.h1.MCAR_10.native.LGB_G_IN.nMAE_median}}%, and 40% MCAR to {{missing.h1.MCAR_40.native.LGB_G_IN.nMAE_median}}%.

**The best imputation strategy depends on the gap pattern.**

- For scattered MCAR gaps, causal last-observation-carried-forward imputation is better than native handling ({{missing.h1.MCAR_10.locf.LGB_G_IN.nMAE_median}}% at 10% MCAR, $h = 1$ h).
- For contiguous outages it is worse: with 168-h blocks at $h = 1$ h it reaches {{missing.h1.BLOCK_168h.locf.LGB_G_IN.nMAE_median}}%, against {{missing.h1.BLOCK_168h.native.LGB_G_IN.nMAE_median}}% (native) and {{missing.h1.BLOCK_168h.seasonal.LGB_G_IN.nMAE_median}}% (weekly-seasonal imputation).

**Training with masked inputs is the most effective remedy.** A model trained with 10% MCAR input masking reaches {{missing.h1.MCAR_10.native.LGB_G_IN_AUG.nMAE_median}}% at 10% MCAR and {{missing.h1.MCAR_40.native.LGB_G_IN_AUG.nMAE_median}}% at 40% MCAR ($h = 1$ h). On clean inputs it costs {{missing.h1.clean.native.LGB_G_IN_AUG.nMAE_median}}% versus {{missing.h1.clean.native.LGB_G_IN.nMAE_median}}%. That is a relative penalty of a few per cent, similar in size to the 1-h geographic gap, which is the price of robustness. Augmentation was tested for the in-region model only.

**Unseen BAs behave the same way.** The zero-shot model degrades in the same way as the in-region model (e.g., {{missing.h1.MCAR_10.native.LGB_G_LRO.nMAE_median}}% at 10% MCAR, $h = 1$ h), so missing data does not interact with geographic shift.

**Unscored hours.** In the most severe scenarios the instance scale cannot be computed for some origins, because fewer than 24 of the preceding 168 hours are observed, and no forecast is issued. All strategies within a scenario are scored on the common set of hours where every strategy issued a forecast; in the worst BA and scenario {{missing.min_scored_pct}}% of hours remain. Real EIA-930 gaps are clustered rather than uniformly random, so the MCAR and uniform-outage scenarios are stylised.

[[TABLE:table_9_missing_data]]

[[FIGURE:fig11_missing_data]]

## Ablations of the zero-shot model

Table {tab:table_10_ablation} and Fig. {fig:fig12_ablation} report ablations for unseen BAs at $h = 24$ h. Each is measured as the median per-BA relative change in nMAE against the full zero-shot model.

**Feature groups.** The changes are:

- removing calendar features: {{ablation.no_calendar.median_rel_change}}% (95% CI {{ablation.no_calendar.rel_ci_lo}} to {{ablation.no_calendar.rel_ci_hi}}%);
- removing the weekly lags: {{ablation.no_weekly_lags.median_rel_change}}% (CI {{ablation.no_weekly_lags.rel_ci_lo}} to {{ablation.no_weekly_lags.rel_ci_hi}}%);
- keeping only the four most recent lags: {{ablation.recent_lags_0_3_only.median_rel_change}}% (CI {{ablation.recent_lags_0_3_only.rel_ci_lo}} to {{ablation.recent_lags_0_3_only.rel_ci_hi}}%).

**Source-pool size.** Shrinking the source pool from 40 BAs to 20, 10 or 5 randomly drawn BAs gives median nMAEs of {{ablationpool.20.nMAE_median}}%, {{ablationpool.10.nMAE_median}}% and {{ablationpool.5.nMAE_median}}% (averages over three draws), against {{ablation.LGB_G_LRO.nMAE_median}}% with all 40 sources. Results vary little across draws (with five sources, {{ablationpool.5.nMAE_min}}–{{ablationpool.5.nMAE_max}}%), so the size of the pool, rather than its particular composition, drives the loss.

[[TABLE:table_10_ablation]]

[[FIGURE:fig12_ablation]]

## Spatially blocked evaluation (post-review)

The random, size-stratified folds of the main analysis keep neighbouring and same-utility BAs of a held-out BA in the training set, so they measure transfer within a covered geography. They may therefore understate the cost of a geographically new region.

**Design.** We repeated the zero-shot experiment with nine spatial blocks: the EIA regions NW, CAL, SW, FLA and CAR, and four merged groups of adjacent single-BA regions (TEX+CENT, MIDW+MIDA, SE+TEN, NE+NY). Every BA in a held-out block is excluded from fitting, early stopping and calibration (Supplementary Table S6).

**Day-ahead results.** At $h = 24$ h the spatially blocked model (G-LRS) attains a median nMAE of {{revsp.h24.LGB_G_LRS.nMAE_median}}%, against {{revsp.h24.LGB_G_LRO.nMAE_median}}% for random folds and {{revsp.h24.LGB_G_IN.nMAE_median}}% in-region.

- The median relative gap to the in-region model roughly triples, to {{revsptest.h24.LGB_G_LRS.LGB_G_IN.median_rel_change}}% (CI {{revsptest.h24.LGB_G_LRS.LGB_G_IN.rel_ci_lo}} to {{revsptest.h24.LGB_G_LRS.LGB_G_IN.rel_ci_hi}}%).
- The 90th percentile of the gap is {{revsptail.h24.p90_rel}}% and the maximum {{revsptail.h24.max_rel}}% ({{revsptail.h24.argmax}}).
- The spatially blocked model remains statistically indistinguishable from local models trained on four years of target data ({{revsptest.h24.LGB_G_LRS.LGB_L.median_rel_change}}%, CI {{revsptest.h24.LGB_G_LRS.LGB_L.rel_ci_lo}} to {{revsptest.h24.LGB_G_LRS.LGB_L.rel_ci_hi}}%).

**Hour-ahead results.** At $h = 1$ h the cost of spatial novelty is much larger.

- The spatially blocked gap is {{revsptest.h1.LGB_G_LRS.LGB_G_IN.median_rel_change}}% (CI {{revsptest.h1.LGB_G_LRS.LGB_G_IN.rel_ci_lo}} to {{revsptest.h1.LGB_G_LRS.LGB_G_IN.rel_ci_hi}}%), against {{test.h1.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% with random folds.
- The gap exceeds 10% in {{revsptail.h1.share_gt_10pct}}% of BAs, with a maximum of {{revsptail.h1.max_rel}}% ({{revsptail.h1.argmax}}).
- The intraday advantage of zero-shot over local models disappears: {{revsptest.h1.LGB_G_LRS.LGB_L.median_rel_change}}%, CI {{revsptest.h1.LGB_G_LRS.LGB_L.rel_ci_lo}} to {{revsptest.h1.LGB_G_LRS.LGB_L.rel_ci_hi}}%.

Neighbouring BAs in the training pool thus explain much of the intraday transfer seen with random folds.

The geographic cost is therefore larger when whole regions are new, especially intraday, although even then the zero-shot model was not worse than local models trained on four years of the target BA's data. Calibration under spatial blocking is reported in Table 8.

## Small and lower-quality BAs (post-review)

The selection criteria excluded five BAs that report demand through 2025: HST, SPA and WAUW (below 200 MW), and PSEI and SEC (data-quality criteria). Applying the in-region model, which never saw these BAs, gives day-ahead median nMAEs of:

- {{revexcl.h24.HST.nMAE_zero_shot}}% for HST;
- {{revexcl.h24.WAUW.nMAE_zero_shot}}% for WAUW;
- {{revexcl.h24.SEC.nMAE_zero_shot}}% for SEC;
- {{revexcl.h24.PSEI.nMAE_zero_shot}}% for PSEI;
- {{revexcl.h24.SPA.nMAE_zero_shot}}% for SPA, a 22 MW federal power-marketing area.

These are comparable to local models trained on the same BAs' own history (Supplementary Table S7) but far above the errors of the study BAs. The headline accuracy figures should therefore not be extrapolated to very small systems.

# Computational complexity

All experiments ran on a 4-core CPU with 15 GB of memory (Table {tab:table_11_compute}; Fig. {fig:fig13_compute}).

**Training time.** At $h = 24$ h the pooled LightGBM model trained in {{compute.h24.LGB_G_IN.fit_seconds}} s on about 1.7 million rows, with model size {{compute.h24.LGB_G_IN.size_mb}} MB. The 48 local models together took {{compute.h24.LGB_L_48_models.fit_seconds}} s, and ridge regression took {{compute.h24.RIDGE_G_IN.fit_seconds}} s.

**Shorter horizons.** At $h = 1$ h the pooled model used the full 3,000-tree budget ({{compute.h1.LGB_G_IN.fit_seconds}} s; {{compute.h1.LGB_G_IN.size_mb}} MB), and the 48 local models together took {{compute.h1.LGB_L_48_models.fit_seconds}} s. Inference was correspondingly slower: {{compute.h1.LGB_G_IN.inference_us}} µs per forecast, against {{compute.h24.LGB_G_IN.inference_us}} µs at 24 h. Wall-clock times were measured on a shared virtual machine and are indicative only. In particular, the 6-h in-region fit ({{compute.h6.LGB_G_IN.fit_seconds}} s) overlapped with a concurrent evaluation job; the six leave-regions-out fits at the same horizon, which ran without contention, averaged {{compute.h6.LGB_G_LRO.fit_seconds}} s.

**Adaptation and calibration.** Fine-tuning on four weeks of target data took {{compute.h24.LGB_FT_k4.fit_seconds_per_region}} s per BA at 24 h. Conformal calibration and ACI updates are negligible by comparison: a sort of the calibration scores, plus one quantile lookup per forecast.

**Overall cost.** The full study, including all horizons, folds, quantile models and robustness experiments, ran in roughly six hours of wall-clock time. In operation, a single pooled model per horizon replaces dozens of local models and their maintenance.

[[TABLE:table_11_compute]]

[[FIGURE:fig13_compute]]
