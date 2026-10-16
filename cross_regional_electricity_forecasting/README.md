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

Requires Python 3.13 and ~8 GB RAM; full run ≈ 3–4 h on 4 CPU cores.

```bash
cd cross_regional_electricity_forecasting
python -m pip install -r requirements.txt
python -m pytest -q tests            # unit tests
python -m src.run_all                # full pipeline (downloads ~95 MB from PUDL S3)
python -m src.build_manuscript       # regenerate manuscript .docx (+ .pdf if LibreOffice present)
```

Individual stages: see `src/run_all.py` (`STAGES`). Raw files are verified by SHA-256
(`configs/experiment.yaml`, `data/raw/SHA256SUMS`).

## Status

See `RESEARCH_STATUS.md` (live status), `CLAIMS_AND_EVIDENCE.md` (claim → evidence map)
and `FINAL_QA_REPORT.md`.

## Licence

Code: MIT (placeholder pending author confirmation). Data: EIA-930 is a U.S. Government
work (public domain); PUDL outputs are CC-BY-4.0 — cite Catalyst Cooperative / PUDL and EIA.
