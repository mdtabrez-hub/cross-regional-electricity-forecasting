# Journal Selection Report

**Manuscript:** Cross-regional hourly electricity-demand forecasting benchmark: 48 U.S. balancing authorities (EIA-930 via PUDL, 2019–2025). It covers leave-regions-out evaluation, limited target-data adaptation, temporal drift and refit, probabilistic calibration under shift (QR, split conformal, CQR, ACI), missing-data robustness, a comparison with operator day-ahead forecasts, and open code and data. Length is about 8,000–10,000 words with about 13 figures.
**Prepared by:** Agent 11 (journal selection) | **Date accessed / evidence date:** 2026-10-16
**Companion files:** `journal_comparison.csv` (all fields, scores and sources) and `submission_checklist.md` (checklist for the primary journal).

> These scores help with the decision. They are **not** estimates of the chance of acceptance, and no acceptance is implied or guaranteed.

---

## 1. Method

1. **Candidates.** I evaluated 15 journals: the 14 suggested ones plus SEGAN, IJEPES and EPSR, which were already on the list. Scientific Data was assessed and then excluded (see §5).
2. **Evidence collection.** All evidence came from WebSearch run on 2026-10-16. Most searches were restricted to official domains: sciencedirect.com, elsevier.com, forecasters.org, ieee-pes.org, cmte.ieee.org, open.ieee.org, ieeexplore.ieee.org, mdpi.com, springeropen.com/link.springer.com, ietresearch.onlinelibrary.wiley.com, cambridge.org, nature.com and scopus.com. **WebFetch of sciencedirect.com failed (DNS error, ENOTFOUND)**, so I could not open any page in full. **Every fact in this report comes from search-result snippets or summaries of official pages and should be treated as snippet-level evidence.**
3. **Rules applied.**
   - I did not invent any impact factor, quartile, APC, review time, acceptance rate or indexing status.
   - Anything not seen on an official or authoritative page is marked "Not verified in this session".
   - I did not infer SCIE coverage from Scopus coverage, or from an impact factor shown on a publisher page.
   - Third-party aggregators (Manusights, SciRev, journalmetrics.org, Editage, LetPub, researcher.life) were noted but never used as the basis for a "verified" field.
4. **Scoring.** Each journal got a 1–5 score on six criteria, using these weights:

   | Criterion | Weight |
   |---|---|
   | Scope | 30% |
   | Scientific quality and indexing suitability | 25% |
   | Methodological / article-type fit | 15% |
   | Review-time evidence | 15% |
   | Cost and accessibility | 10% |
   | Editorial transparency | 5% |

   Weighted total = Σ(score × weight), with a maximum of 5.00. The reason for each score is in the CSV.

## 2. Evidence limitations (read before relying on any number)

- **No Clarivate Master Journal List (MJL) record appeared for any candidate.** SCIE status is therefore "Not verified" for every journal. Impact factors shown on publisher pages suggest JCR coverage but do not show SCIE versus SSCI versus ESCI.
  - IJF in particular may be listed in SSCI and/or SCIE. **Check mjl.clarivate.com (ISSN 0169-2070)** if your institution requires SCIE.
  - The ScienceDirect indexing list for **Energy and AI** shows **ESCI** (Emerging Sources Citation Index), not SCIE.
- **Scopus source pages appeared only for Energy and AI** (CiteScore 2025: 16.3) and, unreliably, for SEGAN. For the other Elsevier titles, CiteScore values appear on ScienceDirect, which strongly suggests Scopus coverage, but I did not see the Scopus source page.
- **Metrics conflict between page snapshots.** For example, IJF shows IF 7.1 on its Insights page and IF 5.7 on an older journal-page snapshot. Where they differed, I quoted the Insights-page value and listed the alternative. The snippets do not show the date of each page.
- **Quartiles:** none verified from JCR or Scopus directly.
- **Acceptance rates:** none officially disclosed among the candidates I could check. The Energies stats page has a rejection-rate section, but its figure was not retrieved.
- **IEEE review times:** only process targets were found, not measured averages.
- **IJF data/code policy, conflicting sources:**
  - The IIF website says that since July 2023, sharing data and code is mandatory unless the EIC accepts a justification, and acceptance depends on passing a reproducibility check.
  - The Guide for Authors snippet says data are expected and code is encouraged.
  - Plan for the stricter policy.

## 3. Ranked table

Review times are as reported on the official pages: first decision (1st dec.), submission to acceptance (sub→acc.), and acceptance to publication (acc.→pub.).

| Rank | Journal | Scope (30%) | Quality / indexing (25%) | Method fit (15%) | Review evidence (15%) | Cost (10%) | Transparency (5%) | **Weighted** | Key verified facts (snippet level, 2026-10-16) | Role |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | International Journal of Forecasting (Elsevier/IIF) | 5 | 4 | 5 | 2 | 5 | 5 | **4.30** | IF 7.1, CiteScore 17.1 (Insights); 1st dec. 9 d; sub→acc. 296 d (Insights) / 318 d; APC USD 3,500 (hybrid); abstract 100–150 words; reproducibility check | **PRIMARY** |
| 2 | Applied Energy (Elsevier) | 4 | 5 | 4 | 4 | 4 | 4 | **4.25** | IF 11.0, CiteScore 20.1; 1st dec. 3 d; sub→acc. 130 d; acc.→online 10 d; APC USD 4,210; abstract ≤250 words; highlights required | **BACKUP 1** |
| 3 | Energy and AI (Elsevier) | 4 | 4 | 4 | 5 | 2 | 4 | **3.95** | IF 9.6; CiteScore 16.3 (Scopus); listed ESCI; 1st dec. 4 d; sub→acc. 95 d; acc.→pub. 5 d; fully OA, APC USD 3,990 (4,270 on another page) | **BACKUP 2** |
| 4 | IEEE Transactions on Power Systems | 4 | 5 | 2 | 3 | 5 | 4 | **3.90** | IF 8.7 (PES/Xplore); 10-page submission limit; ~12-week review process (target); hybrid OA USD 2,800; overlength USD 250/page beyond 12 pages | **AMBITIOUS** |
| 5 | Sustainable Energy, Grids and Networks | 4 | 3 | 4 | 3 | 3 | 4 | 3.50 | IF 5.6, CiteScore 9.2; 1st dec. 9 d vs 76 d (conflicting); APC USD 2,780–2,940 | Alternative |
| 6 | Int. J. Electrical Power & Energy Systems | 3 | 4 | 4 | 4 | 2 | 4 | 3.50 | IF 5.0; 1st dec. 11 d; sub→acc. 186 d; fully gold OA since 2024, APC USD 4,190 | Alternative |
| 7 | Energies (MDPI) | 3 | 3 | 4 | 5 | 3 | 4 | 3.50 | IF 3.9; 1st dec. 16.7 d (median, H1 2026); acc.→pub. 3.5 d; APC CHF 2,600; COPE member | Fast fallback |
| 8 | Electric Power Systems Research | 3 | 3 | 4 | 4 | 3 | 4 | 3.35 | 1st dec. 1 d; sub→acc. 148 d; APC USD 2,870; scope requires power-system context | Alternative |
| 9 | Energy (Elsevier) | 3 | 3 | 2 | 4 | 5 | 4 | 3.25 | Full-length articles 5,000–7,000 words; 1st dec. 23 d; sub→acc. 149 d; acc.→online 3 d; hybrid, APC USD 4,050 | Not preferred (length) |
| 10 | IEEE Open Access J. Power & Energy | 3 | 3 | 2 | 4 | 3 | 3 | 3.00 | IF 2.8 (PES page); 10-page limit; 10-week target from submission to publication; official APC not seen | Short-version fallback |
| 11 | Energy Informatics (SpringerOpen) | 4 | 2 | 4 | 1 | 4 | 3 | 3.00 | APC USD 1,490–1,540 (conflicting); SJR 0.568; no review-time data | Low-cost fallback |
| 12 | IET Generation, Transmission & Distribution | 3 | 3 | 4 | 1 | 3 | 4 | 2.90 | Fully OA, APC USD 3,000; no review-time data | Not preferred |
| 13 | IEEE Transactions on Smart Grid | 2 | 3 | 2 | 2 | 3 | 3 | 2.40 | PES page lists "transmission system load and price forecast" as out of scope | Not recommended |
| 14 | Data-Centric Engineering (CUP) | 2 | 2 | 4 | 1 | 3 | 3 | 2.30 | Energy not named in scope; APC only from DOAJ (secondary) | Not recommended |
| – | Scientific Data (Springer Nature) | 1 | – | – | – | – | – | Excluded | Publishes Data Descriptors, not hypothesis-driven or benchmarking research | Excluded |

## 4. Recommendation

The scores at the top are close: IJF 4.30 and Applied Energy 4.25. Treat the choice between them as a judgement call driven by timeline tolerance.

**Primary: International Journal of Forecasting.**
- **Best scope fit.** The paper's main contribution is about *forecast evaluation*: generalisation to unseen regions, calibration under geographic and temporal shift, adaptation curves, drift, and benchmarking against operational forecasts. That is IJF's core subject. IIF calls for papers in 2026 explicitly list energy and utilities forecasting, reproducible workflows and open-source forecasting.
- **Open code and data become an advantage.** IJF's mandatory sharing and reproducibility check (per the IIF site) align with the open-code, open-data design, so the reproducibility package counts in the paper's favour.
- **Length fits.** A 2020 IIF editorial (dated) says there is no general page limit, which suits 8–10k words and 13 figures. This needs confirming in the current Guide.
- **No-fee route.** IJF is hybrid, so a subscription route with no publication fee exists. This matters because funding is unknown.
- **Trade-off: time.** The official Insights page reports 296 days from submission to acceptance (318 days on another snapshot) and 168 days of review.

**Backup 1: Applied Energy.**
- Forecasting models, AI in energy and data analytics are explicitly listed topics.
- Highest impact metrics among the candidates (IF 11.0).
- Much faster official timeline: 3 days to first decision, 130 days to acceptance, 10 days to online publication. It appears to offer a no-fee hybrid route.
- Choose this as the primary instead if the timeline matters more than venue fit.
- Risks: early desk rejection if the work is not framed as applied and energy-system relevant; a strict 250-word abstract; required highlights.

**Backup 2: Energy and AI.**
- Strong energy-plus-ML fit and the fastest official timeline (4 / 95 / 5 days).
- Caveats: fully OA with a mandatory APC of about USD 4k, and the indexing list shows **ESCI, not SCIE**. That matters if the authors' institution requires SCIE.

**Ambitious: IEEE Transactions on Power Systems.**
- IF 8.7, and the TPWRS scope page explicitly includes system-level load forecasting.
- Main obstacle: the strict **10-page submission limit**, under which papers are returned without review. This would require cutting the study to its central results (leave-regions-out generalisation, calibration under shift and the operator comparison) and moving the rest to supplementary material.

If all four fail, the alternatives are SEGAN, IJEPES or EPSR. Energies is the fast fallback.

## 5. Exclusions and scope mismatches

- **Scientific Data: excluded.** Its official aims and scope and its referee guidance say it publishes Data Descriptors and data-policy articles. It does not publish research testing hypotheses or "extensive analyses aimed at providing new scientific insights". This manuscript is a benchmarking and analysis study and reuses an existing public dataset (EIA-930/PUDL). A Data Descriptor would only make sense for a separately curated new dataset.
- **IEEE Transactions on Smart Grid:** transmission-level load forecasting appears in its out-of-scope list.
- **Energy (Elsevier):** its 5,000–7,000-word full-length limit conflicts with an 8–10k-word manuscript.
- **Data-Centric Engineering:** energy is not named in its scope; the fit is weak.
- **Electric Power Systems Research:** price- or market-focused work is out of scope, and power-system relevance must be explicit.

## 6. Risks

1. **IJF scope framing.** IJF reviewers may see a large applied benchmark as "just an application". Lead with the generalisable methodological findings:
   - an evaluation protocol for unseen-region transfer;
   - the behaviour of conformal and ACI coverage under geographic and temporal shift;
   - adaptation-data curves;
   - practical guidance for forecasters.
2. **IJF reproducibility gate.** Acceptance depends on the EIC reproducing the results. The code must run end to end from public data:
   - pin the PUDL version and environment;
   - provide seeds;
   - state expected runtimes and hardware;
   - document any results that need heavy compute.
   A "minor concerns" outcome means the reproduced numbers differ from those in the paper.
3. **Timeline.** About 10 months to acceptance at IJF, based on official averages. Revisions add more time.
4. **Desk rejection.**
   - Applied Energy: a third-party source (not verified) says many submissions are desk-rejected quickly.
   - IJF: a third-party source (SciRev, editor-provided, date unclear) reports 30% immediate rejection.
5. **Preprints.**
   - Elsevier's sharing policy lets authors post a preprint anywhere at any time, and this is not prior publication. After acceptance, the arXiv version may be updated to the accepted manuscript under CC BY-NC-ND with a DOI link.
   - IJF is society-owned, and Elsevier notes that some society titles have exceptions. Confirm there is no IJF-specific exception.
   - IEEE allows arXiv and TechRxiv preprints, with a required notice statement.
6. **Indexing requirements.** SCIE status was not verified for any journal. If an institutional SCIE or Q1 rule applies, check the Clarivate MJL and JCR before submitting.
7. **Cost.** Funding is unknown. IJF, Applied Energy and TPWRS have no-fee routes. Energy and AI, IJEPES, OAJPE, Energies, IET GTD and Energy Informatics are fully OA with mandatory APCs, although waivers or institutional agreements may apply.
8. **Placeholders.** Author affiliations and funding are placeholders. Funding and competing-interest statements must be completed before any submission.

## 7. Formatting requirements of the primary journal (IJF)

| Item | Finding | Status |
|---|---|---|
| Abstract | 100–150 words; summarise main findings, how they were obtained and why they matter; no references, jargon or mathematical notation | Seen in Guide for Authors snippet |
| Keywords | Required (Guide checklist mentions keywords) | Seen; number not verified |
| Highlights | Mentioned in Guide checklist "where applicable" | Requirement and format **not verified** |
| Graphical abstract | Mentioned "where applicable" | **Not verified** |
| Word / page limit | No general page limit per 2020 IIF editorial (dated); special issues may set limits (e.g., M6 SI 8,000 words; 2026 open-source section about 20 pages) | **Verify on Guide** |
| Reference style | Not retrieved | **Verify on Guide** |
| Data citation | Dataset references need author, title, repository, version, year and persistent identifier, tagged "[dataset]" | Seen in Guide snippet |
| Data and code | Mandatory sharing since July 2023 plus a reproducibility check before acceptance (IIF site); the Guide snippet is weaker | Seen; conflicting; plan for the strict version |
| Preprints | Elsevier: allowed any time; cite preprints with DOI | Seen (Elsevier policy) |
| Open access | Hybrid; APC USD 3,500 excl. taxes (USD 2,800 on Insights page) | Seen; conflicting amounts |
| Ethics | Elsevier journals are COPE members (since Jan 2008) | Seen |

## 8. Sources actually seen (all on 2026-10-16, via WebSearch snippets; no full pages opened)

**Elsevier / ScienceDirect journal pages**
- IJF: journal page, Insights, Guide for Authors and OA options (sciencedirect.com/journal/international-journal-of-forecasting/...).
- Applied Energy: journal page, Insights, Guide for Authors, OA options, Aims and scope.
- Energy and AI: journal page, Insights, Guide for Authors, OA options.
- SEGAN: guide, Insights, OA options.
- IJEPES: Insights, guide, news, OA options.
- EPSR: journal page, Insights, guide, OA options.
- Energy: Insights, guide, OA options.

**Elsevier policy pages**
- elsevier.com: sharing policy, sharing FAQ, COPE page, publishing ethics.

**International Institute of Forecasters**
- forecasters.org/ijf/ and the IJF "for authors" page.
- IJF EIC report, July 2023 (PDF).
- 2020 EIC editorial.
- 2026 calls for papers.
- M6 special-issue call.

**IEEE**
- ieee-pes.org: TPWRS page, TSG page, OAJPE page, Transactions Information for Authors, OAJPE author kit.
- cmte.ieee.org/tpwrs: scope and review-process pages.
- open.ieee.org: APC page and topical-journals page.
- IEEE 2026 APC list (ieeeauthorcenter PDF).
- ieeexplore.ieee.org: TPWRS page.
- IEEE Author Center: preprint/posting pages.

**Other publishers and indexes**
- scopus.com: Energy and AI source page; SEGAN preview (unreliable).
- mdpi.com: Energies journal page, APC, stats, instructions; MDPI ethics and about pages.
- Energy Informatics: energyinformatics.springeropen.com (about, fees); link.springer.com submission guidelines.
- IET GTD: ietresearch.onlinelibrary.wiley.com author guidelines, OA and ethics pages.
- Data-Centric Engineering: cambridge.org pages.
- Scientific Data: nature.com/sdata aims and scope, for referees, submission guidelines.

**Secondary sources (noted only, not relied on for verified fields)**
- Wikipedia, SciRev, journalmetrics.org, Editage, LetPub, researcher.life, Manusights, DOAJ.

**Not seen**
- Clarivate MJL and JCR records for any candidate.
