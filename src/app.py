import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent))
import scoring

DATA = Path(__file__).resolve().parent.parent / "data"

st.set_page_config(page_title="Third-Party Cyber Risk Assessment", layout="wide")
st.title("Third-Party Cybersecurity Risk Assessment")
st.caption("Public-evidence portfolio project — educational, desk-based due diligence. Not an audit.")

df = scoring.load_assessment()
summ = scoring.vendor_summary(df)
evidence = pd.read_csv(DATA / "evidence_register.csv")
sources = pd.read_csv(DATA / "source_register.csv")

vendor = st.selectbox("Vendor", sorted(df["vendor"].unique()))
v = df[df.vendor == vendor].copy()
s = summ.set_index("vendor").loc[vendor]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Tier", f"Tier {int(s.tier)}")
c2.metric("Addressed", int(s.addressed))
c3.metric("Partial", int(s.partial))
c4.metric("Not evidenced", int(s.not_evidenced))
c5.metric("High/Critical residual", int(s.high) + int(s.critical))
st.caption(f"Impact-weighted coverage: {s.impact_weighted_coverage_pct}% · "
           f"{int(s.reviewer_limited)} control(s) limited by a source-review gap (not proof of absence) · "
           f"{int(s.independent_evidence_controls)} control(s) backed by independent (level-3) evidence")

st.subheader("Residual risk by domain")
domain = v.groupby("domain", as_index=False)["residual_risk"].mean().sort_values("residual_risk", ascending=False)
st.bar_chart(domain.set_index("domain"))

st.subheader("Assessment details")
cols = ["control_id", "domain", "requirement", "coverage", "evidence_level", "confidence",
        "reviewer_limited", "adverse_event", "residual_likelihood", "impact", "residual_risk",
        "residual_rating", "evidence_ids", "analyst_rationale"]
st.dataframe(v[cols], use_container_width=True, hide_index=True)

st.subheader("Evidence gaps and follow-up")
gaps = v[v.coverage != "Addressed"].sort_values("residual_risk", ascending=False)
st.dataframe(gaps[["control_id", "requirement", "coverage", "residual_rating", "reviewer_limited", "follow_up_action"]],
             use_container_width=True, hide_index=True)

with st.expander("Evidence register for this vendor"):
    ev_ids = set(";".join(v.evidence_ids).split(";"))
    st.dataframe(evidence[evidence.evidence_id.isin(ev_ids)], use_container_width=True, hide_index=True)

with st.expander("Sources cited for this vendor"):
    src_ids = set(evidence[evidence.evidence_id.isin(ev_ids)].source_id)
    st.dataframe(sources[sources.source_id.isin(src_ids)], use_container_width=True, hide_index=True)

st.subheader("Sensitivity analysis (all vendors)")
st.caption("High/Critical count under alternative assumptions. See docs/methodology.md, Section 6.")
st.dataframe(scoring.sensitivity(df), use_container_width=True, hide_index=True)

st.info("All findings are based on public evidence only, retrieved 24 September 2026. "
        "See reports/Third_Party_Cyber_Risk_Assessment_Report.pdf for the full narrative report.")
