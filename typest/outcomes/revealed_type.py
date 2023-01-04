import re
from typing import Optional

from typest.outcomes.base import Outcome
from typest.utils.fake_type import parse, FakeType


class RevealedType(Outcome):
    """Outcome representing a revealed type"""

    @classmethod
    def from_comment(
        cls,
        linenumber: int,
        comment: str,
    ) -> Optional["RevealedType"]:
        match = re.search(r"\s*expect-type:(.*)", comment)
        if not match:
            return None
        typ = parse(match.group(1))
        return cls(linenumber, typ)

    def __init__(self, linenumber: int, typ: FakeType) -> None:
        super().__init__(linenumber)
        self._type = typ

    def __repr__(self) -> str:
        return f"RevealedType({self.linenumber}, {self._type})"

    def __eq__(self, other: "RevealedType") -> bool:
        if not isinstance(other, RevealedType):
            return False
        return self._type == other._type and self.linenumber == other.linenumber
