# wordle-solver-py

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

# dictionary

- https://slc.is/data/wordles.txt

# usage

```python

from wordle_solver.wordle import WordleGame
from wordle_solver.solvers import RandomSolver, DictionarySolver, EntropySolver


w = WordleGame.of("perky")

# random solver
rs = RandomSolver(w, 200)
rs.solve()

# dictionary based solver
ds = DictionarySolver.of(w)
ds.solve()

# entropy-based solver
es = EntropySolver.of(w)
es.solve()

# or by manual
w.check("{your answer}")
```

# references

- [Wordleの最初の一手を考える](https://qiita.com/Ken-ichi_Hironaka/items/dbcf3f4d3c702fb62ec6)
