from typing import Optional

from typest.outcomes.base import Outcome


class Flaw(Outcome):
    """Outcome representing an unspecified typechecker error"""

    @classmethod
    def from_comment(cls, linenumber: int, comment: str) -> Optional["Flaw"]:
        if comment.strip() == "expect-error":
            return cls(linenumber)
        return None

    def __eq__(self, other: "Flaw") -> bool:
        if not isinstance(other, Flaw):
            return False

        return self.linenumber == other.linenumber

    def __repr__(self) -> str:
        return f"Flaw({self.linenumber})"
