import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common import load_config  # noqa: E402
from src.opsd_adapter import opsd_to_panel  # noqa: E402


def test_opsd_adapter_synthetic(tmp_path):
    t = pd.date_range("2019-01-01", periods=72, freq="h", tz="UTC")
    df = pd.DataFrame({
        "utc_timestamp": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cet_cest_timestamp": t.tz_convert("Europe/Berlin").strftime("%Y-%m-%dT%H:%M:%S%z"),
        "DE_load_actual_entsoe_transparency": np.linspace(50000, 60000, 72),
        "DE_load_forecast_entsoe_transparency": np.linspace(50000, 60000, 72),
        "FR_load_actual_entsoe_transparency": np.r_[np.full(71, 60000.0), np.nan],
        "DE_50hertz_load_actual_entsoe_transparency": 1.0,
    })
    p = tmp_path / "opsd.csv"
    df.to_csv(p, index=False)
    panel, tz = opsd_to_panel(p, load_config())
    assert set(panel.region.astype(str)) == {"DE", "FR"}
    assert tz["DE"] == "Europe/Berlin"
    de = panel[panel.region == "DE"]
    assert de.time_utc.iloc[0] == pd.Timestamp("2019-01-01 01:00")  # shifted to hour-ending
    assert panel[panel.region == "FR"].eval_ok.sum() == 71
