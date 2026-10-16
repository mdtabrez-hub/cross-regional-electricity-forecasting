#!/bin/bash
set -e
cd "$(dirname "$0")/../.."
python3 -u -m src.train_models point --h 6
python3 -u -m src.train_models adapt
python3 -u -m src.train_models refit
python3 -u -m src.robustness_analysis missing
python3 -u -m src.robustness_analysis ablation
echo CAMPAIGN_DONE
