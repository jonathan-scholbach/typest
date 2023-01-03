from typing_extensions import reveal_type

# fmt: off

def func(a: int, b: int) -> int | float:
    return a + b


c = func(12, 7)
reveal_type(c)  # expect-type: int | float
reveal_type(c)  # expect-type: builtins.int | float

d: str = func(12, 7)  # expect-error
e: str = func(12, 7)  # expect-error: Incompatible types in assignment (expression has type "Union[int, float]", variable has type "str")  [assignment]
