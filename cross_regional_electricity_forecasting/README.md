# Cross-Regional Electricity-Demand Forecasting Under Distribution Shift

Reproducible benchmark of hourly electricity-demand forecasting for **balancing
authorities (BAs) never seen during training**, limited target-data adaptation, temporal
drift, missing inputs, and conformal calibration of prediction intervals, using
**U.S. EIA Form 930** data for 48 BAs (2019–2025) as published by Catalyst Cooperative's
PUDL project (release v2026.10.0).

> The project brief named Open Power System Data (OPSD) as the primary dataset. OPSD hosts
> were not reachable from the execution environment; see `DECISION_LOG.md` (D2) and
> `LICENSES_AND_DATA_PROVENANCE.md`. `src/opsd_adapter.py` provides an untested-on-real-data
> replication path for European country-level data.

## Layout

```
configs/experiment.yaml      frozen experimental configuration
docs/                        methodology, frozen protocol, audit and robustness reports
literature/                  literature matrix, review, gap analysis, BibTeX
data/metadata/               inventory, quality report, dataset metadata (raw data not committed)
src/                         pipeline (download → preprocess → train → evaluate → figures/tables)
tests/                       pytest suite (leakage, metrics, conformal, adapters)
results/{metrics,tables,logs,predictions}/
figures/                     PNG (600 dpi) + vector PDF, figure_manifest.csv
manuscript/                  manuscript (.docx/.pdf), internal review, revision matrix
submission/                  journal comparison, checklist, cover letter, statements
```

## Reproduce

Requires Python 3.13, ~8 GB RAM, pandoc ≥ 3.1 and (for the PDF) a Chromium/Chrome binary.
Full run ≈ 6–7 h wall-clock on 4 CPU cores (main campaign) + ≈ 2 h (post-review analyses); `python -m src.run_all` runs everything.

```bash
cd cross_regional_electricity_forecasting
python -m pip install -r requirements.txt
python -m pytest -q tests                      # 15 unit tests (leakage, metrics, conformal, adapters)
python -m src.run_all                          # download → preprocess → train → evaluate → tables/figures
python -m src.revision_experiments ridge       # post-review analyses (DECISION_LOG D14–D16)
python -m src.revision_experiments excluded
python -m src.revision_experiments origins
python -m src.revision_experiments spatial
python -m src.revision_evaluate
python -m src.robustness_analysis evaluate && python -m src.generate_tables && python -m src.generate_figures
python -m src.manuscript_numbers               # every number quoted in the manuscript
python -m src.build_manuscript                 # manuscript_final.docx/.pdf
python -m src.build_manuscript --sections-dir manuscript/supplement --rendered manuscript/supplement_rendered.md --out manuscript/supplementary_material.docx
python -m src.build_submission_docs            # cover letter, highlights, declarations, response template
python -m src.qa_checks                        # automated consistency checks
```

Raw files are verified by SHA-256 (`configs/experiment.yaml`, `data/raw/SHA256SUMS`). Note that the
PUDL `stable/` alias moves with new releases; use the versioned archive if checksums no longer match.
The Chromium path used for the PDF is set in `src/build_manuscript.py` (`CHROME`).

## Status

See `RESEARCH_STATUS.md` (live status), `CLAIMS_AND_EVIDENCE.md` (claim → evidence map)
and `FINAL_QA_REPORT.md`.

## Licence

Code: no licence chosen yet [AUTHOR ACTION: add a LICENSE file, e.g. MIT]. Data: EIA-930 is a U.S. Government
work (public domain); PUDL outputs are CC-BY-4.0 — cite Catalyst Cooperative / PUDL and EIA.
