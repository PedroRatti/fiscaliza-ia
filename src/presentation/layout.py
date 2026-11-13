from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from src.infrastructure import ai_available

PAGE_STYLES = """
<style>
  .block-container {padding-top: 2rem; padding-bottom: 3rem;}
  [data-testid="stMetric"] {background:#f1f5f9;border:1px solid #cbd5e1;
    padding:14px;border-radius:12px;box-shadow:0 2px 8px rgba(15,42,67,.08);}
  [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
    color:#334155 !important;font-weight:600;}
  [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
    color:#0f3a56 !important;font-weight:700;}
  .hero {padding:22px 26px;border-radius:16px;
    background:linear-gradient(120deg,#102a43,#176b87);
    color:white;margin-bottom:20px;}
  .hero h1 {margin:0 0 4px 0;font-size:2.1rem;}
  .hero p {margin:0;opacity:.9;}
  .notice {border-left:4px solid #176b87;background:#eef7fa;
    color:#123047 !important;padding:12px 16px;border-radius:6px;}
  .notice b {color:#0b3954 !important;}
</style>
"""

def configure_page() -> None:
    st.set_page_config(
        page_title="FiscalizaIA",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_header() -> None:
    st.markdown(
        PAGE_STYLES,
        unsafe_allow_html=True,
    )
    st.markdown(
        """<div class="hero">
  <h1>FiscalizaIA</h1>
  <p>Auditoria assistida de medições de obras públicas</p>
</div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="notice"><b>Apoio à decisão:</b> o sistema prioriza indícios para revisão. '
        "Ele não determina fraude, irregularidade ou aprovação de medições.</div>",
        unsafe_allow_html=True,
    )


def render_sidebar(sample_file: Path) -> tuple[str, Any | None]:
    with st.sidebar:
        st.header("Fonte dos dados")
        source = st.radio("Escolha como começar", ["Usar demonstração", "Enviar arquivo"])
        uploaded = None
        if source == "Enviar arquivo":
            uploaded = st.file_uploader("CSV ou XLSX", type=["csv", "xlsx", "xls"])
        st.download_button(
            "Baixar CSV de exemplo",
            data=sample_file.read_bytes(),
            file_name="medicoes_exemplo.csv",
            mime="text/csv",
            width="stretch",
        )
        st.divider()
        st.subheader("Integração de IA")
        if ai_available():
            st.success("Chave OpenAI configurada")
        else:
            st.warning("Modo local: configure OPENAI_API_KEY para gerar o parecer.")
        st.caption("Os cálculos são determinísticos; a IA apenas explica os achados.")
    return source, uploaded
