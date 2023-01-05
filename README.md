# typest

[![pypi](https://img.shields.io/pypi/v/typest.svg)](https://pypi.python.org/pypi/typest)
[![versions](https://img.shields.io/pypi/pyversions/typest.svg)](https://github.com/jonathan-scholbach/typest)

An experimental framework to test your library against type checkers, allowing
to formulate type expectations and expected typechecker errors. Its purpose is
the same as the one of
[pytest-mypy-plugins](https://pypi.org/project/pytest-mypy-plugins/). While
`pytest-mypy-plugins` requires `.yaml` files for specifying the tests, `typest`
test cases are python files, expectations are formulated in comments:


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


You can also specify to expect a mismatch error, i.e. an error where an assigned
type is mismatching the actual type:

```Python
string: str = "not a number"
number: int = string  # expect-mismatch: int <> str
```

## Suppported Typecheckers

+ `mypy`
+ `pyright`


## Installation

`typest` is available at pypi. You can install it through pip:

    pip install typest


## Use

    python -m typest [PATH] [TYPECHECKERS]

If PATH is a directory, all python files under that directory (including
subdirectories) are going to be checked. If PATH points to a file, it has to be
a python file.


TYPECHECKERS is an optional argument, a comma separated list of names of
typecheckers you want to run your tests against. Currently, `mypy` and `pyright`
are suppported.


## Development

You can add more typecheckers by subclassing
`typest.typecheckers.base.TypeChecker` and importing your new class in
`typest/typecheckers/__init__.py`.
