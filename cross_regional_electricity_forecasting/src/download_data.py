"""Download the EIA-930 tables published by Catalyst Cooperative's PUDL project.

Primary source (used in this study): PUDL stable release v2026.10.0 on the public
AWS Open Data bucket ``pudl.catalyst.coop``. The original data are U.S. EIA Form 930
(U.S. Government work, public domain); PUDL outputs are licensed CC-BY-4.0.

Optional source: Open Power System Data (OPSD) time-series package. The OPSD host
was not reachable from the environment used for this study (network policy), so the
OPSD replication path (``--opsd``) is provided but was not executed. See
LICENSES_AND_DATA_PROVENANCE.md.

Usage:
    python -m src.download_data            # PUDL EIA-930 tables (required)
    python -m src.download_data --opsd     # additionally try OPSD 2020-10-06 60-min file
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import requests

from .common import DATA_RAW, load_config, save_json, DATA_META

OPSD_URL = "https://data.open-power-system-data.org/time_series/2020-10-06/time_series_60min_singleindex.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, dest: Path, timeout: int = 600) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with open(tmp, "wb") as fh:
            for chunk in r.iter_content(1 << 20):
                fh.write(chunk)
    tmp.replace(dest)


def download_pudl(cfg: dict, force: bool = False) -> dict:
    base = cfg["data"]["pudl_base_url"]
    record = {}
    for fname, expected in cfg["data"]["files"].items():
        dest = DATA_RAW / fname
        if force or not dest.exists():
            print(f"downloading {fname}")
            fetch(f"{base}/{fname}", dest)
        digest = sha256(dest)
        if expected and digest != expected:
            raise RuntimeError(
                f"SHA-256 mismatch for {fname}: expected {expected}, got {digest}. "
                "The PUDL 'stable' alias may have moved to a newer release; pin the "
                "versioned Zenodo archive (DOI in dataset_metadata.json) instead."
            )
        record[fname] = {"url": f"{base}/{fname}", "sha256": digest, "bytes": dest.stat().st_size}
    return record


def download_opsd() -> dict:
    dest = DATA_RAW / "opsd" / "time_series_60min_singleindex.csv"
    try:
        fetch(OPSD_URL, dest)
    except Exception as exc:  # network policy or host unavailable
        print(f"OPSD download failed: {exc}", file=sys.stderr)
        return {"url": OPSD_URL, "status": f"failed: {type(exc).__name__}"}
    return {"url": OPSD_URL, "status": "ok", "sha256": sha256(dest)}


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--opsd", action="store_true")
    args = ap.parse_args(argv)
    cfg = load_config()
    rec = {"pudl": download_pudl(cfg, args.force)}
    if args.opsd:
        rec["opsd"] = download_opsd()
    save_json(rec, DATA_META / "download_record.json")
    print(rec)


if __name__ == "__main__":
    main()
