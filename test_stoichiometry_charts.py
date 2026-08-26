import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from examples.stoichiometry_charts import (
    convert_mass_between_species,
    elemental_composition,
    plot_elemental_composition,
    plot_reaction_mole_ratios,
    plot_stoichiometric_mass_flow,
    verify_composition,
)
from chembalance import balance_equation


class ElementalCompositionTests(unittest.TestCase):
    def test_water_composition_totals_one_hundred_percent(self):
        rows = elemental_composition("H2O")
        values = {row.element: row.mass_percent for row in rows}
        self.assertTrue(verify_composition(rows))
        self.assertEqual(values["H"], Decimal("11.191"))
        self.assertEqual(values["O"], Decimal("88.809"))

    def test_hydrate_composition_totals_one_hundred_percent(self):
        rows = elemental_composition("CuSO4·5H2O")
        self.assertTrue(verify_composition(rows))
        self.assertEqual(sum(row.atom_count for row in rows), 21)


class StoichiometryConversionTests(unittest.TestCase):
    def test_mass_to_mass_conversion_uses_balanced_ratio(self):
        conversion = convert_mass_between_species(
            "H2 + O2 -> H2O",
            source_formula="H2",
            source_mass_g="4.032",
            target_formula="H2O",
        )
        self.assertEqual(conversion.source_coefficient, 2)
        self.assertEqual(conversion.target_coefficient, 2)
        self.assertEqual(conversion.source_moles, Decimal("2"))
        self.assertEqual(conversion.target_moles, Decimal("2"))
        self.assertEqual(conversion.target_mass_g, Decimal("36.030"))

    def test_chart_functions_write_nonempty_png_files(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            composition_path = plot_elemental_composition("H2O", folder / "composition.png")
            conversion = convert_mass_between_species("H2 + O2 -> H2O", "H2", "4.032", "H2O")
            flow_path = plot_stoichiometric_mass_flow(conversion, folder / "flow.png")
            ratio_path = plot_reaction_mole_ratios(balance_equation("N2 + H2 -> NH3"), folder / "ratio.png")
            for path in (composition_path, flow_path, ratio_path):
                self.assertTrue(path.exists())
                self.assertGreater(path.stat().st_size, 1_000)


if __name__ == "__main__":
    unittest.main()
