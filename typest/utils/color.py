from enum import Enum


class Color(Enum):
    ALERT = "\033[91m"
    OK = "\033[92m"
    RESET = "\033[0m"
