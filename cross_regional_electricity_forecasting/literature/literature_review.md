# Literature Review: Cross-Region Generalisation, Transfer and Calibrated Uncertainty in Hourly Electricity-Demand Forecasting

*Prepared 2026-10-16 by Agent 2 (literature review). All citations refer to keys in `verified_references.bib` and rows in `literature_matrix.csv`. The review is based on web search result snippets and the abstract or index pages they showed. No full texts were read, so the statements below report what abstracts and index records say. Entries marked "partially verified", "preprint" or "unverified" in the matrix need extra care before they are cited in a manuscript.*

---

## 1. Scope and framing

The planned study asks three linked questions about hourly balancing-authority (BA) demand from U.S. EIA Form 930:

1. **Geographic generalisation.** How well do forecasting models trained on some BAs predict BAs that were never in training (leave-regions-out)? How do they compare with per-BA (local) models and naive baselines?
2. **Limited-target adaptation.** How much of the gap closes with a small amount of target data, e.g. 4 weeks used for fine-tuning or local residual correction?
3. **Calibrated uncertainty under shift.** Do split-conformal and adaptive-conformal intervals keep their nominal coverage under geographic shift (unseen BAs) and temporal shift (later years)? How do the results compare with the BAs' own reported day-ahead forecasts?

The relevant literature spans six areas: (i) load-forecasting reviews and competitions; (ii) global versus local forecasting models; (iii) transfer, few-shot and meta-learning for load; (iv) time-series foundation models; (v) probabilistic evaluation and conformal prediction for time series; and (vi) data quality, missing data and evaluation methodology. Each is reviewed below, followed by a synthesis of the closest prior work.

---

## 2. Load forecasting: reviews, competitions and the probabilistic turn

Hong and Fan's tutorial review [hong2016probabilistic] is the standard starting point for probabilistic electric load forecasting. They note that a century of research and practice focused mainly on point forecasts, and they survey probabilistic techniques, evaluation methods and common misunderstandings. The Global Energy Forecasting Competitions set the field's benchmarking conventions:

- **GEFCom2012** [hong2014gefcom2012]: hierarchical (zonal) load forecasting, with the complete data and solutions released as a benchmark.
- **GEFCom2014** [hong2016gefcom2014]: made probabilistic (quantile) forecasting the scored task.
- **GEFCom2017** [hong2019gefcom2017]: combined hierarchy with probabilistic scoring and, for the first time, allowed external data. It drew more than 300 participants.

The later review by Hong et al. [hong2020energy] identifies reproducibility and open data sources as priorities for the field.

Two features of this literature matter for the planned study:

- **Each competition is within one system.** GEFCom data cover the zones of a single utility or ISO. None of the competitions tests whether a model trained on one utility's zones works on another utility. The cross-system question is therefore not addressed by the field's main benchmarks.
- **Temporal shift is documented and consequential.** The post-COVID IEEE DataPort competition [farrokhabadi2022dayahead] was set up specifically because pandemic-era demand shifts broke existing models. It was won by adaptive and online methods. This matches earlier work on adaptive GAMs with Kalman filtering during the French lockdown [obst2021adaptive], which also transferred information from Italy's earlier lockdown. It also matches the probabilistic extension by de Vilmarest et al. [devilmarest2024adaptive]. That paper combines a Kalman-filter adaptive point model with online quantile regression on residuals and evaluates it on GB regional net-load and on demand in seven large U.S. cities. Adaptivity improved both point and probabilistic scores. Its uncertainty quantification is quantile regression, not a conformal coverage guarantee, and it addresses temporal rather than geographic shift.

---

## 3. Global versus local forecasting models

Montero-Manso and Hyndman [montero2021principles] give the theoretical basis for "global" models, meaning one model fitted across many series. They show that global models can be as expressive as local ones without assuming the series are similar, and that they are competitive or better empirically. The M5 competition [makridakis2022m5] made pooled models a mainstream choice for large hierarchical collections. LightGBM [ke2017lightgbm] is the efficient gradient-boosting implementation that is commonly used for this kind of pooled model.

In electricity load specifically:

- **Ahmadi, Zareipour and Leung** [ahmadi2025globalization] (preprint) is the most direct evidence. On Alberta load they report that global target-transforming models consistently beat their local counterparts, especially with global features and clustering. They include a zero-shot evaluation in which models trained on area-level data forecast other regions and the system total, and LightGBM, XGBoost and Ridge appear among the zero-shot models.
- **Ling and Wu** [ling2025comparative] (preprint) compare global, cluster-level and local LightGBM *probabilistic* models on bike-share demand. They report coverage (PICP) and interval width, and find that global models with unit identifiers usually perform best.

This last point matters for the planned design. In a leave-regions-out test the target's identifier is never seen, so identifier-based gains cannot carry over. The planned study should therefore separate two kinds of global model: pooled models that see the target BA's history during training ("in-sample global"), and pooled models applied to a BA excluded from training ("out-of-sample global", i.e. zero-shot). The global-versus-local literature mostly evaluates the first kind. Ahmadi et al. are the clearest exception in load forecasting, but they use a single province.

---

## 4. Transfer learning, few-shot learning and meta-learning for load

Cross-region transfer for load is an established topic, so the planned study cannot claim it is new.

- **Tzortzis et al.** [tzortzis2024transfer] is the closest European analogue to the planned design. They take 27 European national day-ahead demand series of the kind distributed by ENTSO-E/OPSD, train a feed-forward network on source countries, and adapt it to a held-out target country (warm start plus fine-tuning, with and without clustering). Transfer beats per-country training, especially with clustering. The evaluation is point accuracy only and there is no calibration analysis.
- **Yuan et al.** [yuan2026adaptive] (venue and full author list not verified) frame the problem explicitly as *regional distribution shift*. Their STaRNet uses Reptile meta-learning to learn an initialisation that adapts quickly to unseen regions, evaluated on four German TSO areas. They report a 10.79% lower 24-hour MAE than the strongest baseline in the heterogeneous-transfer scenario. This is the most explicit "unseen region" load paper found. It is again point-only and uses four regions.
- **Antoniadis, Gaucher and Goude** [antoniadis2024hierarchical] study transfer *within* a hierarchy (fine-scale to national) using stacked GAM-random forest models and online aggregation of quantile experts.
- **Tsoumplekas et al.** [tsoumplekas2025fewshot] apply MAML to few-shot forecasting for individual consumers.
- **Building level:** BuildingsBench [emami2023buildingsbench] built the reference benchmark for zero-shot and fine-tuned forecasting on *unseen* buildings. It pretrains on 900K simulated buildings and evaluates on more than 1,900 real ones. Synthetic pretraining transferred to real commercial buildings, and fine-tuning helped most targets.

Taken together, cross-region and cross-unit transfer with limited target data is well studied for point forecasts. The questions with less coverage are whether transfer gains survive in *probabilistic* terms, and whether simple approaches (pooled gradient boosting plus a local residual correction) are competitive with meta-learning at the scale of 40-60 heterogeneous BAs. Only a handful of countries or TSO areas appear in [tzortzis2024transfer] and [yuan2026adaptive].

---

## 5. Time-series foundation models (TSFMs)

Pretrained "foundation" forecasters claim zero-shot accuracy on unseen datasets:

- **Chronos** [ansari2024chronos]: tokenised values with T5-family language models.
- **TimesFM** [das2024decoder]: a patched decoder-only model pretrained on about 100B time points.
- **Moirai** [woo2024unified]: a masked encoder trained on the 27B-observation LOTSA archive.
- **Lag-Llama** [rasul2023lagllama]: probabilistic, decoder-only, with lag covariates.
- **TimeGPT** [garza2023timegpt]: commercial and closed.

Applications to electricity load are growing quickly:

- **Household load.** Meyer et al. [meyer2025benchmarking] find zero-shot TSFMs comparable to Transformers trained from scratch.
- **ERCOT, with calibration.** Simeone [simeone2026tsfm] (preprint) benchmarks Chronos-Bolt, Chronos-2, Moirai-2 and TinyTimeMixer on ERCOT hourly load 2020-2024, including calibration and shift episodes (COVID, Winter Storm Uri). Chronos-2's 90% intervals reach about 95% empirical coverage, while Moirai-2 and Prophet are overconfident at about 70%.
- **EIA-930.** Hong, Lee and Shi [hong2026benchmarking] (preprint) benchmark state-space, Transformer and LSTM models on BA-level demand from six U.S. grids. They find no single winner. Models are trained per grid and evaluated on point accuracy.

Two implications follow. First, zero-shot calibration of TSFMs on load varies widely across models. That supports wrapping *any* base forecaster in a conformal layer and not relying on native quantiles. Second, a full TSFM benchmark is a fast-moving, crowded area, and it raises a leakage concern: public pretraining corpora may already contain EIA or other U.S. load series. If TSFMs are included as baselines, the study should document how this was checked. Otherwise TSFMs are better treated as related work than as a core contribution.

---

## 6. Probabilistic evaluation and quantile methods

Gneiting and Raftery [gneiting2007strictly] establish proper scoring rules, including CRPS and the interval and quantile scores. Gneiting, Balabdaoui and Raftery [gneiting2007probabilistic] set out the principle of maximising sharpness subject to calibration, with PIT-based diagnostics. Quantile regression via the check (pinball) loss goes back to Koenker and Bassett [koenker1978regression]. LightGBM's quantile objective is a direct application of it.

For the planned study these give a standard evaluation set:

- empirical coverage, by BA and pooled;
- mean interval width, normalised by BA scale;
- the interval (Winkler) score;
- pinball loss averaged over quantiles as a CRPS approximation.

Because different BAs differ in load by orders of magnitude, point accuracy across BAs should use a scale-free measure such as MASE [hyndman2006another]. Reporting MAPE alone is not adequate.

---

## 7. Conformal prediction for time series and under shift

### 7.1 Exchangeable foundations

Conformal prediction [vovk2005algorithmic] gives finite-sample marginal coverage under exchangeability. Split conformal regression [lei2018distribution] makes this cheap to apply to any regressor. Conformalized quantile regression (CQR) [romano2019conformalized] makes the interval width adapt to heteroscedasticity, which fits LightGBM quantile models naturally. Time-series data and leave-regions-out designs both break exchangeability, which motivates the methods below.

### 7.2 Methods for dependence and drift

- **ACI** (Gibbs and Candès [gibbs2021adaptive]) updates the miscoverage level online and guarantees long-run average coverage whatever the data-generating process.
- **AgACI** (Zaffran et al. [zaffran2022adaptive]) analyses ACI's learning rate (it degrades under exchangeability and helps under AR dependence) and proposes a parameter-free version based on online expert aggregation. Their case study is French day-ahead electricity *prices*.
- **Weighted conformal** (Barber et al. [barber2023conformal]) bounds the coverage gap under non-exchangeability and uses fixed weights to handle drift.
- **EnbPI** [xu2021conformal] and **SPCI** [xu2023sequential] build sequential intervals from bootstrap ensembles and from conditional residual quantiles.
- **Conformal PID control** (Angelopoulos et al. [angelopoulos2023conformal]) recasts online conformal as quantile tracking plus error integration plus "scorecasting", with experiments that include electricity demand.
- **Online optimisation** (Areces et al. [areces2025online]) report a pre-registered Texas electricity-demand experiment with more than 10% smaller sets and more than 30% better quantile loss.

### 7.3 Conformal in load forecasting applications

Matulin et al. [matulin2023cqr] apply CQR to Croatian TSO load and report higher coverage with narrower intervals than conventional methods. A 2026 Applied Sciences article [crossbuilding2026reliability] appears, from its title and one search snippet, to evaluate cross-building load forecasting under distribution shift and sensor missingness, and reports that coverage declines for unseen buildings. Its authors and full content could not be retrieved. It must be read in full before any novelty claim is made, because it may be the closest analogue at building level.

### 7.4 Gap

The online-conformal papers use a few electricity series as illustrations: one ISO, NSW demand, or French prices. None of the work found uses conformal coverage under geographic shift (calibrate on source regions, deploy on an unseen region) as its main object of study for system-level load across many regions. There is also an operational subtlety the planned study should state clearly. ACI-type methods need realised target labels to update. On a newly onboarded BA they therefore start from a source-calibrated level and adapt as target observations arrive. This "cold-start then adapt" behaviour is the part of the problem that is least characterised in the literature.

---

## 8. Data sources and data quality

**EIA-930 and PUDL.** EIA-930 reports hourly BA demand, next-day hourly demand forecasts, net generation and interchange [eia930about]. Ruggles et al. [ruggles2020developing] found about 2.2% of hourly demand values missing and about 0.5% anomalous as of September 2019. They developed screening plus MICE imputation, with a cross-validated imputation MAPE of about 3.5%. Catalyst Cooperative's PUDL [pudl2026] reimplements this screening and publishes EIA-930 tables that include imputed demand. This has a direct consequence for the planned study. If the targets include imputed values, scores computed on them partly measure agreement with the imputation model. The evaluation should therefore score only originally reported, non-flagged hours (or report both), and the exact PUDL release should be cited by its version DOI.

**Operator forecasts as a benchmark.** EIA documentation does not standardise when or how BAs produce their day-ahead forecasts. A comparison with operator forecasts therefore needs a carefully matched information set: no realised weather, and lags available only up to a plausible issue time. Without that, it will not support claims of "beating operators".

**European data.** OPSD [wiese2019opsd] provides cleaned European time series derived largely from ENTSO-E. Hirth et al. [hirth2018entsoe] document substantial quality and usability problems on the ENTSO-E Transparency Platform, and the platform is the basis of much European cross-country work, including [tzortzis2024transfer]. Our study cannot use OPSD here, so it cannot claim European generalisation. Its results are U.S. BA-specific.

**Missing data.** Beyond imputation [ruggles2020developing], Stratigakos et al. [stratigakos2024resilient] treat missing features at test time with robust optimisation. Across load, price, wind and solar they report that this beats imputation-based models and roughly matches retraining without the missing features. Concept-drift terminology and adaptation strategies are surveyed by Gama et al. [gama2014survey].

---

## 9. Evaluation methodology and leakage

- **Rolling-origin evaluation** is standard for time series [tashman2000out].
- **Cross-validation:** blocked cross-validation is preferred for time-series model selection [bergmeir2012use]. Standard K-fold is valid only for purely autoregressive models with uncorrelated errors [bergmeir2018note].
- **Common pitfalls** include leakage through features and normalisation, weak baselines and inappropriate metrics [hewamalage2023forecast].
- **Spatial and group blocking:** Roberts et al. [roberts2017cross] show that random cross-validation can badly misjudge error for spatially or group-structured data. This directly supports holding out whole BAs, and ideally whole interconnections or geographic clusters, so that weather or interchange correlation between neighbouring BAs does not inflate "unseen-region" scores.
- **Significance testing:** pairwise accuracy differences can be tested with Diebold-Mariano [diebold1995comparing], keeping in mind that the test compares forecasts, not models. Uncertainty in score differences across hours can be estimated with block or stationary bootstrap [kunsch1989jackknife; politis1994stationary].
- **Benchmarking practice in energy forecasting:** Lago et al. [lago2021forecasting] show the value of open multi-market benchmarks, explicit best practices and released forecasts.

---

## 10. Synthesis: closest prior work and what remains open

| Closest work | What it already does | What it does not do (relative to the planned study) |
|---|---|---|
| Tzortzis et al. 2024 [tzortzis2024transfer] | Cross-country transfer to held-out European national series; clustering | No probabilistic forecasts or calibration; NN only; Europe only |
| Yuan et al. 2026 [yuan2026adaptive] | Explicit regional distribution shift; meta-learning adaptation to unseen regions | 4 regions; point MAE; no calibration; metadata partially verified |
| Ahmadi et al. 2025 [ahmadi2025globalization] | Global vs local incl. LightGBM; zero-shot regional and system forecasting | Single province; no conformal coverage analysis evident; preprint |
| de Vilmarest et al. 2024 [devilmarest2024adaptive] | Adaptive *probabilistic* load forecasting; includes U.S. city demand | Temporal adaptation only; quantile regression, not conformal; no unseen regions |
| Hong, Lee and Shi 2026 [hong2026benchmarking] | EIA-930 BA-level benchmark of deep models | Per-grid training; no cross-BA transfer; no calibration; no operator benchmark |
| Simeone 2026 [simeone2026tsfm]; BuildingsBench [emami2023buildingsbench] | Zero-shot forecasting with calibration (ERCOT) / unseen buildings | One system / building level; no conformal recalibration across regions |
| Online conformal on electricity [gibbs2021adaptive; zaffran2022adaptive; angelopoulos2023conformal; areces2025online] | Coverage under temporal shift on a few electricity series | Not about geographic shift; few series; no operator comparison |
| Cross-building reliability 2026 [crossbuilding2026reliability] | Apparently: coverage under cross-building shift and missingness | Building level; **unverified** and must be read |

**What remains open.** The searches found no published study that combines all of the following on system-level hourly load:

1. many independently operated regions (tens of U.S. BAs);
2. leave-regions-out evaluation with geographic blocking;
3. global gradient boosting vs local vs naive baselines, with and without a few weeks of target data;
4. split-conformal and adaptive-conformal (ACI/AgACI) intervals assessed *separately* for geographic and temporal shift, including cold-start behaviour on unseen BAs;
5. a matched comparison with the BAs' own published day-ahead forecasts, with missingness and imputation treated explicitly.

Each component has precedent. The combination, and the scale of EIA-930, is the potential contribution. It is best framed as an evaluation framework and benchmark, not as a new algorithm. Search coverage was limited to web search snippets, so this conclusion is conditional. A database search (Scopus, Web of Science) is recommended before submission.
