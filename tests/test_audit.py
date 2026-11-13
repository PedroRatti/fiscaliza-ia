import pandas as pd
import pytest

from src.domain import (
    REQUIRED_COLUMNS,
    audit_measurements,
    portfolio_metrics,
    risk_summary,
    validate_columns,
    validate_measurements,
)


def row(**overrides):
    data = {
        "contrato": "C-1",
        "item": "1",
        "descricao_contratada": "Pavimentacao",
        "descricao_medida": "Pavimentacao",
        "unidade_medida": "m2",
        "quantidade_contratada": 100,
        "quantidade_acumulada": 80,
        "preco_unitario_contratado": 10,
        "preco_unitario_medido": 10,
        "avanco_fisico_pct": 80,
        "avanco_financeiro_pct": 80,
        "inicio_previsto": "2026-01-01",
        "fim_previsto": "2026-12-31",
        "data_medicao": "2026-06-01",
    }
    data.update(overrides)
    return data


def test_regular_item_has_no_alerts():
    assert audit_measurements(pd.DataFrame([row()])).empty


def test_all_required_columns_are_accepted():
    validate_columns(pd.DataFrame([row()]))


def test_missing_columns_are_reported_in_stable_order():
    data = pd.DataFrame([row()]).drop(columns=["item", "contrato"])

    with pytest.raises(
        ValueError,
        match="Colunas obrigatórias ausentes: contrato, item",
    ):
        validate_columns(data)


def test_required_columns_contract_matches_the_input_fixture():
    assert set(row()) == REQUIRED_COLUMNS


def test_quantity_excess_at_least_ten_percent_is_critical():
    alerts = audit_measurements(pd.DataFrame([row(quantidade_acumulada=115)]))
    alert = alerts.loc[alerts["rule_id"] == "QTD_EXCEDENTE"].iloc[0]

    assert alert["severidade"] == "Crítica"
    assert alert["pontos"] == 40
    assert alert["impacto_estimado"] == 150


def test_quantity_equal_to_contract_does_not_alert():
    alerts = audit_measurements(pd.DataFrame([row(quantidade_acumulada=100)]))

    assert "QTD_EXCEDENTE" not in alerts.get("rule_id", pd.Series(dtype=str)).tolist()


def test_quantity_excess_below_ten_percent_is_high():
    alerts = audit_measurements(pd.DataFrame([row(quantidade_acumulada=105)]))
    alert = alerts.loc[alerts["rule_id"] == "QTD_EXCEDENTE"].iloc[0]

    assert alert["severidade"] == "Alta"
    assert alert["pontos"] == 30
    assert alert["impacto_estimado"] == 50


def test_quantity_alert_evidence_includes_the_measurement_unit():
    alerts = audit_measurements(
        pd.DataFrame([row(quantidade_acumulada=115, unidade_medida="m3")])
    )
    evidence = alerts.loc[alerts["rule_id"] == "QTD_EXCEDENTE", "evidencia"].iloc[0]

    assert "15,00 m3" in evidence


def test_price_difference_at_one_percent_does_not_alert():
    alerts = audit_measurements(pd.DataFrame([row(preco_unitario_medido=10.10)]))

    assert "PRECO_DIVERGENTE" not in alerts.get("rule_id", pd.Series(dtype=str)).tolist()


def test_price_difference_above_one_percent_is_medium():
    alerts = audit_measurements(pd.DataFrame([row(preco_unitario_medido=10.20)]))
    alert = alerts.loc[alerts["rule_id"] == "PRECO_DIVERGENTE"].iloc[0]

    assert alert["severidade"] == "Média"
    assert alert["pontos"] == 20
    assert alert["impacto_estimado"] == pytest.approx(16)


def test_price_difference_at_least_ten_percent_is_high():
    alerts = audit_measurements(pd.DataFrame([row(preco_unitario_medido=12)]))
    alert = alerts.loc[alerts["rule_id"] == "PRECO_DIVERGENTE"].iloc[0]

    assert alert["severidade"] == "Alta"
    assert alert["pontos"] == 30
    assert alert["impacto_estimado"] == 160


def test_lower_measured_price_has_zero_potential_impact():
    alerts = audit_measurements(pd.DataFrame([row(preco_unitario_medido=8)]))
    alert = alerts.loc[alerts["rule_id"] == "PRECO_DIVERGENTE"].iloc[0]

    assert alert["severidade"] == "Alta"
    assert alert["impacto_estimado"] == 0


def test_physical_financial_gap_below_fifteen_points_does_not_alert():
    alerts = audit_measurements(
        pd.DataFrame([row(avanco_fisico_pct=50, avanco_financeiro_pct=64.9)])
    )

    assert "FISICO_FINANCEIRO" not in alerts.get("rule_id", pd.Series(dtype=str)).tolist()


def test_physical_financial_gap_at_fifteen_points_is_medium():
    alerts = audit_measurements(
        pd.DataFrame([row(avanco_fisico_pct=50, avanco_financeiro_pct=65)])
    )
    alert = alerts.loc[alerts["rule_id"] == "FISICO_FINANCEIRO"].iloc[0]

    assert alert["severidade"] == "Média"
    assert alert["pontos"] == 20


def test_physical_financial_gap_at_twenty_five_points_is_high():
    alerts = audit_measurements(
        pd.DataFrame([row(avanco_fisico_pct=50, avanco_financeiro_pct=75)])
    )
    alert = alerts.loc[alerts["rule_id"] == "FISICO_FINANCEIRO"].iloc[0]

    assert alert["severidade"] == "Alta"
    assert alert["pontos"] == 30


@pytest.mark.parametrize("data_medicao", ["2025-12-31", "2027-01-01"])
def test_measurement_outside_schedule_is_medium(data_medicao):
    alerts = audit_measurements(pd.DataFrame([row(data_medicao=data_medicao)]))
    alert = alerts.loc[alerts["rule_id"] == "FORA_CRONOGRAMA"].iloc[0]

    assert alert["severidade"] == "Média"
    assert alert["pontos"] == 20


@pytest.mark.parametrize("data_medicao", ["2026-01-01", "2026-12-31"])
def test_measurement_on_schedule_boundary_does_not_alert(data_medicao):
    alerts = audit_measurements(pd.DataFrame([row(data_medicao=data_medicao)]))

    assert "FORA_CRONOGRAMA" not in alerts.get("rule_id", pd.Series(dtype=str)).tolist()


@pytest.mark.parametrize("value", [None, "", pd.NA])
def test_missing_value_is_rejected(value):
    data = pd.DataFrame([row(descricao_medida=value)])

    with pytest.raises(ValueError, match="descricao_medida: valor ausente na linha 2"):
        validate_measurements(data)


@pytest.mark.parametrize(
    "column",
    [
        "quantidade_contratada",
        "quantidade_acumulada",
        "preco_unitario_contratado",
        "preco_unitario_medido",
        "avanco_fisico_pct",
        "avanco_financeiro_pct",
    ],
)
def test_non_numeric_value_is_rejected(column):
    data = pd.DataFrame([row(**{column: "dez"})])

    with pytest.raises(ValueError, match=f"{column}: valor não numérico na linha 2"):
        validate_measurements(data)


@pytest.mark.parametrize(
    "column",
    [
        "quantidade_contratada",
        "quantidade_acumulada",
        "preco_unitario_contratado",
        "preco_unitario_medido",
    ],
)
@pytest.mark.parametrize("value", [0, -1])
def test_non_positive_quantity_or_price_is_rejected(column, value):
    data = pd.DataFrame([row(**{column: value})])

    with pytest.raises(ValueError, match=f"{column}: deve ser maior que zero na linha 2"):
        validate_measurements(data)


@pytest.mark.parametrize("column", ["avanco_fisico_pct", "avanco_financeiro_pct"])
@pytest.mark.parametrize("value", [-0.1, 100.1])
def test_percentage_outside_zero_to_one_hundred_is_rejected(column, value):
    data = pd.DataFrame([row(**{column: value})])

    with pytest.raises(ValueError, match=f"{column}: deve estar entre 0 e 100 na linha 2"):
        validate_measurements(data)


@pytest.mark.parametrize("value", [0, 100])
def test_percentage_boundaries_are_accepted(value):
    data = pd.DataFrame([row(avanco_fisico_pct=value, avanco_financeiro_pct=value)])

    validate_measurements(data)


@pytest.mark.parametrize("column", ["inicio_previsto", "fim_previsto", "data_medicao"])
def test_invalid_date_is_rejected(column):
    data = pd.DataFrame([row(**{column: "data-invalida"})])

    with pytest.raises(ValueError, match=f"{column}: data inválida na linha 2"):
        validate_measurements(data)


def test_start_date_after_end_date_is_rejected():
    data = pd.DataFrame([row(inicio_previsto="2026-12-31", fim_previsto="2026-01-01")])

    with pytest.raises(ValueError, match="inicio_previsto: posterior ao fim_previsto na linha 2"):
        validate_measurements(data)


@pytest.mark.parametrize("value", [None, "", pd.NA])
def test_missing_measurement_unit_is_rejected(value):
    data = pd.DataFrame([row(unidade_medida=value)])

    with pytest.raises(ValueError, match="unidade_medida: valor ausente na linha 2"):
        validate_measurements(data)


def test_empty_spreadsheet_is_rejected():
    data = pd.DataFrame(columns=sorted(REQUIRED_COLUMNS))

    with pytest.raises(ValueError, match="A planilha não possui linhas de dados"):
        validate_measurements(data)


def test_validation_reports_all_errors_at_once():
    data = pd.DataFrame(
        [
            row(quantidade_contratada=0),
            row(preco_unitario_medido="invalido", data_medicao="sem-data"),
        ]
    )

    with pytest.raises(ValueError) as exc_info:
        validate_measurements(data)

    message = str(exc_info.value)
    assert "quantidade_contratada: deve ser maior que zero na linha 2" in message
    assert "preco_unitario_medido: valor não numérico na linha 3" in message
    assert "data_medicao: data inválida na linha 3" in message


def test_validation_uses_plural_for_multiple_rows():
    data = pd.DataFrame([row(descricao_medida=""), row(descricao_medida="")])

    with pytest.raises(ValueError, match="descricao_medida: valor ausente nas linhas 2, 3"):
        validate_measurements(data)


def test_alert_keeps_source_row_identity():
    data = pd.DataFrame(
        [
            row(contrato="C-SEM-ALERTA", item="1"),
            row(contrato="C-COM-ALERTA", item="2", quantidade_acumulada=115),
        ]
    )

    alert = audit_measurements(data).iloc[0]

    assert alert["row_id"] == 1
    assert alert["contrato"] == "C-COM-ALERTA"
    assert alert["item"] == "2"


def test_risk_summary_for_item_without_alerts_is_low():
    data = pd.DataFrame([row()])

    result = risk_summary(data, audit_measurements(data))

    assert result.loc[0, "pontuacao_risco"] == 0
    assert result.loc[0, "nivel_risco"] == "Baixo"
    assert result.loc[0, "total_alertas"] == 0


def test_risk_score_is_capped_at_100():
    item = row(
        quantidade_acumulada=130,
        preco_unitario_medido=15,
        avanco_fisico_pct=20,
        avanco_financeiro_pct=80,
        data_medicao="2027-01-01",
    )
    df = pd.DataFrame([item])
    result = risk_summary(df, audit_measurements(df))
    assert result.loc[0, "pontuacao_risco"] == 100
    assert result.loc[0, "nivel_risco"] == "Crítico"


@pytest.mark.parametrize(
    ("score", "expected_level"),
    [
        (0, "Baixo"),
        (19, "Baixo"),
        (20, "Médio"),
        (49, "Médio"),
        (50, "Alto"),
        (79, "Alto"),
        (80, "Crítico"),
        (100, "Crítico"),
    ],
)
def test_risk_level_boundaries(score, expected_level):
    data = pd.DataFrame([row()])
    alerts = pd.DataFrame(
        [
            {
                "row_id": 0,
                "rule_id": "REGRA_TESTE",
                "pontos": score,
            }
        ]
    )

    result = risk_summary(data, alerts)

    assert result.loc[0, "nivel_risco"] == expected_level


def test_portfolio_metrics_aggregate_contracts_items_and_impact():
    data = pd.DataFrame(
        [
            row(contrato="C-1", item="1", quantidade_acumulada=115),
            row(
                contrato="C-1",
                item="2",
                quantidade_contratada=50,
                quantidade_acumulada=50,
                preco_unitario_contratado=20,
                preco_unitario_medido=20,
                avanco_fisico_pct=100,
                avanco_financeiro_pct=100,
            ),
            row(contrato="C-2", item="3"),
        ]
    )

    metrics = portfolio_metrics(data, audit_measurements(data))

    assert metrics["contratos"] == 2
    assert metrics["itens"] == 3
    assert metrics["alertas"] == 1
    assert metrics["impacto_estimado"] == 150
    assert metrics["valor_contratado"] == 3000
    assert metrics["data_analise"]


def test_portfolio_metrics_without_alerts_has_zero_impact():
    data = pd.DataFrame([row()])

    metrics = portfolio_metrics(data, audit_measurements(data))

    assert metrics["alertas"] == 0
    assert metrics["impacto_estimado"] == 0
