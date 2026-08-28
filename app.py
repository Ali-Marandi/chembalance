"""ChemBalance Desktop application entry point.

Run with ``python app.py`` during development.  The distribution workflow packages
this module as the Windows executable ``ChemBalance.exe``.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QEvent, Qt, QStandardPaths, Signal
from PySide6.QtGui import QAction, QColor, QFont, QKeySequence, QPalette, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QStatusBar,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from analysis_workspace import AnalysisWorkspace
from chembalance import BalanceResult, ChemBalanceError, balance_equation

APP_NAME = "ChemBalance"
APP_VERSION = "1.1.0"

EXAMPLES = {
    "Water formation": "H2 + O2 -> H2O",
    "Iron oxide": "Fe + O2 -> Fe2O3",
    "Neutralization": "Ca(OH)2 + H3PO4 -> Ca3(PO4)2 + H2O",
    "Hydrate loss": "CuSO4·5H2O -> CuSO4 + H2O",
    "Ionic redox": "[Fe^2+] + [MnO4^-] + [H^+] -> [Fe^3+] + [Mn^2+] + H2O",
    "Haber process": "N2 + H2 ⇌ NH3",
}


@dataclass(frozen=True)
class HistoryEntry:
    """One local balancing result stored without network access."""

    equation: str
    balanced_equation: str
    created_at: str


class HistoryStore:
    """A small, robust local JSON history store for the desktop application."""

    def __init__(self) -> None:
        folder = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
        self.path = folder / "history.json"

    def load(self) -> list[HistoryEntry]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return [HistoryEntry(**item) for item in data if isinstance(item, dict)]
        except (OSError, json.JSONDecodeError, TypeError):
            return []

    def save(self, entries: list[HistoryEntry]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps([asdict(item) for item in entries[:100]], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add(self, entry: HistoryEntry) -> list[HistoryEntry]:
        entries = [item for item in self.load() if item.equation != entry.equation]
        entries.insert(0, entry)
        self.save(entries)
        return entries

    def clear(self) -> None:
        try:
            self.path.unlink(missing_ok=True)
        except OSError:
            pass


class NavButton(QPushButton):
    """Sidebar navigation with a stable checked state."""

    def __init__(self, text: str, icon: QStyle.StandardPixmap, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIcon(self.style().standardIcon(icon))
        self.setIconSize(self.iconSize())
        self.setObjectName("navButton")


class EquationEditor(QTextEdit):
    """Equation input which turns Ctrl+Enter into an explicit balance action."""

    balance_requested = Signal()

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.balance_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class SectionCard(QFrame):
    """A consistent rounded surface for dense scientific information."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sectionCard")
        self.setFrameShape(QFrame.Shape.NoFrame)


class ChemBalanceWindow(QMainWindow):
    """The primary window for balancing and inspecting chemical equations."""

    def __init__(self) -> None:
        super().__init__()
        self.history_store = HistoryStore()
        self.current_result: BalanceResult | None = None
        self.history_entries: list[HistoryEntry] = []
        self.dark_mode = False
        self.nav_buttons: list[NavButton] = []

        self.setWindowTitle(f"{APP_NAME} Desktop")
        self.setMinimumSize(1040, 700)
        self.resize(1300, 820)
        self._build_ui()
        self._create_actions()
        self._apply_theme(False)
        self._refresh_history()
        self._show_welcome_state()

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("appRoot")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_sidebar())
        layout.addWidget(self._build_content(), 1)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready — calculations stay on your device.")

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 22, 18, 18)
        sidebar_layout.setSpacing(8)

        brand = QHBoxLayout()
        mark = QLabel("C")
        mark.setObjectName("brandMark")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setFixedSize(38, 38)
        brand.addWidget(mark)
        brand_text = QVBoxLayout()
        title = QLabel("ChemBalance")
        title.setObjectName("brandTitle")
        subtitle = QLabel("DESKTOP 1.0")
        subtitle.setObjectName("brandSubtitle")
        brand_text.addWidget(title)
        brand_text.addWidget(subtitle)
        brand.addLayout(brand_text)
        brand.addStretch()
        sidebar_layout.addLayout(brand)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setObjectName("divider")
        sidebar_layout.addWidget(divider)
        sidebar_layout.addSpacing(10)

        self.workspace_nav = self._add_nav_button("Balance equation", QStyle.StandardPixmap.SP_ArrowForward, 0)
        self.analysis_nav = self._add_nav_button("Analysis & charts", QStyle.StandardPixmap.SP_FileDialogContentsView, 1)
        self.history_nav = self._add_nav_button("History", QStyle.StandardPixmap.SP_FileDialogDetailedView, 2)
        self.about_nav = self._add_nav_button("About & syntax", QStyle.StandardPixmap.SP_MessageBoxInformation, 3)
        sidebar_layout.addWidget(self.workspace_nav)
        sidebar_layout.addWidget(self.analysis_nav)
        sidebar_layout.addWidget(self.history_nav)
        sidebar_layout.addWidget(self.about_nav)
        self.workspace_nav.setChecked(True)

        sidebar_layout.addStretch(1)
        privacy = QLabel("LOCAL-FIRST\nYour equations and history remain on this computer.")
        privacy.setObjectName("privacyNote")
        privacy.setWordWrap(True)
        sidebar_layout.addWidget(privacy)
        sidebar_layout.addSpacing(8)

        theme_row = QHBoxLayout()
        theme_label = QLabel("Dark appearance")
        theme_label.setObjectName("themeLabel")
        self.theme_toggle = QCheckBox()
        self.theme_toggle.setAccessibleName("Enable dark appearance")
        self.theme_toggle.toggled.connect(self._apply_theme)
        theme_row.addWidget(theme_label)
        theme_row.addStretch()
        theme_row.addWidget(self.theme_toggle)
        sidebar_layout.addLayout(theme_row)
        return sidebar

    def _add_nav_button(self, title: str, icon: QStyle.StandardPixmap, index: int) -> NavButton:
        button = NavButton(title, icon)
        button.clicked.connect(lambda checked, target=index: self._switch_page(target))
        self.nav_buttons.append(button)
        return button

    def _build_content(self) -> QWidget:
        content = QFrame()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 26, 32, 22)
        content_layout.setSpacing(0)

        header = QHBoxLayout()
        page_heading = QVBoxLayout()
        self.page_kicker = QLabel("CHEMICAL EQUATION WORKBENCH")
        self.page_kicker.setObjectName("pageKicker")
        self.page_title = QLabel("Balance with certainty.")
        self.page_title.setObjectName("pageTitle")
        self.page_description = QLabel("Exact coefficients, transparent verification, and no floating-point rounding.")
        self.page_description.setObjectName("pageDescription")
        page_heading.addWidget(self.page_kicker)
        page_heading.addWidget(self.page_title)
        page_heading.addWidget(self.page_description)
        header.addLayout(page_heading)
        header.addStretch()
        help_button = QToolButton()
        help_button.setText("Syntax guide")
        help_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton))
        help_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        help_button.setObjectName("subtleButton")
        help_button.clicked.connect(lambda: self._switch_page(2))
        header.addWidget(help_button, alignment=Qt.AlignmentFlag.AlignTop)
        content_layout.addLayout(header)
        content_layout.addSpacing(20)

        self.pages = QStackedWidget()
        self.pages.setObjectName("pages")
        self.pages.addWidget(self._build_workspace_page())
        self.analysis_workspace = AnalysisWorkspace()
        self.pages.addWidget(self.analysis_workspace)
        self.pages.addWidget(self._build_history_page())
        self.pages.addWidget(self._build_about_page())
        content_layout.addWidget(self.pages, 1)
        return content

    def _build_workspace_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        viewport = QWidget()
        layout = QVBoxLayout(viewport)
        layout.setContentsMargins(0, 0, 2, 0)
        layout.setSpacing(18)

        input_card = SectionCard()
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(22, 20, 22, 20)
        input_layout.setSpacing(12)
        input_top = QHBoxLayout()
        input_heading = QLabel("Enter an equation")
        input_heading.setObjectName("cardHeading")
        input_top.addWidget(input_heading)
        input_top.addStretch()
        syntax_hint = QLabel("Use + and → / -> / = / ⇌")
        syntax_hint.setObjectName("mutedCaption")
        input_top.addWidget(syntax_hint)
        input_layout.addLayout(input_top)

        self.equation_input = EquationEditor()
        self.equation_input.setObjectName("equationInput")
        self.equation_input.setPlaceholderText("Example:  Ca(OH)2 + H3PO4  ->  Ca3(PO4)2 + H2O")
        self.equation_input.setFixedHeight(92)
        self.equation_input.balance_requested.connect(self.balance_current_equation)
        self.equation_input.textChanged.connect(self._on_input_changed)
        input_layout.addWidget(self.equation_input)
        input_footer = QHBoxLayout()
        self.input_status = QLabel("Ready for an equation")
        self.input_status.setObjectName("inputStatus")
        input_footer.addWidget(self.input_status)
        input_footer.addStretch()
        self.balance_button = QPushButton("Balance equation")
        self.balance_button.setObjectName("primaryButton")
        self.balance_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        self.balance_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.balance_button.clicked.connect(self.balance_current_equation)
        input_footer.addWidget(self.balance_button)
        input_layout.addLayout(input_footer)
        layout.addWidget(input_card)

        result_card = SectionCard()
        result_card.setObjectName("resultCard")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(22, 20, 22, 20)
        result_layout.setSpacing(8)
        result_top = QHBoxLayout()
        result_heading = QLabel("Balanced equation")
        result_heading.setObjectName("cardHeading")
        result_top.addWidget(result_heading)
        result_top.addStretch()
        self.copy_button = QPushButton("Copy")
        self.copy_button.setObjectName("secondaryButton")
        self.copy_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.copy_button.clicked.connect(self.copy_balanced_equation)
        self.export_button = QPushButton("Export")
        self.export_button.setObjectName("secondaryButton")
        self.export_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        self.export_button.clicked.connect(self.export_result)
        result_top.addWidget(self.copy_button)
        result_top.addWidget(self.export_button)
        result_layout.addLayout(result_top)
        self.result_equation = QLabel("Your balanced equation will appear here.")
        self.result_equation.setObjectName("resultEquation")
        self.result_equation.setWordWrap(True)
        self.result_equation.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        result_layout.addWidget(self.result_equation)
        self.result_explanation = QLabel("ChemBalance uses rational linear algebra to preserve exact integer coefficients.")
        self.result_explanation.setObjectName("resultExplanation")
        self.result_explanation.setWordWrap(True)
        result_layout.addWidget(self.result_explanation)
        layout.addWidget(result_card)

        details = QGridLayout()
        details.setHorizontalSpacing(18)
        details.setVerticalSpacing(18)
        details.setColumnStretch(0, 1)
        details.setColumnStretch(1, 1)
        details.addWidget(self._build_verification_card(), 0, 0)
        details.addWidget(self._build_stoichiometry_card(), 0, 1)
        layout.addLayout(details)

        examples_card = SectionCard()
        examples_layout = QVBoxLayout(examples_card)
        examples_layout.setContentsMargins(22, 18, 22, 18)
        examples_layout.setSpacing(12)
        example_head = QHBoxLayout()
        example_heading = QLabel("Start from a proven example")
        example_heading.setObjectName("cardHeading")
        example_head.addWidget(example_heading)
        example_head.addStretch()
        example_note = QLabel("Click to load it into the workbench")
        example_note.setObjectName("mutedCaption")
        example_head.addWidget(example_note)
        examples_layout.addLayout(example_head)
        examples_grid = QGridLayout()
        examples_grid.setHorizontalSpacing(10)
        examples_grid.setVerticalSpacing(10)
        for number, (name, equation) in enumerate(EXAMPLES.items()):
            button = QPushButton(name)
            button.setObjectName("exampleButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, value=equation: self.load_example(value))
            examples_grid.addWidget(button, number // 3, number % 3)
        examples_layout.addLayout(examples_grid)
        layout.addWidget(examples_card)

        scope_note = QLabel(
            "Scope notice: A balanced equation satisfies conservation constraints; it does not independently establish chemical feasibility, "
            "reaction conditions, hazards, or product identity."
        )
        scope_note.setObjectName("scopeNote")
        scope_note.setWordWrap(True)
        layout.addWidget(scope_note)
        layout.addStretch()
        scroll.setWidget(viewport)
        return scroll

    def _build_verification_card(self) -> QWidget:
        card = SectionCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)
        heading = QLabel("Conservation check")
        heading.setObjectName("cardHeading")
        subheading = QLabel("Every atom count, and charge where present, must match.")
        subheading.setObjectName("mutedCaption")
        subheading.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(subheading)
        self.verification_table = self._create_table(["Constraint", "Reactants", "Products", "Status"])
        layout.addWidget(self.verification_table)
        return card

    def _build_stoichiometry_card(self) -> QWidget:
        card = SectionCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)
        heading = QLabel("Stoichiometry breakdown")
        heading.setObjectName("cardHeading")
        subheading = QLabel("Formula masses are shown for quick classroom and laboratory reference.")
        subheading.setObjectName("mutedCaption")
        subheading.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(subheading)
        self.stoichiometry_table = self._create_table(["Species", "Side", "Coeff.", "Molar mass"])
        layout.addWidget(self.stoichiometry_table)
        return card

    def _build_history_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 2, 0)
        layout.setSpacing(18)
        card = SectionCard()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 20, 22, 20)
        top = QHBoxLayout()
        heading = QLabel("Recent calculations")
        heading.setObjectName("cardHeading")
        top.addWidget(heading)
        top.addStretch()
        clear_button = QPushButton("Clear history")
        clear_button.setObjectName("dangerButton")
        clear_button.clicked.connect(self.clear_history)
        top.addWidget(clear_button)
        card_layout.addLayout(top)
        description = QLabel("History is stored only on this computer. Double-click a row to reopen the original equation.")
        description.setObjectName("mutedCaption")
        description.setWordWrap(True)
        card_layout.addWidget(description)
        self.history_table = self._create_table(["When", "Original equation", "Balanced equation"])
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.doubleClicked.connect(self.open_history_entry)
        card_layout.addWidget(self.history_table)
        layout.addWidget(card, 1)
        return page

    def _build_about_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 2, 0)
        layout.setSpacing(18)

        hero = SectionCard()
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(24, 22, 24, 22)
        headline = QLabel("Built for exact, explainable balance.")
        headline.setObjectName("aboutHeadline")
        hero_layout.addWidget(headline)
        text = QLabel(
            "ChemBalance converts conservation-of-mass constraints into a rational matrix, solves it with Gaussian elimination, "
            "and reduces the answer to the smallest positive whole-number ratio. It avoids floating-point approximation entirely."
        )
        text.setObjectName("aboutText")
        text.setWordWrap(True)
        hero_layout.addWidget(text)
        layout.addWidget(hero)

        syntax = SectionCard()
        syntax_layout = QVBoxLayout(syntax)
        syntax_layout.setContentsMargins(24, 22, 24, 22)
        title = QLabel("Equation syntax")
        title.setObjectName("cardHeading")
        syntax_layout.addWidget(title)
        grid = QGridLayout()
        syntax_examples = [
            ("Reaction arrows", "H2 + O2 -> H2O", "Use `->`, `→`, `=`, or `⇌` between sides."),
            ("Groups", "Ca(OH)2", "Nested parentheses and square brackets are supported."),
            ("Hydrates", "CuSO4·5H2O", "Use a middle dot `·` or period `.` for hydrate notation."),
            ("Ions", "[MnO4^-]", "Write the charge after a caret inside brackets."),
        ]
        for row, (label, example, help_text) in enumerate(syntax_examples):
            key = QLabel(label)
            key.setObjectName("syntaxKey")
            sample = QLabel(example)
            sample.setObjectName("syntaxSample")
            explanation = QLabel(help_text)
            explanation.setObjectName("syntaxHelp")
            explanation.setWordWrap(True)
            grid.addWidget(key, row, 0)
            grid.addWidget(sample, row, 1)
            grid.addWidget(explanation, row, 2)
        grid.setColumnStretch(2, 1)
        syntax_layout.addLayout(grid)
        layout.addWidget(syntax)

        privacy = SectionCard()
        privacy_layout = QVBoxLayout(privacy)
        privacy_layout.setContentsMargins(24, 22, 24, 22)
        privacy_title = QLabel("Privacy, scope, and version")
        privacy_title.setObjectName("cardHeading")
        privacy_layout.addWidget(privacy_title)
        privacy_text = QLabel(
            f"ChemBalance Desktop {APP_VERSION} is local-first: balancing occurs on this device and no equation is sent to a service. "
            "The application is an educational and productivity aid. Always independently evaluate chemical validity, hazards, and operating conditions."
        )
        privacy_text.setObjectName("aboutText")
        privacy_text.setWordWrap(True)
        privacy_layout.addWidget(privacy_text)
        layout.addWidget(privacy)
        layout.addStretch()
        scroll.setWidget(body)
        return scroll

    @staticmethod
    def _create_table(headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        table.setMinimumHeight(190)
        table.setObjectName("dataTable")
        return table

    def _create_actions(self) -> None:
        balance_action = QAction("Balance equation", self)
        balance_action.setShortcut(QKeySequence("Ctrl+Return"))
        balance_action.triggered.connect(self.balance_current_equation)
        self.addAction(balance_action)
        copy_action = QAction("Copy balanced equation", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy_balanced_equation)
        self.addAction(copy_action)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=lambda: self.equation_input.setFocus())

    def _switch_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        for number, button in enumerate(self.nav_buttons):
            button.setChecked(number == index)
        page_metadata = {
            0: ("CHEMICAL EQUATION WORKBENCH", "Balance with certainty.", "Exact coefficients, transparent verification, and no floating-point rounding."),
            1: ("STOICHIOMETRY WORKSPACE", "Trace every calculation.", "Analyze elemental composition and mass flow from exact balanced equations."),
            2: ("LOCAL WORKSPACE", "Your calculation history.", "Review previous equations without sending them anywhere."),
            3: ("REFERENCE", "Know the notation.", "A concise guide to supported input, exact solving, and responsible use."),
        }
        kicker, title, description = page_metadata[index]
        self.page_kicker.setText(kicker)
        self.page_title.setText(title)
        self.page_description.setText(description)
        if index == 2:
            self._refresh_history()

    def _on_input_changed(self) -> None:
        if self.equation_input.toPlainText().strip():
            self.input_status.setText("Press Ctrl+Enter to balance")
        else:
            self.input_status.setText("Ready for an equation")

    def load_example(self, equation: str) -> None:
        self.equation_input.setPlainText(equation)
        self.equation_input.setFocus()
        self.balance_current_equation()

    def balance_current_equation(self) -> None:
        equation = self.equation_input.toPlainText().strip()
        if not equation:
            self._show_error("Enter a chemical equation before balancing it.")
            self.equation_input.setFocus()
            return
        try:
            result = balance_equation(equation)
        except ChemBalanceError as error:
            self._show_error(str(error))
            self.current_result = None
            self.analysis_workspace.set_balance_result(None)
            self.copy_button.setEnabled(False)
            self.export_button.setEnabled(False)
            return
        except Exception as error:  # Defensive UI boundary; detailed internals should not reach an end user.
            self._show_error(f"ChemBalance could not process this equation: {error}")
            self.current_result = None
            self.analysis_workspace.set_balance_result(None)
            return

        self.current_result = result
        self.analysis_workspace.set_balance_result(result)
        self.result_equation.setText(result.balanced_equation)
        self.result_explanation.setText(result.explanation)
        self.input_status.setText("Balanced successfully — all constraints match.")
        self.input_status.setProperty("state", "success")
        self._repolish(self.input_status)
        self.copy_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self._populate_result_tables(result)
        now = datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()
        self.history_entries = self.history_store.add(HistoryEntry(equation, result.balanced_equation, now))
        self._refresh_history()
        self.statusBar().showMessage("Balanced successfully. Saved locally in history.", 5000)

    def _populate_result_tables(self, result: BalanceResult) -> None:
        self.verification_table.setRowCount(0)
        for row, (constraint, left, right) in enumerate(result.verification):
            self.verification_table.insertRow(row)
            values = [constraint, str(left), str(right), "Verified"]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 3:
                    item.setForeground(QColor("#0c8a66"))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                elif column in (1, 2):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.verification_table.setItem(row, column, item)

        self.stoichiometry_table.setRowCount(0)
        for row, (index, species) in enumerate(enumerate(result.all_species)):
            self.stoichiometry_table.insertRow(row)
            side = "Reactant" if index < len(result.reactants) else "Product"
            coefficient = result.coefficients[index]
            values = [species.display_formula, side, str(coefficient), f"{species.molar_mass:.3f} g/mol"]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 2:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.stoichiometry_table.setItem(row, column, item)
        self.verification_table.resizeRowsToContents()
        self.stoichiometry_table.resizeRowsToContents()

    def copy_balanced_equation(self) -> None:
        if not self.current_result:
            return
        QApplication.clipboard().setText(self.current_result.balanced_equation)
        self.statusBar().showMessage("Balanced equation copied to the clipboard.", 3000)

    def export_result(self) -> None:
        if not self.current_result:
            return
        default_name = "chembalance-equation.txt"
        path, _ = QFileDialog.getSaveFileName(self, "Export balanced equation", default_name, "Text files (*.txt)")
        if not path:
            return
        result = self.current_result
        verification = "\n".join(f"- {name}: {left} = {right}" for name, left, right in result.verification)
        breakdown = "\n".join(
            f"- {coefficient} × {species.display_formula} ({species.molar_mass:.3f} g/mol)"
            for coefficient, species in zip(result.coefficients, result.all_species)
        )
        content = (
            "ChemBalance Desktop\n"
            f"Generated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}\n\n"
            f"Input\n{result.original_equation}\n\n"
            f"Balanced equation\n{result.balanced_equation}\n\n"
            f"Conservation verification\n{verification}\n\n"
            f"Stoichiometry breakdown\n{breakdown}\n\n"
            "Scope notice: Mathematical balance does not independently establish chemical feasibility or safe operating conditions.\n"
        )
        try:
            Path(path).write_text(content, encoding="utf-8")
        except OSError as error:
            QMessageBox.warning(self, "Export failed", f"ChemBalance could not write that file.\n\n{error}")
            return
        self.statusBar().showMessage(f"Exported result to {path}", 5000)

    def _refresh_history(self) -> None:
        self.history_entries = self.history_store.load()
        if not hasattr(self, "history_table"):
            return
        self.history_table.setRowCount(0)
        for row, entry in enumerate(self.history_entries):
            self.history_table.insertRow(row)
            try:
                stamp = datetime.fromisoformat(entry.created_at).astimezone().strftime("%d %b %Y, %H:%M")
            except ValueError:
                stamp = entry.created_at
            values = [stamp, entry.equation, entry.balanced_equation]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip(value)
                self.history_table.setItem(row, column, item)
        self.history_table.resizeRowsToContents()

    def open_history_entry(self, model_index) -> None:  # QModelIndex typed dynamically by Qt.
        row = model_index.row()
        if row < 0 or row >= len(self.history_entries):
            return
        self._switch_page(0)
        self.equation_input.setPlainText(self.history_entries[row].equation)
        self.balance_current_equation()

    def clear_history(self) -> None:
        if not self.history_entries:
            return
        response = QMessageBox.question(
            self,
            "Clear local history?",
            "This removes saved calculations from this computer. This action cannot be undone.",
            QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Clear,
            QMessageBox.StandardButton.Cancel,
        )
        if response == QMessageBox.StandardButton.Clear:
            self.history_store.clear()
            self._refresh_history()
            self.statusBar().showMessage("Local history cleared.", 3000)

    def _show_welcome_state(self) -> None:
        self.copy_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.verification_table.setRowCount(0)
        self.stoichiometry_table.setRowCount(0)
        self.analysis_workspace.set_balance_result(None)
        self.equation_input.setFocus()

    def _show_error(self, message: str) -> None:
        self.input_status.setText(f"Check input: {message}")
        self.input_status.setProperty("state", "error")
        self._repolish(self.input_status)
        self.result_equation.setText("ChemBalance needs a valid equation to produce a result.")
        self.result_explanation.setText(message)
        self.result_equation.setProperty("error", True)
        self._repolish(self.result_equation)
        self.verification_table.setRowCount(0)
        self.stoichiometry_table.setRowCount(0)
        self.statusBar().showMessage("No balance was produced. Review the input guidance.", 5000)

    def _apply_theme(self, dark: bool) -> None:
        self.dark_mode = dark
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(self._stylesheet(dark))
        palette = self.palette()
        if dark:
            palette.setColor(QPalette.ColorRole.Window, QColor("#101625"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#edf2ff"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#161e30"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#edf2ff"))
        else:
            palette.setColor(QPalette.ColorRole.Window, QColor("#f4f7fb"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#17213a"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#17213a"))
        self.setPalette(palette)

    @staticmethod
    def _stylesheet(dark: bool) -> str:
        colors = {
            "root": "#101625" if dark else "#f4f7fb",
            "content": "#101625" if dark else "#f4f7fb",
            "sidebar": "#0b1325" if dark else "#17223b",
            "card": "#161e30" if dark else "#ffffff",
            "result": "#142a33" if dark else "#effaf5",
            "border": "#2a3855" if dark else "#e1e8f2",
            "text": "#edf2ff" if dark else "#17213a",
            "muted": "#9caac5" if dark else "#65728a",
            "input": "#101827" if dark else "#fbfcff",
            "accent": "#1db487" if dark else "#0c8a66",
            "accent_hover": "#2bc89a" if dark else "#087454",
            "accent_soft": "#164c48" if dark else "#d9f3e9",
            "danger": "#f38b93" if dark else "#b42335",
            "button": "#222f49" if dark else "#edf2f8",
            "button_hover": "#2a3b5c" if dark else "#e1e9f4",
            "table_header": "#1c2840" if dark else "#f1f5f9",
        }
        return f"""
            * {{ font-family: 'Segoe UI', 'Inter', sans-serif; }}
            QMainWindow, #appRoot {{ background: {colors['root']}; color: {colors['text']}; }}
            #sidebar {{ background: {colors['sidebar']}; border: 0; }}
            #contentArea {{ background: {colors['content']}; }}
            #brandMark {{ background: {colors['accent']}; color: #ffffff; border-radius: 19px; font-size: 20px; font-weight: 800; }}
            #brandTitle {{ color: #ffffff; font-size: 16px; font-weight: 700; }}
            #brandSubtitle {{ color: #90a4c8; font-size: 9px; font-weight: 700; letter-spacing: 1px; }}
            #divider {{ color: #2c3c5e; background: #2c3c5e; max-height: 1px; border: 0; }}
            #navButton {{ text-align: left; color: #c6d2ea; background: transparent; border: 0; border-radius: 9px; padding: 11px 12px; font-size: 13px; font-weight: 600; }}
            #navButton:hover {{ background: #223250; color: #ffffff; }}
            #navButton:checked {{ background: #2a4660; color: #ffffff; }}
            #privacyNote {{ color: #90a4c8; font-size: 10px; font-weight: 600; line-height: 1.35; }}
            #themeLabel {{ color: #c6d2ea; font-size: 12px; }}
            #pageKicker {{ color: {colors['accent']}; font-size: 10px; font-weight: 800; letter-spacing: 1.2px; }}
            #pageTitle {{ color: {colors['text']}; font-size: 28px; font-weight: 750; margin-top: 2px; }}
            #pageDescription {{ color: {colors['muted']}; font-size: 13px; margin-top: 3px; }}
            #sectionCard {{ background: {colors['card']}; border: 1px solid {colors['border']}; border-radius: 14px; }}
            #resultCard {{ background: {colors['result']}; border-color: {colors['accent_soft']}; }}
            #cardHeading {{ color: {colors['text']}; font-size: 14px; font-weight: 700; }}
            #mutedCaption {{ color: {colors['muted']}; font-size: 11px; }}
            #equationInput {{ background: {colors['input']}; color: {colors['text']}; border: 1px solid {colors['border']}; border-radius: 9px; padding: 11px; font-family: 'Cascadia Mono', 'Consolas', monospace; font-size: 16px; selection-background-color: {colors['accent']}; }}
            #equationInput:focus {{ border: 2px solid {colors['accent']}; padding: 10px; }}
            #analysisInput, #analysisCombo {{ background: {colors['input']}; color: {colors['text']}; border: 1px solid {colors['border']}; border-radius: 8px; padding: 8px 10px; font-size: 12px; }}
            #analysisInput:focus, #analysisCombo:focus {{ border: 2px solid {colors['accent']}; padding: 7px 9px; }}
            #analysisSteps {{ color: {colors['text']}; background: {colors['input']}; border: 1px solid {colors['border']}; border-radius: 9px; padding: 14px; font-family: 'Cascadia Mono', 'Consolas', monospace; font-size: 11px; line-height: 1.45; }}
            #inputStatus {{ color: {colors['muted']}; font-size: 11px; }}
            #inputStatus[state='success'] {{ color: {colors['accent']}; font-weight: 600; }}
            #inputStatus[state='error'] {{ color: {colors['danger']}; font-weight: 600; }}
            #primaryButton {{ background: {colors['accent']}; color: #ffffff; border: 0; border-radius: 8px; padding: 10px 17px; font-size: 12px; font-weight: 700; }}
            #primaryButton:hover {{ background: {colors['accent_hover']}; }}
            #primaryButton:disabled {{ background: #8da49e; color: #eff5f3; }}
            #secondaryButton, #subtleButton {{ background: {colors['button']}; color: {colors['text']}; border: 1px solid {colors['border']}; border-radius: 8px; padding: 8px 12px; font-size: 12px; font-weight: 600; }}
            #secondaryButton:hover, #subtleButton:hover {{ background: {colors['button_hover']}; }}
            #secondaryButton:disabled {{ color: {colors['muted']}; background: {colors['button']}; }}
            #resultEquation {{ color: {colors['accent']}; font-family: 'Cascadia Mono', 'Consolas', monospace; font-size: 24px; font-weight: 750; padding: 8px 0 2px 0; }}
            #resultEquation[error='true'] {{ color: {colors['danger']}; font-size: 16px; }}
            #resultExplanation {{ color: {colors['muted']}; font-size: 12px; line-height: 1.45; }}
            #dataTable {{ background: transparent; color: {colors['text']}; border: 1px solid {colors['border']}; border-radius: 8px; gridline-color: {colors['border']}; font-size: 11px; }}
            #dataTable::item {{ padding: 8px; border-bottom: 1px solid {colors['border']}; }}
            #dataTable QHeaderView::section {{ background: {colors['table_header']}; color: {colors['muted']}; border: 0; border-bottom: 1px solid {colors['border']}; padding: 8px; font-size: 10px; font-weight: 700; }}
            #exampleButton {{ background: {colors['button']}; color: {colors['text']}; border: 1px solid {colors['border']}; border-radius: 8px; padding: 10px 12px; font-size: 12px; font-weight: 600; text-align: left; }}
            #exampleButton:hover {{ border-color: {colors['accent']}; background: {colors['accent_soft']}; }}
            #scopeNote {{ color: {colors['muted']}; font-size: 10px; padding: 0 4px; }}
            #dangerButton {{ color: {colors['danger']}; background: transparent; border: 1px solid {colors['danger']}; border-radius: 8px; padding: 8px 12px; font-size: 12px; font-weight: 600; }}
            #dangerButton:hover {{ background: #612a36; color: #ffffff; }}
            #aboutHeadline {{ color: {colors['text']}; font-size: 23px; font-weight: 750; }}
            #aboutText {{ color: {colors['muted']}; font-size: 13px; line-height: 1.5; }}
            #syntaxKey {{ color: {colors['text']}; font-size: 12px; font-weight: 700; padding: 7px 8px 7px 0; }}
            #syntaxSample {{ color: {colors['accent']}; background: {colors['input']}; border: 1px solid {colors['border']}; border-radius: 5px; padding: 6px 8px; font-family: 'Cascadia Mono', 'Consolas', monospace; font-size: 12px; }}
            #syntaxHelp {{ color: {colors['muted']}; font-size: 12px; padding-left: 8px; }}
            QScrollArea {{ border: 0; background: transparent; }}
            QScrollBar:vertical {{ background: transparent; width: 10px; margin: 4px; }}
            QScrollBar::handle:vertical {{ background: {colors['border']}; border-radius: 4px; min-height: 28px; }}
            QStatusBar {{ background: {colors['card']}; color: {colors['muted']}; border-top: 1px solid {colors['border']}; font-size: 11px; }}
            QCheckBox::indicator {{ width: 30px; height: 16px; border-radius: 8px; background: #40516f; }}
            QCheckBox::indicator:checked {{ background: {colors['accent']}; }}
        """

    @staticmethod
    def _repolish(widget: QWidget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()


def main() -> int:
    """Start the native Qt desktop application."""
    QApplication.setOrganizationName("ChemBalance")
    QApplication.setApplicationName("ChemBalance Desktop")
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("ChemBalance Desktop")
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = ChemBalanceWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
