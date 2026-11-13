from __future__ import annotations

from typing import Callable

import pandas as pd

from src.domain.models import Alert
from src.formatting import format_currency, format_number


def _alert(row_id: int, row: pd.Series, **kwargs: object) -> Alert:
    return Alert(row_id=row_id, contrato=str(row["contrato"]), item=str(row["item"]), **kwargs)


def check_quantity_excess(row_id: int, row: pd.Series) -> Alert | None:
    contracted = float(row["quantidade_contratada"])
    measured = float(row["quantidade_acumulada"])
    if measured <= contracted:
        return None

    excess = measured - contracted
    excess_percentage = excess / contracted * 100
    unit = str(row["unidade_medida"])
    return _alert(
        row_id,
        row,
        rule_id="QTD_EXCEDENTE",
        titulo="Quantidade acima do contrato vigente",
        severidade="Crítica" if excess_percentage >= 10 else "Alta",
        pontos=40 if excess_percentage >= 10 else 30,
        evidencia=(
            f"Excesso de {format_number(excess)} {unit} "
            f"({format_number(excess_percentage, 1)}%) "
            "sobre a quantidade contratual vigente."
        ),
        impacto_estimado=excess * float(row["preco_unitario_medido"]),
        recomendacao="Conferir memória de cálculo e base contratual vigente.",
    )


def check_price_difference(row_id: int, row: pd.Series) -> Alert | None:
    contracted = float(row["preco_unitario_contratado"])
    measured = float(row["preco_unitario_medido"])
    difference_percentage = abs(measured - contracted) / contracted * 100
    if difference_percentage <= 1:
        return None

    measured_quantity = float(row["quantidade_acumulada"])
    return _alert(
        row_id,
        row,
        rule_id="PRECO_DIVERGENTE",
        titulo="Preço unitário divergente",
        severidade="Alta" if difference_percentage >= 10 else "Média",
        pontos=30 if difference_percentage >= 10 else 20,
        evidencia=(
            f"Preço aplicado {format_currency(measured)} difere "
            f"{format_number(difference_percentage, 1)}% "
            f"do contratado ({format_currency(contracted)})."
        ),
        impacto_estimado=max(measured - contracted, 0) * measured_quantity,
        recomendacao="Conferir tabela contratual vigente, reajustes e documentação.",
    )


def check_physical_financial_gap(row_id: int, row: pd.Series) -> Alert | None:
    physical = float(row["avanco_fisico_pct"])
    financial = float(row["avanco_financeiro_pct"])
    gap = financial - physical
    if gap < 15:
        return None

    return _alert(
        row_id,
        row,
        rule_id="FISICO_FINANCEIRO",
        titulo="Descompasso físico-financeiro",
        severidade="Alta" if gap >= 25 else "Média",
        pontos=30 if gap >= 25 else 20,
        evidencia=(
            f"Avanço financeiro de {format_number(financial, 1)}% supera o físico de "
            f"{format_number(physical, 1)}% em {format_number(gap, 1)} p.p."
        ),
        impacto_estimado=0,
        recomendacao="Validar memória da medição e evidência do serviço executado em campo.",
    )


def check_schedule(row_id: int, row: pd.Series) -> Alert | None:
    start = pd.to_datetime(row["inicio_previsto"])
    end = pd.to_datetime(row["fim_previsto"])
    measured_at = pd.to_datetime(row["data_medicao"])
    if start <= measured_at <= end:
        return None

    return _alert(
        row_id,
        row,
        rule_id="FORA_CRONOGRAMA",
        titulo="Medição fora do período previsto",
        severidade="Média",
        pontos=20,
        evidencia=(
            f"Medição em {measured_at.strftime('%d/%m/%Y')} fora do intervalo "
            f"de {start.strftime('%d/%m/%Y')} a {end.strftime('%d/%m/%Y')}."
        ),
        impacto_estimado=0,
        recomendacao="Conferir ordem de serviço, prorrogação de prazo e data de execução.",
    )


AuditRule = Callable[[int, pd.Series], Alert | None]
AUDIT_RULES: tuple[AuditRule, ...] = (
    check_quantity_excess,
    check_price_difference,
    check_physical_financial_gap,
    check_schedule,
)
