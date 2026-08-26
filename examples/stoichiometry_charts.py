"""ChemBalance examples: elemental composition and stoichiometry charts.

This module is deliberately independent from the Qt GUI.  It may be run as a
stand-alone analysis script today, then imported into the future ChemBalance
Stoichiometry Workspace without copying scientific logic into presentation code.

Run from the repository root:

    python examples/stoichiometry_charts.py

The script writes three high-resolution PNG files to ``examples/output``.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")  # Headless-safe renderer for CI, servers, and packaged tests.
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

from chembalance import ATOMIC_WEIGHTS, BalanceResult, ChemBalanceError, Species, balance_equation, parse_species


PALETTE = ("#0C8A66", "#2F3E46", "#D90429", "#467599", "#F2B134", "#7E6EA8", "#6C9A8B")
QUANTIZE = Decimal("0.001")


@dataclass(frozen=True)
class ElementComposition:
    """Mass contribution and mass percentage for one element in a formula."""

    element: str
    atom_count: int
    atomic_weight_g_mol: Decimal
    contribution_g_mol: Decimal
    mass_percent: Decimal


@dataclass(frozen=True)
class StoichiometryConversion:
    """A transparent basis-to-target conversion derived from balanced coefficients."""

    equation: str
    source: Species
    target: Species
    source_coefficient: int
    target_coefficient: int
    source_mass_g: Decimal
    source_moles: Decimal
    target_moles: Decimal
    target_mass_g: Decimal


def decimal_molar_mass(species: Species) -> Decimal:
    """Return the formula mass using decimal arithmetic for display calculations."""
    return sum(
        Decimal(str(ATOMIC_WEIGHTS[element])) * Decimal(count)
        for element, count in species.atoms.items()
    )


def elemental_composition(formula: str, *, decimal_places: int = 3) -> tuple[ElementComposition, ...]:
    """Calculate mass-percent composition for every element in ``formula``.

    The formula parser accepts nested groups, hydrates, Unicode subscripts and
    bracketed ionic charges, matching the ChemBalance engine.  The ionic charge
    does not alter formula mass in this educational-standard-atomic-weight model.
    """
    species = parse_species(formula)
    total_mass = decimal_molar_mass(species)
    if not total_mass:
        raise ChemBalanceError(f"Cannot calculate a molar mass for '{formula}'.")

    rows: list[ElementComposition] = []
    for element, atom_count in sorted(species.atoms.items()):
        atomic_weight = Decimal(str(ATOMIC_WEIGHTS[element]))
        contribution = atomic_weight * Decimal(atom_count)
        percent = (contribution / total_mass * Decimal("100")).quantize(
            Decimal("1." + "0" * decimal_places), rounding=ROUND_HALF_UP
        )
        rows.append(
            ElementComposition(
                element=element,
                atom_count=atom_count,
                atomic_weight_g_mol=atomic_weight.quantize(QUANTIZE, rounding=ROUND_HALF_UP),
                contribution_g_mol=contribution.quantize(QUANTIZE, rounding=ROUND_HALF_UP),
                mass_percent=percent,
            )
        )
    return tuple(rows)


def verify_composition(rows: Iterable[ElementComposition], *, tolerance: Decimal = Decimal("0.01")) -> bool:
    """Confirm that displayed percentages sum to 100% within rounding tolerance."""
    return abs(sum((row.mass_percent for row in rows), Decimal("0")) - Decimal("100")) <= tolerance


def plot_elemental_composition(
    formula: str,
    output_path: str | Path,
    *,
    title: str | None = None,
) -> Path:
    """Create a labeled horizontal bar chart of element mass percentages.

    The precise values are shown in both the plot labels and returned calculation
    model; this avoids using a chart alone as the source of truth.
    """
    rows = elemental_composition(formula)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    elements = [row.element for row in rows]
    percentages = [float(row.mass_percent) for row in rows]
    labels = [
        f"{row.element}  ·  {row.atom_count} atom{'s' if row.atom_count != 1 else ''}  ·  "
        f"{row.contribution_g_mol:.3f} g/mol"
        for row in rows
    ]
    colors = [PALETTE[index % len(PALETTE)] for index in range(len(rows))]

    figure, axis = plt.subplots(figsize=(11, 6.2), dpi=180)
    figure.patch.set_facecolor("#F4F7FB")
    axis.set_facecolor("#FFFFFF")
    bars = axis.barh(range(len(rows)), percentages, color=colors, height=0.62)
    axis.set_yticks(range(len(rows)), labels)
    axis.invert_yaxis()
    axis.set_xlim(0, max(100, max(percentages) * 1.18))
    axis.xaxis.set_major_formatter(PercentFormatter(xmax=100))
    axis.set_xlabel("Mass percentage of total molar mass", color="#2F3E46", labelpad=10)
    axis.set_title(title or f"Elemental mass composition — {parse_species(formula).display_formula}",
                   fontsize=16, fontweight="bold", color="#2F3E46", pad=18)
    axis.grid(axis="x", color="#DCE5E1", linewidth=0.8)
    axis.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        axis.spines[spine].set_visible(False)
    axis.spines["bottom"].set_color("#AAB7B1")
    axis.tick_params(axis="y", length=0, colors="#2F3E46")
    axis.tick_params(axis="x", colors="#59656B")

    for bar, percentage in zip(bars, percentages):
        axis.text(
            bar.get_width() + 1.1,
            bar.get_y() + bar.get_height() / 2,
            f"{percentage:.3f}%",
            va="center",
            ha="left",
            fontsize=10,
            color="#2F3E46",
            fontweight="bold",
        )

    total_mass = decimal_molar_mass(parse_species(formula))
    figure.text(
        0.125,
        0.02,
        f"Formula mass: {total_mass:.3f} g/mol  |  Displayed percentages sum to "
        f"{sum(row.mass_percent for row in rows):.3f}%",
        fontsize=9,
        color="#59656B",
    )
    figure.tight_layout(rect=(0, 0.05, 1, 1))
    figure.savefig(output, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)
    return output


def _species_index(result: BalanceResult, formula: str) -> int:
    """Find one species by uncharged formula text while preserving useful errors."""
    requested = parse_species(formula)
    for index, species in enumerate(result.all_species):
        if species.formula == requested.formula and species.charge == requested.charge:
            return index
    raise ChemBalanceError(
        f"'{formula}' is not present in the balanced equation '{result.balanced_equation}'."
    )


def convert_mass_between_species(
    equation: str,
    source_formula: str,
    source_mass_g: Decimal | float | str,
    target_formula: str,
) -> StoichiometryConversion:
    """Convert a known source mass to a target mass through a balanced equation.

    This supports a direct mass-to-mass stoichiometric estimate.  It does not test
    whether the source is a limiting reactant; use it when the source is the stated
    basis or is known to be limiting.
    """
    result = balance_equation(equation)
    source_index = _species_index(result, source_formula)
    target_index = _species_index(result, target_formula)
    source = result.all_species[source_index]
    target = result.all_species[target_index]
    source_coefficient = result.coefficients[source_index]
    target_coefficient = result.coefficients[target_index]
    source_mass = Decimal(str(source_mass_g))
    if source_mass <= 0:
        raise ChemBalanceError("Source mass must be greater than zero.")

    source_moles = source_mass / decimal_molar_mass(source)
    target_moles = source_moles * Decimal(target_coefficient) / Decimal(source_coefficient)
    target_mass = target_moles * decimal_molar_mass(target)
    return StoichiometryConversion(
        equation=result.balanced_equation,
        source=source,
        target=target,
        source_coefficient=source_coefficient,
        target_coefficient=target_coefficient,
        source_mass_g=source_mass,
        source_moles=source_moles,
        target_moles=target_moles,
        target_mass_g=target_mass,
    )


def plot_stoichiometric_mass_flow(
    conversion: StoichiometryConversion,
    output_path: str | Path,
) -> Path:
    """Create a mass-flow chart for a transparent source-to-target conversion."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    categories = [f"Input\n{conversion.source.display_formula}", f"Calculated target\n{conversion.target.display_formula}"]
    values = [float(conversion.source_mass_g), float(conversion.target_mass_g)]
    colors = ["#2F3E46", "#0C8A66"]

    figure, axis = plt.subplots(figsize=(10.5, 6.2), dpi=180)
    figure.patch.set_facecolor("#F4F7FB")
    axis.set_facecolor("#FFFFFF")
    bars = axis.bar(categories, values, color=colors, width=0.52)
    axis.set_ylabel("Mass (g)", color="#2F3E46")
    axis.set_title("Stoichiometric mass flow", fontsize=16, fontweight="bold", color="#2F3E46", pad=18)
    axis.grid(axis="y", color="#DCE5E1", linewidth=0.8)
    axis.set_axisbelow(True)
    for spine in ("top", "right"):
        axis.spines[spine].set_visible(False)
    axis.spines["left"].set_color("#AAB7B1")
    axis.spines["bottom"].set_color("#AAB7B1")
    axis.tick_params(colors="#2F3E46")

    for bar, value in zip(bars, values):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.025,
            f"{value:.3f} g",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color="#2F3E46",
        )

    equation_summary = (
        f"{conversion.equation}\n"
        f"{conversion.source_coefficient}:{conversion.target_coefficient} mole ratio  |  "
        f"{conversion.source_moles:.4f} mol {conversion.source.display_formula} → "
        f"{conversion.target_moles:.4f} mol {conversion.target.display_formula}"
    )
    figure.text(0.5, 0.01, equation_summary, ha="center", fontsize=9, color="#59656B")
    figure.tight_layout(rect=(0, 0.08, 1, 1))
    figure.savefig(output, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)
    return output


def plot_reaction_mole_ratios(result: BalanceResult, output_path: str | Path) -> Path:
    """Visualize the smallest whole-number molar ratio across an equation."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    labels = [species.display_formula for species in result.all_species]
    coefficients = list(result.coefficients)
    colors = ["#2F3E46" if index < len(result.reactants) else "#0C8A66"
              for index in range(len(result.all_species))]

    figure, axis = plt.subplots(figsize=(12, 6.2), dpi=180)
    figure.patch.set_facecolor("#F4F7FB")
    axis.set_facecolor("#FFFFFF")
    bars = axis.bar(labels, coefficients, color=colors, width=0.62)
    axis.set_ylabel("Moles in smallest whole-number ratio", color="#2F3E46")
    axis.set_title("Balanced reaction mole ratio", fontsize=16, fontweight="bold", color="#2F3E46", pad=18)
    axis.grid(axis="y", color="#DCE5E1", linewidth=0.8)
    axis.set_axisbelow(True)
    for spine in ("top", "right"):
        axis.spines[spine].set_visible(False)
    axis.spines["left"].set_color("#AAB7B1")
    axis.spines["bottom"].set_color("#AAB7B1")
    axis.tick_params(colors="#2F3E46")
    for bar, coefficient in zip(bars, coefficients):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.12,
            str(coefficient),
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color="#2F3E46",
        )
    figure.text(
        0.5,
        0.02,
        f"Reactants (dark) → Products (green)  |  {result.balanced_equation}",
        ha="center",
        fontsize=9,
        color="#59656B",
    )
    figure.tight_layout(rect=(0, 0.05, 1, 1))
    figure.savefig(output, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)
    return output


def main() -> int:
    """Generate three reproducible examples for product and documentation review."""
    output_directory = Path(__file__).parent / "output"
    composition_rows = elemental_composition("CuSO4·5H2O")
    if not verify_composition(composition_rows):
        raise RuntimeError("Displayed composition percentages did not total 100%.")

    composition_chart = plot_elemental_composition(
        "CuSO4·5H2O",
        output_directory / "elemental_composition_cuso4_5h2o.png",
    )
    balanced = balance_equation("N2 + H2 -> NH3")
    ratio_chart = plot_reaction_mole_ratios(
        balanced,
        output_directory / "reaction_mole_ratio_haber.png",
    )
    conversion = convert_mass_between_species(
        "H2 + O2 -> H2O",
        source_formula="H2",
        source_mass_g="4.032",
        target_formula="H2O",
    )
    mass_flow_chart = plot_stoichiometric_mass_flow(
        conversion,
        output_directory / "mass_flow_hydrogen_to_water.png",
    )

    print("Created:")
    for path in (composition_chart, ratio_chart, mass_flow_chart):
        print(f"- {path}")
    print(f"Water target mass: {conversion.target_mass_g:.3f} g")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
