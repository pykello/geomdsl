class GeomError(Exception):
    """Base class for normal DSL errors."""

    title = "GeomError"

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format_message())

    def format_message(self) -> str:
        if self.line is not None and self.column is not None:
            return f"{self.title} at line {self.line}, column {self.column}:\n{self.message}"
        return f"{self.title}: {self.message}"


class GeomParseError(GeomError):
    title = "ParseError"


class GeomNameError(GeomError):
    title = "NameError"


class GeomTypeError(GeomError):
    title = "TypeError"


class GeomValueError(GeomError):
    title = "ValueError"


class GeomRenderError(GeomError):
    title = "RenderError"
