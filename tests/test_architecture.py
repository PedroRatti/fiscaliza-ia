import ast
from pathlib import Path

DOMAIN_PATH = Path("src/domain")
FORBIDDEN_DEPENDENCIES = ("src.infrastructure", "src.presentation")


def imported_modules(source_file: Path) -> set[str]:
    tree = ast.parse(source_file.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_domain_does_not_depend_on_external_layers():
    violations: list[str] = []

    for source_file in DOMAIN_PATH.glob("*.py"):
        for imported_module in imported_modules(source_file):
            if imported_module.startswith(FORBIDDEN_DEPENDENCIES):
                violations.append(f"{source_file}: {imported_module}")

    assert not violations, "Dependências proibidas no domínio:\n" + "\n".join(violations)

