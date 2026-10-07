import unittest

from generated_code_validation import validate_generated_source


class GeneratedCodeValidationTests(unittest.TestCase):
    def assert_rejected(self, source: str, file_kind: str):
        with self.assertRaises(ValueError):
            validate_generated_source(source, file_kind)

    def test_rejects_frontend_in_backend(self):
        self.assert_rejected("FRONTEND_HTML = '<html>'", "backend")

    def test_rejects_backend_in_frontend(self):
        self.assert_rejected("from fastapi import FastAPI", "frontend")

    def test_rejects_javascript_backend(self):
        self.assert_rejected("const app = express()", "backend")

    def test_rejects_typescript_backend(self):
        self.assert_rejected("interface User { id: string }", "backend")

    def test_allows_valid_noop_sections(self):
        validate_generated_source("class ConfigResponse:\n    pass", "backend")

    def test_allows_unimplemented_sections_for_now(self):
        validate_generated_source("def handler():\n    pass\n\n# TODO", "backend")
        validate_generated_source("raise NotImplementedError", "frontend")

    def test_accepts_separated_source(self):
        validate_generated_source("def handler():\n    return 1", "backend")
        validate_generated_source("fetch('/api/items')", "frontend")


if __name__ == "__main__":
    unittest.main()
