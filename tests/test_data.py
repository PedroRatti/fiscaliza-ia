from io import BytesIO

import pandas as pd
import pytest

from src.infrastructure import load_measurements, to_excel_bytes


def uploaded_file(content: bytes, name: str) -> BytesIO:
    uploaded = BytesIO(content)
    uploaded.name = name
    return uploaded


def test_empty_csv_has_user_friendly_message():
    uploaded = uploaded_file(b"", "medicoes.csv")

    with pytest.raises(
        ValueError,
        match="O arquivo CSV está vazio ou não possui cabeçalhos",
    ):
        load_measurements(uploaded)


def test_corrupted_xlsx_has_user_friendly_message():
    uploaded = uploaded_file(b"isto nao e um arquivo Excel", "medicoes.xlsx")

    with pytest.raises(
        ValueError,
        match="O arquivo Excel é inválido, está corrompido",
    ):
        load_measurements(uploaded)


def test_unsupported_extension_has_user_friendly_message():
    uploaded = uploaded_file(b"conteudo", "medicoes.txt")

    with pytest.raises(ValueError, match="Formato não suportado. Envie CSV ou XLSX"):
        load_measurements(uploaded)


def test_excel_export_replaces_internal_row_id_with_source_line():
    summary = pd.DataFrame(
        [
            {"row_id": 0, "contrato": "C-1"},
            {"row_id": 1, "contrato": "C-2"},
        ]
    )
    alerts = pd.DataFrame(
        [
            {"row_id": 1, "rule_id": "REGRA_TESTE"},
        ]
    )

    exported = to_excel_bytes(summary, alerts)
    summary_sheet = pd.read_excel(BytesIO(exported), sheet_name="Resumo por item")
    alerts_sheet = pd.read_excel(BytesIO(exported), sheet_name="Alertas")

    assert "row_id" not in summary_sheet.columns
    assert "row_id" not in alerts_sheet.columns
    assert summary_sheet["Linha da planilha"].tolist() == [2, 3]
    assert alerts_sheet["Linha da planilha"].tolist() == [3]
