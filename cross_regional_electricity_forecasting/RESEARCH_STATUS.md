# Research Status

Last updated: 2026-10-16 (session 1)

## Completed
- Environment inspection (Python 3.13.16, Linux x86_64, 4 CPU, 15 GB RAM, no GPU; LibreOffice and
  pandoc available; Times New Roman NOT installed — Liberation Serif, metric-compatible, used for rendering).
- Network: PyPI, GitHub, AWS S3, GCS reachable; OPSD, Crossref, OpenAlex, arXiv, Zenodo, Hugging Face blocked.
- Data: PUDL v2026.10.0 EIA-930 downloaded and checksummed; 48 BAs selected; panel built.
- Literature review (58 entries) and gap analysis (subagent).
- Methodology and protocol written; hyper-parameter selection on validation weeks only.

## In progress
- Protocol freeze commit → full experimental campaign (E1–E7).

## Next actions
1. `python -m src.train_models point` → `adapt` → `refit`; `src.robustness_analysis missing|ablation`.
2. `src.evaluate_models`, `src.robustness_analysis evaluate`, tables, figures.
3. Statistical audit, manuscript, independent review, revision, journals, QA, package.

## Resume instructions
All stages are idempotent; re-run `python -m src.run_all --skip-download --from-stage N`.
Raw data are not in git: run `python -m src.download_data` first in a fresh container.
