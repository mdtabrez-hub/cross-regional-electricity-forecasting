# Search Log

**Date:** 2026-10-16
**Agent:** Agent 2 (Literature Review and Research-Gap Specialist)

## Sources actually reached

- **WebSearch tool, "standard" mode:** about 60 queries. One query used "extended" mode.
- **What the results contained:** titles, URLs and short summaries drawn from:
  - publisher, proceedings and repository pages: proceedings.neurips.cc, proceedings.mlr.press, projecteuclid.org, link.springer.com, pmc.ncbi.nlm.nih.gov, ieeexplore.ieee.org (listing only), sciencedirect.com (listing only), mdpi.com (link only);
  - bibliographic indexes: ideas.repec.org (RePEc), mlanthology.org, DOAJ;
  - preprint servers: arxiv.org;
  - institutional repositories: eprints.gla.ac.uk, orbit.dtu.dk, research portals of IP Paris, XJTLU, Tilburg, Monash and UW;
  - data and documentation: zenodo.org, docs.catalyst.coop, eia.gov.
- **WebFetch:** tried once (mdpi.com) and failed with a DNS error (ENOTFOUND). No full texts were downloaded or read.
- **Not accessed:** Scopus, Web of Science, Crossref API, OpenAlex API, Google Scholar. DOIs were therefore checked only against search-result content, not resolved at doi.org.

## Queries run (in order, paraphrased exactly as submitted)

1. Hong Fan 2016 "Probabilistic electric load forecasting: A tutorial review" International Journal of Forecasting doi
2. Montero-Manso Hyndman 2021 "Principles and algorithms for forecasting groups of time series: Locality and globality" doi
3. Ruggles Farnham Tong Caldeira "Developing reliable hourly electricity demand data through screening and imputation" Scientific Data 2020
4. Gibbs Candès "Adaptive conformal inference under distribution shift" NeurIPS 2021
5. BuildingsBench Emami 2023 large-scale dataset 900K buildings pretraining short-term load forecasting
6. conformal prediction electricity load forecasting adaptive conformal inference distribution shift paper
7. EIA-930 balancing authority hourly demand forecasting machine learning benchmark day-ahead forecast accuracy
8. transfer learning load forecasting across regions countries few-shot target data paper
9. time series foundation models zero-shot electricity load forecasting evaluation Chronos TimesFM Moirai benchmark energy
10. Zaffran Féron Goude Josse Dieuleveut "Adaptive conformal predictions for time series" ICML 2022 electricity spot prices
11. "Transfer learning for day-ahead load forecasting: a case study on European national electricity demand time series" authors journal
12. arXiv 2602.21415 "Benchmarking State Space Models, Transformers, and Recurrent Networks for US Grid Forecasting" authors
13. Meyer "Benchmarking Time Series Foundation Models for Short-Term Household Electricity Load Forecasting" 2024
14. conformal prediction probabilistic load forecasting smart meter calibration prediction intervals journal
15. global forecasting model electricity load pooled across regions LightGBM generalization unseen regions
16. arXiv 2507.11729 "Globalization for Scalable Short-term Load Forecasting" authors
17. "Comparative Analysis of Global and Local Probabilistic Time Series Forecasting for Contiguous Spatial Demand Regions" authors dataset
18. Simeone arXiv 2602.10848 "Time Series Foundation Models for Energy Load Forecasting on Consumer Hardware" ERCOT
19. GEFCom2017 hierarchical probabilistic load forecasting International Journal of Forecasting
20. Hong Pinson Fan Zareipour Troccoli Hyndman "Probabilistic energy forecasting: GEFCom2014 and beyond" doi
21. Gneiting Raftery 2007 "Strictly proper scoring rules, prediction, and estimation" JASA doi
22. Gneiting Balabdaoui Raftery 2007 "Probabilistic forecasts, calibration and sharpness" JRSS B doi
23. Barber Candès Ramdas Tibshirani "Conformal prediction beyond exchangeability" Annals of Statistics 2023 doi
24. Xu Xie "Conformal prediction interval for dynamic time-series" ICML 2021 EnbPI PMLR
25. Angelopoulos Candès Tibshirani "Conformal PID control for time series prediction" NeurIPS 2023
26. Bergmeir Benítez 2012 "On the use of cross-validation for time series predictor evaluation" doi
27. Bergmeir Hyndman Koo 2018 "A note on the validity of cross-validation..." doi
28. Hewamalage Ackermann Bergmeir "Forecast evaluation for data scientists..." doi
29. Tashman 2000 "Out-of-sample tests of forecasting accuracy: an analysis and review" doi
30. Hyndman Koehler 2006 "Another look at measures of forecast accuracy" doi
31. Diebold Mariano 1995 "Comparing predictive accuracy" doi
32. Politis Romano 1994 "The stationary bootstrap"; Künsch 1989 "The jackknife and the bootstrap for general stationary observations" doi
33. Ke Meng Finley "LightGBM..." NIPS 2017 proceedings
34. Wiese Schlecht Bunke "Open Power System Data..." Applied Energy 2019 doi
35. Hirth Mühlenpfordt Bulkeley 2018 "The ENTSO-E Transparency Platform..." doi
36. "Open Power System Data" Wiese 2019 "10.1016/j.apenergy.2018.11.097" (DOI corroboration)
37. "Comparing predictive accuracy" Diebold Mariano DOI corroboration query; DOI **not** corroborated, so it was left blank
38. Ansari et al. "Chronos: Learning the language of time series" TMLR 2024
39. Das Kong Sen Zhou "A decoder-only foundation model for time-series forecasting" ICML 2024
40. Woo et al. "Unified training of universal time series forecasting transformers" Moirai ICML 2024
41. Rasul et al. "Lag-Llama..." arXiv
42. Makridakis Spiliotis Assimakopoulos "M5 accuracy competition..." doi
43. Hong Pinson Fan 2014 "Global Energy Forecasting Competition 2012" doi
44. Romano Patterson Candès "Conformalized quantile regression" NeurIPS 2019
45. Gama et al. "A survey on concept drift adaptation" doi
46. Hong et al. "Energy forecasting: A review and outlook" OAJPE 2020 doi
47. EIA-930 balancing authority day-ahead demand forecast error analysis study
48. domain adaptation few-shot electricity load forecasting unseen buildings or regions meta-learning
49. online conformal prediction load forecasting distribution shift coverage evaluation electricity demand 2024 2025
50. Koenker Bassett 1978 "Regression quantiles" doi
51. "Adaptive load forecasting under regional distribution shifts" meta-learning STaRNet
52. Areces "Online conformal prediction via online optimization" ICML 2025
53. Garza Mergenthaler-Canseco "TimeGPT-1" arXiv
54. Vovk Gammerman Shafer "Algorithmic Learning in a Random World" doi
55. Catalyst Cooperative PUDL Zenodo data release doi
56. STaRNet journal / author follow-up
57. de Vilmarest et al. "Adaptive probabilistic forecasting of electricity (net-)load" IEEE TPWRS
58. Obst de Vilmarest Goude "Adaptive methods ... COVID-19 lockdown in France" doi; journal **not** confirmed
59. Farrokhabadi et al. "Day-ahead electricity demand forecasting competition: post-COVID paradigm"
60. missing data imputation electricity load time series forecasting robustness
61. Stratigakos et al. "Towards resilient energy forecasting: a robust optimization approach"
62. "A Grid-Aware Spatio-Temporal Framework for Probabilistic Load Forecasting with Mondrian Conformal Calibration" authors (not retrieved; excluded from matrix)
63. Matulin Capuder Plavšić conformalized quantile regression load forecasting
64. EIA Form 930 data quality issues research paper
65. Hyndman Athanasopoulos "Forecasting: Principles and Practice" (found; not included)
66. "balancing authorities" probabilistic load forecasting quantile conformal EIA multiple regions
67. arXiv 2604.22077 TSFM power system forecasting authors (not retrieved; excluded)
68. zero-shot load forecasting unseen region conformal prediction intervals coverage transfer learning (**extended** mode)
69. "Evaluating the Reliability of Cross-Building Load Forecasting Under Distribution Shift and Sensor Missingness" (authors not retrieved)
70. arXiv 2609.26959 transfer learning + CQR for solar PV (found; excluded as off-topic: PV, not load)
71. Ahmadi Zareipour Leung zero-shot Alberta details
72. mdpi applied sciences 2026 16 7984 cross-building (follow-up; not resolved)
73. Roberts et al. 2017 cross-validation strategies Ecography doi
74. Lei et al. 2018 "Distribution-free predictive inference for regression" doi
75. Xu Xie SPCI ICML 2023
76. EIA Hourly Electric Grid Monitor / Form EIA-930 about the data
77. Tsoumplekas few-shot load forecasting Energies 2025 doi
78. Antoniadis Gaucher Goude hierarchical transfer learning IJF 2024 doi
79. Lago et al. 2021 day-ahead price forecasting benchmark doi
80. Hong Lee Shi 2026 EIA-930 benchmark abstract details
81. Tzortzis et al. Mathematics DOI follow-up; DOI **not** seen, so it was left blank and the URL used

## Found but excluded

The following came up in searches but were left out, either because metadata could not be retrieved or because the topic was peripheral:

- Tilburg Mondrian conformal paper (authors not retrieved)
- arXiv 2604.22077 (authors not retrieved)
- ETASR 2026 building CQR paper (peripheral)
- UiT 2021 master's thesis on deep conformalized quantile regression (thesis)
- arXiv 2609.26959 solar PV transfer + CQR (PV, not load)
- O'Connor et al. 2025 conformal electricity price forecasting (price, not load)
- "Informative Missingness in Grid Load Forecasting", NeurIPS 2026 listing (authors not retrieved)
- Simeone-adjacent ERCOT TSFM benchmark (authors not retrieved)

## Notes on verification policy

- A `doi` field appears in the BibTeX only when the DOI string appeared in a search result: a publisher page, PMC, Project Euclid, a RePEc/IDEAS record, BibSonomy, DOAJ or an institutional repository. DOIs that are probably correct but were not seen were left blank. This applies to Diebold-Mariano 1995, Tashman 2000, Hyndman-Koehler 2006, GEFCom2014, GEFCom2017 and Tzortzis et al. 2024.
- The matrix contains one "unverified" entry, [crossbuilding2026reliability]. It was kept because it may be the closest competitor and must be read in full.
- Search engines can return synthesised summaries. Every finding recorded in the matrix is taken from abstract-level text and should be checked against the full paper before it is cited in the manuscript.

---

## Revision pass (2026-10-16, after internal review)

**Sources reached:** WebSearch only, about 22 further queries (3 in "extended" mode). WebFetch was not retried. Scopus, Web of Science and Crossref were still not accessed.

### Re-verification queries

1. Applied Sciences cross-building reliability paper: exact title (extended); DOI plus "HEEW"; title plus "mdpi applsci author"; "16(16) 7984 HEEW ... conformal SHAP" (extended).
2. STaRNet exact title plus "journal doi" (extended).
3. GEFCom2014 title with a candidate DOI string, which was **not** corroborated.
4. GEFCom2017 title plus DOI.
5. Tashman with a candidate DOI string.
6. Hyndman–Koehler with a candidate DOI string, then a ScienceDirect PII query.
7. Diebold–Mariano on Taylor & Francis.
8. Tzortzis et al. title plus "Mathematics doi".
9. Stratigakos et al. plus IEEE TSG.
10. Obst et al. plus IEEE TPWRS.
11. "PUDL Data Release v2026.10.0 zenodo".
12. Matulin DOI.
13. Ahmadi et al. journal version.

### New-entry queries

Tibshirani et al. 2019 (covariate shift); Salinas et al. DeepAR (twice); Oreshkin et al. N-BEATS; Hewamalage, Bergmeir & Bandara 2022; Bhatnagar et al. 2023; Ribeiro et al. 2018. *Forecasting: Principles and Practice* (3rd edition) was verified from earlier search results (OTexts 2021, ISBN 9780987507136).

### Outcomes

**Now verified (DOI added only where the DOI string itself was seen):**
- yuan2026adaptive: Engineering Applications of Artificial Intelligence 164:113104; DOI 10.1016/j.engappai.2025.113104; full author list.
- hong2019gefcom2017: DOI 10.1016/j.ijforecast.2019.02.006.
- hyndman2006another: DOI 10.1016/j.ijforecast.2006.03.001, seen as a doi.org result.
- stratigakos2024resilient: IEEE Transactions on Smart Grid 15(1):874–885; DOI 10.1109/TSG.2023.3272379, from HAL and dblp.
- tzortzis2024transfer: venue confirmed. DOI string never seen, so it was left blank and the MDPI URL is used.

**Still partially verified:**
- hong2016gefcom2014, tashman2000out, diebold1995comparing: DOI never seen.
- obst2021adaptive: journal stated only on a co-author's publications page.
- matulin2023cqr: DOI seen once and not corroborated, so it was removed from the BibTeX doi field.
- eia930about.
- pudl2026: **no Zenodo record for v2026.10.0 was found**. The latest release seen was v2026.7.2, and two different concept DOIs appeared (10.5281/zenodo.3404014 and 10.5281/zenodo.3653158), so the DOI was left blank.

**Marked "unverified – do not cite":**
- crossbuilding2026reliability: title and DOI 10.3390/app16167984 were seen, but the author list could not be established from a publisher page.
  - Its content, per search summaries, makes it the closest design analogue found: HEEW buildings, building-isolated folds, LightGBM residual model, future-year scenario, sensor missingness, and conformal coverage lost on unseen buildings.
  - It is removed from related_work_draft.md citations. The gap analysis was updated to state the overlap plainly.

**New entries:**
- tibshirani2019conformal
- salinas2020deepar: DOI seen.
- oreshkin2020nbeats
- hewamalage2022global: DOI not seen.
- bhatnagar2023improved
- ribeiro2018transfer: DOI not seen.
- hyndman2021fpp3

### BibTeX changes

- Bibkeys of existing entries are unchanged.
- Placeholder text was removed from author and journal fields.
- The do-not-cite entry keeps its BibTeX record, with no author field and an explanatory note.

**Matrix totals after revision:** 65 entries. 51 verified, 7 partially verified, 6 arXiv-only preprints, 1 unverified – do not cite.
