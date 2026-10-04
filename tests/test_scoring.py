import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import scoring, validate


def test_bands():
    assert scoring.risk_band(4) == "Low"
    assert scoring.risk_band(5) == "Medium" and scoring.risk_band(12) == "Medium"
    assert scoring.risk_band(13) == "High" and scoring.risk_band(19) == "High"
    assert scoring.risk_band(20) == "Critical" and scoring.risk_band(25) == "Critical"


def test_likelihood_rules():
    assert scoring.residual_likelihood("Addressed", "N", "N") == 2
    assert scoring.residual_likelihood("Partial", "N", "N") == 3
    assert scoring.residual_likelihood("Not evidenced", "N", "N") == 4
    assert scoring.residual_likelihood("Not evidenced", "Y", "N") == 3   # absence not established
    assert scoring.residual_likelihood("Partial", "Y", "Y") == 4        # adverse uplift
    assert scoring.residual_likelihood("Not evidenced", "N", "Y") == 5  # capped at 5


def test_data_integrity():
    assert validate.run() == []


def test_scores_are_discriminating():
    df = scoring.load_assessment()
    hi = scoring.vendor_summary(df).set_index("vendor")[["high", "critical"]].sum(axis=1)
    assert hi.nunique() == 3                            # scores must discriminate between vendors
    assert (df.residual_risk <= df.inherent_risk).all()


def test_no_likelihood_of_one_from_public_evidence():
    df = scoring.load_assessment()
    assert df.residual_likelihood.min() >= 2            # 1 is reserved for post-validation
