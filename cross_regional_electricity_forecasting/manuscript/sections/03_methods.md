# Data and data preparation

## Source and licence

We use the U.S. Energy Information Administration (EIA) Form 930 hourly balancing-authority operations data [@eia930about] as cleaned and published by the Public Utility Data Liberation (PUDL) project of Catalyst Cooperative, release v2026.10.0 [@pudl_eia930_2026; @pudl2026]. A balancing authority (BA) is the entity that balances generation, interchange and load within its area in real time. A BA's hourly *demand* (MWh in an hour, numerically equal to the average MW) is calculated by the BA as metered net generation minus net metered interchange with neighbouring BAs. It therefore excludes behind-the-meter generation such as most rooftop photovoltaics. The EIA data are a U.S. Government work in the public domain; the PUDL release is distributed under CC-BY-4.0. Timestamps are in UTC and mark the end of the hour, so daylight-saving transitions create neither duplicate nor missing timestamps. The raw table contains {{data.n_bas_raw}} BAs from July 2015 to September 2026.

The PUDL release also provides a screened demand series in which missing, non-positive, constant-run, spike and other anomalous values are flagged and imputed with the method of Ruggles et al. [@ruggles2020developing], with a reason code for every flagged hour. Each BA's reported day-ahead demand forecast is included as well.

The project brief originally specified the Open Power System Data (OPSD) time-series package [@wiese2019opsd]. Its hosts were not reachable from the execution environment, so OPSD could not be used. A converter from the OPSD 60-minute file to our panel format is provided with the code for a European replication.

## Region selection

We fixed the study window to 2019–2025 and, before any modelling, applied the following inclusion criteria to the {{data.n_bas_window}} BAs present in that window:

- not a generation-only BA;
- in the Eastern, Western or ERCOT interconnection;
- active through 2025;
- reported demand available for at least 97% of hours;
- at most 5% of hours flagged by PUDL screening, and no year discarded as a "bad year";
- mean demand of at least 200 MW;
- a documented reporting time zone.

{{data.n_regions}} BAs satisfy all criteria: {{data.n_eastern}} in the Eastern interconnection, {{data.n_western}} in the Western and {{data.n_ercot}} in ERCOT (Fig. {fig:fig02_dataset_coverage}; Appendix Table {tab:table_A1_regions}). Their mean demand ranges from {{data.min_mean_mw}} MW ({{data.min_mean_ba}}) to {{data.max_mean_mw}} MW ({{data.max_mean_ba}}), a ratio of about {{data.ratio_max_min}}:1, and their climates range from the Pacific Northwest to Florida and the desert Southwest. Fig. {fig:fig03_example_series} illustrates the resulting differences in daily and seasonal shape.

The panel contains {{data.panel_rows}} BA-hours ({{data.hours_per_region}} hours per BA). Of these, {{data.flagged_pct}}% are flagged by PUDL screening (Fig. {fig:fig04_data_quality}).

[[FIGURE:fig01_workflow]]

[[FIGURE:fig02_dataset_coverage]]

[[FIGURE:fig03_example_series]]

[[FIGURE:fig04_data_quality]]

## Labels, inputs and leakage control

Labels and inputs are deliberately constructed differently.

**Labels.** The training and evaluation label $y_t$ is the PUDL screened demand. Training and scoring use only hours whose reported value was retained by the screening (no reason code). Imputed hours are never scored.

**Inputs.** PUDL's screening uses two-sided windows and whole-series statistics, so using screened values as model *inputs* would leak future information. The input series $x_t$ is therefore the *reported* demand after a causal screen that uses only strictly earlier hours. Non-positive values are set to missing, as is any value above 2.5 times or below 0.25 times the median of the preceding 168 hours (at least 24 observations required). This screen removes {{data.input_missing_pct}}% of input hours.

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

All settings were fixed in a configuration file before test-set evaluation (Fig. {fig:fig01_workflow}).

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
