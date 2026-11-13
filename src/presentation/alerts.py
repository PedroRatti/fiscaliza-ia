from __future__ import annotations

import pandas as pd
import streamlit as st

from src.formatting import format_currency


def render_alerts(alerts: pd.DataFrame) -> None:
    if alerts.empty:
        st.success("Nenhum alerta foi identificado pelas regras configuradas.")
        return

    severity_options = sorted(alerts["severidade"].unique().tolist())
    selected = st.multiselect("Filtrar severidade", severity_options, default=severity_options)
    filtered = alerts[alerts["severidade"].isin(selected)].sort_values(
        ["pontos", "impacto_estimado"], ascending=False
    )
    for _, alert in filtered.iterrows():
        alert_title = (
            f"{alert['severidade']} · {alert['contrato']} / item {alert['item']} · "
            f"{alert['titulo']}"
        )
        with st.expander(
            alert_title,
            expanded=alert["severidade"] in {"Crítica", "Alta"},
        ):
            st.write(alert["evidencia"])
            st.caption(f"Recomendação: {alert['recomendacao']}")
            if alert["impacto_estimado"] > 0:
                st.metric(
                    "Impacto potencial estimado",
                    format_currency(alert["impacto_estimado"]),
                )
