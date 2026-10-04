"""Integrity checks: every reference resolves, every vendor covers every control."""
from pathlib import Path
import sys
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"


def run(data_dir: Path = DATA) -> list[str]:
    errors = []
    inputs = pd.read_csv(data_dir / "assessment_inputs.csv")
    catalog = pd.read_csv(data_dir / "control_catalog.csv")
    evidence = pd.read_csv(data_dir / "evidence_register.csv")
    sources = pd.read_csv(data_dir / "source_register.csv")
    profiles = pd.read_csv(data_dir / "vendor_profiles.csv")

    ev_ids = set(evidence.evidence_id)
    src_ids = set(sources.source_id)
    for _, r in evidence.iterrows():
        if r.source_id not in src_ids:
            errors.append(f"{r.evidence_id}: unknown source {r.source_id}")
    for _, r in inputs.iterrows():
        for e in str(r.evidence_ids).split(";"):
            if e not in ev_ids:
                errors.append(f"{r.vendor}/{r.control_id}: unknown evidence {e}")
        if r.coverage not in ("Addressed", "Partial", "Not evidenced"):
            errors.append(f"{r.vendor}/{r.control_id}: bad coverage {r.coverage}")
        if r.coverage == "Addressed" and r.evidence_level < 2:
            errors.append(f"{r.vendor}/{r.control_id}: Addressed requires evidence_level >= 2")
        vend_ev = evidence.set_index("evidence_id").vendor
        for e in str(r.evidence_ids).split(";"):
            if e in ev_ids and vend_ev[e] != r.vendor:
                errors.append(f"{r.vendor}/{r.control_id}: evidence {e} belongs to {vend_ev[e]}")
    for vendor in profiles.vendor:
        have = set(inputs[inputs.vendor == vendor].control_id)
        want = set(catalog.control_id)
        if have != want:
            errors.append(f"{vendor}: missing {sorted(want - have)} extra {sorted(have - want)}")
    dup = inputs.duplicated(["vendor", "control_id"]).sum()
    if dup:
        errors.append(f"{dup} duplicate vendor/control rows")
    return errors


if __name__ == "__main__":
    errs = run()
    print("OK - all checks passed" if not errs else "\n".join(errs))
    sys.exit(1 if errs else 0)
