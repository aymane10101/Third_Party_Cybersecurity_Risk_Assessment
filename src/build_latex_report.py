"""Generates latex/report.tex (the findings report) from the data files, then compiles it
with pdflatex into reports/Third_Party_Cyber_Risk_Assessment_Report.pdf.
"""
from pathlib import Path
import pandas as pd
import scoring
from latex_common import esc, esc_plain, PREAMBLE, fancy_header, longtable_str

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT, TEX = ROOT / "data", ROOT / "reports", ROOT / "latex"
ASSESS_DATE = "24 September 2026"


def band_word(score):
    return scoring.risk_band(score)


def rc(score):
    return rf"\ratingcell{{{int(score)}}}"


def cov_word(cov):
    return {"Addressed": "Addressed", "Partial": "Partial", "Not evidenced": "Not evid."}[cov]


def main():
    df = scoring.load_assessment()
    summ = scoring.vendor_summary(df)
    sens = scoring.sensitivity(df)
    cat = pd.read_csv(DATA / "control_catalog.csv")
    ev = pd.read_csv(DATA / "evidence_register.csv")
    src = pd.read_csv(DATA / "source_register.csv")
    fw = pd.read_csv(DATA / "framework_register.csv")
    prof = pd.read_csv(DATA / "vendor_profiles.csv")
    fu = pd.read_csv(DATA / "followup_requests.csv")
    S = summ.set_index("vendor")
    TEX.mkdir(exist_ok=True)

    tex = [PREAMBLE]
    tex.append(fancy_header("Third-Party Cybersecurity Risk Assessment", "Public Evidence Edition"))
    tex.append(r"""
\title{\bfseries Third-Party Cybersecurity\\ Risk Assessment}
\author{Public Evidence Edition}
\date{Assessment date: """ + ASSESS_DATE + r""" \\[2pt] \small Desk-based, educational use --- not an audit}
""")
    tex.append(r"\begin{document}")
    tex.append(r"\begin{titlepage}")
    tex.append(r"\centering")
    tex.append(r"\vspace*{3cm}")
    tex.append(r"{\Huge\bfseries Third-Party Cybersecurity\\[4pt] Risk Assessment\par}")
    tex.append(r"\vspace{0.8cm}")
    tex.append(r"{\Large Public Evidence Edition\par}")
    tex.append(r"\vspace{0.4cm}")
    tex.append(r"{\large Vendors assessed: Atlassian, Greenhouse Software, Notion\par}")
    tex.append(r"\vspace{2.5cm}")
    tex.append(r"\renewcommand{\arraystretch}{1.5}")
    tex.append(r"\begin{tabularx}{0.92\textwidth}{L{0.32\textwidth} X}")
    tex.append(r"\toprule")
    tex.append(r"\textbf{Document control} & \\")
    tex.append(r"\midrule")
    rows = [
        ("Status", "Final for portfolio review"),
        ("Assessment date", f"{ASSESS_DATE}. All sources retrieved on this date."),
        ("Assessment type", "Desk-based (basic) due diligence using publicly available information, per the NIST SP 1326 definition"),
        ("Frameworks referenced", "NIST SP 800-161r1, SP 1326, SP 800-30r1, CSF 2.0, SP 800-53r5; ISO/IEC 27001:2022, 27036, 27005, ISO 31000:2018. Alignment only --- no compliance or certification is claimed."),
        ("Client scenario", "Fictional multinational enterprise (about 3,000 staff, EU and US operations, GDPR-regulated)."),
        ("Classification", "Public --- educational portfolio material"),
        ("Next scheduled review", "Annual, or earlier on a material vendor change (see Section 9.3)"),
    ]
    for k, v in rows:
        tex.append(rf"\textbf{{{esc(k)}}} & {esc(v)} \\")
    tex.append(r"\bottomrule")
    tex.append(r"\end{tabularx}")
    tex.append(r"\renewcommand{\arraystretch}{1.15}")
    tex.append(r"\vfill")
    tex.append(r"\end{titlepage}")
    tex.append(r"\tableofcontents")
    tex.append(r"\clearpage")

    # ---------------------------------------------------------- 1 exec summary
    tex.append(r"\chapter{Executive summary}")
    tex.append(esc(
        f"This report assesses three SaaS vendors that a fictional client might rely on: Atlassian (Jira/Confluence/JSM), "
        f"Greenhouse Software (applicant tracking and onboarding) and Notion (internal wiki with AI features). Each vendor "
        f"was assessed against a 27-control catalogue mapped to ISO/IEC 27001:2022 Annex A, NIST CSF 2.0, NIST SP 800-53r5 "
        f"and SOC 2 criteria, using only public evidence retrieved on {ASSESS_DATE}. Every finding is traceable to a "
        "numbered evidence item, which cites a source, the page section and a paraphrased finding (Appendices C and D)."))

    tex.append(r"\section*{Headline results}")
    hdr = ["Vendor", "Tier", "Addr.", "Part.", "Not evid.", "Weighted cov.", "High", "Crit.", "Limited src.*"]
    rows_ = []
    for v in ["Atlassian", "Greenhouse Software", "Notion"]:
        r = S.loc[v]
        rows_.append([esc(v), f"{int(r.tier)}", str(int(r.addressed)), str(int(r.partial)), str(int(r.not_evidenced)),
                      f"{r.impact_weighted_coverage_pct}\\%", str(int(r.high)), str(int(r.critical)), str(int(r.reviewer_limited))])
    tex.append(longtable_str(hdr, rows_, "L{3.1cm}C{0.9cm}C{1.1cm}C{1.1cm}C{1.3cm}C{1.9cm}C{0.9cm}C{0.9cm}C{1.7cm}", small=True))
    tex.append(r"{\footnotesize *Controls where an indexed public source (mainly vendor FAQ sections) was not retrieved. "
               r"This is a limitation of this review, not evidence of a control gap. See Section~8.\par}")

    tex.append(r"\section*{Coverage by vendor}")
    hdr2 = ["Vendor", "Addressed", "Partial", "Not evidenced", "Total"]
    rows2 = []
    for v in ["Atlassian", "Greenhouse Software", "Notion"]:
        r = S.loc[v]
        rows2.append([esc(v), str(int(r.addressed)), str(int(r.partial)), str(int(r.not_evidenced)), str(int(r.controls))])
    tex.append(longtable_str(hdr2, rows2, "L{4.5cm}C{2.2cm}C{2.2cm}C{2.6cm}C{1.6cm}", small=False))

    tex.append(r"\section*{Key findings}")
    tex.append(r"\begin{itemize}")
    for b in [
        f"\\textbf{{Notion}} has the deepest public evidence: {int(S.loc['Notion','addressed'])} of 27 controls are Addressed with stated parameters (TLS 1.2+, AES-256, quarterly access reviews, 24-hour access removal, 72-hour breach notice, annual BC/DR tests). Its single High item is the absence of general customer-content retention periods (DAT-02).",
        "\\textbf{Atlassian} (Tier 1, the most critical dependency) publishes a detailed contractual security exhibit, but three High items remain: no access-review cadence (IAM-04), no post-termination deletion timeframe (DAT-02) and no fixed incident-notification window (IR-02). Its SOC~2 report is product-scoped (Jira and Confluence shown) and the FY26 report (period ended 30 Sep 2025) was not confirmed as issued on the Trust Center; the FY27 period closes on 30 Sep 2026.",
        f"\\textbf{{Greenhouse}} carries the most open items ({int(S.loc['Greenhouse Software','high'])} High) largely because its detailed answers sit in a 251-answer FAQ that was indexed but not read. Two items are substantive: a disclosed \\textbf{{third-party incident at supplier Klue (11 June 2026)}} where compromised integration credentials reached Greenhouse sales/CRM data (root cause still open on the page reviewed), and MFA enforcement not being evidenced.",
        "\\textbf{Do not read this as a vendor league table.} The results measure how much public evidence was retrievable, not how secure each vendor is. Notion publishes its controls with parameters on one page; the other two publish more behind FAQs and gated reports.",
        "\\textbf{AI-provider concentration} is a growing fourth-party exposure: Notion lists roughly a dozen AI/LLM and search subprocessors; Greenhouse discloses Anthropic and OpenAI; Atlassian's current public AI documentation was reviewed for the AI-01 criterion.",
    ]:
        tex.append(rf"\item {esc(b)}")
    tex.append(r"\end{itemize}")

    tex.append(r"\section*{Priority actions (detail in Section 9)}")
    tex.append(r"\begin{itemize}")
    for b in ["Obtain and read the SOC 2 Type II reports (scope, period, exceptions, complementary user-entity controls) and bridge letters for all three vendors, starting with Atlassian (Tier 1).",
              "Close three contractual gaps across vendors: incident-notification window, post-termination deletion timeframe, sub-processor change notice.",
              "Greenhouse: obtain the Klue incident root-cause summary and confirm MFA enforcement; remaining gaps are substantive evidence requests rather than source-review limitations.",
              "Set a monitoring calendar for time-bound artifacts: Atlassian FY27 SOC 2 (period ends 30 Sep 2026), Notion insurance evidence (expires Nov 2026), Greenhouse Onboarding pentest (last dated Q3 2025)."]:
        tex.append(rf"\item {esc(b)}")
    tex.append(r"\end{itemize}")
    tex.append(r"\clearpage")

    # ---------------------------------------------------------- 2 scope
    tex.append(r"\chapter{Scope, context and objectives}")
    tex.append(r"\section{Objective and approach}")
    tex.append(esc("The objective is to give a decision-maker a transparent, repeatable view of what public evidence "
               "supports for each vendor, where the assurance gaps are, and what to ask for next. The process follows "
               "the ISO 31000:2018 cycle (establish context, identify, analyse, evaluate, treat, monitor, communicate) "
               "and uses NIST SP 800-30r1 for likelihood/impact reasoning, NIST SP 800-161r1 for supplier criticality "
               "and C-SCRM practice, and NIST SP 1326 for the due-diligence scope."))
    tex.append(r"\section{What NIST SP 1326 says this assessment is}")
    tex.append(esc("SP 1326 (final, 8 July 2026) distinguishes basic due diligence (desktop research using publicly "
               "available information) from enhanced due diligence (commercial datasets, proprietary sources, "
               "supply-chain illumination tools). This project is basic due diligence. SP 1326 organises assessments "
               "into five components; coverage here is:"))
    hdr = ["SP 1326 component", "Covered?", "How"]
    rows_ = [
        ["Foundational cyber practices", "Yes", "Controls GOV, IAM, DAT, VUL, IR, LOG, SDLC, ASSUR, AI"],
        ["Resilience", "Yes", "BC-01, BC-02, SUP-03 (plus incident history in the vendor findings)"],
        ["Supply chain tiers", "Partly", "Subprocessor transparency and supplier oversight (DAT-03, SUP-01, SUP-02, AI-01); fourth-party depth beyond the published lists was not analysed"],
        ["Foreign ownership, control or influence (FOCI)", "No", "Out of scope. Recommended for an enhanced review"],
        ["Provenance", "No", "Out of scope. Applies mainly to products and components"],
    ]
    tex.append(longtable_str(hdr, [[esc(c) for c in r] for r in rows_], "L{4.5cm}C{1.8cm}L{7.8cm}", small=True))

    tex.append(r"\section{Fictional client scenario and use cases}")
    tex.append(esc("The client is a fictional multinational (about 3,000 staff, EU and US operations, subject to GDPR). "
               "The use cases below are assumptions used to size impact; they are not facts about any real organisation."))
    hdr = ["Vendor", "Assumed use case", "Sens.", "Crit.", "Integr.", "Lock-in", "Reg.", "Score", "Tier"]
    rows_ = []
    for _, x in prof.iterrows():
        rows_.append([esc(x.vendor), esc(x.assumed_use_case), str(x.data_sensitivity), str(x.business_criticality),
                      str(x.integration_depth), str(x.substitutability_difficulty), str(x.regulatory_exposure),
                      str(x.inherent_score), f"{int(x.tier)} ({esc(x.tier_label)})"])
    tex.append(longtable_str(hdr, rows_, "L{2.2cm}L{4.4cm}C{0.8cm}C{0.8cm}C{0.9cm}C{0.9cm}C{0.7cm}C{0.9cm}L{2.0cm}", small=True))
    tex.append(r"{\footnotesize Each factor is scored 1 (low) to 5 (high). Tier 1 (score 3.75 or more) calls for "
               r"enhanced due diligence; Tier 2 (3.0 to 3.74) for basic plus targeted follow-ups; Tier 3 for basic "
               r"only. Thresholds are project-defined.\par}")
    tex.append(r"\clearpage")

    # ---------------------------------------------------------- 3 methodology
    tex.append(r"\chapter{Methodology}")
    tex.append(r"\section{Evidence hierarchy}")
    hdr = ["Level", "Name", "Definition", "Examples in this project"]
    rows_ = [
        ["3", "Independent", "An independent attestation, certificate or third-party test artifact is publicly listed. Contents are usually gated, so existence is evidenced, not content.", "SOC 2 Type II listing, ISO certificate, dated pentest report/letter"],
        ["2", "Vendor-specific", "A specific vendor-authored control description or a published contractual exhibit, ideally with parameters.", "Atlassian security-measures exhibit; Notion control statements"],
        ["1", "Assertion", "Summary checklist, badge, marketing statement, self-attestation or indirect evidence.", "Trust Center quick-summary ticks, SIG Lite, PCI SAQ"],
        ["0", "None", "Nothing found in the reviewed sources. This does not mean the control is absent.", "---"],
    ]
    tex.append(longtable_str(hdr, [[esc(c) for c in r] for r in rows_], "C{0.7cm}L{2.1cm}L{5.4cm}L{4.6cm}", small=True))

    tex.append(r"\section{Coverage status (control-level)}")
    tex.append(r"\begin{itemize}")
    for b in ["\\textbf{Addressed} --- the public source explicitly describes the control. Binary features (SSO, DPA, status page, bug bounty) need an explicit statement; operational controls (reviews, testing, DR, encryption) need at least one parameter such as a cadence, timeframe, protocol or algorithm. Addressed requires evidence level 2 or 3.",
              "\\textbf{Partial} --- the control is named or indirectly evidenced but scope, depth, parameters or product coverage are limited.",
              "\\textbf{Not evidenced} --- nothing relevant was found in the reviewed sources. Where a relevant source was \\textit{indexed but not read}, the row is flagged \\textbf{reviewer-limited} and is not treated as proof of absence."]:
        tex.append(rf"\item {esc(b)}")
    tex.append(r"\end{itemize}")

    tex.append(r"\section{Risk model}")
    tex.append(esc("Residual Risk = Residual Likelihood x Impact, on a 5 x 5 scale, following the semi-quantitative "
               "approach of NIST SP 800-30r1. All parameters are project-defined assumptions, not ISO or NIST thresholds."))
    hdr = ["Element", "Rule"]
    rows_ = [
        ["Impact (1--5)", "Set per control in the catalogue (3 to 5) from the client scenario: 5 for identity, data protection and incident response; 4 for other operational and assurance controls; 3 for methodology and risk-transfer items."],
        ["Residual likelihood", "Addressed = 2; Partial = 3; Not evidenced = 4. A Not-evidenced row that is reviewer-limited is set to 3. Likelihood 1 is never assigned from public evidence; it is reserved for controls validated against an actual report or contract (enhanced due diligence)."],
        ["Adverse-event uplift", "+1 (maximum 5) where a public, vendor-disclosed event in the last 24 months shows the control failing and root cause or remediation is not fully disclosed. Applied once: Greenhouse SUP-01 (Klue). This is a risk judgement, not a finding of fault."],
        ["Inherent likelihood", "By vendor tier: Tier 1 = 5, Tier 2 = 4, Tier 3 = 3. Inherent risk = inherent likelihood x impact."],
        ["Confidence", "Reported separately from risk: evidence level 3 = High, 2 = Medium, 1 = Low. Confidence is not multiplied into the score. It orders follow-up work (lowest confidence first among equal scores)."],
    ]
    tex.append(longtable_str(hdr, [[esc(c) for c in r] for r in rows_], "L{3.2cm}L{11.0cm}", small=True))

    tex.append(r"\subsection*{5$\times$5 risk matrix}")
    tex.append(r"\begin{center}")
    tex.append(r"\renewcommand{\arraystretch}{1.3}")
    tex.append(r"\begin{tabular}{c|ccccc}")
    tex.append(r"\textbf{L $\backslash$ I} & \textbf{1} & \textbf{2} & \textbf{3} & \textbf{4} & \textbf{5} \\ \hline")
    for L in range(5, 0, -1):
        cells = " & ".join(rc(L * I) for I in range(1, 6))
        tex.append(rf"\textbf{{{L}}} & {cells} \\")
    tex.append(r"\end{tabular}")
    tex.append(r"\renewcommand{\arraystretch}{1.15}")
    tex.append(r"\end{center}")
    tex.append(r"{\footnotesize Bands (grayscale, darker = higher risk): Low 1--4; Medium 5--12; High 13--19; "
               r"Critical 20--25.\par}")

    tex.append(r"\section{Source quality grades}")
    tex.append(esc("A+ = contractual document published by the vendor; A = full vendor trust portal fetched with "
               "dated content; B = vendor marketing/documentation page; C = partial excerpt or partly stale. "
               "Third-party blogs and review sites were excluded from scoring. Sources are grouped in Appendix D "
               "with retrieval date and depth of review (full page or excerpt only)."))
    tex.append(r"\clearpage")

    # ---------------------------------------------------------- 4 results
    tex.append(r"\chapter{Results}")
    tex.append(r"\section{Residual risk by control}")
    tex.append(esc("Each row shows the residual score and coverage status for a control across all three vendors. "
               "Cells are shaded on a grayscale from white (Low) to black (Critical); no hue is used anywhere in "
               "this report. No control reached Critical or Low: public evidence alone cannot support a likelihood "
               "below 2, and no impact-5 control was wholly unevidenced."))
    order_c = list(cat.control_id)
    piv = df.pivot(index="control_id", columns="vendor", values="residual_risk")
    cov = df.pivot(index="control_id", columns="vendor", values="coverage")
    hdr = ["Control", "Atlassian", "Greenhouse", "Notion"]
    rows_ = []
    for c in order_c:
        row = [esc(c)]
        for v in ["Atlassian", "Greenhouse Software", "Notion"]:
            sc = int(piv.loc[c, v]); cv = cov_word(cov.loc[c, v])
            row.append(rf"\ratingcell{{{sc}}} {cv}")
        rows_.append(row)
    tex.append(longtable_str(hdr, rows_, "L{2.9cm}L{3.6cm}L{3.6cm}L{3.6cm}", small=True))

    tex.append(r"\section{High residual items}")
    hi = df[df.residual_rating.isin(["High", "Critical"])].sort_values(["residual_risk", "tier"], ascending=[False, True])
    hdr = ["Vendor", "Control", "Coverage", "L x I", "Rating", "Why"]
    rows_ = []
    for _, x in hi.iterrows():
        rows_.append([esc(x.vendor), esc(f"{x.control_id} {x.requirement}"),
                      esc(x.coverage + (" (source-limited)" if x.reviewer_limited == "Y" else "")),
                      f"{x.residual_likelihood}x{x.impact}={x.residual_risk}", esc(x.residual_rating), esc(x.analyst_rationale)])
    tex.append(longtable_str(hdr, rows_, "L{1.8cm}L{2.9cm}L{2.0cm}C{1.1cm}L{1.2cm}L{5.1cm}", small=True))

    tex.append(r"\section{Domain view}")
    dom = df.groupby(["domain", "vendor"]).agg(n=("control_id", "count"), partial=("coverage", lambda x: int((x != "Addressed").sum()))).reset_index()
    pv = dom.pivot(index="domain", columns="vendor", values="partial").fillna(0).astype(int)
    cnt = df[df.vendor == "Notion"].groupby("domain").size()
    hdr = ["Domain (non-Addressed / total)", "Atlassian", "Greenhouse", "Notion"]
    rows_ = []
    for d in pv.index:
        rows_.append([esc(d), f"{pv.loc[d,'Atlassian']} / {cnt[d]}", f"{pv.loc[d,'Greenhouse Software']} / {cnt[d]}", f"{pv.loc[d,'Notion']} / {cnt[d]}"])
    tex.append(longtable_str(hdr, rows_, "L{6.2cm}C{2.6cm}C{2.6cm}C{2.6cm}", small=False))
    tex.append(r"\clearpage")


    # ---------------------------------------------------------- 5 vendor findings
    tex.append(r"\chapter{Vendor findings}")

    def vend(name, strengths, gaps, events, actions):
        g = df[df.vendor == name]
        tex.append(rf"\section{{{esc(name)}}}")
        tex.append(esc(f"Tier {int(g.tier.iloc[0])} ({g.tier_label.iloc[0]}). Use case: "
                        f"{prof[prof.vendor==name].assumed_use_case.iloc[0]}. Impact-weighted coverage "
                        f"{S.loc[name,'impact_weighted_coverage_pct']}%; {int(S.loc[name,'high'])} High residual item(s)."))
        tex.append(r"\subsection*{Strengths}")
        tex.append(r"\begin{itemize}")
        for b in strengths:
            tex.append(rf"\item {esc(b)}")
        tex.append(r"\end{itemize}")
        tex.append(r"\subsection*{Gaps and caveats}")
        tex.append(r"\begin{itemize}")
        for b in gaps:
            tex.append(rf"\item {esc(b)}")
        tex.append(r"\end{itemize}")
        if events:
            tex.append(r"\subsection*{Notable public events}")
            tex.append(r"\begin{itemize}")
            for b in events:
                tex.append(rf"\item {esc(b)}")
            tex.append(r"\end{itemize}")
        tex.append(r"\subsection*{Recommended next steps}")
        tex.append(r"\begin{itemize}")
        for b in actions:
            tex.append(rf"\item {esc(b)}")
        tex.append(r"\end{itemize}")

    vend("Atlassian",
         ["Contractual exhibit (effective 7 Oct 2025) states least privilege, MFA, AES-256/TLS 1.2+, quarterly DR tests validated by external auditors, environment separation and a supplier-risk framework, with numbered sections that make every claim citable.",
          "Public IAM reference architecture (1 Sep 2026) and built-in-controls guide describe customer-side SSO, MFA, SCIM and SIEM-integrated audit logging.",
          "Bug bounty (Bugcrowd), published advisories and bulletins, and a CVSS-based bugfix policy."],
         ["SOC 2 Type II reports listed are product-specific (Jira, Confluence). The FY26 report (1 Oct 2024 to 30 Sep 2025) was announced as due December 2025; no issuance notice was visible.",
          "No access-review cadence, no fixed incident-notification hours, no post-termination deletion period, no RTO/RPO values.",
          "Advanced identity controls depend on Atlassian Guard licensing (plan dependency).",
          "Least-privilege and environment-separation evidence rests on the contractual exhibit rather than on the migration-only white paper or on tenant isolation, which is a different control."],
         [],
         ["Read the FY26 SOC 2 reports for every in-scope product; obtain bridge letter and FY27 timeline.", "Negotiate notification window and deletion timeframe; confirm Guard plan and cost.", "Request latest pentest executive summary (only an annual statement is public)."])

    vend("Greenhouse Software",
         ["Broadest independent artifact listing: SOC 2 Type 2 and SOC 1 Type 2 (2025), ISO 27001:2022, ISO 27701:2019, ISO 42001:2023 (announced Feb 2026), and three dated pentest artifacts (Q3 2025, Q1 2026, Q2 2026).",
          "30 subprocessors with location and purpose, updated 1 Sep 2026; DPF transfer mechanisms stated.",
          "Prompt, transparent vulnerability response (CVE-2025-55182, Dec 2025)."],
         ["Nine controls are reviewer-limited: the Access, Cloud Security, Continuity, Vendor Management, Secure Development, Incident and Privacy FAQs were indexed (251 answers) but not read.",
          "MFA enforcement, encryption parameters, RTO/RPO and access-review evidence are not visible on the pages reviewed.",
          "The 1 Sep 2026 'last updated' date applies to the subprocessor list only, not to the whole Trust Center.",
          "PCI evidence is a self-assessment questionnaire and SIG Lite is a self-attestation; neither is independent assurance."],
         ["Klue third-party incident (announced 24 Jun 2026): attackers obtained credentials Klue used to connect to Greenhouse business systems on 11 Jun 2026; exposure limited to business contact data in sales/CRM systems; no candidate or hiring data; authorities notified; investigation ongoing. This is a realised supply-chain event and drives the +1 uplift on SUP-01."],
         ["Request the Klue root-cause summary and integration-credential controls (rotation, scoping, monitoring).", "Read the seven FAQ sections and re-score; confirm MFA can be enforced for all users.", "Ask for the 2026 Onboarding pentest retest (last report Q3 2025) and SOC 2 period end date."])

    vend("Notion",
         ["16 control categories published with parameters: TLS 1.2+, AES-256 including backups, customer-managed keys, access review at least quarterly, access removal within 24 hours, 72-hour standard breach notification, annual IR and BC/DR testing.",
          "Public HackerOne bug bounty; 2026 pentest reports (web, mobile, desktop, Calendar, Mail) and July 2026 CAIQ/VSA/HECVAT listed.",
          "Detailed AI governance controls including retention limits (30/60 days), kill switch and no-training commitments."],
         ["All reports are request-gated; statements are vendor-authored and unverified.",
          "ISO 27701, 27017 and 27018 are claimed in the header and security page, but only the ISO 27001 certificate and Statement of Applicability are listed as documents.",
          "General retention/deletion timeframes and a cross-border transfer mechanism are not stated; insurance evidence is dated 2025 and valid until November 2026.",
          "AI/LLM and search subprocessors increase fourth-party exposure; current Atlassian AI safeguards are now explicitly reviewed."],
         [],
         ["Request SOC 2 report and ISO 27701/27018 certificates; confirm 72-hour notice meets client needs.", "Ask for deletion timeframe and transfer mechanism; request cyber-insurance certificate before November 2026 expiry.", "Review the AI-provider list and the no-training contractual terms."])
    tex.append(r"\clearpage")

    # ---------------------------------------------------------- 6 cross-vendor
    tex.append(r"\chapter{Cross-vendor observations}")
    tex.append(r"\begin{itemize}")
    for b in [
        "\\textbf{Disclosure asymmetry.} Notion's Trust Center shows control-level detail on one page; Greenhouse and Atlassian expose FAQ counts (251 and 169) and gated documents. A reader comparing scores should distinguish public transparency from independent assurance.",
        "\\textbf{Assurance artifacts are gated.} For all three vendors the SOC 2 report contents, audit period and exceptions are invisible. A listed report supports level 3 evidence of existence, not of effectiveness.",
        "\\textbf{Time-bound artifacts.} Atlassian FY26 SOC 2 currency (unconfirmed), Greenhouse Onboarding pentest age (about 12 months), and Notion insurance evidence (expires November 2026) each need a diary date.",
        "\\textbf{AI and fourth-party concentration.} LLM hosting providers appear in the subprocessor lists of Greenhouse (Anthropic, OpenAI) and Notion (a dozen providers). Client data flows to those providers under vendor-level contracts the client cannot audit directly. Only Greenhouse holds an independent AI management-system certificate (ISO 42001).",
        "\\textbf{Binary features versus parameters.} Several 'has X' checklist ticks (annual pentest, DR plan, cyber insurance, centralised SSO) are workforce-level assertions. They were kept at evidence level 1 unless a parameter or artifact backed them.",
        "\\textbf{Common contractual gaps.} Deletion timing remains a substantive contractual/product-documentation gap where the public DPA does not give a fixed period; incident-notification and subprocessor-notice terms are now evidenced for Atlassian.",
    ]:
        tex.append(rf"\item {esc(b)}")
    tex.append(r"\end{itemize}")

    # ---------------------------------------------------------- 7 sensitivity
    tex.append(r"\chapter{Sensitivity analysis}")
    tex.append(esc("The ranking of vendors should hold under reasonable changes to the assumptions. The table shows "
               "the number of High or Critical residual items (out of 27) under alternative treatments."))
    hdr = ["Vendor", "Base case", "Limited favourable", "Limited adverse", "No adverse uplift"]
    rows_ = []
    for _, x in sens.iterrows():
        rows_.append([esc(x.vendor), str(int(x.base)), str(int(x.reviewer_limited_resolved_favourably)),
                      str(int(x.reviewer_limited_resolved_adversely)), str(int(x.without_adverse_event_uplift))])
    tex.append(longtable_str(hdr, rows_, "L{3.6cm}C{2.4cm}C{2.9cm}C{2.6cm}C{2.9cm}", small=False))
    tex.append(r"\begin{note}No vendor/control row remains reviewer-limited in this updated run, so the two limited-source sensitivity columns now equal the base case. Remaining sensitivity is driven by substantive control uncertainty and the documented Klue adverse-event uplift.\end{note}")
    tex.append(r"\clearpage")

    # ---------------------------------------------------------- 8 limitations
    tex.append(r"\chapter{Limitations, bias and independence}")
    tex.append(r"\begin{itemize}")
    for b in [
        "\\textbf{Public evidence only.} Gated audit reports remain listed rather than reviewed; Atlassian's current public DPA was reviewed. Nothing here is an audit, certification opinion, penetration test or legal advice.",
        "\\textbf{Remaining source limitations.} Gated audit reports and some vendor documentation remain unavailable without access requests. No assessment row remains reviewer-limited after the current source review; remaining gaps are substantive (for example, Greenhouse IAM-04 and Atlassian DAT-02).",
        "\\textbf{Vendor-authored statements are unverified.} Even level 2 evidence is a claim by the vendor. Independent verification needs the SOC 2 report or a technical test.",
        "\\textbf{Point in time.} Trust Centers change. Findings in this updated run use the original 24 September 2026 snapshot plus sources reviewed on 4 October 2026. Sources are cited by URL and section; no archived snapshots were taken (recommended improvement).",
        "\\textbf{Assumptions drive the numbers.} Impact values, tier factors, likelihood mapping and bands are project-defined and documented in Section~3; they are not ISO or NIST thresholds.",
        "\\textbf{Scope gaps.} FOCI and provenance (SP 1326) were not assessed; nor were concentration risk, financial health, litigation, breach history beyond vendor announcements, or technical attack-surface signals.",
        "\\textbf{Independence.} Findings were derived from cited public text; readers should apply their own judgement and verify anything material before relying on it.",
    ]:
        tex.append(rf"\item {esc(b)}")
    tex.append(r"\end{itemize}")

    # ---------------------------------------------------------- 9 treatment
    tex.append(r"\chapter{Risk treatment plan and monitoring}")
    tex.append(r"\section{Evaluation criteria (ISO 31000 risk evaluation)}")
    hdr = ["Rating", "Proposed treatment rule (project assumption)"]
    rows_ = [
        ["Critical", "Do not onboard or renew without executive-approved treatment plan and compensating controls."],
        ["High", "Treatment plan with owner and date before onboarding; renewal only if closed or formally accepted by the business owner."],
        ["Medium", "Accept with monitoring; validate at next scheduled review."],
        ["Low", "Accept."],
    ]
    tex.append(longtable_str(hdr, [[esc(c) for c in r] for r in rows_], "L{2.0cm}L{12.0cm}", small=False))

    tex.append(r"\section{Prioritised actions}")
    hdr = ["\\#", "Action", "Vendors", "Treatment", "Timing"]
    rows9 = [
        ["1", "Obtain and read SOC 2 Type II reports and bridge letters; record scope, period, exceptions and complementary user-entity controls", "All (Atlassian first)", "Mitigate -- validate", "30 days"],
        ["2", "Contract: incident-notification hours, post-termination deletion timeframe, sub-processor change notice and objection right", "All", "Mitigate -- contract", "Before signature/renewal"],
        ["3", "Greenhouse: Klue root-cause summary; integration-credential rotation and scoping; confirm MFA enforcement", "Greenhouse", "Mitigate -- validate", "30 days"],
        ["4", "Retrieve and read vendor FAQ sections marked reviewer-limited, then re-score", "Greenhouse, Atlassian", "Reduce uncertainty", "30 days"],
        ["5", "Request pentest executive summaries or letters (Atlassian) and 2026 Onboarding retest (Greenhouse)", "Atlassian, Greenhouse", "Mitigate -- validate", "60 days"],
        ["6", "Request RTO/RPO values and last DR test evidence", "All", "Mitigate -- validate", "60 days"],
        ["7", "Confirm data-residency options and transfer mechanism; verify DPF registry entries", "All", "Mitigate -- contract", "60 days"],
        ["8", "Verify ISO 27001:2022 certificate scope and expiry with the certification body; request ISO 27701/27018 certificates where claimed", "All", "Mitigate -- validate", "60 days"],
        ["9", "Client-side configuration baseline: enforce SSO and MFA, restrict SMS, restrict marketplace apps and AI features, enable audit-log export to SIEM", "All", "Mitigate -- configure", "90 days"],
        ["10", "Request cyber-insurance certificates and note renewal dates", "All", "Transfer -- verify", "90 days"],
        ["11", "Enhanced due diligence for Atlassian (Tier 1): FOCI, provenance, questionnaire, technical review of Marketplace app governance", "Atlassian", "Reduce uncertainty", "90 days"],
    ]
    tex.append(longtable_str(hdr, [[esc(c) for c in r] for r in rows9], "C{0.5cm}L{5.6cm}L{2.6cm}L{2.6cm}L{2.2cm}", small=True))

    tex.append(r"\section{Monitoring triggers}")
    tex.append(r"\begin{itemize}")
    for b in ["Annual re-assessment (Tier 1 vendors: every 6 months for Trust Center changes).",
              "Subscribe to each Trust Center's update feed; review new incident announcements within 5 working days.",
              "Date-driven: Atlassian FY27 SOC 2 period ends 30 Sep 2026; Notion insurance evidence expires Nov 2026; Greenhouse Klue investigation update; Greenhouse Onboarding pentest renewal.",
              "Event-driven: security incident, subprocessor or AI-provider change, acquisition, new product in scope, loss of a certification."]:
        tex.append(rf"\item {esc(b)}")
    tex.append(r"\end{itemize}")
    tex.append(r"\clearpage")

    # ---------------------------------------------------------- 10 improvements
    tex.append(r"\chapter{Recommended further improvements to this project}")
    tex.append(r"\begin{itemize}")
    for b in ["\\textbf{Archive evidence.} Save dated PDF/HTML snapshots of each source page (or use a web-archive service) so findings survive Trust Center changes.",
              "\\textbf{Retrieve remaining gated assurance artifacts} (SOC 2 reports, bridge letters and any restricted policies) and re-run the scoring; the current public-source review no longer has reviewer-limited assessment rows.",
              "\\textbf{Add enhanced due diligence inputs}: FOCI/ownership, provenance, breach history in public databases, external attack-surface scoring, and the actual SOC 2 reports.",
              "\\textbf{Second-reviewer check.} Have a second analyst score a sample of rows blind to measure agreement.",
              "\\textbf{Weighting by client data flows} (which module, which data class) instead of one impact value per control.",
              "\\textbf{Track over time.} Store each assessment run so that changes between quarters are visible.",
              "\\textbf{Automate change detection} on Trust Center pages and announcements to trigger re-assessment."]:
        tex.append(rf"\item {esc(b)}")
    tex.append(r"\end{itemize}")
    tex.append(r"\clearpage")

    # ---------------------------------------------------------- Appendix A
    tex.append(r"\appendix")
    tex.append(r"\chapter{Control catalogue and framework mapping}")
    hdr = ["ID", "Requirement", "I", "ISO 27001:2022", "CSF 2.0", "SP 800-53r5", "SOC 2", "SP 1326"]
    rows_ = []
    for _, x in cat.iterrows():
        rows_.append([esc(x.control_id), esc(x.requirement), str(x.impact), esc(x.iso27001_2022_annexA),
                      esc(x.nist_csf_2_0), esc(x.nist_sp800_53_r5), esc(x.soc2_tsc), esc(x.sp1326_component)])
    tex.append(longtable_str(hdr, rows_, "L{1.4cm}L{3.0cm}C{0.4cm}L{2.3cm}L{2.0cm}L{2.0cm}L{1.6cm}L{2.0cm}", small=True))
    tex.append(r"{\footnotesize Mappings are indicative cross-references prepared for this project. They are not "
               r"official crosswalks and standard text is not reproduced (ISO texts are paywalled). Impact (I) is "
               r"1--5.\par}")
    tex.append(r"\clearpage")

    # ---------------------------------------------------------- Appendix B
    tex.append(r"\chapter{Full assessment matrix}")
    for v in ["Atlassian", "Greenhouse Software", "Notion"]:
        g = df[df.vendor == v]
        tex.append(rf"\section{{{esc(v)}}}")
        hdr = ["Ctrl.", "Coverage", "Ev.", "L", "I", "Score", "Rating", "Evidence IDs", "Rationale / flag"]
        rows_ = []
        for _, x in g.iterrows():
            flag = (" [source-limited]" if x.reviewer_limited == "Y" else "") + (" [adverse +1]" if x.adverse_event == "Y" else "")
            rows_.append([esc(x.control_id), esc(x.coverage), str(x.evidence_level), str(x.residual_likelihood),
                          str(x.impact), rf"\ratingcell{{{x.residual_risk}}}", esc(x.residual_rating),
                          esc(x.evidence_ids.replace(";", ", ")), esc(x.analyst_rationale) + esc(flag)])
        tex.append(longtable_str(hdr, rows_, "L{1.1cm}L{1.4cm}C{0.4cm}C{0.4cm}C{0.4cm}C{0.8cm}L{1.0cm}L{2.0cm}L{4.7cm}", small=True))
    tex.append(r"\clearpage")

    # ---------------------------------------------------------- Appendix C
    tex.append(r"\chapter{Evidence register}")
    tex.append(esc("Findings are paraphrased from public pages retrieved on 24 September 2026. Source IDs resolve "
               "in Appendix D. Level: 3 independent, 2 vendor-specific, 1 assertion."))
    hdr = ["ID", "Src", "Locator", "Finding (paraphrased)", "Lvl", "Limitation"]
    rows_ = []
    for _, x in ev.iterrows():
        rows_.append([esc(x.evidence_id.replace("EV-", "")), esc(x.source_id.replace("S-", "")), esc(x.locator),
                      esc(x.finding_paraphrased), str(x.evidence_level), esc(x.limitation)])
    tex.append(longtable_str(hdr, rows_, "L{1.3cm}L{1.0cm}L{2.1cm}L{4.6cm}C{0.5cm}L{3.2cm}", small=True))
    tex.append(r"\clearpage")

    # ---------------------------------------------------------- Appendix D
    tex.append(r"\chapter{Source register}")
    hdr = ["ID", "Publisher / title", "URL", "Type", "Gr.", "Date shown", "Retrieved / depth", "Limitations"]
    rows_ = []
    for _, x in src.iterrows():
        rows_.append([esc(x.source_id), esc(x.vendor_or_publisher) + " -- " + esc(x.title), rf"{{\tiny\seqsplit{{{esc_plain(x.url)}}}}}",
                      esc(x.source_type), str(x.reliability_grade), esc(x.published_or_effective_date),
                      f"{x.retrieved_on}; {esc(x.depth_of_review)}", esc(x.limitations)])
    tex.append(longtable_str(hdr, rows_, "L{1.0cm}L{2.4cm}L{2.9cm}L{1.2cm}C{0.4cm}L{1.6cm}L{1.7cm}L{2.5cm}", small=True))

    tex.append(r"\chapter{Framework and standards references}")
    hdr = ["ID", "Publisher", "Title", "Version / date", "URL", "Role"]
    rows_ = []
    for _, x in fw.iterrows():
        rows_.append([esc(x.source_id), esc(x.publisher), esc(x.title), esc(x.version_or_date), rf"{{\tiny\seqsplit{{{esc_plain(x.url)}}}}}", esc(x.role_in_this_project)])
    tex.append(longtable_str(hdr, rows_, "L{1.2cm}L{1.3cm}L{3.0cm}L{1.5cm}L{3.0cm}L{3.5cm}", small=True))
    tex.append(r"\clearpage")

    # ---------------------------------------------------------- Appendix F
    tex.append(r"\chapter{Vendor follow-up request list}")
    tex.append(esc("Ordered by residual score within each vendor. Each request targets a Partial or Not-evidenced control."))
    for v in ["Atlassian", "Greenhouse Software", "Notion"]:
        g = fu[fu.vendor == v]
        tex.append(rf"\section{{{esc(v)}}}")
        hdr = ["Control", "Rating", "Request"]
        rows_ = []
        for _, x in g.iterrows():
            rows_.append([esc(f"{x.control_id} {x.requirement}") + (" (source-limited)" if x.reviewer_limited == "Y" else ""),
                          esc(x.residual_rating), esc(x.follow_up_action)])
        tex.append(longtable_str(hdr, rows_, "L{4.3cm}C{1.4cm}L{8.3cm}", small=True))

    tex.append(r"\end{document}")

    (TEX / "report.tex").write_text("\n".join(tex), encoding="utf-8")
    print("wrote", TEX / "report.tex")


if __name__ == "__main__":
    main()
