from __future__ import annotations

import json
import os

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


SYSTEM_INSTRUCTIONS = """Voce e um assistente de apoio a fiscalizacao de obras publicas.
Explique apenas os alertas fornecidos, sem inventar fatos e sem declarar fraude ou irregularidade.
Deixe claro que os achados sao indicios para revisao humana. Escreva em portugues do Brasil,
de forma objetiva, com: resumo executivo, prioridades, perguntas para o fiscal e limitacoes.
"""


def ai_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def generate_audit_report(alerts: pd.DataFrame, metrics: dict) -> str:
    if alerts.empty:
        return (
            "Nenhum alerta foi identificado pelas regras configuradas. "
            "A revisao humana continua recomendada."
        )
    if not ai_available():
        raise RuntimeError("OPENAI_API_KEY nao configurada no arquivo .env.")

    payload = {
        "metricas": metrics,
        "alertas": alerts.sort_values(["pontos", "impacto_estimado"], ascending=False)
        .head(20)
        .to_dict(orient="records"),
    }
    client = OpenAI()
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        instructions=SYSTEM_INSTRUCTIONS,
        input=json.dumps(payload, ensure_ascii=False, default=str),
    )
    return response.output_text
