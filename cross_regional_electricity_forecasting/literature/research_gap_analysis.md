# Research Gap Analysis

*Agent 2, 2026-10-16. Based on the 58-entry `literature_matrix.csv`. Sources: web search result snippets only. Scopus, Web of Science and Crossref were not accessed. Treat every novelty statement as provisional until a database search has been done.*

## 1. Candidate research directions

| ID | Direction | One-line description |
|---|---|---|
| **A** | Cross-region evaluation benchmark with calibrated uncertainty (recommended) | Leave-BAs-out evaluation on EIA-930 of global LightGBM vs local vs naive; limited-target adaptation (about 4 weeks); split, CQR and ACI/AgACI intervals assessed separately under geographic and temporal shift; matched comparison with BA day-ahead forecasts; missingness robustness |
| **B** | New transfer/meta-learning algorithm for unseen BAs | Propose a novel meta-learning or domain-adaptation architecture (STaRNet-like) and show gains on unseen BAs |
| **C** | Time-series foundation-model zero-shot benchmark on EIA-930 | Chronos/TimesFM/Moirai/Lag-Llama zero-shot vs trained models on BAs, with calibration |
| **D** | Audit of operator day-ahead forecast skill | Characterise accuracy, bias and drift of the BA-reported day-ahead forecasts in EIA-930 across BAs and years |
| **E** | Missing-data robustness study | Effect of gaps, imputation and anomaly flags on forecast accuracy and interval coverage |

## 2. Scoring (1 = poor, 5 = excellent)

| Criterion | A | B | C | D | E |
|---|---|---|---|---|---|
| Novelty | 3 | 2 | 2 | 3 | 2 |
| Scientific importance | 4 | 3 | 3 | 3 | 3 |
| Practical relevance | 5 | 3 | 3 | 4 | 4 |
| Dataset suitability (EIA-930) | 5 | 4 | 4 | 5 | 4 |
| Feasibility (one project cycle) | 4 | 2 | 3 | 5 | 4 |
| Reproducibility | 5 | 3 | 2 | 5 | 5 |
| Compute (5 = low) | 5 | 2 | 2 | 5 | 5 |
| Journal suitability | 4 | 3 | 3 | 3 | 3 |
| **Total (/40)** | **35** | **22** | **22** | **33** | **30** |

### Justification

**Direction A.**
- *Novelty (3).* Every component has precedent: transfer [tzortzis2024transfer; yuan2026adaptive], global vs local [montero2021principles; ahmadi2025globalization], ACI and online conformal on electricity series [gibbs2021adaptive; zaffran2022adaptive; angelopoulos2023conformal; areces2025online], and adaptive probabilistic load [devilmarest2024adaptive]. The searches found nothing that combines leave-regions-out evaluation, conformal coverage separated by shift type, and an operator benchmark across tens of BAs. Novelty lies in the combination and the evaluation, not in any method. It scores 3, not 4, because the possibly overlapping building-level paper [crossbuilding2026reliability] could not be verified.
- *Importance (4).* It answers a practical question the field leaves open: whether calibrated intervals stay valid when a model is applied to a new system.
- *Practical relevance (5).* It speaks directly to onboarding small or new BAs and to operators' interest in reliable intervals.
- *Dataset suitability (5).* EIA-930 is the only public, consistent hourly BA-level source with many regions and operator forecasts [hong2026benchmarking; eia930about].
- *Feasibility, reproducibility, compute (4/5/5).* LightGBM plus conformal wrappers run on CPU, and the data are open with PUDL versioning [pudl2026].
- *Journal suitability (4).* Fits IJF, Applied Energy, IEEE TPWRS/TSG or Energy and AI as an empirical, evaluation-focused paper.

**Direction B.**
- STaRNet [yuan2026adaptive], MAML for load [tsoumplekas2025fewshot] and transfer with clustering [tzortzis2024transfer] already occupy this space.
- A new architecture needs extensive tuning and GPU compute, and would be judged against strong, quickly moving baselines. The probability of a defensible algorithmic gain is low.

**Direction C.**
- Several load TSFM benchmarks already exist [meyer2025benchmarking; simeone2026tsfm; emami2023buildingsbench], and model versions change monthly.
- Pretraining-corpus leakage cannot be ruled out easily, and TimeGPT is closed [garza2023timegpt]. Reproducibility is poor and compute is heavy.
- It is better as an optional baseline arm of A, with a documented leakage check.

**Direction D.**
- Highly feasible and useful. The searches found no peer-reviewed systematic audit of EIA-930 day-ahead forecasts; only a commercial tracker surfaced.
- On its own it has limited methodological depth, and BA forecast issue times and methods are undocumented, which limits interpretation. It works best as one component of A.

**Direction E.**
- Builds on Ruggles et al. [ruggles2020developing] and Stratigakos et al. [stratigakos2024resilient]. It is incremental on its own and fits naturally as a robustness section of A.

## 3. Closest prior work (ranked by overlap with A)

1. **Tzortzis et al. 2024** [tzortzis2024transfer]. Held-out-country transfer on 27 European national series. *Difference:* A is probabilistic with conformal coverage, uses U.S. BAs (more and more heterogeneous units), uses pooled GBMs plus residual correction rather than NN warm-start, and adds an operator benchmark.
2. **Yuan et al. 2026, STaRNet** [yuan2026adaptive]. Meta-learning for unseen regions under regional shift. *Difference:* A uses 40-60 regions rather than 4, puts calibration first, and benchmarks simple methods rather than proposing an architecture. *Caveat:* venue unverified.
3. **Ahmadi et al. 2025** [ahmadi2025globalization]. Global vs local, including LightGBM, with zero-shot regional forecasts in Alberta. *Difference:* A has independent BAs across interconnections, conformal coverage under shift, limited-target adaptation and an operator comparison. *Caveat:* we did not see their full results tables.
4. **de Vilmarest et al. 2024** [devilmarest2024adaptive]. Adaptive probabilistic load forecasting under temporal shift (GB and U.S. cities). *Difference:* A adds geographic shift and conformal guarantees, and separates temporal from geographic miscoverage.
5. **Hong, Lee and Shi 2026** [hong2026benchmarking]. Deep-model benchmark on EIA-930. *Difference:* A covers cross-BA generalisation, calibration and operator comparison.
6. **Online conformal on electricity** [gibbs2021adaptive; zaffran2022adaptive; angelopoulos2023conformal; areces2025online] and **cross-building reliability** [crossbuilding2026reliability, unverified]. *Difference:* these cover temporal shift on a few series, or building-level shift. A covers system-level geographic shift at scale.

**Plain statement of overlap.** If [crossbuilding2026reliability] turns out to evaluate conformal coverage on unseen buildings with leave-units-out evaluation, then the *conceptual* design of A (coverage under unit-level shift) has a building-level precedent. A's distinctiveness would then rest on system-level BA data, the separation of geographic and temporal shift, limited-target adaptation, and the operator benchmark. A must not be presented as the first study of conformal coverage under cross-unit load shift.

## 4. Recommended gap statement (conservative)

> Prior work has studied cross-region transfer of point load forecasts on a small number of countries or TSO areas, adaptive probabilistic load forecasting under temporal shift, and online conformal prediction on individual electricity series. To our knowledge, based on a structured but non-exhaustive search, no study has jointly assessed (i) the accuracy of pooled and local models on balancing authorities withheld from training, (ii) the gain from a few weeks of target data, and (iii) whether split and adaptive conformal intervals keep nominal coverage under geographic versus temporal shift, across tens of U.S. balancing authorities and against the operators' own published day-ahead forecasts. We provide a reproducible evaluation framework and benchmark for this setting on EIA-930 data.

The contribution type is an **evaluation framework, benchmark and empirical findings**, not a new forecasting or conformal algorithm.

## 5. Design implications drawn from the literature

- **Geographic blocking.** Hold out BAs grouped by interconnection or geography, not single random BAs, so that neighbour correlation does not leak [roberts2017cross]. Report both random-BA and blocked splits if feasible.
- **Temporal discipline.** Use rolling-origin evaluation [tashman2000out]. Fit scalers, feature statistics and conformal calibration sets on training or calibration windows only [hewamalage2023forecast]. Never use realised weather when comparing with operator forecasts.
- **Scale-free metrics.** Use MASE [hyndman2006another], pinball/CRPS-approximation and interval scores [gneiting2007strictly], coverage and width diagnostics [gneiting2007probabilistic], with per-BA distributions as well as pooled averages.
- **Inference.** Use Diebold-Mariano with HAC variance [diebold1995comparing] and block or stationary bootstrap for score differences [kunsch1989jackknife; politis1994stationary]. Correct for multiple comparisons across BAs.
- **Imputed targets.** Score on reported, non-imputed hours [ruggles2020developing; pudl2026], or report both.
- **Cold-start conformal.** For unseen BAs, report coverage over time-since-onboarding for split conformal calibrated on source BAs vs ACI/AgACI started from that calibration [gibbs2021adaptive; zaffran2022adaptive].

## 6. Claims we must NOT make

1. "First to apply conformal prediction to load forecasting." This is false [matulin2023cqr; angelopoulos2023conformal; areces2025online].
2. "First cross-region / transfer-learning study for load forecasting." This is false [tzortzis2024transfer; yuan2026adaptive; obst2021adaptive; ahmadi2025globalization].
3. "First study of unseen-region (zero-shot) load forecasting." This is false [ahmadi2025globalization; emami2023buildingsbench].
4. "Conformal intervals are guaranteed valid on unseen regions." Split conformal assumes exchangeability, which leave-regions-out breaks. ACI gives only *long-run average* coverage and needs target feedback [gibbs2021adaptive; barber2023conformal]. Report empirical coverage only.
5. "ACI provides conditional or per-hour coverage." It provides long-run marginal coverage.
6. "Our models outperform the balancing authorities' forecasts" as a general statement. Issue times, information sets and purposes of operator forecasts are not documented. At most: "under the stated information set, model X had lower error than the reported day-ahead forecast for k of N BAs."
7. "Results generalise to Europe / OPSD / other countries." No European data were used.
8. "Global gradient boosting is superior to deep learning or foundation models" unless those were actually benchmarked under the same protocol.
9. Any novelty claim that relies on not having found prior work. Use "to our knowledge, based on a non-exhaustive search".
10. "We introduce a new algorithm." Residual correction and ACI/AgACI/CQR are existing methods.
11. Claims of operational or real-time readiness, or of economic value, without a cost or dispatch analysis.
12. Claims that imputed EIA-930 values are ground truth.

## 7. Open risks

- [crossbuilding2026reliability] and [yuan2026adaptive] could not be fully verified and may overlap more than abstracts suggest. Read both in full.
- Recent arXiv preprints (2025-2026) appear quickly in this area. Repeat the search immediately before submission.
- The full results of [ahmadi2025globalization] (zero-shot table) were not seen, so its overlap with A may be larger than estimated.
