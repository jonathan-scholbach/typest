from abc import abstractmethod, ABC, abstractstaticmethod
from pathlib import Path

from subprocess import Popen, PIPE

from comment_parser import comment_parser

from typest.error import Error
from typest.outcomes import Flaw, Outcome, RevealedType
from typest.outcomes.mismatch import Mismatch
from typest.utils.color import Color
from typest.utils.fake_type import FakeType


class NoTestFound(Exception):
    pass


class TypeChecker(ABC):
    """Base class for running a typechecker and interpreting its output"""

    name: str

    def __init__(self, path: Path) -> None:
        self.path = path

    @abstractmethod
    def command(self) -> list[str]:
        """Command to invoke the typechecker on a certain file"""
        pass

    @abstractstaticmethod
    def _extract_linenumber(line: str) -> int | None:
        """Extract linenumber from line of typechecker's output"""
        pass

    @abstractstaticmethod
    def _extract_type(line: str, linenumber: int) -> RevealedType | None:
        """Extract revealed type from line of typechecker's output"""
        pass

    @abstractstaticmethod
    def _extract_flaw(line: str, linenumber: int) -> Flaw | None:
        """Extract unspecific error from line of typechecker's output"""
        pass

    @abstractstaticmethod
    def _extract_mismatch(line: str, linenumber: int) -> Mismatch | None:
        """Extract type mismatch error from line of typechecker's output"""
        pass

    def _expected_outcomes(self) -> list[Outcome]:
        expected: list[Outcome] = []
        for comment in comment_parser.extract_comments(self.path):
            text = comment.text()
            linenumber = comment.line_number()
            expectation = RevealedType.from_comment(
                linenumber, text
            ) or Flaw.from_comment(linenumber, text)
            if expectation is not None:
                expected.append(expectation)
        return expected

    def _actual_outcomes(self) -> list[Outcome]:
        actual: list[Outcome] = []
        process = Popen(self.command(), stdout=PIPE)
        output, _ = process.communicate()
        for line in output.decode("utf-8").split("\n"):
            linenumber = self._extract_linenumber(line)
            if linenumber is None:
                continue

            flaw = self._extract_flaw(line, linenumber)
            if flaw is not None:
                actual.append(flaw)

            mismatch = self._extract_mismatch(line, linenumber)
            if mismatch is not None:
                actual.append(mismatch)

            revealed_type = self._extract_type(line, linenumber)
            if revealed_type is not None:
                actual.append(revealed_type)

        return actual

    def run(self) -> list[Error]:
        """Raises NoTestFound if no tests are defined in this testfile"""
        expected_outcomes = self._expected_outcomes()
        if not expected_outcomes:
            raise NoTestFound()

        print(self.path, end=" ")

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
                        self.path,
                        expected,
                        actual,
                    )
                )

            else:
                if not has_match:
                    errors.append(Error(self.path, expected, None))
        print("", end="\r")
        return errors
