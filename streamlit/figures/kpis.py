"""Headline numbers for the KPI strips.

Market KPIs come from the same yearly aggregates as the pay pool chart (analyses 1, 3 and 7), so
the strip and the charts always agree. Broker KPIs come from `firm_stats` (analyses 5 and 9).
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import streamlit as st

from figures.analyses import firm_stats, market_by_year
from figures.data import Filters, Tables
from figures.theme import count, growth, money


@dataclass
class Kpi:
    label: str
    value: str
    delta: str | None = None
    description: str | None = None
    chart: list[float] | None = None
    help: str | None = None
    color: str = "normal"
    arrow: str = "auto"


def render(kpis: list[Kpi], columns=None) -> None:
    """Draw KPIs side by side, one bordered metric per column."""
    columns = columns or st.columns(len(kpis))
    for col, k in zip(columns, kpis):
        col.metric(
            k.label,
            k.value,
            delta=k.delta,
            delta_color=k.color,
            delta_arrow=k.arrow,
            delta_description=k.description,
            help=k.help,
            border=True,
            chart_data=k.chart,
            chart_type="area",
        )


def _signed(v: float, fmt: str, unit: str = "") -> str:
    return f"{'+' if v >= 0 else '-'}{format(abs(v), fmt)}{unit}"


def market(t: Tables, f: Filters, lines: list[str] | None = None) -> list[Kpi]:
    m = market_by_year(t, f, lines)
    first, last = m.iloc[0], m.iloc[-1]
    since = f"since {f.start}"
    if first["compensation"] <= 0 or last["compensation"] <= 0:
        return [
            Kpi(label, "–")
            for label in [
                "Broker pay",
                "Covered lives",
                "Pay per covered life",
                "Take rate",
                "Paid as fees",
            ]
        ]

    per_life_change = last["comp_per_life"] - first["comp_per_life"]
    kpis = [
        Kpi(
            "Broker pay",
            money(last["compensation"], plotly=False),
            _signed(growth(last["compensation"], first["compensation"]), ".0f", "%"),
            since,
            m["compensation"].tolist(),
            f"Commissions plus carrier-paid fees on welfare-plan insurance contracts (Schedule A) in {f.end}.",
        ),
        Kpi(
            "Covered lives",
            count(last["lives"]),
            _signed(growth(last["lives"], first["lives"]), ".0f", "%"),
            since,
            m["lives"].tolist(),
            "People covered at year end on those contracts. Counts can include dependents.",
        ),
        Kpi(
            "Pay per covered life",
            f"\\${last['comp_per_life']:.2f}",
            f"{'+' if per_life_change >= 0 else '-'}\\${abs(per_life_change):.2f}",
            since,
            m["comp_per_life"].tolist(),
            "Broker pay divided by covered lives: what a broker earns for each person on the plan.",
        ),
        Kpi(
            "Take rate",
            f"{last['take_rate']:.2f}%",
            _signed(last["take_rate"] - first["take_rate"], ".2f", " pts"),
            since,
            m["take_rate"].tolist(),
            "Broker pay as a share of premium, on contracts that pass the premium screens "
            "(under \\$250M premium, pay no more than 100% of premium).",
        ),
        Kpi(
            "Paid as fees",
            f"{last['fee_share']:.1f}%",
            _signed(last["fee_share"] - first["fee_share"], ".1f", " pts"),
            since,
            m["fee_share"].tolist(),
            "Share of broker pay that carriers paid as fees (bonuses, overrides, service fees) "
            "rather than commissions.",
        ),
    ]
    if lines:
        scope = lines[0] if len(lines) == 1 else f"{len(lines)} lines"
        for k in kpis:
            k.label = f"{k.label} ({scope})"
    return kpis


def _ordinal(n: int) -> str:
    suffix = (
        "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    )
    return f"{n}{suffix}"


def broker(stats: pd.DataFrame, firm: str, f: Filters) -> list[Kpi]:
    if stats.empty or firm not in stats.index:
        return [
            Kpi(label, "–")
            for label in [
                "Plans served",
                "Leaderboard rank",
                "Net plan wins",
                "Wins from local brokers",
                "Clients kept",
            ]
        ]
    row = stats.loc[firm]
    since = f"since {f.start}"
    plans = [row[f"plans_{y}"] for y in f.years]

    plan_growth = row["growth"]
    plan_delta = _signed(plan_growth, ".0f", "%") if np.isfinite(plan_growth) else "New"

    moved = int(row["rank_first"] - row["rank_last"])
    rank_delta = (
        "No change"
        if moved == 0
        else f"{'+' if moved > 0 else '-'}{abs(moved)} place{'s' if abs(moved) != 1 else ''}"
    )

    top10 = stats.sort_values("rank_last").head(10)
    peer = top10["retention"].median()
    retention = row["retention"]

    local_share = row["won_local"] / row["won"] * 100 if row["won"] > 0 else np.nan

    def series(prefix: str) -> list[float] | None:
        values = pd.Series(
            [row.get(f"{prefix}_{y}", np.nan) for y in f.years[1:]], dtype=float
        )
        values = values.ffill().bfill()
        return values.tolist() if len(values) >= 2 and values.notna().all() else None

    trends = {
        "net": series("net"),
        "local": series("won_local"),
        "kept": series("retention"),
    }
    if any(v is None for v in trends.values()):  # keep every card the same height
        trends = dict.fromkeys(trends)
        plans = None
    return [
        Kpi(
            "Plans served",
            f"{row['plans_last']:.0f}",
            plan_delta,
            since,
            plans,
            f"Single-employer welfare plans naming {firm} on Schedule C in {f.end}.",
        ),
        Kpi(
            "Leaderboard rank",
            _ordinal(int(row["rank_last"])),
            rank_delta,
            since,
            [-row[f"rank_{y}"] for y in f.years] if plans else None,
            "Rank among 22 national brokers and consultants by plans served.",
            color="normal" if moved else "off",
            arrow="auto" if moved else "off",
        ),
        Kpi(
            "Net plan wins",
            f"{row['net']:+.0f}",
            f"{row['won']:.0f} won, {row['lost']:.0f} lost",
            f"{f.start}–{f.end}",
            trends["net"],
            "Plans that newly named the firm, minus plans that stopped naming it, among plans filing "
            "in consecutive years.",
            color="off",
            arrow="off",
        ),
        Kpi(
            "Wins from local brokers",
            f"{local_share:.0f}%" if np.isfinite(local_share) else "–",
            f"{row['won_local']:.0f} of {row['won']:.0f} wins",
            None,
            trends["local"],
            "Share of new plans that were previously served by a local broker (a broker, agent or "
            "consultant that is not one of the 22 national firms). Some of these reflect acquisitions.",
            color="off",
            arrow="off",
        ),
        Kpi(
            "Clients kept",
            f"{retention:.0f}%" if np.isfinite(retention) else "–",
            _signed(retention - peer, ".0f", " pts")
            if np.isfinite(retention) and np.isfinite(peer)
            else None,
            "vs. top-10 median",
            trends["kept"],
            "Share of plans served one year that still name the firm the next year.",
        ),
    ]


__all__ = ["Kpi", "broker", "firm_stats", "market", "render"]
