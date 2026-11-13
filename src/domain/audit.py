from __future__ import annotations

import pandas as pd

from src.domain.models import Alert
from src.domain.rules import AUDIT_RULES
from src.domain.validation import validate_measurements


def audit_measurements(df: pd.DataFrame) -> pd.DataFrame:
    validate_measurements(df)
    alerts: list[Alert] = []

    for row_id, row in df.reset_index(drop=True).iterrows():
        for rule in AUDIT_RULES:
            if alert := rule(row_id, row):
                alerts.append(alert)

    columns = list(Alert.__dataclass_fields__)
    return pd.DataFrame([alert.to_dict() for alert in alerts], columns=columns)
