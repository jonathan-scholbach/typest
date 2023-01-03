# typest

Framework to test your library against type checkers, allowing to create
expected errors and. Its purpose is the same as the one of
[pytest-mypy-plugins](https://pypi.org/project/pytest-mypy-plugins/). While
`pytest-mypy-plugins` requires `.yaml` files for specifying the tests,
`typest` test cases are python files, expectations are formulated in comments:

```Python
from mylibrary import some_function

result = some_function()

reveal_type(result)  # expect-type: int
```

Besides expressing type expectations, you can also specify to expect an error
from the typechecker:

```Python
string: str = "not a number"
number: int = string  # expect-error
```

You can also specify which error you expect:

```Python
string: str = "not a number"
number: int = string  # expect-error: Incompatible types in assignment (expression has type "int", variable has type "str")  [assignment]
```
