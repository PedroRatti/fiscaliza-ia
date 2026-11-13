from src.formatting import format_currency, format_number
from src.presentation import layout


def test_format_currency_uses_brazilian_separators():
    assert format_currency(1234.5) == "R$ 1.234,50"


def test_format_currency_disambiguates_dashboard_impact():
    assert format_currency(87900) == "R$ 87.900,00"


def test_format_currency_includes_zero_cents():
    assert format_currency(0) == "R$ 0,00"


def test_format_number_uses_brazilian_separators():
    assert format_number(1234.5) == "1.234,50"


def test_header_html_starts_at_the_markdown_margin(monkeypatch):
    rendered_blocks: list[str] = []
    monkeypatch.setattr(
        layout.st,
        "markdown",
        lambda body, **_kwargs: rendered_blocks.append(body),
    )

    layout.render_header()

    assert rendered_blocks[1].startswith('<div class="hero">')

