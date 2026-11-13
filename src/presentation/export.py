from __future__ import annotations

import pandas as pd
import streamlit as st

from src.infrastructure import to_excel_bytes


def render_data_export(
    data: pd.DataFrame,
    summary: pd.DataFrame,
    alerts: pd.DataFrame,
) -> None:
    st.markdown("#### Dados analisados")
    st.dataframe(
        data,
        width="stretch",
        hide_index=True,
        column_config={
            "contrato": st.column_config.TextColumn("Contrato"),
            "item": st.column_config.TextColumn("Item"),
            "descricao_contratada": st.column_config.TextColumn("Descrição contratada"),
            "descricao_medida": st.column_config.TextColumn("Descrição medida"),
            "unidade_medida": st.column_config.TextColumn("Unidade de medida"),
            "quantidade_contratada": st.column_config.NumberColumn(
                "Quantidade contratada",
                format="localized",
            ),
            "quantidade_acumulada": st.column_config.NumberColumn(
                "Quantidade acumulada",
                format="localized",
            ),
            "preco_unitario_contratado": st.column_config.NumberColumn(
                "Preço unitário contratado",
                format="R$ %.2f",
            ),
            "preco_unitario_medido": st.column_config.NumberColumn(
                "Preço unitário aplicado na medição",
                format="R$ %.2f",
            ),
            "avanco_fisico_pct": st.column_config.NumberColumn(
                "Avanço físico (%)",
                format="%.1f%%",
            ),
            "avanco_financeiro_pct": st.column_config.NumberColumn(
                "Avanço financeiro (%)",
                format="%.1f%%",
            ),
            "inicio_previsto": st.column_config.DateColumn(
                "Início previsto",
                format="DD/MM/YYYY",
            ),
            "fim_previsto": st.column_config.DateColumn(
                "Fim previsto",
                format="DD/MM/YYYY",
            ),
            "data_medicao": st.column_config.DateColumn(
                "Data da medição",
                format="DD/MM/YYYY",
            ),
        },
    )
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
