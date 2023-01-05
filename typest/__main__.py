import argparse
import os
import sys
from typing import Type

from comment_parser import comment_parser

from typest.typecheckers.base import NoTestFound
from typest.typecheckers import TypeChecker
from typest.utils.color import Color


def _run_file(
    typechecker: Type[TypeChecker], execution_path: str, filepath: str
) -> bool:
    rel_path = os.path.relpath(filepath, execution_path)
    try:
        errors = typechecker(rel_path, filepath).run()
    except NoTestFound:
        print(
            Color.WARN.value
            + f"{rel_path} "
            + Color.RESET.value
            + f"no tests found"
        )

        return True
    except comment_parser.UnsupportedError:
        print(
            Color.WARN.value
            + f"{rel_path} "
            + Color.RESET.value
            + f"file format not supported or file empty"
        )
        return True
    if errors:
        print(f"{Color.ALERT.value}{rel_path} {Color.RESET.value}")
        for error in errors:
            print(error)
        return False
    else:
        print(f"{Color.OK.value}{rel_path} {Color.RESET.value}")
        return True


def _run_dir(
    typecheckers: list[Type[TypeChecker]],
    execution_path: str,
    dir_path: str,
) -> bool:
    flawless = True

    test_directory = os.path.join(execution_path, dir_path)
    for typechecker in typecheckers:
        print(f"Running tests against {typechecker.name} typechecker")
        for dirpath, _, names in os.walk(test_directory):
            for name in names:
                if name.endswith(".py"):
                    filepath = os.path.join(dirpath, name)
                    if not _run_file(typechecker, execution_path, filepath):
                        flawless = False
        print("\n")
    return flawless


parser = argparse.ArgumentParser(
    prog="typest",
    description="A type testing framework",
)

parser.add_argument(
    "path",
    default=None,
)

parser.add_argument(
    "typechecker",
    action="store",
    default=None,
)

if __name__ == "__main__":
    typecheckers = TypeChecker.__subclasses__()
    execution_path = sys.path[0]
    args = parser.parse_args()
    if args.typechecker is not None:
        names = args.typechecker.split(",")
        typecheckers = [
            typechecker
            for typechecker in typecheckers
            if typechecker.name in names
        ]

    target_path = args.path or execution_path
    flawless = True
    if os.path.isfile(target_path):
        if not target_path.endswith(".py"):
            print("file path must be a python file")
        else:
            flawless = _run_file(typecheckers, execution_path, target_path)
    else:
        flawless = _run_dir(typecheckers, execution_path, target_path)

    if not flawless:
        sys.exit(1)
