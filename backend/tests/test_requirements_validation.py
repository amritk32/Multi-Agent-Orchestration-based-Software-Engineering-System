import unittest

from requirements_validation import validate_requirements


class RequirementsValidationTests(unittest.TestCase):
    def test_rejects_single_character_input(self):
        self.assertIsNotNone(validate_requirements("d"))

    def test_rejects_gibberish_input(self):
        self.assertIsNotNone(
            validate_requirements("afodenuofnaiofnoiewfoijaweofijweoi")
        )

    def test_rejects_spaced_gibberish_input(self):
        self.assertIsNotNone(validate_requirements("asdf qwer zxcv"))

    def test_accepts_action_without_specific_software_term(self):
        self.assertIsNone(validate_requirements("Make a simple game for children"))

    def test_accepts_meaningful_project_request(self):
        self.assertIsNone(validate_requirements("Build a todo API with a web frontend"))


if __name__ == "__main__":
    unittest.main()
