from __future__ import annotations

import json
from dataclasses import dataclass

from .ast import (
    Assignment,
    BinaryExpr,
    BooleanExpr,
    CallExpr,
    DefaultsStmt,
    DrawStmt,
    ExportStmt,
    Expr,
    IncludeStmt,
    IndexExpr,
    InlineStyle,
    NumberExpr,
    ParamRange,
    Program,
    SceneStmt,
    SourceSpan,
    Statement,
    StringExpr,
    StyleExpr,
    StyleRef,
    StyleStmt,
    TupleExpr,
    UnaryExpr,
    VarExpr,
    VersionStmt,
)
from .errors import GeomParseError


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    column: int
    index: int

    @property
    def span(self) -> SourceSpan:
        return SourceSpan(self.line, self.column, self.index)


_SINGLE = {
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    "[": "LBRACKET",
    "]": "RBRACKET",
    ",": "COMMA",
    ":": "COLON",
    "=": "EQUAL",
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
    "^": "CARET",
    "@": "AT",
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.i = 0
        self.line = 1
        self.column = 1

    def tokens(self) -> list[Token]:
        out: list[Token] = []
        while self.i < len(self.source):
            ch = self.source[self.i]
            if ch in " \t\r\n":
                self._advance()
                continue
            if ch == "#":
                while self.i < len(self.source) and self.source[self.i] != "\n":
                    self._advance()
                continue
            if ch == "." and self._peek(1) == ".":
                out.append(self._token("RANGE", ".."))
                self._advance(2)
                continue
            if ch in _SINGLE:
                out.append(self._token(_SINGLE[ch], ch))
                self._advance()
                continue
            if ch == '"':
                out.append(self._string())
                continue
            if ch.isdigit() or (ch == "." and self._peek(1).isdigit()):
                out.append(self._number())
                continue
            if ch.isalpha() or ch == "_":
                out.append(self._ident())
                continue
            raise GeomParseError(f"Unexpected character {ch!r}.", self.line, self.column)
        out.append(Token("EOF", "", self.line, self.column, self.i))
        return out

    def _peek(self, offset: int) -> str:
        j = self.i + offset
        return self.source[j] if j < len(self.source) else ""

    def _token(self, kind: str, value: str) -> Token:
        return Token(kind, value, self.line, self.column, self.i)

    def _advance(self, n: int = 1) -> None:
        for _ in range(n):
            ch = self.source[self.i]
            self.i += 1
            if ch == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1

    def _string(self) -> Token:
        start = self._token("STRING", "")
        self._advance()
        value = []
        while self.i < len(self.source):
            ch = self.source[self.i]
            if ch == '"':
                self._advance()
                return Token("STRING", "".join(value), start.line, start.column, start.index)
            if ch == "\\":
                nxt = self._peek(1)
                escapes = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
                value.append(escapes.get(nxt, nxt))
                self._advance(2)
                continue
            value.append(ch)
            self._advance()
        raise GeomParseError("Unterminated string literal.", start.line, start.column)

    def _number(self) -> Token:
        start = self._token("NUMBER", "")
        text = []
        seen_dot = False
        while self.i < len(self.source):
            ch = self.source[self.i]
            if ch.isdigit():
                text.append(ch)
                self._advance()
                continue
            if ch == "." and not seen_dot and self._peek(1) != ".":
                seen_dot = True
                text.append(ch)
                self._advance()
                continue
            break
        return Token("NUMBER", "".join(text), start.line, start.column, start.index)

    def _ident(self) -> Token:
        start = self._token("IDENT", "")
        text = []
        while self.i < len(self.source):
            ch = self.source[self.i]
            if ch.isalnum() or ch == "_":
                text.append(ch)
                self._advance()
                continue
            break
        return Token("IDENT", "".join(text), start.line, start.column, start.index)


class Parser:
    def __init__(self, source: str):
        self.tokens = Lexer(source).tokens()
        self.i = 0

    def parse_program(self) -> Program:
        span = self.peek().span
        statements: list[Statement] = []
        while not self.match("EOF"):
            statements.append(self.statement())
        return Program(span, statements)

    def statement(self) -> Statement:
        token = self.expect("IDENT", "Expected statement.")
        if token.value == "version":
            version = self.expect("STRING", "Expected version string after 'version'.")
            return VersionStmt(token.span, version.value)
        if token.value == "include":
            path = self.expect("STRING", "Expected path string after 'include'.")
            return IncludeStmt(token.span, path.value)
        if token.value == "scene":
            return SceneStmt(token.span, self.named_call_args())
        if token.value == "export":
            return ExportStmt(token.span, self.named_call_args())
        if token.value == "defaults":
            return DefaultsStmt(token.span, self.defaults_entries())
        if token.value == "style":
            name = self.expect("IDENT", "Expected style name.")
            self.expect("EQUAL", "Expected '=' after style name.")
            return StyleStmt(token.span, name.value, self.style_expr())
        if token.value == "draw":
            expr = self.expr()
            style = self.style_expr() if self.match("AT") else None
            return DrawStmt(token.span, expr, style)
        name = token.value
        self.expect("EQUAL", "Expected '=' in assignment.")
        return Assignment(token.span, name, self.expr())

    def named_call_args(self) -> dict[str, Expr]:
        self.expect("LPAREN", "Expected '('.")
        args: dict[str, Expr] = {}
        if not self.match("RPAREN"):
            while True:
                name = self.expect("IDENT", "Expected named argument.")
                self.expect("EQUAL", "Expected '=' after argument name.")
                args[name.value] = self.expr()
                if self.match("COMMA"):
                    if self.match("RPAREN"):
                        break
                    continue
                self.expect("RPAREN", "Expected ')' after arguments.")
                break
        return args

    def defaults_entries(self) -> dict[str, StyleExpr]:
        self.expect("LBRACE", "Expected '{' after defaults.")
        entries: dict[str, StyleExpr] = {}
        while not self.match("RBRACE"):
            name = self.expect("IDENT", "Expected default category.")
            self.expect("COLON", "Expected ':' after default category.")
            entries[name.value] = self.style_expr()
            self.match("COMMA")
        return entries

    def style_expr(self) -> StyleExpr:
        if self.match("LBRACE"):
            start = self.previous()
            fields: dict[str, Expr] = {}
            if not self.match("RBRACE"):
                while True:
                    name = self.expect("IDENT", "Expected style field name.")
                    self.expect("COLON", "Expected ':' after style field.")
                    fields[name.value] = self.expr()
                    if self.match("COMMA"):
                        if self.match("RBRACE"):
                            break
                        continue
                    self.expect("RBRACE", "Expected '}' after style fields.")
                    break
            return InlineStyle(start.span, fields)
        name = self.expect("IDENT", "Expected style name or inline style.")
        return StyleRef(name.span, name.value)

    def expr(self) -> Expr:
        return self.add_expr()

    def add_expr(self) -> Expr:
        expr = self.mul_expr()
        while self.match("PLUS", "MINUS"):
            op = self.previous()
            right = self.mul_expr()
            expr = BinaryExpr(op.span, expr, op.value, right)
        return expr

    def mul_expr(self) -> Expr:
        expr = self.pow_expr()
        while self.match("STAR", "SLASH"):
            op = self.previous()
            right = self.pow_expr()
            expr = BinaryExpr(op.span, expr, op.value, right)
        return expr

    def pow_expr(self) -> Expr:
        expr = self.unary_expr()
        if self.match("CARET"):
            op = self.previous()
            right = self.pow_expr()
            expr = BinaryExpr(op.span, expr, op.value, right)
        return expr

    def unary_expr(self) -> Expr:
        if self.match("MINUS"):
            op = self.previous()
            return UnaryExpr(op.span, "-", self.unary_expr())
        return self.postfix_expr()

    def postfix_expr(self) -> Expr:
        expr = self.primary()
        while self.match("LBRACKET"):
            start = self.previous()
            index = self.expr()
            self.expect("RBRACKET", "Expected ']' after index.")
            expr = IndexExpr(start.span, expr, index)
        return expr

    def primary(self) -> Expr:
        if self.match("NUMBER"):
            tok = self.previous()
            return NumberExpr(tok.span, float(tok.value))
        if self.match("STRING"):
            tok = self.previous()
            return StringExpr(tok.span, tok.value)
        if self.match("IDENT"):
            tok = self.previous()
            if tok.value in {"true", "false"}:
                return BooleanExpr(tok.span, tok.value == "true")
            if self.match("LPAREN"):
                return CallExpr(tok.span, tok.value, self.call_args())
            return VarExpr(tok.span, tok.value)
        if self.match("LPAREN"):
            start = self.previous()
            first = self.expr()
            if self.match("COMMA"):
                second = self.expr()
                items = [first, second]
                while self.match("COMMA"):
                    items.append(self.expr())
                self.expect("RPAREN", "Expected ')' after tuple.")
                return TupleExpr(start.span, items)
            self.expect("RPAREN", "Expected ')' after expression.")
            return first
        tok = self.peek()
        raise GeomParseError("Expected expression.", tok.line, tok.column)

    def call_args(self) -> list[Expr | ParamRange]:
        args: list[Expr | ParamRange] = []
        if self.match("RPAREN"):
            return args
        while True:
            if self.check("IDENT") and self.check_next("EQUAL"):
                name = self.advance()
                self.advance()
                start = self.expr()
                self.expect("RANGE", "Expected '..' in parameter range.")
                end = self.expr()
                args.append(ParamRange(name.span, name.value, start, end))
            else:
                args.append(self.expr())
            if self.match("COMMA"):
                if self.check("RPAREN"):
                    tok = self.peek()
                    raise GeomParseError("Expected expression after ','.", tok.line, tok.column)
                continue
            self.expect("RPAREN", "Expected ')' after arguments.")
            break
        return args

    def match(self, *kinds: str) -> bool:
        if self.peek().kind in kinds:
            self.advance()
            return True
        return False

    def expect(self, kind: str, message: str) -> Token:
        if self.check(kind):
            return self.advance()
        tok = self.peek()
        raise GeomParseError(message, tok.line, tok.column)

    def check(self, kind: str) -> bool:
        return self.peek().kind == kind

    def check_next(self, kind: str) -> bool:
        return self.tokens[self.i + 1].kind == kind if self.i + 1 < len(self.tokens) else False

    def advance(self) -> Token:
        tok = self.tokens[self.i]
        self.i += 1
        return tok

    def previous(self) -> Token:
        return self.tokens[self.i - 1]

    def peek(self) -> Token:
        return self.tokens[self.i]


def parse(source: str) -> Program:
    return Parser(source).parse_program()


def dumps_ast(program: Program) -> str:
    from .ast import as_plain

    return json.dumps(as_plain(program), indent=2, sort_keys=True)
