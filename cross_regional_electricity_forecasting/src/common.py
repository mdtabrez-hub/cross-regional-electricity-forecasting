"""Shared paths, configuration loading, logging and reproducibility helpers."""
from __future__ import annotations

import json
import logging
import os
import platform
import random
import resource
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_META = ROOT / "data" / "metadata"
RESULTS = ROOT / "results"
PRED_DIR = RESULTS / "predictions"
METRIC_DIR = RESULTS / "metrics"
LOG_DIR = RESULTS / "logs"
TABLE_DIR = RESULTS / "tables"
FIG_DIR = ROOT / "figures"
CONFIG_PATH = ROOT / "configs" / "experiment.yaml"

for _d in (DATA_RAW, DATA_PROCESSED, DATA_META, PRED_DIR, METRIC_DIR, LOG_DIR, TABLE_DIR, FIG_DIR):
    _d.mkdir(parents=True, exist_ok=True)


def load_config(path: Path | str = CONFIG_PATH) -> dict:
    with open(path) as fh:
        return yaml.safe_load(fh)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        fh = logging.FileHandler(LOG_DIR / f"{name}.log")
        fh.setFormatter(fmt)
        logger.addHandler(sh)
        logger.addHandler(fh)
    return logger


def peak_rss_mb() -> float:
    """Peak resident set size of this process in MB (Linux reports KB)."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


@contextmanager
def timer():
    t = {"start": time.perf_counter()}
    yield t
    t["seconds"] = time.perf_counter() - t["start"]


def environment_record() -> dict:
    import importlib

    pkgs = {}
    for p in ["numpy", "pandas", "scipy", "sklearn", "lightgbm", "statsmodels", "matplotlib", "docx", "pyarrow", "yaml"]:
        try:
            pkgs[p] = importlib.import_module(p).__version__
        except Exception:  # pragma: no cover - record absence
            pkgs[p] = None
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "packages": pkgs,
    }


def save_json(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2, default=str)
