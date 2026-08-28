"""PySide6 workspace for ChemBalance composition and stoichiometry charts.

The UI owns only user interaction and chart rendering. All formula validation and
scientific calculation remains in :mod:`stoichiometry_analysis`, so the same
results are testable without a GUI and reusable by exports or a future CLI.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Callable

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from chembalance import BalanceResult
from stoichiometry_analysis import (
    DomainValidationError,
    ElementalCompositionAnalysis,
    MassToMassConversion,
    analyze_elemental_composition,
    convert_mass_to_mass,
)


_CHART_BACKGROUND = "#f4f7fb"
_CHART_SURFACE = "#ffffff"
_CHART_TEXT = "#17213a"
_CHART_MUTED = "#65728a"
_CHART_GRID = "#dce5e1"
_COMPOSITION_COLORS = ("#0c8a66", "#2f3e46", "#467599", "#f2b134", "#7e6ea8", "#d90429")


class CompositionChartCanvas(FigureCanvas):
    """Render a composition analysis supplied by the domain layer."""

    def __init__(self, parent: QWidget | None = None) -> None:
        self.figure = Figure(figsize=(6.2, 3.6), dpi=110)
        super().__init__(self.figure)
        self.setParent(parent)
        self.setMinimumHeight(290)
        self.clear_chart("Enter a formula to view elemental mass percentages.")

    def clear_chart(self, message: str) -> None:
        self.figure.clear()
        self.figure.set_facecolor(_CHART_BACKGROUND)
        axis = self.figure.add_subplot(111)
        axis.set_facecolor(_CHART_SURFACE)
        axis.text(0.5, 0.5, message, ha="center", va="center", color=_CHART_MUTED, wrap=True)
        axis.set_axis_off()
        self.figure.tight_layout(pad=1.0)
        self.draw_idle()

    def render(self, analysis: ElementalCompositionAnalysis) -> None:
        self.figure.clear()
        self.figure.set_facecolor(_CHART_BACKGROUND)
        axis = self.figure.add_subplot(111)
        axis.set_facecolor(_CHART_SURFACE)
        rows = analysis.contributions
        labels = [f"{row.element}  ({row.atom_count})" for row in rows]
        values = [float(row.mass_percent) for row in rows]
        colors = [_COMPOSITION_COLORS[index % len(_COMPOSITION_COLORS)] for index in range(len(rows))]
        bars = axis.barh(range(len(rows)), values, color=colors, height=0.62)
        axis.set_yticks(range(len(rows)), labels)
        axis.invert_yaxis()
        axis.set_xlim(0, max(100, max(values) * 1.18))
        axis.xaxis.set_major_formatter(PercentFormatter(xmax=100))
        axis.set_xlabel("Mass percentage", color=_CHART_MUTED, labelpad=8)
        axis.set_title(f"Elemental composition — {analysis.formula}", color=_CHART_TEXT, fontsize=12, fontweight="bold", pad=13)
        axis.grid(axis="x", color=_CHART_GRID, linewidth=0.8)
        axis.set_axisbelow(True)
        for spine in ("top", "right", "left"):
            axis.spines[spine].set_visible(False)
        axis.spines["bottom"].set_color("#aab7b1")
        axis.tick_params(axis="y", length=0, colors=_CHART_TEXT)
        axis.tick_params(axis="x", colors=_CHART_MUTED)
        for bar, value in zip(bars, values):
            axis.text(
                bar.get_width() + 1.0,
                bar.get_y() + bar.get_height() / 2,
                f"{value:.3f}%",
                ha="left",
                va="center",
                fontsize=9,
                color=_CHART_TEXT,
                fontweight="bold",
            )
        self.figure.text(
            0.125,
            0.02,
            f"Formula mass: {analysis.molar_mass_g_mol:.3f} g/mol  |  Displayed total: {analysis.displayed_percent_total:.3f}%",
            fontsize=8.5,
            color=_CHART_MUTED,
        )
        self.figure.tight_layout(rect=(0, 0.06, 1, 1), pad=1.0)
        self.draw_idle()


class MassFlowChartCanvas(FigureCanvas):
    """Render a mass-to-mass conversion supplied by the domain layer."""

    def __init__(self, parent: QWidget | None = None) -> None:
        self.figure = Figure(figsize=(6.2, 3.6), dpi=110)
        super().__init__(self.figure)
        self.setParent(parent)
        self.setMinimumHeight(290)
        self.clear_chart("Balance an equation and choose a source and target species.")

    def clear_chart(self, message: str) -> None:
        self.figure.clear()
        self.figure.set_facecolor(_CHART_BACKGROUND)
        axis = self.figure.add_subplot(111)
        axis.set_facecolor(_CHART_SURFACE)
        axis.text(0.5, 0.5, message, ha="center", va="center", color=_CHART_MUTED, wrap=True)
        axis.set_axis_off()
        self.figure.tight_layout(pad=1.0)
        self.draw_idle()

    def render(self, conversion: MassToMassConversion) -> None:
        self.figure.clear()
        self.figure.set_facecolor(_CHART_BACKGROUND)
        axis = self.figure.add_subplot(111)
        axis.set_facecolor(_CHART_SURFACE)
        labels = [f"Source\n{conversion.source.display_formula}", f"Target\n{conversion.target.display_formula}"]
        values = [float(conversion.source_quantity.grams), float(conversion.target_mass_g)]
        bars = axis.bar(labels, values, color=("#2f3e46", "#0c8a66"), width=0.52)
        axis.set_ylabel("Mass (g)", color=_CHART_MUTED)
        axis.set_title("Stoichiometric mass flow", color=_CHART_TEXT, fontsize=12, fontweight="bold", pad=13)
        axis.grid(axis="y", color=_CHART_GRID, linewidth=0.8)
        axis.set_axisbelow(True)
        for spine in ("top", "right"):
            axis.spines[spine].set_visible(False)
        axis.spines["left"].set_color("#aab7b1")
        axis.spines["bottom"].set_color("#aab7b1")
        axis.tick_params(colors=_CHART_TEXT)
        upper_padding = max(values) * 0.04 if max(values) else 0.1
        axis.set_ylim(0, max(values) + upper_padding * 2.5)
        for bar, value in zip(bars, values):
            axis.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + upper_padding,
                f"{value:.3f} g",
                ha="center",
                va="bottom",
                fontsize=9.5,
                color=_CHART_TEXT,
                fontweight="bold",
            )
        self.figure.text(
            0.5,
            0.02,
            f"{conversion.source_coefficient}:{conversion.target_coefficient} mole ratio  |  {conversion.balanced_equation}",
            ha="center",
            fontsize=8.2,
            color=_CHART_MUTED,
        )
        self.figure.tight_layout(rect=(0, 0.07, 1, 1), pad=1.0)
        self.draw_idle()


class AnalysisWorkspace(QWidget):
    """Composition and stoichiometry desktop workspace bound to a balance result."""

    analysis_state_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._balance_result: BalanceResult | None = None
        self._build_ui()

    @property
    def balance_result(self) -> BalanceResult | None:
        """Expose the current parent-workspace result for smoke tests and integrations."""
        return self._balance_result

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 2, 0)
        layout.setSpacing(18)

        notice = QLabel(
            "Analysis is calculated from a valid formula and a balanced equation. It does not establish chemical feasibility, reaction conditions, or safety."
        )
        notice.setObjectName("scopeNote")
        notice.setWordWrap(True)
        layout.addWidget(notice)

        composition_card = self._card()
        composition_layout = QVBoxLayout(composition_card)
        composition_layout.setContentsMargins(22, 20, 22, 20)
        composition_layout.setSpacing(12)
        composition_layout.addWidget(self._heading("Elemental mass composition", "Validate one formula, inspect each contribution, and view a precise percentage chart."))

        composition_controls = QHBoxLayout()
        self.formula_input = QLineEdit()
        self.formula_input.setObjectName("analysisInput")
        self.formula_input.setPlaceholderText("Formula, e.g. CuSO4·5H2O or Ca3(PO4)2")
        self.formula_input.returnPressed.connect(self.refresh_composition)
        self.composition_button = QPushButton("Analyze formula")
        self.composition_button.setObjectName("primaryButton")
        self.composition_button.clicked.connect(self.refresh_composition)
        composition_controls.addWidget(self.formula_input, 1)
        composition_controls.addWidget(self.composition_button)
        composition_layout.addLayout(composition_controls)

        composition_body = QGridLayout()
        composition_body.setHorizontalSpacing(18)
        composition_body.setColumnStretch(0, 4)
        composition_body.setColumnStretch(1, 5)
        self.composition_table = self._table(["Element", "Atoms", "Contribution", "Mass %"])
        self.composition_table.setMinimumHeight(260)
        self.composition_chart = CompositionChartCanvas()
        composition_body.addWidget(self.composition_table, 0, 0)
        composition_body.addWidget(self.composition_chart, 0, 1)
        composition_layout.addLayout(composition_body)
        layout.addWidget(composition_card)

        conversion_card = self._card()
        conversion_layout = QVBoxLayout(conversion_card)
        conversion_layout.setContentsMargins(22, 20, 22, 20)
        conversion_layout.setSpacing(12)
        conversion_layout.addWidget(self._heading("Stoichiometric mass flow", "Choose reactant and product after balancing an equation; the calculation path remains visible."))

        controls = QGridLayout()
        controls.setHorizontalSpacing(12)
        controls.setVerticalSpacing(7)
        self.source_combo = QComboBox()
        self.source_combo.setObjectName("analysisCombo")
        self.target_combo = QComboBox()
        self.target_combo.setObjectName("analysisCombo")
        self.mass_input = QLineEdit("1")
        self.mass_input.setObjectName("analysisInput")
        self.mass_input.setMaximumWidth(120)
        self.source_unit_combo = QComboBox()
        self.source_unit_combo.addItems(["g", "mg", "kg"])
        self.target_unit_combo = QComboBox()
        self.target_unit_combo.addItems(["g", "mg", "kg"])
        self.convert_button = QPushButton("Calculate mass flow")
        self.convert_button.setObjectName("primaryButton")
        self.convert_button.clicked.connect(self.refresh_conversion)
        self.convert_button.setEnabled(False)

        controls.addWidget(self._control_label("Reactant basis"), 0, 0)
        controls.addWidget(self._control_label("Mass"), 0, 1)
        controls.addWidget(self._control_label("Unit"), 0, 2)
        controls.addWidget(self._control_label("Product target"), 0, 3)
        controls.addWidget(self._control_label("Display unit"), 0, 4)
        controls.addWidget(self.source_combo, 1, 0)
        controls.addWidget(self.mass_input, 1, 1)
        controls.addWidget(self.source_unit_combo, 1, 2)
        controls.addWidget(self.target_combo, 1, 3)
        controls.addWidget(self.target_unit_combo, 1, 4)
        controls.addWidget(self.convert_button, 1, 5)
        controls.setColumnStretch(0, 3)
        controls.setColumnStretch(3, 3)
        conversion_layout.addLayout(controls)

        conversion_body = QGridLayout()
        conversion_body.setHorizontalSpacing(18)
        conversion_body.setColumnStretch(0, 4)
        conversion_body.setColumnStretch(1, 5)
        self.calculation_steps = QLabel("Balance an equation in the main workspace to unlock mass-flow analysis.")
        self.calculation_steps.setObjectName("analysisSteps")
        self.calculation_steps.setWordWrap(True)
        self.calculation_steps.setTextInteractionFlags(Qt.TextSelectableByMouse)
        conversion_body.addWidget(self.calculation_steps, 0, 0, alignment=Qt.AlignTop)
        self.mass_flow_chart = MassFlowChartCanvas()
        conversion_body.addWidget(self.mass_flow_chart, 0, 1)
        conversion_layout.addLayout(conversion_body)
        layout.addWidget(conversion_card)

        self.error_label = QLabel()
        self.error_label.setObjectName("analysisError")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        layout.addStretch(1)

    @staticmethod
    def _card() -> QFrame:
        card = QFrame()
        card.setObjectName("sectionCard")
        card.setFrameShape(QFrame.NoFrame)
        return card

    @staticmethod
    def _heading(title: str, description: str) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        heading = QLabel(title)
        heading.setObjectName("cardHeading")
        description_label = QLabel(description)
        description_label.setObjectName("mutedCaption")
        description_label.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(description_label)
        return container

    @staticmethod
    def _control_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("mutedCaption")
        return label

    @staticmethod
    def _table(headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setFocusPolicy(Qt.NoFocus)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setObjectName("dataTable")
        return table

    def set_balance_result(self, result: BalanceResult | None) -> None:
        """Bind a newly balanced equation and populate valid source/target choices."""
        self._balance_result = result
        self.source_combo.clear()
        self.target_combo.clear()
        if result is None:
            self.convert_button.setEnabled(False)
            self.calculation_steps.setText("Balance an equation in the main workspace to unlock mass-flow analysis.")
            self.mass_flow_chart.clear_chart("Balance an equation and choose a source and target species.")
            return
        for index, species in enumerate(result.reactants):
            self.source_combo.addItem(species.display_formula, species.formula)
        for index, species in enumerate(result.products):
            self.target_combo.addItem(species.display_formula, species.formula)
        self.convert_button.setEnabled(bool(result.reactants and result.products))
        if result.reactants:
            self.formula_input.setText(result.reactants[0].source)
            self.refresh_composition()
        self.refresh_conversion()
        self.analysis_state_changed.emit("balance_result_ready")

    def refresh_composition(self) -> None:
        """Validate a formula, fill the table, and render a chart from the same analysis."""
        try:
            analysis = analyze_elemental_composition(self.formula_input.text())
        except DomainValidationError as error:
            self._show_error(str(error))
            self.composition_table.setRowCount(0)
            self.composition_chart.clear_chart("Enter a valid formula to render its composition.")
            return
        self._clear_error()
        self.composition_table.setRowCount(0)
        for row_number, row in enumerate(analysis.contributions):
            self.composition_table.insertRow(row_number)
            values = [
                row.element,
                str(row.atom_count),
                f"{row.contribution_g_mol:.3f} g/mol",
                f"{row.mass_percent:.3f}%",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in (1, 2, 3):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.composition_table.setItem(row_number, column, item)
        self.composition_table.resizeRowsToContents()
        self.composition_chart.render(analysis)
        self.analysis_state_changed.emit("composition_ready")

    def refresh_conversion(self) -> None:
        """Calculate a source-to-target flow from the current exact balance result."""
        if self._balance_result is None:
            return
        try:
            conversion = convert_mass_to_mass(
                self._balance_result.original_equation,
                source_formula=str(self.source_combo.currentData()),
                source_mass=self.mass_input.text(),
                source_unit=self.source_unit_combo.currentText(),
                target_formula=str(self.target_combo.currentData()),
                target_unit=self.target_unit_combo.currentText(),
            )
        except DomainValidationError as error:
            self._show_error(str(error))
            self.calculation_steps.setText("Correct the selected species or mass to calculate a valid flow.")
            self.mass_flow_chart.clear_chart("A valid source mass and balanced equation are required.")
            return
        self._clear_error()
        target_value = conversion.target_quantity.value
        step_lines = "<br>".join(
            f"<b>{index}.</b> {step}" for index, step in enumerate(conversion.calculation_steps, start=1)
        )
        self.calculation_steps.setText(
            f"<b>{conversion.balanced_equation}</b><br><br>{step_lines}<br><br>"
            f"<b>Result:</b> {target_value:.3f} {conversion.target_quantity.unit} {conversion.target.display_formula}"
        )
        self.mass_flow_chart.render(conversion)
        self.analysis_state_changed.emit("mass_flow_ready")

    def _show_error(self, message: str) -> None:
        self.error_label.setText(f"Analysis check: {message}")
        self.error_label.setVisible(True)
        self.error_label.setStyleSheet(f"color: #b42335; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; padding: 9px 12px;")

    def _clear_error(self) -> None:
        self.error_label.clear()
        self.error_label.setVisible(False)


__all__ = ["AnalysisWorkspace", "CompositionChartCanvas", "MassFlowChartCanvas"]
