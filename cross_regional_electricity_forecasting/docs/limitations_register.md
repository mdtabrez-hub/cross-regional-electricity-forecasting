# Limitations Register

| ID | Limitation | Type | Effect on conclusions | Mitigation / status |
|---|---|---|---|---|
| L1 | OPSD (European) data, specified in the brief, could not be accessed; study uses U.S. EIA-930 only | Data / external validity | Findings concern U.S. BAs; transfer to European countries untested | OPSD adapter provided; replication listed as future work |
| L2 | No weather inputs (temperature forecasts dominate day-ahead load forecasting practice) | Design | Absolute errors are higher than operational weather-driven models; relative comparisons among models are on equal information | Stated in all comparisons with BA day-ahead forecasts |
| L3 | BA day-ahead forecasts have unknown issuance time and use weather forecasts; our h = 24 models use data up to 24 h before each target | Comparability | BA-DA comparison is a contextual reference, not a fair head-to-head | Reported separately (Table 11) |
| L4 | BAs are spatially correlated (shared weather, interconnection, ISO/utility overlap in operations) | Statistics | Region-level tests overstate effective sample size | Effects reported with bootstrap CIs and block bootstrap; p-values interpreted cautiously |
| L5 | Single test window (2024–2025) and a single training window for the main results; one rolling refit | Temporal external validity | Results may depend on the specific years (e.g. structural load growth or BA membership changes in 2024–2025) | Year-wise and seasonal breakdowns; refit experiment |
| L6 | Labels are PUDL-screened values; scoring only on unflagged hours | Measurement | Extreme events flagged as anomalies are excluded from scoring; errors during anomalies are not measured | Flag shares reported (Fig. 4); input screening is causal |
| L7 | Early stopping uses odd ISO weeks of 2023; adaptation windows overlap 2023 | Selection | Minor optimism for validation-year errors (not for test) | Validation errors flagged as optimistic in temporal analysis |
| L8 | Hyper-parameters chosen for the pooled model at h = 24 h and reused for all settings | Tuning | Local and small-data models may be sub-optimally tuned | Local grid tuned separately; adaptation models use fixed small-tree settings (documented) |
| L9 | No neural or foundation models (CPU only; Hugging Face weights not reachable) | Scope | Cannot state how foundation models compare | Listed as future work; literature discussed |
| L10 | Times New Roman not installed in the build environment; figures and PDF rendered with metric-compatible Liberation Serif; DOCX specifies Times New Roman | Presentation | Visual appearance only | Re-running `src.generate_figures` where TNR is installed embeds TNR |
| L11 | Literature verification relied on search-engine snippets (Crossref/Scopus/WoS not accessible) | Bibliography | Residual risk of metadata errors | Verification status column in literature matrix; manual check required before submission |
| L12 | Calendar features use each BA's reporting time zone and U.S. federal holidays only | Features | Regional holidays not modelled | Equal for all models |
| L13 | Conformal guarantees assume exchangeability, which time series and unseen regions violate | Theory | Coverage is empirical, not guaranteed | This is the object of study (RQ3) |
