from typest.outcome import ErrorOutcome, TypeOutcome, Outcome
from typest.utils.color import Color


class Error:
    """Wrapper class for holding test errors and printing them"""

    def __init__(
        self,
        filename: str,
        expected: Outcome,
        actual: Outcome | None,
    ):
        self.filename = filename
        self.linenumber = expected.linenumber
        self.expected = expected
        self.actual = actual

    @staticmethod
    def _pad(string: str) -> str:
        return string.ljust(20)

    def __repr__(self) -> str:
        return f"Error({self.filename}, {self.expected}, {self.actual})"

    def __str__(self) -> str:
        msg = f"=== LINE {self.linenumber} ===\n"

        if isinstance(self.expected, TypeOutcome):
            msg += (
                self._pad("Expected type")
                + Color.ALERT.value
                + str(self.expected._type)
                + Color.RESET.value
                + "\n"
            )
            if isinstance(self.actual, TypeOutcome):
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

        if isinstance(self.expected, ErrorOutcome):
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
            if isinstance(self.actual, ErrorOutcome):
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
