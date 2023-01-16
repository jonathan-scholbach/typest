import re

from typest.outcomes import Flaw, RevealedType
from typest.outcomes.mismatch import Mismatch
from typest.typecheckers.base import TypeChecker
from typest.utils.fake_type import parse


class Pyright(TypeChecker):

    name = "pyright"

    def command(self) -> list[str]:
        return ["pyright", str(self.path)]

    @staticmethod
    def _extract_linenumber(line: str) -> int | None:
        match = re.search(r".*\.py:(\d+):.*", line)
        if match is None:
            return None
        return int(match.group(1))

    @staticmethod
    def _extract_type(line: str, linenumber: int) -> RevealedType | None:
        match = re.search(
            r'.*\.py:\d+:\d+ - information: Type of ".*?" is "(.*)"', line
        )
        if match is None:
            return None
        return RevealedType(linenumber, parse(match.group(1)))

    @staticmethod
    def _extract_flaw(line: str, linenumber: int) -> Flaw | None:
        match = re.search(r".*\.py:\d+:\d+ - error: (.*)", line)
        if match is None:
            return None
        return Flaw(linenumber)

    @staticmethod
    def _extract_mismatch(line: str, linenumber: int) -> Mismatch | None:
        pattern = (
            r".* - error: Expression of type "
            r'"(.*)" cannot be assigned to declared type "(.*)"'
        )
        match = re.search(pattern, line)
        if not match:
            return None
        assigned_type = match.group(2)
        actual_type = match.group(1)

        return Mismatch(linenumber, assigned_type, actual_type)
