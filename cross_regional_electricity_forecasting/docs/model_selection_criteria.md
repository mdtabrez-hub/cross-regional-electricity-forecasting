# Model Selection Criteria

Models were chosen for relevance to the research questions, data size (~1.7 M training
rows), a 4-core CPU-only budget, and practical use by system operators.

| Model | Included | Rationale |
|---|---|---|
| Seasonal naive (24 h, 168 h), persistence | Yes | Mandatory reference baselines; MASE scaling |
| Ridge regression (pooled) | Yes | Transparent linear benchmark on identical features |
| LightGBM local | Yes | Strong, widely used tabular forecaster; represents per-region practice |
| LightGBM global (pooled) | Yes | Global models are the natural vehicle for cross-region transfer (Montero-Manso & Hyndman, 2021); GBDTs dominated M5 |
| LightGBM fine-tuning (continued boosting) | Yes | Cheapest limited-data adaptation for GBDTs |
| LightGBM quantile + conformal (SCP, CQR, ACI) | Yes | Distribution-free calibration with and without exchangeability |
| SARIMA / ETS | No | Hourly multi-seasonality and 48 regions × 3 horizons make per-region fitting costly; seasonal naive and local GBDT cover the local-model role. Logged as limitation |
| Random forest, XGBoost | No | Redundant with LightGBM for the questions asked |
| Recurrent / transformer networks, time-series foundation models (Chronos, TimesFM, Moirai) | No | No GPU; model weights hosted on Hugging Face are unreachable from this environment (network policy). Logged as limitation and future work |

Hyper-parameter selection: small grid (num_leaves × min_data_in_leaf) on the validation
year for the pooled model at h = 24 and for local models (median validation nMAE across
regions); the chosen setting is reused for all horizons, folds and adaptation variants.
