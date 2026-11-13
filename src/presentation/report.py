from __future__ import annotations

import pandas as pd
import streamlit as st

from src.infrastructure import AuditReportError, ai_available, generate_audit_report


def render_ai_report(alerts: pd.DataFrame, metrics: dict[str, object]) -> None:
    st.write(
        "A IA recebe somente métricas e alertas calculados pelo motor de regras. "
        "Ela não recebe documentos pessoais nem substitui a análise do fiscal."
    )
    if st.button("Gerar parecer com IA", type="primary", disabled=not ai_available()):
        with st.spinner("Gerando parecer fundamentado nos alertas..."):
            try:
                st.session_state["report"] = generate_audit_report(alerts, metrics)
            except AuditReportError as exc:
                st.error(f"Falha ao gerar parecer: {exc}")

    report = st.session_state.get("report")
    if report:
        st.markdown(report)
        st.download_button("Baixar parecer", report, "parecer_fiscalizaia.md", "text/markdown")
    elif not ai_available():
        st.info("Adicione OPENAI_API_KEY ao arquivo .env e reinicie a aplicação.")
