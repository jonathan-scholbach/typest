from typing_extensions import reveal_type
from typing import Union

# fmt: off

def func(a: int, b: int) -> Union[int, str]:
    return a + b


c = func(12, 7)
reveal_type(c)  # expect-type: int | str

reveal_type(c)  # expect-type: builtins.int | str

d: str = func(12, 7)  # expect-error
e: str = func(12, 7)  # expect-error: Incompatible types in assignment (expression has type "Union[int, str]", variable has type "str")
