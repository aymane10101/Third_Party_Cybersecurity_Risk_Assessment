"""Generates latex/explainer.tex (the project-overview document) from the data files,
then compiles it with pdflatex into reports/Project_Explainer.pdf.
"""
from pathlib import Path
import pandas as pd
from latex_common import esc, esc_plain, PREAMBLE, fancy_header, longtable_str

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT, TEX = ROOT / "data", ROOT / "reports", ROOT / "latex"


def main():
    src = pd.read_csv(DATA / "source_register.csv")
    fw = pd.read_csv(DATA / "framework_register.csv")
    TEX.mkdir(exist_ok=True)

    tex = [PREAMBLE]
    tex.append(fancy_header("Third-Party Cybersecurity Risk Assessment", "Project Overview"))
    tex.append(r"\begin{document}")

    # ---- cover
    tex.append(r"\begin{titlepage}")
    tex.append(r"\centering")
    tex.append(r"\vspace*{3cm}")
    tex.append(r"{\Huge\bfseries Third-Party Cybersecurity\\[4pt] Risk Assessment\par}")
    tex.append(r"\vspace{0.8cm}")
    tex.append(r"{\Large Project Overview\par}")
    tex.append(r"\vspace{0.3cm}")
    tex.append(r"{\large What this is, how it works, and where every piece of information came from\par}")
    tex.append(r"\vspace{2.5cm}")
    tex.append(r"\renewcommand{\arraystretch}{1.5}")
    tex.append(r"\begin{tabularx}{0.92\textwidth}{L{0.32\textwidth} X}")
    tex.append(r"\toprule")
    tex.append(r"\textbf{Document control} & \\")
    tex.append(r"\midrule")
    rows = [
        ("What this is", "A companion explainer to the risk-assessment report and repository. Read this first if you are new to the project."),
        ("Companion documents", "Third_Party_Cyber_Risk_Assessment_Report.pdf (the full findings report) and the source code / data repository"),
        ("Prepared", "4 October 2026"),
        ("Nature of the project", "Educational / portfolio demonstration of a third-party cyber-risk due-diligence workflow. Not a commissioned audit."),
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

    # ---- 1 what is this
    tex.append(r"\chapter{What this project is}")
    tex.append(esc("This is a worked example of third-party (vendor) cybersecurity risk assessment - the process an "
               "organisation uses to decide how much to trust a supplier with its data and systems, before signing "
               "a contract and periodically afterwards. It answers, for three real SaaS vendors, one question a "
               "security or procurement team would actually ask: \u201cbased on what this vendor makes public, how "
               "confident can we be in their security controls, and what should we ask them for before we rely on "
               "them?\u201d"))
    tex.append(esc("The project is built around three real, currently operating vendors - Atlassian (Jira / "
               "Confluence / Jira Service Management), Greenhouse Software (applicant tracking and onboarding) and "
               "Notion (workspace / wiki with AI features) - assessed against a client scenario that is fictional: "
               "an invented multinational enterprise of about 3,000 staff. The vendors are real and the evidence "
               "about them is real and cited; the client and its specific use of each vendor are an assumption "
               "used to size business impact, and are labelled as such throughout."))
    tex.append(r"\section*{Why this exists}")
    tex.append(r"\begin{itemize}")
    for b in ["To demonstrate a repeatable, evidence-based due-diligence method rather than a one-off opinion: every conclusion traces back to a specific, dated, public web page.",
              "To show how public evidence should be graded rather than taken at face value - a marketing-page sentence, a badge, and a listed independent audit report are not the same strength of evidence, and the project scores them differently.",
              "To practise and demonstrate applying recognised frameworks (NIST, ISO, SOC 2) to a concrete, current scenario rather than reciting them abstractly.",
              "As a portfolio artifact: the repository is written so that another person can inspect every input, re-run the scoring, and regenerate the report from scratch."]:
        tex.append(rf"\item {esc(b)}")
    tex.append(r"\end{itemize}")
    tex.append(r"\section*{What this project is \textbf{not}}")
    tex.append(r"\begin{itemize}")
    for b in ["Not an audit, a penetration test, a certification opinion, or legal advice.",
              "Not a statement that any assessed vendor is or is not secure. It is a statement about what could be verified from public sources on one specific date (4 October 2026), and about what to ask for next.",
              "Not a live or continuously monitored assessment - Trust Center pages change, and this is a single snapshot."]:
        tex.append(rf"\item {esc(b)}")
    tex.append(r"\end{itemize}")
    tex.append(r"\clearpage")

    # ---- 2 structure
    tex.append(r"\chapter{What is inside the project}")
    tex.append(esc("The project is a small data pipeline, not just a document: a set of input tables, a scoring "
               "script, and a report-builder that reads the tables and produces the PDF. Nothing in the report is "
               "typed by hand into the PDF - it is generated from the CSV files below, so the numbers in the "
               "report and the numbers in the data always agree."))
    hdr = ["Folder / file", "What it holds"]
    rows_ = [
        ["data/control\\_catalog.csv", "27 security controls the vendors are judged against, each mapped to ISO 27001:2022, NIST CSF 2.0, NIST SP 800-53, SOC 2 and an NIST SP 1326 category"],
        ["data/source\\_register.csv", "Every web page used as a source: publisher, exact URL, source type, a reliability grade (A+ to C), the date shown on the page, the date it was retrieved, and how thoroughly it was read"],
        ["data/framework\\_register.csv", "Every standard/framework referenced (NIST, ISO, AICPA, GDPR) with its official title, version and URL"],
        ["data/evidence\\_register.csv", "68 individual factual findings, each one paraphrased from a specific source and page section, graded by evidence strength, with its own limitation noted"],
        ["data/vendor\\_profiles.csv", "The fictional client's assumed use of each vendor, and the resulting inherent-risk tier"],
        ["data/assessment\\_inputs.csv", "The only hand-authored judgement file: for every vendor/control pair, the coverage status, evidence strength, and which evidence items support it"],
        ["data/assessment\\_matrix.csv, vendor\\_summary.csv,\\newline sensitivity\\_analysis.csv, followup\\_requests.csv", "All generated automatically from assessment_inputs.csv by the scripts below - never hand-edited"],
        ["src/scoring.py", "The risk-scoring rules (turns coverage + evidence strength into a likelihood, then a risk score and rating)"],
        ["src/validate.py", "Checks that every citation actually resolves and every vendor has been scored against every control"],
        ["src/build\\_outputs.py", "Regenerates every derived CSV from the input tables"],
        ["src/build\\_latex\\_report.py,\\newline src/build\\_latex\\_explainer.py", "Generate the .tex sources for the two PDFs (findings report, and this overview) from the CSVs, then compile them"],
        ["tests/test\\_scoring.py", "Automated tests for the scoring rules"],
        ["docs/methodology.md, evidence\\_collection.md", "Longer-form written methodology, and notes on how each vendor's evidence was gathered"],
        ["reports/, latex/", "The two PDFs and their LaTeX sources"],
    ]
    tex.append(longtable_str(hdr, [[a, esc(b)] for a, b in rows_], "L{5.0cm}L{10.0cm}", small=True))
    tex.append(r"\clearpage")

    # ---- 3 pipeline
    tex.append(r"\chapter{How the assessment was actually produced, step by step}")
    steps = [
        ("Define the fictional client scenario", "An assumed multinational enterprise and a plausible use case for each vendor (e.g. Jira/Confluence for engineering delivery) were written down first, before any scoring, so that impact judgements have a stated basis (data/vendor_profiles.csv)."),
        ("Build the control catalogue", "27 controls across 9 domains (governance, identity, data protection, vulnerability management, incident response, continuity, secure development, third-party risk, assurance) were selected and mapped to ISO/IEC 27001:2022, NIST CSF 2.0, NIST SP 800-53 Rev. 5 and SOC 2 (data/control_catalog.csv)."),
        ("Retrieve public evidence", "Each vendor's public Trust Center and, where available, a published contractual security exhibit were fetched directly (not from memory) and read. Marketing pages and support articles were used as secondary sources where they were found via a live web search. Every page is logged in data/source_register.csv with its exact URL, the date it was retrieved, and whether it was read in full or only as a search excerpt."),
        ("Record each finding as evidence", "Every individual fact extracted from a source - a stated control, a listed certificate, a disclosed incident - was written down once, paraphrased in the analyst's own words, tagged to its exact source and page section, and graded for strength (data/evidence_register.csv)."),
        ("Judge coverage per vendor per control", "For each of the 81 vendor/control combinations, the evidence was judged as Addressed, Partial, or Not evidenced, with a written one-line rationale and the specific evidence IDs relied on (data/assessment_inputs.csv). This is the one file in the whole project that is a human judgement call; everything else is either a source citation or a calculation."),
        ("Score the risk", "A script (src/scoring.py) turns each coverage judgement into a likelihood, multiplies by a pre-set impact value, and bands the result Low/Medium/High/Critical - the same rule applied consistently to all 81 rows, so no vendor is scored more leniently than another."),
        ("Check the citations", "src/validate.py automatically checks that every evidence ID used in the scoring actually exists in the evidence register, belongs to the right vendor, and that every vendor has in fact been scored on every one of the 27 controls."),
        ("Generate the outputs", "src/build_outputs.py writes the derived CSVs, and the two build_latex_*.py scripts turn those CSVs into LaTeX source, which is compiled to the two PDFs. Re-running these scripts on the same input files reproduces the same conclusions."),
    ]
    for i, (t, d) in enumerate(steps, 1):
        tex.append(rf"\subsection*{{{i}. {esc(t)}}}")
        tex.append(esc(d))
    tex.append(r"\clearpage")

    # ---- 4 sources
    tex.append(r"\chapter{Where the information came from}")
    tex.append(esc("This is the chapter that matters most for verifying the project. Every factual claim about a "
               "vendor in the risk-assessment report traces to one of the sources below, via an evidence ID "
               "recorded in data/evidence_register.csv. Nothing about vendor security controls was taken from "
               "general knowledge - it was read from the specific, live pages listed here on the retrieval date "
               "shown. Standards (NIST, ISO, SOC 2, GDPR) are cited separately in Section 4.2 and their text is "
               "not reproduced (ISO standards in particular are paywalled)."))
    tex.append(r"\section{Vendor evidence sources (retrieved 4 October 2026)}")
    tex.append(esc("Grade: A+ = a public contractual document; A = the vendor's full Trust Center page, fetched "
               "in full; B = a vendor marketing/documentation page; C = a partial excerpt or a page containing "
               "some stale information. \u201cDepth\u201d states plainly whether the whole page was read or only "
               "a short search-result excerpt was seen."))
    for _, x in src.iterrows():
        tex.append(rf"\subsection*{{{esc(x.source_id)} --- {esc(x.vendor_or_publisher)}}}")
        hdr = ["Field", "Value"]
        rows_ = [
            ["Title", x.title],
            ["URL", None],
            ["Type / grade", f"{x.source_type} / {x.reliability_grade}"],
            ["Date shown on page", x.published_or_effective_date],
            ["Retrieved on", str(x.retrieved_on)],
            ["Depth of review", x.depth_of_review],
            ["What it was used for", x.what_it_is_used_for],
            ["Limitations", x.limitations],
        ]
        body = []
        for k, v in rows_:
            if k == "URL":
                body.append([esc(k), rf"{{\small\seqsplit{{{esc_plain(x.url)}}}}}"])
            else:
                body.append([esc(k), esc(v)])
        tex.append(longtable_str(hdr, body, "L{3.0cm}L{10.5cm}", small=True, zebra=False))
    tex.append(r"\clearpage")

    tex.append(r"\section{Standards and frameworks referenced}")
    tex.append(esc("These are established, independently published frameworks used to structure and cross-"
               "reference the assessment. They were not used as evidence about any vendor - they define what "
               "\u201cgood\u201d looks like, against which the vendor evidence above was judged."))
    hdr = ["ID", "Publisher", "Title", "Version / date", "URL"]
    rows_ = []
    for _, x in fw.iterrows():
        rows_.append([esc(x.source_id), esc(x.publisher), esc(x.title), esc(x.version_or_date),
                      rf"{{\tiny\seqsplit{{{esc_plain(x.url)}}}}}"])
    tex.append(longtable_str(hdr, rows_, "L{1.5cm}L{1.5cm}L{4.6cm}L{2.1cm}L{3.3cm}", small=True))
    tex.append(esc("The full 68-item evidence register (which finding came from which source and page section) "
               "is reproduced in Appendix C of the risk-assessment report, and is available in full in "
               "data/evidence_register.csv."))
    tex.append(r"\clearpage")

    # ---- 5 methodology summary
    tex.append(r"\chapter{Methodology, in brief}")
    tex.append(esc("Full detail is in docs/methodology.md and Section 3 of the risk-assessment report. In short:"))
    tex.append(r"\begin{itemize}")
    for b in [
        "Each fact is graded by evidence strength: \\textbf{3} an independent attestation/certificate/test report is listed; \\textbf{2} a specific vendor-authored statement or a published contract exhibit; \\textbf{1} a summary badge or checklist assertion; \\textbf{0} nothing found.",
        "Each control, per vendor, is rated \\textbf{Addressed} (explicitly and specifically supported), \\textbf{Partial} (named but missing detail or scope), or \\textbf{Not evidenced} (nothing found in the sources reviewed - which is a limit of this review, not proof the control is missing).",
        "Residual risk = likelihood (from the rating above) x impact (pre-set per control, 3-5). Impact and likelihood are combined on a 5x5 matrix into Low / Medium / High / Critical.",
        "Where a relevant source exists but is not read in full (for example, a gated audit report or FAQ body), the row is flagged so the reader knows the gap is a research limitation, not a finding. In the current run, no assessment row remains reviewer-limited.",
        "A short sensitivity analysis shows how the results would change under different reasonable assumptions, so the reader can judge how solid the conclusions are.",
    ]:
        tex.append(rf"\item {esc(b)}")
    tex.append(r"\end{itemize}")

    # ---- 6 limitations
    tex.append(r"\chapter{Limitations and how to read this project}")
    tex.append(r"\begin{itemize}")
    for b in [
        "This is \\textbf{basic}, publicly-available-information due diligence, as defined by NIST SP 1326 - not enhanced due diligence, which would involve reading the actual (currently gated) audit reports and contracts.",
        "Findings are a snapshot from 4 October 2026. Vendor Trust Centers change; nothing here is monitored continuously.",
        "A vendor that publishes more detail on its public page is not necessarily more secure than one that gates the same detail behind a report request - it is more transparent in this specific, desk-based review. The report itself repeats this caution wherever comparisons are drawn.",
    ]:
        tex.append(rf"\item {esc(b)}")
    tex.append(r"\end{itemize}")
    tex.append(r"\begin{note}For the actual findings, ratings, and recommended next steps for each vendor, see "
               r"Third\_Party\_Cyber\_Risk\_Assessment\_Report.pdf.\end{note}")

    tex.append(r"\end{document}")
    (TEX / "explainer.tex").write_text("\n".join(tex), encoding="utf-8")
    print("wrote", TEX / "explainer.tex")


if __name__ == "__main__":
    main()
