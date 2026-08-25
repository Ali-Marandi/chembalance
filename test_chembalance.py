import unittest

from chembalance import ChemBalanceError, balance, balance_equation, format_formula, parse_formula, parse_species


class FormulaParsingTests(unittest.TestCase):
    def test_simple_formula(self):
        self.assertEqual(parse_formula("C6H12O6"), {"C": 6, "H": 12, "O": 6})

    def test_nested_parentheses(self):
        self.assertEqual(
            parse_formula("Ca3(PO4)2"),
            {"Ca": 3, "P": 2, "O": 8},
        )

    def test_square_brackets(self):
        self.assertEqual(
            parse_formula("K4[Fe(CN)6]"),
            {"K": 4, "Fe": 1, "C": 6, "N": 6},
        )

    def test_hydrate_and_unicode_subscripts(self):
        self.assertEqual(
            parse_formula("CuSO₄·5H₂O"),
            {"Cu": 1, "S": 1, "O": 9, "H": 10},
        )

    def test_charge_is_retained_on_species(self):
        species = parse_species("[MnO4^-]")
        self.assertEqual(species.atoms, {"Mn": 1, "O": 4})
        self.assertEqual(species.charge, -1)

    def test_rejects_unknown_elements_and_bad_groups(self):
        with self.assertRaises(ChemBalanceError):
            parse_formula("Xx2")
        with self.assertRaises(ChemBalanceError):
            parse_formula("Ca(OH2")


class BalancingTests(unittest.TestCase):
    def test_water(self):
        self.assertEqual(balance(["H2", "O2"], ["H2O"]), (2, 1, 2))

    def test_iron_oxide(self):
        self.assertEqual(balance(["Fe", "O2"], ["Fe2O3"]), (4, 3, 2))

    def test_nested_formula_reaction(self):
        result = balance_equation("Ca(OH)2 + H3PO4 -> Ca3(PO4)2 + H2O")
        self.assertEqual(result.coefficients, (3, 2, 1, 6))
        self.assertEqual(result.balanced_equation, "3Ca(OH)₂ + 2H₃PO₄ → Ca₃(PO₄)₂ + 6H₂O")

    def test_hydrate_reaction(self):
        result = balance_equation("CuSO4.5H2O -> CuSO4 + H2O")
        self.assertEqual(result.coefficients, (1, 1, 5))
        self.assertEqual(result.balanced_equation, "CuSO₄·5H₂O → CuSO₄ + 5H₂O")

    def test_charged_redox_equation(self):
        result = balance_equation("[Fe^2+] + [MnO4^-] + [H^+] -> [Fe^3+] + [Mn^2+] + H2O")
        self.assertEqual(result.coefficients, (5, 1, 8, 5, 1, 4))
        self.assertTrue(all(left == right for _, left, right in result.verification))
        self.assertIn(("Net charge", 17, 17), result.verification)

    def test_accepts_reversible_arrow(self):
        result = balance_equation("N2 + H2 ⇌ NH3")
        self.assertEqual(result.arrow, "⇌")
        self.assertEqual(result.balanced_equation, "N₂ + 3H₂ ⇌ 2NH₃")

    def test_rejects_underdetermined_reaction(self):
        with self.assertRaisesRegex(ChemBalanceError, "more than one independent"):
            balance_equation("H2 + O2 -> H2O + H2O2")

    def test_rejects_missing_arrow(self):
        with self.assertRaisesRegex(ChemBalanceError, "reaction arrow"):
            balance_equation("H2 + O2 + H2O")


class FormattingTests(unittest.TestCase):
    def test_formula_formatting(self):
        self.assertEqual(format_formula("Fe2(SO4)3", 3), "Fe₂(SO₄)₃³⁺")


if __name__ == "__main__":
    unittest.main()
