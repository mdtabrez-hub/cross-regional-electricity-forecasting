# Project Plan

**Working title:** Forecasting Electricity Demand in Unseen Regions: A Leave-Regions-Out
Benchmark of Global Models, Limited-Data Adaptation and Conformal Calibration on 48 U.S.
Balancing Authorities (final title set after results; see `manuscript/`).

## Agents (executed as roles; Agent 2 and the reviewer/QA roles run as independent subagents)

| Agent | Role | Main outputs |
|---|---|---|
| 1 PI | coordination, decisions, integration | PROJECT_PLAN, DECISION_LOG, RESEARCH_STATUS, CLAIMS_AND_EVIDENCE |
| 2 Literature | literature, gap | `literature/*` (subagent) |
| 3 Data | acquisition, QA, provenance | `data/metadata/*`, `src/download_data.py`, `src/preprocess_data.py`, `src/inspect_data.py` |
| 4 Methodology | design, frozen protocol | `docs/methodology_specification.md`, `docs/experimental_protocol.md`, `docs/model_selection_criteria.md` |
| 5 Engineer | implementation, tests, runs | `src/*`, `tests/*`, `results/*` |
| 6 Auditor | statistics, robustness | `docs/statistical_audit.md`, `docs/robustness_report.md`, `docs/limitations_register.md` |
| 7 Visualisation | figures/tables | `figures/*`, `results/tables/*`, manifests |
| 8 Writer | manuscript | `manuscript/manuscript_final.docx/.pdf` |
| 9 Reviewer | independent critical review | `manuscript/independent_review_report.md`, `reviewer_comments.csv` (subagent) |
| 10 Revision | revision, response | `manuscript/revision_matrix.csv`, `revised_manuscript.docx`, response template |
| 11 Journals | journal selection | `submission/journal_*` (subagent) |
| 12 QA | final audit | `FINAL_QA_REPORT.md`, `final_file_inventory.csv` |

## Milestones

1. Environment inspection, data access resolution — done (D2)
2. Literature review and gap validation — done
3. Data acquisition and validation — done
4. Protocol freeze — commit before test scoring
5. Pilot (validation-only grid) → full campaign (E1–E7)
6. Evaluation, statistical audit, figures, tables
7. Manuscript → independent review → revision
8. Journal selection, final QA, submission package
