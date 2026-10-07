import unittest

from syntax_analysis import SyntaxAnalyzer


class SyntaxAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = SyntaxAnalyzer()

    def assert_valid(self, source):
        self.assertTrue(self.analyzer.analyze(source))

    def assert_invalid(self, source):
        self.assertFalse(self.analyzer.analyze(source))

    def test_valid_python(self):
        self.assert_valid("value = 1 + 2.5\n")

    def test_invalid_python(self):
        self.assert_invalid("value = (1 + )\n")

    def test_invalid_character(self):
        self.assert_invalid("value = 1 $\n")

    def test_malformed_expression(self):
        self.assert_invalid("value = [1, 2\n")

    def test_missing_colon(self):
        self.assert_invalid("if value\n    pass\n")

    def test_missing_delimiter(self):
        self.assert_invalid('result = {"name": "Krishna"\n')

    def test_valid_function(self):
        self.assert_valid("def add(first, second):\n    return first + second\n")

    def test_valid_class(self):
        self.assert_valid(
            "class Example:\n" "    def value(self):\n" "        return True\n"
        )

    def test_valid_noop_statements(self):
        self.assert_valid(
            "class ConfigResponse:\n    pass\n\n"
            "def fallback():\n    try:\n        return 1\n"
            "    except Exception:\n        pass\n"
        )


if __name__ == "__main__":
    unittest.main()
