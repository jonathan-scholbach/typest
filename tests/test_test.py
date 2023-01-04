from unittest import TestCase

from typest.typecheckers.mypy import Mypy


class TestMypy(TestCase):
    def test_run(self):
        errors = Mypy("/", "tests/case.py").run()
        self.assertEqual(errors, [])
