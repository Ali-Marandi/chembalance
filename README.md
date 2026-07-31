# ChemBalance

Balance simple chemical equations with exact rational linear algebra—no
floating-point rounding and no third-party packages.

```python
from chembalance import balance

assert balance(["Fe", "O2"], ["Fe2O3"]) == (4, 3, 2)
```

Run `python -m unittest -v`. The compact parser supports element symbols and
integer subscripts; parentheses, ionic charge and hydrate notation are planned.
