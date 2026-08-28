# Changelog

All notable changes to ChemBalance are documented in this file.

## [1.1.1] — 2026-08-28

ChemBalance 1.1.1 fixes the Linux release environment for the interactive analysis workspace.

| Area | Delivered improvements |
| --- | --- |
| Linux CI | Installs the `libegl1` runtime dependency before the headless PySide6 smoke test, keeping the native Linux release pipeline compatible with the chart workspace. |
| Versioning | Aligns the desktop application version with the corrected cross-platform release workflow. |

## [1.1.0] — 2026-08-28

ChemBalance 1.1 extends the desktop workbench with an interactive, traceable stoichiometry analysis workspace.

| Area | Delivered improvements |
| --- | --- |
| Analysis workspace | A new **Analysis & charts** desktop page for formula validation, elemental mass-composition tables, interactive composition charts, and mass-flow charts. |
| Scientific domain layer | UI-independent `Decimal`-based composition and mass-to-mass services, with explicit units, formula/charge matching, calculation steps, and actionable validation errors. |
| Product quality | Extended headless UI coverage, full regression testing, and packaging support for the Matplotlib Qt/Agg renderers used by the analysis workspace. |
| Distribution | Native release bundles continue to be built on the target platform; this release includes updated executable assets and SHA-256 integrity files. |

> ChemBalance is a mathematical conservation and stoichiometry tool. It does not determine chemical feasibility, product identity, purity, safety, or reaction conditions.

## [1.0.0] — 2026-08-26

ChemBalance 1.0 introduces the first Windows desktop workbench for exact chemical-equation balancing.

| Area | Delivered improvements |
| --- | --- |
| Desktop experience | A polished PySide6 Windows interface with dark appearance, high-DPI-friendly layout, keyboard shortcuts, examples, copy, plain-text export, and local history. |
| Equation engine | Exact fraction-based solving with nested parentheses and brackets, hydrates, Unicode subscripts, ionic charges, charge conservation, and clear actionable errors. |
| Verification | Atom and net-charge validation alongside coefficient and molar-mass tables. |
| Quality | Expanded unit tests, a headless UI smoke test, and continuous testing on Python 3.10 through 3.13. |
| Distribution | A reproducible Windows build workflow that packages the application and emits a SHA-256 checksum for tagged GitHub Releases. |

> ChemBalance is a mathematical conservation tool. It does not determine chemical feasibility, product identity, safety, or reaction conditions.
