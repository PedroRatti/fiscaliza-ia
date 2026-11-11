import pandas as pd

from src.audit import audit_measurements, risk_summary


def row(**overrides):
    data = {
        "contrato": "C-1",
        "item": "1",
        "descricao_contratada": "Pavimentacao",
        "descricao_medida": "Pavimentacao",
        "quantidade_contratada": 100,
        "quantidade_acumulada": 80,
        "preco_unitario_contratado": 10,
        "preco_unitario_medido": 10,
        "avanco_fisico_pct": 80,
        "avanco_financeiro_pct": 80,
        "inicio_previsto": "2026-01-01",
        "fim_previsto": "2026-12-31",
        "data_medicao": "2026-06-01",
        "possui_aditivo": "nao",
    }
    data.update(overrides)
    return data


def test_regular_item_has_no_alerts():
    assert audit_measurements(pd.DataFrame([row()])).empty


def test_excess_without_addendum_is_critical():
    alerts = audit_measurements(pd.DataFrame([row(quantidade_acumulada=115)]))
    assert "QTD_EXCEDENTE" in alerts["rule_id"].tolist()
    assert alerts.loc[alerts["rule_id"] == "QTD_EXCEDENTE", "impacto_estimado"].iloc[0] == 150


def test_addendum_suppresses_quantity_alert():
    alerts = audit_measurements(pd.DataFrame([row(quantidade_acumulada=115, possui_aditivo="sim")]))
    assert "QTD_EXCEDENTE" not in alerts.get("rule_id", pd.Series(dtype=str)).tolist()


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
    assert result.loc[0, "nivel_risco"] == "Critico"
