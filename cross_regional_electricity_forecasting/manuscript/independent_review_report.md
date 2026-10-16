# Independent Review Report (SIMULATED INTERNAL REVIEW)

> **This is a simulated, internal referee report.** It was written by an independent reviewing agent (Agent 9) that did not write the manuscript, imitating a demanding referee for the *International Journal of Forecasting* or *Applied Energy*. It is **not** a real journal review and has no editorial standing. Its purpose is to find weaknesses before submission.

**Manuscript:** "Forecasting Electricity Demand in Unseen Regions: A Leave-Regions-Out Benchmark of Global Models, Short-Window Adaptation and Conformal Calibration across 48 U.S. Balancing Authorities"
**Materials reviewed:** `manuscript/manuscript_rendered.md`, `manuscript/manuscript_final.pdf` (33 pp.), `docs/*`, `DECISION_LOG.md`, `configs/experiment.yaml`, `src/*.py`, `tests/*.py`, `results/metrics/*.csv`, `results/logs/*`, selected `figures/*.png`, `literature/*`, `submission/*`.
**Date:** 2026-10-16

---

## 1. Summary of the submission

The paper benchmarks hourly demand forecasting for 48 U.S. balancing authorities (EIA-930 via PUDL, 2019–2025). It compares four settings:

- in-region global LightGBM (G-IN);
- leave-regions-out global LightGBM (G-LRO, six size-stratified folds of eight BAs);
- per-BA local LightGBM;
- ridge regression and naive references.

All models use instance-normalised lag and calendar features. No weather inputs are used. Forecasts are made at horizons of 1, 6 and 24 h. The paper also evaluates:

- adaptation with 1–13 weeks of target data (local-k and fine-tuning);
- temporal drift, plus a rolling refit;
- prediction intervals (QR, SCP, CQR, SCP-T4, ACI-CQR with delayed feedback, and a validation-tuned ACI-CQR-V);
- robustness to missing inputs;
- ablations and computational cost.

The headline claims are:

- (i) the zero-shot gap is small: a median of 0.5% at 24 h and 3.4% at 1 h;
- (ii) G-LRO is "no worse" than local models;
- (iii) fine-tuning on short windows hurts;
- (iv) static conformal intervals under-cover in 21–33% of BAs, "irrespective of geographic shift";
- (v) ACI fixes per-BA coverage if its step size suits the feedback delay.

## 2. Strengths

1. **Careful leakage engineering.** Inputs and labels are constructed differently: a causal input screen is used for inputs and PUDL-screened labels for scoring. Features are past-only, and a unit test checks this by perturbing future inputs (`tests/test_pipeline.py::test_features_do_not_use_future`). LRO models are fitted, early-stopped and calibrated only on source BAs (`src/train_models.py::run_point`). I verified these code paths and found no test-set leakage into the point forecasts.
2. **Correct ACI implementation with delayed feedback.** In `src/conformal.py::aci_intervals`, the miscoverage at step *t* is the score at index *t − h* compared with the threshold *issued* at that index. Scores enter the pool only once observed. Dropped (flagged) hours make the index-based delay conservative rather than leaky.
3. **Transparent reporting.** The paper reports negative results (fine-tuning, SCP-T4) and a post-hoc γ table that is clearly labelled. Amendments are logged (D9–D13). The internal audit (`docs/statistical_audit.md`) is candid.
4. **Effect sizes before p-values.** Results use per-BA medians, bootstrap CIs over BAs and a per-BA moving-block bootstrap.
5. **Numbers match the result files.** Every number I spot-checked in the text and tables (about 90 values, Section 5) matches `results/metrics/*.csv` to the stated rounding.
6. **Well-defined computational and data-quality context.** The data source is public, carries checksums and has a provenance record.

## 3. Overall assessment

This is a competent, honest benchmark with a reproducible pipeline. It is not ready for IJF or Applied Energy in its current form, for four reasons:

- The "unseen region" design does not create a strong geographic shift. Folds are random within size blocks, so close neighbours and same-utility siblings of each held-out BA remain in training. Yet the paper's central conclusions are that "geographic shift matters little" and that zero-shot transfer "works".
- Several headline claims go further than the evidence. These include "no worse than local", "pooling is worth more than target history", "fine-tuning should be avoided" and "ACI restores per-BA coverage". Some rest on non-significant differences. Some rest on a single adaptation origin. Some rest on properties that ACI guarantees by construction.
- The set of baselines is thin for 2026: no weather, no statistical models, no neural models and no foundation models. The ridge baseline is untuned.
- The bibliography contains an entry whose authors are "not retrieved" and another whose venue is "not verified". These appear verbatim in the PDF reference list.

**Recommendation: Major revision required** (see Section 6).

---

## 4. Issues by severity

Counts: **Critical 2 · Major 8 · Moderate 10 · Minor 10** (30 in total; details and requested actions are also in `manuscript/reviewer_comments.csv`).

### 4.1 Critical

**R1 — The "unseen region" design does not test geographic shift (Sections 3, 7, 9.1, 9.4, 10).**
- **Design.** Folds are built by ranking on size and randomly permuting within blocks of six (`src/train_models.py::lro_folds`). Geography, utility membership and climate are ignored.
- **Consequence.** For most held-out BAs, a neighbour sharing weather, customer mix or operator stays in the training pool. Examples from Table A1 (folds): CPLE (fold 5) with CPLW (3) and DUK (3); CHPD (0) with GCPD and DOPD (1); FPC (0) with FPL (4), TEC (5) and JEA (5); PACE (5) with PACW (1); and the Arizona and New Mexico desert BAs spread across folds.
- **Why it matters.** The test period is simultaneous for all BAs. The model never sees the target's own lags, but it has learned the calendar and seasonal response to the same weather regime from co-located source BAs. The measured "geographic gap" is therefore a lower bound for genuinely new geography.
- **Claims affected.** The paper cites spatial cross-validation (Roberts et al., 2017) but does not apply it. The following claims all rest on this weak shift: "geographic shift matters little for calibration" (Section 9.4); "irrespective of geographic shift" (Abstract); and "temporal and BA-specific rather than geographic" (Conclusion 3).
- **Requested action.** Add spatially blocked designs: at minimum leave-one-interconnection-out (Western versus Eastern), plus leave-climate-region-out or leave-neighbourhood-out with a buffer that excludes BAs adjacent to the target. Report how the gap and coverage change. Until then, re-word the claims as "unseen BA within a covered geography".

**R2 — Unverified and placeholder references in the bibliography (Section 2; reference list).**
- **Placeholder citation.** The PDF cites "(Authors not retrieved, 2026)" in the text (PDF line ≈139). The reference list entry reads "Authors not retrieved, 2026. Evaluating the reliability of cross-building load forecasting…" (`literature/verified_references.bib`, key `crossbuilding2026reliability`; literature matrix status "unverified").
- **Unverified venue.** `yuan2026adaptive` is rendered as "Elsevier journal (venue not verified)" with "others" in the author list.
- **Snippet-only verification.** 19 of 58 matrix entries are "partially verified" or "preprint". Even classic references such as Hyndman & Koehler (2006), Diebold & Mariano (1995) and Tashman (2000) have DOIs that were "not verified" (DECISION_LOG D7: verification only from search snippets).
- Two of the four sources used to state the research gap are recent preprints (`hong2026benchmarking`, `simeone2026tsfm`) or unverified (`yuan2026adaptive`).
- **Requested action.** Verify every reference against the publisher or Crossref. Remove or replace any reference whose authors and venue cannot be confirmed. Clearly mark preprints. Re-check that the gap statement still holds once verified sources are used.

### 4.2 Major

**R3 — "Zero-shot is no worse than local" and "pooling is worth more than target history" are over-claimed (Abstract, Sections 9.1, 10, 13, 16).**
- **The test result.** At 24 h, G-LRO versus local gives a median of −0.8% (CI −1.6 to 0.2%). The raw Wilcoxon p is 0.068 and the Holm-adjusted p is 0.21 (`paired_tests_point.csv`). That is a failure to reject, not a demonstrated non-inferiority; no equivalence margin was pre-specified.
- **Instability over time.** In 2024 the local model had the *lowest* median 24-h nMAE: 4.49% versus 4.54% (G-IN) and 4.56% (G-LRO). It was also lowest in spring (MAM 4.54% versus 4.64%/4.78%) and in the 2023 validation year (4.56% versus 4.60%/4.67%) (`temporal_metrics_summary.csv`).
- **Source of the global advantage.** The 24-h advantage of the global models appears only in 2025, when the frozen local models are two years old. Refitting improves local models by 0.85% (Holm p < 1e-5).
- **Requested action.**
  - State a non-inferiority margin and test against it, for example with TOST on per-BA relative nMAE.
  - Report the global-versus-local comparison by year and with refitted local models.
  - Remove "data pooling is worth more than target-specific history" for the day-ahead horizon, or restrict it to 1–6 h, where it is robust.

**R4 — The adaptation experiment (RQ2) cannot support general conclusions (Sections 6.2, 9.2, 10, 13, 16).**
- **One origin.** Every adaptation model uses a single origin, 1 January 2024. The window covers only the last 1–13 weeks of 2023, and the adapted model is then frozen for two years. Month and day-of-year features are almost constant inside a December window. Continued boosting therefore learns a December-specific correction and applies it all year, which explains the degradation by design.
- **Fixed settings.** Adaptation settings were fixed a priori (FT: 200 trees, learning rate 0.02, 15 leaves; local-k: 300 trees, no early stopping).
- **Undisclosed learning-rate difference.** Contrary to the statement that the learning-rate amendment D13 was "applied identically to all LightGBM variants within a horizon", LGB-L-k uses the default learning rate of 0.05 at h ∈ {1, 6}. The code passes `small` without the horizon override (`src/train_models.py::run_adapt`), while the base models use 0.2.
- **Mixed result at 1 h.** At h = 1 the 13-week fine-tuned model is *better* than zero-shot: −1.5%, CI −2.5 to −0.7%, better in 87.5% of BAs.
- **Over-generalised conclusions.** "Fine-tuning … should be avoided" (Section 13) and "Short-window adaptation does not help" (Conclusion 2) do not follow from this design.
- **Requested action.**
  - Repeat E2 at several onboarding origins spread over the year, for example monthly.
  - Add rolling re-adaptation, plus regularised or shrinkage adaptation (for example a bias or level correction only, or fine-tuning only leaf values).
  - Tune the number of trees with an inner time split inside the window.
  - Fix or disclose the learning-rate inconsistency.
  - Tone down Conclusion 2.

**R5 — Baselines are inadequate for IJF or Applied Energy in 2026 (Sections 6, 14).**
- **No weather.** There are no weather covariates at all. Even an *oracle* run with observed temperature (e.g. ERA5 or NOAA ISD, by BA centroid) would show whether the geographic gap and the calibration findings survive once the dominant driver is present. Limitation 2 acknowledges this but does not test it.
- **No statistical models.** There is no SARIMA/ETS/TBATS/MSTL or comparable benchmark, and no GEFCom-style multiple-linear-regression benchmark.
- **No neural global models.** DeepAR and N-BEATS/N-HiTS are absent, although these are the natural global-model comparators.
- **No foundation models.** None is included, even though the introduction motivates the work with zero-shot foundation models. Small CPU-runnable checkpoints exist (e.g. Chronos-Bolt-small/tiny). The stated obstacle, that weights were "not reachable", is an execution-environment problem, not a scientific reason.
- **Untuned ridge.** Ridge uses λ = 1 without tuning, while LightGBM was grid-searched.
- **Requested action.** Add at least one weather-informed model, one classical statistical model, one global neural model and one foundation model under the same LRO protocol. Tune ridge λ on VAL-ES.

**R6 — ACI evaluation and interpretation (Sections 6.3, 9.4, 10, 13).**
- **Coverage near nominal is guaranteed.** ACI's long-run bound |mean(err) − α| ≤ (max(α₁, 1−α₁) + γ)/(γT) holds deterministically for any sequence. Mean per-BA coverage of about 90% is therefore guaranteed rather than discovered. "Restores coverage in every BA" should not be presented as an empirical finding.
- **Conditional coverage is not reported.** The informative quantities are conditional coverage (by season, hour of day, peak-load hours, ramps) and sharpness. Fig. 9c shows pooled January coverage of about 86–88% for ACI-CQR-V as well. The protocol's E4 promised a seasonal coverage breakdown, which is not reported.
- **No sharpness gain at 24 h.** ACI-CQR-V's median interval score (28.24%) is *no better* than static CQR (28.15%) for unseen BAs, so the gain is purely in marginal per-BA coverage.
- **Selected γ is at the grid edge.** The validation-selected γ = 0.001 is the smallest value in the grid (`aci_gamma_selected_on_validation.csv`; validation IS 0.315 versus 0.359 for γ = 0.002). The least adaptive option wins, and a γ = 0 control (an expanding calibration pool without updating α) is missing.
- **The γ = 0.005 failure depends on the capping rule.** When α_t leaves (0, 1), the threshold is capped at the maximum score ever seen (post-freeze fix D9). This makes capped intervals extremely wide (mean width 82.6% of load; up to 20% of hours capped in one BA, `aci_capped_share_by_region.csv`). The conclusion that "step size is decisive" is therefore partly an artefact of this capping rule.
- **Requested action.**
  - Add a γ = 0 control and extend the γ grid below 0.001.
  - Add a variant that clips α_t to [ε, 1−ε].
  - Add aggregated ACI (AgACI), conformal PID / quantile tracking and a rolling-window CQR.
  - Report conditional coverage by season, hour and load decile.
  - Re-phrase the ACI claims accordingly.

**R7 — ACI-CQR-V is post hoc and uses target-BA history (Sections 6.3, 9.4, 10, 13, 15).**
- **Target data used.** γ is selected on the 2023 data of the *held-out* (test) BAs (`evaluate_models.py::select_gamma_validation`). This contradicts "Online recalibration with ACI solves the per-BA coverage problem without any target history" (Section 10).
- **Post hoc.** The variant was added after the pre-registered variant was seen to fail on the test set (D10). The selection stream (2023) is also in the same year as the source calibration scores, which makes validation easier than the 2-year-ahead test.
- **Recommendation rests on it.** Practical recommendation 3 depends on this variant.
- **Requested action.** Select γ using *source* BAs only, within each LRO fold. Confirm the result on a later hold-out (for example 2026 data, which are available to September 2026). Label ACI-CQR-V as exploratory throughout, including the Abstract and Highlights.

**R8 — Fairness and convergence of hyper-parameter tuning (Sections 6.1, 12; DECISION_LOG D13).**
- **Grid too small.** Each grid is 2×2, and both selected optima lie at the grid edge (global: 255 leaves; local: 127 leaves, 100 minimum samples; `hyperparameter_grid_validation.json`).
- **Tuning tied to one setting.** Selection was done only at h = 24, on G-IN, using validation weeks of *all 48* BAs. The result was reused for G-LRO, so held-out BAs influenced the LRO hyper-parameters. This is a small but real departure from "unseen".
- **Unequal convergence at 1 h.** At h = 1, G-IN still hits the 3,000-tree cap even at learning rate 0.2 (Table 11, `compute_costs_point.csv`). LRO folds stop at 2,262–2,998 trees. The two arms being compared are not equally converged, and the 1-h gap (3.4%) and the global-versus-local differences at 1 h may be biased.
- **Learning rate changed without retuning.** The learning rate was changed by horizon without retuning leaves.
- **Requested action.**
  - Tune per horizon on source-only validation data inside each fold (nested).
  - Widen the grid.
  - Raise the tree cap, or report sensitivity to it.
  - Report convergence diagnostics for every arm.

**R9 — Median effects hide large BA-level failures, which matters for the practical claims (Sections 9.1, 10, 13, 15).**
- **Large gaps exist.** The 1-h relative gap is 44.6% for GCPD and about 19% for MISO, a 74-GW market. At 6 h it is 29.3% for GCPD (Fig. 6b; recomputed from `point_metrics_by_region.csv`).
- **Contradicted statements.**
  - "Within about 1–3% (relative)" and "can be deployed from the first day" (Section 13.1).
  - Construct validity: "the largest ISOs, where the geographic gap was small" (Section 15). This is contradicted at h = 1 by MISO.
- **Requested action.** Report the distribution of the gap, including the 90th percentile and maximum, and the share of BAs above, say, 10%. Diagnose GCPD and MISO; for MISO, consider reporting-practice and footprint changes. Qualify the deployment recommendation by tail risk.

**R10 — "Pre-registered" is overstated, and amendment accounting is inconsistent (Abstract, Sections 3, 7, 15).**
- **What the freeze is.** The freeze is an internal version-control commit made on the same day as the analysis (all DECISION_LOG entries are dated 2026-10-16). There is no time-stamped external registration (OSF, AsPredicted).
- **Count mismatch.** The text says "Four post-freeze amendments", but the protocol lists D9–D12 as post-freeze and D13 is also post-freeze, which makes five. D12, the year-grouping change, is omitted from the manuscript.
- **Protocol items not delivered.** E4 at h = 6 and the seasonal coverage breakdown are not reported, and the h = 6 omission is not flagged as a deviation in Section 15.
- **Different gap definition.** The protocol defines the gap as an absolute metric difference; the paper reports relative change.
- **Requested action.** Replace "pre-registered" with "protocol frozen in version control before test evaluation" (or register externally for a confirmatory follow-up on 2026 data). Give a complete deviation table.

### 4.3 Moderate

**R11 — Dependence between BAs and multiple testing (Section 8).**
- **Dependence ignored.** Wilcoxon tests treat 48 BAs as independent, although they share weather, interconnections and, in some cases, operators.
- **Holm families misdescribed.** The text says Holm is applied "over all reported comparisons". In the code it is applied over the 72 point tests only. Adaptation, refit (2 tests per horizon) and ablation tests have separate Holm families (`stats.compare_methods`, `paired_tests_refit.csv`).
- **Requested action.** Add a cluster or block bootstrap over BA groups (interconnection or region) for the headline effects. Describe the Holm families accurately, or apply one family.

**R12 — Sample selection versus the motivating use case (Sections 1, 4.2).**
- **Mismatch.** The introduction motivates the work with "a small BA without a dedicated forecasting team" and data-poor systems. Selection excludes BAs below 200 MW and those with more than 3% missing or more than 5% flagged hours: 18 of 66 BAs, many of them small (`regions_all.csv`). Results therefore apply to large, well-reported BAs.
- **Requested action.** Report results for the excluded small or low-quality BAs as a secondary analysis, or narrow the motivation.

**R13 — The operator day-ahead comparison is over-interpreted (Sections 9.1, 10).**
- **Speculative attribution.** "This difference mainly reflects the value of weather information" is not tested. The issuance time of the BA forecasts is unknown and probably earlier than 24 h ahead, which works against the operators. Their models also differ in many other ways.
- **Unmentioned result.** At h = 6, G-IN (3.49%) is more accurate than BA-DA (3.57%) (`ba_dayahead_summary.csv`), but this is not mentioned.
- **Requested action.** Remove the causal attribution, or support it with the weather experiment (R5).

**R14 — Missing-data experiment design (Sections 7, 11.1).**
- **Different scored hours.** Strategies are compared on different hour sets: native handling drops origins with fewer than 24 observed hours (minimum scored share 96.9%), while LOCF and seasonal imputation score all hours. This violates protocol rule 2 ("identical (region, hour) pairs").
- **Unrealistic gap patterns.** MCAR and uniform random blocks are not realistic EIA-930 outage patterns.
- **Partial coverage of the augmentation.** Augmentation is tested only for G-IN, not for G-LRO.
- **Inconsistent framing.** A +2.5% relative cost on clean data (1.17% versus 1.14%) is called "almost nothing", while a +3.4% geographic gap is called "systematic".
- **Requested action.** Score all strategies on common hours. Add a scenario based on the empirical gap patterns in EIA-930. Make the framing consistent.

**R15 — SCP-T4 conclusion (Section 9.4).**
- **Optimistic residuals.** For in-region models, the 4-week target window includes odd ISO weeks used for early stopping (VAL-ES), so the residuals are optimistic.
- **One window.** The conclusion "target calibration from recent weeks fails" generalises from one December window.
- **Missing baseline.** A *rolling* 4-week target calibration, updated online, is the natural baseline and is missing.
- **Requested action.** Exclude early-stopping weeks from the window, add rolling-window target calibration, and repeat over several origins.

**R16 — Ablation interpretation (Section 11.2).**
- **Confounded pool size.** Smaller source pools also mean fewer training rows, with hyper-parameters fixed for 48 BAs (255 leaves).
- **Too few draws.** Three draws cannot support "the size of the pool, rather than its particular composition, drives the loss".
- **Contradicted statement.** Section 10 says accuracy "degrades only when the source pool is small", yet 20 sources already cost 0.4–0.8%, about the size of the 24-h geographic gap.
- **Requested action.** Use more draws, report a subsampled-rows control, and revise the wording.

**R17 — Literature coverage gaps (Section 2).**
- **Missing work.** Global and probabilistic neural forecasters (DeepAR, Salinas et al., IJF 2020; N-BEATS, Oreshkin et al., 2020); the global-model literature beyond Montero-Manso & Hyndman (e.g. Hewamalage, Bergmeir & Bandara, 2022); conformal prediction under covariate shift (Tibshirani et al., 2019); strongly adaptive online conformal methods (Bhatnagar et al., 2023); and cross-building transfer learning (e.g. Ribeiro et al., 2018).
- **Weak support for the gap.** The gap statement relies on preprints.
- **Requested action.** Extend the related work with verified sources and re-assess novelty. In particular, BuildingsBench and Ahmadi et al. already include zero-shot evaluation on unseen regions or buildings; sharpen what is new.

**R18 — Length, structure and presentation (whole manuscript).**
- **Too long.** The manuscript runs to 33 pages, 16 sections, 13 figures and 12 tables.
- **Tables for the supplement.** Table 9 (90 rows) and Table 7 (48 rows) belong in a supplement. Table 3 largely duplicates Table 1.
- **Weak figure.** Fig. 6a (points on the identity line) conveys little.
- **Unclear column.** In Table 7, the column "BAs under-covered >5 pp" holds percentages (values up to 69), not counts.
- **Requested action.** Condense the paper to fit the IJF norm (about 8–10k words in the main text). Move detail tables to an online appendix. Merge Sections 13–15.

**R19 — Reproducibility statements are incomplete or inconsistent (Back matter, Section 12).**
- **Placeholders.** The code and data DOIs are placeholders, yet the abstract says "Code and protocol are openly available".
- **Run time.** Section 12 gives "roughly six hours", while the Code availability statement gives "approximately 3–4 hours".
- **Contaminated timing.** The 6-h G-IN timing overlapped another job and was not rerun.
- **Unarchived inputs.** Raw data are referenced by checksum, but the processed panel is not archived.
- **Requested action.** Mint a DOI for the code and derived data, harmonise the run-time statement, rerun the timing, and archive the processed panel.

**R20 — Practical significance not quantified in energy-system terms (Sections 13, 16; Applied Energy fit).**
- **Missing link.** No link is made from nMAE or coverage to reserve or imbalance cost, peak errors or ramps.
- **Requested action.** For Applied Energy in particular, add at least one operational metric, such as the error at daily peak, the upper-tail coverage relevant to reserve sizing, or a stylised reserve-cost calculation.

### 4.4 Minor

- **R21.** Section 3 says "The search was not exhaustive (see Section 14)", but Section 14 (Limitations) does not discuss the literature search.
- **R22.** Section 9.3 reads "Holm *p* = <0.0001"; it should read "*p* < 0.0001".
- **R23.** Figure numbering differs from the file names: Fig. 7 is `fig08_transfer.png` and Fig. 8 is `fig07_temporal_shift.png`. The x-axis of Fig. 7 (0, 1, 4, 13 weeks) is non-linear without saying so.
- **R24.** The Abstract says under-coverage occurs in "20.8–33.3%" of systems, while Conclusion 3 says "a fifth to a half of BAs". The latter mixes in QR and 50% intervals. The Highlights say ACI "fixes coverage". Harmonise all three.
- **R25.** The text says the raw table holds "70 BAs", while DECISION_LOG D2 says "72 BAs". Reconcile the two.
- **R26.** Table A1 has lowercased BA names and a typo ("tuscon" for Tucson).
- **R27.** The Persistence row at h = 24 is identical to SN24. Remove it, or footnote it in Tables 1 and 4.
- **R28.** In Table 2, "nan" cells for pairs without a block bootstrap should be shown as "–".
- **R29.** The ACI delay is applied by index, not by timestamp. This is conservative but should be documented. In the 50% intervals, ACI never caps; say so.
- **R30.** RQ5 (trade-offs) is not answered explicitly. Add a short synthesis table covering accuracy, coverage, cost and data needs.

---

## 5. Number-verification log

I checked numbers in the manuscript text, tables and abstract against the result files. ✓ means a match to the stated rounding. File paths are relative to `results/metrics/` unless stated otherwise.

| # | Manuscript value (location) | Source file / field | Source value | Result |
|---|---|---|---|---|
| 1 | G-IN nMAE 4.64%, MASE 0.884 (h = 24; Sec. 9.1, Table 1) | point_metrics_summary.csv | 0.046447; 0.883957 | ✓ |
| 2 | G-LRO 4.75%; local 4.72%; ridge 5.05%; SN24 5.48% (h = 24) | point_metrics_summary.csv | 0.047510; 0.047233; 0.050478; 0.054773 | ✓ |
| 3 | h = 6: 3.50 / 3.66 / 3.78; h = 1: 1.14 / 1.17 / 1.28 | point_metrics_summary.csv | 0.035005/0.036601/0.037831; 0.011416/0.011722/0.012815 | ✓ |
| 4 | Gap 0.5% (CI 0.4–0.7), LRO better in 6.2% of BAs (h = 24) | paired_tests_point.csv | 0.00545 [0.00381, 0.00749]; share 0.0625 | ✓ |
| 5 | Gap 1.9% (h = 6); 3.4% (CI 2.5–4.6) (h = 1) | paired_tests_point.csv | 0.0191; 0.0338 [0.0249, 0.0457] | ✓ |
| 6 | Block bootstrap: in-region better in 97.9% (h = 1), 52.1% (h = 24) | block_bootstrap_summary.csv | 0.979167; 0.520833 | ✓ |
| 7 | GCPD gap 6.6%; corr −0.25; LRO range 2.47% (GCPD) – 8.55% (AECI) (h = 24) | recomputed from point_metrics_by_region.csv + data/processed/regions.csv | 6.59%; Pearson −0.250; 2.47; 8.55 | ✓ |
| 8 | Local→G-IN −1.4% (CI −2.2 to −0.8) at 24 h; −9.2% at 1 h | paired_tests_point.csv | −0.0141 [−0.0220, −0.0076]; −0.0915 | ✓ |
| 9 | G-LRO vs local −0.8% (CI −1.6 to 0.2), Holm p = 0.21; −5.4% (CI −8.1 to −3.7) at 1 h | paired_tests_point.csv | −0.0075 [−0.0157, 0.0022], p_holm_all 0.205 (raw p 0.068); −0.0541 [−0.0813, −0.0371] | ✓ (raw p not reported; see R3) |
| 10 | Ridge comparisons −5.5% (24 h), −19.3% (1 h); ridge gap 0.1% | paired_tests_point.csv | −0.0553; −0.1935; 0.0012 | ✓ |
| 11 | BA-DA 3.57% vs G-IN 4.64% | ba_dayahead_summary.csv | 0.035692; 0.046447 | ✓ |
| 12 | Local-k at 24 h: 9.21 / 8.07 / 5.77%; FT: 5.37 / 5.26 / 5.00% | adaptation_metrics_summary.csv | 0.092094/0.080700/0.057677; 0.053678/0.052620/0.049958 | ✓ |
| 13 | FT vs zero-shot: +12.9% (CI 9.7–17.9) at 4 wk, +6.5% at 13 wk; h = 1: +0.9%, −1.5% | paired_tests_adaptation.csv | 0.1293 [0.0974, 0.1791]; 0.0646; 0.0092; −0.0152 | ✓ |
| 14 | Temporal: G-IN 4.60 / 4.54 / 4.67; SN 5.16 / 5.56; local 4.49→4.80; LRO 4.56→4.72 | temporal_metrics_summary.csv | 0.045986/0.045368/0.046745; 0.051607/0.055574; 0.044868→0.047968; 0.045574→0.047204 | ✓ (local is *best* in 2024; see R3) |
| 15 | Season (24 h): DJF 4.76, JJA 4.76, SON 4.34 | temporal_metrics_summary.csv | 0.047618, 0.047557, 0.043358 | ✓ |
| 16 | Refit: 4.67 vs 4.67; local 4.80→4.78; +0.1% (p = 0.87), −0.9% (p < 0.0001) | refit_metrics_summary.csv; paired_tests_refit.csv | 0.046745/0.046680; 0.047968/0.047761; 0.00066 (0.867); −0.0085 (6.2e-6) | ✓ (Holm family is per horizon, not "all"; see R11) |
| 17 | CQR unseen 90% (24 h): mean 89.2%, min 78.6%, 20.8% under-covered | probabilistic_summary.csv | 0.891688; 0.786488; 0.208333 | ✓ |
| 18 | QR mean 87.3%; SCP min 71.4%; in-region CQR 89.2%, 18.8% | probabilistic_summary.csv | 0.872592; 0.713626; 0.892422, 0.1875 | ✓ |
| 19 | SCP-T4 85.3%; CQR 89.5%→88.8% (2024→2025) | probabilistic_summary.csv | 0.852713; 0.894929→0.888442 | ✓ |
| 20 | ACI γ = 0.005: mean 90.0%, min 89.8%, capped 4.4%, IS 88.55% vs CQR 28.15% | probabilistic_summary.csv; aci_gamma_sensitivity_summary.csv | 0.8996; 0.8979; 0.0437; 0.885535 vs 0.281529 | ✓ |
| 21 | Selected γ 0.001 (24 h), 0.002 (1 h) | aci_gamma_selected_on_validation.csv | 0.001; 0.002 | ✓ (both at or near the grid edge) |
| 22 | ACI-CQR-V (24 h): 89.4–90.5%, IS 28.24%, width 17.81%; h = 1: min 89.7%, IS 7.13% vs CQR 7.21%; CQR 33.3% under-covered | probabilistic_summary.csv | 0.8938–0.9050; 0.282371; 0.178115; 0.897353; 0.071328 vs 0.072136; 0.333333 | ✓ |
| 23 | Abstract "20.8–33.3% of systems" | probabilistic_summary.csv (unseen CQR 90%, h = 24/1) | 0.2083; 0.3333 | ✓ (but see R24 vs the Conclusion) |
| 24 | Missing data, G-IN 24 h: 4.64→5.05 (10% MCAR), 6.93 (40%) | missing_data_summary.csv | 0.050485; 0.069349 | ✓ |
| 25 | Missing data, 1 h: 1.84, 4.04; LOCF 1.68; block-168 LOCF 2.66 / native 1.95 / seasonal 2.05 | missing_data_summary.csv | 0.018376; 0.040355; 0.016820; 0.026604/0.019461/0.020502 | ✓ |
| 26 | Augmented model 1.32 / 2.29; clean 1.17; LRO 1.93; min scored share 96.9% | missing_data_summary.csv | 0.013205/0.022936; 0.011698; 0.019340; 0.968831 | ✓ |
| 27 | Ablations: calendar 6.7% (5.0–7.0); weekly 0.6% (0.5–1.3); recent 0.3% (0.1–0.4) | ablation_results.csv | 0.0672 [0.0495, 0.0702]; 0.0065 [0.0055, 0.0128]; 0.0027 [0.0012, 0.0036] | ✓ |
| 28 | Pool sizes 20/10/5 → 4.81 / 4.87 / 4.97 (mean of draws); 4.93–5.00 | ablation_results.csv | 4.807 / 4.866 / 4.975; 4.925–5.004 | ✓ |
| 29 | Compute: 42.0 s, 4.64 MB, local 83.6 s, ridge 20.6 s (24 h); 298.1 s, 70.74 MB, 3,000 trees, local 595.6 s (1 h); 164.2 / 5.59 µs; 1,261.9 s; LRO 6 h mean 79.7 s; LRO 1 h mean 245.6 s / 2,708 trees | results/logs/compute_costs_point.csv | 42.03; 4,638,129 B; 83.55; 20.59; 298.06; 70,735,825 B; 3000; 595.63; 138.27 s/842,112 rows; 4.708/842,112; 1261.89; mean(56.2…99.4) = 79.7; mean = 245.6 / 2707.5 | ✓ |
| 30 | Fine-tuning 0.23 s per BA (4 wk, 24 h) | results/logs/compute_costs_adapt.csv | 0.232 | ✓ |
| 31 | 48 BAs: 21 Eastern / 26 Western / 1 ERCOT; 2,945,664 BA-hours; 0.55% flagged; ratio 419:1 | data/processed/regions.csv | 21/26/1; 2,945,664; 0.5516%; 419.19 | ✓ |
| 32 | 48 of 66 BAs selected | data/processed/regions_all.csv; data_quality_report.md | 66 rows; "48 of 66" | ✓ |
| 33 | "Four post-freeze amendments" | DECISION_LOG.md; docs/experimental_protocol.md | D9, D10, D11, D12, D13 (five) | ✗ mismatch (R10) |
| 34 | Full study run time "roughly six hours" (Sec. 12) vs "approximately 3–4 hours" (Code availability) | internal inconsistency | — | ✗ mismatch (R19) |
| 35 | D13 "applied identically to all LightGBM variants within a horizon" | src/train_models.py::run_adapt | LGB-L-k uses learning rate 0.05 at h = 1/6 | ✗ mismatch (R4) |
| 36 | "Holm adjustment over all reported comparisons" | src/evaluate_models.py; src/stats.py | separate families for point / adaptation / refit / ablation | ✗ mismatch (R11) |
| 37 | Raw table "70 BAs" | DECISION_LOG D2 ("72 BAs") | — | ✗ unresolved (R25) |
| 38 | Causal input screen removes 0.33% of input hours | data/metadata (not located in a CSV during review) | — | not verified |

**Summary:** 32 numeric checks (about 90 individual values) matched. Five statements are inconsistent with the code or logs, and one value could not be verified.

---

## 6. Recommendation

**Major revision required.**

**Justification.** The engineering is careful, the numbers are internally consistent, and the evaluation framework is a useful contribution in its own right. But the paper's central scientific message, that geographic shift is a minor problem compared with temporal and BA heterogeneity, is not yet supported:

- (a) The leave-regions-out folds keep neighbouring and same-utility BAs in training (R1).
- (b) There are no weather inputs and no modern global, neural or foundation baselines (R5).
- (c) Several headline claims are stronger than the statistics allow: "no worse than local" and "pooling beats target history" (R3), "fine-tuning should be avoided" (R4), and "ACI restores coverage" (R6, R7).

The bibliography also contains placeholder and unverified entries (R2). That alone would trigger desk rejection, although it is straightforward to fix.

None of these problems is fatal to the project. They can be addressed with additional experiments the existing pipeline already supports: spatially blocked folds, multiple adaptation origins, a γ = 0 control and conditional coverage, a weather covariate, and one foundation-model baseline. They also need re-worded claims and a verified bibliography. If those are done, the work would be a credible IJF submission. For Applied Energy it additionally needs operational, energy-system metrics (R20).
