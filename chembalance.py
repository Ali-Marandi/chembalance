"""Balance simple chemical equations using exact rational arithmetic."""

from fractions import Fraction
from functools import reduce
from math import gcd
import re


def parse_formula(formula: str) -> dict[str, int]:
    tokens = re.findall(r"([A-Z][a-z]?)(\d*)", formula)
    if not tokens or "".join(e + n for e, n in tokens) != formula:
        raise ValueError("supports element symbols with integer subscripts only")
    return {element: count + int(number or 1) for element, number in tokens for count in [0]}


def _lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b)


def balance(reactants: list[str], products: list[str]) -> tuple[int, ...]:
    compounds = reactants + products
    parsed = [parse_formula(item) for item in compounds]
    elements = sorted({element for item in parsed for element in item})
    matrix = [
        [Fraction(item.get(element, 0) * (1 if i < len(reactants) else -1))
         for i, item in enumerate(parsed)]
        for element in elements
    ]
    variables = len(compounds)
    a = [row[:-1] + [-row[-1]] for row in matrix]
    pivot_row = 0
    pivots = []
    for column in range(variables - 1):
        found = next((r for r in range(pivot_row, len(a)) if a[r][column]), None)
        if found is None:
            continue
        a[pivot_row], a[found] = a[found], a[pivot_row]
        scale = a[pivot_row][column]
        a[pivot_row] = [value / scale for value in a[pivot_row]]
        for row in range(len(a)):
            if row != pivot_row and a[row][column]:
                factor = a[row][column]
                a[row] = [x - factor * y for x, y in zip(a[row], a[pivot_row])]
        pivots.append(column)
        pivot_row += 1
    solution = [Fraction(0) for _ in range(variables - 1)] + [Fraction(1)]
    for row, column in reversed(list(enumerate(pivots))):
        solution[column] = a[row][-1]
    denominator = reduce(_lcm, (value.denominator for value in solution), 1)
    integers = [int(value * denominator) for value in solution]
    common = reduce(gcd, (abs(value) for value in integers if value))
    integers = [value // common for value in integers]
    if any(value <= 0 for value in integers):
        raise ValueError("equation does not have a unique positive balance")
    return tuple(integers)
