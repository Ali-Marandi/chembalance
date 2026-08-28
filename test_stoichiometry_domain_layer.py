"""Regression tests for the UI-independent stoichiometry domain-layer example."""

from __future__ import annotations

from decimal import Decimal
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / "examples"
if str(EXAMPLES) not in sys.path:
    sys.path.insert(0, str(EXAMPLES))

from stoichiometry_analysis import (  # noqa: E402
    DomainValidationError,
    analyze_elemental_composition,
    convert_mass_to_mass,
    validate_formula,
    validate_mass_quantity,
)


class FormulaValidationTests(unittest.TestCase):
    def test_nested_formula_is_valid_and_preserves_display(self) -> None:
        result = validate_formula("Ca3(PO4)2")
        self.assertTrue(result.valid)
        self.assertEqual(result.species.atoms, {"Ca": 3, "P": 2, "O": 8})
        self.assertEqual(result.normalized_display, "Ca₃(PO₄)₂")

    def test_hydrate_and_ionic_formula_are_valid(self) -> None:
        hydrate = validate_formula("CuSO4·5H2O")
        ion = validate_formula("[Fe(CN)6]^3-")
        self.assertTrue(hydrate.valid)
        self.assertEqual(hydrate.species.atoms, {"Cu": 1, "S": 1, "O": 9, "H": 10})
        self.assertTrue(ion.valid)
        self.assertEqual(ion.species.charge, -3)

    def test_empty_and_unknown_formula_have_stable_issues(self) -> None:
        empty = validate_formula("  ")
        unknown = validate_formula("Xx2")
        self.assertFalse(empty.valid)
        self.assertEqual(empty.issues[0].code, "empty_formula")
        self.assertFalse(unknown.valid)
        self.assertEqual(unknown.issues[0].code, "invalid_formula")


class CompositionTests(unittest.TestCase):
    def test_water_composition_has_expected_percentages(self) -> None:
        analysis = analyze_elemental_composition("H2O")
        by_element = {row.element: row for row in analysis.contributions}
        self.assertEqual(analysis.molar_mass_g_mol, Decimal("18.015"))
        self.assertEqual(by_element["H"].mass_percent, Decimal("11.191"))
        self.assertEqual(by_element["O"].mass_percent, Decimal("88.809"))
        self.assertEqual(analysis.displayed_percent_total, Decimal("100.000"))

    def test_hydrate_percentages_are_within_display_tolerance(self) -> None:
        analysis = analyze_elemental_composition("CuSO4·5H2O")
        self.assertLessEqual(abs(analysis.displayed_percent_total - Decimal("100")), Decimal("0.01"))
        self.assertEqual([row.element for row in analysis.contributions], ["Cu", "H", "O", "S"])


class StoichiometryConversionTests(unittest.TestCase):
    def test_exact_balance_drives_mass_to_mass_conversion(self) -> None:
        conversion = convert_mass_to_mass(
            "H2 + O2 -> H2O",
            source_formula="H2",
            source_mass="4.032",
            source_unit="g",
            target_formula="H2O",
            target_unit="g",
        )
        self.assertEqual(conversion.balanced_equation, "2H₂ + O₂ → 2H₂O")
        self.assertEqual((conversion.source_coefficient, conversion.target_coefficient), (2, 2))
        self.assertEqual(conversion.source_moles, Decimal("2"))
        self.assertEqual(conversion.target_moles, Decimal("2"))
        self.assertEqual(conversion.target_mass_g, Decimal("36.030"))
        self.assertEqual(conversion.target_quantity.value, Decimal("36.030"))
        self.assertEqual(len(conversion.calculation_steps), 3)

    def test_unit_normalization_is_explicit(self) -> None:
        quantity = validate_mass_quantity("2500", "mg")
        self.assertEqual(quantity.grams, Decimal("2.500"))

    def test_invalid_mass_and_species_side_are_rejected(self) -> None:
        with self.assertRaises(DomainValidationError):
            validate_mass_quantity("0", "g")
        with self.assertRaises(DomainValidationError):
            convert_mass_to_mass(
                "H2 + O2 -> H2O",
                source_formula="H2O",
                source_mass="1",
                source_unit="g",
                target_formula="H2O",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
