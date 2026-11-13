from __future__ import annotations

import json
import os
from typing import Any, Mapping, Protocol

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()


SYSTEM_INSTRUCTIONS = """Você é um assistente de apoio à fiscalização de obras públicas.
Explique apenas os alertas fornecidos, sem inventar fatos e sem declarar fraude ou irregularidade.
Deixe claro que os achados são indícios para revisão humana. Escreva em português do Brasil,
de forma objetiva, com: resumo executivo, prioridades, perguntas para o fiscal e limitações.
"""


class AuditReportError(RuntimeError):
    """Raised when the optional AI report cannot be generated safely."""


class ResponsesClient(Protocol):
    def create(self, **kwargs: object) -> Any: ...


class AuditAIClient(Protocol):
    responses: ResponsesClient


def ai_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def generate_audit_report(
    alerts: pd.DataFrame,
    metrics: Mapping[str, object],
    client: AuditAIClient | None = None,
) -> str:
    if alerts.empty:
        return (
            "Nenhum alerta foi identificado pelas regras configuradas. "
            "A revisão humana continua recomendada."
        )
    if client is None and not ai_available():
        raise AuditReportError("OPENAI_API_KEY não configurada no arquivo .env.")

    payload = {
        "metricas": metrics,
        "alertas": alerts.sort_values(["pontos", "impacto_estimado"], ascending=False)
        .head(20)
        .to_dict(orient="records"),
    }
    try:
        api_client = client or OpenAI()
        response = api_client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            instructions=SYSTEM_INSTRUCTIONS,
            input=json.dumps(payload, ensure_ascii=False, default=str),
        )
    except OpenAIError as exc:
        raise AuditReportError("Não foi possível gerar o parecer com a OpenAI.") from exc

    output_text = str(response.output_text).strip()
    if not output_text:
        raise AuditReportError("A OpenAI retornou um parecer vazio.")
    return output_text
