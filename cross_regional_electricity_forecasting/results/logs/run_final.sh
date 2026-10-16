#!/bin/bash
set -e
cd "$(dirname "$0")/../.."
# evaluate_models already completed
python3 -u -m src.robustness_analysis evaluate
python3 -u -m src.revision_evaluate
python3 -u -m src.generate_tables
python3 -u -m src.generate_figures
python3 -u -m src.manuscript_numbers
echo FINAL_EVAL_DONE
