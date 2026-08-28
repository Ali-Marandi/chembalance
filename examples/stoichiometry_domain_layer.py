"""Backward-compatible import path for the ChemBalance stoichiometry example.

The production domain layer now lives in :mod:`stoichiometry_analysis`; this
module preserves the original example import path for existing users.
"""

from stoichiometry_analysis import *  # noqa: F403
