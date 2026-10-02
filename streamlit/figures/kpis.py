"""KPI strips for each page, built from the same aggregates as the charts."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import streamlit as st

from figures.analyses import market_by_year
from figures.constants import STATE_NAMES
from figures.data import Filters, Tables, subset
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
            f"{f.start}-{f.end}",
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


SHORT_SECTORS = {
    "Accommodation & Food Services": "Hospitality",
    "Admin & Support Services": "Admin & Support",
    "Educational Services": "Education",
    "Health Care & Social Assistance": "Health Care",
    "Management of Companies": "Holding Companies",
    "Professional & Technical Services": "Professional Services",
    "Public Administration": "Public Admin",
    "Transportation & Warehousing": "Transportation",
}


def _pool(df: pd.DataFrame, by: str, f: Filters) -> pd.DataFrame:
    """Broker pay by `by` (rows) and year (columns)."""
    return (
        df.assign(comp=df["commissions"] + df["fees"])
        .pivot_table(index=by, columns="year", values="comp", aggfunc="sum")
        .reindex(columns=f.years)
        .fillna(0)
    )


def _share(df: pd.DataFrame, numerator: str, f: Filters) -> pd.Series:
    agg = df.groupby("year")[[numerator, "plans"]].sum().reindex(f.years)
    return (agg[numerator] / agg["plans"].where(agg["plans"] >= 25) * 100).astype(float)


def _share_kpi(label: str, share: pd.Series, f: Filters, help: str) -> Kpi:
    first, last = share.iloc[0], share.iloc[-1]
    if not (np.isfinite(first) and np.isfinite(last)):
        return Kpi(label, "–", help=help)
    return Kpi(
        label,
        f"{last:.1f}%",
        _signed(last - first, ".1f", " pts"),
        f"since {f.start}",
        share.ffill().bfill().tolist(),
        help,
    )


def opportunity(t: Tables, f: Filters) -> list[Kpi]:
    since = f"since {f.start}"
    out = []

    # Where: the state card ignores the state filter (like the map) unless one is picked
    states = subset(t.contracts, f, state=False)
    states = _pool(states[states["state"].isin(STATE_NAMES)], "state", f)
    us_growth = growth(states[f.end].sum(), states[f.start].sum())
    if f.state:
        row = (
            states.loc[f.state]
            if f.state in states.index
            else pd.Series(0.0, index=f.years)
        )
        change = growth(row[f.end], row[f.start])
        out.append(
            Kpi(
                f"{STATE_NAMES[f.state]} broker pay",
                money(row[f.end], plotly=False),
                _signed(change, ".0f", "%") if np.isfinite(change) else None,
                f"vs. U.S. {us_growth:+.0f}%",
                row.tolist(),
                f"Broker pay on plans sponsored in {STATE_NAMES[f.state]}, {f.end}.",
            )
        )
    else:
        established = states[states[f.start] >= states[f.start].sum() * 0.0093]
        rates = growth(established[f.end], established[f.start]).dropna()
        if rates.empty:
            out.append(Kpi("Fastest-growing state", "–"))
        else:
            top = rates.idxmax()
            out.append(
                Kpi(
                    "Fastest-growing state",
                    STATE_NAMES[top],
                    _signed(rates[top], ".0f", "%"),
                    since,
                    states.loc[top].tolist(),
                    "Growth in broker pay among states with at least 0.9% of the national pool "
                    f"in {f.start}. The U.S. grew {us_growth:+.0f}%.",
                )
            )

    sectors = subset(t.contracts, f, industry=False)
    sectors = _pool(sectors[sectors["sector"] != "Unknown"], "sector", f)
    all_growth = growth(sectors[f.end].sum(), sectors[f.start].sum())
    if f.industry:
        row = (
            sectors.loc[f.industry]
            if f.industry in sectors.index
            else pd.Series(0.0, index=f.years)
        )
        change = growth(row[f.end], row[f.start])
        out.append(
            Kpi(
                f"{SHORT_SECTORS.get(f.industry, f.industry)} broker pay",
                money(row[f.end], plotly=False),
                _signed(change, ".0f", "%") if np.isfinite(change) else None,
                f"vs. all industries {all_growth:+.0f}%",
                row.tolist(),
                f"Broker pay on plans sponsored by {f.industry} employers, {f.end}.",
            )
        )
    else:
        top10 = sectors.sort_values(f.end, ascending=False).head(10)
        rates = growth(top10[f.end], top10[f.start]).dropna()
        if rates.empty:
            out.append(Kpi("Fastest-growing industry", "–"))
        else:
            top = rates.idxmax()
            out.append(
                Kpi(
                    "Fastest-growing industry",
                    SHORT_SECTORS.get(top, top),
                    _signed(rates[top], ".0f", "%"),
                    since,
                    sectors.loc[top].tolist(),
                    f"{top}: fastest growth in broker pay among the 10 largest industries.",
                )
            )

    # What employers buy
    health = subset(t.health, f)
    out.append(
        _share_kpi(
            "Self-funded health plans",
            _share(health, "self_funded", f),
            f,
            "Single-employer health plans (100+ participants) with no fully insured medical "
            "contract: self-funded or level-funded.",
        )
    )
    out.append(
        _share_kpi(
            "Self-funded, 100-249 participants",
            _share(health[health["band"] == "100-249"], "self_funded", f),
            f,
            "The same measure for the smallest plans in the data, where the shift is fastest.",
        )
    )
    out.append(
        _share_kpi(
            "Plans with voluntary benefits",
            _share(subset(t.voluntary, f), "with_voluntary", f),
            f,
            "Single-employer welfare plans (100+ participants) with an insured voluntary contract "
            "such as accident, critical illness or hospital indemnity.",
        )
    )
    return out
