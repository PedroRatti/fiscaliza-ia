from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.domain import audit_measurements, portfolio_metrics, risk_summary
from src.infrastructure import load_measurements
from src.presentation import (
    configure_page,
    render_ai_report,
    render_alerts,
    render_dashboard,
    render_data_export,
    render_header,
    render_overview,
    render_sidebar,
)

ROOT = Path(__file__).parent
SAMPLE_FILE = ROOT / "data" / "medicoes_exemplo.csv"


def load_selected_data(source: str, uploaded_file) -> pd.DataFrame:
    if source == "Usar demonstração":
        return pd.read_csv(SAMPLE_FILE)
    if uploaded_file is not None:
        return load_measurements(uploaded_file)

    st.info("Envie uma planilha ou selecione a demonstração para iniciar.")
    st.stop()


def main() -> None:
    configure_page()
    render_header()
    source, uploaded_file = render_sidebar(SAMPLE_FILE)

    try:
        data = load_selected_data(source, uploaded_file)
    except (OSError, ValueError) as exc:
        st.error(f"Não foi possível ler a planilha: {exc}")
        st.stop()

    alerts = audit_measurements(data)
    summary = risk_summary(data, alerts)
    metrics = portfolio_metrics(data, alerts)

    render_overview(summary, metrics)
    dashboard_tab, alerts_tab, report_tab, data_tab = st.tabs(
        ["Dashboard", "Alertas", "Parecer assistido", "Dados e exportação"]
    )

    with dashboard_tab:
        render_dashboard(summary, alerts)
    with alerts_tab:
        render_alerts(alerts)
    with report_tab:
        render_ai_report(alerts, metrics)
    with data_tab:
        render_data_export(data, summary, alerts)


if __name__ == "__main__":
    main()
