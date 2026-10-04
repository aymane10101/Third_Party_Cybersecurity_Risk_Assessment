# Evidence Collection Notes

All sources were retrieved on **24 September 2026**. The full citation trail (URL, source type,
reliability grade, date shown on the page, retrieval date, depth of review, and limitations) is
in `data/source_register.csv`. Framework/standard references are separately tracked in
`data/framework_register.csv`. Every individual finding is in `data/evidence_register.csv`,
cited from `data/assessment_inputs.csv` by evidence ID — nothing in the assessment matrix is
sourced only as "the Trust Center."

## Greenhouse Software

Primary source: the public Trust Center (`trust.greenhouse.com`, Conveyor platform), fully
fetched. It lists badges for ISO 42001, ISO 27001, ISO 27701, SOC 1 Type II, SOC 2 Type II, PCI,
SIG, GDPR, CCPA and the EU-US/UK-US/Swiss-US Data Privacy Framework; featured documents including
a 2025 SOC 2 Type 2 report, a 2025 SOC 1 Type 2 report, ISO certificates, and three dated
penetration-test artifacts (Q3 2025 Onboarding, Q1 2026 external network, Q2 2026 Recruiting); a
30-entry subprocessor list (last updated 1 September 2026); and three dated announcements,
including a disclosed **third-party security incident involving supplier Klue** (announced 24
June 2026) and a rapid response to CVE-2025-55182 (December 2025).

Secondary sources: the `greenhouse.com/security` marketing page (encryption, DPF transfer
mechanisms, ISO editions) and a support knowledge-base article excerpt (S3 encryption, PCI SAQ)
that was reviewed only as a search-result excerpt and cites an older ISO 27001:2013/27701:2019
edition — flagged as partly stale against the 2022/2019 editions on the newer page.

**Retrieval gap**: the Trust Center indexes 251 FAQ answers across categories (Access Management,
Application and Data Security, Continuity and DR, Incident Management, Secure Development,
Vendor Management, Privacy, AI, and others) that were not individually retrieved. Nine controls
are flagged `reviewer_limited` as a result — this is the single largest source of uncertainty in
the Greenhouse assessment (see the sensitivity analysis in the report, Section 7).

## Atlassian

Primary source: the public Trust Center (`customertrust.atlassian.com`, Conveyor platform),
fully fetched — badges, six featured documents (product-specific SOC 1/SOC 2 reports, a C5
assessment letter, an ISO 27001 certificate) and twelve announcements from March 2025 to
September 2026, including a status notice on the FY26 SOC 2 report timeline and several AI
security white papers (Rovo architecture, MCP server security, OWASP Top 10 for LLMs).

A second primary source — and the most valuable one for this assessment — is **"Atlassian's
Technical and Organisational Security Measures"** (`atlassian.com/legal/security-measures`), a
public contractual exhibit effective 7 October 2025 with 20 numbered sections covering access
control, encryption, incident response, business continuity, SDLC, environment separation and
supply-chain risk management in specific, citable language. This exhibit is the strongest single
source for Atlassian in this assessment and grounds most of the Addressed ratings for its
control-level detail.

Secondary source: `atlassian.com/trust/security/security-practices`, reviewed as a search excerpt
(encryption parameters, key management, backup design).

**Retrieval gap**: 169 FAQ answers and the bodies of several 2026 AI/IAM white papers were
indexed but not retrieved (six controls flagged `reviewer_limited`, concentrated in AI-01 and the
sub-processor detail).

## Notion

Primary source: the public Trust Center (`trust.notion.com`, Wolfia platform), fully fetched.
Unlike the other two vendors, Notion's Trust Center publishes 16 control categories with specific
parameters directly on the page (not gated) — TLS 1.2+, AES-256 including backups, customer-managed
keys via AWS KMS, quarterly access reviews, 24-hour access termination, 72-hour standard breach
notification, annual BC/DR and penetration testing, and a detailed AI-governance control set
(retention limits, a kill switch, no-training commitments). A 26-entry subprocessor list
(including roughly a dozen AI/LLM and search providers) and about 20 request-gated policy
documents (SOC 2, SOC 3, ISO 27001 certificate and Statement of Applicability, HIPAA and C5
attestations, 2026 penetration-test reports and retests, and July-2026 CAIQ/VSA/HECVAT
questionnaires) are also listed.

Secondary source: `notion.com/security`, reviewed as a search excerpt, which claims ISO 27701,
27017 and 27018 in addition to ISO 27001 — but no certificate for any of the three appears in the
Trust Center's own document list, so this is recorded at evidence level 1 pending a listed
artifact (`ASSUR-03` is rated Partial rather than Addressed for this reason).

**Retrieval gap**: minimal — one control (`IR-02`) is flagged `reviewer_limited` because the DPA
terms behind the stated 72-hour notification were not read.

## Interpretation rule

Public availability does not equal complete assurance. Scope, audit period, exceptions, customer
responsibilities and product coverage must be reviewed whenever the underlying report is
obtained — this is the substance of nearly every follow-up request in Appendix F of the report.
A vendor that publishes more detail on its public page (Notion) is not necessarily more secure
than one that gates the same detail behind a report request (Atlassian, Greenhouse) — it is more
*transparent* in this specific, desk-based review. Comparing the three vendors' security postures
would require actually obtaining and reading their gated reports, which is exactly the enhanced
due diligence this basic review recommends as a next step.
