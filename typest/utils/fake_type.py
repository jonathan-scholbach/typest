from os import truncate
import re
from typing import Optional


class FakeBuiltin:
    types: list[str] = [
        "bool",
        "bytes",
        "bytearray",
        "complex",
        "contextmanager",
        "dict",
        "float",
        "frozenset",
        "function",
        "GenericAlias",
        "int",
        "list",
        "module",
        "range",
        "set",
        "str",
        "tuple",
        "memoryview",
        "None",
        "NoneType",
    ]

    def __init__(self, typ: Optional["FakeType"]) -> None:
        self._type = typ

    def __eq__(self, other: "FakeType") -> bool:
        if not isinstance(other, FakeBuiltin):
            return False

        if self._type in ["None", "NoneType"]:
            return other._type in ["None", "NoneType"]
        return self._type == other._type

    def __hash__(self) -> int:
        return hash(self._type)

    def __repr__(self) -> str:
        return f"builtins.{self._type}"


class FakeOptional:
    def __init__(self, typ: Optional["FakeType"]) -> None:
        self._type = typ

    def __eq__(self, other: "FakeType") -> bool:
        if isinstance(other, FakeUnion):
            return other.__eq__(self)

        if not isinstance(other, FakeOptional):
            return False
        return self._type == other._type

    def __hash__(self) -> int:
        return hash(self._type)

    def __repr__(self) -> str:
        return f"Optional[{self._type}]"


class FakeUnion:
    def __init__(self, *types: "FakeType") -> None:
        self._types = tuple(
            parse(t) if isinstance(t, str) else t for t in types
        )

    def __eq__(self, other: "FakeType") -> bool:
        if isinstance(other, FakeOptional):
            return self == FakeUnion(other._type, FakeBuiltin("None"))
        if not isinstance(other, FakeUnion):
            return False
        return set(self._types) == set(other._types)

    def __hash__(self) -> int:
        return hash(*self._types)

    def __repr__(self) -> str:
        inner = ", ".join([str(x) for x in self._types])
        return f"Union[{inner}]"


FakeType = FakeBuiltin | FakeOptional | FakeUnion | str


def parse(text: str) -> FakeType:
    """Parse a string represenation of a type into a which are easier to
    compare. This does not check the string to be well-formatted."""
    for builtin_type in FakeBuiltin.types:
        if text == builtin_type or text == f"builtins.{builtin_type}":
            return FakeBuiltin(builtin_type)

    optional_pattern = r"Optional\[(.*)\]"
    if match := re.match(optional_pattern, text):
        return FakeOptional(parse(match.group(1)))

    union_pattern = r"Union\[(.*)\]"
    if match := re.match(union_pattern, text):
        return FakeUnion(
            *[
                parse(union_type.strip())
                for union_type in match.group(1).split(",")
            ]
        )

    if "|" in text:
        return FakeUnion(
            *[parse(union_type.strip()) for union_type in text.split("|")]
        )

    return text
