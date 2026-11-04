import unittest

from support_lab.models import SupportCase
from support_lab.normalize import normalize_text, validate


class NormalizeTests(unittest.TestCase):
    def test_collapses_whitespace(self):
        self.assertEqual(normalize_text("  hello\n  world  "), "hello world")

    def test_requires_conversation_text(self):
        case = SupportCase(case_id="SYN-X", subject="Empty", text="   ")
        self.assertIn("missing_conversation_text", validate(case))


if __name__ == "__main__":
    unittest.main()
