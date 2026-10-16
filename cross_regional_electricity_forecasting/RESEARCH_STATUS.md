# Research Status

Last updated: 2026-10-16 (session 1, end)

## Completed
- Environment inspection; network constraints documented (OPSD, Crossref, Hugging Face blocked).
- Data: PUDL v2026.10.0 EIA-930, 48 BAs, 2019–2025; quality report, metadata, provenance.
- Literature: 66-entry matrix (web-search verification only), gap analysis, related work; revision pass.
- Frozen protocol (git commit 2d794f4) → full campaign E1–E7 (h = 1, 6, 24); amendments D9–D13 logged.
- Evaluation, statistics (Wilcoxon/Holm, block bootstrap, cluster bootstrap), 13 figures, 12 main + 10 supplementary tables.
- Manuscript (DOCX/PDF), supplementary material, simulated internal review (Major revision), revision with new
  experiments (spatial blocking, source-only ACI, multi-origin adaptation, excluded BAs; D14–D16), revision matrix,
  response template (labelled simulated), journal selection (IJF primary), cover letter, highlights, declarations.
- Automated QA checks (src/qa_checks.py) passing except items requiring manual verification.

## Requires author action before submission
- Author names, affiliations, ORCID, funding, COI, CRediT, generative-AI disclosure.
- Mint repository DOI (e.g. Zenodo) and insert in data/code availability statements.
- Verify partially verified references (literature_matrix.csv verification_status) via Crossref/publisher pages;
  complete the Applied Sciences 2026 reference (authors unknown) or remove the sentence.
- Confirm journal facts (SCIE status, APC, word limits) on official pages; reformat for the chosen journal.
- Optional: install Times New Roman and re-run `python -m src.generate_figures` to embed TNR in figures.

## Not done (future work)
- OPSD/ENTSO-E European replication; weather covariates; statistical/neural/foundation-model baselines;
  nested tuning; 2026 confirmation hold-out; regularised adaptation; aggregated ACI.

## Resume instructions
All stages idempotent: `python -m src.run_all --skip-download --from-stage N`; revision experiments:
`python -m src.revision_experiments {ridge,excluded,origins,spatial}` then `python -m src.revision_evaluate`.
Raw data are not in git: run `python -m src.download_data` first in a fresh container.
