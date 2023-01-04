from unittest import TestCase

from typest.test import Test as Typest


class TestTest(TestCase):
    def test_test(self):
        errors = Typest("/", "tests/case.py").run()
        self.assertEqual(errors, [])
