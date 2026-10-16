# Results

All results refer to the 2024–2025 test period unless stated otherwise. They are computed on the {{data.n_regions}} BAs, using hours where the label is unflagged and every compared method has a forecast. This covers more than 99.5% of test hours at every horizon.

## Point accuracy and the geographic generalisation gap (RQ1)

Table {tab:table_2_point_accuracy} and Fig. {fig:fig05_accuracy} summarise per-BA accuracy.

**Day-ahead horizon.** At $h = 24$ h the global LightGBM model trained on all BAs (G-IN) attains a median nMAE of {{point.h24.LGB_G_IN.nMAE_median}}% (MASE {{point.h24.LGB_G_IN.MASE_median}}). The same model class with the evaluated BA held out (G-LRO, zero-shot) attains {{point.h24.LGB_G_LRO.nMAE_median}}%, against {{point.h24.LGB_L.nMAE_median}}% for local models trained on four years of each BA's own data, {{point.h24.RIDGE_G_IN.nMAE_median}}% for pooled ridge regression and {{point.h24.SN24.nMAE_median}}% for the 24-h seasonal naive.

**Shorter horizons.** At $h = 6$ h the medians are {{point.h6.LGB_G_IN.nMAE_median}}% (G-IN), {{point.h6.LGB_G_LRO.nMAE_median}}% (G-LRO) and {{point.h6.LGB_L.nMAE_median}}% (local). At $h = 1$ h they are {{point.h1.LGB_G_IN.nMAE_median}}%, {{point.h1.LGB_G_LRO.nMAE_median}}% and {{point.h1.LGB_L.nMAE_median}}%.

[[TABLE:table_2_point_accuracy]]

[[FIGURE:fig05_accuracy]]

**Size of the gap.** The cost of never having seen a BA is small but systematic (Table {tab:table_3_paired_tests}). At $h = 24$ h the median per-BA relative increase in nMAE from G-IN to G-LRO is {{test.h24.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% (95% bootstrap CI {{test.h24.nMAE.LGB_G_LRO.LGB_G_IN.rel_ci_lo}} to {{test.h24.nMAE.LGB_G_LRO.LGB_G_IN.rel_ci_hi}}%). The held-out model is better in only {{test.h24.nMAE.LGB_G_LRO.LGB_G_IN.share_a_better}}% of BAs. The gap grows as the horizon shrinks: {{test.h6.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% at 6 h and {{test.h1.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% at 1 h (CI {{test.h1.nMAE.LGB_G_LRO.LGB_G_IN.rel_ci_lo}} to {{test.h1.nMAE.LGB_G_LRO.LGB_G_IN.rel_ci_hi}}%). The moving-block bootstrap shows that the in-region model is significantly better within {{block.h1.LGB_G_LRO.LGB_G_IN.share_b_better_sig}}% of BAs at 1 h but only {{block.h24.LGB_G_LRO.LGB_G_IN.share_b_better_sig}}% at 24 h.

**Distribution across BAs.** The gap is concentrated in a few BAs (Fig. {fig:fig06_regional_errors}). The largest relative gap at 24 h is {{derived.h24.gap_max_pct}}% ({{derived.h24.gap_max_ba}}), and the gap is weakly related to BA size (correlation with log mean demand {{derived.h24.corr_gap_logsize}}). Per-BA errors of the zero-shot model range from {{derived.h24.best_ba_lro_nmae}}% ({{derived.h24.best_ba_lro}}) to {{derived.h24.worst_ba_lro_nmae}}% ({{derived.h24.worst_ba_lro}}). This spread across BAs is an order of magnitude larger than the geographic gap itself.

**Global versus local.** Pooling helps more than locality does. The median per-BA relative change in nMAE from local models to G-IN is {{test.h24.nMAE.LGB_G_IN.LGB_L.median_rel_change}}% at 24 h (CI {{test.h24.nMAE.LGB_G_IN.LGB_L.rel_ci_lo}} to {{test.h24.nMAE.LGB_G_IN.LGB_L.rel_ci_hi}}%) and {{test.h1.nMAE.LGB_G_IN.LGB_L.median_rel_change}}% at 1 h (negative values favour the global model). More strikingly, the *zero-shot* G-LRO model, which has never seen the target BA, is not worse than a local model trained on four years of that BA's data. The median relative difference is {{test.h24.nMAE.LGB_G_LRO.LGB_L.median_rel_change}}% at 24 h (CI {{test.h24.nMAE.LGB_G_LRO.LGB_L.rel_ci_lo}} to {{test.h24.nMAE.LGB_G_LRO.LGB_L.rel_ci_hi}}%; Holm-adjusted $p$ = {{test.h24.nMAE.LGB_G_LRO.LGB_L.p_holm_all}}) and {{test.h1.nMAE.LGB_G_LRO.LGB_L.median_rel_change}}% at 1 h (CI {{test.h1.nMAE.LGB_G_LRO.LGB_L.rel_ci_lo}} to {{test.h1.nMAE.LGB_G_LRO.LGB_L.rel_ci_hi}}%).

**Linear benchmark.** Relative to ridge regression on the same features, G-IN changes nMAE by a median {{test.h24.nMAE.LGB_G_IN.RIDGE_G_IN.median_rel_change}}% at 24 h and {{test.h1.nMAE.LGB_G_IN.RIDGE_G_IN.median_rel_change}}% at 1 h. Its own geographic gap is negligible ({{test.h24.nMAE.RIDGE_G_LRO.RIDGE_G_IN.median_rel_change}}% at 24 h), consistent with a low-capacity model that cannot memorise BA-specific patterns.

[[TABLE:table_3_paired_tests]]

[[FIGURE:fig06_regional_errors]]

**Operator reference.** The BAs' own day-ahead forecasts reach a median nMAE of {{ba.h24.BA_DA.nMAE_median}}% on the same hours, against {{ba.h24.LGB_G_IN.nMAE_median}}% for G-IN at 24 h (Table {tab:table_11_ba_reference}). Operators use weather forecasts and our models do not, so this difference mainly reflects the value of weather information at the day-ahead horizon. It is not a like-for-like comparison of methods.

[[TABLE:table_11_ba_reference]]

## Limited target-data adaptation (RQ2)

Table {tab:table_4_adaptation} and Fig. {fig:fig08_transfer} compare adaptation strategies for unseen BAs.

**Local models need history.** With little target history, local models are poor. At $h = 24$ h, a local model trained on one week reaches a median nMAE of {{adapt.h24.LGB_L_k1.nMAE_median}}%, on four weeks {{adapt.h24.LGB_L_k4.nMAE_median}}% and on thirteen weeks {{adapt.h24.LGB_L_k13.nMAE_median}}%. All of these are worse than the zero-shot global model ({{adapt.h24.LGB_G_LRO.nMAE_median}}%).

**Fine-tuning gives little and can hurt.** Fine-tuning the global model on the same data yields {{adapt.h24.LGB_FT_k1.nMAE_median}}%, {{adapt.h24.LGB_FT_k4.nMAE_median}}% and {{adapt.h24.LGB_FT_k13.nMAE_median}}% for one, four and thirteen weeks. The median relative change versus zero-shot is {{testadapt.h24.nMAE.LGB_FT_k4.LGB_G_LRO.median_rel_change}}% with four weeks (CI {{testadapt.h24.nMAE.LGB_FT_k4.LGB_G_LRO.rel_ci_lo}} to {{testadapt.h24.nMAE.LGB_FT_k4.LGB_G_LRO.rel_ci_hi}}%) and {{testadapt.h24.nMAE.LGB_FT_k13.LGB_G_LRO.median_rel_change}}% with thirteen. At $h = 1$ h the corresponding changes are {{testadapt.h1.nMAE.LGB_FT_k4.LGB_G_LRO.median_rel_change}}% and {{testadapt.h1.nMAE.LGB_FT_k13.LGB_G_LRO.median_rel_change}}%.

The adaptation windows end in late December, so they over-represent winter and holiday conditions. This is a realistic feature of onboarding at an arbitrary date, and Section 10 discusses it.

[[TABLE:table_4_adaptation]]

[[FIGURE:fig08_transfer]]

## Temporal distribution shift (RQ4)

**Drift with model age.** Errors of models frozen at the end of 2022 did not grow monotonically with their age (Table {tab:table_5_temporal}; Fig. {fig:fig07_temporal_shift}). At $h = 24$ h the median nMAE of G-IN was {{temporal.h24.year.2023_(validation).LGB_G_IN.nMAE_median}}% in 2023 (validation year, mildly optimistic because it includes the early-stopping weeks), {{temporal.h24.year.2024.LGB_G_IN.nMAE_median}}% in 2024 and {{temporal.h24.year.2025.LGB_G_IN.nMAE_median}}% in 2025. The seasonal naive benchmark follows the same pattern ({{temporal.h24.year.2024.SN24.nMAE_median}}% in 2024 and {{temporal.h24.year.2025.SN24.nMAE_median}}% in 2025), which indicates that 2025 was intrinsically harder to forecast rather than that the models aged. The increase from 2024 to 2025 was largest for local models ({{temporal.h24.year.2024.LGB_L.nMAE_median}}% to {{temporal.h24.year.2025.LGB_L.nMAE_median}}%), compared with the zero-shot model ({{temporal.h24.year.2024.LGB_G_LRO.nMAE_median}}% to {{temporal.h24.year.2025.LGB_G_LRO.nMAE_median}}%) and G-IN.

**Seasonal pattern.** Errors are highest in winter and summer and lowest in autumn: at 24 h, G-IN reaches {{temporal.h24.season.DJF.LGB_G_IN.nMAE_median}}% in DJF, {{temporal.h24.season.JJA.LGB_G_IN.nMAE_median}}% in JJA and {{temporal.h24.season.SON.LGB_G_IN.nMAE_median}}% in SON. This pattern reflects weather-driven heating and cooling load that calendar and lag features cannot anticipate.

**Effect of refitting.** Refitting on data through 2023 and evaluating on 2025 (Table {tab:table_6_refit}) leaves the median nMAE of G-IN essentially unchanged ({{refit.h24.LGB_G_IN.nMAE_median}}% frozen, {{refit.h24.LGB_G_IN_refit.nMAE_median}}% refit), and of local models from {{refit.h24.LGB_L.nMAE_median}}% to {{refit.h24.LGB_L_refit.nMAE_median}}%. The median per-BA relative change is {{testrefit.h24.nMAE.LGB_G_IN_refit.LGB_G_IN.median_rel_change}}% for G-IN (Holm $p$ = {{testrefit.h24.nMAE.LGB_G_IN_refit.LGB_G_IN.p_holm}}) and {{testrefit.h24.nMAE.LGB_L_refit.LGB_L.median_rel_change}}% for local models (Holm $p$ = {{testrefit.h24.nMAE.LGB_L_refit.LGB_L.p_holm}}). Refitting thus benefits local models, which gain a fifth year of their own data, but not the pooled model, which already has abundant data.

[[TABLE:table_5_temporal]]

[[TABLE:table_6_refit]]

[[FIGURE:fig07_temporal_shift]]

## Interval calibration under geographic and temporal shift (RQ3)

Table {tab:table_7_probabilistic} and Fig. {fig:fig09_calibration} report interval calibration.

**Calibration fails BA by BA, not on average.** The static methods are close to nominal *on average* but not *per BA*. At $h = 24$ h and nominal 90%, CQR calibrated on source BAs achieves a mean coverage of {{prob.h24.unseen-region.90.CQR.all.coverage_mean}}% for unseen BAs, yet coverage ranges down to {{prob.h24.unseen-region.90.CQR.all.coverage_min}}%. In {{prob.h24.unseen-region.90.CQR.all.share_regions_undercover_5pp}}% of BAs it is more than 5 percentage points below nominal. Raw quantile regression under-covers more (mean {{prob.h24.unseen-region.90.QR.all.coverage_mean}}%), and symmetric SCP has the widest spread across BAs (minimum {{prob.h24.unseen-region.90.SCP.all.coverage_min}}%).

**Geographic shift matters little for calibration.** Unseen-region intervals behave almost identically to in-region ones: in-region CQR reaches a mean of {{prob.h24.in-region.90.CQR.all.coverage_mean}}% and under-covers in {{prob.h24.in-region.90.CQR.all.share_regions_undercover_5pp}}% of BAs. The binding problem is *heterogeneity across BAs and over time*, not the absence of the BA from training.

**Target calibration from recent weeks fails.** Calibrating on the target BA's own last four weeks (SCP-T4) *reduces* mean coverage to {{prob.h24.unseen-region.90.SCP-T4.all.coverage_mean}}%. Four December weeks are not exchangeable with the following two years.

**Temporal drift lowers coverage.** Static coverage declines from 2024 to 2025: CQR falls from {{prob.h24.unseen-region.90.CQR.2024.coverage_mean}}% to {{prob.h24.unseen-region.90.CQR.2025.coverage_mean}}% (Fig. {fig:fig09_calibration}c).

**ACI restores per-BA coverage, but its step size is decisive.** Adaptive conformal inference with horizon-delayed feedback restores coverage in every BA. With the pre-registered step size $\gamma = 0.005$, coverage is {{prob.h24.unseen-region.90.ACI-CQR.all.coverage_mean}}% on average, with a minimum of {{prob.h24.unseen-region.90.ACI-CQR.all.coverage_min}}%. This is partly achieved, however, by issuing very wide intervals: the threshold is capped in a mean of {{acicap.h24.unseen-region.90.ACI-CQR}}% of hours, and the median interval score rises to {{prob.h24.unseen-region.90.ACI-CQR.all.interval_score_norm_median}}% of mean load, against {{prob.h24.unseen-region.90.CQR.all.interval_score_norm_median}}% for CQR.

**A validation-selected step size gives coverage and sharpness.** Choosing $\gamma$ on the 2023 data of held-out BAs selects $\gamma$ = {{gamma.h24.90}} at 24 h and {{gamma.h1.90}} at 1 h. The resulting ACI-CQR-V keeps per-BA coverage between {{prob.h24.unseen-region.90.ACI-CQR-V.all.coverage_min}}% and {{prob.h24.unseen-region.90.ACI-CQR-V.all.coverage_max}}% at 24 h. Its median interval score ({{prob.h24.unseen-region.90.ACI-CQR-V.all.interval_score_norm_median}}%) and median hourly width ({{prob.h24.unseen-region.90.ACI-CQR-V.all.width_hour_median_norm_median}}% of mean load) are on a par with CQR. The same holds at $h = 1$ h: ACI-CQR-V coverage has a minimum of {{prob.h1.unseen-region.90.ACI-CQR-V.all.coverage_min}}% and a median interval score of {{prob.h1.unseen-region.90.ACI-CQR-V.all.interval_score_norm_median}}%, against {{prob.h1.unseen-region.90.CQR.all.interval_score_norm_median}}% for CQR, while static CQR under-covers in {{prob.h1.unseen-region.90.CQR.all.share_regions_undercover_5pp}}% of BAs.

**Post-hoc sensitivity.** Table {tab:table_7b_aci_sensitivity} shows the test-set sensitivity of ACI to $\gamma$. It is labelled post hoc and was not used for selection. The degradation at $\gamma \ge 0.005$ is consistent with the 24-h feedback delay: with large steps, $\alpha_t$ overshoots before the effect of earlier updates is observed.

[[TABLE:table_7_probabilistic]]

[[TABLE:table_7b_aci_sensitivity]]

[[FIGURE:fig09_calibration]]

[[FIGURE:fig10_interval_example]]
