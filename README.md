# Third-Party Cybersecurity Risk Assessment — Public Evidence Edition

## Purpose

A realistic third-party cybersecurity due-diligence workflow built on **real SaaS vendors and
public evidence only**: Atlassian, Greenhouse Software and Notion. It is a portfolio/educational
project, not an audit, certification opinion, penetration test, or legal/compliance opinion.

## Highlights

- **27-control catalogue** mapped to ISO/IEC 27001:2022 Annex A, NIST CSF 2.0, NIST SP 800-53r5
  and SOC 2 TSC, each with an SP 1326 component tag (`data/control_catalog.csv`).
- **Two-tier citation trail**: an 8-row **source register** (vendor pages + contractual
  exhibits, graded A+ to C, with retrieval date and depth of review) and a 52-row **evidence
  register** (one row per fact, citing a source, page locator, a paraphrased finding, an
  evidence level, and a stated limitation). Every assessment row cites specific evidence IDs —
  not just "the Trust Center."
- **A discriminating risk model.** Naive scoring can rate *every* impact-5 control "High"
  regardless of evidence quality, collapsing every vendor to the same result. This model revises
  the band thresholds, adds a `reviewer_limited` flag (evidence was indexed but not read — this
  is a limitation of the review, not proof of absence) and a one-time adverse-event likelihood
  uplift for a disclosed, unresolved incident, so results actually discriminate between vendors.
- **Vendor risk tiering.** Inherent likelihood is derived from a five-factor vendor profile
  (data sensitivity, business criticality, integration depth, switching cost, regulatory
  exposure) instead of a fixed value for every vendor.
- **Sensitivity analysis** (`data/sensitivity_analysis.csv`) showing how the High/Critical count
  moves under favourable/adverse resolution of the reviewer-limited items — so the conclusions
  can be checked rather than taken on faith.
- **Reproducible pipeline**: `src/scoring.py` computes every score from `data/assessment_inputs.csv`;
  `src/validate.py` checks referential integrity (every evidence ID resolves, every vendor
  covers every control, no orphaned rows); `tests/test_scoring.py` is a small pytest suite;
  `src/build_outputs.py` regenerates every derived CSV; `src/build_latex_report.py` and
  `src/build_latex_explainer.py` generate LaTeX source from the CSVs, which is then compiled
  with `pdflatex` into the two PDFs — nothing in either report is hand-typed.
- **Typeset in LaTeX, black and white only.** Both PDFs are real `report`-class LaTeX documents
  (not an imitation): standard A4 margins, Computer Modern type, `booktabs`/`longtable` tables,
  numbered chapters and a table of contents. Risk severity is shown by grayscale shading alone
  (white → black); no colour is used anywhere.

## Vendors assessed

- Atlassian (Jira / Confluence / Jira Service Management)
- Greenhouse Software (applicant tracking and onboarding)
- Notion (internal wiki with AI features)

## Evidence rule

A source stating a control exists is recorded as evidence at a specific **level** (3 =
independent artifact/attestation listed, 2 = vendor-specific statement or contractual exhibit,
1 = summary assertion/badge/self-attestation, 0 = none found). If a detail is not visible in a
reviewed source, the project records **Partial** or **Not evidenced** rather than asserting the
control is absent — and if the reason is that a source was indexed but not read (e.g. an
unretrieved FAQ), the row is flagged `reviewer_limited` and treated more cautiously in scoring
and in the sensitivity analysis.

## Methodology (see `docs/methodology.md` for full detail)

1. Define a fictional client scenario and derive vendor inherent-risk tiers.
2. Build a 27-control catalogue with cross-framework mapping.
3. Collect public evidence from vendor Trust Centers and published contractual exhibits.
4. Record source, evidence level, coverage status and limitations for every control/vendor pair.
5. Score `Inherent Risk = Inherent Likelihood × Impact` and
   `Residual Risk = Residual Likelihood × Impact` on a 5×5 matrix.
6. Apply project-defined thresholds (Low 1–4, Medium 5–12, High 13–19, Critical 20–25) — **not**
   ISO/NIST-mandated values.
7. Run a sensitivity analysis and produce vendor-level findings, a prioritised treatment plan and
   a per-vendor follow-up request list.

## Framework references

Primary: NIST SP 800-161 Rev. 1 (C-SCRM) and SP 1326 (C-SCRM Due Diligence Assessment
Quick-Start Guide), SP 800-30 Rev. 1 (risk assessment), CSF 2.0, SP 800-53
Rev. 5. Secondary: ISO/IEC 27001:2022, 27036, 27005, ISO 31000:2018, AICPA SOC 2 TSC. Full
citations with URLs in `data/framework_register.csv`. Standard text is not reproduced anywhere
in this project (ISO texts are paywalled); only control identifiers/clause numbers are used for
cross-referencing.

## Disclaimer

Educational portfolio project. Not an independent audit, certification opinion, penetration
test, or legal/compliance opinion. Public evidence is incomplete by nature; gated vendor reports
were not treated as independently reviewed. See Section 8 (Limitations, bias and independence) of
the report.

## Repository layout

```
data/        control catalogue, source & evidence registers, vendor profiles,
             analyst inputs (assessment_inputs.csv — the only hand-authored judgement file),
             and derived outputs (assessment_matrix.csv, vendor_summary.csv,
             sensitivity_analysis.csv, followup_requests.csv)
docs/        methodology.md, evidence_collection.md
src/         scoring.py, validate.py, build_outputs.py, build_latex_report.py,
             build_latex_explainer.py, latex_common.py, app.py
tests/       test_scoring.py (pytest)
latex/       generated .tex sources and compiled .pdf (build working directory)
reports/     Third_Party_Cyber_Risk_Assessment_Report.pdf, Project_Explainer.pdf (final copies)
```

## How to reproduce

Requires a LaTeX distribution with `pdflatex` on PATH (TeX Live or MiKTeX), plus the packages
`booktabs`, `longtable`, `tabularx`, `xcolor`, `colortbl`, `fancyhdr`, `titlesec`, `enumitem`,
`xurl`, `seqsplit`, `hyperref`, `babel` (all standard/included in a full TeX Live install).

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python src/validate.py                        # integrity checks
pytest -q                                      # unit tests
python src/build_outputs.py                    # regenerate derived CSVs from assessment_inputs.csv
python src/build_latex_report.py               # generate latex/report.tex
python src/build_latex_explainer.py            # generate latex/explainer.tex
cd latex && pdflatex report.tex && pdflatex report.tex        # run twice for the TOC
pdflatex explainer.tex && pdflatex explainer.tex && cd ..
cp latex/report.pdf reports/Third_Party_Cyber_Risk_Assessment_Report.pdf
cp latex/explainer.pdf reports/Project_Explainer.pdf
streamlit run src/app.py                       # interactive dashboard
```

Only `data/assessment_inputs.csv` (the analyst's coverage/evidence-level judgements) and the
registers under `data/` are hand-authored; every other file under `data/`, and both PDFs, are
generated by the scripts above and should not be hand-edited.
