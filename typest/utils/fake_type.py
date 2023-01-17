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

        if self._type in ["None", "NoneType", None]:
            return other._type in ["None", "NoneType", None]
        return self._type == other._type

    def __hash__(self) -> int:
        return hash(self._type)

    def __repr__(self) -> str:
        return f"builtins.{self._type}"


class FakeGeneric:
    def __init__(self, name: str, *types: "FakeType") -> None:
        self._name = name
        self._types = tuple(t for t in types)

    def __eq__(self, other: "FakeType") -> bool:
        if not isinstance(other, FakeGeneric):
            return False
        return self._name == other._name and self._types == other._types

    def __repr__(self) -> str:
        return f"{self._name}[{self._types}]"


class FakeUnion:
    def __init__(self, *types: "FakeType") -> None:
        self._types = tuple(
            parse(t) if isinstance(t, str) else t for t in types
        )

    def __eq__(self, other: "FakeType") -> bool:
        if not isinstance(other, FakeUnion):
            return False
        return set(self._types) == set(other._types)

    def __hash__(self) -> int:
        return hash(*self._types)

    def __repr__(self) -> str:
        inner = ", ".join([str(x) for x in self._types])
        return f"Union[{inner}]"


FakeType = FakeBuiltin | FakeUnion | FakeGeneric | str


def parse_arg_list(text: str) -> tuple["FakeType"]:
    split_indices: list[int | None] = [0]
    open_brackets = 0
    for index, char in enumerate(text):
        if char == "[":
            open_brackets += 1
            continue
        if char == "]":
            open_brackets -= 1
            continue
        if char == "," and not open_brackets:
            split_indices.append(index)
    split_indices.append(None)
    parts = [
        text[split_indices[i] : split_indices[i + 1]].strip(",")
        for i in range(len(split_indices) - 1)
    ]

    return tuple(parse(part) for part in parts)


def _parse_inner(text: str) -> FakeType:
    text = text.strip()

    for builtin_type in FakeBuiltin.types:
        if text == builtin_type or text == f"builtins.{builtin_type}":
            return FakeBuiltin(builtin_type)

    if "|" in text:
        return FakeUnion(
            *(parse(union_type.strip()) for union_type in text.split("|"))
        )

    return text


def parse(text: str) -> FakeType:
    """Parse a string representation of a type into a FakeType for ease of
    comparison. This does not check the string to be well-formatted."""
    text = text.strip()
    if not text.count("[") == text.count("]"):
        raise ValueError(f"Unbalanced brackets in `{text}`")

    if not "[" in text:
        return _parse_inner(text)

    if not text[-1] == "]":
        raise ValueError(f"Invalid type representation `{text}`")

    index = text.index("[")
    name = text[:index]
    tail = text[index + 1 : -1]
    match name:
        case "Optional":
            return FakeUnion(FakeBuiltin("None"), parse(tail))
        case "Union":
            return FakeUnion(*parse_arg_list(tail))
        case _:
            return FakeGeneric(name, *parse_arg_list(tail))
