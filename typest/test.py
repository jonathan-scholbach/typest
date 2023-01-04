from os.path import relpath

from subprocess import Popen, PIPE

from comment_parser import comment_parser

from typest.error import Error
from typest.outcome import ErrorOutcome, Outcome, TypeOutcome
from typest.utils.color import Color


class NoTestFound(Exception):
    pass


class Test:
    def __init__(self, base_path: str, file_path: str) -> None:
        self.path = file_path
        self.rel_path = relpath(file_path, base_path)
        self.command = ["mypy", self.path]

    def _expected_outcomes(self) -> list[Outcome]:
        expected: list[Outcome] = []
        for comment in comment_parser.extract_comments(self.path):
            text = comment.text()
            linenumber = comment.line_number()
            expectation = TypeOutcome.from_comment(
                linenumber, text
            ) or ErrorOutcome.from_comment(linenumber, text)
            if expectation is not None:
                expected.append(expectation)
        return expected

    def _actual_outcomes(self) -> list[Outcome]:
        actual: list[Outcome] = []
        process = Popen(self.command, stdout=PIPE)
        output, _ = process.communicate()
        for line in output.decode("utf-8").split("\n"):
            outcome = TypeOutcome.from_mypy_output(
                line
            ) or ErrorOutcome.from_mypy_output(line)
            if outcome is not None:
                actual.append(outcome)
        return actual

    def run(self) -> list[Error]:
        """Raises NoTestFound if no tests are defined in this testfile"""
        expected_outcomes = self._expected_outcomes()
        if not expected_outcomes:
            raise NoTestFound()

        print(self.rel_path, end=" ")

        errors: list[Error] = []

        for expected in expected_outcomes:
            has_match = False
            for actual in self._actual_outcomes():
                if expected.linenumber != actual.linenumber:
                    continue
                has_match = True
                if expected == actual:
                    print(Color.OK.value + "." + Color.RESET.value, end="")
                    break

                print(Color.ALERT.value + "F" + Color.RESET.value, end="")
                errors.append(
                    Error(
                        self.rel_path,
                        expected,
                        actual,
                    )
                )

            else:
                if not has_match:
                    errors.append(Error(self.rel_path, expected, None))
        print("", end="\r")
        return errors
