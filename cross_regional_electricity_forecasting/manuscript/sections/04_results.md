# Results

All results refer to the 2024–2025 test period unless stated otherwise. They are computed on the {{data.n_regions}} BAs, using hours where the label is unflagged and every compared method has a forecast. This covers more than 99.5% of test hours at every horizon.

## Point accuracy and the geographic generalisation gap (RQ1)

Table {tab:table_01_point_accuracy} and Fig. {fig:fig05_accuracy} summarise per-BA accuracy.

**Day-ahead horizon.** At $h = 24$ h the global LightGBM model trained on all BAs (G-IN) attains a median nMAE of {{point.h24.LGB_G_IN.nMAE_median}}% (MASE {{point.h24.LGB_G_IN.MASE_median}}). The same model class with the evaluated BA held out (G-LRO, zero-shot) attains {{point.h24.LGB_G_LRO.nMAE_median}}%, against {{point.h24.LGB_L.nMAE_median}}% for local models trained on four years of each BA's own data, {{point.h24.RIDGE_G_IN.nMAE_median}}% for pooled ridge regression and {{point.h24.SN24.nMAE_median}}% for the 24-h seasonal naive.

**Shorter horizons.** At $h = 6$ h the medians are {{point.h6.LGB_G_IN.nMAE_median}}% (G-IN), {{point.h6.LGB_G_LRO.nMAE_median}}% (G-LRO) and {{point.h6.LGB_L.nMAE_median}}% (local). At $h = 1$ h they are {{point.h1.LGB_G_IN.nMAE_median}}%, {{point.h1.LGB_G_LRO.nMAE_median}}% and {{point.h1.LGB_L.nMAE_median}}%.

[[TABLE:table_01_point_accuracy]]

[[FIGURE:fig05_accuracy]]

**Size of the gap.** The cost of never having seen a BA is small but systematic (Table {tab:table_02_paired_tests}). At $h = 24$ h the median per-BA relative increase in nMAE from G-IN to G-LRO is {{test.h24.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% (95% bootstrap CI {{test.h24.nMAE.LGB_G_LRO.LGB_G_IN.rel_ci_lo}} to {{test.h24.nMAE.LGB_G_LRO.LGB_G_IN.rel_ci_hi}}%). The held-out model is better in only {{test.h24.nMAE.LGB_G_LRO.LGB_G_IN.share_a_better}}% of BAs. The gap grows as the horizon shrinks: {{test.h6.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% at 6 h and {{test.h1.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% at 1 h (CI {{test.h1.nMAE.LGB_G_LRO.LGB_G_IN.rel_ci_lo}} to {{test.h1.nMAE.LGB_G_LRO.LGB_G_IN.rel_ci_hi}}%). The moving-block bootstrap shows that the in-region model is significantly better within {{block.h1.LGB_G_LRO.LGB_G_IN.share_b_better_sig}}% of BAs at 1 h but only {{block.h24.LGB_G_LRO.LGB_G_IN.share_b_better_sig}}% at 24 h.

**Distribution across BAs.** The median hides a tail (Fig. {fig:fig06_regional_errors}).

- At $h = 1$ h the gap exceeds 5% in {{revgap.h1.LGB_G_LRO.LGB_G_IN.share_gt_5pct}}% of BAs. The 90th percentile is {{revgap.h1.LGB_G_LRO.LGB_G_IN.p90_rel}}% and the maximum {{revgap.h1.LGB_G_LRO.LGB_G_IN.max_rel}}% ({{revgap.h1.LGB_G_LRO.LGB_G_IN.argmax}}). MISO, the second-largest BA, also shows a gap of {{derived.h1.gap.MISO}}% at this horizon.
- At $h = 6$ h the maximum is {{revgap.h6.LGB_G_LRO.LGB_G_IN.max_rel}}% ({{revgap.h6.LGB_G_LRO.LGB_G_IN.argmax}}).
- At $h = 24$ h the 90th percentile is {{revgap.h24.LGB_G_LRO.LGB_G_IN.p90_rel}}% and the maximum {{revgap.h24.LGB_G_LRO.LGB_G_IN.max_rel}}% ({{revgap.h24.LGB_G_LRO.LGB_G_IN.argmax}}).

The gap is weakly related to BA size (correlation with log mean demand {{derived.h24.corr_gap_logsize}} at 24 h). Per-BA errors of the zero-shot model range from {{derived.h24.best_ba_lro_nmae}}% ({{derived.h24.best_ba_lro}}) to {{derived.h24.worst_ba_lro_nmae}}% ({{derived.h24.worst_ba_lro}}) at 24 h, a spread much larger than the median gap.

**Robustness to spatial correlation.** Resampling the nine spatial blocks of Section 11.3 instead of individual BAs gives 95% intervals for the median gap of {{revgap.h24.LGB_G_LRO.LGB_G_IN.cluster_ci_lo}} to {{revgap.h24.LGB_G_LRO.LGB_G_IN.cluster_ci_hi}}% at 24 h and {{revgap.h1.LGB_G_LRO.LGB_G_IN.cluster_ci_lo}} to {{revgap.h1.LGB_G_LRO.LGB_G_IN.cluster_ci_hi}}% at 1 h.

**Global versus local.** Pooling helps more than locality does. The median per-BA relative change in nMAE from local models to G-IN is {{test.h24.nMAE.LGB_G_IN.LGB_L.median_rel_change}}% at 24 h (CI {{test.h24.nMAE.LGB_G_IN.LGB_L.rel_ci_lo}} to {{test.h24.nMAE.LGB_G_IN.LGB_L.rel_ci_hi}}%) and {{test.h1.nMAE.LGB_G_IN.LGB_L.median_rel_change}}% at 1 h (negative values favour the global model). The *zero-shot* G-LRO model, which has never seen the target BA, compares with local models trained on four years of that BA's data as follows.

- **At $h = 1$ h and $h = 6$ h it is more accurate:** median relative change {{test.h1.nMAE.LGB_G_LRO.LGB_L.median_rel_change}}% (CI {{test.h1.nMAE.LGB_G_LRO.LGB_L.rel_ci_lo}} to {{test.h1.nMAE.LGB_G_LRO.LGB_L.rel_ci_hi}}%) and {{test.h6.nMAE.LGB_G_LRO.LGB_L.median_rel_change}}%.
- **At $h = 24$ h the difference is small and not significant:** {{test.h24.nMAE.LGB_G_LRO.LGB_L.median_rel_change}}% (CI {{test.h24.nMAE.LGB_G_LRO.LGB_L.rel_ci_lo}} to {{test.h24.nMAE.LGB_G_LRO.LGB_L.rel_ci_hi}}%; Holm-adjusted $p$ {{test.h24.nMAE.LGB_G_LRO.LGB_L.p_holm_all}}). With a 1% non-inferiority margin, chosen post hoc, the 90% cluster-bootstrap interval ({{reveq.h24.1.cluster_ci90_lo}} to {{reveq.h24.1.cluster_ci90_hi}}%) supports non-inferiority but not equivalence.
- **By year at 24 h,** the paired difference is {{revyear.h24.2024.LGB_G_LRO.LGB_L.median_rel_change}}% in 2024 and {{revyear.h24.2025.LGB_G_LRO.LGB_L.median_rel_change}}% in 2025. In 2024 the local models have a marginally lower *median level* across BAs (Table {tab:table_05_temporal}), so the zero-shot model matches rather than beats local models at the day-ahead horizon.

**Linear benchmark.** Relative to ridge regression on the same features, G-IN changes nMAE by a median {{test.h24.nMAE.LGB_G_IN.RIDGE_G_IN.median_rel_change}}% at 24 h and {{test.h1.nMAE.LGB_G_IN.RIDGE_G_IN.median_rel_change}}% at 1 h. Ridge regression's own geographic gap is negligible ({{test.h24.nMAE.RIDGE_G_LRO.RIDGE_G_IN.median_rel_change}}% at 24 h), consistent with a low-capacity model that cannot memorise BA-specific patterns.

[[TABLE:table_02_paired_tests]]

[[FIGURE:fig06_regional_errors]]

**Operator reference.** The BAs' own day-ahead forecasts reach a median nMAE of {{ba.h24.BA_DA.nMAE_median}}% on the same hours, against {{ba.h24.LGB_G_IN.nMAE_median}}% for G-IN at 24 h (Table {tab:table_03_ba_reference}). The information sets differ: operators use weather forecasts and other operational information, issue forecasts at undocumented times, and are not restricted to our past-demand features. We therefore do not attribute the difference to any single cause, and the comparison is not like-for-like. For orientation only, the in-region model at $h = 6$ h ({{point.h6.LGB_G_IN.nMAE_median}}%), which has far more recent information than any day-ahead forecast, is more accurate than the operators' day-ahead forecasts.

[[TABLE:table_03_ba_reference]]

## Limited target-data adaptation (RQ2)

Table {tab:table_04_adaptation} and Fig. {fig:fig07_transfer} compare adaptation strategies for unseen BAs.

**Local models need history.** With little target history, local models are poor. At $h = 24$ h, a local model trained on one week reaches a median nMAE of {{adapt.h24.LGB_L_k1.nMAE_median}}%, on four weeks {{adapt.h24.LGB_L_k4.nMAE_median}}% and on thirteen weeks {{adapt.h24.LGB_L_k13.nMAE_median}}%. All of these are worse than the zero-shot global model ({{adapt.h24.LGB_G_LRO.nMAE_median}}%).

**Fine-tuning gives little and usually hurts.** Fine-tuning the global model on the same data yields {{adapt.h24.LGB_FT_k1.nMAE_median}}%, {{adapt.h24.LGB_FT_k4.nMAE_median}}% and {{adapt.h24.LGB_FT_k13.nMAE_median}}% for one, four and thirteen weeks. The median relative change versus zero-shot is {{testadapt.h24.nMAE.LGB_FT_k4.LGB_G_LRO.median_rel_change}}% with four weeks (CI {{testadapt.h24.nMAE.LGB_FT_k4.LGB_G_LRO.rel_ci_lo}} to {{testadapt.h24.nMAE.LGB_FT_k4.LGB_G_LRO.rel_ci_hi}}%) and {{testadapt.h24.nMAE.LGB_FT_k13.LGB_G_LRO.median_rel_change}}% with thirteen. The exception is $h = 1$ h with thirteen weeks, where fine-tuning helps slightly ({{testadapt.h1.nMAE.LGB_FT_k13.LGB_G_LRO.median_rel_change}}%, CI {{testadapt.h1.nMAE.LGB_FT_k13.LGB_G_LRO.rel_ci_lo}} to {{testadapt.h1.nMAE.LGB_FT_k13.LGB_G_LRO.rel_ci_hi}}%).

**The degradation is not specific to a December origin.** We repeated the experiment at three onboarding origins inside the test period: 1 April, 1 July and 1 October 2024, each evaluated over the following year. Fine-tuning remained worse than zero-shot at every origin. Median relative changes ranged from +{{revorigrange.h24.FT.min}}% to +{{revorigrange.h24.FT.max}}% at 24 h, and from +{{revorigrange.h6.FT.min}}% to +{{revorigrange.h6.FT.max}}% at 6 h (Supplementary Table S5). These adaptation settings were fixed a priori; better-regularised adaptation might behave differently.

[[TABLE:table_04_adaptation]]

[[FIGURE:fig07_transfer]]

## Temporal distribution shift (RQ4)

**Drift with model age.** Errors of models frozen at the end of 2022 did not grow monotonically with their age (Table {tab:table_05_temporal}; Fig. {fig:fig08_temporal_shift}). At $h = 24$ h the median nMAE of G-IN was {{temporal.h24.year.2023_(validation).LGB_G_IN.nMAE_median}}% in 2023 (validation year, mildly optimistic because it includes the early-stopping weeks), {{temporal.h24.year.2024.LGB_G_IN.nMAE_median}}% in 2024 and {{temporal.h24.year.2025.LGB_G_IN.nMAE_median}}% in 2025. The seasonal naive benchmark follows the same pattern ({{temporal.h24.year.2024.SN24.nMAE_median}}% in 2024 and {{temporal.h24.year.2025.SN24.nMAE_median}}% in 2025), which indicates that 2025 was intrinsically harder to forecast rather than that the models aged. The increase from 2024 to 2025 was largest for local models ({{temporal.h24.year.2024.LGB_L.nMAE_median}}% to {{temporal.h24.year.2025.LGB_L.nMAE_median}}%), compared with the zero-shot model ({{temporal.h24.year.2024.LGB_G_LRO.nMAE_median}}% to {{temporal.h24.year.2025.LGB_G_LRO.nMAE_median}}%) and G-IN.

**Seasonal pattern.** Errors are highest in winter and summer and lowest in autumn: at 24 h, G-IN reaches {{temporal.h24.season.DJF.LGB_G_IN.nMAE_median}}% in DJF, {{temporal.h24.season.JJA.LGB_G_IN.nMAE_median}}% in JJA and {{temporal.h24.season.SON.LGB_G_IN.nMAE_median}}% in SON. This pattern reflects weather-driven heating and cooling load that calendar and lag features cannot anticipate.

**Effect of refitting.** Refitting on data through 2023 and evaluating on 2025 (Table {tab:table_06_refit}) leaves the median nMAE of G-IN essentially unchanged ({{refit.h24.LGB_G_IN.nMAE_median}}% frozen, {{refit.h24.LGB_G_IN_refit.nMAE_median}}% refit), and of local models from {{refit.h24.LGB_L.nMAE_median}}% to {{refit.h24.LGB_L_refit.nMAE_median}}%. The median per-BA relative change is {{testrefit.h24.nMAE.LGB_G_IN_refit.LGB_G_IN.median_rel_change}}% for G-IN (Holm $p$ {{testrefit.h24.nMAE.LGB_G_IN_refit.LGB_G_IN.p_holm}}) and {{testrefit.h24.nMAE.LGB_L_refit.LGB_L.median_rel_change}}% for local models (Holm $p$ {{testrefit.h24.nMAE.LGB_L_refit.LGB_L.p_holm}}). Refitting thus benefits local models, which gain a fifth year of their own data, but not the pooled model, which already has abundant data.

[[TABLE:table_05_temporal]]

[[TABLE:table_06_refit]]

[[FIGURE:fig08_temporal_shift]]

## Interval calibration under geographic and temporal shift (RQ3)

Table {tab:table_07_probabilistic} and Fig. {fig:fig09_calibration} report interval calibration.

**Calibration fails BA by BA, not on average.** The static methods are close to nominal *on average* but not *per BA*. At $h = 24$ h and nominal 90%, CQR calibrated on source BAs achieves a mean coverage of {{prob.h24.unseen-region.90.CQR.all.coverage_mean}}% for unseen BAs, yet coverage ranges down to {{prob.h24.unseen-region.90.CQR.all.coverage_min}}%. In {{prob.h24.unseen-region.90.CQR.all.share_regions_undercover_5pp}}% of BAs it is more than 5 percentage points below nominal. Raw quantile regression under-covers more (mean {{prob.h24.unseen-region.90.QR.all.coverage_mean}}%), and symmetric SCP has the widest spread across BAs (minimum {{prob.h24.unseen-region.90.SCP.all.coverage_min}}%).

**Geographic shift matters little for calibration.** Unseen-region intervals behave almost identically to in-region ones: in-region CQR reaches a mean of {{prob.h24.in-region.90.CQR.all.coverage_mean}}% and under-covers in {{prob.h24.in-region.90.CQR.all.share_regions_undercover_5pp}}% of BAs. The binding problem is *heterogeneity across BAs and over time*, not the absence of the BA from training.

**Target calibration from recent weeks fails.** Calibrating on the target BA's own last four weeks (SCP-T4) *reduces* mean coverage to {{prob.h24.unseen-region.90.SCP-T4.all.coverage_mean}}%. Four December weeks are not exchangeable with the following two years.

**Temporal drift lowers coverage.** Static coverage declines from 2024 to 2025: CQR falls from {{prob.h24.unseen-region.90.CQR.2024.coverage_mean}}% to {{prob.h24.unseen-region.90.CQR.2025.coverage_mean}}% (Fig. {fig:fig09_calibration}c).

**Online recalibration: what ACI does and does not show.** ACI is guaranteed by construction to reach the nominal long-run coverage for each stream, so per-BA coverage close to 90% is expected rather than an empirical finding. The empirical questions are how sharp the resulting intervals are, how they behave conditionally, and how the step size should be chosen without test data.

**The frozen-protocol step size is too large.** With the frozen-protocol step size $\gamma = 0.005$ and 24-h feedback delay, the threshold had to be capped at the largest score seen in a mean of {{acicap.h24.unseen-region.90.ACI-CQR}}% of hours. The median interval score rose to {{prob.h24.unseen-region.90.ACI-CQR.all.interval_score_norm_median}}% of mean load, against {{prob.h24.unseen-region.90.CQR.all.interval_score_norm_median}}% for CQR.

**Step size chosen on source BAs only (ACI-CQR-S).** After the internal review we selected $\gamma$ separately for each fold from $\{0, 0.0005, 0.001, 0.002, 0.005, 0.01\}$, using only the source BAs' calibration weeks. The selected values were {{revgamma.unseen_random_folds.h24}} at 24 h and {{revgamma.unseen_random_folds.h1}} at 1 h (Table 8).

- *Coverage.* ACI-CQR-S keeps mean coverage at {{revcal.unseen_random_folds.h24.ACI-CQR-S.coverage_mean}}% with a minimum of {{revcal.unseen_random_folds.h24.ACI-CQR-S.coverage_min}}% across BAs at 24 h.
- *Sharpness.* Its median interval score ({{revcal.unseen_random_folds.h24.ACI-CQR-S.IS_median}}%) is close to that of static CQR ({{revcal.unseen_random_folds.h24.CQR.IS_median}}%), and its median hourly width is {{revcal.unseen_random_folds.h24.ACI-CQR-S.width_p50_median}}% of mean load.
- *Hour-ahead.* At 1 h, ACI-CQR-S reaches a minimum coverage of {{revcal.unseen_random_folds.h1.ACI-CQR-S.coverage_min}}% and a median interval score of {{revcal.unseen_random_folds.h1.ACI-CQR-S.IS_median}}%, against {{revcal.unseen_random_folds.h1.CQR.IS_median}}% for CQR.

**The adaptive update is what helps.** A $\gamma = 0$ control, which keeps adding observed target scores to the calibration pool without adapting $\alpha_t$, under-covers like static CQR: minimum {{revcal.unseen_random_folds.h24.ACI-CQR_g0.coverage_min}}%, with {{revcal.unseen_random_folds.h24.ACI-CQR_g0.share_under_5pp}}% of BAs more than 5 points below nominal. The benefit therefore comes from the adaptive update, not from pooling target scores. The variant whose $\gamma$ was chosen on the held-out BAs' own 2023 data (ACI-CQR-V; exploratory, see Section 15) gives similar results.

**Rolling target calibration.** A simple rolling alternative is split conformal prediction on each BA's most recent four weeks of observed residuals (SCP-R4).

- *Day-ahead.* It is also well calibrated per BA (mean {{revcal.unseen_random_folds.h24.SCP-R4.coverage_mean}}%, minimum {{revcal.unseen_random_folds.h24.SCP-R4.coverage_min}}%), but less sharp: median interval score {{revcal.unseen_random_folds.h24.SCP-R4.IS_median}}% against {{revcal.unseen_random_folds.h24.ACI-CQR-S.IS_median}}% for ACI-CQR-S.
- *Hour-ahead.* It is competitive (minimum coverage {{revcal.unseen_random_folds.h1.SCP-R4.coverage_min}}%; median interval score {{revcal.unseen_random_folds.h1.SCP-R4.IS_median}}% against {{revcal.unseen_random_folds.h1.ACI-CQR-S.IS_median}}%).

What matters is therefore online use of recent target feedback; the particular online scheme is secondary.

**Spatially blocked folds.** Under spatial blocking (Section 11.3), static CQR covers {{revcal.unseen_spatial_blocks.h24.CQR.coverage_mean}}% on average (minimum {{revcal.unseen_spatial_blocks.h24.CQR.coverage_min}}%) and ACI-CQR-S {{revcal.unseen_spatial_blocks.h24.ACI-CQR-S.coverage_mean}}% (minimum {{revcal.unseen_spatial_blocks.h24.ACI-CQR-S.coverage_min}}%). The calibration conclusions are thus unchanged when whole regions are new.

**Conditional coverage.** Marginal coverage hides conditional deviations (Supplementary Table S8).

- *Season.* For ACI-CQR-S at 24 h, mean coverage across BAs is {{revcond.unseen_random_folds.h24.ACI-CQR-S.season.DJF.mean}}% in winter and {{revcond.unseen_random_folds.h24.ACI-CQR-S.season.JJA.mean}}% in summer.
- *Load level.* In the top load decile of each BA it is {{revcond.unseen_random_folds.h24.ACI-CQR-S.decile.9.mean}}%, against {{revcond.unseen_random_folds.h24.CQR.decile.9.mean}}% for CQR.
- *Daily peaks.* At the daily peak hour, the observed load exceeds the upper 90% bound on {{revpeak.unseen_random_folds.above_upper.CQR}}% of days for CQR and {{revpeak.unseen_random_folds.above_upper.ACI-CQR-S}}% for ACI-CQR-S. A calibrated central 90% interval would be exceeded from above on 5% of hours, so peak-hour upper-tail risk is under-stated by roughly a factor of two. This matters for reserve sizing.

**Peak-hour point accuracy.** The daily-peak absolute percentage error of the zero-shot point forecast has a median across BAs of {{revpeak.unseen_random_folds.APE_zero_shot_median}}%, against {{revpeak.unseen_random_folds.APE_BA_DA_median}}% for the operators' day-ahead forecasts.

**Post-hoc sensitivity.** Supplementary Table S2 gives the test-set sensitivity of ACI to $\gamma$. It was not used for any selection.

[[TABLE:table_07_probabilistic]]

[[TABLE:table_08_calibration_revision]]


[[FIGURE:fig09_calibration]]

[[FIGURE:fig10_interval_example]]
