import ast


class SyntaxAnalyzer:
    """Validate generated Python using Python's own parser."""

    def __init__(self) -> None:
        self.last_error: str | None = None

    def analyze(self, source: str) -> bool:
        self.last_error = None
        try:
            ast.parse(source)
            return True
        except SyntaxError as error:
            self.last_error = self._format_error(error)
            return False

    @staticmethod
    def _format_error(error: SyntaxError) -> str:
        return f"{error.msg} at line {error.lineno}, column {error.offset}"
