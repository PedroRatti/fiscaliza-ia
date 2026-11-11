from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.ai import ai_available, generate_audit_report
from src.audit import audit_measurements, portfolio_metrics, risk_summary
from src.data import load_measurements, to_excel_bytes

ROOT = Path(__file__).parent
SAMPLE_FILE = ROOT / "data" / "medicoes_exemplo.csv"

st.set_page_config(
    page_title="FiscalizaIA",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 2rem; padding-bottom: 3rem;}
      [data-testid="stMetric"] {background:#f7f9fc;border:1px solid #e3e8ef;
        padding:14px;border-radius:12px;}
      .hero {padding:22px 26px;border-radius:16px;
        background:linear-gradient(120deg,#102a43,#176b87);
        color:white;margin-bottom:20px;}
      .hero h1 {margin:0 0 4px 0;font-size:2.1rem;}
      .hero p {margin:0;opacity:.9;}
      .notice {border-left:4px solid #176b87;background:#eef7fa;
        padding:12px 16px;border-radius:6px;}
    </style>
    <div class="hero">
      <h1>FiscalizaIA</h1>
      <p>Auditoria assistida de medições de obras públicas</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="notice"><b>Apoio à decisão:</b> o sistema prioriza indícios para revisão. '
    "Ele não determina fraude, irregularidade ou aprovação de medições.</div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Fonte dos dados")
    source = st.radio("Escolha como começar", ["Usar demonstração", "Enviar arquivo"])
    uploaded = None
    if source == "Enviar arquivo":
        uploaded = st.file_uploader("CSV ou XLSX", type=["csv", "xlsx", "xls"])
    st.download_button(
        "Baixar CSV de exemplo",
        data=SAMPLE_FILE.read_bytes(),
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

try:
    if source == "Usar demonstração":
        data = pd.read_csv(SAMPLE_FILE)
    elif uploaded is not None:
        data = load_measurements(uploaded)
    else:
        st.info("Envie uma planilha ou selecione a demonstração para iniciar.")
        st.stop()
except Exception as exc:
    st.error(f"Não foi possível ler a planilha: {exc}")
    st.stop()

alerts = audit_measurements(data)
summary = risk_summary(data, alerts)
metrics = portfolio_metrics(data, alerts)

st.subheader("Visão geral")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Itens analisados", metrics["itens"])
c2.metric("Alertas encontrados", metrics["alertas"])
c3.metric("Itens de alto risco", int(summary["nivel_risco"].isin(["Alto", "Critico"]).sum()))
c4.metric(
    "Impacto potencial",
    f"R$ {metrics['impacto_estimado']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    help="Estimativa de exposição para priorização; não representa prejuízo confirmado.",
)

tab_dashboard, tab_alerts, tab_report, tab_data = st.tabs(
    ["Dashboard", "Alertas", "Parecer assistido", "Dados e exportação"]
)

with tab_dashboard:
    left, right = st.columns([1, 1.4])
    with left:
        risk_counts = (
            summary["nivel_risco"]
            .value_counts()
            .reindex(["Baixo", "Medio", "Alto", "Critico"], fill_value=0)
        )
        risk_df = risk_counts.rename_axis("Risco").reset_index(name="Itens")
        fig = px.bar(
            risk_df,
            x="Risco",
            y="Itens",
            color="Risco",
            color_discrete_map={
                "Baixo": "#2a9d8f",
                "Medio": "#e9c46a",
                "Alto": "#f4a261",
                "Critico": "#e76f51",
            },
            title="Distribuição dos itens por risco",
        )
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(fig, width="stretch")
    with right:
        by_rule = (
            alerts.groupby(["rule_id", "titulo"], as_index=False)
            .agg(ocorrencias=("row_id", "count"), impacto=("impacto_estimado", "sum"))
            .sort_values("ocorrencias", ascending=True)
            if not alerts.empty
            else pd.DataFrame(columns=["titulo", "ocorrencias", "impacto"])
        )
        fig = px.bar(
            by_rule,
            x="ocorrencias",
            y="titulo",
            orientation="h",
            title="Alertas por regra de auditoria",
            color="impacto",
            color_continuous_scale="Blues",
        )
        fig.update_layout(margin=dict(l=10, r=10, t=55, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig, width="stretch")

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
            "pontuacao_risco": st.column_config.ProgressColumn("Risco", min_value=0, max_value=100)
        },
    )

with tab_alerts:
    if alerts.empty:
        st.success("Nenhum alerta foi identificado pelas regras configuradas.")
    else:
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
                expanded=alert["severidade"] in {"Critica", "Alta"},
            ):
                st.write(alert["evidencia"])
                st.caption(f"Recomendação: {alert['recomendacao']}")
                if alert["impacto_estimado"] > 0:
                    st.metric("Impacto potencial estimado", f"R$ {alert['impacto_estimado']:,.2f}")

with tab_report:
    st.write(
        "A IA recebe somente métricas e alertas calculados pelo motor de regras. "
        "Ela não recebe documentos pessoais nem substitui a análise do fiscal."
    )
    if st.button("Gerar parecer com IA", type="primary", disabled=not ai_available()):
        with st.spinner("Gerando parecer fundamentado nos alertas..."):
            try:
                st.session_state["report"] = generate_audit_report(alerts, metrics)
            except Exception as exc:
                st.error(f"Falha ao gerar parecer: {exc}")
    report = st.session_state.get("report")
    if report:
        st.markdown(report)
        st.download_button("Baixar parecer", report, "parecer_fiscalizaia.md", "text/markdown")
    elif not ai_available():
        st.info("Adicione OPENAI_API_KEY ao arquivo .env e reinicie a aplicação.")

with tab_data:
    st.markdown("#### Dados analisados")
    st.dataframe(data, width="stretch", hide_index=True)
    st.download_button(
        "Baixar relatório Excel",
        data=to_excel_bytes(summary, alerts),
        file_name="relatorio_fiscalizaia.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    with st.expander("Metodologia e limitações"):
        st.markdown(
            """
            - Os alertas são produzidos por regras explícitas e reproduzíveis.
            - O impacto financeiro é uma estimativa para priorização, não um prejuízo confirmado.
            - A presença de um alerta exige conferência documental e técnica.
            - Dados sintéticos são usados na demonstração; nenhuma informação pessoal é necessária.
            - A qualidade da análise depende da completude e consistência da planilha enviada.
            """
        )
