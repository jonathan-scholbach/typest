from typing_extensions import reveal_type


x: int = 2

reveal_type(x)  # expect-type: int
reveal_type(x)  # expect-type: str
