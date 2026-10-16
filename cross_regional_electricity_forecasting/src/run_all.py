"""Run the complete pipeline end to end.

    python -m src.run_all            # full study (~3-4 h on 4 CPU cores)
    python -m src.run_all --skip-download
Each stage is idempotent and writes its outputs under data/ and results/.
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from .common import LOG_DIR, environment_record, save_json

STAGES = [
    ["src.download_data"],
    ["src.preprocess_data"],
    ["src.inspect_data"],
    ["src.train_models", "select"],
    ["src.train_models", "point"],
    ["src.train_models", "adapt"],
    ["src.train_models", "refit"],
    ["src.robustness_analysis", "missing"],
    ["src.robustness_analysis", "ablation"],
    ["src.evaluate_models"],
    ["src.robustness_analysis", "evaluate"],
    ["src.generate_tables"],
    ["src.generate_figures"],
]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-download", action="store_true")
    ap.add_argument("--from-stage", type=int, default=0)
    a = ap.parse_args(argv)
    save_json(environment_record(), LOG_DIR / "environment.json")
    subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"], check=True)
    for i, st in enumerate(STAGES):
        if i < a.from_stage or (a.skip_download and st[0] == "src.download_data"):
            continue
        print(f"[run_all] stage {i}: {' '.join(st)}", flush=True)
        subprocess.run([sys.executable, "-m", *st], check=True)


if __name__ == "__main__":
    main()
