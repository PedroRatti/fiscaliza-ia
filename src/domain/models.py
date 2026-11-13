from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Alert:
    row_id: int
    contrato: str
    item: str
    rule_id: str
    titulo: str
    severidade: str
    pontos: int
    evidencia: str
    impacto_estimado: float
    recomendacao: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
