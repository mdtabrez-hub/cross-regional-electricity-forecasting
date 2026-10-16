"""Create research_submission_package.zip (manuscript, code, configs, figures, tables, docs,
references, submission materials) and predictions_supplement.zip (compact test predictions).

Excludes raw data (re-downloadable, checksummed), full prediction files, model binaries, caches.
Usage: python -m src.package_submission
"""
from __future__ import annotations

import zipfile
from pathlib import Path

from .common import ROOT

INCLUDE = ["README.md", "PROJECT_PLAN.md", "DECISION_LOG.md", "RESEARCH_STATUS.md", "CLAIMS_AND_EVIDENCE.md",
           "FINAL_QA_REPORT.md", "final_file_inventory.csv", "LICENSES_AND_DATA_PROVENANCE.md",
           "requirements.txt", "environment.yml", ".gitignore", "configs", "src", "tests", "docs", "literature",
           "data/metadata", "data/processed/regions.csv", "data/processed/regions_all.csv", "data/raw/SHA256SUMS",
           "results/metrics", "results/tables", "results/logs", "results/manuscript_numbers.json", "figures",
           "manuscript", "submission"]
SKIP_SUFFIX = {".pyc", ".part", ".html"}
SKIP_PARTS = {"__pycache__", ".pytest_cache"}
SKIP_NAMES = {"campaign.out", "campaign2.out", "final.out"}  # very large stderr logs (warnings); summaries kept


def add(z, p: Path):
    if p.is_dir():
        for q in sorted(p.rglob("*")):
            if q.is_file():
                add(z, q)
        return
    if p.suffix in SKIP_SUFFIX or SKIP_PARTS & set(p.parts) or p.name in SKIP_NAMES:
        return
    z.write(p, Path("cross_regional_electricity_forecasting") / p.relative_to(ROOT))


def main():
    out = ROOT / "research_submission_package.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for item in INCLUDE:
            p = ROOT / item
            if p.exists():
                add(z, p)
        z.writestr("cross_regional_electricity_forecasting/PACKAGE_README.txt",
                   "Research submission package. Start with README.md (exact reproduction commands), then\n"
                   "manuscript/manuscript_final.docx, FINAL_QA_REPORT.md and RESEARCH_STATUS.md (author actions).\n"
                   "Raw data are not included: run `python -m src.download_data` (SHA-256 verified).\n"
                   "Compact test predictions are in the separate predictions_supplement.zip.\n")
    print(out, round(out.stat().st_size / 1e6, 1), "MB")
    sup = ROOT / "predictions_supplement.zip"
    with zipfile.ZipFile(sup, "w", zipfile.ZIP_STORED) as z:
        for f in sorted((ROOT / "results" / "predictions_compact").glob("*.parquet")):
            z.write(f, Path("predictions_compact") / f.name)
    print(sup, round(sup.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
