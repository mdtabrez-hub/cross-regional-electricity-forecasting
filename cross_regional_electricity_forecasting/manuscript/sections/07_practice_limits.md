# Practical implications

For system operators, market participants and planners, the results translate into five recommendations.

1. **Onboarding a new or data-poor BA.** A pooled, instance-normalised gradient-boosting model trained on other BAs can be deployed from the first day. It needs only a week of recent observations to compute the scale. In our data, its accuracy is within about 1–3% (relative) of a model that has seen the BA. Fine-tuning on a few weeks of data was counter-productive and should be avoided until a full seasonal cycle is available.
2. **Small BAs.** Small BAs benefit from pooling as much as large ones. Because the gap was only weakly related to size, a single shared model with BA-specific online calibration is a viable service model for many small utilities.
3. **Uncertainty for reserves and risk.** Intervals calibrated once on pooled data will under-cover in a substantial share of BAs and drift over time, so operational use should include online recalibration. ACI on top of CQR, with a step size selected on held-out systems and periods, delivered near-nominal coverage per BA at both horizons without wider typical intervals. When feedback is delayed (day-ahead), the step size must be conservative.
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

# Threats to validity

**Internal validity.** The main safeguards against test-set leakage were:

- a configuration and protocol frozen in version control before test scoring;
- past-only feature construction, verified by unit tests that perturb future inputs;
- held-out BAs excluded from fitting, early stopping and calibration;
- separate early-stopping and calibration weeks.

Four post-freeze amendments were necessary and are logged with their motivation: an ACI implementation fix, a validation-selected ACI variant, a median-width metric and a compute-driven learning-rate change. The validation-selected ACI variant was *motivated* by test-set behaviour of the pre-registered variant, even though its step size was chosen on validation data. Its advantage should therefore be confirmed on new data.

**Construct validity.** Instance-normalised nMAE weights all BAs equally. An analysis weighted by energy would emphasise the largest ISOs, where the geographic gap was small. BA day-ahead forecasts have undocumented issuance times and a different information set.

**External validity.** The 48 BAs span three interconnections and a wide range of sizes and climates, but they are not a random sample of power systems worldwide. Regions with very different load composition (e.g. electric heating-dominated systems) may behave differently.

**Statistical conclusion validity.** Multiple comparisons are Holm-adjusted, effect sizes carry bootstrap intervals, and temporal dependence is handled by block bootstrap. Spatial correlation between BAs is not modelled explicitly.

# Conclusion and future work

We built a leakage-resistant, pre-registered benchmark for forecasting hourly electricity demand of balancing authorities that a model has never seen, using 48 U.S. BAs from EIA Form 930. Four conclusions follow.

1. **Zero-shot transfer works.** A pooled, instance-normalised LightGBM model transfers to unseen BAs with a small but systematic accuracy loss of about {{test.h24.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% (24 h) to {{test.h1.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% (1 h) relative to in-region training. It is no worse than local models trained on four years of target data.
2. **Short-window adaptation does not help.** Fine-tuning or local training on one to thirteen weeks of target data mostly made forecasts worse.
3. **Interval calibration is the binding problem, and it is temporal and BA-specific rather than geographic.** Static conformal intervals under-covered in a fifth to a half of BAs, whether or not the BA had been seen in training. Online adaptive conformal inference restored per-BA coverage, but only with a step size matched to the feedback delay.
4. **Data gaps matter mainly intraday, and compute is cheap.** Missing inputs degraded hour-ahead forecasts substantially but day-ahead forecasts only modestly, and training with masked inputs largely removed the hour-ahead penalty. Computational cost was a minor concern.

**Future work.** Several extensions follow directly:

- replicate the protocol on European data (OPSD/ENTSO-E) and on other national systems;
- add weather forecasts and evaluate whether the geographic gap and calibration findings persist;
- include time-series foundation models in the same leave-regions-out protocol;
- test parameter-free online calibration (e.g. aggregated ACI) and regularised adaptation schemes;
- extend the analysis to probabilistic forecasts of peaks and ramps.
