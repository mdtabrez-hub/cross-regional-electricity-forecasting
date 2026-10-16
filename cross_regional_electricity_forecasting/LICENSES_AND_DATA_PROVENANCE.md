# Licences and Data Provenance

## Data used

| Item | Value |
|---|---|
| Dataset | U.S. EIA Form 930 "Hourly and Daily Balancing Authority Operations Report", as processed by the Public Utility Data Liberation (PUDL) project, Catalyst Cooperative |
| Release | PUDL `v2026.10.0` (datapackage `created` 2026-10-14T17:10:33Z; S3 marker `stable-2026-10-14-1552-90561c620-v2026-10-0`) |
| Retrieved | 2026-10-16 from `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/` |
| Tables | `out_eia930__hourly_operations`, `core_eia930__hourly_operations` (inspection only), `core_eia__codes_balancing_authorities`, `core_pudl__codes_imputation_reasons`, `pudl_parquet_datapackage.json` |
| Checksums | `data/raw/SHA256SUMS` |
| PUDL EIA-930 archive DOI (as listed in the PUDL datapackage) | 10.5281/zenodo.22525116 (concept DOI 10.5281/zenodo.10840077) |
| Original licence | U.S. Government work, public domain (as stated in PUDL metadata) |
| PUDL licence | Creative Commons Attribution 4.0 (CC-BY-4.0) |
| Attribution | Catalyst Cooperative, PUDL; U.S. Energy Information Administration |

Redistribution: CC-BY-4.0 permits redistribution with attribution. Nevertheless, raw files
(~95 MB) are **not** included in the submission archive; `src/download_data.py`
re-downloads and verifies them by SHA-256. Note that the `stable/` alias moves with new
PUDL releases; the checksum check fails loudly if the content changes, in which case the
versioned Zenodo archive above should be used.

## Data originally specified but not used

Open Power System Data (OPSD) time series (`https://data.open-power-system-data.org/time_series/`).
Not accessible from the execution environment (egress proxy refusal; DNS failure from the
server-side fetch tool), 2026-10-16. Licence information for OPSD could therefore not be
re-verified in this session. `src/opsd_adapter.py` converts the OPSD 60-min single-index
file into this project's panel format; it was unit-tested on a synthetic file only.

## Software

All dependencies are open source (see `requirements.txt`). Project code: MIT licence
(`LICENSE`), placeholder pending author confirmation.
