from __future__ import annotations

from io import BytesIO

import pandas as pd

from src.audit import validate_columns


def load_measurements(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Formato nao suportado. Envie CSV ou XLSX.")
    validate_columns(df)
    return df


def to_excel_bytes(summary: pd.DataFrame, alerts: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Resumo por item", index=False)
        alerts.to_excel(writer, sheet_name="Alertas", index=False)
    return output.getvalue()
