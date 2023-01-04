import re
from typing import Optional

from typest.utils.fake_type import parse
from typest.utils.fake_type import FakeType


class ParsingFailed(ValueError):
    pass


class Outcome:
    def from_mypy_output(cls, raw: str) -> Optional["Outcome"]:
        try:
            linenumber = Outcome._linenumber_from_mypy_output(raw)
            return Outcome(linenumber)
        except ParsingFailed:
            return None

    def __init__(self, linenumber) -> None:
        self.linenumber = linenumber


class TypeOutcome(Outcome):

    comment_prefix: str = " expect-type: "

    @classmethod
    def from_comment(
        cls,
        linenumber: int,
        comment: str,
    ) -> Optional["TypeOutcome"]:
        try:
            type_in_comment = cls._type_from_comment(comment)
            return cls(linenumber, type_in_comment)
        except ParsingFailed:
            return None

    def __init__(self, linenumber: int, typ: FakeType) -> None:
        super().__init__(linenumber)
        self._type = typ

    def __repr__(self) -> str:
        return f"TypeOutcome({self.linenumber}, {self._type})"

    def __eq__(self, other: "TypeOutcome") -> bool:
        if not isinstance(other, TypeOutcome):
            return False
        return self._type == other._type and self.linenumber == other.linenumber

    @classmethod
    def _type_from_comment(cls, comment: str) -> FakeType:
        match = re.search(f"{cls.comment_prefix}(.*)", comment)
        if not match:
            raise ParsingFailed()
        return parse(match.group(1))


class ErrorOutcome(Outcome):

    comment_prefix: str = "expect-error:"

    @classmethod
    def from_comment(
        cls, linenumber: int, comment: str
    ) -> Optional["ErrorOutcome"]:
        comment = comment.strip()
        if comment.startswith(cls.comment_prefix):
            return cls(linenumber, comment[len(cls.comment_prefix) :].strip())
        return None

    def __init__(self, linenumber: int, error: str) -> None:
        super().__init__(linenumber)
        self.error = error

    def __eq__(self, other: "ErrorOutcome") -> bool:
        if not isinstance(other, ErrorOutcome):
            return False

        if self.linenumber != other.linenumber:
            return False

        if self.error is None or other.error is None:
            # Error outcomes without specification are just checked for existence
            return True

        return self.error == other.error
