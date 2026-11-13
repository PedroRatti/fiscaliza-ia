from __future__ import annotations

from io import BytesIO

import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from src.domain import validate_measurements


def _prepare_export(data: pd.DataFrame) -> pd.DataFrame:
    exported = data.copy()
    if "row_id" in exported.columns:
        exported["row_id"] = exported["row_id"].astype(int) + 2
        exported = exported.rename(columns={"row_id": "Linha da planilha"})
    return exported


def load_measurements(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file)
        except EmptyDataError as exc:
            raise ValueError("O arquivo CSV está vazio ou não possui cabeçalhos.") from exc
        except (ParserError, UnicodeDecodeError) as exc:
            raise ValueError("O arquivo CSV é inválido ou não pôde ser interpretado.") from exc
    elif name.endswith((".xlsx", ".xls")):
        try:
            df = pd.read_excel(uploaded_file)
        except (OSError, ValueError) as exc:
            raise ValueError(
                "O arquivo Excel é inválido, está corrompido ou não corresponde "
                "ao formato informado."
            ) from exc
    else:
        raise ValueError("Formato não suportado. Envie CSV ou XLSX.")
    validate_measurements(df)
    return df


def to_excel_bytes(summary: pd.DataFrame, alerts: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        _prepare_export(summary).to_excel(writer, sheet_name="Resumo por item", index=False)
        _prepare_export(alerts).to_excel(writer, sheet_name="Alertas", index=False)
    return output.getvalue()
