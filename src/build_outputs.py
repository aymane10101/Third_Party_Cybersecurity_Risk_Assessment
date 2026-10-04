"""Regenerates every derived CSV from the analyst inputs. Never edit derived files by hand."""
from pathlib import Path
import pandas as pd
import scoring

DATA = scoring.DATA


def main():
    df = scoring.load_assessment()
    evidence = pd.read_csv(DATA / "evidence_register.csv").set_index("evidence_id")
    df["evidence_locators"] = df.evidence_ids.apply(
        lambda s: " | ".join(f"{e}: {evidence.loc[e,'source_id']} - {evidence.loc[e,'locator']}" for e in s.split(";")))
    cols = ["vendor", "control_id", "domain", "requirement", "coverage", "evidence_level", "confidence",
            "reviewer_limited", "adverse_event", "impact", "inherent_likelihood", "inherent_risk", "inherent_rating",
            "residual_likelihood", "residual_risk", "residual_rating", "evidence_ids", "evidence_locators",
            "analyst_rationale", "follow_up_action"]
    df[cols].to_csv(DATA / "assessment_matrix.csv", index=False)
    scoring.vendor_summary(df).to_csv(DATA / "vendor_summary.csv", index=False)
    scoring.sensitivity(df).to_csv(DATA / "sensitivity_analysis.csv", index=False)

    fu = df[(df.coverage != "Addressed") | (df.follow_up_action.str.len() > 0)].copy()
    fu = fu[fu.coverage != "Addressed"]
    fu = fu.sort_values(["vendor", "residual_risk", "evidence_level"], ascending=[True, False, True])
    fu[["vendor", "control_id", "requirement", "coverage", "residual_rating", "reviewer_limited", "follow_up_action"]] \
        .to_csv(DATA / "followup_requests.csv", index=False)


if __name__ == "__main__":
    main()
