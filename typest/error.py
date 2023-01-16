from pathlib import Path

from typest.outcomes import Flaw, RevealedType, Outcome
from typest.utils.color import Color


class Error:
    """Wrapper class for holding test errors and printing them"""

    def __init__(
        self,
        path: Path,
        expected: Outcome,
        actual: Outcome | None,
    ):
        self.path = path
        self.linenumber = expected.linenumber
        self.expected = expected
        self.actual = actual

    @staticmethod
    def _pad(string: str) -> str:
        return string.ljust(20)

    def __repr__(self) -> str:
        return f"Error({self.path}, {self.expected}, {self.actual})"

    def __str__(self) -> str:
        msg = f"=== LINE {self.linenumber} ===\n"

        if isinstance(self.expected, RevealedType):
            msg += (
                self._pad("Expected type")
                + Color.ALERT.value
                + str(self.expected._type)
                + Color.RESET.value
                + "\n"
            )
            if isinstance(self.actual, RevealedType):
                msg += (
                    self._pad("Found type")
                    + Color.OK.value
                    + str(self.actual._type)
                    + Color.RESET.value
                    + "\n"
                )
            else:
                msg += (
                    "No type note found. Did you forget to call `reveal_type`?"
                    "\n"
                )

        if isinstance(self.expected, Flaw):
            if self.expected.error is None:
                msg += "Expected error.\n"
            else:
                msg += (
                    self._pad("Expected error")
                    + Color.ALERT.value
                    + self.expected.error
                    + Color.RESET.value
                    + "\n"
                )
            if isinstance(self.actual, Flaw):
                msg += (
                    self._pad("Found error")
                    + Color.OK.value
                    + self.actual.error
                    + Color.RESET.value
                    + "\n"
                )
            else:
                msg += f"No error found."

        return msg
