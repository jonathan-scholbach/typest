from abc import abstractmethod, ABC, abstractstaticmethod

from subprocess import Popen, PIPE

from comment_parser import comment_parser

from typest.error import Error
from typest.outcomes import Flaw, Outcome, RevealedType
from typest.utils.color import Color
from typest.utils.fake_type import FakeType


class NoTestFound(Exception):
    pass


class TypeChecker(ABC):
    """Base class for running a typechecker and interpreting its output"""

    name: str

    def __init__(self, rel_path, abs_path: str) -> None:
        self.path = abs_path
        self.rel_path = rel_path

    @abstractmethod
    def command(self) -> list[str]:
        """Command invoking the typechecker on a certain file"""
        pass

    @abstractstaticmethod
    def _extract_linenumber(line: str) -> int | None:
        """Extract linenumber from line of typechecker's output"""
        pass

    @abstractstaticmethod
    def _extract_type(line: str) -> FakeType | None:
        """Extract revealed type from line of typechecker's output"""
        pass

    @abstractstaticmethod
    def _extract_error(line: str) -> str | None:
        """Extract error from line of typechecker's output"""
        pass

    def _revealed_type(self, line: str) -> RevealedType | None:
        linenumber = self._extract_linenumber(line)
        if linenumber is None:
            return None
        revealed_type = self._extract_type(line)
        if revealed_type is None:
            return None

        return RevealedType(linenumber, revealed_type)

    def _flaw(self, line: str) -> Flaw | None:
        linenumber = self._extract_linenumber(line)
        if linenumber is None:
            return None

        error = self._extract_error(line)
        if error is None:
            return None

        return Flaw(linenumber, error)

    def _expected_outcomes(self) -> list[Outcome]:
        expected: list[Outcome] = []
        for comment in comment_parser.extract_comments(self.path):
            text = comment.text()
            linenumber = comment.line_number()
            expectation = (
                RevealedType.from_comment(linenumber, text)
                or Flaw.from_comment(linenumber, text)
            )
            if expectation is not None:
                expected.append(expectation)
        return expected

    def _actual_outcomes(self) -> list[Outcome]:
        actual: list[Outcome] = []
        process = Popen(self.command(), stdout=PIPE)
        output, _ = process.communicate()
        for line in output.decode("utf-8").split("\n"):
            flaw = self._flaw(line)
            if flaw is not None:
                actual.append(flaw)
            revealed_type = self._revealed_type(line)
            if revealed_type is not None:
                actual.append(revealed_type)
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
