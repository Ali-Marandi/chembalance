"""Capture a deterministic product screenshot for the ChemBalance presentation."""

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication

from app import ChemBalanceWindow


def main() -> int:
    app = QApplication([])
    window = ChemBalanceWindow()
    window.resize(QSize(1440, 900))
    window.equation_input.setPlainText("Ca(OH)2 + H3PO4 -> Ca3(PO4)2 + H2O")
    window.balance_current_equation()
    window.show()
    app.processEvents()
    output = Path("assets/chembalance-workbench.png")
    output.parent.mkdir(exist_ok=True)
    if not window.grab().save(str(output)):
        raise RuntimeError("Could not save ChemBalance product screenshot")
    print(output)
    window.close()
    app.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
