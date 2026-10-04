# Methodology

This document is the working reference behind the PDF report; the report (Sections 2–3) is the
version intended for a reader, this file is the version intended for someone extending the code.

## 1. Assessment objective and type

Assess the cybersecurity risk of three named third-party SaaS providers from the perspective of a
fictional enterprise customer, using **basic due diligence** as NIST SP 1326 defines it: desktop
research using publicly available information (PAI). No commercial dataset, proprietary source,
or supply-chain illumination tool was used, and no gated vendor report, contract or DPA was read.

## 2. Scope

Nine control domains, 27 controls (`data/control_catalog.csv`): Governance, Identity & Access,
Data Protection, Vulnerability Management, Incident Response, Business Continuity, Secure
Development, Third-Party Risk, and Assurance, plus a standalone AI-governance control (`AI-01`)
and a dedicated security-logging control (`LOG-01`). Each control
carries cross-references to ISO/IEC 27001:2022 Annex A, NIST CSF 2.0, NIST SP 800-53 Rev. 5, SOC 2
Trust Services Criteria, and the relevant SP 1326 due-diligence component. These are indicative
crosswalks prepared for this project, not official mappings, and no copyrighted standard text is
reproduced.

Explicitly out of scope, per SP 1326's five due-diligence components: Foreign Ownership, Control
or Influence (FOCI) and Provenance. Both are flagged as enhanced-due-diligence follow-ups in the
report (Section 9.2, item 11).

## 3. Vendor inherent-risk tiering

Each vendor is scored 1–5 on five factors given an assumed client use case
(`data/vendor_profiles.csv`): data sensitivity, business criticality, integration depth,
substitutability difficulty (switching cost), and regulatory exposure. The mean of the five
factors places the vendor in a tier:

| Score | Tier | Label | Due-diligence depth |
|---|---|---|---|
| ≥ 3.75 | 1 | Critical | Enhanced (SOC 2 report read, contract review, technical validation) |
| 3.00–3.74 | 2 | Important | Basic plus targeted enhanced follow-ups |
| < 3.00 | 3 | Standard | Basic (public-information) due diligence |

Tier drives **inherent likelihood** (Tier 1 = 5, Tier 2 = 4, Tier 3 = 3) rather than using one
fixed value for every vendor regardless of how critical it is.

## 4. Evidence hierarchy

Every fact is recorded once in `data/evidence_register.csv` with an **evidence level**:

- **3 – Independent**: an independent attestation, certificate, or third-party test artifact is
  publicly listed (contents are usually gated, so this evidences *existence*, not content).
- **2 – Vendor-specific**: a specific vendor-authored control description, or a published
  contractual exhibit, ideally with a stated parameter (protocol, algorithm, cadence, timeframe).
- **1 – Assertion**: a summary checklist tick, badge, marketing statement, self-attestation
  (e.g. a PCI SAQ or a SIG Lite), or indirect evidence.
- **0 – None**: nothing found in the reviewed sources.

## 5. Control-level coverage status

- **Addressed** — the source explicitly supports the control. A binary feature (SSO exists, a DPA
  is offered) needs an explicit statement. An operational control (access reviews, encryption,
  DR) needs at least one stated parameter to count as Addressed, and Addressed always requires
  evidence level ≥ 2 (an unsupported assertion cannot mark a control Addressed — enforced by
  `src/validate.py`).
- **Partial** — the control is named or indirectly evidenced, but scope, depth, parameters or
  product coverage are insufficient.
- **Not evidenced** — nothing relevant was found in the reviewed sources. **This does not mean
  the control is absent.** Where the reason is that an indexed source (typically a vendor FAQ
  section) was not retrieved, the row carries `reviewer_limited = Y`. This is a limitation of
  this specific review — a different reviewer with more time would resolve it, in either
  direction — and it is treated distinctly in scoring (Section 6) and tested in the sensitivity
  analysis (Section 7 of the report).

## 6. Risk model

`Residual Risk = Residual Likelihood × Impact`, on a 5×5 scale (NIST SP 800-30 Rev. 1
semi-quantitative style). All numeric parameters below are **project-defined assumptions**, not
values mandated by ISO or NIST.

| Element | Rule |
|---|---|
| Impact (1–5) | Set per control in the catalogue: 5 for identity, data-protection and incident-response controls; 4 for most other operational/assurance controls; 3 for methodology and risk-transfer items (evidence currency, cyber insurance). |
| Residual likelihood | Addressed → 2; Partial → 3; Not evidenced → 4. A Not-evidenced row that is `reviewer_limited` is floored at 3, not 4 — absence has not been established, so the model does not assume the worst case. |
| Adverse-event uplift | +1 (capped at 5) where a public, vendor-disclosed event within the last 24 months demonstrates the control failing and root cause/remediation is not yet fully disclosed. Applied once in this run (Greenhouse `SUP-01`, the Klue third-party incident). This is a risk judgement about uncertainty, not a finding of vendor fault. |
| Inherent likelihood | By vendor tier — see Section 3. |
| Bands | Low 1–4, Medium 5–12, High 13–19, Critical 20–25. |

Likelihood **1** is never assigned from public evidence alone in this project; it is reserved for
a control that has been validated against an actual report, test result or contract (i.e. enhanced
due diligence), which is out of scope here. This is enforced by
`tests/test_scoring.py::test_no_likelihood_of_one_from_public_evidence`.

**Confidence** is reported separately and is *not* multiplied into the score: evidence level 3 =
High confidence, 2 = Medium, 1 = Low. It is used only to order follow-up requests (lowest
confidence first, among equally scored controls).

### Why these particular band thresholds

A naive set of bands (e.g. 1–4 / 5–9 / 10–15 / 16–25) has a problem: an impact-5 control scores 10
("High") even at the best possible evidence level (Addressed → residual likelihood 2). Every
impact-5 control in the catalogue would then be rated High or Critical for every vendor
regardless of evidence quality, and the model could not discriminate between a well-evidenced
vendor and a poorly-evidenced one. The bands used here (Medium up to 12) instead let a fully
Addressed impact-5 control (2 × 5 = 10) land in Medium, while a Not-evidenced impact-5 control
(4 × 5 = 20) lands in Critical. See the sensitivity table in Section 7 of the report for the
effect this choice has on the headline numbers.

## 7. Why certifications are not treated as a security score

ISO 27001, SOC 2 and similar assurance artifacts raise confidence in a control environment, but
the assessment still asks: is the relevant service in scope; is the evidence current; what is the
audit period; are there exceptions; are complementary user-entity controls relevant; are
customer-specific contractual requirements covered? None of these questions can be answered from
a badge alone — they require reading the actual report, which this project's basic-due-diligence
scope does not include (see Section 9.2, item 1 of the report, and the follow-up list in
Appendix F).

## 8. Risk treatment and monitoring

Findings feed a treatment plan (report Section 9) using an ISO 31000-style evaluation rule
(Critical → do not onboard without a plan; High → plan with owner and date; Medium → accept with
monitoring; Low → accept) and a monitoring calendar keyed to time-bound artifacts (SOC 2 report
periods, insurance expiry, pentest age) and events (incidents, subprocessor changes,
certification loss).

## 9. Limitations

Public evidence only; several indexed sources (vendor FAQ bodies, most white-paper bodies) were
not retrieved and are flagged `reviewer_limited`; vendor-authored statements are unverified;
findings are a point-in-time snapshot (24 September 2026) with no archived page snapshots taken;
FOCI, provenance, concentration risk, financial health, litigation history and technical
attack-surface signals are out of scope. See report Section 8 for the full list and Section 10
for recommended next steps to close these gaps. The assessments are educational and must not be
presented as formal audit conclusions.
