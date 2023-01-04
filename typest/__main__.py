import argparse
import os
from os.path import relpath
import sys

from comment_parser import comment_parser

from typest.test import NoTestFound, Test
from typest.utils.color import Color


def _run_file(execution_path: str, filepath: str) -> bool:
    rel_path = os.path.relpath(filepath, execution_path)
    try:
        errors = Test(execution_path, filepath).run()
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
        return False
    else:
        print(f"{Color.OK.value}{rel_path} {Color.RESET.value}")
        return True


def _run_dir(execution_path: str, dir_path: str) -> bool:
    flawless = True

    test_directory = os.path.join(execution_path, dir_path)
    for dirpath, _, names in os.walk(test_directory):
        for name in names:
            if name.endswith(".py"):
                filepath = os.path.join(dirpath, name)
                if not _run_file(execution_path, filepath):
                    flawless = False
    return flawless


parser = argparse.ArgumentParser(
    prog="typest",
    description="A type testing framework",
)

parser.add_argument("path",
    nargs="?",
    default=None,
)

if __name__ == "__main__":
    execution_path = sys.path[0]
    args = parser.parse_args()
    target_path = args.path or execution_path
    flawless = True
    if os.path.isfile(target_path):
        if not target_path.endswith(".py"):
            print("file path must be a python file")
        else:
            flawless = _run_file(execution_path, target_path)
    else:
        flawless = _run_dir(execution_path, target_path)

    if not flawless:
        sys.exit(1)
