from types import SimpleNamespace

import pandas as pd
import pytest

from src.infrastructure import AuditReportError, generate_audit_report


class FakeResponses:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text
        self.request: dict[str, object] | None = None

    def create(self, **kwargs: object) -> SimpleNamespace:
        self.request = kwargs
        return SimpleNamespace(output_text=self.output_text)


class FakeClient:
    def __init__(self, output_text: str) -> None:
        self.responses = FakeResponses(output_text)


def alert_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "rule_id": "QTD_EXCEDENTE",
                "pontos": 40,
                "impacto_estimado": 150.0,
                "evidencia": "Excesso sintético para teste.",
            }
        ]
    )


def test_report_without_alerts_does_not_require_client():
    report = generate_audit_report(pd.DataFrame(), {"alertas": 0})

    assert "Nenhum alerta" in report


def test_report_requires_key_when_client_is_not_injected(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(AuditReportError, match="OPENAI_API_KEY não configurada"):
        generate_audit_report(alert_frame(), {"alertas": 1})


def test_report_uses_injected_client_without_real_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = FakeClient("Parecer sintético sujeito à revisão humana.")

    report = generate_audit_report(alert_frame(), {"alertas": 1}, client=client)

    assert report == "Parecer sintético sujeito à revisão humana."
    assert client.responses.request is not None
    assert client.responses.request["model"] == "gpt-5-mini"
    assert "QTD_EXCEDENTE" in str(client.responses.request["input"])


def test_empty_ai_response_is_rejected():
    client = FakeClient("   ")

    with pytest.raises(AuditReportError, match="parecer vazio"):
        generate_audit_report(alert_frame(), {"alertas": 1}, client=client)

