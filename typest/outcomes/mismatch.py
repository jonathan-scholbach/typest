import re
from typing import Optional

from typest.outcomes.base import Outcome
from typest.utils.fake_type import parse, FakeType


class Mismatch(Outcome):
    """Outcome representing a Mismatch between assigned type and actual type"""

    @classmethod
    def from_comment(
        cls,
        linenumber,
        comment: str,
    ) -> Optional["Mismatch"]:
        match = re.search(r"\s*expect-mismatch:(.+)<>\s*(.+)\s*", comment)
        if not match:
            return None
        assigned_type = parse(match.group(1))
        if not assigned_type:
            return None
        actual_type = parse(match.group(2))
        if not actual_type:
            return None
        return cls(linenumber, assigned_type, actual_type)

    def __init__(
        self,
        linenumber: int,
        assigned_type: FakeType,
        actual_type: FakeType,
    ) -> None:
        super().__init__(linenumber)
        self._assigned = assigned_type
        self._actual = actual_type

    def __repr__(self) -> str:
        return (
            f"Mismatch({self.linenumber}, {self._assigned} <> {self._actual})"
        )

    def __eq__(self, other: "Mismatch") -> bool:
        if not isinstance(other, Mismatch):
            return False

        return (
            self.linenumber == other.linenumber
            and self._assigned == other._assigned
            and self._actual == other._actual
        )
