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

Forecasting models are increasingly expected to serve power systems they were not trained on. We benchmark this on hourly EIA-930 demand of {{data.n_regions}} U.S. balancing authorities (2019–2025), using a leakage-resistant protocol frozen before test evaluation. A pooled LightGBM model applied to unseen balancing authorities lost a median {{test.h24.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% (day-ahead) to {{test.h1.nMAE.LGB_G_LRO.LGB_G_IN.median_rel_change}}% (hour-ahead) accuracy relative to in-region training. When whole regions were held out the loss rose to {{revsptest.h24.LGB_G_LRS.LGB_G_IN.median_rel_change}}% (day-ahead) and {{revsptest.h1.LGB_G_LRS.LGB_G_IN.median_rel_change}}% (hour-ahead), yet zero-shot forecasts still matched local models trained on four years of target data. Fine-tuning on one to thirteen weeks of target data degraded accuracy. Static conformal intervals under-covered by more than five points in {{prob.h24.unseen-region.90.CQR.all.share_regions_undercover_5pp}}–{{prob.h1.unseen-region.90.CQR.all.share_regions_undercover_5pp}}% of systems, whether seen or unseen. Adaptive conformal inference, with its step size chosen on other systems, restored per-system coverage at little cost in sharpness.

**Keywords:** load forecasting; distribution shift; transfer learning; conformal prediction; global forecasting models; balancing authorities
