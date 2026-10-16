---
title: "Forecasting Electricity Demand in Unseen Regions: A Leave-Regions-Out Benchmark of Global Models, Short-Window Adaptation and Conformal Calibration across 48 U.S. Balancing Authorities"
---

::: {custom-style="Author"}
[Author 1]^a^, [Author 2]^b^ [AUTHOR ACTION: names, affiliations, ORCID, corresponding author e-mail]
:::

::: {custom-style="Author"}
^a^ [Affiliation 1]; ^b^ [Affiliation 2]
:::

# Abstract {.unnumbered}

Forecasting models are increasingly expected to serve power systems they were not trained on. We present a pre-registered, leakage-resistant benchmark on hourly EIA-930 demand of {{data.n_regions}} U.S. balancing authorities (2019–2025) that separates geographic from temporal distribution shift. A pooled, instance-normalised LightGBM model applied to balancing authorities held out from training lost a median {{test.h24.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% (day-ahead) to {{test.h1.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% (hour-ahead) accuracy relative to in-region training. It was no worse than local models trained on four years of target data. Fine-tuning on one to thirteen weeks of target data mostly degraded accuracy. Static conformal intervals achieved near-nominal average coverage but under-covered by more than five points in {{prob.h24.unseen-region.90.CQR.all.share_regions_undercover_5pp}}–{{prob.h1.unseen-region.90.CQR.all.share_regions_undercover_5pp}}% of systems, irrespective of geographic shift. Adaptive conformal inference restored per-system coverage only when its step size suited the forecast feedback delay. Code and protocol are openly available.

**Keywords:** load forecasting; distribution shift; transfer learning; conformal prediction; global forecasting models; balancing authorities
