from unittest import TestCase

from typy.test import Test as TypyTest


class TestTest(TestCase):
    def test_test(self):
        errors = TypyTest("/", "tests/case.py").run()
        self.assertEqual(errors, [])
