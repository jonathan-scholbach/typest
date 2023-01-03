import os
import sys

from typy.test import Test


def mypy(directory: str):
    for dirpath, _, names in os.walk(test_directory):
        for name in names:
            if name.endswith(".py"):
                path = os.path.join(dirpath, name)
                for error in Test(current_path, path).run():
                    print(error)


if __name__ == "__main__":
    current_path = sys.path[0]
    test_directory = os.path.join(current_path, "../tests")
    mypy(test_directory)
