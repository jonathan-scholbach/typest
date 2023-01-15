from unittest import TestCase
from pathlib import Path

from typest.typecheckers.mypy import Mypy


class TestMypy(TestCase):
    def test_run(self):
        errors = Mypy(Path("tests/cases/passing_case.py")).run()
        self.assertEqual(errors, [])
