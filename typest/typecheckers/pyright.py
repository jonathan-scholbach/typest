import re

from typest.outcomes import Flaw, RevealedType
from typest.typecheckers.base import TypeChecker
from typest.utils.fake_type import parse


class Pyright(TypeChecker):

    name = "pyright"

    def command(self) -> list[str]:
        return ["pyright", self.path]

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
