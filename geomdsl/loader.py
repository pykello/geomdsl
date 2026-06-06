from __future__ import annotations

from pathlib import Path

from .ast import IncludeStmt, Program, SourceSpan, Statement
from .errors import GeomParseError
from .parser import parse


def load_program(source: str, *, base_path: str | Path | None = None) -> Program:
    """Parse source and expand include statements.

    Includes are resolved relative to the including file. Callers that
    evaluate a raw source string must pass a base path before includes
    can be resolved.
    """

    path = Path(base_path).resolve() if base_path is not None else None
    return _load_program(source, path, [])


def load_file(path: str | Path) -> Program:
    resolved = Path(path).resolve()
    source = resolved.read_text(encoding="utf-8")
    return _load_program(source, resolved, [])


def _load_program(source: str, path: Path | None, stack: list[Path]) -> Program:
    program = parse(source)
    statements: list[Statement] = []

    for stmt in program.statements:
        if not isinstance(stmt, IncludeStmt):
            statements.append(stmt)
            continue

        if path is None:
            raise GeomParseError(
                "include requires evaluate(..., base_path=...) or a file input.",
                stmt.span.line,
                stmt.span.column,
            )

        include_path = _resolve_include(path, stmt.path, stmt.span)
        if include_path in stack:
            chain = [*stack, include_path]
            names = " -> ".join(str(p) for p in chain)
            raise GeomParseError(f"Include cycle detected: {names}.", stmt.span.line, stmt.span.column)

        try:
            include_source = include_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise GeomParseError(f"Cannot read include '{stmt.path}': {exc}", stmt.span.line, stmt.span.column) from exc

        included = _load_program(include_source, include_path, [*stack, include_path])
        statements.extend(included.statements)

    return Program(program.span, statements)


def _resolve_include(path: Path, include: str, span: SourceSpan) -> Path:
    include_path = Path(include)
    if include_path.is_absolute():
        raise GeomParseError("include paths must be relative.", span.line, span.column)
    return (path.parent / include_path).resolve()
