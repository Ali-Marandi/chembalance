# Changelog

All notable changes to ChemBalance are documented in this file.

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
