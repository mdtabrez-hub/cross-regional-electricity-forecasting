# Final Quality-Assurance Report

**Auditor:** Agent 12 (independent final QA). **Date:** 2026-10-16 (audit window ≈ 15:30–16:00 UTC).
**Scope:** project root `cross_regional_electricity_forecasting/`, manuscript `manuscript/manuscript_final.docx` (+ `.pdf`, `manuscript_rendered.md`), supplement, simulated review and revision materials, submission package.
**Method:** I re-derived numbers from `results/metrics/*_by_region.csv` (per-BA files) and, for the headline numbers, from the raw prediction parquet files. I did not use `results/manuscript_numbers.json`. I also ran `python3 -m pytest -q tests` and `python3 -m src.qa_checks`, inspected the DOCX with python-docx and the PDF with poppler, viewed four figure PNGs, and read every submission document. I did not run git. "In git" status is inferred from `.gitignore` rules.

> **Note on concurrent edits.** `README.md` (15:29:59 UTC) and `LICENSES_AND_DATA_PROVENANCE.md` (15:30:16 UTC) changed while this audit was running. The findings below refer to the versions on disk at about 15:33 UTC.

---

## 1. Summary verdict

**Verdict: NOT YET SUBMISSION-READY.** The science and the numbers are sound, but the manuscript cannot be submitted as it stands.

**What checks out:**
- **No critical defects.** Every one of the 52 numbers I re-derived matches the manuscript within rounding.
- **Tables and figures match the data.** The main tables match their source CSVs. The headline accuracy numbers reproduce exactly from the raw predictions.
- **Tests and checksums pass.** All 15 unit tests pass, and the raw-data SHA-256 checksums verify.
- **The Word file is correctly formatted.** It uses Times New Roman at 12 pt, justified, with 1.5 line spacing. It has page numbers and 13 embedded figures, and no unresolved citations.
- **Simulated materials are clearly labelled.** The review and response materials say plainly that they are simulated.

**What blocks submission:**
1. **Mandatory author actions (not defects).** There are 9 `[AUTHOR ACTION]` placeholders in the manuscript: names, affiliations, funding, COI, CRediT, AI disclosure and the repository DOI. There is also no code licence, an unfinished in-text reference (the Applied Sciences 2026 article, by DOI only), and 13 cited references that are preprints or only partially verified.
2. **Two moderate text defects.**
   - **D1.** An unsupported claim that small BAs benefit from pooling as much as large ones; the data show the opposite.
   - **D2.** Reproducibility and availability statements that are not yet true. A "single command reproduces the full study" is false, because `run_all` omits the post-review stages. Predictions are said to be "included in the repository", but they are gitignored.
3. **Several minor defects (D3–D11).** These are listed in §4.

When the moderate defects are fixed and the author actions are done, I expect the manuscript to be ready to submit. That still requires a final regeneration (`src.build_manuscript`) and a re-run of `src.qa_checks`.

**Check tally (16 items):** Passed 11 · Partially verified 4 · Requires manual verification 1 · Failed 0.

---

## 2. Check table

| # | Check | Status | Evidence |
|---|---|---|---|
| 1 | Dataset source documented; licensing respected; raw data not committed | **Passed** | `LICENSES_AND_DATA_PROVENANCE.md` names the source (PUDL v2026.10.0, EIA-930, retrieval date, S3 marker, Zenodo DOI 10.5281/zenodo.22525116) and its licences (EIA public domain; PUDL CC-BY-4.0, attributed). `data/metadata/dataset_metadata.json` matches (pudl_version 2026.10.0, git sha 90561c6, licences). `.gitignore` excludes `data/raw/*.parquet`, `data/processed/*.parquet`, `results/models/` and the predictions. The OPSD substitution is documented (DECISION_LOG D2; manuscript §4.1). Note: `data/raw/pudl_parquet_datapackage.json` (4.5 MB, CC-BY metadata) and `data/raw/SHA256SUMS` are not ignored, which is acceptable. |
| 2 | Data transformations reproducible | **Partially verified** | All 22 `src/` modules exist. `src/run_all.py` `STAGES` runs: download → preprocess → inspect → train (select / point / adapt / refit) → robustness (missing / ablation) → evaluate → robustness evaluate → tables → figures. `sha256sum -c data/raw/SHA256SUMS` passes for all 4 parquet files, and `configs/experiment.yaml` also carries the checksums. **Gaps:** `run_all` does not include `revision_experiments`, `revision_evaluate`, `manuscript_numbers` or the manuscript build. README lists them separately, but the manuscript claims a single command (D2). `run_all` was never run end to end; there is no `results/logs/environment.json`, and the campaign used `results/logs/run_*.sh`. |
| 3 | All reported experiments executed | **Passed** | Every experiment family has predictions, metrics and logs (table below). Timestamps run in order from 05:33 (download) to 15:25 (revision evaluation). `results/logs/final.out` ends with a traceback in `robustness_analysis evaluate`; the code was fixed at 15:05:43 and the metrics regenerated at 15:10:29, but the re-run itself is not logged (D9). |
| 4 | Numerical consistency (≥25 numbers re-derived) | **Passed** | 52 numbers re-derived independently (§3); 52 of 52 match within display rounding. The headline h = 24 and h = 1 medians and gaps were also recomputed from `results/predictions_compact/*.parquet`: 4.645 / 4.751 / 4.723% and 0.545%; 1.142 / 1.172 / 1.281% and 3.383%; maximum gap 44.62% (GCPD). `src.qa_checks` also passes its raw-prediction check. |
| 5 | Tables match underlying CSVs | **Passed** | Every data row of the 12 main tables in `results/tables/*.md` appears verbatim in `manuscript_rendered.md`. Spot-checks against the metrics: file `table_2` (manuscript Table 1) against `point_metrics_summary.csv`; `table_3` (Table 2) against `paired_tests_point.csv` + `block_bootstrap_summary.csv`, using p_holm_all for the 72-test family; `table_7` against `probabilistic_summary.csv` (12 of 12 rows); `table_8` against `rev_calibration_summary.csv` (15 of 15); `table_9` against `missing_data_summary.csv` (common hours; 40 of 40 cells); `table_10` against `ablation_results.csv` (14 of 14). File and caption numbering differs from the manuscript numbering (D6). |
| 6 | Figures match saved data | **Passed** | `figures/figure_manifest.csv` lists all 13 figures (PNG at 600 dpi plus PDF) with their source and script. **Fig. 5:** box medians match `point_metrics_by_region.csv`. **Fig. 7:** points match `adaptation_metrics_summary.csv` (e.g. 24 h: 9.21 / 8.07 / 5.77 local-k; 5.37 / 5.26 / 5.00 FT; zero-shot 4.75). **Fig. 9:** unseen CQR mean ≈ 89.2, SCP-T4 minimum ≈ 60.8, ACI tight at 90. **Fig. 12:** calendar ablation +6.7 [5.0, 7.0]; in-region −0.5; pool draws 4.93–5.00 (5), 4.86–4.87 (10), 4.79–4.82 (20); full pool 4.75. Fonts are Liberation Serif (documented substitute). The Fig. 10 source is in gitignored `results/predictions/`. |
| 7 | Citations genuine | **Requires manual verification** | 63 keys are cited in `manuscript/sections/*.md`; all are in `literature_matrix.csv` and `verified_references.bib` (66 entries). All 34 bib DOIs are well formed (`10.xxxx/…`). The "do not cite" entry `crossbuilding2026reliability` is **not cited by key** and does not appear in the rendered reference list (63 bibliography paragraphs). However, the same work is described in the text by DOI (`10.3390/app16167984`) with an `[AUTHOR ACTION]` flag (`02_related.md` l.21), so it must be completed or removed. **Preprints cited (6):** ahmadi2025globalization, garza2023timegpt, hong2026benchmarking (used in the gap statement), ling2025comparative, rasul2023lagllama, simeone2026tsfm. **Partially verified (7):** diebold1995comparing, eia930about, hong2016gefcom2014, matulin2023cqr, obst2021adaptive, pudl2026 (v2026.10.0 Zenodo record not found; concept DOI conflicting), tashman2000out. All verification was from web-search snippets; Crossref, Scopus and WoS were unavailable (DECISION_LOG D7). I saw no fabricated-looking entries; titles, venues and years are plausible and consistent. |
| 8 | No unsupported novelty claims or overstatements | **Partially verified** | Novelty is hedged appropriately ("To our knowledge, based on a non-exhaustive search"; "not a new forecasting or conformal algorithm"; C14 marked P). ACI coverage is correctly described as holding by construction. Post-hoc analyses are labelled. **Remaining overstatements:** D1 (small BAs benefit from pooling as much as large ones); D2 (single-command reproduction; predictions in repository; also in the cover letter and declarations); D4 (abstract and highlight under-coverage range attributed to "static conformal intervals… seen or unseen"); D8 (cover-letter framing omits the 8.0% spatial hour-ahead gap). |
| 9 | Reviewer-response materials labelled simulated/internal | **Passed** | `response_to_reviewers_template.docx` is headed "PREPARATION EXERCISE" and states: "The comments below come from an INTERNAL, SIMULATED review … NOT comments from any journal or real referee." `independent_review_report.md` is headed "SIMULATED INTERNAL REVIEW". DECISION_LOG D14 says "simulated internal review". The manuscript refers only to an "internal review". |
| 10 | Limitations acknowledged; critical findings R1, R2 resolved or documented | **Passed** | §14 lists 12 limitations, and §15 covers threats to validity, including the post-hoc analyses and five post-freeze amendments. **R1 (critical):** resolved. Spatially blocked folds were run; `rev_spatial_*.csv` and Table 8 / S6 exist and were verified (gap 1.7% / 8.0%; spatial CQR 89.5% mean). **R2 (critical):** documented. The bad entry was removed from the reference list and is now an AUTHOR ACTION, and `revision_matrix.csv` status reads "Partially verified … manual check required". R5 and R19 are "Partially resolved", and R8 is "Disclosed, not resolved"; all three are disclosed in Limitations. |
| 11 | Word document formatting | **Passed** | Details are listed after this table. |
| 12 | Code and dependencies; tests pass | **Passed** | `requirements.txt` pins 13 packages, and every installed version matches the pins exactly (numpy 2.5.3, pandas 3.0.5, lightgbm 4.7.0, …). `environment.yml` specifies python 3.13 plus the pip requirements. All third-party imports in `src/` are covered. `python3 -m pytest -q tests`: **15 passed in 0.74 s**. pandoc 3.1.3 and Chromium are non-Python requirements; they are documented in README but not listed in `environment.yml`. |
| 13 | Execution instructions; referenced commands exist | **Passed** | Every README command resolves: `src.run_all`; `src.revision_experiments {ridge, excluded, origins, spatial}` (matches the argparse `choices`); `src.revision_evaluate`; `src.robustness_analysis evaluate` (choices missing / ablation / evaluate); `src.generate_tables`; `src.generate_figures`; `src.manuscript_numbers`; `src.build_manuscript --sections-dir --rendered --out` (all are argparse options); `src.build_submission_docs`; `src.qa_checks`. Runtime statements are inconsistent across files (D7). |
| 14 | Journal recommendations use current evidence; no fabricated metrics | **Partially verified** | `journal_selection_report.md` and `journal_comparison.csv` date all evidence to 2026-10-16 and mark it as snippet-level. They state explicitly that SCIE status, quartiles and acceptance rates are "Not verified". Conflicting values are shown side by side (IJF IF 7.1 vs 5.7; APC 3,500 vs 2,800). They say scores are "not estimates of the chance of acceptance", and the checklist uses [V]/[U] tags. I could not re-verify the metric values themselves (no web access in this audit), so the author must confirm them. The abstract (133 words) meets IJF's 100–150 limit. The highlights (74–83 characters) meet Applied Energy's ≤ 85. |
| 15 | Author-specific placeholders, not invented | **Passed** | The manuscript has 9 `[AUTHOR ACTION]` placeholders plus `[Author 1]`, `[Author 2]`, `[Affiliation 1]` and `[Affiliation 2]`. The cover letter has date, corresponding author, repository and suggested-reviewer placeholders. `declarations_template.docx` has funding, COI, CRediT and AI-use placeholders. README and LICENSES carry a code-licence `[AUTHOR ACTION]`. No names, grants or affiliations are invented. The AI-assistance disclosure is drafted for the authors to complete. |
| 16 | Other blockers | **Partially verified** | No scientific blockers. Before submission: the moderate defects D1 and D2; the author actions in §5; the IJF reference style is unverified (currently Elsevier-Harvard CSL); the uncaptioned RQ5 table (D5). |

**Check 11 details (Word document formatting).** `manuscript_final.docx` opens in python-docx (426 paragraphs, 13 tables, 13 inline images).
- **Font:** every non-empty run is Times New Roman, including the 114 OMML math objects. Heading styles reference theme fonts, but every heading run overrides them with TNR.
- **Body text:** 12 pt, justified, line spacing w:line = 360 (1.5×) on all 278 body paragraphs (Body Text, First Paragraph, Compact). The bibliography uses 11 pt; captions 10 pt; table text 8 pt.
- **Page numbers:** the footer contains a PAGE field.
- **Citations:** none unresolved; no `[@`, `???` or citeproc "missing" markers.
- **Figures:** all 13 are embedded.
- **Identical copy:** `revised_manuscript.docx` is byte-identical to `manuscript_final.docx` (`cmp`).
- **Figure fonts:** the figures use **Liberation Serif**, a metric-compatible substitute because Times New Roman is not installed. This is documented in `figure_manifest.csv`, `src/generate_figures.py` and `RESEARCH_STATUS.md`.
- **PDF:** the PDF is **not** exported from the DOCX. It is rendered by pandoc (HTML/MathML) and headless Chromium (Skia/PDF m141), because LibreOffice drops inline OMML. It is 35 A4 pages with page numbers, and its embedded fonts are LiberationSerif, FreeSans, DejaVuSans and DejaVuSansMono. Treat the PDF as a preview; the DOCX is the submission source.
- **Note:** one uncaptioned table (D5).

**Experiment execution evidence (check 3).** File sizes are in bytes; times are UTC on 2026-10-16.

| Family (manuscript) | Predictions | Metrics | Log |
|---|---|---|---|
| E1 point (h 1/6/24) | `point_h1` 168.7 MB (08:29), `point_h6` 83.5 MB (09:34), `point_h24` 168.7 MB (06:21) | `point_metrics_*`, `paired_tests_point`, `block_bootstrap_*` | `train.log`, `evaluate.log`, `compute_costs_point.csv` |
| Adaptation (E2) | `adapt_h1/h6/h24` ≈ 65.6 MB each (09:46–09:53) | `adaptation_metrics_*`, `paired_tests_adaptation` | `train.log`, `compute_costs_adapt.csv` |
| Refit (E3) | `refit_h1/h6/h24` ≈ 19.6 MB each (10:10–10:18) | `refit_metrics_*`, `paired_tests_refit`, `temporal_metrics_*` | `train.log` |
| Probabilistic (E4) | `lro_source_calibration_h1/h24` 48.4 MB, `h6` 13.6 MB; quantile columns in `point_h*` | `probabilistic_*`, `pinball_*`, `aci_*` | `evaluate.log`, `prob_eval.out` |
| Missing data (E5) | `missing_h1` 466.9 MB (12:07), `missing_h24` 467.0 MB (12:14) | `missing_data_*` (regenerated 15:10) | `robustness.log`, `campaign3.out` |
| Ablation (E6) | `ablation_h24` 95.8 MB (12:47) + `ablation_source_pools.json` | `ablation_*` | `robustness.log` |
| Spatial (post-review) | `spatial_h1` 40.9 MB, `spatial_h24` 83.5 MB, `spatial_source_calibration_h1/h24` | `rev_spatial_*`, `rev_calibration_*`, `rev_gap_distribution_cluster_bootstrap` | `revision.out` (… "NE+NY done", REVISION_DONE), `rev_eval.log` |
| Multi-origin adaptation | `adapt_origins_h6/h24` ≈ 64.7 MB (13:29–13:36) | `rev_adapt_origins_*` | `revision.log` |
| Excluded BAs | `excluded_bas.parquet` 4.95 MB (13:25) | `rev_excluded_bas.csv` | `revision.log` |
| Ridge grid | – (validation only) | `results/logs/ridge_alpha_grid_validation.csv`, table S9 | `revision.log` |
| Compute (E7) | – | `compute_costs_point.csv`, `compute_costs_adapt.csv` | – |

---

## 3. Number-verification log

All values were recomputed from `results/metrics/*_by_region.csv` as medians, means or shares over the 48 BAs, or as paired per-BA ratios A/B − 1. Rows marked † were also recomputed from the raw predictions. "Loc." is the section of `manuscript_rendered.md`. All values are in %, unless they are MASE values or counts.

| # | Loc. | Quantity | In text | Recomputed | OK |
|---|---|---|---|---|---|
| 1 | Abstract, 9.1 | Median gap G-LRO vs G-IN, 24 h † | 0.5 | 0.545 | ✓ |
| 2 | Abstract, 9.1 | Median gap, 1 h † | 3.4 | 3.383 | ✓ |
| 3 | 9.1 | Median gap, 6 h | 1.9 | 1.911 | ✓ |
| 4 | Abstract, 11.3 | Spatial gap 24 h / 1 h | 1.7 / 8.0 | 1.71 / 7.96 | ✓ |
| 5 | Abstract | Unseen CQR share > 5 pp under, 24 h / 1 h | 20.8 / 33.3 | 20.83 / 33.33 | ✓ |
| 6 | 9.1 | G-IN median nMAE 24 h † | 4.64 | 4.645 | ✓ |
| 7 | 9.1 | G-LRO median nMAE 24 h † | 4.75 | 4.751 | ✓ |
| 8 | 9.1 | Local median nMAE 24 h † | 4.72 | 4.723 | ✓ |
| 9 | 9.1 | Ridge / SN24 median nMAE 24 h | 5.05 / 5.48 | 5.048 / 5.477 | ✓ |
| 10 | 9.1 | G-IN MASE 24 h | 0.884 | 0.884 | ✓ |
| 11 | 9.1 | 6 h medians G-IN / G-LRO / Local | 3.50 / 3.66 / 3.78 | 3.500 / 3.660 / 3.783 | ✓ |
| 12 | 9.1 | 1 h medians G-IN / G-LRO / Local † | 1.14 / 1.17 / 1.28 | 1.142 / 1.172 / 1.281 | ✓ |
| 13 | 9.1 | Share of BAs where G-LRO is better, 24 h | 6.2 | 6.25 | ✓ |
| 14 | 9.1 | Block bootstrap: G-IN significantly better, 1 h / 24 h | 97.9 / 52.1 | 97.92 / 52.08 | ✓ |
| 15 | 9.1 | 1 h gap: share > 5% / P90 / max (BA) † | 31.2 / 8.3 / 44.6 (GCPD) | 31.25 / 8.32 / 44.62 (GCPD) | ✓ |
| 16 | 9.1 | MISO gap 1 h | 18.5 | 18.48 | ✓ |
| 17 | 9.1 | 6 h max gap; 24 h P90 / max | 29.3 (GCPD); 1.8 / 6.6 (GCPD) | 29.28 (GCPD); 1.79 / 6.59 (GCPD) | ✓ |
| 18 | 9.1 | Pearson correlation of gap with log mean demand, 24 h | −0.25 | −0.250 | ✓ |
| 19 | 9.1 | Zero-shot 24 h min / max BA | 2.47 (GCPD) / 8.55 (AECI) | 2.47 (GCPD) / 8.55 (AECI) | ✓ |
| 20 | 9.1 | G-IN vs Local, 24 h / 1 h | −1.4 / −9.2 | −1.411 / −9.153 | ✓ |
| 21 | 9.1, Table 2 | G-LRO vs Local, 1 h / 6 h / 24 h | −5.4 / −3.1 / −0.8 | −5.408 / −3.074 / −0.752 | ✓ |
| 22 | 9.1 | Holm p (72-test family), G-LRO vs Local 24 h | 0.21 | 0.205 (p_holm_all) | ✓ |
| 23 | 9.1 | 90% cluster CI for non-inferiority, 24 h | −2.1 to 0.3 | −2.08 to 0.32 | ✓ |
| 24 | 9.1 | G-LRO vs Local by year, 24 h: 2024 / 2025 | 0.0 / −1.4 | 0.00 / −1.37 | ✓ |
| 25 | 9.1 | G-IN vs Ridge, 24 h / 1 h; ridge gap 24 h | −5.5 / −19.3; 0.1 | −5.531 / −19.346; 0.122 | ✓ |
| 26 | 9.1 | BA day-ahead median nMAE | 3.57 | 3.569 | ✓ |
| 27 | 9.2 | Local-k 24 h (1 / 4 / 13 wk) | 9.21 / 8.07 / 5.77 | 9.209 / 8.070 / 5.768 | ✓ |
| 28 | 9.2 | FT-k 24 h (1 / 4 / 13 wk) | 5.37 / 5.26 / 5.00 | 5.368 / 5.262 / 4.996 | ✓ |
| 29 | 9.2 | FT vs zero-shot: 4 wk 24 h / 13 wk 24 h / 13 wk 1 h | 12.9 / 6.5 / −1.5 | 12.93 / 6.46 / −1.52 | ✓ |
| 30 | 9.2 | Extra origins, FT range 24 h / 6 h | +5.4 to +14.3 / +1.2 to +6.0 | 5.37–14.35 / 1.23–5.96 | ✓ |
| 31 | 9.3 | G-IN 24 h by year 2023 / 2024 / 2025 | 4.60 / 4.54 / 4.67 | 4.599 / 4.537 / 4.674 | ✓ |
| 32 | 9.3 | SN24 2024 / 2025; Local 2024 / 2025; G-LRO 2024 / 2025 | 5.16 / 5.56; 4.49 / 4.80; 4.56 / 4.72 | 5.161 / 5.557; 4.487 / 4.797; 4.557 / 4.720 | ✓ |
| 33 | 9.3 | G-IN by season DJF / JJA / SON | 4.76 / 4.76 / 4.34 | 4.762 / 4.756 / 4.336 | ✓ |
| 34 | 9.3 | Refit 2025: Local frozen → refit; per-BA change Local / G-IN | 4.80 → 4.78; −0.9 / 0.1 | 4.797 → 4.776; −0.851 / 0.066 | ✓ |
| 35 | 9.4 | Unseen CQR 24 h mean / min | 89.2 / 78.6 | 89.17 / 78.65 | ✓ |
| 36 | 9.4 | In-region CQR 24 h mean / share; in-region 1 h share | 89.2 / 18.8; 25.0 | 89.24 / 18.75; 25.00 | ✓ |
| 37 | 9.4 | QR mean; SCP min (24 h) | 87.3; 71.4 | 87.26; 71.36 | ✓ |
| 38 | 9.4 | SCP-T4 mean 24 h | 85.3 | 85.27 | ✓ |
| 39 | 9.4 | CQR 2024 / 2025 | 89.5 / 88.8 | 89.49 / 88.84 | ✓ |
| 40 | 9.4 | ACI γ = 0.005: capped share; median IS vs CQR | 4.4; 88.55 vs 28.15 | 4.37; 88.55 vs 28.15 | ✓ |
| 41 | 9.4 | ACI-CQR-S 24 h mean / min / IS / width | 89.9 / 88.9 / 28.18 / 17.81 | 89.88 / 88.95 / 28.18 / 17.81 | ✓ |
| 42 | 9.4 | ACI-CQR-S 1 h min / IS; CQR 1 h IS | 89.8 / 7.40; 7.21 | 89.80 / 7.40; 7.21 | ✓ |
| 43 | 9.4 | Selected γ: 24 h; 1 h | 0.0005; 0.002, 0.005 | 0.0005 in all 6 folds; 0.005 in 5 folds, 0.002 in 1 | ✓ |
| 44 | 9.4 | γ = 0 control min / share | 79.3 / 20.8 | 79.28 / 20.83 | ✓ |
| 45 | 9.4 | SCP-R4 24 h mean / min / IS; 1 h min / IS | 89.2 / 88.4 / 31.65; 89.5 / 7.31 | 89.25 / 88.38 / 31.65; 89.54 / 7.31 | ✓ |
| 46 | 9.4 | Spatial CQR mean / min; ACI-S mean / min | 89.5 / 78.9; 89.9 / 88.9 | 89.54 / 78.92; 89.90 / 88.90 | ✓ |
| 47 | 9.4 | Conditional ACI-S DJF / JJA; top decile ACI-S / CQR | 88.3 / 90.0; 87.9 / 87.0 | 88.32 / 90.05; 87.95 / 87.00 | ✓ |
| 48 | 9.4 | Peak above upper bound CQR / ACI-S; peak APE zero-shot / BA-DA | 11.8 / 11.2; 4.76 / 3.69 | 11.76 / 11.23 (mean over BAs); 4.76 / 3.69 | ✓ |
| 49 | 11.1 | G-IN native: 24 h MCAR10 / 40; 1 h MCAR10 / 40 | 5.05 / 6.93; 1.84 / 4.04 | 5.05 / 6.93; 1.84 / 4.04 | ✓ |
| 50 | 11.1 | 1 h LOCF MCAR10; 168 h block LOCF / native / seasonal; augmented MCAR10 / 40 / clean; LRO MCAR10; minimum scored-hour coverage | 1.68; 2.42 / 1.95 / 1.87; 1.32 / 2.29 / 1.17; 1.93; 96.9 | 1.68; 2.42 / 1.95 / 1.87; 1.32 / 2.29 / 1.17; 1.93; 96.88 | ✓ |
| 51 | 11.2 | Ablation calendar / weekly / recent-lags; pool 20 / 10 / 5 (mean of draws) | 6.7 / 0.6 / 0.3; 4.81 / 4.87 / 4.97 | 6.716 / 0.649 / 0.267; 4.807 / 4.866 / 4.975 | ✓ |
| 52 | 4.2, 11.4, 12 | 48 BAs (21 E / 26 W / 1 ERCOT); 218 to 91,577 MW (419:1); 2,945,664 BA-hours; 0.55% flagged; excluded HST / WAUW / SEC / PSEI / SPA nMAE 24 h; G-IN fit 42.0 s; 1 h inference 164.20 µs; 1 h LRO trees 2,262–2,998 | as in text | 48 (21 / 26 / 1); 218 CHPD, 91,577 PJM, 419; 2,945,664; 0.552; 7.02 / 6.40 / 10.29 / 4.01 / 25.30; 42.03 s; 138.27 s / 842,112 = 164.2 µs; 2,262–2,998 | ✓ |

**Result: 52 of 52 consistent.** Each row covers one or more distinct quoted numbers; more than 120 individual values were checked.

---

## 4. Defects found

| ID | Severity | Location | Defect | Suggested fix |
|---|---|---|---|---|
| D1 | **Moderate** (unsupported claim) | `manuscript/sections/07_practice_limits.md` l.6 (rendered l.902), Practical implication 2 | "Small BAs benefit from pooling as much as large ones." The data contradict this. The pooling benefit (G-IN vs Local) is smaller for small BAs: at 24 h, median −0.8% for the 14 BAs under 1.5 GW against −1.7% for the larger ones (1 h: −7.6% vs −11.6%), and the correlation of the benefit with log size is −0.42 at 24 h. The zero-shot gap is also larger for smaller BAs (r = −0.25). §11.4 itself warns against extrapolating to very small systems. | Rephrase, e.g. "Small BAs also benefit from pooling, although less than large ones…", or delete the sentence. |
| D2 | **Moderate** (availability and reproducibility statements not yet true) | `08_backmatter.md` l.7 (Code availability), l.3 (Data availability); `02b_gap.md` l.17 (Contribution 4); `submission/declarations_template.docx`; `submission/cover_letter.docx` | (a) "A single command (`python -m src.run_all`) reproduces the full study". `run_all` `STAGES` omit `revision_experiments` (spatial, origins, excluded, ridge), `revision_evaluate`, `manuscript_numbers` and the builds, so Table 8, Tables S5–S9 and the spatial results are not produced by it. (b) "Derived predictions … are included in the code repository" and "All code, configurations, predictions and metrics are released". `results/predictions/*.parquet` (2.1 GB) and `results/predictions_compact/` (203 MB) are gitignored, so they are not in the repository; the Fig. 10 source data are among them. | Either add the revision stages to `run_all`, or reword to "the commands listed in README". Deposit predictions (at least `predictions_compact`) in the Zenodo archive and say so, or reword. |
| D3 | Minor | Manuscript Table 8, rows with "ACI-CQR (gamma=0.005, pre-registered)" (rendered l.641, 646, 651); labels come from `rev_calibration_summary.csv` via `src/generate_tables.py` | "pre-registered" contradicts the R10 / D16 change to "frozen in version control". Table 7 uses "frozen protocol" and γ, while Table 8 uses "gamma=". | Relabel to "ACI-CQR (γ = 0.005, frozen protocol)" and use γ throughout. |
| D4 | Minor (imprecise headline) | `00_front.md` l.15 (Abstract); `submission/highlights.txt` l.4 | The abstract says "Static conformal intervals under-covered by more than five points in 20.8–33.3% of systems, whether seen or unseen." That range is unseen-region **CQR** only. In-region CQR is 18.8–25.0%, SCP is 29–31%, and SCP-T4 at 24 h is 39.6%. The Conclusion correctly says "(CQR)". | Say "CQR intervals" and give a range covering both settings (e.g. "about 19–33%"). |
| D5 | Minor (format) | Discussion "Trade-offs (RQ5)" table (`05_discussion.md` l.17ff; rendered l.700) | This table has no number or caption; the DOCX has 13 tables but 12 captions. | Caption it (e.g. "Table 9. Trade-offs …") and renumber, or turn it into prose. |
| D6 | Minor (traceability) | `results/tables/table_manifest.csv` and file names | Table files and captions do not match manuscript numbering: `table_2_*` is Table 1, `table_3_*` is Table 2, `table_12_*` is Table 3, and `table_S10` is captioned "Table 10b". `qa_checks` labels its check "Table 2" while checking manuscript Table 1. R23 fixed this for figures only. | Renumber the table files and captions to match the manuscript. |
| D7 | Minor (consistency) | `06_robustness.md` l.86 ("roughly six hours"); `08_backmatter.md` l.7 ("six to seven hours"); `README.md` ("≈ 6–7 h + ≈ 2 h"); `src/run_all.py` docstring ("~3-4 h") | Four different runtime statements. | Harmonise them, e.g. "≈ 6–7 h main campaign + ≈ 2 h post-review analyses". |
| D8 | Minor (framing) | `submission/cover_letter.docx`, findings bullet 1 | "…(1.7% day-ahead when whole regions are held out), matching local models day-ahead and beating them intraday…". This omits the 8.0% hour-ahead spatial gap, and that the intraday advantage over local models disappears under spatial blocking (−0.8%, CI −3.1 to 1.8). | Add "and 8.0% hour-ahead; under spatial blocking it matches local models at both horizons". |
| D9 | Low (audit trail) | `results/logs/final.out` (15 MB, tracked) | The log ends with a pandas `TypeError` traceback in `robustness_analysis.evaluate` (l.177). The code was fixed (15:05:43) and the outputs regenerated (`missing_data_*`, `ablation_*` at 15:10:29), but the successful re-run is not logged. The 15 MB log is mostly one repeated list. | Re-run `python -m src.robustness_analysis evaluate`, keep the log, and truncate or replace `final.out`. |
| D10 | Low | `literature/verified_references.bib` l.389 | The "do not cite" entry `crossbuilding2026reliability` sits in a file named *verified*. It is not cited and not rendered. | Move it to a separate file, or delete it after the author decides on the in-text mention. |
| D11 | Low | §11.4 ("SPA, a 22 MW federal power-marketing area") | 22 MW is the test-period mean (`rev_excluded_bas.csv`: 21.9). `regions_all.csv` gives 52 MW for 2019–2025, the period used for the 200 MW criterion. | State the period ("22 MW mean in 2024–2025"). |

No critical defects were found. No number in the manuscript disagrees with the underlying CSVs.

---

## 5. Required manual actions before submission (author, not defects)

1. **Fill all `[AUTHOR ACTION]` placeholders** in `manuscript/sections/00_front.md` and `08_backmatter.md`, then rebuild with `python -m src.build_manuscript`:
   - author names, affiliations, ORCID and corresponding e-mail;
   - funding, competing interests, CRediT roles, generative-AI disclosure and acknowledgements.

   Do the same in `submission/cover_letter.docx` and `submission/declarations_template.docx` (via `src.build_submission_docs`).
2. **Archive the release and insert its link.** Mint a permanent repository and data archive (e.g. a Zenodo release) that includes code, metrics, tables and **predictions** (see D2). Insert the DOI or URL in the Data and Code availability statements and in the cover letter.
3. **Choose and add a code licence** (`LICENSE` file is absent; README and LICENSES carry an AUTHOR ACTION).
4. **Applied Sciences 2026 article** (doi:10.3390/app16167984, `02_related.md` l.21): obtain its author list from the publisher page and add a proper reference, or delete the sentence.
5. **Verify the 13 preprint or partially verified references** listed in check 7 against Crossref or publisher pages. Decide whether a preprint (hong2026benchmarking) should support the gap statement. Add missing DOIs for diebold1995comparing, hong2016gefcom2014 and tashman2000out. Resolve the pudl2026 version and DOI conflict.
6. **Confirm journal facts** (IJF Guide for Authors: reference style, highlights, length, review model, data/code policy; SCIE status via Clarivate MJL) and reformat the submission accordingly.
7. **Optional:** install Times New Roman and re-run `python -m src.generate_figures` and `python -m src.build_manuscript`, so the figures embed TNR rather than Liberation Serif. If a PDF is submitted, produce it from the final DOCX in Word, because the current PDF is a Chromium/Liberation Serif preview.
8. **Optional:** confirm the frozen-protocol commit (`2d794f4`, RESEARCH_STATUS) predates the first test-scoring timestamp. I did not run git, so I could not check this.
9. **Final pass.** After the fixes, re-run `python -m src.manuscript_numbers`, `python -m src.build_manuscript` and `python -m src.qa_checks`, then confirm 0 unresolved citations and 0 `[AUTHOR ACTION]` strings remain.

---

## 6. Artefacts produced by this audit

- `FINAL_QA_REPORT.md` (this file).
- `final_file_inventory.csv`: every project file except `data/raw/*.parquet`, `results/predictions*`, `results/models/*`, `__pycache__` and `.pytest_cache`, with size, category, a short description and the in-git status implied by `.gitignore`.
- `results/logs/qa_checks.json`, regenerated by `python3 -m src.qa_checks` during this audit: 15 Passed, 1 Partially verified (figure font), 2 Requires manual verification (citations, placeholders).

---

## Addendum: resolution of D1–D11 (by the PI after the audit, 2026-10-16 ~16:10 UTC)

*This addendum was written by the principal investigator, not the independent auditor. Verification is by re-running `python -m src.qa_checks`: all automated checks pass except "Requires manual verification" items (references, author placeholders) and the documented figure-font substitution.*

| Defect | Resolution |
|---|---|
| D1 | Practical implication 2 rewritten: "Small BAs also benefit from pooling, although less than large ones…". |
| D2 | `src/run_all.py` now runs every stage. This covers the post-review experiments and evaluation, number export, manuscript and supplement builds, submission documents and QA. Availability statements, contribution 4 and the cover letter now say the predictions come as a supplementary archive (`predictions_supplement.zip`) to be deposited with the code release [AUTHOR ACTION]. |
| D3 | Table 8 labels now use "γ = 0.005, frozen protocol" and "γ selected on source BAs". |
| D4 | Abstract and highlight now name CQR and give the range over both settings (in-region 24 h to unseen 1 h: 19–33%). |
| D5 | The RQ5 trade-off table is captioned and numbered (Table 9) through a new `TABLECAP` directive. |
| D6 | Table files are renumbered to match the manuscript (`table_01`–`table_12`, A1, S1–S10). The QA check is relabelled. |
| D7 | Runtime statements are harmonised: about 6–7 h main campaign plus about 2 h post-review, about 8–9 h for `run_all`. |
| D8 | The cover letter now reports the 8.0% hour-ahead spatial gap and that zero-shot matches local models at both horizons under spatial blocking. |
| D9 | The crash log `final.out` is deleted. `robustness_analysis evaluate` was re-run with its log kept (`results/logs/robustness_evaluate_rerun.log`, exit = 0). |
| D10 | The do-not-cite entry is moved to `literature/excluded_references.bib`. |
| D11 | SPA's demand is now given as the 2024–2025 mean, rendered from `rev_excluded_bas.csv`. |

**Status after the fixes.** No known defects remain. The manuscript is **not** submission-ready until the author actions in §5 are completed: placeholders, repository DOI and prediction deposit, licence, the Applied Sciences reference, verification of partially verified references, and journal-specific formatting.
