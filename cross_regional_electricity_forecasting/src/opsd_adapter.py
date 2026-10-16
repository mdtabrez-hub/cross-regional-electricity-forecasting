"""Convert an OPSD ``time_series_60min_singleindex.csv`` file to this project's panel format.

Not executed in the reported study (OPSD host unreachable from the execution
environment); provided for replication on European country-level data. Tested only on a
synthetic file (tests/test_opsd_adapter.py).

Column convention in OPSD: ``<CC>_load_actual_entsoe_transparency`` (MW, hourly mean),
``<CC>_load_forecast_entsoe_transparency`` (day-ahead forecast). Timestamps
``utc_timestamp`` mark the *start* of the interval; this adapter shifts them by +1 h to
the hour-ending convention used by EIA-930/PUDL. OPSD provides no imputation flags, so
``target`` equals the reported value and ``eval_ok`` marks non-missing positive values.
"""
from __future__ import annotations

import pandas as pd

from .preprocess_data import causal_clean

LOAD = "_load_actual_entsoe_transparency"
FCST = "_load_forecast_entsoe_transparency"

# Representative IANA zones for calendar features (holidays remain U.S.-federal in
# features.py; replace with national calendars for a European replication).
COUNTRY_TZ = {"AT": "Europe/Vienna", "BE": "Europe/Brussels", "BG": "Europe/Sofia", "CH": "Europe/Zurich",
              "CZ": "Europe/Prague", "DE": "Europe/Berlin", "DK": "Europe/Copenhagen", "EE": "Europe/Tallinn",
              "ES": "Europe/Madrid", "FI": "Europe/Helsinki", "FR": "Europe/Paris", "GB": "Europe/London",
              "GR": "Europe/Athens", "HR": "Europe/Zagreb", "HU": "Europe/Budapest", "IE": "Europe/Dublin",
              "IT": "Europe/Rome", "LT": "Europe/Vilnius", "LU": "Europe/Luxembourg", "LV": "Europe/Riga",
              "ME": "Europe/Podgorica", "NL": "Europe/Amsterdam", "NO": "Europe/Oslo", "PL": "Europe/Warsaw",
              "PT": "Europe/Lisbon", "RO": "Europe/Bucharest", "RS": "Europe/Belgrade", "SE": "Europe/Stockholm",
              "SI": "Europe/Ljubljana", "SK": "Europe/Bratislava"}


def opsd_to_panel(path, cfg: dict) -> tuple[pd.DataFrame, dict[str, str]]:
    raw = pd.read_csv(path, parse_dates=["utc_timestamp"])
    t = raw["utc_timestamp"].dt.tz_convert("UTC").dt.tz_localize(None) + pd.Timedelta("1h")
    # Only country-level columns (two-letter prefix) are used; sub-national/TSO columns skipped.
    countries = sorted({c.split("_")[0] for c in raw.columns if c.endswith(LOAD) and len(c.split("_")[0]) == 2})
    idx = pd.date_range(t.min(), t.max(), freq="h")
    parts, tz = [], {}
    for cc in countries:
        s = pd.Series(raw[cc + LOAD].to_numpy(float), index=t).groupby(level=0).first().reindex(idx)
        f = raw.get(cc + FCST)
        fc = (pd.Series(f.to_numpy(float), index=t).groupby(level=0).first().reindex(idx)
              if f is not None else pd.Series(float("nan"), index=idx))
        d = pd.DataFrame({"region": cc, "time_utc": idx, "reported": s.to_numpy(), "target": s.to_numpy(),
                          "ba_forecast": fc.to_numpy(), "imputation_code": None})
        d["eval_ok"] = d["target"].notna() & (d["target"] > 0)
        d["x_input"] = causal_clean(pd.Series(d["reported"].to_numpy()), cfg).to_numpy()
        parts.append(d)
        tz[cc] = COUNTRY_TZ.get(cc, "UTC")
    panel = pd.concat(parts, ignore_index=True)
    panel["region"] = panel["region"].astype("category")
    return panel, tz
