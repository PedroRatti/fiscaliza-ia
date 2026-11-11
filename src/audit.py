from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date

import pandas as pd

REQUIRED_COLUMNS = {
    "contrato",
    "item",
    "descricao_contratada",
    "descricao_medida",
    "quantidade_contratada",
    "quantidade_acumulada",
    "preco_unitario_contratado",
    "preco_unitario_medido",
    "avanco_fisico_pct",
    "avanco_financeiro_pct",
    "inicio_previsto",
    "fim_previsto",
    "data_medicao",
    "possui_aditivo",
}


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

    def to_dict(self) -> dict:
        return asdict(self)


def validate_columns(df: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError("Colunas obrigatorias ausentes: " + ", ".join(missing))


def _money(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "sim", "s", "yes"}


def _alert(row_id: int, row: pd.Series, **kwargs) -> Alert:
    return Alert(row_id=row_id, contrato=str(row["contrato"]), item=str(row["item"]), **kwargs)


def audit_measurements(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df)
    alerts: list[Alert] = []

    for row_id, row in df.reset_index(drop=True).iterrows():
        qty_contract = float(row["quantidade_contratada"])
        qty_measured = float(row["quantidade_acumulada"])
        price_contract = float(row["preco_unitario_contratado"])
        price_measured = float(row["preco_unitario_medido"])
        physical = float(row["avanco_fisico_pct"])
        financial = float(row["avanco_financeiro_pct"])
        has_addendum = _bool(row["possui_aditivo"])

        if qty_contract > 0 and qty_measured > qty_contract and not has_addendum:
            excess = qty_measured - qty_contract
            pct = excess / qty_contract * 100
            impact = excess * price_measured
            alerts.append(
                _alert(
                    row_id,
                    row,
                    rule_id="QTD_EXCEDENTE",
                    titulo="Quantidade acima do contrato",
                    severidade="Critica" if pct >= 10 else "Alta",
                    pontos=40 if pct >= 10 else 30,
                    evidencia=(
                        f"Excesso de {excess:.2f} unidades ({pct:.1f}%), sem aditivo informado."
                    ),
                    impacto_estimado=impact,
                    recomendacao="Verificar aditivo, memoria de calculo e autorizacao da medicao.",
                )
            )

        if price_contract > 0:
            price_delta_pct = abs(price_measured - price_contract) / price_contract * 100
            if price_delta_pct > 1:
                impact = max(price_measured - price_contract, 0) * qty_measured
                alerts.append(
                    _alert(
                        row_id,
                        row,
                        rule_id="PRECO_DIVERGENTE",
                        titulo="Preco unitario divergente",
                        severidade="Alta" if price_delta_pct >= 10 else "Media",
                        pontos=30 if price_delta_pct >= 10 else 20,
                        evidencia=(
                            f"Preco medido {_money(price_measured)} difere {price_delta_pct:.1f}% "
                            f"do contratado ({_money(price_contract)})."
                        ),
                        impacto_estimado=impact,
                        recomendacao=(
                            "Conferir tabela contratual, reajuste e documentacao do aditivo."
                        ),
                    )
                )

        physical_financial_gap = financial - physical
        if physical_financial_gap >= 15:
            alerts.append(
                _alert(
                    row_id,
                    row,
                    rule_id="FISICO_FINANCEIRO",
                    titulo="Descompasso fisico-financeiro",
                    severidade="Alta" if physical_financial_gap >= 25 else "Media",
                    pontos=30 if physical_financial_gap >= 25 else 20,
                    evidencia=(
                        f"Avanco financeiro de {financial:.1f}% supera o fisico de "
                        f"{physical:.1f}% em {physical_financial_gap:.1f} p.p."
                    ),
                    impacto_estimado=0,
                    recomendacao=(
                        "Validar memoria da medicao e evidencia do servico executado em campo."
                    ),
                )
            )

        start = pd.to_datetime(row["inicio_previsto"], errors="coerce")
        end = pd.to_datetime(row["fim_previsto"], errors="coerce")
        measured_at = pd.to_datetime(row["data_medicao"], errors="coerce")
        if pd.notna(measured_at) and (
            (pd.notna(start) and measured_at < start) or (pd.notna(end) and measured_at > end)
        ):
            alerts.append(
                _alert(
                    row_id,
                    row,
                    rule_id="FORA_CRONOGRAMA",
                    titulo="Medicao fora do periodo previsto",
                    severidade="Media",
                    pontos=20,
                    evidencia=(
                        f"Medicao em {measured_at.date()} fora do intervalo "
                        f"{start.date()} a {end.date()}."
                    ),
                    impacto_estimado=0,
                    recomendacao=(
                        "Conferir ordem de servico, prorrogacao de prazo e data de execucao."
                    ),
                )
            )

    columns = list(Alert.__dataclass_fields__)
    return pd.DataFrame([alert.to_dict() for alert in alerts], columns=columns)


def risk_summary(df: pd.DataFrame, alerts: pd.DataFrame) -> pd.DataFrame:
    base = df.reset_index(drop=True).copy()
    base["row_id"] = base.index
    if alerts.empty:
        base["pontuacao_risco"] = 0
        base["nivel_risco"] = "Baixo"
        base["total_alertas"] = 0
        return base

    grouped = alerts.groupby("row_id").agg(
        pontuacao_risco=("pontos", "sum"), total_alertas=("rule_id", "count")
    )
    base = base.merge(grouped, on="row_id", how="left").fillna(
        {"pontuacao_risco": 0, "total_alertas": 0}
    )
    base["pontuacao_risco"] = base["pontuacao_risco"].clip(upper=100).astype(int)
    base["total_alertas"] = base["total_alertas"].astype(int)
    base["nivel_risco"] = pd.cut(
        base["pontuacao_risco"],
        bins=[-1, 19, 49, 79, 100],
        labels=["Baixo", "Medio", "Alto", "Critico"],
    ).astype(str)
    return base


def portfolio_metrics(df: pd.DataFrame, alerts: pd.DataFrame) -> dict:
    contract_value = (
        df["quantidade_contratada"].astype(float) * df["preco_unitario_contratado"].astype(float)
    ).sum()
    return {
        "contratos": int(df["contrato"].nunique()),
        "itens": int(len(df)),
        "alertas": int(len(alerts)),
        "impacto_estimado": float(alerts["impacto_estimado"].sum()) if not alerts.empty else 0,
        "valor_contratado": float(contract_value),
        "data_analise": date.today().isoformat(),
    }
