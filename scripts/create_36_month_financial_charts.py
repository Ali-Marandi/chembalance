"""Render 36-month revenue, cash, and acquisition-sensitivity charts for ChemBalance.

All series originate from the management assumptions in
``create_seed_financial_model.py``.  The output is an illustrative plan, not
historical revenue, booked ARR, or a forecast guaranteed to investors.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from create_seed_financial_model import ASSUMPTIONS

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CSV_PATH = DOCS / "financial_36_month_forecast.csv"
FORECAST_CHART = DOCS / "financial_36_month_forecast.png"
SENSITIVITY_CHART = DOCS / "financial_sensitivity_scenarios.png"

YEARS = (2027, 2028, 2029)
SEGMENTS = (
    ("Pro", "New Pro subscriptions", "Pro annual price ($)", "#0C8A66"),
    ("Team", "New Team accounts", "Team annual contract value ($)", "#467599"),
    ("Enterprise", "New Enterprise accounts", "Enterprise annual contract value ($)", "#D90429"),
)


def monthly_records() -> list[dict[str, float | int | str]]:
    """Build a 36-month plan that exactly rolls to the annual Seed model.

    Each year's additions are spread uniformly across the twelve months.
    The monthly average active count is ``beginning + new * (m - .5) / 12``;
    this makes the sum of monthly revenue equal the annual revenue formula
    ``(beginning + ending) / 2 * ACV`` used in the workbook.
    """
    records: list[dict[str, float | int | str]] = []
    ending_accounts = {segment[0]: 0.0 for segment in SEGMENTS}
    cash = 0.0
    month_number = 0

    for year_index, year in enumerate(YEARS):
        annual_operating_cost = (
            ASSUMPTIONS["Research & development ($000)"][year_index]
            + ASSUMPTIONS["Sales & marketing ($000)"][year_index]
            + ASSUMPTIONS["General & administrative ($000)"][year_index]
            + ASSUMPTIONS["Working capital / tools ($000)"][year_index]
        )
        seed_proceeds = ASSUMPTIONS["Seed capital proceeds ($000)"][year_index]
        for month_in_year in range(1, 13):
            month_number += 1
            row: dict[str, float | int | str] = {
                "month_number": month_number,
                "period": f"{year}-{month_in_year:02d}",
                "year": year,
                "month_in_year": month_in_year,
            }
            total_revenue = 0.0
            for segment, additions_key, price_key, _color in SEGMENTS:
                annual_additions = float(ASSUMPTIONS[additions_key][year_index])
                annual_price = float(ASSUMPTIONS[price_key][year_index])
                beginning = ending_accounts[segment]
                average_active = beginning + annual_additions * (month_in_year - 0.5) / 12
                revenue = average_active * annual_price / 12 / 1000
                row[f"{segment.lower()}_revenue_k"] = revenue
                total_revenue += revenue
            cost_of_revenue = total_revenue * float(ASSUMPTIONS["Cost of revenue (% of revenue)"][year_index])
            monthly_operating_cost = annual_operating_cost / 12
            free_cash_flow = total_revenue - cost_of_revenue - monthly_operating_cost
            if month_in_year == 1:
                cash += seed_proceeds
            cash += free_cash_flow
            row["revenue_k"] = total_revenue
            row["cost_of_revenue_k"] = cost_of_revenue
            row["operating_and_working_capital_k"] = monthly_operating_cost
            row["free_cash_flow_k"] = free_cash_flow
            row["ending_cash_k"] = cash
            records.append(row)
        for segment, additions_key, _price_key, _color in SEGMENTS:
            ending_accounts[segment] += float(ASSUMPTIONS[additions_key][year_index])
    return records


def write_csv(records: list[dict[str, float | int | str]]) -> None:
    fieldnames = list(records[0].keys())
    with CSV_PATH.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def month_label(record: dict[str, float | int | str]) -> str:
    return str(record["period"])


def money_format(value: float, _position: int) -> str:
    return f"${value:,.0f}k"


def decorate_axis(axis) -> None:
    axis.set_facecolor("#FFFFFF")
    axis.grid(axis="y", color="#DCE5E1", linewidth=0.8)
    axis.set_axisbelow(True)
    axis.spines[["top", "right"]].set_visible(False)
    axis.tick_params(colors="#2F3E46")


def draw_forecast(records: list[dict[str, float | int | str]]) -> None:
    x_values = list(range(1, 37))
    labels = [month_label(record) for record in records]
    figure, (revenue_axis, cash_axis) = plt.subplots(2, 1, figsize=(15, 10), dpi=180, sharex=True)
    figure.patch.set_facecolor("#F4F7FB")

    bottom = [0.0] * len(records)
    for segment, _additions_key, _price_key, color in SEGMENTS:
        series = [float(record[f"{segment.lower()}_revenue_k"]) for record in records]
        revenue_axis.bar(x_values, series, bottom=bottom, label=segment, color=color, width=0.82)
        bottom = [current + value for current, value in zip(bottom, series)]
    revenue_axis.set_title("36-month recurring revenue build — management base case", fontweight="bold", color="#2F3E46")
    revenue_axis.set_ylabel("Monthly revenue ($000)")
    revenue_axis.legend(frameon=False, ncol=3, loc="upper left")
    decorate_axis(revenue_axis)

    cash_series = [float(record["ending_cash_k"]) for record in records]
    cash_axis.plot(x_values, cash_series, color="#2F3E46", linewidth=2.7, marker="o", markersize=2.5)
    cash_axis.fill_between(x_values, cash_series, color="#CFE9E0")
    cash_axis.axhline(0, color="#D90429", linewidth=1.1)
    cash_axis.set_title("Ending cash after operating cost and working-capital/tools", fontweight="bold", color="#2F3E46")
    cash_axis.set_ylabel("Ending cash ($000)")
    decorate_axis(cash_axis)
    cash_axis.yaxis.set_major_formatter(FuncFormatter(money_format))
    tick_positions = [1, 6, 12, 18, 24, 30, 36]
    cash_axis.set_xticks(tick_positions, [labels[position - 1] for position in tick_positions])
    cash_axis.set_xlabel("Forecast month")

    for end_month, label in ((12, "2027E"), (24, "2028E"), (36, "2029E")):
        revenue_axis.axvline(end_month + 0.5, color="#A5B1AC", linewidth=0.8)
        cash_axis.axvline(end_month + 0.5, color="#A5B1AC", linewidth=0.8)
        cash_axis.annotate(label, (end_month, cash_series[end_month - 1]), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=9, color="#2F3E46")

    figure.suptitle("ChemBalance Seed plan — monthly view", fontsize=17, fontweight="bold", color="#2F3E46")
    figure.text(0.5, 0.012, "Illustrative management assumptions only; not actual revenue, booked ARR, contracted revenue, or investment guidance.", ha="center", fontsize=9, color="#59656B")
    figure.tight_layout(rect=(0, 0.04, 1, 0.95))
    figure.savefig(FORECAST_CHART, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)


def scenario_cash(records: list[dict[str, float | int | str]], multiplier: float) -> list[float]:
    """Recalculate cash when new-logo-derived revenue changes and costs stay base case."""
    cash = 0.0
    result: list[float] = []
    for index, record in enumerate(records):
        year_index = index // 12
        base_revenue = float(record["revenue_k"])
        adjusted_revenue = base_revenue * multiplier
        adjusted_cost_of_revenue = adjusted_revenue * float(ASSUMPTIONS["Cost of revenue (% of revenue)"][year_index])
        operating_cost = float(record["operating_and_working_capital_k"])
        if index % 12 == 0:
            cash += float(ASSUMPTIONS["Seed capital proceeds ($000)"][year_index])
        cash += adjusted_revenue - adjusted_cost_of_revenue - operating_cost
        result.append(cash)
    return result


def draw_sensitivity(records: list[dict[str, float | int | str]]) -> None:
    scenarios = (("Downside: 70% acquisition", 0.70, "#D90429"), ("Base: 100% acquisition", 1.00, "#2F3E46"), ("Upside: 130% acquisition", 1.30, "#0C8A66"))
    x_values = list(range(1, 37))
    labels = [month_label(record) for record in records]
    figure, (cash_axis, terminal_axis) = plt.subplots(1, 2, figsize=(15, 6.7), dpi=180, gridspec_kw={"width_ratios": [2.1, 1]})
    figure.patch.set_facecolor("#F4F7FB")
    terminal_cash: list[float] = []

    for name, multiplier, color in scenarios:
        cash = scenario_cash(records, multiplier)
        terminal_cash.append(cash[-1])
        cash_axis.plot(x_values, cash, label=name, color=color, linewidth=2.6)
    cash_axis.axhline(0, color="#D90429", linewidth=1.0)
    cash_axis.set_title("Cash sensitivity to customer-acquisition pace", fontweight="bold", color="#2F3E46")
    cash_axis.set_ylabel("Ending cash ($000)")
    cash_axis.set_xlabel("Forecast month")
    cash_axis.set_xticks([1, 12, 24, 36], [labels[0], labels[11], labels[23], labels[35]])
    cash_axis.yaxis.set_major_formatter(FuncFormatter(money_format))
    cash_axis.legend(frameon=False, loc="upper right")
    decorate_axis(cash_axis)

    scenario_names = [item[0].split(":")[0] for item in scenarios]
    scenario_colors = [item[2] for item in scenarios]
    bars = terminal_axis.bar(scenario_names, terminal_cash, color=scenario_colors, width=0.62)
    terminal_axis.axhline(0, color="#D90429", linewidth=1.0)
    terminal_axis.set_title("2029E ending cash", fontweight="bold", color="#2F3E46")
    terminal_axis.set_ylabel("Cash ($000)")
    terminal_axis.yaxis.set_major_formatter(FuncFormatter(money_format))
    decorate_axis(terminal_axis)
    for bar, value in zip(bars, terminal_cash):
        terminal_axis.text(bar.get_x() + bar.get_width() / 2, value + 20, f"${value:.1f}k", ha="center", fontweight="bold", color="#2F3E46")

    figure.suptitle("ChemBalance Seed plan — acquisition sensitivity", fontsize=17, fontweight="bold", color="#2F3E46")
    figure.text(0.5, 0.01, "Only acquisition-derived revenue varies; pricing and operating costs remain at base assumptions. Management scenario, not a guaranteed forecast.", ha="center", fontsize=9, color="#59656B")
    figure.tight_layout(rect=(0, 0.05, 1, 0.94))
    figure.savefig(SENSITIVITY_CHART, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)


def main() -> int:
    DOCS.mkdir(parents=True, exist_ok=True)
    records = monthly_records()
    write_csv(records)
    draw_forecast(records)
    draw_sensitivity(records)
    annual_cash = [records[index]["ending_cash_k"] for index in (11, 23, 35)]
    print(f"Created {CSV_PATH}")
    print(f"Created {FORECAST_CHART}")
    print(f"Created {SENSITIVITY_CHART}")
    print("Annual ending cash ($000):", annual_cash)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
