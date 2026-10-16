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

Forecasting models are increasingly expected to serve power systems they were not trained on. We benchmark this on hourly EIA-930 demand of 48 U.S. balancing authorities (2019–2025), using a leakage-resistant protocol frozen before test evaluation. A pooled LightGBM model applied to unseen balancing authorities lost a median 0.5% (day-ahead) to 3.4% (hour-ahead) accuracy relative to in-region training. When whole regions were held out the loss rose to 1.7% (day-ahead) and 8.0% (hour-ahead), yet zero-shot forecasts still matched local models trained on four years of target data. Fine-tuning on one to thirteen weeks of target data degraded accuracy. Static conformal intervals under-covered by more than five points in 20.8–33.3% of systems, whether seen or unseen. Adaptive conformal inference, with its step size chosen on other systems, restored per-system coverage at little cost in sharpness.

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

**Global versus local models.** Global models fitted jointly across many series can be as expressive as local models without assuming that the series are similar [@montero2021principles]. Pooled gradient boosting was prominent in the M5 competition [@makridakis2022m5], and LightGBM [@ke2017lightgbm] is a common implementation. Global neural forecasters such as DeepAR [@salinas2020deepar] and N-BEATS [@oreshkin2020nbeats] share the same principle, and simulation evidence clarifies when global models help [@hewamalage2022global]. For electricity load, Ahmadi et al. report that global models outperform local ones on Alberta data and include a zero-shot evaluation on regions not used for training [@ahmadi2025globalization]. Ling and Wu compare global, clustered and local probabilistic LightGBM models in a non-energy setting [@ling2025comparative]. Most global-versus-local comparisons, however, evaluate series that were pooled during training. Generalisation to withheld series is seldom isolated, and its effect on uncertainty calibration is rarely reported.

**Transfer and few-shot learning across regions.** Tzortzis et al. pre-train neural networks on European national demand and adapt them to held-out countries [@tzortzis2024transfer]. Yuan et al. propose a meta-learning initialisation that adapts to unseen German transmission-system-operator areas [@yuan2026adaptive]. Hierarchical transfer [@antoniadis2024hierarchical], meta-learning for data-scarce consumers [@tsoumplekas2025fewshot] and cross-building transfer with seasonal adjustment [@ribeiro2018transfer] address related settings. At building level, BuildingsBench established zero-shot and fine-tuning evaluation on unseen buildings [@emami2023buildingsbench]. These works mostly report point accuracy on a few target regions or on building-level data. Whether transfer preserves *calibrated* uncertainty for large, independently operated systems remains largely unexamined.

**Time-series foundation models.** Pre-trained forecasters such as Chronos [@ansari2024chronos], TimesFM [@das2024decoder], Moirai [@woo2024unified], Lag-Llama [@rasul2023lagllama] and TimeGPT [@garza2023timegpt] claim competitive zero-shot accuracy on unseen datasets. For household load, zero-shot foundation models perform comparably to Transformers trained from scratch [@meyer2025benchmarking]. A recent preprint on ERCOT system load reports that interval calibration differs sharply between foundation models [@simeone2026tsfm], and another benchmarks deep sequence models on EIA-930 with per-grid training [@hong2026benchmarking]. Calibration of zero-shot models therefore cannot be assumed, which motivates a model-agnostic recalibration layer of the kind studied here.

**Probabilistic evaluation and conformal prediction under shift.** We evaluate forecasts with proper scoring rules [@gneiting2007strictly], following the principle of maximising sharpness subject to calibration [@gneiting2007probabilistic], and use quantile losses rooted in quantile regression [@koenker1978regression]. Split conformal prediction [@vovk2005algorithmic; @lei2018distribution] gives distribution-free marginal coverage under exchangeability, and conformalised quantile regression adds heteroscedastic adaptivity [@romano2019conformalized]. For dependent and drifting data, several extensions exist:

- adaptive conformal inference (ACI) guarantees long-run coverage by updating the target miscoverage online [@gibbs2021adaptive];
- aggregated ACI removes the step-size choice and was demonstrated on electricity prices [@zaffran2022adaptive];
- weighted conformal methods bound the loss of coverage under non-exchangeability [@barber2023conformal];
- EnbPI [@xu2021conformal] and SPCI [@xu2023sequential] exploit residual structure;
- conformal PID control [@angelopoulos2023conformal] and online-optimisation approaches [@areces2025online] include electricity-demand experiments.

Conformalised quantile regression has also been applied to transmission-level load [@matulin2023cqr]. Weighted conformal prediction handles known covariate shift [@tibshirani2019conformal], and strongly adaptive online methods refine ACI [@bhatnagar2023improved]. The closest design precedent we found is at building level: a 2026 article in *Applied Sciences* (doi:10.3390/app16167984) holds out whole buildings, combines a LightGBM correction with persistence, and reports loss of conformal coverage on unseen buildings and under sensor missingness. [AUTHOR ACTION: we could not verify this article's author list from a publisher page; complete the reference before submission.] Our study transfers the question to system-level balancing-authority demand and adds operator benchmarks and spatially blocked folds. Electricity applications of online conformal methods have so far mostly concerned single series under temporal drift. Coverage under *geographic* shift, where a model is calibrated on some regions and deployed on a region it has never seen, is less studied for system-level load.

**Data quality and evaluation methodology.** EIA-930 provides hourly demand and day-ahead forecasts for U.S. balancing authorities [@eia930about]. Ruggles et al. documented its missing and anomalous values and developed the screening and imputation reimplemented in PUDL [@ruggles2020developing; @pudl2026]. The comparable European resources, OPSD [@wiese2019opsd] and the ENTSO-E Transparency Platform [@hirth2018entsoe], have documented quality limitations. Robust optimisation has been proposed as an alternative to imputation for missing inputs [@stratigakos2024resilient].

Our evaluation design follows established practice. We use rolling-origin and blocked validation for dependent data [@tashman2000out; @bergmeir2012use; @bergmeir2018note], group-blocked validation analogous to spatial cross-validation [@roberts2017cross], and scale-free accuracy (MASE) [@hyndman2006another]. We test differences with block-bootstrap intervals [@kunsch1989jackknife; @politis1994stationary], in the spirit of Diebold–Mariano comparisons [@diebold1995comparing], and we avoid known pitfalls in forecast evaluation [@hewamalage2023forecast; @lago2021forecasting].

**Positioning.** Every ingredient of this study has precedent: cross-region transfer, global gradient boosting, adaptive conformal prediction and operator-forecast data. To our knowledge, based on a non-exhaustive search, they have not been combined in a single frozen-protocol evaluation across tens of independently operated U.S. balancing authorities. Such an evaluation separates geographic from temporal shift, quantifies the value of a few weeks of target data, assesses interval coverage under both shifts, and benchmarks against the operators' own forecasts. Our contribution is this evaluation framework and benchmark, not a new forecasting or conformal algorithm.


# Research gap and contributions

The literature review (Section 2 and the supplementary literature matrix) shows that each ingredient of the problem has been studied in isolation:

- transfer to held-out regions, mostly for point forecasts on a few European countries or German control areas [@tzortzis2024transfer; @yuan2026adaptive];
- global versus local models, mostly on series seen in training [@montero2021principles; @ahmadi2025globalization];
- adaptive conformal prediction on single electricity series under temporal drift [@gibbs2021adaptive; @zaffran2022adaptive; @angelopoulos2023conformal];
- EIA-930 benchmarks trained per grid [@hong2026benchmarking].

We found no study that measures, on a common protocol, (i) the accuracy cost of never having seen a system, (ii) the value of a few weeks of target data, and (iii) whether interval coverage survives geographic and temporal shift, across tens of independently operated systems with operator forecasts as a reference. The search was not exhaustive (see Section 14).

The study makes four contributions.

1. *A leakage-resistant benchmark for cross-region load forecasting with a protocol frozen before test evaluation.* It covers 48 U.S. BAs from EIA Form 930 (2019–2025), spanning three orders of magnitude in size. Its components are: leave-regions-out folds in which held-out BAs are excluded from fitting, early stopping and calibration; past-only input screening independent of the label imputation; a protocol and configuration frozen in version control before test evaluation; and a log of every subsequent amendment.
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
where $\mathrm{err}_{t-h}$ indicates whether the interval issued for hour $t-h$ missed. Feedback is therefore delayed by the horizon. Scores enter the calibration pool once their outcomes are observed. When $\alpha_t$ leaves $(0,1)$ the exact ACI interval is unbounded or empty; we cap it at the most extreme score observed so far and report the share of capped hours. Two implementation details: the online stream runs over scored (unflagged) hours only, so the delay of $h$ steps corresponds to at least $h$ hours, a conservative choice; and at nominal 50% coverage the threshold never needed capping. ACI-CQR uses the step size fixed in the frozen protocol, $\gamma = 0.005$. **ACI-CQR-V** uses $\gamma$ selected from $\{0.001, 0.002, 0.005, 0.01\}$ by interval score on the 2023 data of held-out BAs; this variant was added after the freeze (Section 15).

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

**Post-review analyses.** The following analyses were added after an internal review, after the test results had been seen, and are reported as such (DECISION_LOG D14–D16):

- spatially blocked folds: nine blocks of contiguous EIA regions, at $h = 24$ h (point and quantile models) and $h = 1$ h (point);
- ACI with $\gamma$ selected per fold on the *source* BAs' calibration weeks only (ACI-CQR-S), with a $\gamma = 0$ expanding-pool control;
- split conformal calibrated on each BA's most recent four weeks of observed residuals (SCP-R4);
- conditional coverage by season and load decile, and peak-hour diagnostics;
- adaptation at three further onboarding origins (1 April, 1 July and 1 October 2024; $k \in \{4, 13\}$ weeks; $h \in \{6, 24\}$ h);
- zero-shot forecasts for the five excluded BAs;
- a ridge penalty grid;
- a cluster bootstrap over the nine spatial blocks and non-inferiority bounds with post-hoc margins of 1% and 2%.

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

**Statistical comparisons.** Paired comparisons across BAs use the Wilcoxon signed-rank test on per-BA nMAE. Holm adjustment is applied within families: the 72 point-forecast tests (8 pairs, 3 metrics, 3 horizons), the adaptation tests, the refit tests and the ablation tests. Effect sizes are median relative changes, with 95% percentile bootstrap intervals over BAs (1,000 resamples). Within each BA, temporal dependence is handled by a moving-block bootstrap [@kunsch1989jackknife] of the hourly absolute-error differential (168-h blocks, 1,000 resamples); we report the share of BAs whose 95% interval excludes zero. BAs are spatially correlated, so region-level tests overstate the effective sample size [@roberts2017cross]. We therefore emphasise effect sizes.


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

**Distribution across BAs.** The median hides a tail (Fig. 6).

- At $h = 1$ h the gap exceeds 5% in 31.2% of BAs. The 90th percentile is 8.3% and the maximum 44.6% (GCPD). MISO, the second-largest BA, also shows a gap of 18.5% at this horizon.
- At $h = 6$ h the maximum is 29.3% (GCPD).
- At $h = 24$ h the 90th percentile is 1.8% and the maximum 6.6% (GCPD).

The gap is weakly related to BA size (correlation with log mean demand -0.25 at 24 h). Per-BA errors of the zero-shot model range from 2.47% (GCPD) to 8.55% (AECI) at 24 h, a spread much larger than the median gap.

**Robustness to spatial correlation.** Resampling the nine spatial blocks of Section 11.3 instead of individual BAs gives 95% intervals for the median gap of 0.3 to 0.8% at 24 h and 2.5 to 4.6% at 1 h.

**Global versus local.** Pooling helps more than locality does. The median per-BA relative change in nMAE from local models to G-IN is -1.4% at 24 h (CI -2.2 to -0.8%) and -9.2% at 1 h (negative values favour the global model). The *zero-shot* G-LRO model, which has never seen the target BA, compares with local models trained on four years of that BA's data as follows.

- **At $h = 1$ h and $h = 6$ h it is more accurate:** median relative change -5.4% (CI -8.1 to -3.7%) and -3.1%.
- **At $h = 24$ h the difference is small and not significant:** -0.8% (CI -1.6 to 0.2%; Holm-adjusted $p$ = 0.21). With a 1% non-inferiority margin, chosen post hoc, the 90% cluster-bootstrap interval (-2.1 to 0.3%) supports non-inferiority but not equivalence.
- **By year at 24 h,** the paired difference is 0.0% in 2024 and -1.4% in 2025. In 2024 the local models have a marginally lower *median level* across BAs (Table 5), so the zero-shot model matches rather than beats local models at the day-ahead horizon.

**Linear benchmark.** Relative to ridge regression on the same features, G-IN changes nMAE by a median -5.5% at 24 h and -19.3% at 1 h. Ridge regression's own geographic gap is negligible (0.1% at 24 h), consistent with a low-capacity model that cannot memorise BA-specific patterns.



::: {custom-style="Table Caption"}
**Table 2.** Key paired comparisons of per-BA nMAE (test period; negative = A more accurate).
:::

|   h (h) | A vs B                     |   Median rel. change % | 95% CI         |   A better (BAs %) | A sig. better / B sig. better (block bootstrap, BAs %)   | Holm p   |
|--------:|:---------------------------|-----------------------:|:---------------|-------------------:|:---------------------------------------------------------|:---------|
|       1 | G-LRO (zero-shot) vs G-IN  |                    3.4 | [2.5, 4.6]     |                  0 | 0 / 98                                                   | <1e-4    |
|       1 | G-IN vs Local              |                   -9.2 | [-11.7, -7.3]  |                 92 | 83 / 4                                                   | <1e-4    |
|       1 | G-LRO (zero-shot) vs Local |                   -5.4 | [-8.1, -3.7]   |                 77 | 75 / 12                                                  | 0.0005   |
|       1 | G-LRO (zero-shot) vs SN24  |                  -79.6 | [-81.7, -77.5] |                100 | 100 / 0                                                  | <1e-4    |
|       6 | G-LRO (zero-shot) vs G-IN  |                    1.9 | [1.6, 2.3]     |                  0 | 0 / 90                                                   | <1e-4    |
|       6 | G-IN vs Local              |                   -5.7 | [-7.1, -4.0]   |                 88 | 79 / 4                                                   | <1e-4    |
|       6 | G-LRO (zero-shot) vs Local |                   -3.1 | [-5.6, -1.8]   |                 71 | 54 / 15                                                  | 0.007    |
|       6 | G-LRO (zero-shot) vs SN24  |                  -35.3 | [-37.2, -32.6] |                 98 | 98 / 2                                                   | <1e-4    |
|      24 | G-LRO (zero-shot) vs G-IN  |                    0.5 | [0.4, 0.7]     |                  6 | 0 / 52                                                   | <1e-4    |
|      24 | G-IN vs Local              |                   -1.4 | [-2.2, -0.8]   |                 71 | 35 / 6                                                   | 0.003    |
|      24 | G-LRO (zero-shot) vs Local |                   -0.8 | [-1.6, 0.2]    |                 62 | 31 / 17                                                  | 0.2      |
|      24 | G-LRO (zero-shot) vs SN24  |                  -12   | [-15.2, -10.5] |                100 | 94 / 0                                                   | <1e-4    |






![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig06_regional_errors.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 6.** (a) Per-BA nMAE of the global model when the BA is held out vs included in training (colour: log10 mean demand). (b) Relative geographic generalisation gap vs BA size.
:::



**Operator reference.** The BAs' own day-ahead forecasts reach a median nMAE of 3.57% on the same hours, against 4.64% for G-IN at 24 h (Table 3). The information sets differ: operators use weather forecasts and other operational information, issue forecasts at undocumented times, and are not restricted to our past-demand features. We therefore do not attribute the difference to any single cause, and the comparison is not like-for-like. For orientation only, the in-region model at $h = 6$ h (3.50%), which has far more recent information than any day-ahead forecast, is more accurate than the operators' day-ahead forecasts.



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

**Fine-tuning gives little and usually hurts.** Fine-tuning the global model on the same data yields 5.37%, 5.26% and 5.00% for one, four and thirteen weeks. The median relative change versus zero-shot is 12.9% with four weeks (CI 9.7 to 17.9%) and 6.5% with thirteen. The exception is $h = 1$ h with thirteen weeks, where fine-tuning helps slightly (-1.5%, CI -2.5 to -0.7%).

**The degradation is not specific to a December origin.** We repeated the experiment at three onboarding origins inside the test period: 1 April, 1 July and 1 October 2024, each evaluated over the following year. Fine-tuning remained worse than zero-shot at every origin. Median relative changes ranged from +5.4% to +14.3% at 24 h, and from +1.2% to +6.0% at 6 h (Supplementary Table S5). These adaptation settings were fixed a priori; better-regularised adaptation might behave differently.



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






![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig07_transfer.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 7.** Limited target-data adaptation for unseen BAs: median test nMAE vs weeks of target (x-axis on a symmetric-log scale) history.
:::



## Temporal distribution shift (RQ4)

**Drift with model age.** Errors of models frozen at the end of 2022 did not grow monotonically with their age (Table 5; Fig. 8). At $h = 24$ h the median nMAE of G-IN was 4.60% in 2023 (validation year, mildly optimistic because it includes the early-stopping weeks), 4.54% in 2024 and 4.67% in 2025. The seasonal naive benchmark follows the same pattern (5.16% in 2024 and 5.56% in 2025), which indicates that 2025 was intrinsically harder to forecast rather than that the models aged. The increase from 2024 to 2025 was largest for local models (4.49% to 4.80%), compared with the zero-shot model (4.56% to 4.72%) and G-IN.

**Seasonal pattern.** Errors are highest in winter and summer and lowest in autumn: at 24 h, G-IN reaches 4.76% in DJF, 4.76% in JJA and 4.34% in SON. This pattern reflects weather-driven heating and cooling load that calendar and lag features cannot anticipate.

**Effect of refitting.** Refitting on data through 2023 and evaluating on 2025 (Table 6) leaves the median nMAE of G-IN essentially unchanged (4.67% frozen, 4.67% refit), and of local models from 4.80% to 4.78%. The median per-BA relative change is 0.1% for G-IN (Holm $p$ = 0.87) and -0.9% for local models (Holm $p$ < 0.0001). Refitting thus benefits local models, which gain a fifth year of their own data, but not the pooled model, which already has abundant data.



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






![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig08_temporal_shift.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 8.** Temporal distribution shift: (a) median nMAE by year for models trained on 2019–2022; (b) by season (test period); (c) frozen vs refit models on 2025.
:::



## Interval calibration under geographic and temporal shift (RQ3)

Table 7 and Fig. 9 report interval calibration.

**Calibration fails BA by BA, not on average.** The static methods are close to nominal *on average* but not *per BA*. At $h = 24$ h and nominal 90%, CQR calibrated on source BAs achieves a mean coverage of 89.2% for unseen BAs, yet coverage ranges down to 78.6%. In 20.8% of BAs it is more than 5 percentage points below nominal. Raw quantile regression under-covers more (mean 87.3%), and symmetric SCP has the widest spread across BAs (minimum 71.4%).

**Geographic shift matters little for calibration.** Unseen-region intervals behave almost identically to in-region ones: in-region CQR reaches a mean of 89.2% and under-covers in 18.8% of BAs. The binding problem is *heterogeneity across BAs and over time*, not the absence of the BA from training.

**Target calibration from recent weeks fails.** Calibrating on the target BA's own last four weeks (SCP-T4) *reduces* mean coverage to 85.3%. Four December weeks are not exchangeable with the following two years.

**Temporal drift lowers coverage.** Static coverage declines from 2024 to 2025: CQR falls from 89.5% to 88.8% (Fig. 9c).

**Online recalibration: what ACI does and does not show.** ACI is guaranteed by construction to reach the nominal long-run coverage for each stream, so per-BA coverage close to 90% is expected rather than an empirical finding. The empirical questions are how sharp the resulting intervals are, how they behave conditionally, and how the step size should be chosen without test data.

**The frozen-protocol step size is too large.** With the frozen-protocol step size $\gamma = 0.005$ and 24-h feedback delay, the threshold had to be capped at the largest score seen in a mean of 4.4% of hours. The median interval score rose to 88.55% of mean load, against 28.15% for CQR.

**Step size chosen on source BAs only (ACI-CQR-S).** After the internal review we selected $\gamma$ separately for each fold from $\{0, 0.0005, 0.001, 0.002, 0.005, 0.01\}$, using only the source BAs' calibration weeks. The selected values were 0.0005 at 24 h and 0.002, 0.005 at 1 h (Table 8).

- *Coverage.* ACI-CQR-S keeps mean coverage at 89.9% with a minimum of 88.9% across BAs at 24 h.
- *Sharpness.* Its median interval score (28.18%) is close to that of static CQR (28.15%), and its median hourly width is 17.81% of mean load.
- *Hour-ahead.* At 1 h, ACI-CQR-S reaches a minimum coverage of 89.8% and a median interval score of 7.40%, against 7.21% for CQR.

**The adaptive update is what helps.** A $\gamma = 0$ control, which keeps adding observed target scores to the calibration pool without adapting $\alpha_t$, under-covers like static CQR: minimum 79.3%, with 20.8% of BAs more than 5 points below nominal. The benefit therefore comes from the adaptive update, not from pooling target scores. The variant whose $\gamma$ was chosen on the held-out BAs' own 2023 data (ACI-CQR-V; exploratory, see Section 15) gives similar results.

**Rolling target calibration.** A simple rolling alternative is split conformal prediction on each BA's most recent four weeks of observed residuals (SCP-R4).

- *Day-ahead.* It is also well calibrated per BA (mean 89.2%, minimum 88.4%), but less sharp: median interval score 31.65% against 28.18% for ACI-CQR-S.
- *Hour-ahead.* It is competitive (minimum coverage 89.5%; median interval score 7.31% against 7.40%).

What matters is therefore online use of recent target feedback; the particular online scheme is secondary.

**Spatially blocked folds.** Under spatial blocking (Section 11.3), static CQR covers 89.5% on average (minimum 78.9%) and ACI-CQR-S 89.9% (minimum 88.9%). The calibration conclusions are thus unchanged when whole regions are new.

**Conditional coverage.** Marginal coverage hides conditional deviations (Supplementary Table S8).

- *Season.* For ACI-CQR-S at 24 h, mean coverage across BAs is 88.3% in winter and 90.0% in summer.
- *Load level.* In the top load decile of each BA it is 87.9%, against 87.0% for CQR.
- *Daily peaks.* At the daily peak hour, the observed load exceeds the upper 90% bound on 11.8% of days for CQR and 11.2% for ACI-CQR-S. A calibrated central 90% interval would be exceeded from above on 5% of hours, so peak-hour upper-tail risk is under-stated by roughly a factor of two. This matters for reserve sizing.

**Peak-hour point accuracy.** The daily-peak absolute percentage error of the zero-shot point forecast has a median across BAs of 4.76%, against 3.69% for the operators' day-ahead forecasts.

**Post-hoc sensitivity.** Supplementary Table S2 gives the test-set sensitivity of ACI to $\gamma$. It was not used for any selection.



::: {custom-style="Table Caption"}
**Table 7.** Calibration of nominal 90% intervals for unseen BAs (random folds, test period). Widths and interval scores (IS) are in % of mean load.
:::

|   h (h) | Method                                                |   Mean cov. % | Min–max cov. %   |   BAs > 5 pp under % |   Median hourly width % |   Median IS % |
|--------:|:------------------------------------------------------|--------------:|:-----------------|---------------------:|------------------------:|--------------:|
|       1 | QR                                                    |          83.9 | 64.8–97.5        |                   52 |                    4.2  |          7.4  |
|       1 | SCP                                                   |          87.5 | 52.6–98.9        |                   31 |                    4.78 |          7.72 |
|       1 | CQR                                                   |          88.1 | 69.2–98.7        |                   33 |                    4.74 |          7.21 |
|       1 | SCP-T4                                                |          86.9 | 74.3–96.5        |                   29 |                    4.3  |          7.81 |
|       1 | ACI-CQR (γ = 0.005, frozen protocol)                  |          90   | 89.9–90.2        |                    0 |                    4.9  |          7.4  |
|       1 | ACI-CQR-V (γ on held-out BAs' 2023 data; exploratory) |          90   | 89.7–90.4        |                    0 |                    4.9  |          7.13 |
|      24 | QR                                                    |          87.3 | 76.1–96.1        |                   29 |                   17.15 |         28.26 |
|      24 | SCP                                                   |          88.9 | 71.4–99.3        |                   29 |                   20.14 |         31.88 |
|      24 | CQR                                                   |          89.2 | 78.6–97.3        |                   21 |                   18.14 |         28.15 |
|      24 | SCP-T4                                                |          85.3 | 60.8–95.9        |                   40 |                   14.97 |         34.15 |
|      24 | ACI-CQR (γ = 0.005, frozen protocol)                  |          90   | 89.8–90.2        |                    0 |                   18.6  |         88.55 |
|      24 | ACI-CQR-V (γ on held-out BAs' 2023 data; exploratory) |          89.9 | 89.4–90.5        |                    0 |                   17.81 |         28.24 |






::: {custom-style="Table Caption"}
**Table 8.** Online and source-only calibration of 90% intervals for unseen BAs, including spatially blocked folds (post-review analyses; γ selected on source BAs only for ACI-CQR-S).
:::

| Setting                 |   h (h) | Method                                     |   Mean cov. % | Min–max cov. %   |   BAs > 5 pp under % |   Median hourly width % |   Median IS % |
|:------------------------|--------:|:-------------------------------------------|--------------:|:-----------------|---------------------:|------------------------:|--------------:|
| unseen (random folds)   |       1 | ACI-CQR (gamma=0, expanding pool)          |          88.3 | 70.2–98.6        |                   31 |                    4.75 |          7.21 |
| unseen (random folds)   |       1 | ACI-CQR (gamma=0.005, pre-registered)      |          90   | 89.9–90.2        |                    0 |                    4.9  |          7.4  |
| unseen (random folds)   |       1 | ACI-CQR-S (gamma source-selected)          |          90   | 89.8–90.2        |                    0 |                    4.9  |          7.4  |
| unseen (random folds)   |       1 | CQR                                        |          88.1 | 69.2–98.7        |                   33 |                    4.74 |          7.21 |
| unseen (random folds)   |       1 | SCP-R4 (rolling 4-week target calibration) |          89.9 | 89.5–90.1        |                    0 |                    4.76 |          7.31 |
| unseen (random folds)   |      24 | ACI-CQR (gamma=0, expanding pool)          |          89.2 | 79.3–97.1        |                   21 |                   18.07 |         28.15 |
| unseen (random folds)   |      24 | ACI-CQR (gamma=0.005, pre-registered)      |          90   | 89.8–90.2        |                    0 |                   18.6  |         88.55 |
| unseen (random folds)   |      24 | ACI-CQR-S (gamma source-selected)          |          89.9 | 88.9–90.8        |                    0 |                   17.81 |         28.18 |
| unseen (random folds)   |      24 | CQR                                        |          89.2 | 78.6–97.3        |                   21 |                   18.14 |         28.15 |
| unseen (random folds)   |      24 | SCP-R4 (rolling 4-week target calibration) |          89.2 | 88.4–90.0        |                    0 |                   19.39 |         31.65 |
| unseen (spatial blocks) |      24 | ACI-CQR (gamma=0, expanding pool)          |          89.6 | 79.5–97.8        |                   19 |                   19.39 |         28.5  |
| unseen (spatial blocks) |      24 | ACI-CQR (gamma=0.005, pre-registered)      |          90   | 89.8–90.1        |                    0 |                   19.04 |         88.27 |
| unseen (spatial blocks) |      24 | ACI-CQR-S (gamma source-selected)          |          89.9 | 88.9–91.0        |                    0 |                   18.51 |         28.51 |
| unseen (spatial blocks) |      24 | CQR                                        |          89.5 | 78.9–98.0        |                   19 |                   19.39 |         28.5  |
| unseen (spatial blocks) |      24 | SCP-R4 (rolling 4-week target calibration) |          89.3 | 88.4–90.0        |                    0 |                   19.63 |         31.9  |







![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig09_calibration.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 9.** Calibration of nominal 90% intervals (h = 24 h): per-BA coverage (dots; bar = mean) for (a) in-region and (b) unseen-region models; (c) monthly pooled coverage for unseen BAs.
:::





![](/home/user/cross-regional-electricity-forecasting/cross_regional_electricity_forecasting/figures/fig10_interval_example.png){width=16cm}

::: {custom-style="Figure Caption"}
**Fig. 10.** Day-ahead 90% prediction intervals for an unseen BA (IID), test period (BA chosen as the one with median CQR coverage).
:::




# Discussion

**Why does zero-shot transfer work as well as it does?** Three design choices make an unseen BA look "in distribution" to a global model.

- *Instance scaling* by the trailing weekly mean removes level differences of three orders of magnitude, and with them most of the between-BA variation in absolute terms.
- *Shared shapes.* Once normalised, the daily and weekly profiles of U.S. BAs share a small number of shapes driven by human activity and climate. Forty source BAs from all three interconnections cover these shapes well. Accuracy declines steadily as the source pool shrinks: to a median nMAE of 4.81% with 20 sources and 4.97% with five, against 4.75% with 40 (Section 11.2).
- *Lag-dominated information.* At short horizons the most recent observations carry most of the information. This explains why the geographic gap, although statistically clear, is small in absolute terms at the median: about 0.1 percentage point of nMAE at 24 h with random folds, rising to about 1.7% (relative) when whole regions are held out. It also explains why the gap is largest in relative terms at 1 h, where errors are smallest and BA-specific intraday dynamics matter most. The largest relative gaps occur in a few BAs: Grant County PUD (GCPD) at every horizon, and MISO at 1 h. We did not investigate the causes, which may include atypical customer mixes or reporting practices.

With random folds, zero-shot models are more accurate than local models at intraday horizons and non-inferior day-ahead. When whole regions are held out, they are on a par with local models at both horizons. This is consistent with the global-model literature [@montero2021principles; @hewamalage2022global]. For system-level load with the information set studied here, the practical corollary is that *data pooling is worth at least as much as target-specific history*. The exceptions, a few BAs with large intraday gaps, are discussed under practical implications.

**Why does fine-tuning on a few weeks hurt?** Continued boosting on one to thirteen weeks fits the idiosyncrasies of a short window. Whatever the onboarding date, such a window is seasonally unrepresentative of the following year: the degradation appeared at all four dates we tested (late December, April, July and October). Local models trained on the same window are far worse still. Without a validation scheme for choosing how much to adapt, which the short window cannot provide, the safest policy for a newly onboarded system is to use the pooled model unchanged. Adaptation should be revisited once at least a full seasonal cycle is available. Shrinkage-based or regularised adaptation, and adaptation of the *calibration layer* rather than of the point model, are natural alternatives. The latter is what ACI effectively does.

**Calibration is a per-system and per-period property.** Average coverage over 48 BAs hides large BA-level deviations. A single pooled calibration set cannot be exchangeable with every BA. This holds for unseen and in-region BAs alike, and with spatially blocked folds; the heterogeneity among BAs and over time therefore matters more than whether the BA was seen in training. Short target-specific calibration windows fail for the same reason that short adaptation windows do: they are seasonally unrepresentative.

Online recalibration with ACI fixes per-BA marginal coverage by construction, so its value lies in the price paid in sharpness. With delayed feedback (24 h), a step that is too large lets $\alpha_t$ overshoot before earlier updates take effect, producing occasional extreme intervals. Choosing $\gamma$ on *other* BAs' validation data avoided this. It gave intervals as sharp as static CQR at 24 h and a few per cent less sharp at 1 h. Conditional coverage remains imperfect at seasonal peaks and in the highest load decile, which matters most for reserves. Aggregated or strongly adaptive variants [@zaffran2022adaptive; @bhatnagar2023improved] and conditional methods are natural next steps.

**Trade-offs (RQ5).** The table below summarises the trade-offs across the regimes studied.

| Regime | Accuracy (median, relative) | Interval reliability | Target data needed | Compute and maintenance |
|---|---|---|---|---|
| Local LightGBM (per BA) | Baseline | Needs per-BA recalibration | Years | One model per BA |
| Global, in-region | Best at all horizons | Static CQR under-covers (>5 pp) in 18.8% (24 h) to 25.0% (1 h) of BAs | Shared pool including target | One model per horizon |
| Global, zero-shot (random folds) | +0.5% (24 h) to +3.4% (1 h) vs in-region; maximum +44.6% at 1 h | Same as in-region | One week (for scale) | Same; no retraining to add a BA |
| Global, zero-shot (spatial blocks) | +1.7% (24 h) to +8.0% (1 h) vs in-region; on a par with local | Same pattern | One week | Same |
| Fine-tuned on 1–13 weeks | Worse than zero-shot | Not studied | Weeks | Small per-BA cost |
| + ACI (source-selected γ) | Unchanged (point) | Near-nominal per-BA marginal coverage; sharpness equal to CQR at 24 h, slightly lower at 1 h | Online feedback | Negligible |

**Relation to operator forecasts.** The BAs' own day-ahead forecasts are more accurate than our 24-h models, which use only past demand and calendar information. This does not contradict the main findings. The purpose of the benchmark is to isolate the effects of geographic and temporal shift under a fixed, reproducible information set, not to replace operational weather-driven forecasting. The results suggest a practical complement: a pooled, weather-free model calibrated online can serve as a fallback or sanity check for any BA from day one, including BAs without forecasting staff.


# Robustness and ablation analysis

## Missing input observations (RQ4)

Table 9 and Fig. 11 report accuracy when test-period inputs are corrupted while labels are left intact.

**Day-ahead forecasts degrade modestly.** At $h = 24$ h, with 10% of input hours missing completely at random (MCAR), the median nMAE of G-IN rises from 4.64% to 5.05% with LightGBM's native missing-value handling. It rises to 6.93% when 40% of inputs are missing.

**Hour-ahead forecasts are far more sensitive,** because they rely on the most recent observation. With native handling, 10% MCAR raises the median nMAE from 1.14% to 1.84%, and 40% MCAR to 4.04%.

**The best imputation strategy depends on the gap pattern.**

- For scattered MCAR gaps, causal last-observation-carried-forward imputation is better than native handling (1.68% at 10% MCAR, $h = 1$ h).
- For contiguous outages it is worse: with 168-h blocks at $h = 1$ h it reaches 2.42%, against 1.95% (native) and 1.87% (weekly-seasonal imputation).

**Training with masked inputs is the most effective remedy.** A model trained with 10% MCAR input masking reaches 1.32% at 10% MCAR and 2.29% at 40% MCAR ($h = 1$ h). On clean inputs it costs 1.17% versus 1.14%. That is a relative penalty of a few per cent, similar in size to the 1-h geographic gap, which is the price of robustness. Augmentation was tested for the in-region model only.

**Unseen BAs behave the same way.** The zero-shot model degrades in the same way as the in-region model (e.g., 1.93% at 10% MCAR, $h = 1$ h), so missing data does not interact with geographic shift.

**Unscored hours.** In the most severe scenarios the instance scale cannot be computed for some origins, because fewer than 24 of the preceding 168 hours are observed, and no forecast is issued. All strategies within a scenario are scored on the common set of hours where every strategy issued a forecast; in the worst BA and scenario 96.9% of hours remain. Real EIA-930 gaps are clustered rather than uniformly random, so the MCAR and uniform-outage scenarios are stylised.



::: {custom-style="Table Caption"}
**Table 9.** Median nMAE (%) of the in-region global model with corrupted inputs (test period; common scored hours).
:::

|   h (h) | Scenario   |   Native NaN | LOCF   | Weekly-seasonal   |   MCAR-trained, native |
|--------:|:-----------|-------------:|:-------|:------------------|-----------------------:|
|       1 | clean      |         1.14 | –      | –                 |                   1.17 |
|       1 | MCAR_10    |         1.84 | 1.68   | 2.19              |                   1.32 |
|       1 | MCAR_40    |         4.04 | 3.68   | 5.14              |                   2.29 |
|       1 | BLOCK_24h  |         1.89 | 2.52   | 1.91              |                   1.71 |
|       1 | BLOCK_168h |         1.95 | 2.42   | 1.87              |                   1.94 |
|      24 | clean      |         4.64 | –      | –                 |                   4.65 |
|      24 | MCAR_10    |         5.05 | 4.81   | 5.06              |                   4.72 |
|      24 | MCAR_40    |         6.93 | 5.98   | 6.66              |                   5.4  |
|      24 | BLOCK_24h  |         5.02 | 5.81   | 5.13              |                   4.94 |
|      24 | BLOCK_168h |         5.07 | 5.79   | 5.07              |                   5.03 |






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



## Spatially blocked evaluation (post-review)

The random, size-stratified folds of the main analysis keep neighbouring and same-utility BAs of a held-out BA in the training set, so they measure transfer within a covered geography. They may therefore understate the cost of a geographically new region.

**Design.** We repeated the zero-shot experiment with nine spatial blocks: the EIA regions NW, CAL, SW, FLA and CAR, and four merged groups of adjacent single-BA regions (TEX+CENT, MIDW+MIDA, SE+TEN, NE+NY). Every BA in a held-out block is excluded from fitting, early stopping and calibration (Supplementary Table S6).

**Day-ahead results.** At $h = 24$ h the spatially blocked model (G-LRS) attains a median nMAE of 4.81%, against 4.75% for random folds and 4.64% in-region.

- The median relative gap to the in-region model roughly triples, to 1.7% (CI 1.3 to 2.4%).
- The 90th percentile of the gap is 4.7% and the maximum 8.8% (GCPD).
- The spatially blocked model remains statistically indistinguishable from local models trained on four years of target data (0.9%, CI -1.0 to 1.6%).

**Hour-ahead results.** At $h = 1$ h the cost of spatial novelty is much larger.

- The spatially blocked gap is 8.0% (CI 6.5 to 10.8%), against 3.4% with random folds.
- The gap exceeds 10% in 41.7% of BAs, with a maximum of 46.3% (GCPD).
- The intraday advantage of zero-shot over local models disappears: -0.8%, CI -3.1 to 1.8%.

Neighbouring BAs in the training pool thus explain much of the intraday transfer seen with random folds.

The geographic cost is therefore larger when whole regions are new, especially intraday, although even then the zero-shot model was not worse than local models trained on four years of the target BA's data. Calibration under spatial blocking is reported in Table 8.

## Small and lower-quality BAs (post-review)

The selection criteria excluded five BAs that report demand through 2025: HST, SPA and WAUW (below 200 MW), and PSEI and SEC (data-quality criteria). Applying the in-region model, which never saw these BAs, gives day-ahead median nMAEs of:

- 7.02% for HST;
- 6.40% for WAUW;
- 10.29% for SEC;
- 4.01% for PSEI;
- 25.30% for SPA, a 22 MW federal power-marketing area.

These are comparable to local models trained on the same BAs' own history (Supplementary Table S7) but far above the errors of the study BAs. The headline accuracy figures should therefore not be extrapolated to very small systems.

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

1. **Onboarding a new or data-poor BA.** A pooled, instance-normalised gradient-boosting model trained on other BAs can produce usable forecasts from the first day; it needs only a week of recent observations to compute the scale. In our data its median accuracy was within 0.5% (day-ahead) to 3.4% (hour-ahead), in relative terms, of a model that had seen the BA. Tail risk is material for intraday use, however: at 1 h the gap exceeded 10% for 6.2% of BAs, including one very large BA. A zero-shot model should therefore be monitored against the BA's own data, and replaced or pooled with that data, during the first months. Fine-tuning on a few weeks of data degraded accuracy at every onboarding date we tested and is not recommended with the settings studied here.
2. **Small BAs.** Small BAs benefit from pooling as much as large ones. Because the gap was only weakly related to size, a single shared model with BA-specific online calibration is a viable service model for many small utilities.
3. **Uncertainty for reserves and risk.** Intervals calibrated once on pooled data under-covered in a substantial share of BAs and drifted over time, so operational use should include online recalibration. ACI on top of CQR is guaranteed to reach the nominal long-run coverage. What matters in practice is its sharpness and its behaviour in the first months on a new system, and both depend on the step size. A step size chosen on *other* BAs' validation data (ACI-CQR-S) gave a median interval score of 28.18% against 28.15% for static CQR at 24 h; Table 8 gives the details. With day-ahead feedback delay, large step sizes should be avoided. A rolling four-week recalibration on the BA's own recent residuals is a simpler alternative that worked comparably for hour-ahead intervals but was less sharp day-ahead.
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

1. **Zero-shot transfer works, with a tail.** A pooled, instance-normalised LightGBM model transfers to unseen BAs with a small but systematic median accuracy loss: 0.5% (24 h) to 3.4% (1 h) with random folds, and 1.7% (24 h) to 8.0% (1 h) when whole regions are held out. With random folds it is non-inferior to local models trained on four years of target data day-ahead and better intraday; with whole regions held out it matches local models at both horizons. Some BAs show large intraday gaps.
2. **Short-window adaptation does not help.** With the settings studied, fine-tuning or local training on one to thirteen weeks of target data degraded forecasts at every onboarding date tested.
3. **Interval calibration is the binding problem, and it is temporal and BA-specific rather than geographic.** Static conformal intervals (CQR) under-covered by more than 5 points in a fifth to a third of BAs, whether or not the BA had been seen in training. Online adaptive conformal inference restores marginal coverage by construction. Its practical value depended on the step size: chosen on other BAs, it gave sharpness close to CQR (equal at 24 h, slightly lower at 1 h), whereas the larger pre-specified step produced very wide intervals at 24 h.
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

All code needed to reproduce every number, table and figure (data download, preprocessing, model training, evaluation, statistics, figures, tables and manuscript assembly) is available at [AUTHOR ACTION: repository URL / DOI]. A single command (`python -m src.run_all`) reproduces the full study on a 4-core CPU in roughly six to seven hours of wall-clock time; the frozen protocol, configuration and decision log are versioned with the code.

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
| PJM  | Pjm Interconnection                      | eastern        |              91577 |                   99.73 |               0.3  |          2 |
| MISO | Midcontinent ISO                         | eastern        |              73658 |                   99.91 |               0.1  |          3 |
| ERCO | Electric Reliability Council of Texas    | ercot          |              48661 |                   99.92 |               0.09 |          1 |
| SWPP | Southwest Power Pool                     | eastern        |              31811 |                  100    |               3.7  |          5 |
| SOCO | Southern Company Services                | eastern        |              26887 |                   99.96 |               0.06 |          0 |
| CISO | California ISO                           | western        |              25117 |                   99.81 |               0.33 |          4 |
| TVA  | Tennessee Valley Authority               | eastern        |              18446 |                  100    |               0.03 |          1 |
| NYIS | New York ISO                             | eastern        |              17277 |                  100    |               0.01 |          2 |
| FPL  | Florida Power and Light                  | eastern        |              15664 |                   98.77 |               1.36 |          4 |
| ISNE | Iso New England                          | eastern        |              13193 |                  100    |               0    |          0 |
| DUK  | Duke Energy Carolinas                    | eastern        |              12102 |                   99.92 |               0.08 |          3 |
| CPLE | Duke Energy Progress East                | eastern        |               6982 |                   99.85 |               0.16 |          5 |
| BPAT | Bonneville Power                         | western        |               6563 |                  100    |               0.03 |          1 |
| FPC  | Progress Energy Florida                  | eastern        |               6418 |                   99.92 |               0.09 |          0 |
| PACE | Pacificorp East                          | western        |               5754 |                  100    |               0.19 |          5 |
| PSCO | Public Service Company of Colorado       | western        |               5283 |                   99.96 |               0.13 |          4 |
| NEVP | Nevada Power                             | western        |               4452 |                   99.97 |               0.1  |          3 |
| LGEE | Louisville Gas and Electric and Kentucky | eastern        |               4124 |                   99.72 |               0.42 |          2 |
| SRP  | Salt River Project                       | western        |               3792 |                   99.6  |               0.51 |          4 |
| AZPS | Arizona Public Service                   | western        |               3775 |                   99.96 |               0.14 |          5 |
| WACM | Western Area Power Mountain              | western        |               3104 |                  100    |               0.87 |          0 |
| LDWP | Los Angeles Dept of Water and Power      | western        |               2867 |                   99.73 |               0.48 |          2 |
| SC   | South Carolina Public Service            | eastern        |               2849 |                   99.78 |               0.32 |          3 |
| SCEG | South Carolina Electric and Gas          | eastern        |               2789 |                   99.69 |               0.39 |          1 |
| AECI | Associated Electric Coop                 | eastern        |               2663 |                   99.98 |               0.04 |          4 |
| TEC  | Tampa Electric                           | eastern        |               2513 |                   99.87 |               0.14 |          5 |
| PGE  | Portland General Electric                | western        |               2506 |                   99.96 |               0.07 |          3 |
| PACW | Pacificorp West                          | western        |               2390 |                  100    |               0.04 |          1 |
| FMPP | Florida Municipal Power Pool             | eastern        |               2117 |                   99.76 |               0.5  |          0 |
| IPCO | Idaho Power                              | western        |               2075 |                  100    |               0.01 |          2 |
| BANC | Northern California                      | western        |               1985 |                   99.99 |               2.22 |          0 |
| PNM  | Public Service Company of New Mexico     | western        |               1631 |                  100    |               0.11 |          2 |
| TEPC | Tucson Electric Power                    | western        |               1564 |                   98.43 |               1.61 |          4 |
| JEA  | Jacksonville Energy                      | eastern        |               1518 |                   99.56 |               0.5  |          5 |
| AVA  | Avista                                   | western        |               1462 |                  100    |               0.09 |          3 |
| NWMT | Northwestern Energy                      | western        |               1362 |                   99.96 |               0.39 |          1 |
| SCL  | Seattle City Light                       | western        |               1078 |                   99.99 |               0.08 |          4 |
| WALC | Western Area Power Southwest             | western        |               1052 |                   99.92 |               0.71 |          5 |
| EPE  | El Paso Electric                         | western        |               1015 |                   99.99 |               0.1  |          2 |
| GCPD | Public Utility Grant County              | western        |                689 |                  100    |               0.37 |          1 |
| CPLW | Duke Energy Progress West                | eastern        |                564 |                   99.88 |               0.21 |          3 |
| TPWR | City of Tacoma                           | western        |                545 |                  100    |               0.15 |          0 |
| IID  | Imperial Irrigation                      | western        |                436 |                   99.73 |               1.08 |          3 |
| TIDC | Turlock Irrigation District              | western        |                327 |                   99.8  |               0.72 |          4 |
| TAL  | City of Tallahassee                      | eastern        |                320 |                   98.83 |               1.29 |          2 |
| DOPD | Public Utility of Douglas County         | western        |                240 |                   97.69 |               3.07 |          1 |
| GVL  | Gainesville Regional                     | eastern        |                237 |                   97.89 |               2.66 |          5 |
| CHPD | Public Utility District of Chelan County | western        |                218 |                   99.89 |               0.44 |          0 |



