import argparse
import sys
from typing import Type
from pathlib import Path

from comment_parser import comment_parser

from typest.typecheckers.base import NoTestFound
from typest.typecheckers import TypeChecker
from typest.utils.color import Color


def _run_file(typechecker: Type[TypeChecker], path: Path) -> bool:
    # Use relative paths when possible, only for visualization's sake
    if path.is_relative_to(Path.cwd()):
        path = path.relative_to(Path.cwd())

    try:
        errors = typechecker(path).run()
    except NoTestFound:
        print(
            Color.WARN.value
            + f"{path} "
            + Color.RESET.value
            + f"no tests found"
        )

        return True
    except comment_parser.UnsupportedError:
        print(
            Color.WARN.value
            + f"{path} "
            + Color.RESET.value
            + f"file format not supported or file empty"
        )
        return True
    if errors:
        print(f"{Color.ALERT.value}{path} {Color.RESET.value}")
        for error in errors:
            print(error)
        return False
    else:
        print(f"{Color.OK.value}{path} {Color.RESET.value}")
        return True


def _run_file_typecheckers(
    typecheckers: list[Type[TypeChecker]], path: Path
) -> bool:
    flawless = True
    for typechecker in typecheckers:
        print(f"Running tests against {typechecker.name}")
        if not _run_file(typechecker, path):
            flawless = False
        print("\n")
    return flawless


def _run_dir(typecheckers: list[Type[TypeChecker]], path: Path) -> bool:
    flawless = True

    for file in path.rglob("*.py"):
        if not _run_file_typecheckers(typecheckers, file):
            flawless = False
    return flawless


parser = argparse.ArgumentParser(
    prog="typest",
    description="A type testing framework",
)

parser.add_argument(
    "path",
    nargs="?",
    default=Path.cwd(),
    type=Path,
)

parser.add_argument(
    "typechecker",
    nargs="?",
    action="store",
    default=None,
)

if __name__ == "__main__":
    typecheckers = TypeChecker.__subclasses__()
    args = parser.parse_args()
    if args.typechecker is not None:
        names = args.typechecker.split(",")
        typecheckers = [
            typechecker
            for typechecker in typecheckers
            if typechecker.name in names
        ]

    target_path: Path = args.path
    flawless = True
    if target_path.is_file():
        if target_path.suffix != ".py":
            print("file path must be a python file")
        else:
            flawless = _run_file_typecheckers(typecheckers, target_path)
    else:
        flawless = _run_dir(typecheckers, target_path)

    if not flawless:
        sys.exit(1)
