from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.formatting import format_currency

RISK_COLORS = {
    "Baixo": "#2a9d8f",
    "Médio": "#e9c46a",
    "Alto": "#f4a261",
    "Crítico": "#e76f51",
}

def render_overview(summary: pd.DataFrame, metrics: dict[str, object]) -> None:
    st.subheader("Visão geral")
    items, alerts, high_risk, impact = st.columns(4)
    items.metric("Itens analisados", metrics["itens"])
    alerts.metric("Alertas encontrados", metrics["alertas"])
    high_risk.metric(
        "Itens de alto risco",
        int(summary["nivel_risco"].isin(["Alto", "Crítico"]).sum()),
    )
    impact.metric(
        "Impacto potencial",
        format_currency(float(metrics["impacto_estimado"])),
        help="Estimativa de exposição para priorização; não representa prejuízo confirmado.",
    )


def render_dashboard(summary: pd.DataFrame, alerts: pd.DataFrame) -> None:
    left, right = st.columns([1, 1.4])
    with left:
        risk_counts = (
            summary["nivel_risco"]
            .value_counts()
            .reindex(["Baixo", "Médio", "Alto", "Crítico"], fill_value=0)
        )
        risk_data = risk_counts.rename_axis("Risco").reset_index(name="Itens")
        risk_chart = px.bar(
            risk_data,
            x="Risco",
            y="Itens",
            color="Risco",
            color_discrete_map=RISK_COLORS,
            title="Distribuição dos itens por risco",
        )
        risk_chart.update_traces(
            hovertemplate=(
                "<b>Nível de risco: %{x}</b><br>"
                "Itens analisados: %{y}"
                "<extra></extra>"
            )
        )
        risk_chart.update_layout(showlegend=False, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(risk_chart, width="stretch")

    with right:
        alerts_by_rule = (
            alerts.groupby(["rule_id", "titulo"], as_index=False)
            .agg(ocorrencias=("row_id", "count"), impacto=("impacto_estimado", "sum"))
            .sort_values("ocorrencias", ascending=True)
            if not alerts.empty
            else pd.DataFrame(columns=["titulo", "ocorrencias", "impacto"])
        )
        alerts_by_rule["impacto_formatado"] = alerts_by_rule["impacto"].map(format_currency)
        alerts_chart = px.bar(
            alerts_by_rule,
            x="ocorrencias",
            y="titulo",
            orientation="h",
            title="Alertas por regra de auditoria",
            color="impacto",
            color_continuous_scale="Blues",
            custom_data=["impacto_formatado"],
        )
        alerts_chart.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Ocorrências: %{x}<br>"
                "Impacto potencial: %{customdata[0]}"
                "<extra></extra>"
            )
        )
        alerts_chart.update_layout(
            margin=dict(l=10, r=10, t=55, b=10),
            coloraxis_showscale=False,
        )
        st.plotly_chart(alerts_chart, width="stretch")

    st.markdown("#### Itens priorizados")
    st.dataframe(
        summary.sort_values("pontuacao_risco", ascending=False)[
            [
                "contrato",
                "item",
                "descricao_contratada",
                "pontuacao_risco",
                "nivel_risco",
                "total_alertas",
            ]
        ],
        width="stretch",
        hide_index=True,
        column_config={
            "contrato": st.column_config.TextColumn("Contrato"),
            "item": st.column_config.TextColumn("Item"),
            "descricao_contratada": st.column_config.TextColumn("Descrição contratada"),
            "pontuacao_risco": st.column_config.ProgressColumn(
                "Pontuação de risco",
                min_value=0,
                max_value=100,
                format="%d pontos",
            ),
            "nivel_risco": st.column_config.TextColumn("Nível de risco"),
            "total_alertas": st.column_config.NumberColumn(
                "Total de alertas",
                format="%d",
            ),
        },
    )
