from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {
    "contrato",
    "item",
    "descricao_contratada",
    "descricao_medida",
    "unidade_medida",
    "quantidade_contratada",
    "quantidade_acumulada",
    "preco_unitario_contratado",
    "preco_unitario_medido",
    "avanco_fisico_pct",
    "avanco_financeiro_pct",
    "inicio_previsto",
    "fim_previsto",
    "data_medicao",
}

NUMERIC_COLUMNS = {
    "quantidade_contratada",
    "quantidade_acumulada",
    "preco_unitario_contratado",
    "preco_unitario_medido",
    "avanco_fisico_pct",
    "avanco_financeiro_pct",
}

POSITIVE_COLUMNS = {
    "quantidade_contratada",
    "quantidade_acumulada",
    "preco_unitario_contratado",
    "preco_unitario_medido",
}

PERCENTAGE_COLUMNS = {
    "avanco_fisico_pct",
    "avanco_financeiro_pct",
}

DATE_COLUMNS = {
    "inicio_previsto",
    "fim_previsto",
    "data_medicao",
}

TEXT_COLUMNS = {
    "contrato",
    "item",
    "descricao_contratada",
    "descricao_medida",
    "unidade_medida",
}

def validate_columns(df: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(missing))


def _row_location(mask: pd.Series) -> str:
    rows = [str(position + 2) for position, invalid in enumerate(mask.tolist()) if invalid]
    label = "na linha" if len(rows) == 1 else "nas linhas"
    return f"{label} {', '.join(rows)}"


def validate_measurements(df: pd.DataFrame) -> None:
    """Validate the input contract before running deterministic audit rules."""
    validate_columns(df)
    if df.empty:
        raise ValueError("A planilha não possui linhas de dados.")

    errors: list[str] = []

    for column in sorted(REQUIRED_COLUMNS):
        missing = df[column].isna()
        if column in TEXT_COLUMNS:
            missing |= df[column].astype("string").str.strip().eq("").fillna(False)
        if missing.any():
            errors.append(f"{column}: valor ausente {_row_location(missing)}")

    numeric_values: dict[str, pd.Series] = {}
    for column in sorted(NUMERIC_COLUMNS):
        converted = pd.to_numeric(df[column], errors="coerce")
        numeric_values[column] = converted
        invalid = converted.isna() & df[column].notna()
        if invalid.any():
            errors.append(f"{column}: valor não numérico {_row_location(invalid)}")

    for column in sorted(POSITIVE_COLUMNS):
        non_positive = numeric_values[column].notna() & (numeric_values[column] <= 0)
        if non_positive.any():
            errors.append(f"{column}: deve ser maior que zero {_row_location(non_positive)}")

    for column in sorted(PERCENTAGE_COLUMNS):
        out_of_range = numeric_values[column].notna() & ~numeric_values[column].between(0, 100)
        if out_of_range.any():
            errors.append(f"{column}: deve estar entre 0 e 100 {_row_location(out_of_range)}")

    parsed_dates: dict[str, pd.Series] = {}
    for column in sorted(DATE_COLUMNS):
        parsed = pd.to_datetime(df[column], errors="coerce")
        parsed_dates[column] = parsed
        invalid = parsed.isna() & df[column].notna()
        if invalid.any():
            errors.append(f"{column}: data inválida {_row_location(invalid)}")

    inverted_period = (
        parsed_dates["inicio_previsto"].notna()
        & parsed_dates["fim_previsto"].notna()
        & (parsed_dates["inicio_previsto"] > parsed_dates["fim_previsto"])
    )
    if inverted_period.any():
        errors.append(
            "inicio_previsto: posterior ao fim_previsto " + _row_location(inverted_period)
        )

    if errors:
        raise ValueError("Dados inválidos:\n- " + "\n- ".join(errors))
