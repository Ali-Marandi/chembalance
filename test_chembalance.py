import unittest

from chembalance import balance, parse_formula


class BalanceTests(unittest.TestCase):
    def test_water(self):
        self.assertEqual(balance(["H2", "O2"], ["H2O"]), (2, 1, 2))

    def test_iron_oxide(self):
        self.assertEqual(balance(["Fe", "O2"], ["Fe2O3"]), (4, 3, 2))

    def test_formula(self):
        self.assertEqual(parse_formula("C6H12O6"), {"C": 6, "H": 12, "O": 6})


if __name__ == "__main__":
    unittest.main()
