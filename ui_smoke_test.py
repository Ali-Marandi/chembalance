"""Headless smoke test for the ChemBalance desktop window."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app import ChemBalanceWindow


def main() -> int:
    app = QApplication([])
    window = ChemBalanceWindow()
    window.equation_input.setPlainText("Ca(OH)2 + H3PO4 -> Ca3(PO4)2 + H2O")
    window.balance_current_equation()
    assert window.current_result is not None
    assert window.result_equation.text() == "3Ca(OH)₂ + 2H₃PO₄ → Ca₃(PO₄)₂ + 6H₂O"
    assert window.verification_table.rowCount() == 4
    assert window.stoichiometry_table.rowCount() == 4
    assert window.workspace_nav.isChecked()
    window._switch_page(2)
    assert window.pages.currentIndex() == 2
    window.close()
    app.quit()
    print("UI smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
