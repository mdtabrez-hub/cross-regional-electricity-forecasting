#!/bin/bash
set -e
cd "$(dirname "$0")/../.."
python3 -u -m src.evaluate_models
python3 -u -m src.robustness_analysis evaluate
python3 -u -m src.generate_tables
python3 -u -m src.generate_figures
python3 -u -m src.manuscript_numbers
echo POST_DONE
