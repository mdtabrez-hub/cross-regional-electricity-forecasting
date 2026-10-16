# Practical implications

For system operators, market participants and planners, the results translate into five recommendations.

1. **Onboarding a new or data-poor BA.** A pooled, instance-normalised gradient-boosting model trained on other BAs can produce usable forecasts from the first day; it needs only a week of recent observations to compute the scale. In our data its median accuracy was within {{test.h24.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% (day-ahead) to {{test.h1.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% (hour-ahead), in relative terms, of a model that had seen the BA. Tail risk is material for intraday use, however: at 1 h the gap exceeded 10% for {{revgap.h1.LGB_G_LRO.LGB_G_IN.share_gt_10pct}}% of BAs, including one very large BA. A zero-shot model should therefore be monitored against the BA's own data, and replaced or pooled with that data, during the first months. Fine-tuning on a few weeks of data degraded accuracy at every onboarding date we tested and is not recommended with the settings studied here.
2. **Small BAs.** Small BAs also benefit from pooling, although less than large ones: the benefit of the global model over local models and the zero-shot gap both depend weakly on size. Very small systems (tens of MW) remain hard to forecast with any method (Section 11.4). A shared model with BA-specific online calibration is a viable service model for many small utilities, provided that its errors are monitored.
3. **Uncertainty for reserves and risk.** Intervals calibrated once on pooled data under-covered in a substantial share of BAs and drifted over time, so operational use should include online recalibration. ACI on top of CQR is guaranteed to reach the nominal long-run coverage. What matters in practice is its sharpness and its behaviour in the first months on a new system, and both depend on the step size. A step size chosen on *other* BAs' validation data (ACI-CQR-S) gave a median interval score of {{revcal.unseen_random_folds.h24.ACI-CQR-S.IS_median}}% against {{revcal.unseen_random_folds.h24.CQR.IS_median}}% for static CQR at 24 h; Table 8 gives the details. With day-ahead feedback delay, large step sizes should be avoided. A rolling four-week recalibration on the BA's own recent residuals is a simpler alternative that worked comparably for hour-ahead intervals but was less sharp day-ahead.
4. **Data quality.** Input gaps matter much more for intraday than for day-ahead forecasts. A simple remedy, training with randomly masked inputs, removes most of the intraday degradation at negligible cost on clean data. For long outages, native missing-value handling or seasonal filling is preferable to carrying the last value forward (Section 11).
5. **Compute.** All models in this study train on a commodity 4-core CPU. A pooled model (one model per horizon) is cheaper to maintain than 48 local models and was more accurate.

# Limitations

1. **Single country and dataset.** The study uses U.S. EIA-930 data only. The planned European replication on OPSD could not be run because the data host was unreachable from the execution environment.
2. **No weather inputs.** Absolute errors are therefore well above operational, weather-driven day-ahead forecasts.
3. **One test window.** The main test window (2024–2025) and a single rolling refit cover two years of temporal variation.
4. **Correlated BAs.** BAs are spatially correlated, so paired tests across BAs overstate the effective sample size. We report effect sizes and block-bootstrap results to mitigate this.
5. **Untuned adaptation.** Hyper-parameters for the adaptation methods were fixed a priori rather than tuned. Better-regularised adaptation may perform better.
6. **Compute amendment.** For compute reasons, models at $h \in \{1, 6\}$ used a higher learning rate, and probabilistic experiments were run at $h \in \{1, 24\}$ only.
7. **No neural or foundation models.** These could not be included (CPU only; model weights not reachable). How they compare under the same protocol remains open.
8. **Unscored anomalies.** Labels are PUDL-screened values, and flagged hours were not scored, so performance during data anomalies is not measured.
9. **Limited tuning.** Hyper-parameter grids were small (2×2), were tuned at $h = 24$ h on the pooled model and reused for leave-regions-out folds. They were not re-tuned after the 1-h and 6-h learning-rate change. At $h = 1$ h the in-region model reached the 3,000-tree cap, while the leave-regions-out models stopped between about 2,260 and 3,000 trees, so convergence was not perfectly equal across arms.
10. **Fixed adaptation settings.** The small-tree adaptation models used a learning rate of 0.05 (local) or 0.02 (fine-tuning) at every horizon; they were not covered by the 1-h/6-h amendment.
11. **Literature search.** The search relied on web-search results of publisher pages; Scopus, Web of Science and Crossref were not accessible. Some references could only be partially verified, and closely related work may have been missed.
12. **Sample of BAs.** The 48 BAs were selected for data quality and size (at least 200 MW), so the main results concern well-reported, medium-to-large BAs. Section 11 reports a secondary zero-shot check on the excluded small and low-quality BAs.

# Threats to validity

**Internal validity.** The main safeguards against test-set leakage were:

- a configuration and protocol frozen in version control before test scoring;
- past-only feature construction, verified by unit tests that perturb future inputs;
- held-out BAs excluded from fitting, early stopping and calibration;
- separate early-stopping and calibration weeks.

The freeze was an internal, timestamped commit made on the same day as the analysis; it was not registered externally. Five post-freeze amendments are logged with their motivation (DECISION_LOG D9–D13):

- an ACI implementation fix;
- a validation-selected ACI variant;
- a median-width metric;
- interval-start dating of hour-ending timestamps;
- a compute-driven learning-rate change at 1 h and 6 h.

All analyses added in response to the internal review (spatially blocked folds, source-only ACI step-size selection, multiple adaptation origins, excluded BAs, conditional and peak-hour diagnostics; D14–D16) are also post hoc. The validation-selected ACI variant was *motivated* by test-set behaviour of the frozen-protocol variant, and its step size was chosen on 2023 data of the evaluated BAs themselves. We therefore treat it as exploratory and base recommendations on the source-only variant.

**Construct validity.** Instance-normalised nMAE weights all BAs equally. An analysis weighted by energy would emphasise the largest ISOs, where the geographic gap was small. BA day-ahead forecasts have undocumented issuance times and a different information set.

**External validity.** The 48 BAs span three interconnections and a wide range of sizes and climates, but they are not a random sample of power systems worldwide. Regions with very different load composition (e.g. electric heating-dominated systems) may behave differently.

**Statistical conclusion validity.** Multiple comparisons are Holm-adjusted, effect sizes carry bootstrap intervals, and temporal dependence is handled by block bootstrap. Spatial correlation between BAs is not modelled explicitly.

# Conclusion and future work

We built a leakage-resistant benchmark, with a protocol frozen before test evaluation, for forecasting hourly electricity demand of balancing authorities that a model has never seen, using 48 U.S. BAs from EIA Form 930. Four conclusions follow.

1. **Zero-shot transfer works, with a tail.** A pooled, instance-normalised LightGBM model transfers to unseen BAs with a small but systematic median accuracy loss: {{test.h24.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% (24 h) to {{test.h1.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% (1 h) with random folds, and {{revsptest.h24.LGB_G_LRS.LGB_G_IN.median_rel_change}}% (24 h) to {{revsptest.h1.LGB_G_LRS.LGB_G_IN.median_rel_change}}% (1 h) when whole regions are held out. With random folds it is non-inferior to local models trained on four years of target data day-ahead and better intraday; with whole regions held out it matches local models at both horizons. Some BAs show large intraday gaps.
2. **Short-window adaptation does not help.** With the settings studied, fine-tuning or local training on one to thirteen weeks of target data degraded forecasts at every onboarding date tested.
3. **Interval calibration is the binding problem, and it is temporal and BA-specific rather than geographic.** Static conformal intervals (CQR) under-covered by more than 5 points in a fifth to a third of BAs, whether or not the BA had been seen in training. Online adaptive conformal inference restores marginal coverage by construction. Its practical value depended on the step size: chosen on other BAs, it gave sharpness close to CQR (equal at 24 h, slightly lower at 1 h), whereas the larger pre-specified step produced very wide intervals at 24 h.
4. **Data gaps matter mainly intraday, and compute is cheap.** Missing inputs degraded hour-ahead forecasts substantially but day-ahead forecasts only modestly, and training with masked inputs largely removed the hour-ahead penalty. Computational cost was a minor concern.

**Future work.** Several extensions follow directly:

- replicate the protocol on European data (OPSD/ENTSO-E) and on other national systems;
- add weather forecasts and evaluate whether the geographic gap and calibration findings persist;
- include time-series foundation models in the same leave-regions-out protocol;
- test parameter-free online calibration (e.g. aggregated ACI) and regularised adaptation schemes;
- extend the analysis to probabilistic forecasts of peaks and ramps.
