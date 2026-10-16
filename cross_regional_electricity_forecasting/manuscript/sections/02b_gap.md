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

