from __future__ import annotations

from datetime import date

import pandas as pd


def risk_summary(df: pd.DataFrame, alerts: pd.DataFrame) -> pd.DataFrame:
    base = df.reset_index(drop=True).copy()
    base["row_id"] = base.index
    if alerts.empty:
        base["pontuacao_risco"] = 0
        base["nivel_risco"] = "Baixo"
        base["total_alertas"] = 0
        return base

    grouped = alerts.groupby("row_id").agg(
        pontuacao_risco=("pontos", "sum"), total_alertas=("rule_id", "count")
    )
    base = base.merge(grouped, on="row_id", how="left").fillna(
        {"pontuacao_risco": 0, "total_alertas": 0}
    )
    base["pontuacao_risco"] = base["pontuacao_risco"].clip(upper=100).astype(int)
    base["total_alertas"] = base["total_alertas"].astype(int)
    base["nivel_risco"] = pd.cut(
        base["pontuacao_risco"],
        bins=[-1, 19, 49, 79, 100],
        labels=["Baixo", "Médio", "Alto", "Crítico"],
    ).astype(str)
    return base


def portfolio_metrics(df: pd.DataFrame, alerts: pd.DataFrame) -> dict[str, object]:
    contract_value = (
        df["quantidade_contratada"].astype(float) * df["preco_unitario_contratado"].astype(float)
    ).sum()
    return {
        "contratos": int(df["contrato"].nunique()),
        "itens": int(len(df)),
        "alertas": int(len(alerts)),
        "impacto_estimado": float(alerts["impacto_estimado"].sum()) if not alerts.empty else 0,
        "valor_contratado": float(contract_value),
        "data_analise": date.today().isoformat(),
    }
