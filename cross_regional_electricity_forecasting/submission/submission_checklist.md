# Submission Checklist: International Journal of Forecasting (primary)

**Prepared:** 2026-10-16 (Agent 11).

**Official Guide for Authors:** https://www.sciencedirect.com/journal/international-journal-of-forecasting/publish/guide-for-authors

**IIF journal page:** https://forecasters.org/ijf/

**Legend**

- **[V]** Seen in a snippet of an official page on 2026-10-16.
- **[U]** Not verified. *Verify on the official Guide for Authors before submission.*

Snippet-level evidence only. Full pages could not be opened in this session.

---

## A. Scope and framing

- [ ] **Scope fit [V].** The cover letter and introduction frame the contribution as a forecasting-methodology and evaluation contribution, covering:
  - unseen-region evaluation protocol;
  - calibration under shift;
  - adaptation curves;
  - drift and refit;
  - benchmarking against operator forecasts.

  IJF covers "all aspects of forecasting". The 2026 IIF calls list energy and utilities forecasting, reproducible workflows and open-source forecasting.
- [ ] Check whether a currently open IJF special issue or section fits better. Open calls seen:
  - "Open-source forecasting" (2026);
  - "The future of forecasting: bridging theory and practice" (Aug 2026).

  Read each call for its deadline and length limit (for example, about 20 pages for the open-source section) **[V, call pages; deadlines U]**.
- [ ] Explicitly position the paper against prior IJF energy-forecasting work (GEFCom, probabilistic load forecasting, conformal methods).

## B. Manuscript format

- [ ] **Abstract: 100–150 words [V].** It must summarise:
  - the principal findings;
  - how they were obtained;
  - why they matter to researchers and practitioners.

  No references, no jargon, no mathematical notation.
- [ ] **Keywords** provided [V that keywords are required]. Number and format [U].
- [ ] **Highlights.** The Guide checklist mentions highlights "where applicable". Whether they are required, and the character limits, are [U]. If used, follow Elsevier's usual format (3–5 bullets) [U for IJF].
- [ ] **Graphical abstract:** "where applicable" [U].
- [ ] **Length.** A 2020 IIF editorial says there is no page limit [dated]. Confirm the current rule [U].

  The manuscript is 8–10k words with about 13 figures. Consider moving secondary figures (for example, per-BA detail and missing-data sweeps) to an online appendix.
- [ ] **Reference style [U].** Elsevier journals often accept "Your Paper Your Way" at first submission; this is [U] for IJF.
- [ ] Figures readable in greyscale and colour-blind safe. Production file formats and resolution [U].
- [ ] Title page with author details, as a separate file if required [U]. Review model (single- or double-anonymised) [U]. If double-anonymised, anonymise the code and repository links in the manuscript.
- [ ] Line and page numbering for review [U].

## C. Data, code and reproducibility (critical for IJF)

- [ ] **Data and code sharing.**
  - The IIF site says sharing has been mandatory since July 2023 unless the EIC accepts a justification [V].
  - The Guide snippet says data are expected and code is encouraged [V].
  - Plan for the stricter requirement.
- [ ] **Reproducibility check [V].** Acceptance depends on the reproducibility check. Possible outcomes are "pass", "minor concerns" (the reproduced results deviate from the paper) and "major discrepancies". Prepare a reproducibility package that includes:
  - [ ] a single entry-point script or Makefile that regenerates every table and figure;
  - [ ] pinned environment files (`environment.yml` / `requirements.txt` with exact versions), fixed random seeds, and a record of LightGBM and other library versions;
  - [ ] PUDL / EIA-930 data version (release tag or DOI) and download instructions or scripts, plus checksums;
  - [ ] the hardware and runtime of each stage; a "fast path" using cached intermediate results for expensive experiments;
  - [ ] a README mapping each figure and table to the script that produces it;
  - [ ] a permanent archive (Zenodo DOI) of the exact submitted code version, plus a GitHub link;
  - [ ] an open licence for the code; confirm that the EIA-930/PUDL data licence permits redistribution (see `LICENSES_AND_DATA_PROVENANCE.md`).
- [ ] **Data citation [V].** Cite datasets with author, title, repository, version, year and persistent identifier, tagged "[dataset]". Do this for EIA-930, PUDL and any weather or operator forecast sources.
- [ ] Data availability statement. Elsevier journals include one, but the exact IJF wording and placement are [U].
- [ ] Operator day-ahead forecasts. Document their provenance and any limits on redistribution.

## D. Ethics, declarations and policies

- [ ] **Publisher ethics:** Elsevier journals are COPE members [V].
- [ ] Declaration of competing interests (Elsevier form or template) [U for IJF specifics].
- [ ] **Funding statement.** Currently a placeholder and **must be completed**.
- [ ] **Author affiliations.** Currently placeholders and **must be completed**. Add ORCIDs.
- [ ] CRediT author contribution statement [U].
- [ ] Declaration of generative AI use in the writing process. Elsevier has a policy; the wording is [U for IJF].
- [ ] Confirm the work is not under consideration elsewhere and has not been published previously.
- [ ] **Preprint [V, Elsevier policy].**
  - Posting on arXiv or SSRN is allowed at any time and is not prior publication.
  - After acceptance, you may update the arXiv version to the accepted manuscript (CC BY-NC-ND) and link the DOI.
  - IJF is society-owned and Elsevier notes possible exceptions for society titles, so confirm there is no IJF exception [U].
  - Cite preprints with their DOI.

## E. Open access and cost

- [ ] **Choose a route.**
  - Subscription: no APC [V hybrid].
  - Gold OA: APC USD 3,500 excl. taxes per the OA options page; the Insights page shows USD 2,800 [V, conflicting]. Check the price shown at submission.
- [ ] Check whether the corresponding author's institution has an Elsevier OA agreement. Eligibility is based on the corresponding author's affiliation (Elsevier general guidance) [U for IJF].
- [ ] Check whether the funder requires open access, a CC BY licence or zero embargo. Funding is currently unknown.

## F. Submission package

- [ ] Cover letter covering:
  - the contribution;
  - fit with IJF scope and any open call;
  - the reproducibility package link;
  - suggested and opposed reviewers (if the system asks) [U].
- [ ] Manuscript, tables and figures in separate files if required [U].
- [ ] Supplementary material: appendix with per-BA results, extended calibration tables and the missing-data experiments.
- [ ] Response-to-reviewers template ready. Expect a long review: the official Insights page reports 168 days of review time and 296 days to acceptance; the journal-page snapshot reports 318 days [V].

## G. Expected timeline (official Insights page snippets, seen 2026-10-16)

| Stage | Reported value | Note |
|---|---|---|
| Submission to first decision | 9 days | Mostly desk decisions |
| Review time | 168 days | |
| Submission to acceptance | 296 days | 318 days on the journal-page snapshot |
| Acceptance to publication | Not found | [U] |

## H. Fallback readiness (if IJF rejects)

| Journal | Changes needed |
|---|---|
| Applied Energy | Abstract of 250 words or fewer [V]; 3–5 highlights of at most 85 characters each, including spaces [V], as a separate editable file; graphical abstract encouraged [V]; data availability statement at submission [V]; reframe around applied energy-system relevance; word limit [U] |
| Energy and AI | Fully OA with a mandatory APC of about USD 3,990–4,270 [V, conflicting]; listed in ESCI, not SCIE [V, snippet]; author guidelines [U] |
| IEEE TPWRS (ambitious) | Cut to 10 pages or fewer, IEEE format; returned without review if over the limit [V]; overlength charge of USD 250 per page beyond 12 published pages [V]; move extended results to supplementary material |
