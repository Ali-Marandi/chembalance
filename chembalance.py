"""Exact, dependency-free balancing of chemical equations.

ChemBalance turns the conservation constraints for atoms and electrical charge into a
rational matrix and solves its one-dimensional null space.  Floating-point arithmetic
is never used, so coefficients are reproducible and exact.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from math import gcd
import re
from typing import Iterable


class ChemBalanceError(ValueError):
    """Raised when an equation cannot be parsed or uniquely balanced."""


_SUBSCRIPT_TRANSLATION = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
_SUPERSCRIPT_TRANSLATION = str.maketrans({
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
    "⁺": "+", "⁻": "-",
})
_UNICODE_SUBSCRIPTS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
_UNICODE_SUPERSCRIPTS = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")

# Standard atomic weights (g/mol).  Values are appropriate for educational
# stoichiometry; bracketed conventional values are represented by the usual
# standard atomic-weight approximation.
ATOMIC_WEIGHTS: dict[str, float] = {
    "H": 1.008, "He": 4.0026, "Li": 6.94, "Be": 9.0122, "B": 10.81,
    "C": 12.011, "N": 14.007, "O": 15.999, "F": 18.998, "Ne": 20.180,
    "Na": 22.990, "Mg": 24.305, "Al": 26.982, "Si": 28.085, "P": 30.974,
    "S": 32.06, "Cl": 35.45, "Ar": 39.948, "K": 39.098, "Ca": 40.078,
    "Sc": 44.956, "Ti": 47.867, "V": 50.942, "Cr": 51.996, "Mn": 54.938,
    "Fe": 55.845, "Co": 58.933, "Ni": 58.693, "Cu": 63.546, "Zn": 65.38,
    "Ga": 69.723, "Ge": 72.630, "As": 74.922, "Se": 78.971, "Br": 79.904,
    "Kr": 83.798, "Rb": 85.468, "Sr": 87.62, "Y": 88.906, "Zr": 91.224,
    "Nb": 92.906, "Mo": 95.95, "Tc": 98.0, "Ru": 101.07, "Rh": 102.91,
    "Pd": 106.42, "Ag": 107.87, "Cd": 112.41, "In": 114.82, "Sn": 118.71,
    "Sb": 121.76, "Te": 127.60, "I": 126.90, "Xe": 131.29, "Cs": 132.91,
    "Ba": 137.33, "La": 138.91, "Ce": 140.12, "Pr": 140.91, "Nd": 144.24,
    "Pm": 145.0, "Sm": 150.36, "Eu": 151.96, "Gd": 157.25, "Tb": 158.93,
    "Dy": 162.50, "Ho": 164.93, "Er": 167.26, "Tm": 168.93, "Yb": 173.05,
    "Lu": 174.97, "Hf": 178.49, "Ta": 180.95, "W": 183.84, "Re": 186.21,
    "Os": 190.23, "Ir": 192.22, "Pt": 195.08, "Au": 196.97, "Hg": 200.59,
    "Tl": 204.38, "Pb": 207.2, "Bi": 208.98, "Po": 209.0, "At": 210.0,
    "Rn": 222.0, "Fr": 223.0, "Ra": 226.0, "Ac": 227.0, "Th": 232.04,
    "Pa": 231.04, "U": 238.03, "Np": 237.0, "Pu": 244.0, "Am": 243.0,
    "Cm": 247.0, "Bk": 247.0, "Cf": 251.0, "Es": 252.0, "Fm": 257.0,
    "Md": 258.0, "No": 259.0, "Lr": 266.0, "Rf": 267.0, "Db": 268.0,
    "Sg": 269.0, "Bh": 270.0, "Hs": 277.0, "Mt": 278.0, "Ds": 281.0,
    "Rg": 282.0, "Cn": 285.0, "Nh": 286.0, "Fl": 289.0, "Mc": 290.0,
    "Lv": 293.0, "Ts": 294.0, "Og": 294.0,
}


@dataclass(frozen=True)
class Species:
    """A parsed chemical species, including its elemental formula and net charge."""

    source: str
    formula: str
    atoms: dict[str, int]
    charge: int = 0

    @property
    def molar_mass(self) -> float:
        """Return the formula mass in grams per mole."""
        return sum(ATOMIC_WEIGHTS[element] * count for element, count in self.atoms.items())

    @property
    def display_formula(self) -> str:
        """Return a chemistry-friendly Unicode rendering of the species formula."""
        return format_formula(self.formula, self.charge)


@dataclass(frozen=True)
class BalanceResult:
    """The exact balancing result, ready for a UI or another caller to consume."""

    original_equation: str
    arrow: str
    reactants: tuple[Species, ...]
    products: tuple[Species, ...]
    coefficients: tuple[int, ...]

    @property
    def all_species(self) -> tuple[Species, ...]:
        return self.reactants + self.products

    @property
    def reactant_coefficients(self) -> tuple[int, ...]:
        return self.coefficients[: len(self.reactants)]

    @property
    def product_coefficients(self) -> tuple[int, ...]:
        return self.coefficients[len(self.reactants):]

    @property
    def balanced_equation(self) -> str:
        left = _format_side(self.reactants, self.reactant_coefficients)
        right = _format_side(self.products, self.product_coefficients)
        return f"{left} {self.arrow} {right}"

    @property
    def verification(self) -> tuple[tuple[str, int, int], ...]:
        """Return totals for every conserved element and charge, in display order."""
        entries: list[tuple[str, int, int]] = []
        elements = sorted({element for item in self.all_species for element in item.atoms})
        for element in elements:
            left = sum(coefficient * item.atoms.get(element, 0)
                       for coefficient, item in zip(self.reactant_coefficients, self.reactants))
            right = sum(coefficient * item.atoms.get(element, 0)
                        for coefficient, item in zip(self.product_coefficients, self.products))
            entries.append((element, left, right))
        if any(item.charge for item in self.all_species):
            left_charge = sum(coefficient * item.charge
                              for coefficient, item in zip(self.reactant_coefficients, self.reactants))
            right_charge = sum(coefficient * item.charge
                               for coefficient, item in zip(self.product_coefficients, self.products))
            entries.append(("Net charge", left_charge, right_charge))
        return tuple(entries)

    @property
    def explanation(self) -> str:
        """Give a concise description of how the exact result was obtained."""
        element_count = len({element for item in self.all_species for element in item.atoms})
        charge_clause = " and net charge" if any(item.charge for item in self.all_species) else ""
        return (
            f"ChemBalance solved {element_count} atom-conservation constraint"
            f"{'s' if element_count != 1 else ''}{charge_clause} using exact rational arithmetic, "
            "then reduced the result to the smallest positive whole-number ratio."
        )


def _normalize_text(text: str) -> str:
    normalized = text.translate(_SUBSCRIPT_TRANSLATION).translate(_SUPERSCRIPT_TRANSLATION)
    return normalized.replace("−", "-").replace("·", ".").replace("→", "->").strip()


def _merge_counts(destination: dict[str, int], source: dict[str, int], multiplier: int = 1) -> None:
    for element, count in source.items():
        destination[element] = destination.get(element, 0) + count * multiplier


def _read_number(text: str, index: int) -> tuple[int, int]:
    start = index
    while index < len(text) and text[index].isdigit():
        index += 1
    return (int(text[start:index]) if index > start else 1), index


def _parse_grouped_formula(text: str, index: int = 0, terminator: str | None = None) -> tuple[dict[str, int], int]:
    counts: dict[str, int] = {}
    pairs = {"(": ")", "[": "]"}

    while index < len(text):
        char = text[index]
        if terminator and char == terminator:
            return counts, index + 1
        if char in ")]":
            raise ChemBalanceError(f"unexpected '{char}' in formula '{text}'")
        if char in pairs:
            nested, index = _parse_grouped_formula(text, index + 1, pairs[char])
            multiplier, index = _read_number(text, index)
            _merge_counts(counts, nested, multiplier)
            continue
        if not char.isupper():
            raise ChemBalanceError(
                f"expected an element symbol or group near '{text[index:]}' in formula '{text}'"
            )
        element = char
        index += 1
        if index < len(text) and text[index].islower():
            element += text[index]
            index += 1
        if element not in ATOMIC_WEIGHTS:
            raise ChemBalanceError(f"unknown element '{element}' in formula '{text}'")
        multiplier, index = _read_number(text, index)
        counts[element] = counts.get(element, 0) + multiplier

    if terminator:
        raise ChemBalanceError(f"missing closing '{terminator}' in formula '{text}'")
    return counts, index


def _parse_formula_core(formula: str) -> dict[str, int]:
    if not formula:
        raise ChemBalanceError("a chemical formula cannot be empty")
    total: dict[str, int] = {}
    for segment in formula.split("."):
        if not segment:
            raise ChemBalanceError(f"invalid hydrate notation in formula '{formula}'")
        match = re.fullmatch(r"(\d+)?(.+)", segment)
        if not match:
            raise ChemBalanceError(f"invalid formula segment '{segment}'")
        leading = int(match.group(1) or 1)
        body = match.group(2)
        parsed, consumed = _parse_grouped_formula(body)
        if consumed != len(body):
            raise ChemBalanceError(f"could not parse formula '{formula}'")
        _merge_counts(total, parsed, leading)
    return total


def _extract_charge(text: str) -> tuple[str, int]:
    """Separate a terminal caret charge from a species while retaining grouping brackets."""
    candidate = text
    wrapped = re.fullmatch(r"\[(.*)\]", candidate)
    if wrapped:
        inner = wrapped.group(1)
        charged = re.fullmatch(r"(.+)\^(\d*)([+-])", inner)
        if charged:
            magnitude = int(charged.group(2) or "1")
            return charged.group(1), magnitude if charged.group(3) == "+" else -magnitude
    charged = re.fullmatch(r"(.+)\^(\d*)([+-])", candidate)
    if charged:
        magnitude = int(charged.group(2) or "1")
        return charged.group(1), magnitude if charged.group(3) == "+" else -magnitude
    return candidate, 0


def parse_formula(formula: str) -> dict[str, int]:
    """Parse a neutral or charged formula and return its elemental composition.

    Parentheses, square-bracketed coordination groups, hydrates, and unicode
    subscripts are accepted.  Use :func:`parse_species` when charge information is
    also needed.
    """
    normalized = _normalize_text(formula).replace(" ", "")
    core, _ = _extract_charge(normalized)
    return _parse_formula_core(core)


def parse_species(formula: str) -> Species:
    """Parse one species, retaining a net ionic charge where supplied."""
    normalized = _normalize_text(formula).replace(" ", "")
    if not normalized:
        raise ChemBalanceError("a reaction contains an empty compound")
    core, charge = _extract_charge(normalized)
    return Species(source=formula.strip(), formula=core, atoms=_parse_formula_core(core), charge=charge)


def _split_compounds(side: str) -> list[str]:
    depth = 0
    parts: list[str] = []
    start = 0
    for index, char in enumerate(side):
        if char in "([":
            depth += 1
        elif char in ")]":
            depth -= 1
            if depth < 0:
                raise ChemBalanceError("a reaction contains an unmatched closing bracket")
        elif char == "+" and depth == 0:
            piece = side[start:index].strip()
            if not piece:
                raise ChemBalanceError("a reaction has an empty compound beside '+ '")
            parts.append(piece)
            start = index + 1
    if depth:
        raise ChemBalanceError("a reaction contains an unclosed bracket")
    piece = side[start:].strip()
    if not piece:
        raise ChemBalanceError("a reaction cannot end with '+'")
    parts.append(piece)
    return parts


def _split_equation(equation: str) -> tuple[list[str], list[str], str]:
    normalized = _normalize_text(equation)
    matches = list(re.finditer(r"<->|<=>|⇌|->|=", normalized))
    if len(matches) != 1:
        raise ChemBalanceError("use exactly one reaction arrow: '->', '→', '=', or '⇌'")
    match = matches[0]
    left, right = normalized[:match.start()].strip(), normalized[match.end():].strip()
    if not left or not right:
        raise ChemBalanceError("enter at least one reactant and one product")
    arrow = "⇌" if match.group() in {"<->", "<=>", "⇌"} else "→"
    return _split_compounds(left), _split_compounds(right), arrow


def _lcm(first: int, second: int) -> int:
    return abs(first * second) // gcd(first, second) if first and second else 0


def _rref(matrix: list[list[Fraction]]) -> tuple[list[list[Fraction]], list[int]]:
    """Return reduced row echelon form and its pivot column indices."""
    if not matrix:
        return matrix, []
    result = [row[:] for row in matrix]
    rows, columns = len(result), len(result[0])
    pivot_row = 0
    pivots: list[int] = []
    for column in range(columns):
        found = next((row for row in range(pivot_row, rows) if result[row][column]), None)
        if found is None:
            continue
        result[pivot_row], result[found] = result[found], result[pivot_row]
        pivot = result[pivot_row][column]
        result[pivot_row] = [value / pivot for value in result[pivot_row]]
        for row in range(rows):
            if row != pivot_row and result[row][column]:
                factor = result[row][column]
                result[row] = [value - factor * base for value, base in zip(result[row], result[pivot_row])]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == rows:
            break
    return result, pivots


def _smallest_positive_null_vector(matrix: list[list[Fraction]]) -> tuple[int, ...]:
    columns = len(matrix[0])
    reduced, pivots = _rref(matrix)
    free_columns = [column for column in range(columns) if column not in pivots]
    if len(free_columns) != 1:
        if not free_columns:
            raise ChemBalanceError("the reaction has no non-zero balancing solution")
        raise ChemBalanceError(
            "the reaction has more than one independent balance; add missing species or balance each reaction separately"
        )
    free = free_columns[0]
    solution = [Fraction(0) for _ in range(columns)]
    solution[free] = Fraction(1)
    for row, pivot in enumerate(pivots):
        solution[pivot] = -reduced[row][free]
    denominator = reduce(_lcm, (value.denominator for value in solution), 1)
    integers = [int(value * denominator) for value in solution]
    common = reduce(gcd, (abs(value) for value in integers if value), 0)
    if not common:
        raise ChemBalanceError("the reaction has no usable balancing solution")
    integers = [value // common for value in integers]
    if all(value < 0 for value in integers):
        integers = [-value for value in integers]
    if any(value <= 0 for value in integers):
        raise ChemBalanceError("the reaction does not have a unique positive balance")
    return tuple(integers)


def balance(reactants: list[str], products: list[str]) -> tuple[int, ...]:
    """Return the smallest positive integer coefficients for two lists of formulae."""
    if not reactants or not products:
        raise ChemBalanceError("enter at least one reactant and one product")
    parsed_reactants = [parse_species(item) for item in reactants]
    parsed_products = [parse_species(item) for item in products]
    compounds = parsed_reactants + parsed_products
    elements = sorted({element for item in compounds for element in item.atoms})
    matrix: list[list[Fraction]] = [
        [Fraction(item.atoms.get(element, 0) * (1 if index < len(parsed_reactants) else -1))
         for index, item in enumerate(compounds)]
        for element in elements
    ]
    if any(item.charge for item in compounds):
        matrix.append([
            Fraction(item.charge * (1 if index < len(parsed_reactants) else -1))
            for index, item in enumerate(compounds)
        ])
    return _smallest_positive_null_vector(matrix)


def balance_equation(equation: str) -> BalanceResult:
    """Balance a human-entered equation and return a structured result."""
    reactant_text, product_text, arrow = _split_equation(equation)
    reactants = tuple(parse_species(item) for item in reactant_text)
    products = tuple(parse_species(item) for item in product_text)
    coefficients = balance(reactant_text, product_text)
    return BalanceResult(
        original_equation=equation.strip(),
        arrow=arrow,
        reactants=reactants,
        products=products,
        coefficients=coefficients,
    )


def format_formula(formula: str, charge: int = 0) -> str:
    """Format a formula with Unicode subscripts and an optional superscript charge."""
    normalized = _normalize_text(formula)
    output: list[str] = []
    previous = ""
    for char in normalized:
        if char.isdigit() and (previous.isalpha() or previous in ")]" or previous.isdigit()):
            output.append(char.translate(_UNICODE_SUBSCRIPTS))
        else:
            output.append(char)
        previous = char
    if charge:
        magnitude = "" if abs(charge) == 1 else str(abs(charge))
        output.append((magnitude + ("+" if charge > 0 else "-")).translate(_UNICODE_SUPERSCRIPTS))
    return "".join(output).replace(".", "·")


def _format_side(species: Iterable[Species], coefficients: Iterable[int]) -> str:
    pieces = []
    for coefficient, item in zip(coefficients, species):
        prefix = "" if coefficient == 1 else str(coefficient)
        pieces.append(f"{prefix}{item.display_formula}")
    return " + ".join(pieces)


__all__ = [
    "ATOMIC_WEIGHTS",
    "BalanceResult",
    "ChemBalanceError",
    "Species",
    "balance",
    "balance_equation",
    "format_formula",
    "parse_formula",
    "parse_species",
]
