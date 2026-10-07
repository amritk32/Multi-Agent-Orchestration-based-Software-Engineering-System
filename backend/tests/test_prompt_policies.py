import unittest

from prompts import (
    ARCHITECTURE_SYSTEM_PROMPT,
    BOILERPLATE_SYSTEM_PROMPT,
    CODE_WRITING_SYSTEM_PROMPT,
)


class PromptPolicyTests(unittest.TestCase):
    def test_architecture_requires_library_selection(self):
        self.assertIn("Technology and library selection", ARCHITECTURE_SYSTEM_PROMPT)
        self.assertIn("LangChain", ARCHITECTURE_SYSTEM_PROMPT)
        self.assertIn("database driver", ARCHITECTURE_SYSTEM_PROMPT)

    def test_boilerplate_requires_dependency_contract(self):
        self.assertIn("LIBRARY AND DEPENDENCY CONTRACT", BOILERPLATE_SYSTEM_PROMPT)
        self.assertIn("Installation commands", BOILERPLATE_SYSTEM_PROMPT)

    def test_code_writer_must_use_selected_libraries(self):
        self.assertIn(
            "LIBRARY-FIRST IMPLEMENTATION CONTRACT", CODE_WRITING_SYSTEM_PROMPT
        )
        self.assertIn("must actually import and use", CODE_WRITING_SYSTEM_PROMPT)
        self.assertIn("SQLAlchemy", CODE_WRITING_SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
