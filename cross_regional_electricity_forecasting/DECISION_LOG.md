# Decision Log

| # | Date (UTC) | Decision | Rationale / evidence | Agent |
|---|---|---|---|---|
| D1 | 2026-10-16 | Work on branch `claude/happy-cori-waxjb8`; project in `cross_regional_electricity_forecasting/` | Repository contained only a stub README | PI |
| D2 | 2026-10-16 | **Primary dataset changed from OPSD to U.S. EIA-930 (via PUDL v2026.10.0).** | `data.open-power-system-data.org` and `open-power-system-data.org` refused by the environment's egress proxy (HTTP 403 on CONNECT) and not resolvable by the server-side fetch tool (ENOTFOUND). Mirrors (Hugging Face, data.pypsa.org, Zenodo) also blocked. PUDL's public S3 bucket is reachable, versioned, documented, CC-BY-4.0 (EIA source: public domain), covers 72 BAs 2015-07→2026-09 at hourly resolution, includes per-hour quality flags and the BAs' own day-ahead forecasts. OPSD's last time-series release (2020-10-06) ends in 2020, so EIA-930 also gives more recent and longer test periods. An OPSD loader is retained (`src/opsd_adapter.py`) for replication when network access permits. | PI, Data |
| D3 | 2026-10-16 | Use PUDL `out_` table (screened/imputed demand + imputation codes) for labels; causal screen for inputs | PUDL screening uses two-sided windows → would leak future information if used for inputs; used only to define clean evaluation hours | Data, Methodology |
| D4 | 2026-10-16 | Study window 2019–2025; 48 BAs by pre-specified criteria | Post-2018 EIA-930 data quality is better (subregion reporting, UTC fixes); 2026 incomplete | Data |
| D5 | 2026-10-16 | Instance normalisation by trailing 168-h mean | Enables a single global model across BAs spanning 0.2–92 GW and zero-shot transfer without target statistics | Methodology |
| D6 | 2026-10-16 | No neural/foundation models | CPU-only; Hugging Face blocked (weights unavailable); documented as limitation | PI |
| D7 | 2026-10-16 | Literature verification via web-search snippets of publisher pages only | Crossref/OpenAlex/Semantic Scholar/arXiv APIs blocked; Scopus/WoS not accessible | Literature |
| D8 | 2026-10-16 | Protocol frozen (docs/methodology_specification.md, docs/experimental_protocol.md) prior to test scoring | Pre-registration against test-set reuse | PI |
