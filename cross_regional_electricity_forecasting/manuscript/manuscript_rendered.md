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

Forecasting models are increasingly expected to serve power systems they were not trained on. We present a pre-registered, leakage-resistant benchmark on hourly EIA-930 demand of 48 U.S. balancing authorities (2019–2025) that separates geographic from temporal distribution shift. A pooled, instance-normalised LightGBM model applied to balancing authorities held out from training lost a median 0.5% (day-ahead) to 3.4% (hour-ahead) accuracy relative to in-region training. It was no worse than local models trained on four years of target data. Fine-tuning on one to thirteen weeks of target data mostly degraded accuracy. Static conformal intervals achieved near-nominal average coverage but under-covered by more than five points in 20.8–33.3% of systems, irrespective of geographic shift. Adaptive conformal inference restored per-system coverage only when its step size suited the forecast feedback delay. Code and protocol are openly available.

**Keywords:** load forecasting; distribution shift; transfer learning; conformal prediction; global forecasting models; balancing authorities


# Introduction

Short-term electricity-demand forecasts underpin unit commitment, reserve procurement, interchange scheduling and market operations. Every balancing authority (BA) in the United States produces them, and their errors translate directly into reserve and balancing costs [@hong2016probabilistic]. Most published forecasting studies, however, train and test on the same system. In practice, three situations call for a model that works on a system it has not seen:

- a new or reorganised balancing area;
- a utility joining a market;
- a small BA without a dedicated forecasting team.

A forecaster that generalises across regions, and whose prediction intervals remain trustworthy when it does, has engineering value beyond a marginal accuracy gain on a familiar system.

Two developments make cross-region forecasting plausible. First, *global* models fitted jointly to many series often match or outperform per-series models [@montero2021principles; @makridakis2022m5]. Second, pre-trained time-series foundation models promise zero-shot forecasting [@ansari2024chronos; @das2024decoder]. Whether such transfer works for system-level electricity demand, and at what cost to uncertainty quantification, is a question of distribution shift. An unseen BA differs from the training BAs in size, climate, customer mix and data-collection practice (geographic shift), and every BA changes over time through load growth, electrification, behind-the-meter solar and membership changes (temporal shift).

Conformal prediction offers distribution-free coverage guarantees, but only under exchangeability [@vovk2005algorithmic]. Adaptive variants recover long-run coverage under drift [@gibbs2021adaptive; @zaffran2022adaptive]. Their behaviour under geographic shift, under the delayed feedback inherent in day-ahead forecasting, and in the start-up period on a new system has not been characterised for system-level load.

This paper asks five research questions:

- **RQ1.** How much does forecast accuracy deteriorate when a BA is excluded from training, compared with in-region global and local models?
- **RQ2.** How much do one to thirteen weeks of target-region data help, through local training or fine-tuning of a global model?
- **RQ3.** Do quantile-regression and conformal prediction intervals remain calibrated under geographic and temporal shift?
- **RQ4.** How robust are the forecasts to temporal drift and to missing input observations?
- **RQ5.** What are the trade-offs among accuracy, interval reliability, computational cost and adaptation data?

The paper is organised as follows. Section 2 reviews related work and Section 3 states the research gap and contributions. Section 4 describes the data, Section 5 formulates the problem, Section 6 presents the methods, Section 7 details the experimental design and Section 8 the metrics. Section 9 reports the results and Section 10 discusses them. Section 11 covers robustness and ablations and Section 12 computational cost. Practical implications, limitations and threats to validity follow in Sections 13–15, and Section 16 concludes.


# Related work

**Load-forecasting benchmarks and the probabilistic turn.** Short-term load forecasting was long dominated by point prediction. Hong and Fan's tutorial review [@hong2016probabilistic] made the case for probabilistic forecasts and their evaluation. The Global Energy Forecasting Competitions established zonal and hierarchical forecasting [@hong2014gefcom2012], quantile-based scoring [@hong2016gefcom2014] and hierarchical probabilistic forecasting with external data [@hong2019gefcom2017] as standard benchmarks, and later reviews stressed reproducibility and open data [@hong2020energy]. These benchmarks are, however, *within-system*: models are trained and tested on zones of the same utility or ISO.

Robustness to *temporal* shift has received more attention since the COVID-19 pandemic. Adaptive state-space models and online aggregation performed well in a post-pandemic day-ahead competition [@farrokhabadi2022dayahead]. Kalman-filter adaptation of additive models [@obst2021adaptive] was later extended to adaptive probabilistic forecasting [@devilmarest2024adaptive]. These studies concern change over time within known systems, not deployment to systems absent from training.

**Global versus local models.** Global models fitted jointly across many series can be as expressive as local models without assuming that the series are similar [@montero2021principles]. Pooled gradient boosting was prominent in the M5 competition [@makridakis2022m5], and LightGBM [@ke2017lightgbm] is a common implementation. For electricity load, Ahmadi et al. report that global models outperform local ones on Alberta data and include a zero-shot evaluation on regions not used for training [@ahmadi2025globalization]. Ling and Wu compare global, clustered and local probabilistic LightGBM models in a non-energy setting [@ling2025comparative]. Most global-versus-local comparisons, however, evaluate series that were pooled during training. Generalisation to withheld series is seldom isolated, and its effect on uncertainty calibration is rarely reported.

**Transfer and few-shot learning across regions.** Tzortzis et al. pre-train neural networks on European national demand and adapt them to held-out countries [@tzortzis2024transfer]. Yuan et al. propose a meta-learning initialisation that adapts to unseen German transmission-system-operator areas [@yuan2026adaptive]. Hierarchical transfer [@antoniadis2024hierarchical] and meta-learning for data-scarce consumers [@tsoumplekas2025fewshot] address related settings. At building level, BuildingsBench established zero-shot and fine-tuning evaluation on unseen buildings [@emami2023buildingsbench]. These works mostly report point accuracy on a few target regions or on building-level data. Whether transfer preserves *calibrated* uncertainty for large, independently operated systems remains largely unexamined.

**Time-series foundation models.** Pre-trained forecasters such as Chronos [@ansari2024chronos], TimesFM [@das2024decoder], Moirai [@woo2024unified], Lag-Llama [@rasul2023lagllama] and TimeGPT [@garza2023timegpt] claim competitive zero-shot accuracy on unseen datasets. For household load, zero-shot foundation models perform comparably to Transformers trained from scratch [@meyer2025benchmarking]. A recent preprint on ERCOT system load reports that interval calibration differs sharply between foundation models [@simeone2026tsfm], and another benchmarks deep sequence models on EIA-930 with per-grid training [@hong2026benchmarking]. Calibration of zero-shot models therefore cannot be assumed, which motivates a model-agnostic recalibration layer of the kind studied here.

**Probabilistic evaluation and conformal prediction under shift.** We evaluate forecasts with proper scoring rules [@gneiting2007strictly], following the principle of maximising sharpness subject to calibration [@gneiting2007probabilistic], and use quantile losses rooted in quantile regression [@koenker1978regression]. Split conformal prediction [@vovk2005algorithmic; @lei2018distribution] gives distribution-free marginal coverage under exchangeability, and conformalised quantile regression adds heteroscedastic adaptivity [@romano2019conformalized]. For dependent and drifting data, several extensions exist:

- adaptive conformal inference (ACI) guarantees long-run coverage by updating the target miscoverage online [@gibbs2021adaptive];
- aggregated ACI removes the step-size choice and was demonstrated on electricity prices [@zaffran2022adaptive];
- weighted conformal methods bound the loss of coverage under non-exchangeability [@barber2023conformal];
- EnbPI [@xu2021conformal] and SPCI [@xu2023sequential] exploit residual structure;
- conformal PID control [@angelopoulos2023conformal] and online-optimisation approaches [@areces2025online] include electricity-demand experiments.

Conformalised quantile regression has also been applied to transmission-level load [@matulin2023cqr]. A recent study reports reduced coverage when building-level load models are applied to unseen buildings [@crossbuilding2026reliability]. Electricity applications of online conformal methods have so far mostly concerned single series under temporal drift. Coverage under *geographic* shift, where a model is calibrated on some regions and deployed on a region it has never seen, is less studied for system-level load.

**Data quality and evaluation methodology.** EIA-930 provides hourly demand and day-ahead forecasts for U.S. balancing authorities [@eia930about]. Ruggles et al. documented its missing and anomalous values and developed the screening and imputation reimplemented in PUDL [@ruggles2020developing; @pudl2026]. The comparable European resources, OPSD [@wiese2019opsd] and the ENTSO-E Transparency Platform [@hirth2018entsoe], have documented quality limitations. Robust optimisation has been proposed as an alternative to imputation for missing inputs [@stratigakos2024resilient].

Our evaluation design follows established practice. We use rolling-origin and blocked validation for dependent data [@tashman2000out; @bergmeir2012use; @bergmeir2018note], group-blocked validation analogous to spatial cross-validation [@roberts2017cross], and scale-free accuracy (MASE) [@hyndman2006another]. We test differences with block-bootstrap intervals [@kunsch1989jackknife; @politis1994stationary], in the spirit of Diebold–Mariano comparisons [@diebold1995comparing], and we avoid known pitfalls in forecast evaluation [@hewamalage2023forecast; @lago2021forecasting].

**Positioning.** Every ingredient of this study has precedent: cross-region transfer, global gradient boosting, adaptive conformal prediction and operator-forecast data. To our knowledge, based on a non-exhaustive search, they have not been combined in a single pre-registered evaluation across tens of independently operated U.S. balancing authorities. Such an evaluation separates geographic from temporal shift, quantifies the value of a few weeks of target data, assesses interval coverage under both shifts, and benchmarks against the operators' own forecasts. Our contribution is this evaluation framework and benchmark, not a new forecasting or conformal algorithm.


# Research gap and contributions

The literature review (Section 2 and the supplementary literature matrix) shows that each ingredient of the problem has been studied in isolation:

- transfer to held-out regions, mostly for point forecasts on a few European countries or German control areas [@tzortzis2024transfer; @yuan2026adaptive];
- global versus local models, mostly on series seen in training [@montero2021principles; @ahmadi2025globalization];
- adaptive conformal prediction on single electricity series under temporal drift [@gibbs2021adaptive; @zaffran2022adaptive; @angelopoulos2023conformal];
- EIA-930 benchmarks trained per grid [@hong2026benchmarking].

We found no study that measures, on a common protocol, (i) the accuracy cost of never having seen a system, (ii) the value of a few weeks of target data, and (iii) whether interval coverage survives geographic and temporal shift, across tens of independently operated systems with operator forecasts as a reference. The search was not exhaustive (see Section 14).

The study makes four contributions.

1. *A leakage-resistant, pre-registered benchmark for cross-region load forecasting.* It covers 48 U.S. BAs from EIA Form 930 (2019–2025), spanning three orders of magnitude in size. Its components are: leave-regions-out folds in which held-out BAs are excluded from fitting, early stopping and calibration; past-only input screening independent of the label imputation; a protocol and configuration frozen in version control before test evaluation; and a log of every subsequent amendment.
2. *A quantification of the geographic generalisation gap for instance-normalised global models.* We compare zero-shot, limited-data adaptation, local and in-region regimes at 1-, 6- and 24-h horizons, with BA-level paired statistics that account for temporal dependence.
3. *An assessment of interval calibration by shift type.* We evaluate quantile regression, split conformal prediction, conformalised quantile regression, target-calibrated conformal prediction and adaptive conformal inference with horizon-delayed feedback, separately for in-region and unseen-region deployment and by year and season. This includes the sensitivity of ACI to its step size, which we found to be decisive.
4. *Engineering evidence and an open reproducible pipeline.* We report robustness to missing inputs, the computational cost of each regime, and a comparison with the BAs' own day-ahead forecasts. All code, configurations, predictions and metrics are released.

We do not propose a new forecasting algorithm. The contribution is an evaluation framework and the empirical evidence it produces.



# Data and data preparation

## Source and licence

We use the U.S. Energy Information Administration (EIA) Form 930 hourly balancing-authority operations data [@eia930about] as cleaned and published by the Public Utility Data Liberation (PUDL) project of Catalyst Cooperative, release v2026.10.0 [@pudl_eia930_2026; @pudl2026]. A balancing authority (BA) is the entity that balances generation, interchange and load within its area in real time. A BA's hourly *demand* (MWh in an hour, numerically equal to the average MW) is calculated by the BA as metered net generation minus net metered interchange with neighbouring BAs. It therefore excludes behind-the-meter generation such as most rooftop photovoltaics. The EIA data are a U.S. Government work in the public domain; the PUDL release is distributed under CC-BY-4.0. Timestamps are in UTC and mark the end of the hour, so daylight-saving transitions create neither duplicate nor missing timestamps. The raw table contains 70 BAs from July 2015 to September 2026.

The PUDL release also provides a screened demand series in which missing, non-positive, constant-run, spike and other anomalous values are flagged and imputed with the method of Ruggles et al. [@ruggles2020developing], with a reason code for every flagged hour. Each BA's reported day-ahead demand forecast is included as well.

The project brief originally specified the Open Power System Data (OPSD) time-series package [@wiese2019opsd]. Its hosts were not reachable from the execution environment, so OPSD could not be used. A converter from the OPSD 60-minute file to our panel format is provided with the code for a European replication.

## Region selection

We fixed the study window to 2019–2025 and, before any modelling, applied the following inclusion criteria to the 66 BAs present in that window:

- not a generation-only BA;
- in the Eastern, Western or ERCOT interconnection;
- active through 2025;
- reported demand available for at least 97% of hours;
- at most 5% of hours flagged by PUDL screening, and no year discarded as a "bad year";
- mean demand of at least 200 MW;
- a documented reporting time zone.

48 BAs satisfy all criteria: 21 in the Eastern interconnection, 26 in the Western and 1 in ERCOT (Fig. 2; Appendix Table A1). Their mean demand ranges from 218 MW (CHPD) to 91,577 MW (PJM), a ratio of about 419:1, and their climates range from the Pacific Northwest to Florida and the desert Southwest. Fig. 3 illustrates the resulting differences in daily and seasonal shape.

The panel contains 2,945,664 BA-hours (61,368 hours per BA). Of these, 0.55% are flagged by PUDL screening (Fig. 4).



![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig01_workflow.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 1.** Research workflow and leakage-resistant evaluation design.
:::





![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig02_dataset_coverage.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 2.** Selected balancing authorities: (a) mean demand by interconnection; (b) share of hours flagged by PUDL screening or missing, by year.
:::





![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig03_example_series.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 3.** Normalised hourly demand of three BAs of different size and climate (validation year 2023; test data not shown).
:::





![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig04_data_quality.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 4.** PUDL screening codes by BA (2019–2025, sorted by mean demand). Flagged hours are excluded from scoring; model inputs use an independent causal screen.
:::



## Labels, inputs and leakage control

Labels and inputs are deliberately constructed differently.

**Labels.** The training and evaluation label $y_t$ is the PUDL screened demand. Training and scoring use only hours whose reported value was retained by the screening (no reason code). Imputed hours are never scored.

**Inputs.** PUDL's screening uses two-sided windows and whole-series statistics, so using screened values as model *inputs* would leak future information. The input series $x_t$ is therefore the *reported* demand after a causal screen that uses only strictly earlier hours. Non-positive values are set to missing, as is any value above 2.5 times or below 0.25 times the median of the preceding 168 hours (at least 24 observations required). This screen removes 0.33% of input hours.

Unit tests verify the leakage controls by perturbing every input after a forecast origin and checking that all features at that origin are unchanged.

# Problem formulation

Let $r \in \mathcal{R}$ index BAs and $t$ hours. For horizon $h \in \{1, 6, 24\}$ h we forecast $y_{r,t}$ at origin $o = t - h$ using $\{x_{r,s}: s \le o\}$ and deterministic calendar information about $t$. We use the direct strategy, with one model per horizon. The 24-h horizon approximates the information set of a day-ahead forecast issued one day before each target hour. The 1-h and 6-h horizons correspond to intraday operation.

To allow one model to serve BAs whose demand differs by three orders of magnitude, and to forecast BAs that were never seen, we normalise each example by an *instance scale* computed at the origin:
$$
s_{r,o} = \frac{1}{|W_{r,o}|}\sum_{s\in W_{r,o}} x_{r,s},\qquad W_{r,o} = \{s \in [o-167, o] : x_{r,s}\ \text{observed}\},
$$
with $|W_{r,o}|\ge 24$. Models predict $z_{r,t} = y_{r,t}/s_{r,o}$, and the forecast is $\hat y_{r,t} = \hat z_{r,t}\, s_{r,o}$.

The features, all divided by $s_{r,o}$, are:

- the 24 most recent values $x_{r,o-k}$, $k = 0, \dots, 23$;
- the values at the same hour on the previous one or two days, $x_{r,t-24m}$ for $m = \lceil h/24\rceil, \lceil h/24\rceil+1$;
- weekly lags $x_{r,t-168}$ and $x_{r,t-336}$;
- the trailing 24-h mean, minimum and maximum and the 168-h standard deviation at $o$;
- the share of missing inputs in the last 24 h.

Calendar features are taken in the BA's reporting time zone: hour of day, day of week, month, day-of-year sine and cosine, weekend, and U.S. federal holiday. No region identifier or absolute-level feature is used, so every model can be applied to an unseen BA.

# Methodology

## Point forecasting methods

We compare simple references with linear and gradient-boosted models that receive identical inputs.

**Seasonal naive and persistence.** SN24 uses $x_{r,t-24\lceil h/24\rceil}$ and SN168 uses $x_{r,t-168}$, both causally forward-filled. Persistence uses $x_{r,t-h}$; at $h = 24$ it coincides with SN24.

**Ridge regression.** Ridge regression ($\lambda = 1$) is fitted on standardised numeric features and one-hot hour, weekday and month, pooled across training BAs.

**LightGBM.** We use LightGBM [@ke2017lightgbm] with an absolute-error objective, so the model targets the conditional median of $z$, consistent with MAE scoring. It is trained in three regimes:

- *local*: one model per BA, trained on that BA only;
- *global in-region* (G-IN): one model pooled over all 48 BAs;
- *global leave-regions-out* (G-LRO): pooled over the BAs of the other five folds, so that the evaluated BA is unseen [@montero2021principles].

**Operator reference.** BA-DA is each BA's own reported day-ahead forecast. It is reported only as an operational reference, for two reasons: operators use weather forecasts, which our models do not, and issuance times are undocumented.

**Hyper-parameters.** These were selected by grid search on the odd ISO weeks of 2023 and fixed for all horizons and folds. The global model uses 255 leaves with at least 100 samples per leaf; local models use 127 leaves with at least 100. Settings that are not tuned are a learning rate of 0.05 at $h = 24$, feature and bagging fractions of 0.8, and L2 regularisation of 1. At $h \in \{1, 6\}$ the 1-h model reached the 3,000-tree cap at a learning rate of 0.05, so all LightGBM models at these horizons use a learning rate of 0.2. This compute-driven amendment was made before any 1-h or 6-h test evaluation. Early stopping uses 100 rounds on the same weeks. In leave-regions-out runs it uses only the source BAs.

## Limited target-data adaptation

For an unseen BA with $k \in \{1, 4, 13\}$ weeks of history immediately before the test period, we compare two adaptation methods:

- **LGB-L-k**, a local LightGBM model with 15 leaves, at least 10 samples per leaf and 300 trees, trained only on those $k$ weeks;
- **LGB-FT-k**, which continues boosting the G-LRO model with 200 further trees (learning rate 0.02, 15 leaves) on the same $k$ weeks.

Both use only labels observable at the start of the test period.

## Probabilistic forecasting and calibration

For $h \in \{1, 24\}$, central intervals with nominal coverage $1-\alpha$, $\alpha \in \{0.1, 0.5\}$, are built on the normalised scale and multiplied by $s_{r,o}$:

- **QR**: LightGBM quantile models at $\tau \in \{0.05, 0.25, 0.75, 0.95\}$, with the L1 point model as the median.
- **SCP**: split conformal prediction [@vovk2005algorithmic; @lei2018distribution], giving $\hat z \pm \hat q$, where $\hat q$ is the $\lceil (n+1)(1-\alpha)\rceil$-th smallest absolute residual $|z-\hat z|$ on the calibration set.
- **CQR**: conformalised quantile regression [@romano2019conformalized], giving $[\hat q_{\alpha/2} - \hat c,\ \hat q_{1-\alpha/2} + \hat c]$ with conformity scores $\max(\hat q_{\alpha/2} - z,\ z - \hat q_{1-\alpha/2})$.
- **SCP-T4**: SCP calibrated on the target BA's own last four weeks before the test period, the only target information that would be available when onboarding a new BA.
- **ACI-CQR**: adaptive conformal inference [@gibbs2021adaptive] applied online per BA to CQR scores, described next.

**Calibration sets.** The calibration set consists of the even ISO weeks of 2023, which are never used for fitting or early stopping. For unseen-region models it is restricted to the source BAs.

**ACI-CQR.** The working miscoverage level is updated as
$$
\alpha_{t+1} = \alpha_t + \gamma\,(\alpha - \mathrm{err}_{t-h}),
$$
where $\mathrm{err}_{t-h}$ indicates whether the interval issued for hour $t-h$ missed. Feedback is therefore delayed by the horizon. Scores enter the calibration pool once their outcomes are observed. When $\alpha_t$ leaves $(0,1)$ the exact ACI interval is unbounded or empty; we cap it at the most extreme score observed so far and report the share of capped hours. ACI-CQR uses the pre-registered step size $\gamma = 0.005$. **ACI-CQR-V** uses $\gamma$ selected from $\{0.001, 0.002, 0.005, 0.01\}$ by interval score on the 2023 data of held-out BAs; this variant was added after the freeze (Section 15).

# Experimental design

All settings were fixed in a configuration file before test-set evaluation (Fig. 1).

**Splits.** The data are divided chronologically:

- training: 2019–2022;
- validation: 2023, split by ISO week parity into an early-stopping/selection set (odd weeks) and a conformal calibration set (even weeks);
- test: 2024–2025, used once.

**Folds.** For leave-regions-out evaluation, BAs were ranked by mean demand, dealt into blocks of six and randomly permuted within each block. This gives six folds of eight BAs with similar size distributions. Every model, early-stopping set and calibration set for a held-out fold excludes that fold's BAs.

**Experiments.** The experiments are:

- (E1) point accuracy and the geographic generalisation gap;
- (E2) limited-data adaptation;
- (E3) temporal shift, comprising validation-year versus test-year error, 2024 versus 2025 error and seasonal breakdowns, plus a rolling-origin refit (training through 2023, validation on 2024, testing on 2025);
- (E4) interval calibration;
- (E5) robustness to missing inputs;
- (E6) ablations;
- (E7) computational cost.

**Missing inputs (E5).** Test-period inputs, but not labels, are corrupted with missing-completely-at-random (MCAR) gaps at 5–40% rates and with random 24-h or 168-h outages removing about 10% of hours. Four strategies are compared:

- LightGBM's native handling of missing values;
- causal last-observation-carried-forward imputation;
- causal weekly-seasonal imputation;
- a global model trained with 10% MCAR input augmentation.

**Ablations (E6).** For unseen BAs at $h = 24$, we remove the calendar features, the weekly lags, or the recent lags beyond the first four, and we shrink the source pool to 5, 10 or 20 randomly drawn BAs (three draws each).

**Hardware.** All runs used a 4-core CPU with 15 GB of memory and no GPU. Fixed seeds and LightGBM's deterministic mode were used throughout.

# Evaluation metrics

For BA $r$ with scored hours $T_r$ (test period, unflagged label, all compared methods available):
$$
\mathrm{MAE}_r = \frac{1}{|T_r|}\sum_{t\in T_r}|y_{r,t}-\hat y_{r,t}|,\qquad
\mathrm{nMAE}_r = \frac{\mathrm{MAE}_r}{\bar y_r},\qquad
\mathrm{nRMSE}_r = \frac{1}{\bar y_r}\sqrt{\frac{1}{|T_r|}\sum_{t\in T_r}(y_{r,t}-\hat y_{r,t})^2},
$$
where $\bar y_r$ is the mean observed demand over $T_r$. The mean absolute scaled error [@hyndman2006another] divides $\mathrm{MAE}_r$ by the training-period mean absolute 24-h seasonal difference. Bias is $\sum_t(\hat y_{r,t}-y_{r,t}) / \sum_t y_{r,t}$.

**Probabilistic metrics.** For intervals $[l_{r,t}, u_{r,t}]$ we report:

- empirical coverage;
- width normalised by $\bar y_r$, both mean and median over hours;
- the interval score [@gneiting2007strictly]:
$$
\mathrm{IS}_\alpha = (u-l) + \frac{2}{\alpha}(l-y)\,\mathbb{1}\{y<l\} + \frac{2}{\alpha}(y-u)\,\mathbb{1}\{y>u\}.
$$

The quantile grid is scored with the average pinball loss $\rho_\tau(e) = \max(\tau e, (\tau-1)e)$, $e = y - \hat q_\tau$, normalised by $\bar y_r$. Calibration across BAs is summarised by the mean absolute coverage deviation and by the share of BAs whose coverage falls more than 5 percentage points below nominal.

**Aggregation.** Cross-BA summaries are medians (with interquartile ranges) of per-BA metrics, so each BA counts equally. This is deliberate: pooled MWh errors would be dominated by PJM, MISO and ERCOT.

**Statistical comparisons.** Paired comparisons across BAs use the Wilcoxon signed-rank test on per-BA nMAE, with Holm adjustment over all reported comparisons. Effect sizes are median relative changes, with 95% percentile bootstrap intervals over BAs (1,000 resamples). Within each BA, temporal dependence is handled by a moving-block bootstrap [@kunsch1989jackknife] of the hourly absolute-error differential (168-h blocks, 1,000 resamples); we report the share of BAs whose 95% interval excludes zero. BAs are spatially correlated, so region-level tests overstate the effective sample size [@roberts2017cross]. We therefore emphasise effect sizes.


# Results

All results refer to the 2024–2025 test period unless stated otherwise. They are computed on the 48 BAs, using hours where the label is unflagged and every compared method has a forecast. This covers more than 99.5% of test hours at every horizon.

## Point accuracy and the geographic generalisation gap (RQ1)

Table 1 and Fig. 5 summarise per-BA accuracy.

**Day-ahead horizon.** At $h = 24$ h the global LightGBM model trained on all BAs (G-IN) attains a median nMAE of 4.64% (MASE 0.884). The same model class with the evaluated BA held out (G-LRO, zero-shot) attains 4.75%, against 4.72% for local models trained on four years of each BA's own data, 5.05% for pooled ridge regression and 5.48% for the 24-h seasonal naive.

**Shorter horizons.** At $h = 6$ h the medians are 3.50% (G-IN), 3.66% (G-LRO) and 3.78% (local). At $h = 1$ h they are 1.14%, 1.17% and 1.28%.



::: {custom-style="Table Caption"}
**Table 1.** Test-period (2024–2025) point accuracy across 48 BAs.
:::

|   h (h) | Method                                      | nMAE % median [IQR]   |   nRMSE % median |   MASE median |   Bias % median |   Regions |
|--------:|:--------------------------------------------|:----------------------|-----------------:|--------------:|----------------:|----------:|
|       1 | Seasonal naive (24 h)                       | 5.48 [4.57, 6.81]     |             7.81 |         1.009 |           -0.02 |        48 |
|       1 | Seasonal naive (168 h)                      | 9.12 [8.17, 11.40]    |            12.84 |         1.731 |           -0.04 |        48 |
|       1 | Persistence                                 | 3.49 [3.12, 4.23]     |             4.42 |         0.626 |            0    |        48 |
|       1 | Ridge, global (in-region)                   | 1.42 [1.16, 1.71]     |             2.16 |         0.246 |            0    |        48 |
|       1 | Ridge, global (unseen region)               | 1.40 [1.16, 1.69]     |             2.16 |         0.245 |            0    |        48 |
|       1 | LightGBM, local                             | 1.28 [1.01, 1.61]     |             1.84 |         0.22  |            0.02 |        48 |
|       1 | LightGBM, global (in-region)                | 1.14 [0.87, 1.51]     |             1.63 |         0.194 |            0.01 |        48 |
|       1 | LightGBM, global (unseen region, zero-shot) | 1.17 [0.90, 1.55]     |             1.67 |         0.201 |            0.01 |        48 |
|       6 | Seasonal naive (24 h)                       | 5.48 [4.57, 6.81]     |             7.81 |         1.009 |           -0.02 |        48 |
|       6 | Seasonal naive (168 h)                      | 9.12 [8.17, 11.40]    |            12.84 |         1.731 |           -0.04 |        48 |
|       6 | Persistence                                 | 15.80 [14.16, 19.89]  |            19.71 |         2.817 |           -0.01 |        48 |
|       6 | Ridge, global (in-region)                   | 4.16 [3.44, 5.13]     |             5.95 |         0.758 |            0.01 |        48 |
|       6 | Ridge, global (unseen region)               | 4.17 [3.44, 5.13]     |             5.96 |         0.759 |            0.02 |        48 |
|       6 | LightGBM, local                             | 3.78 [3.13, 4.60]     |             5.4  |         0.676 |           -0.01 |        48 |
|       6 | LightGBM, global (in-region)                | 3.50 [2.95, 4.35]     |             5.12 |         0.627 |            0.03 |        48 |
|       6 | LightGBM, global (unseen region, zero-shot) | 3.66 [3.03, 4.40]     |             5.29 |         0.654 |           -0.01 |        48 |
|      24 | Seasonal naive (24 h)                       | 5.48 [4.57, 6.81]     |             7.81 |         1.009 |           -0.02 |        48 |
|      24 | Seasonal naive (168 h)                      | 9.12 [8.17, 11.40]    |            12.84 |         1.731 |           -0.04 |        48 |
|      24 | Persistence                                 | 5.48 [4.57, 6.81]     |             7.81 |         1.009 |           -0.02 |        48 |
|      24 | Ridge, global (in-region)                   | 5.05 [4.17, 6.21]     |             7.12 |         0.932 |            0.07 |        48 |
|      24 | Ridge, global (unseen region)               | 5.06 [4.17, 6.21]     |             7.13 |         0.933 |            0.08 |        48 |
|      24 | LightGBM, local                             | 4.72 [3.94, 5.94]     |             6.85 |         0.893 |           -0.19 |        48 |
|      24 | LightGBM, global (in-region)                | 4.64 [3.88, 5.87]     |             6.92 |         0.884 |           -0.1  |        48 |
|      24 | LightGBM, global (unseen region, zero-shot) | 4.75 [3.91, 5.91]     |             6.93 |         0.888 |           -0.1  |        48 |






![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig05_accuracy.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 5.** Distribution of per-BA test nMAE (2024–2025) by method and horizon.
:::



**Size of the gap.** The cost of never having seen a BA is small but systematic (Table 2). At $h = 24$ h the median per-BA relative increase in nMAE from G-IN to G-LRO is 0.5% (95% bootstrap CI 0.4 to 0.7%). The held-out model is better in only 6.2% of BAs. The gap grows as the horizon shrinks: 1.9% at 6 h and 3.4% at 1 h (CI 2.5 to 4.6%). The moving-block bootstrap shows that the in-region model is significantly better within 97.9% of BAs at 1 h but only 52.1% at 24 h.

**Distribution across BAs.** The gap is concentrated in a few BAs (Fig. 6). The largest relative gap at 24 h is 6.6% (GCPD), and the gap is weakly related to BA size (correlation with log mean demand -0.25). Per-BA errors of the zero-shot model range from 2.47% (GCPD) to 8.55% (AECI). This spread across BAs is an order of magnitude larger than the geographic gap itself.

**Global versus local.** Pooling helps more than locality does. The median per-BA relative change in nMAE from local models to G-IN is -1.4% at 24 h (CI -2.2 to -0.8%) and -9.2% at 1 h (negative values favour the global model). More strikingly, the *zero-shot* G-LRO model, which has never seen the target BA, is not worse than a local model trained on four years of that BA's data. The median relative difference is -0.8% at 24 h (CI -1.6 to 0.2%; Holm-adjusted $p$ = 0.21) and -5.4% at 1 h (CI -8.1 to -3.7%).

**Linear benchmark.** Relative to ridge regression on the same features, G-IN changes nMAE by a median -5.5% at 24 h and -19.3% at 1 h. Its own geographic gap is negligible (0.1% at 24 h), consistent with a low-capacity model that cannot memorise BA-specific patterns.



::: {custom-style="Table Caption"}
**Table 2.** Paired comparisons of per-BA nMAE (test period).
:::

|   h (h) | A                                           | B                             |   Median rel. change in nMAE (A vs B) % | 95% CI (regions bootstrap)   |   A better (share of BAs) |   Wilcoxon p (Holm, all) |   BAs with A sig. better (block bootstrap) |   BAs with B sig. better |
|--------:|:--------------------------------------------|:------------------------------|----------------------------------------:|:-----------------------------|--------------------------:|-------------------------:|-------------------------------------------:|-------------------------:|
|       1 | LightGBM, global (unseen region, zero-shot) | LightGBM, global (in-region)  |                                     3.4 | [2.5, 4.6]                   |                      0    |                  5.1e-13 |                                       0    |                     0.98 |
|       1 | LightGBM, global (in-region)                | LightGBM, local               |                                    -9.2 | [-11.7, -7.3]                |                      0.92 |                  2.1e-08 |                                       0.83 |                     0.04 |
|       1 | LightGBM, global (unseen region, zero-shot) | LightGBM, local               |                                    -5.4 | [-8.1, -3.7]                 |                      0.77 |                  0.00052 |                                       0.75 |                     0.12 |
|       1 | LightGBM, global (unseen region, zero-shot) | Seasonal naive (24 h)         |                                   -79.6 | [-81.7, -77.5]               |                      1    |                  5.1e-13 |                                       1    |                     0    |
|       1 | LightGBM, global (in-region)                | Ridge, global (in-region)     |                                   -19.3 | [-22.3, -15.5]               |                      1    |                  5.1e-13 |                                       1    |                     0    |
|       1 | Ridge, global (unseen region)               | Ridge, global (in-region)     |                                     0.5 | [0.2, 0.6]                   |                      0.23 |                  0.0083  |                                     nan    |                   nan    |
|       1 | LightGBM, global (unseen region, zero-shot) | Ridge, global (unseen region) |                                   -14.8 | [-19.7, -11.5]               |                      0.98 |                  2.1e-11 |                                     nan    |                   nan    |
|       1 | LightGBM, local                             | Seasonal naive (24 h)         |                                   -78.1 | [-79.2, -76.4]               |                      1    |                  5.1e-13 |                                     nan    |                   nan    |
|       6 | LightGBM, global (unseen region, zero-shot) | LightGBM, global (in-region)  |                                     1.9 | [1.6, 2.3]                   |                      0    |                  5.1e-13 |                                       0    |                     0.9  |
|       6 | LightGBM, global (in-region)                | LightGBM, local               |                                    -5.7 | [-7.1, -4.0]                 |                      0.88 |                  3.9e-08 |                                       0.79 |                     0.04 |
|       6 | LightGBM, global (unseen region, zero-shot) | LightGBM, local               |                                    -3.1 | [-5.6, -1.8]                 |                      0.71 |                  0.0067  |                                       0.54 |                     0.15 |
|       6 | LightGBM, global (unseen region, zero-shot) | Seasonal naive (24 h)         |                                   -35.3 | [-37.2, -32.6]               |                      0.98 |                  6.4e-13 |                                       0.98 |                     0.02 |
|       6 | LightGBM, global (in-region)                | Ridge, global (in-region)     |                                   -15.8 | [-18.1, -14.1]               |                      1    |                  5.1e-13 |                                       1    |                     0    |
|       6 | Ridge, global (unseen region)               | Ridge, global (in-region)     |                                     0.2 | [0.1, 0.2]                   |                      0.25 |                  0.00065 |                                     nan    |                   nan    |
|       6 | LightGBM, global (unseen region, zero-shot) | Ridge, global (unseen region) |                                   -13   | [-15.5, -12.3]               |                      0.98 |                  3.6e-12 |                                     nan    |                   nan    |
|       6 | LightGBM, local                             | Seasonal naive (24 h)         |                                   -32.5 | [-35.3, -29.9]               |                      1    |                  5.1e-13 |                                     nan    |                   nan    |
|      24 | LightGBM, global (unseen region, zero-shot) | LightGBM, global (in-region)  |                                     0.5 | [0.4, 0.7]                   |                      0.06 |                  2.5e-11 |                                       0    |                     0.52 |
|      24 | LightGBM, global (in-region)                | LightGBM, local               |                                    -1.4 | [-2.2, -0.8]                 |                      0.71 |                  0.0029  |                                       0.35 |                     0.06 |
|      24 | LightGBM, global (unseen region, zero-shot) | LightGBM, local               |                                    -0.8 | [-1.6, 0.2]                  |                      0.62 |                  0.21    |                                       0.31 |                     0.17 |
|      24 | LightGBM, global (unseen region, zero-shot) | Seasonal naive (24 h)         |                                   -12   | [-15.2, -10.5]               |                      1    |                  5.1e-13 |                                       0.94 |                     0    |
|      24 | LightGBM, global (in-region)                | Ridge, global (in-region)     |                                    -5.5 | [-7.1, -5.2]                 |                      1    |                  5.1e-13 |                                       0.98 |                     0    |
|      24 | Ridge, global (unseen region)               | Ridge, global (in-region)     |                                     0.1 | [0.0, 0.2]                   |                      0.25 |                  0.00021 |                                     nan    |                   nan    |
|      24 | LightGBM, global (unseen region, zero-shot) | Ridge, global (unseen region) |                                    -5.4 | [-6.5, -4.6]                 |                      1    |                  5.1e-13 |                                     nan    |                   nan    |
|      24 | LightGBM, local                             | Seasonal naive (24 h)         |                                   -11.7 | [-14.3, -10.1]               |                      0.98 |                  6.4e-13 |                                     nan    |                   nan    |






![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig06_regional_errors.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 6.** (a) Per-BA nMAE of the global model when the BA is held out vs included in training (colour: log10 mean demand). (b) Relative geographic generalisation gap vs BA size.
:::



**Operator reference.** The BAs' own day-ahead forecasts reach a median nMAE of 3.57% on the same hours, against 4.64% for G-IN at 24 h (Table 3). Operators use weather forecasts and our models do not, so this difference mainly reflects the value of weather information at the day-ahead horizon. It is not a like-for-like comparison of methods.



::: {custom-style="Table Caption"}
**Table 3.** Comparison with BA-reported day-ahead forecasts (hours where available).
:::

|   h (h) | Method                                      | nMAE % median [IQR]   |   Bias % median |   Regions |
|--------:|:--------------------------------------------|:----------------------|----------------:|----------:|
|       1 | BA day-ahead forecast (reference)           | 3.57 [2.55, 6.41]     |            0.01 |        48 |
|       1 | LightGBM, global (in-region)                | 1.14 [0.87, 1.51]     |            0.01 |        48 |
|       1 | LightGBM, global (unseen region, zero-shot) | 1.17 [0.90, 1.55]     |            0.01 |        48 |
|       1 | Seasonal naive (24 h)                       | 5.47 [4.57, 6.81]     |           -0.02 |        48 |
|       6 | BA day-ahead forecast (reference)           | 3.57 [2.55, 6.41]     |            0.01 |        48 |
|       6 | LightGBM, global (in-region)                | 3.49 [2.95, 4.35]     |            0.03 |        48 |
|       6 | LightGBM, global (unseen region, zero-shot) | 3.65 [3.03, 4.40]     |           -0.01 |        48 |
|       6 | Seasonal naive (24 h)                       | 5.47 [4.57, 6.81]     |           -0.02 |        48 |
|      24 | BA day-ahead forecast (reference)           | 3.57 [2.55, 6.41]     |            0.01 |        48 |
|      24 | LightGBM, global (in-region)                | 4.64 [3.88, 5.87]     |           -0.1  |        48 |
|      24 | LightGBM, global (unseen region, zero-shot) | 4.75 [3.91, 5.91]     |           -0.1  |        48 |
|      24 | Seasonal naive (24 h)                       | 5.47 [4.57, 6.81]     |           -0.02 |        48 |




## Limited target-data adaptation (RQ2)

Table 4 and Fig. 7 compare adaptation strategies for unseen BAs.

**Local models need history.** With little target history, local models are poor. At $h = 24$ h, a local model trained on one week reaches a median nMAE of 9.21%, on four weeks 8.07% and on thirteen weeks 5.77%. All of these are worse than the zero-shot global model (4.75%).

**Fine-tuning gives little and can hurt.** Fine-tuning the global model on the same data yields 5.37%, 5.26% and 5.00% for one, four and thirteen weeks. The median relative change versus zero-shot is 12.9% with four weeks (CI 9.7 to 17.9%) and 6.5% with thirteen. At $h = 1$ h the corresponding changes are 0.9% and -1.5%.

The adaptation windows end in late December, so they over-represent winter and holiday conditions. This is a realistic feature of onboarding at an arbitrary date, and Section 10 discusses it.



::: {custom-style="Table Caption"}
**Table 4.** Limited target-data adaptation for unseen BAs (test 2024–2025).
:::

|   h (h) | Method                                      | nMAE % median [IQR]   |   MASE median |
|--------:|:--------------------------------------------|:----------------------|--------------:|
|       1 | Seasonal naive (24 h)                       | 5.48 [4.57, 6.81]     |         1.009 |
|       1 | LightGBM, global (unseen region, zero-shot) | 1.17 [0.90, 1.55]     |         0.201 |
|       1 | LightGBM local, 1 wk target data            | 5.35 [4.74, 7.09]     |         1.004 |
|       1 | Global fine-tuned, 1 wk target data         | 1.24 [0.99, 1.59]     |         0.212 |
|       1 | LightGBM local, 4 wk target data            | 3.87 [3.21, 4.72]     |         0.679 |
|       1 | Global fine-tuned, 4 wk target data         | 1.21 [0.94, 1.56]     |         0.205 |
|       1 | LightGBM local, 13 wk target data           | 2.09 [1.81, 2.45]     |         0.345 |
|       1 | Global fine-tuned, 13 wk target data        | 1.16 [0.89, 1.51]     |         0.197 |
|       1 | LightGBM, local                             | 1.28 [1.01, 1.61]     |         0.22  |
|       1 | LightGBM, global (in-region)                | 1.14 [0.87, 1.51]     |         0.194 |
|       6 | Seasonal naive (24 h)                       | 5.48 [4.57, 6.81]     |         1.009 |
|       6 | LightGBM, global (unseen region, zero-shot) | 3.66 [3.03, 4.40]     |         0.654 |
|       6 | LightGBM local, 1 wk target data            | 8.92 [7.04, 11.55]    |         1.587 |
|       6 | Global fine-tuned, 1 wk target data         | 4.01 [3.44, 5.21]     |         0.753 |
|       6 | LightGBM local, 4 wk target data            | 7.79 [5.93, 10.58]    |         1.449 |
|       6 | Global fine-tuned, 4 wk target data         | 3.93 [3.17, 4.89]     |         0.719 |
|       6 | LightGBM local, 13 wk target data           | 5.45 [4.73, 6.67]     |         1.023 |
|       6 | Global fine-tuned, 13 wk target data        | 3.70 [3.06, 4.67]     |         0.675 |
|       6 | LightGBM, local                             | 3.78 [3.13, 4.60]     |         0.676 |
|       6 | LightGBM, global (in-region)                | 3.50 [2.95, 4.35]     |         0.627 |
|      24 | Seasonal naive (24 h)                       | 5.48 [4.57, 6.81]     |         1.009 |
|      24 | LightGBM, global (unseen region, zero-shot) | 4.75 [3.91, 5.91]     |         0.888 |
|      24 | LightGBM local, 1 wk target data            | 9.21 [7.57, 11.18]    |         1.728 |
|      24 | Global fine-tuned, 1 wk target data         | 5.37 [4.43, 6.90]     |         1.057 |
|      24 | LightGBM local, 4 wk target data            | 8.07 [6.50, 9.65]     |         1.462 |
|      24 | Global fine-tuned, 4 wk target data         | 5.26 [4.42, 7.09]     |         1.029 |
|      24 | LightGBM local, 13 wk target data           | 5.77 [5.06, 7.30]     |         1.13  |
|      24 | Global fine-tuned, 13 wk target data        | 5.00 [4.16, 6.43]     |         0.969 |
|      24 | LightGBM, local                             | 4.72 [3.94, 5.94]     |         0.893 |
|      24 | LightGBM, global (in-region)                | 4.64 [3.88, 5.87]     |         0.884 |






![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig08_transfer.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 7.** Limited target-data adaptation for unseen BAs: median test nMAE vs weeks of target history.
:::



## Temporal distribution shift (RQ4)

**Drift with model age.** Errors of models frozen at the end of 2022 did not grow monotonically with their age (Table 5; Fig. 8). At $h = 24$ h the median nMAE of G-IN was 4.60% in 2023 (validation year, mildly optimistic because it includes the early-stopping weeks), 4.54% in 2024 and 4.67% in 2025. The seasonal naive benchmark follows the same pattern (5.16% in 2024 and 5.56% in 2025), which indicates that 2025 was intrinsically harder to forecast rather than that the models aged. The increase from 2024 to 2025 was largest for local models (4.49% to 4.80%), compared with the zero-shot model (4.56% to 4.72%) and G-IN.

**Seasonal pattern.** Errors are highest in winter and summer and lowest in autumn: at 24 h, G-IN reaches 4.76% in DJF, 4.76% in JJA and 4.34% in SON. This pattern reflects weather-driven heating and cooling load that calendar and lag features cannot anticipate.

**Effect of refitting.** Refitting on data through 2023 and evaluating on 2025 (Table 6) leaves the median nMAE of G-IN essentially unchanged (4.67% frozen, 4.67% refit), and of local models from 4.80% to 4.78%. The median per-BA relative change is 0.1% for G-IN (Holm $p$ = 0.87) and -0.9% for local models (Holm $p$ = <0.0001). Refitting thus benefits local models, which gain a fifth year of their own data, but not the pooled model, which already has abundant data.



::: {custom-style="Table Caption"}
**Table 5.** Median nMAE (%) by evaluation year (frozen models trained on 2019–2022).
:::

|   h (h) | Method                                      |   2023 (validation) |   2024 |   2025 |
|--------:|:--------------------------------------------|--------------------:|-------:|-------:|
|       1 | LightGBM, global (in-region)                |                1.11 |   1.12 |   1.19 |
|       1 | LightGBM, global (unseen region, zero-shot) |                1.17 |   1.16 |   1.22 |
|       1 | LightGBM, local                             |                1.22 |   1.26 |   1.3  |
|       1 | Seasonal naive (24 h)                       |                5.34 |   5.16 |   5.56 |
|       6 | LightGBM, global (in-region)                |                3.44 |   3.49 |   3.53 |
|       6 | LightGBM, global (unseen region, zero-shot) |                3.65 |   3.64 |   3.64 |
|       6 | LightGBM, local                             |                3.57 |   3.69 |   3.8  |
|       6 | Seasonal naive (24 h)                       |                5.34 |   5.16 |   5.56 |
|      24 | LightGBM, global (in-region)                |                4.6  |   4.54 |   4.67 |
|      24 | LightGBM, global (unseen region, zero-shot) |                4.67 |   4.56 |   4.72 |
|      24 | LightGBM, local                             |                4.56 |   4.49 |   4.8  |
|      24 | Seasonal naive (24 h)                       |                5.34 |   5.16 |   5.56 |






::: {custom-style="Table Caption"}
**Table 6.** Frozen vs. refit (rolling origin) models on 2025: median nMAE (%).
:::

|   h (h) |   Global frozen (2025) % |   Global refit (2025) % |   Local frozen (2025) % |   Local refit (2025) % |
|--------:|-------------------------:|------------------------:|------------------------:|-----------------------:|
|       1 |                     1.19 |                    1.2  |                     1.3 |                   1.26 |
|       6 |                     3.53 |                    3.49 |                     3.8 |                   3.71 |
|      24 |                     4.67 |                    4.67 |                     4.8 |                   4.78 |






![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig07_temporal_shift.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 8.** Temporal distribution shift: (a) median nMAE by year for models trained on 2019–2022; (b) by season (test period); (c) frozen vs refit models on 2025.
:::



## Interval calibration under geographic and temporal shift (RQ3)

Table 7 and Fig. 9 report interval calibration.

**Calibration fails BA by BA, not on average.** The static methods are close to nominal *on average* but not *per BA*. At $h = 24$ h and nominal 90%, CQR calibrated on source BAs achieves a mean coverage of 89.2% for unseen BAs, yet coverage ranges down to 78.6%. In 20.8% of BAs it is more than 5 percentage points below nominal. Raw quantile regression under-covers more (mean 87.3%), and symmetric SCP has the widest spread across BAs (minimum 71.4%).

**Geographic shift matters little for calibration.** Unseen-region intervals behave almost identically to in-region ones: in-region CQR reaches a mean of 89.2% and under-covers in 18.8% of BAs. The binding problem is *heterogeneity across BAs and over time*, not the absence of the BA from training.

**Target calibration from recent weeks fails.** Calibrating on the target BA's own last four weeks (SCP-T4) *reduces* mean coverage to 85.3%. Four December weeks are not exchangeable with the following two years.

**Temporal drift lowers coverage.** Static coverage declines from 2024 to 2025: CQR falls from 89.5% to 88.8% (Fig. 9c).

**ACI restores per-BA coverage, but its step size is decisive.** Adaptive conformal inference with horizon-delayed feedback restores coverage in every BA. With the pre-registered step size $\gamma = 0.005$, coverage is 90.0% on average, with a minimum of 89.8%. This is partly achieved, however, by issuing very wide intervals: the threshold is capped in a mean of 4.4% of hours, and the median interval score rises to 88.55% of mean load, against 28.15% for CQR.

**A validation-selected step size gives coverage and sharpness.** Choosing $\gamma$ on the 2023 data of held-out BAs selects $\gamma$ = 0.001 at 24 h and 0.002 at 1 h. The resulting ACI-CQR-V keeps per-BA coverage between 89.4% and 90.5% at 24 h. Its median interval score (28.24%) and median hourly width (17.81% of mean load) are on a par with CQR. The same holds at $h = 1$ h: ACI-CQR-V coverage has a minimum of 89.7% and a median interval score of 7.13%, against 7.21% for CQR, while static CQR under-covers in 33.3% of BAs.

**Post-hoc sensitivity.** Table 8 shows the test-set sensitivity of ACI to $\gamma$. It is labelled post hoc and was not used for selection. The degradation at $\gamma \ge 0.005$ is consistent with the 24-h feedback delay: with large steps, $\alpha_t$ overshoots before the effect of earlier updates is observed.



::: {custom-style="Table Caption"}
**Table 7.** Interval calibration on the test period (48 BAs).
:::

| Nominal   |   h (h) | Setting       | Method    |   Mean coverage % | Min–max coverage %   |   Mean |cov. dev.| pp |   BAs under-covered >5 pp |   Median hourly width % |   Mean width % |   Median interval score % |
|:----------|--------:|:--------------|:----------|------------------:|:---------------------|----------------------:|--------------------------:|------------------------:|---------------:|--------------------------:|
| 90%       |       1 | in-region     | QR        |              84.8 | 66.7–96.4            |                   6.8 |                        44 |                    4.08 |           4.46 |                      7.12 |
| 90%       |       1 | in-region     | SCP       |              88.3 | 54.8–99.5            |                   7   |                        31 |                    4.8  |           4.96 |                      7.45 |
| 90%       |       1 | in-region     | CQR       |              88.7 | 70.1–98.0            |                   5.3 |                        25 |                    4.59 |           4.98 |                      6.99 |
| 90%       |       1 | in-region     | SCP-T4    |              86.4 | 74.1–95.5            |                   4.6 |                        29 |                    4.1  |           4.44 |                      7.54 |
| 90%       |       1 | in-region     | ACI-CQR   |              90   | 89.9–90.1            |                   0   |                         0 |                    4.76 |           5.34 |                      7.15 |
| 90%       |       1 | in-region     | ACI-CQR-V |              90   | 89.7–90.4            |                   0.1 |                         0 |                    4.74 |           5.17 |                      6.9  |
| 90%       |       1 | unseen-region | QR        |              83.9 | 64.8–97.5            |                   7.8 |                        52 |                    4.2  |           4.53 |                      7.4  |
| 90%       |       1 | unseen-region | SCP       |              87.5 | 52.6–98.9            |                   7.2 |                        31 |                    4.78 |           4.93 |                      7.72 |
| 90%       |       1 | unseen-region | CQR       |              88.1 | 69.2–98.7            |                   5.9 |                        33 |                    4.74 |           5.1  |                      7.21 |
| 90%       |       1 | unseen-region | SCP-T4    |              86.9 | 74.3–96.5            |                   4.6 |                        29 |                    4.3  |           4.58 |                      7.81 |
| 90%       |       1 | unseen-region | ACI-CQR   |              90   | 89.9–90.2            |                   0   |                         0 |                    4.9  |           5.49 |                      7.4  |
| 90%       |       1 | unseen-region | ACI-CQR-V |              90   | 89.7–90.4            |                   0.1 |                         0 |                    4.9  |           5.38 |                      7.13 |
| 90%       |      24 | in-region     | QR        |              87.5 | 77.2–93.3            |                   3.5 |                        23 |                   17.04 |          20.25 |                     27.79 |
| 90%       |      24 | in-region     | SCP       |              89.1 | 71.7–99.3            |                   5.5 |                        31 |                   20.29 |          20.96 |                     31.43 |
| 90%       |      24 | in-region     | CQR       |              89.2 | 79.7–95.1            |                   3.1 |                        19 |                   17.98 |          21.18 |                     27.78 |
| 90%       |      24 | in-region     | SCP-T4    |              85.3 | 61.4–96.2            |                   6.4 |                        40 |                   15.27 |          15.97 |                     34.23 |
| 90%       |      24 | in-region     | ACI-CQR   |              90   | 89.8–90.1            |                   0.1 |                         0 |                   18.37 |          98.41 |                    104.47 |
| 90%       |      24 | in-region     | ACI-CQR-V |              89.9 | 89.4–90.4            |                   0.2 |                         0 |                   17.75 |          21.03 |                     27.81 |
| 90%       |      24 | unseen-region | QR        |              87.3 | 76.1–96.1            |                   3.8 |                        29 |                   17.15 |          20.14 |                     28.26 |
| 90%       |      24 | unseen-region | SCP       |              88.9 | 71.4–99.3            |                   5.6 |                        29 |                   20.14 |          20.88 |                     31.88 |
| 90%       |      24 | unseen-region | CQR       |              89.2 | 78.6–97.3            |                   3.5 |                        21 |                   18.14 |          21.18 |                     28.15 |
| 90%       |      24 | unseen-region | SCP-T4    |              85.3 | 60.8–95.9            |                   6.3 |                        40 |                   14.97 |          15.68 |                     34.15 |
| 90%       |      24 | unseen-region | ACI-CQR   |              90   | 89.8–90.2            |                   0.1 |                         0 |                   18.6  |          82.58 |                     88.55 |
| 90%       |      24 | unseen-region | ACI-CQR-V |              89.9 | 89.4–90.5            |                   0.3 |                         0 |                   17.81 |          21.32 |                     28.24 |
| 50%       |       1 | in-region     | QR        |              41.9 | 28.2–57.8            |                   8.9 |                        69 |                    1.31 |           1.48 |                      3.78 |
| 50%       |       1 | in-region     | SCP       |              48   | 21.3–75.8            |                  10.7 |                        40 |                    1.49 |           1.54 |                      3.79 |
| 50%       |       1 | in-region     | CQR       |              48.5 | 32.2–67.6            |                   7.2 |                        35 |                    1.55 |           1.73 |                      3.75 |
| 50%       |       1 | in-region     | SCP-T4    |              46.7 | 33.2–61.1            |                   5.6 |                        31 |                    1.45 |           1.5  |                      3.82 |
| 50%       |       1 | in-region     | ACI-CQR   |              49.9 | 49.6–50.1            |                   0.1 |                         0 |                    1.64 |           1.84 |                      3.75 |
| 50%       |       1 | in-region     | ACI-CQR-V |              49.8 | 48.9–50.3            |                   0.2 |                         0 |                    1.63 |           1.83 |                      3.75 |
| 50%       |       1 | unseen-region | QR        |              41.4 | 27.2–58.7            |                   9.8 |                        65 |                    1.35 |           1.52 |                      3.9  |
| 50%       |       1 | unseen-region | SCP       |              46.3 | 20.3–73.6            |                  10.5 |                        50 |                    1.49 |           1.54 |                      3.91 |
| 50%       |       1 | unseen-region | CQR       |              47.7 | 31.0–66.9            |                   8.1 |                        42 |                    1.58 |           1.77 |                      3.88 |
| 50%       |       1 | unseen-region | SCP-T4    |              47.3 | 34.0–64.5            |                   5.6 |                        35 |                    1.52 |           1.6  |                      3.9  |
| 50%       |       1 | unseen-region | ACI-CQR   |              49.9 | 49.5–50.2            |                   0.1 |                         0 |                    1.69 |           1.93 |                      3.87 |
| 50%       |       1 | unseen-region | ACI-CQR-V |              49.8 | 48.9–50.4            |                   0.2 |                         0 |                    1.69 |           1.92 |                      3.87 |
| 50%       |      24 | in-region     | QR        |              47.6 | 36.5–55.5            |                   3.9 |                        25 |                    6.31 |           7.5  |                     15.27 |
| 50%       |      24 | in-region     | SCP       |              48.3 | 29.8–74.1            |                   7.4 |                        38 |                    6.11 |           6.31 |                     15.6  |
| 50%       |      24 | in-region     | CQR       |              48.8 | 37.5–56.8            |                   3.8 |                        19 |                    6.5  |           7.69 |                     15.28 |
| 50%       |      24 | in-region     | SCP-T4    |              48.6 | 22.4–67.4            |                   7.2 |                        33 |                    6.05 |           6.1  |                     15.86 |
| 50%       |      24 | in-region     | ACI-CQR   |              49.9 | 49.6–50.2            |                   0.1 |                         0 |                    6.62 |           7.66 |                     15.34 |
| 50%       |      24 | in-region     | ACI-CQR-V |              49.7 | 48.6–50.6            |                   0.4 |                         0 |                    6.59 |           7.54 |                     15.28 |
| 50%       |      24 | unseen-region | QR        |              47.1 | 36.3–58.2            |                   4.5 |                        29 |                    6.23 |           7.4  |                     15.64 |
| 50%       |      24 | unseen-region | SCP       |              47.9 | 29.9–73.1            |                   7.6 |                        35 |                    6.08 |           6.28 |                     15.89 |
| 50%       |      24 | unseen-region | CQR       |              48.8 | 37.6–60.7            |                   4.2 |                        25 |                    6.49 |           7.68 |                     15.64 |
| 50%       |      24 | unseen-region | SCP-T4    |              48.9 | 23.3–65.0            |                   7   |                        33 |                    6    |           6.15 |                     16.07 |
| 50%       |      24 | unseen-region | ACI-CQR   |              49.9 | 49.6–50.2            |                   0.1 |                         0 |                    6.75 |           7.69 |                     15.68 |
| 50%       |      24 | unseen-region | ACI-CQR-V |              49.7 | 48.5–50.7            |                   0.4 |                         0 |                    6.63 |           7.54 |                     15.64 |






::: {custom-style="Table Caption"}
**Table 8.** POST-HOC test-set sensitivity of ACI-CQR (90%, unseen BAs) to the step size γ (not used for any selection).
:::

|   h (h) |     γ |   Mean coverage % |   Min coverage % |   Median hourly width % of mean load |   Median interval score % |   Capped hours % |
|--------:|------:|------------------:|-----------------:|-------------------------------------:|--------------------------:|-----------------:|
|       1 | 0.001 |              90   |             89.5 |                                 4.88 |                      7.13 |             0    |
|       1 | 0.002 |              90   |             89.7 |                                 4.9  |                      7.13 |             0    |
|       1 | 0.005 |              90   |             89.9 |                                 4.9  |                      7.4  |             0.09 |
|       1 | 0.01  |              90   |             89.9 |                                 4.93 |                      7.71 |             0.46 |
|      24 | 0.001 |              89.9 |             89.4 |                                17.81 |                     28.24 |             0.13 |
|      24 | 0.002 |              89.9 |             89.6 |                                18.05 |                     29.35 |             0.97 |
|      24 | 0.005 |              90   |             89.8 |                                18.6  |                     88.55 |             4.37 |
|      24 | 0.01  |              90   |             89.9 |                                19.51 |                    272.91 |            12.25 |






![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig09_calibration.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 9.** Calibration of nominal 90% intervals (h = 24 h): per-BA coverage (dots; bar = mean) for (a) in-region and (b) unseen-region models; (c) monthly pooled coverage for unseen BAs.
:::





![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig10_interval_example.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 10.** Day-ahead 90% prediction intervals for an unseen BA (IID), test period (BA chosen as the one with median CQR coverage).
:::




# Discussion

**Why does zero-shot transfer work so well here?** Three design choices make an unseen BA look "in distribution" to a global model.

- *Instance scaling* by the trailing weekly mean removes level differences of three orders of magnitude, and with them most of the between-BA variation in absolute terms.
- *Shared shapes.* Once normalised, the daily and weekly profiles of U.S. BAs share a small number of shapes driven by human activity and climate. Forty source BAs from all three interconnections cover these shapes well. The ablation in Section 11 shows that accuracy degrades only when the source pool is small.
- *Lag-dominated information.* At short horizons the most recent observations carry most of the information. This explains why the geographic gap, although statistically clear, is small in absolute terms: about 0.1 percentage point of nMAE at 24 h. It also explains why the gap is largest in relative terms at 1 h, where errors are smallest and BA-specific intraday dynamics matter most. The largest relative gaps occur in a few BAs: Grant County PUD (GCPD) at every horizon, and MISO at 1 h. We did not investigate the causes, which may include atypical customer mixes or reporting practices.

The finding that a never-seen global model matches local models trained on four years of target data is consistent with the global-model literature [@montero2021principles]. It has a direct practical corollary: for system-level load with the information set studied here, *data pooling is worth more than target-specific history*.

**Why does fine-tuning on a few weeks hurt?** Continued boosting on one to thirteen weeks fits the idiosyncrasies of a short, seasonally unrepresentative window: late-December weeks, with holidays and winter peaks. It degrades accuracy on the following two years. Local models trained on the same window are far worse still. Without a validation scheme for choosing how much to adapt, which the short window cannot provide, the safest policy for a newly onboarded system is to use the pooled model unchanged. Adaptation should be revisited once at least a full seasonal cycle is available. Shrinkage-based or regularised adaptation, and adaptation of the *calibration layer* rather than of the point model, are natural alternatives. The latter is what ACI effectively does.

**Calibration is a per-system and per-period property.** Average coverage over 48 BAs hides large BA-level deviations. A single pooled calibration set cannot be exchangeable with every BA. This holds for unseen and in-region BAs alike, which is why the geographic shift changes calibration much less than the heterogeneity among BAs does. Short target-specific calibration windows fail for the same reason that short adaptation windows do: they are seasonally unrepresentative. Online recalibration with ACI solves the per-BA coverage problem without any target history, but only if its step size is matched to the feedback delay. With delayed feedback (24 h), a step that is too large lets $\alpha_t$ overshoot before earlier updates take effect, producing occasional extreme intervals. Selecting $\gamma$ on validation data from other BAs and periods worked well here. The aggregated variant [@zaffran2022adaptive], which removes the choice altogether, is a natural next step.

**Relation to operator forecasts.** The BAs' own day-ahead forecasts are more accurate than our weather-free 24-h models. This is expected and does not contradict the main findings. The purpose of the benchmark is to isolate the effects of geographic and temporal shift under a fixed, reproducible information set, not to replace operational weather-driven forecasting. The results suggest a practical complement: a pooled, weather-free model calibrated online can serve as a reliable fallback or sanity check for any BA from day one, including BAs without forecasting staff.


# Robustness and ablation analysis

## Missing input observations (RQ4)

Table 9 and Fig. 11 report accuracy when test-period inputs are corrupted while labels are left intact.

**Day-ahead forecasts degrade modestly.** At $h = 24$ h, with 10% of input hours missing completely at random (MCAR), the median nMAE of G-IN rises from 4.64% to 5.05% with LightGBM's native missing-value handling. It rises to 6.93% when 40% of inputs are missing.

**Hour-ahead forecasts are far more sensitive,** because they rely on the most recent observation. With native handling, 10% MCAR raises the median nMAE from 1.14% to 1.84%, and 40% MCAR to 4.04%.

**The best imputation strategy depends on the gap pattern.**

- For scattered MCAR gaps, causal last-observation-carried-forward imputation is better than native handling (1.68% at 10% MCAR, $h = 1$ h).
- For contiguous outages it is worse: with 168-h blocks at $h = 1$ h it reaches 2.66%, against 1.95% (native) and 2.05% (weekly-seasonal imputation).

**Training with masked inputs is the most effective remedy.** A model trained with 10% MCAR input masking reaches 1.32% at 10% MCAR and 2.29% at 40% MCAR ($h = 1$ h). On clean inputs it costs almost nothing (1.17% versus 1.14%).

**Unseen BAs behave the same way.** The zero-shot model degrades in the same way as the in-region model (e.g., 1.93% at 10% MCAR, $h = 1$ h), so missing data does not interact with geographic shift.

**Unscored hours.** In the most severe scenarios the instance scale cannot be computed for some origins, because fewer than 24 of the preceding 168 hours are observed. No forecast is then issued, and in the worst BA and scenario 96.9% of hours remain scored. Errors are computed on the scored hours.



::: {custom-style="Table Caption"}
**Table 9.** Robustness to missing input observations (test period).
:::

|   h (h) | Scenario   | Strategy   | Model        |   Input missing % |   nMAE % median |   nMAE % mean |   Min. scored share of hours |
|--------:|:-----------|:-----------|:-------------|------------------:|----------------:|--------------:|-----------------------------:|
|       1 | BLOCK_168h | locf       | LGB_G_IN     |               9.7 |            2.66 |          2.8  |                        1     |
|       1 | BLOCK_168h | locf       | LGB_G_LRO    |               9.7 |            2.68 |          2.84 |                        1     |
|       1 | BLOCK_168h | native     | LGB_G_IN     |               9.7 |            1.95 |          2.08 |                        0.969 |
|       1 | BLOCK_168h | native     | LGB_G_IN_AUG |               9.7 |            1.94 |          2.01 |                        0.969 |
|       1 | BLOCK_168h | native     | LGB_G_LRO    |               9.7 |            1.99 |          2.11 |                        0.969 |
|       1 | BLOCK_168h | seasonal   | LGB_G_IN     |               9.7 |            2.05 |          2.07 |                        1     |
|       1 | BLOCK_168h | seasonal   | LGB_G_LRO    |               9.7 |            2.08 |          2.12 |                        1     |
|       1 | BLOCK_24h  | locf       | LGB_G_IN     |               9.5 |            2.52 |          2.56 |                        1     |
|       1 | BLOCK_24h  | locf       | LGB_G_LRO    |               9.5 |            2.56 |          2.6  |                        1     |
|       1 | BLOCK_24h  | native     | LGB_G_IN     |               9.5 |            1.89 |          1.98 |                        1     |
|       1 | BLOCK_24h  | native     | LGB_G_IN_AUG |               9.5 |            1.71 |          1.81 |                        1     |
|       1 | BLOCK_24h  | native     | LGB_G_LRO    |               9.5 |            1.97 |          2.02 |                        1     |
|       1 | BLOCK_24h  | seasonal   | LGB_G_IN     |               9.5 |            1.91 |          2.02 |                        1     |
|       1 | BLOCK_24h  | seasonal   | LGB_G_LRO    |               9.5 |            1.93 |          2.07 |                        1     |
|       1 | MCAR_10    | locf       | LGB_G_IN     |              10.2 |            1.68 |          1.66 |                        1     |
|       1 | MCAR_10    | locf       | LGB_G_LRO    |              10.2 |            1.7  |          1.71 |                        1     |
|       1 | MCAR_10    | native     | LGB_G_IN     |              10.2 |            1.84 |          1.84 |                        1     |
|       1 | MCAR_10    | native     | LGB_G_IN_AUG |              10.2 |            1.32 |          1.41 |                        1     |
|       1 | MCAR_10    | native     | LGB_G_LRO    |              10.2 |            1.93 |          1.93 |                        1     |
|       1 | MCAR_10    | seasonal   | LGB_G_IN     |              10.2 |            2.19 |          2.26 |                        1     |
|       1 | MCAR_10    | seasonal   | LGB_G_LRO    |              10.2 |            2.22 |          2.31 |                        1     |
|       1 | MCAR_20    | locf       | LGB_G_IN     |              20.2 |            2.21 |          2.2  |                        1     |
|       1 | MCAR_20    | locf       | LGB_G_LRO    |              20.2 |            2.24 |          2.24 |                        1     |
|       1 | MCAR_20    | native     | LGB_G_IN     |              20.2 |            2.56 |          2.51 |                        1     |
|       1 | MCAR_20    | native     | LGB_G_IN_AUG |              20.2 |            1.52 |          1.62 |                        1     |
|       1 | MCAR_20    | native     | LGB_G_LRO    |              20.2 |            2.7  |          2.64 |                        1     |
|       1 | MCAR_20    | seasonal   | LGB_G_IN     |              20.2 |            3.19 |          3.27 |                        1     |
|       1 | MCAR_20    | seasonal   | LGB_G_LRO    |              20.2 |            3.25 |          3.31 |                        1     |
|       1 | MCAR_40    | locf       | LGB_G_IN     |              40.1 |            3.68 |          3.68 |                        1     |
|       1 | MCAR_40    | locf       | LGB_G_LRO    |              40.1 |            3.68 |          3.7  |                        1     |
|       1 | MCAR_40    | native     | LGB_G_IN     |              40.1 |            4.04 |          4.11 |                        1     |
|       1 | MCAR_40    | native     | LGB_G_IN_AUG |              40.1 |            2.29 |          2.34 |                        1     |
|       1 | MCAR_40    | native     | LGB_G_LRO    |              40.1 |            4.22 |          4.31 |                        1     |
|       1 | MCAR_40    | seasonal   | LGB_G_IN     |              40.1 |            5.14 |          5.28 |                        1     |
|       1 | MCAR_40    | seasonal   | LGB_G_LRO    |              40.1 |            5.19 |          5.31 |                        1     |
|       1 | MCAR_5     | locf       | LGB_G_IN     |               5.2 |            1.37 |          1.44 |                        1     |
|       1 | MCAR_5     | locf       | LGB_G_LRO    |               5.2 |            1.41 |          1.48 |                        1     |
|       1 | MCAR_5     | native     | LGB_G_IN     |               5.2 |            1.47 |          1.53 |                        1     |
|       1 | MCAR_5     | native     | LGB_G_IN_AUG |               5.2 |            1.25 |          1.33 |                        1     |
|       1 | MCAR_5     | native     | LGB_G_LRO    |               5.2 |            1.56 |          1.6  |                        1     |
|       1 | MCAR_5     | seasonal   | LGB_G_IN     |               5.2 |            1.66 |          1.76 |                        1     |
|       1 | MCAR_5     | seasonal   | LGB_G_LRO    |               5.2 |            1.7  |          1.8  |                        1     |
|       1 | clean      | native     | LGB_G_IN     |               0.2 |            1.14 |          1.23 |                        1     |
|       1 | clean      | native     | LGB_G_IN_AUG |               0.2 |            1.17 |          1.26 |                        1     |
|       1 | clean      | native     | LGB_G_LRO    |               0.2 |            1.17 |          1.28 |                        1     |
|      24 | BLOCK_168h | locf       | LGB_G_IN     |               9.7 |            6.11 |          6.07 |                        1     |
|      24 | BLOCK_168h | locf       | LGB_G_LRO    |               9.7 |            6.14 |          6.1  |                        1     |
|      24 | BLOCK_168h | native     | LGB_G_IN     |               9.7 |            5.07 |          5.34 |                        0.969 |
|      24 | BLOCK_168h | native     | LGB_G_IN_AUG |               9.7 |            5.03 |          5.3  |                        0.969 |
|      24 | BLOCK_168h | native     | LGB_G_LRO    |               9.7 |            5.08 |          5.38 |                        0.969 |
|      24 | BLOCK_168h | seasonal   | LGB_G_IN     |               9.7 |            5.09 |          5.42 |                        1     |
|      24 | BLOCK_168h | seasonal   | LGB_G_LRO    |               9.7 |            5.12 |          5.46 |                        1     |
|      24 | BLOCK_24h  | locf       | LGB_G_IN     |               9.5 |            5.81 |          5.82 |                        1     |
|      24 | BLOCK_24h  | locf       | LGB_G_LRO    |               9.5 |            5.83 |          5.85 |                        1     |
|      24 | BLOCK_24h  | native     | LGB_G_IN     |               9.5 |            5.02 |          5.3  |                        1     |
|      24 | BLOCK_24h  | native     | LGB_G_IN_AUG |               9.5 |            4.94 |          5.22 |                        1     |
|      24 | BLOCK_24h  | native     | LGB_G_LRO    |               9.5 |            5.12 |          5.33 |                        1     |
|      24 | BLOCK_24h  | seasonal   | LGB_G_IN     |               9.5 |            5.13 |          5.39 |                        1     |
|      24 | BLOCK_24h  | seasonal   | LGB_G_LRO    |               9.5 |            5.21 |          5.42 |                        1     |
|      24 | MCAR_10    | locf       | LGB_G_IN     |              10.2 |            4.81 |          5.09 |                        1     |
|      24 | MCAR_10    | locf       | LGB_G_LRO    |              10.2 |            4.91 |          5.12 |                        1     |
|      24 | MCAR_10    | native     | LGB_G_IN     |              10.2 |            5.05 |          5.33 |                        1     |
|      24 | MCAR_10    | native     | LGB_G_IN_AUG |              10.2 |            4.72 |          5.03 |                        1     |
|      24 | MCAR_10    | native     | LGB_G_LRO    |              10.2 |            5.14 |          5.36 |                        1     |
|      24 | MCAR_10    | seasonal   | LGB_G_IN     |              10.2 |            5.06 |          5.41 |                        1     |
|      24 | MCAR_10    | seasonal   | LGB_G_LRO    |              10.2 |            5.16 |          5.45 |                        1     |
|      24 | MCAR_20    | locf       | LGB_G_IN     |              20.2 |            5.05 |          5.28 |                        1     |
|      24 | MCAR_20    | locf       | LGB_G_LRO    |              20.2 |            5.13 |          5.31 |                        1     |
|      24 | MCAR_20    | native     | LGB_G_IN     |              20.2 |            5.62 |          5.77 |                        1     |
|      24 | MCAR_20    | native     | LGB_G_IN_AUG |              20.2 |            4.87 |          5.12 |                        1     |
|      24 | MCAR_20    | native     | LGB_G_LRO    |              20.2 |            5.69 |          5.79 |                        1     |
|      24 | MCAR_20    | seasonal   | LGB_G_IN     |              20.2 |            5.57 |          5.89 |                        1     |
|      24 | MCAR_20    | seasonal   | LGB_G_LRO    |              20.2 |            5.65 |          5.91 |                        1     |
|      24 | MCAR_40    | locf       | LGB_G_IN     |              40.1 |            5.98 |          5.95 |                        1     |
|      24 | MCAR_40    | locf       | LGB_G_LRO    |              40.1 |            5.99 |          5.98 |                        1     |
|      24 | MCAR_40    | native     | LGB_G_IN     |              40.1 |            6.93 |          6.88 |                        1     |
|      24 | MCAR_40    | native     | LGB_G_IN_AUG |              40.1 |            5.4  |          5.54 |                        1     |
|      24 | MCAR_40    | native     | LGB_G_LRO    |              40.1 |            7.02 |          6.9  |                        1     |
|      24 | MCAR_40    | seasonal   | LGB_G_IN     |              40.1 |            6.66 |          6.91 |                        1     |
|      24 | MCAR_40    | seasonal   | LGB_G_LRO    |              40.1 |            6.69 |          6.93 |                        1     |
|      24 | MCAR_5     | locf       | LGB_G_IN     |               5.2 |            4.72 |          5.02 |                        1     |
|      24 | MCAR_5     | locf       | LGB_G_LRO    |               5.2 |            4.82 |          5.06 |                        1     |
|      24 | MCAR_5     | native     | LGB_G_IN     |               5.2 |            4.84 |          5.14 |                        1     |
|      24 | MCAR_5     | native     | LGB_G_IN_AUG |               5.2 |            4.68 |          4.99 |                        1     |
|      24 | MCAR_5     | native     | LGB_G_LRO    |               5.2 |            4.94 |          5.18 |                        1     |
|      24 | MCAR_5     | seasonal   | LGB_G_IN     |               5.2 |            4.86 |          5.19 |                        1     |
|      24 | MCAR_5     | seasonal   | LGB_G_LRO    |               5.2 |            4.96 |          5.22 |                        1     |
|      24 | clean      | native     | LGB_G_IN     |               0.2 |            4.64 |          4.96 |                        1     |
|      24 | clean      | native     | LGB_G_IN_AUG |               0.2 |            4.65 |          4.97 |                        1     |
|      24 | clean      | native     | LGB_G_LRO    |               0.2 |            4.75 |          5    |                        1     |






![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig11_missing_data.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 11.** Robustness to missing inputs: median test nMAE vs share of missing input hours for imputation strategies; × and + mark 24-h and 168-h outage scenarios.
:::



## Ablations of the zero-shot model

Table 10 and Fig. 12 report ablations for unseen BAs at $h = 24$ h. Each is measured as the median per-BA relative change in nMAE against the full zero-shot model.

**Feature groups.** The changes are:

- removing calendar features: 6.7% (95% CI 5.0 to 7.0%);
- removing the weekly lags: 0.6% (CI 0.5 to 1.3%);
- keeping only the four most recent lags: 0.3% (CI 0.1 to 0.4%).

**Source-pool size.** Shrinking the source pool from 40 BAs to 20, 10 or 5 randomly drawn BAs gives median nMAEs of 4.81%, 4.87% and 4.97% (averages over three draws), against 4.75% with all 40 sources. Results vary little across draws (with five sources, 4.93–5.00%), so the size of the pool, rather than its particular composition, drives the loss.



::: {custom-style="Table Caption"}
**Table 10.** Ablations of the zero-shot global model (h = 24 h, unseen BAs).
:::

| Variant                                     |   nMAE % median | Median rel. change vs full LRO %   | 95% CI       | Wilcoxon p (Holm)   |
|:--------------------------------------------|----------------:|:-----------------------------------|:-------------|:--------------------|
| LightGBM, global (unseen region, zero-shot) |            4.75 | reference                          |              |                     |
| LightGBM, global (in-region)                |            4.64 | -0.5                               | [-0.7, -0.4] | 6.3e-12             |
| Without calendar features                   |            5.09 | 6.7                                | [5.0, 7.0]   | 9.2e-14             |
| Without weekly lags (168, 336 h)            |            4.87 | 0.6                                | [0.5, 1.3]   | 7.8e-05             |
| Recent lags 0–3 h only (drop lags 4–23 h)   |            4.76 | 0.3                                | [0.1, 0.4]   | 7.8e-05             |
| 5 random source BAs (draw 1)                |            4.93 | 3.2                                | [2.2, 4.8]   | 9.2e-14             |
| 5 random source BAs (draw 2)                |            5    | 3.3                                | [2.6, 4.9]   | 3.2e-13             |
| 5 random source BAs (draw 3)                |            4.99 | 3.7                                | [3.1, 4.5]   | 1.6e-13             |
| 10 random source BAs (draw 1)               |            4.87 | 1.6                                | [1.1, 1.9]   | 1.2e-10             |
| 10 random source BAs (draw 2)               |            4.86 | 2.1                                | [1.4, 2.4]   | 7.4e-11             |
| 10 random source BAs (draw 3)               |            4.87 | 2.1                                | [1.6, 2.7]   | 2.1e-13             |
| 20 random source BAs (draw 1)               |            4.79 | 0.8                                | [0.4, 1.1]   | 3.6e-09             |
| 20 random source BAs (draw 2)               |            4.82 | 0.7                                | [0.3, 0.9]   | 3.5e-07             |
| 20 random source BAs (draw 3)               |            4.81 | 0.4                                | [0.2, 0.7]   | 7.8e-05             |






![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig12_ablation.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 12.** Ablations of the zero-shot global model (h = 24 h): (a) feature groups (bars: median relative change; whiskers: 95% bootstrap CI over BAs); (b) size of the source-region pool.
:::



# Computational complexity

All experiments ran on a 4-core CPU with 15 GB of memory (Table 11; Fig. 13).

**Training time.** At $h = 24$ h the pooled LightGBM model trained in 42.0 s on about 1.7 million rows, with model size 4.64 MB. The 48 local models together took 83.6 s, and ridge regression took 20.6 s.

**Shorter horizons.** At $h = 1$ h the pooled model used the full 3,000-tree budget (298.1 s; 70.74 MB), and the 48 local models together took 595.6 s. Inference was correspondingly slower: 164.20 µs per forecast, against 5.59 µs at 24 h. Wall-clock times were measured on a shared virtual machine and are indicative only. In particular, the 6-h in-region fit (1261.9 s) overlapped with a concurrent evaluation job; the six leave-regions-out fits at the same horizon, which ran without contention, averaged 79.7 s.

**Adaptation and calibration.** Fine-tuning on four weeks of target data took 0.23 s per BA at 24 h. Conformal calibration and ACI updates are negligible by comparison: a sort of the calibration scores, plus one quantile lookup per forecast.

**Overall cost.** The full study, including all horizons, folds, quantile models and robustness experiments, ran in roughly six hours of wall-clock time. In operation, a single pooled model per horizon replaces dozens of local models and their maintenance.



::: {custom-style="Table Caption"}
**Table 11.** Computational cost (4-core CPU).
:::

| Model                |   h (h) |   Fits |   Mean fit time (s) |   Inference (µs/forecast) |   Model size (MB) |   Trees |   Peak RSS of run (MB) |
|:---------------------|--------:|-------:|--------------------:|--------------------------:|------------------:|--------:|-----------------------:|
| LGB_G_IN             |       1 |      1 |               298.1 |                    164.2  |             70.74 |    3000 |                   3718 |
| LGB_G_IN             |       6 |      1 |              1261.9 |                     13.53 |              9.48 |     399 |                   3708 |
| LGB_G_IN             |      24 |      1 |                42   |                      5.59 |              4.64 |     192 |                   3723 |
| LGB_G_IN (quantile)  |       1 |      4 |                78.8 |                     30.3  |             14.21 |     596 |                   5161 |
| LGB_G_IN (quantile)  |      24 |      4 |                33.7 |                      4.4  |              3.92 |     162 |                   5208 |
| LGB_G_LRO            |       1 |      6 |               245.6 |                    171.24 |             63.81 |    2708 |                   5173 |
| LGB_G_LRO            |       6 |      6 |                79.7 |                     37.64 |             17.63 |     747 |                   5250 |
| LGB_G_LRO            |      24 |      6 |                39.3 |                      6.81 |              5.54 |     230 |                   5208 |
| LGB_G_LRO (quantile) |       1 |     24 |                64.5 |                     26.97 |             12.15 |     510 |                   5206 |
| LGB_G_LRO (quantile) |      24 |     24 |                33.4 |                      5.27 |              4.35 |     180 |                   5208 |
| LGB_L (48 models)    |       1 |      1 |               595.6 |                    nan    |            809.5  |     nan |                   5161 |
| LGB_L (48 models)    |       6 |      1 |               162.2 |                    nan    |            169.12 |     nan |                   5250 |
| LGB_L (48 models)    |      24 |      1 |                83.6 |                    nan    |             61.45 |     nan |                   5208 |
| RIDGE_G_IN           |       1 |      1 |                23.4 |                      0.99 |            nan    |     nan |                   5161 |
| RIDGE_G_IN           |       6 |      1 |                27.3 |                      2.14 |            nan    |     nan |                   5250 |
| RIDGE_G_IN           |      24 |      1 |                20.6 |                      0.99 |            nan    |     nan |                   5208 |






![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig13_compute.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 13.** Computational cost on a 4-core CPU: (a) wall-clock training time; (b) serialised model size (ridge size not measured). The h = 6 h in-region fit coincided with a concurrent evaluation job and its time is inflated by CPU contention; LRO fits at h = 6 h are representative.
:::




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

1. **Zero-shot transfer works.** A pooled, instance-normalised LightGBM model transfers to unseen BAs with a small but systematic accuracy loss of about 0.5% (24 h) to 3.4% (1 h) relative to in-region training. It is no worse than local models trained on four years of target data.
2. **Short-window adaptation does not help.** Fine-tuning or local training on one to thirteen weeks of target data mostly made forecasts worse.
3. **Interval calibration is the binding problem, and it is temporal and BA-specific rather than geographic.** Static conformal intervals under-covered in a fifth to a half of BAs, whether or not the BA had been seen in training. Online adaptive conformal inference restored per-BA coverage, but only with a step size matched to the feedback delay.
4. **Data gaps matter mainly intraday, and compute is cheap.** Missing inputs degraded hour-ahead forecasts substantially but day-ahead forecasts only modestly, and training with masked inputs largely removed the hour-ahead penalty. Computational cost was a minor concern.

**Future work.** Several extensions follow directly:

- replicate the protocol on European data (OPSD/ENTSO-E) and on other national systems;
- add weather forecasts and evaluate whether the geographic gap and calibration findings persist;
- include time-series foundation models in the same leave-regions-out protocol;
- test parameter-free online calibration (e.g. aggregated ACI) and regularised adaptation schemes;
- extend the analysis to probabilistic forecasts of peaks and ramps.


# Data availability statement {.unnumbered}

This study uses publicly available data only. The EIA Form 930 hourly balancing-authority data, as processed by the Public Utility Data Liberation project (Catalyst Cooperative), release v2026.10.0, are available from the PUDL public data bucket (`s3://pudl.catalyst.coop/stable/`, retrieved 16 October 2026) and the corresponding Zenodo archive (DOI 10.5281/zenodo.22525116). The original EIA data are a U.S. Government work in the public domain; PUDL outputs are licensed CC-BY-4.0. The download script verifies SHA-256 checksums of the exact files used. Derived predictions, metrics and tables are included in the code repository and supplementary archive. [AUTHOR ACTION: insert the permanent repository/DOI link for the code and derived data, e.g. a Zenodo release of the repository.]

# Code availability statement {.unnumbered}

All code needed to reproduce every number, table and figure (data download, preprocessing, model training, evaluation, statistics, figures, tables and manuscript assembly) is available at [AUTHOR ACTION: repository URL / DOI]. A single command (`python -m src.run_all`) reproduces the full study on a 4-core CPU in approximately 3–4 hours; the frozen protocol, configuration and decision log are versioned with the code.

# Funding {.unnumbered}

[AUTHOR ACTION: Funding statement. If none: "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."]

# Declaration of competing interest {.unnumbered}

[AUTHOR ACTION: Declare any competing interests, or state: "The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper."]

# CRediT authorship contribution statement {.unnumbered}

[AUTHOR ACTION: Assign CRediT roles for each author, e.g. **[Author 1]:** Conceptualization, Methodology, Software, Formal analysis, Writing – original draft. **[Author 2]:** Supervision, Writing – review & editing.]

# Declaration of generative AI use {.unnumbered}

[AUTHOR ACTION: Most journals require disclosure of generative-AI assistance. This manuscript, its code and analyses were prepared with substantial assistance from an AI system (Claude, Anthropic); the authors must review, verify and take responsibility for all content and complete the journal's AI-disclosure statement accordingly.]

# Acknowledgements {.unnumbered}

We thank Catalyst Cooperative for the PUDL project and the U.S. Energy Information Administration for publishing Form 930 data. [AUTHOR ACTION: add further acknowledgements or delete.]

# References {.unnumbered}

::: {#refs}
:::

# Appendix A. Balancing authorities {.unnumbered}



::: {custom-style="Table Caption"}
**Table A1.** Balancing authorities included in the study (2019–2025).
:::

| BA   | Name                                     | Interconnect   |   Mean demand (MW) |   Reported coverage (%) |   PUDL-flagged (%) |   LRO fold |
|:-----|:-----------------------------------------|:---------------|-------------------:|------------------------:|-------------------:|-----------:|
| PJM  | pjm interconnection                      | eastern        |              91577 |                   99.73 |               0.3  |          2 |
| MISO | midcontinent iso                         | eastern        |              73658 |                   99.91 |               0.1  |          3 |
| ERCO | electric reliability council of texas    | ercot          |              48661 |                   99.92 |               0.09 |          1 |
| SWPP | southwest power pool                     | eastern        |              31811 |                  100    |               3.7  |          5 |
| SOCO | southern company services                | eastern        |              26887 |                   99.96 |               0.06 |          0 |
| CISO | california iso                           | western        |              25117 |                   99.81 |               0.33 |          4 |
| TVA  | tennessee valley authority               | eastern        |              18446 |                  100    |               0.03 |          1 |
| NYIS | new york iso                             | eastern        |              17277 |                  100    |               0.01 |          2 |
| FPL  | florida power and light                  | eastern        |              15664 |                   98.77 |               1.36 |          4 |
| ISNE | iso new england                          | eastern        |              13193 |                  100    |               0    |          0 |
| DUK  | duke energy carolinas                    | eastern        |              12102 |                   99.92 |               0.08 |          3 |
| CPLE | duke energy progress east                | eastern        |               6982 |                   99.85 |               0.16 |          5 |
| BPAT | bonneville power                         | western        |               6563 |                  100    |               0.03 |          1 |
| FPC  | progress energy florida                  | eastern        |               6418 |                   99.92 |               0.09 |          0 |
| PACE | pacificorp east                          | western        |               5754 |                  100    |               0.19 |          5 |
| PSCO | public service company of colorado       | western        |               5283 |                   99.96 |               0.13 |          4 |
| NEVP | nevada power                             | western        |               4452 |                   99.97 |               0.1  |          3 |
| LGEE | louisville gas and electric and kentucky | eastern        |               4124 |                   99.72 |               0.42 |          2 |
| SRP  | salt river project                       | western        |               3792 |                   99.6  |               0.51 |          4 |
| AZPS | arizona public service                   | western        |               3775 |                   99.96 |               0.14 |          5 |
| WACM | western area power mountain              | western        |               3104 |                  100    |               0.87 |          0 |
| LDWP | los angeles dept of water and power      | western        |               2867 |                   99.73 |               0.48 |          2 |
| SC   | south carolina public service            | eastern        |               2849 |                   99.78 |               0.32 |          3 |
| SCEG | south carolina electric and gas          | eastern        |               2789 |                   99.69 |               0.39 |          1 |
| AECI | associated electric coop                 | eastern        |               2663 |                   99.98 |               0.04 |          4 |
| TEC  | tampa electric                           | eastern        |               2513 |                   99.87 |               0.14 |          5 |
| PGE  | portland general electric                | western        |               2506 |                   99.96 |               0.07 |          3 |
| PACW | pacificorp west                          | western        |               2390 |                  100    |               0.04 |          1 |
| FMPP | florida municipal power pool             | eastern        |               2117 |                   99.76 |               0.5  |          0 |
| IPCO | idaho power                              | western        |               2075 |                  100    |               0.01 |          2 |
| BANC | northern california                      | western        |               1985 |                   99.99 |               2.22 |          0 |
| PNM  | public service company of new mexico     | western        |               1631 |                  100    |               0.11 |          2 |
| TEPC | tuscon electric power                    | western        |               1564 |                   98.43 |               1.61 |          4 |
| JEA  | jacksonville energy                      | eastern        |               1518 |                   99.56 |               0.5  |          5 |
| AVA  | avista                                   | western        |               1462 |                  100    |               0.09 |          3 |
| NWMT | northwestern energy                      | western        |               1362 |                   99.96 |               0.39 |          1 |
| SCL  | seattle city light                       | western        |               1078 |                   99.99 |               0.08 |          4 |
| WALC | western area power southwest             | western        |               1052 |                   99.92 |               0.71 |          5 |
| EPE  | el paso electric                         | western        |               1015 |                   99.99 |               0.1  |          2 |
| GCPD | public utility grant county              | western        |                689 |                  100    |               0.37 |          1 |
| CPLW | duke energy progress west                | eastern        |                564 |                   99.88 |               0.21 |          3 |
| TPWR | city of tacoma                           | western        |                545 |                  100    |               0.15 |          0 |
| IID  | imperial irrigation                      | western        |                436 |                   99.73 |               1.08 |          3 |
| TIDC | turlock irrigation district              | western        |                327 |                   99.8  |               0.72 |          4 |
| TAL  | city of tallahassee                      | eastern        |                320 |                   98.83 |               1.29 |          2 |
| DOPD | public utility of douglas county         | western        |                240 |                   97.69 |               3.07 |          1 |
| GVL  | gainesville regional                     | eastern        |                237 |                   97.89 |               2.66 |          5 |
| CHPD | public utility district of chelan county | western        |                218 |                   99.89 |               0.44 |          0 |



