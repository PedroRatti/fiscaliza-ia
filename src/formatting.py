from __future__ import annotations


def format_number(value: float, decimal_places: int = 2) -> str:
    formatted = f"{value:,.{decimal_places}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def format_currency(value: float) -> str:
    return f"R$ {format_number(value)}"
