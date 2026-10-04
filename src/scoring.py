"""Scoring model for the third-party cyber risk assessment.

All parameters are project-defined assumptions (see docs/methodology.md).
They are NOT thresholds mandated by ISO or NIST.
"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"

# Residual likelihood of the control not operating as needed, given PUBLIC evidence only.
LIKELIHOOD_BY_COVERAGE = {"Addressed": 2, "Partial": 3, "Not evidenced": 4}
REVIEWER_LIMITED_FLOOR = 3      # absence not established when a source was indexed but not read
ADVERSE_EVENT_UPLIFT = 1        # public, unresolved event that demonstrates a control failure
INHERENT_LIKELIHOOD_BY_TIER = {1: 5, 2: 4, 3: 3}
CONFIDENCE = {3: "High", 2: "Medium", 1: "Low", 0: "None"}
RATING_ORDER = ["Low", "Medium", "High", "Critical"]


def risk_band(score: int) -> str:
    """5x5 matrix bands: 1-4 Low, 5-12 Medium, 13-19 High, 20-25 Critical."""
    if score <= 4:
        return "Low"
    if score <= 12:
        return "Medium"
    if score <= 19:
        return "High"
    return "Critical"


def residual_likelihood(coverage: str, reviewer_limited: str, adverse: str) -> int:
    lik = LIKELIHOOD_BY_COVERAGE[coverage]
    if coverage == "Not evidenced" and reviewer_limited == "Y":
        lik = REVIEWER_LIMITED_FLOOR
    if adverse == "Y":
        lik = min(5, lik + ADVERSE_EVENT_UPLIFT)
    return lik


def load_assessment(data_dir: Path = DATA) -> pd.DataFrame:
    inputs = pd.read_csv(data_dir / "assessment_inputs.csv")
    catalog = pd.read_csv(data_dir / "control_catalog.csv")
    profiles = pd.read_csv(data_dir / "vendor_profiles.csv")
    df = inputs.merge(catalog[["control_id", "domain", "requirement", "impact"]], on="control_id", how="left")
    df = df.merge(profiles[["vendor", "tier", "tier_label"]], on="vendor", how="left")
    df["inherent_likelihood"] = df["tier"].map(INHERENT_LIKELIHOOD_BY_TIER)
    df["inherent_risk"] = df["inherent_likelihood"] * df["impact"]
    df["inherent_rating"] = df["inherent_risk"].apply(risk_band)
    df["residual_likelihood"] = [
        residual_likelihood(c, r, a)
        for c, r, a in zip(df.coverage, df.reviewer_limited, df.adverse_event)
    ]
    df["residual_risk"] = df["residual_likelihood"] * df["impact"]
    df["residual_rating"] = df["residual_risk"].apply(risk_band)
    df["confidence"] = df["evidence_level"].map(CONFIDENCE)
    df["follow_up_priority"] = df.groupby("vendor")["residual_risk"].rank(method="first", ascending=False)
    return df


def vendor_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for vendor, g in df.groupby("vendor", sort=False):
        weighted = g.loc[g.coverage == "Addressed", "impact"].sum() / g["impact"].sum()
        rows.append({
            "vendor": vendor,
            "tier": int(g.tier.iloc[0]),
            "controls": len(g),
            "addressed": int((g.coverage == "Addressed").sum()),
            "partial": int((g.coverage == "Partial").sum()),
            "not_evidenced": int((g.coverage == "Not evidenced").sum()),
            "reviewer_limited": int((g.reviewer_limited == "Y").sum()),
            "independent_evidence_controls": int((g.evidence_level == 3).sum()),
            "impact_weighted_coverage_pct": round(100 * weighted, 1),
            "medium": int((g.residual_rating == "Medium").sum()),
            "high": int((g.residual_rating == "High").sum()),
            "critical": int((g.residual_rating == "Critical").sum()),
            "max_residual": int(g.residual_risk.max()),
        })
    return pd.DataFrame(rows)


def sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    """High+Critical counts under alternative assumptions."""
    out = []
    for vendor, g in df.groupby("vendor", sort=False):
        base = int(g.residual_rating.isin(["High", "Critical"]).sum())
        worst = g.copy()
        worst.loc[worst.reviewer_limited == "Y", "residual_likelihood"] = [
            min(5, 4 + (a == "Y")) for a in worst.loc[worst.reviewer_limited == "Y", "adverse_event"]]
        worst_n = int((worst.residual_likelihood * worst.impact).apply(risk_band).isin(["High", "Critical"]).sum())
        best = g.copy()
        best.loc[best.reviewer_limited == "Y", "residual_likelihood"] = [
            min(5, 2 + (a == "Y")) for a in best.loc[best.reviewer_limited == "Y", "adverse_event"]]
        best_n = int((best.residual_likelihood * best.impact).apply(risk_band).isin(["High", "Critical"]).sum())
        no_adv = g.copy()
        no_adv["residual_likelihood"] = [residual_likelihood(c, r, "N") for c, r in zip(g.coverage, g.reviewer_limited)]
        no_adv_n = int((no_adv.residual_likelihood * no_adv.impact).apply(risk_band).isin(["High", "Critical"]).sum())
        out.append({"vendor": vendor, "base": base,
                    "reviewer_limited_resolved_favourably": best_n,
                    "reviewer_limited_resolved_adversely": worst_n,
                    "without_adverse_event_uplift": no_adv_n})
    return pd.DataFrame(out)
