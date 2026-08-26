"""A UI-independent stoichiometry domain layer for ChemBalance.

This example builds on the exact formula parser and balancing engine in
``chembalance.py``.  It deliberately keeps validation, scientific calculation,
and presentation separate so a PySide6 page, a CLI, or an export pipeline can
consume the same deterministic results.

The module calculates mathematical relationships from a balanced equation. It
never asserts chemical feasibility, reaction conditions, hazards, purity, or
safe operating conditions.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal

from chembalance import ATOMIC_WEIGHTS, BalanceResult, ChemBalanceError, Species, balance_equation, parse_species

MassUnit = Literal["mg", "g", "kg"]

_DISPLAY_QUANTUM = Decimal("0.001")
_MASS_TO_GRAMS: dict[MassUnit, Decimal] = {
    "mg": Decimal("0.001"),
    "g": Decimal("1"),
    "kg": Decimal("1000"),
}


class DomainValidationError(ValueError):
    """Raised when a formula, quantity, unit, or selected species is invalid."""


@dataclass(frozen=True)
class ValidationIssue:
    """One user-presentable validation issue with a stable machine-readable code."""

    code: str
    message: str


@dataclass(frozen=True)
class FormulaValidation:
    """The result of validating and parsing one chemical formula."""

    input_text: str
    valid: bool
    normalized_display: str | None
    species: Species | None
    issues: tuple[ValidationIssue, ...]

    def require_species(self) -> Species:
        """Return the parsed species or raise a domain-specific validation error."""
        if self.species is None:
            message = self.issues[0].message if self.issues else "The chemical formula is invalid."
            raise DomainValidationError(message)
        return self.species


@dataclass(frozen=True)
class ElementContribution:
    """Mass contribution of one element to a chemical formula."""

    element: str
    atom_count: int
    atomic_weight_g_mol: Decimal
    contribution_g_mol: Decimal
    mass_percent: Decimal


@dataclass(frozen=True)
class ElementalCompositionAnalysis:
    """Formula mass and mass-percent analysis for one parsed species."""

    formula: str
    molar_mass_g_mol: Decimal
    contributions: tuple[ElementContribution, ...]
    displayed_percent_total: Decimal


@dataclass(frozen=True)
class Quantity:
    """A positive mass quantity preserving the unit chosen by the user."""

    value: Decimal
    unit: MassUnit

    @property
    def grams(self) -> Decimal:
        """Normalize the quantity to grams for scientific calculations."""
        return self.value * _MASS_TO_GRAMS[self.unit]


@dataclass(frozen=True)
class MassToMassConversion:
    """Transparent mass-to-mass conversion from an exact balanced equation."""

    balanced_equation: str
    source: Species
    target: Species
    source_coefficient: int
    target_coefficient: int
    source_quantity: Quantity
    source_moles: Decimal
    target_moles: Decimal
    target_mass_g: Decimal
    target_quantity: Quantity
    calculation_steps: tuple[str, ...]


def validate_formula(formula: str) -> FormulaValidation:
    """Validate a formula using ChemBalance's single parser of record.

    The validation result is safe for UI usage: invalid user input returns an
    issue rather than leaking a parser exception to a view layer. The parser
    supports nested parentheses, bracketed groups, hydrates, ionic charge and
    Unicode subscripts, exactly as the main balancing engine does.
    """
    if not isinstance(formula, str):
        return FormulaValidation(
            input_text=str(formula),
            valid=False,
            normalized_display=None,
            species=None,
            issues=(ValidationIssue("invalid_type", "Enter a chemical formula as text."),),
        )
    if not formula.strip():
        return FormulaValidation(
            input_text=formula,
            valid=False,
            normalized_display=None,
            species=None,
            issues=(ValidationIssue("empty_formula", "Enter a chemical formula before calculating."),),
        )
    try:
        species = parse_species(formula)
    except ChemBalanceError as error:
        return FormulaValidation(
            input_text=formula,
            valid=False,
            normalized_display=None,
            species=None,
            issues=(ValidationIssue("invalid_formula", str(error)),),
        )
    return FormulaValidation(
        input_text=formula,
        valid=True,
        normalized_display=species.display_formula,
        species=species,
        issues=(),
    )


def _decimal_molar_mass(species: Species) -> Decimal:
    """Calculate formula mass from the engine's atomic-weight source of truth."""
    return sum(
        Decimal(str(ATOMIC_WEIGHTS[element])) * Decimal(atom_count)
        for element, atom_count in species.atoms.items()
    )


def _display(value: Decimal, places: int = 3) -> Decimal:
    """Round only a display value; the calculation path remains higher precision."""
    if places < 0:
        raise DomainValidationError("Display precision cannot be negative.")
    quantum = Decimal("1") if places == 0 else Decimal("1." + "0" * places)
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


def analyze_elemental_composition(formula: str, *, display_places: int = 3) -> ElementalCompositionAnalysis:
    """Return formula mass and elemental mass percentages for one formula.

    ``mass_percent`` values are rounded only for display. Consumers that need to
    verify the total should use ``displayed_percent_total`` with a documented
    rounding tolerance rather than assuming a literal 100.000 in all cases.
    """
    species = validate_formula(formula).require_species()
    molar_mass = _decimal_molar_mass(species)
    if molar_mass <= 0:
        raise DomainValidationError(f"Cannot calculate a positive molar mass for '{formula}'.")

    contributions: list[ElementContribution] = []
    for element, atom_count in sorted(species.atoms.items()):
        atomic_weight = Decimal(str(ATOMIC_WEIGHTS[element]))
        contribution = atomic_weight * Decimal(atom_count)
        percentage = Decimal("100") * contribution / molar_mass
        contributions.append(
            ElementContribution(
                element=element,
                atom_count=atom_count,
                atomic_weight_g_mol=_display(atomic_weight, display_places),
                contribution_g_mol=_display(contribution, display_places),
                mass_percent=_display(percentage, display_places),
            )
        )
    displayed_total = sum((row.mass_percent for row in contributions), Decimal("0"))
    return ElementalCompositionAnalysis(
        formula=species.display_formula,
        molar_mass_g_mol=_display(molar_mass, display_places),
        contributions=tuple(contributions),
        displayed_percent_total=_display(displayed_total, display_places),
    )


def validate_mass_quantity(value: Decimal | str | float | int, unit: str) -> Quantity:
    """Validate a positive mass input and normalize the unit type for services."""
    if unit not in _MASS_TO_GRAMS:
        choices = ", ".join(_MASS_TO_GRAMS)
        raise DomainValidationError(f"Unsupported mass unit '{unit}'. Choose one of: {choices}.")
    try:
        decimal_value = Decimal(str(value))
    except Exception as error:  # Decimal exposes several implementation-specific exception types.
        raise DomainValidationError("Enter a valid numeric mass.") from error
    if not decimal_value.is_finite() or decimal_value <= 0:
        raise DomainValidationError("Mass must be a positive finite number.")
    return Quantity(value=decimal_value, unit=unit)  # type: ignore[arg-type]


def _species_index(result: BalanceResult, formula: str, *, side: Literal["reactant", "product", "either"] = "either") -> int:
    """Resolve one formula to a specific species in a balanced equation.

    Matching includes both formula and charge. The optional side constraint
    prevents a user from accidentally choosing a product as a source reactant.
    """
    requested = validate_formula(formula).require_species()
    for index, species in enumerate(result.all_species):
        is_reactant = index < len(result.reactants)
        side_matches = side == "either" or (side == "reactant" and is_reactant) or (side == "product" and not is_reactant)
        if side_matches and species.formula == requested.formula and species.charge == requested.charge:
            return index
    side_phrase = "the selected side of " if side != "either" else ""
    raise DomainValidationError(
        f"'{requested.display_formula}' is not present on {side_phrase}the balanced equation '{result.balanced_equation}'."
    )


def convert_mass_to_mass(
    equation: str,
    *,
    source_formula: str,
    source_mass: Decimal | str | float | int,
    source_unit: MassUnit,
    target_formula: str,
    target_unit: MassUnit = "g",
) -> MassToMassConversion:
    """Calculate a mass-to-mass stoichiometric conversion from a balanced reaction.

    The caller must supply a stated basis or a reactant known to be limiting.
    This function intentionally does not infer a limiting reagent from a single
    mass input. A future multi-reactant service should perform that separate
    domain calculation.
    """
    source_quantity = validate_mass_quantity(source_mass, source_unit)
    if target_unit not in _MASS_TO_GRAMS:
        raise DomainValidationError(f"Unsupported target mass unit '{target_unit}'.")
    try:
        result = balance_equation(equation)
    except ChemBalanceError as error:
        raise DomainValidationError(f"Cannot balance the supplied equation: {error}") from error

    source_index = _species_index(result, source_formula, side="reactant")
    target_index = _species_index(result, target_formula, side="product")
    source = result.all_species[source_index]
    target = result.all_species[target_index]
    source_coefficient = result.coefficients[source_index]
    target_coefficient = result.coefficients[target_index]

    source_molar_mass = _decimal_molar_mass(source)
    target_molar_mass = _decimal_molar_mass(target)
    source_moles = source_quantity.grams / source_molar_mass
    target_moles = source_moles * Decimal(target_coefficient) / Decimal(source_coefficient)
    target_mass_g = target_moles * target_molar_mass
    target_quantity = Quantity(
        value=target_mass_g / _MASS_TO_GRAMS[target_unit],
        unit=target_unit,
    )
    steps = (
        f"{source_quantity.grams} g {source.display_formula} ÷ {source_molar_mass} g/mol = {source_moles} mol",
        f"{source_moles} mol {source.display_formula} × {target_coefficient}/{source_coefficient} = {target_moles} mol {target.display_formula}",
        f"{target_moles} mol {target.display_formula} × {target_molar_mass} g/mol = {target_mass_g} g",
    )
    return MassToMassConversion(
        balanced_equation=result.balanced_equation,
        source=source,
        target=target,
        source_coefficient=source_coefficient,
        target_coefficient=target_coefficient,
        source_quantity=source_quantity,
        source_moles=source_moles,
        target_moles=target_moles,
        target_mass_g=target_mass_g,
        target_quantity=target_quantity,
        calculation_steps=steps,
    )


__all__ = [
    "DomainValidationError",
    "ElementContribution",
    "ElementalCompositionAnalysis",
    "FormulaValidation",
    "MassToMassConversion",
    "Quantity",
    "ValidationIssue",
    "analyze_elemental_composition",
    "convert_mass_to_mass",
    "validate_formula",
    "validate_mass_quantity",
]
