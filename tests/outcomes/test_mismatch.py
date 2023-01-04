from unittest import TestCase

from typest.outcomes.mismatch import Mismatch
from typest.utils.fake_type import FakeBuiltin


class TestFromComment(TestCase):
    def test_returns_none_if_comment_does_not_match(self):
        result = Mismatch.from_comment(1, "expect: int <> str")
        self.assertIsNone(result)

        result = Mismatch.from_comment(1, "expect-mismatch: int <>")
        self.assertIsNone(result)

        result = Mismatch.from_comment(1, "expect-mismatch: <> str")
        self.assertIsNone(result)

    def test_contains_correct_assigned_and_actual_type(self):
        result = Mismatch.from_comment(1, "expect-mismatch: int <> str")
        self.assertIsInstance(result, Mismatch)
        self.assertEqual(result._assigned, FakeBuiltin("int"))
        self.assertEqual(result._actual, FakeBuiltin("str"))
