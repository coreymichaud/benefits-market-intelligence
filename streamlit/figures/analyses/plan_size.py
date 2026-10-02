"""Self-funding and voluntary benefits adoption by plan size (analyses 4 and 8)."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from figures.analyses.common import Chart, fit
from figures.constants import SELF_FUNDING_BANDS, VOLUNTARY_BANDS
from figures.data import Filters, Tables, subset
from figures.theme import (
    BLACK,
    GREY,
    GRID,
    PALETTE,
    base_theme,
    empty_figure,
    trend_color,
)

# 4. Is self-funding moving down-market into smaller employers?

YEAR_COLORS = ["#D9D9D9", "#C9E3A0", PALETTE[0], PALETTE[1], "#2E8B3A", PALETTE[2]]


def _band_rates(
    df: pd.DataFrame, bands: list[str], f: Filters, numerator: str
) -> pd.DataFrame:
    agg = df.groupby(["band", "year"])[[numerator, "plans"]].sum()
    # Skip cells with too few plans to be reliable
    agg = agg[agg["plans"] >= 25]
    rates = (
        (agg[numerator] / agg["plans"] * 100)
        .unstack("year")
        .reindex(index=bands, columns=f.years)
    )
    return rates.dropna(subset=[f.start, f.end])


def _band_plans(df: pd.DataFrame, rates: pd.DataFrame, f: Filters) -> pd.DataFrame:
    """Plan counts by band and year for the hover text."""
    plans = df.groupby(["band", "year"])["plans"].sum().unstack("year")
    return plans.reindex(index=rates.index, columns=f.years).fillna(0)


def self_funding(t: Tables, f: Filters, height: int = 300) -> Chart:
    notes: list[dict] = []
    health = subset(t.health, f)
    rates = _band_rates(health, SELF_FUNDING_BANDS, f, "self_funded")
    if len(rates) < 2:
        return Chart(
            "Too few health plans for this selection",
            "",
            empty_figure("Too few plans", height),
        )

    rates["delta"] = rates[f.end] - rates[f.start]
    lead = rates["delta"].idxmax()
    d = rates.loc[lead, "delta"]
    if d <= 0:
        headline = f"Self-funding is flat or falling in every plan size since {f.start}"
    elif lead in SELF_FUNDING_BANDS[:2]:
        headline = f"Self-funding is moving down-market: {lead}-participant plans are up {d:.1f} pts since {f.start}"
    else:
        headline = f"Self-funding grew most among {lead}-participant plans, up {d:.1f} pts since {f.start}"
    caption = (
        "Health plans (100+ participants) with no fully insured medical contract on Schedule A, "
        "meaning self-funded or level-funded."
    )

    bands = rates.index.tolist()
    plans = _band_plans(health, rates, f)
    colors = YEAR_COLORS[-len(f.years) :]
    fig = go.Figure()
    for band in bands:
        row = rates.loc[band, f.years].dropna()
        fig.add_trace(
            go.Scatter(
                x=[row.min(), row.max()],
                y=[band, band],
                mode="lines",
                line=dict(color="#E3E3E3", width=11),
                showlegend=False,
                hoverinfo="skip",
            )
        )
    for year, color in zip(f.years, colors):
        fig.add_trace(
            go.Scatter(
                x=rates[year],
                y=bands,
                mode="markers",
                name=str(year),
                marker=dict(
                    size=19 if year == f.end else 13,
                    color=color,
                    line=dict(color="white", width=1.5),
                ),
                customdata=plans[year],
                hovertemplate=f"{year}<br>%{{y}} participants<br>%{{x:.1f}}% self-funded"
                "<br>%{customdata:,.0f} health plans<extra></extra>",
            )
        )
    for band, delta in rates["delta"].items():
        notes.append(
            dict(
                x=rates.loc[band, f.years].max(),
                y=band,
                text=f"<b>{delta:+.1f} pts</b>",
                showarrow=False,
                xanchor="left",
                xshift=14,
                font=dict(size=12, color=trend_color(delta, 1)),
            )
        )
    x_min, x_max = np.nanmin(rates[f.years].values), np.nanmax(rates[f.years].values)
    base_theme(fig, height, margin=dict(l=10, r=10, t=26, b=10))
    fig.update_layout(
        legend=dict(y=1.0, yanchor="bottom", x=1, xanchor="right", font=dict(size=11)),
        xaxis=dict(
            ticksuffix="%",
            range=[np.floor(x_min / 5) * 5 - 2, np.ceil(x_max / 5) * 5 + 8],
            gridcolor=GRID,
            zeroline=False,
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            categoryorder="array",
            categoryarray=bands[::-1],
            showgrid=False,
            tickfont=dict(size=11),
            title=dict(text="Participants", font=dict(size=11, color=GREY)),
        ),
    )
    fig.update_layout(annotations=notes)
    return Chart(headline, caption, fig)


# 8. Is voluntary benefits adoption spreading across employer sizes?

BAND_COLORS = ["#A9D46F", PALETTE[0], PALETTE[1], "#2E8B3A", PALETTE[2]]


def voluntary(t: Tables, f: Filters, height: int = 300) -> Chart:
    notes: list[dict] = []
    vol = subset(t.voluntary, f)
    adoption = _band_rates(vol, VOLUNTARY_BANDS, f, "with_voluntary")
    if len(adoption) < 2:
        return Chart(
            "Too few welfare plans for this selection",
            "",
            empty_figure("Too few plans", height),
        )

    adoption["delta"] = adoption[f.end] - adoption[f.start]
    lead = adoption["delta"].idxmax()
    up = (adoption["delta"] > 0).sum()
    if up == 0:
        headline = f"Voluntary benefits adoption has not grown in any plan size since {f.start}"
    else:
        scope = (
            "every"
            if up == len(adoption)
            else "most"
            if up > len(adoption) / 2
            else "some"
        )
        sizes = "plan size" if scope == "every" else "plan sizes"
        gain = f"+{adoption.loc[lead, 'delta']:.1f} pts"
        headline = fit(
            f"Voluntary benefits adoption rose in {scope} {sizes}; "
            f"{lead}-participant plans gained the most ({gain})",
            f"Voluntary benefits adoption rose in {scope} {sizes}, led by {lead} participants ({gain})",
            limit=98,
        )
    caption = (
        "Plans (100+ participants) with an insured voluntary contract, such as accident or "
        "critical illness cover."
    )

    fig = go.Figure()
    color_for = dict(zip(VOLUNTARY_BANDS, BAND_COLORS))
    plans = _band_plans(vol, adoption, f)
    for band in adoption.index:
        y = adoption.loc[band, f.years]
        color = color_for[band]
        fig.add_trace(
            go.Scatter(
                x=f.years,
                y=y,
                mode="lines+markers",
                name=band,
                line=dict(color=color, width=3.5),
                marker=dict(
                    size=[8] + [5] * (len(f.years) - 2) + [11]
                    if len(f.years) > 1
                    else 10,
                    color=color,
                    line=dict(color="white", width=1.5),
                ),
                customdata=plans.loc[band, f.years],
                hovertemplate=f"{band} participants<br>%{{x}}: %{{y:.1f}}% of plans"
                "<br>%{customdata:,.0f} welfare plans<extra></extra>",
                showlegend=False,
            )
        )
        notes.append(
            dict(
                x=f.end,
                y=y.iloc[-1],
                xanchor="left",
                xshift=12,
                showarrow=False,
                text=f"<b>{band}</b>  {y.iloc[-1]:.0f}%  ({adoption.loc[band, 'delta']:+.1f} pts)",
                font=dict(size=11, color=BLACK),
            )
        )
    vals = adoption[f.years].values
    base_theme(fig, height, margin=dict(l=10, r=200, t=10, b=10))
    fig.update_layout(
        xaxis=dict(
            tickvals=f.years,
            showgrid=False,
            range=[f.start - 0.2, f.end + 0.1],
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            ticksuffix="%",
            gridcolor=GRID,
            zeroline=False,
            tickfont=dict(size=11),
            range=[
                np.floor(np.nanmin(vals) / 10) * 10 - 2,
                np.ceil(np.nanmax(vals) / 10) * 10 + 2,
            ],
        ),
    )
    fig.update_layout(annotations=notes)
    return Chart(headline, caption, fig)
