"""Where broker pay is growing, by plan sponsor state."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from figures.analyses.common import Chart
from figures.constants import STATE_NAMES
from figures.data import Filters, Tables, subset
from figures.theme import (
    BLACK,
    FAINT,
    PALETTE,
    RED,
    base_theme,
    empty_figure,
    growth,
    join_names,
    money,
)

# 10. Where is broker compensation growing fastest?


def _growth_without_top_plans(t: Tables, f: Filters, n: int = 5) -> pd.Series:
    """Each state's broker pay growth with its n fastest-growing plans taken out."""
    df = subset(t.plan_pay, f, state=False)
    df = df[df["year"].isin([f.start, f.end])]
    pay = df.pivot_table(
        index=["state", "plan_id"],
        columns="year",
        values="pay",
        aggfunc="sum",
        fill_value=0,
        observed=True,
    ).reindex(columns=[f.start, f.end], fill_value=0)
    pay["change"] = pay[f.end] - pay[f.start]
    top = pay.groupby(level="state", group_keys=False)["change"].nlargest(n).index
    rest = pay.drop(top).groupby(level="state")[[f.start, f.end]].sum()
    return growth(rest[f.end], rest[f.start])


def state_map(t: Tables, f: Filters, height: int = 400) -> Chart:
    df = subset(t.contracts, f, state=False)
    df = df[df["state"].isin(STATE_NAMES) & df["year"].isin([f.start, f.end])]
    by_state = (
        df.assign(comp=df["commissions"] + df["fees"])
        .pivot_table(index="state", columns="year", values="comp", aggfunc="sum")
        .reindex(columns=[f.start, f.end])
        .dropna()
    )
    by_state = by_state[(by_state[f.start] > 0) & (by_state[f.end] > 0)]
    if len(by_state) < 5:
        return Chart(
            "Too few states with broker pay for this selection",
            "",
            empty_figure("Too few states", height),
        )

    by_state["growth"] = growth(by_state[f.end], by_state[f.start])
    by_state["growth_ex5"] = _growth_without_top_plans(t, f).reindex(by_state.index)
    national = growth(by_state[f.end].sum(), by_state[f.start].sum())
    # Same cut-offs as the notebook ($25M / $50M on the full market), scaled to the current slice
    small = by_state[f.end] < by_state[f.end].sum() * 0.0033
    established = by_state[by_state[f.start] >= by_state[f.start].sum() * 0.0093]
    fastest = established["growth"].sort_values(ascending=False).index[:3].tolist()
    largest = by_state[f.end].idxmax()
    lg = by_state.loc[largest, "growth"]
    headline = (
        f"Broker pay is growing fastest in {join_names([STATE_NAMES[s] for s in fastest])}; "
        f"{STATE_NAMES[largest]}, the largest market, {'lags' if lg < national else 'leads'} at {lg:+.0f}%"
    )
    cutoff = money(by_state[f.end].sum() * 0.0033, 0, plotly=False)
    lead_ex5 = by_state.loc[fastest[0], "growth_ex5"] if fastest else np.nan
    check = (
        f" Without its five fastest-growing plans, {STATE_NAMES[fastest[0]]} grew "
        f"{lead_ex5:+.0f}%."
        if np.isfinite(lead_ex5)
        else ""
    )
    caption = (
        f"Broker pay growth by plan sponsor state, {f.start} to {f.end}, against the U.S. rate "
        f"of {national:+.0f}%.{check} Grey: markets under {cutoff}. Click a state to filter."
    )

    span = max(abs(national), 10)
    fig = go.Figure()
    small_states = by_state.index[small]
    if len(small_states):
        fig.add_trace(
            go.Choropleth(
                locations=small_states,
                locationmode="USA-states",
                z=[0] * len(small_states),
                colorscale=[[0, "#E3E3E3"], [1, "#E3E3E3"]],
                showscale=False,
                marker_line_color="white",
                marker_line_width=1,
                customdata=np.column_stack(
                    [
                        [STATE_NAMES[s] for s in small_states],
                        [money(v) for v in by_state.loc[small, f.end]],
                    ]
                ),
                hovertemplate="<b>%{customdata[0]}</b><br>"
                + str(f.end)
                + " pool: %{customdata[1]} (small market)<extra></extra>",
                unselected=dict(marker=dict(opacity=1)),
            )
        )
    big = by_state[~small]
    fig.add_trace(
        go.Choropleth(
            locations=big.index,
            locationmode="USA-states",
            z=big["growth"],
            zmin=national - span,
            zmax=national + span,
            zmid=national,
            colorscale=[
                [0, RED],
                [0.3, "#E6B3B5"],
                [0.5, FAINT],
                [0.7, PALETTE[0]],
                [1, PALETTE[2]],
            ],
            marker_line_color="white",
            marker_line_width=1,
            customdata=np.column_stack(
                [
                    [STATE_NAMES[s] for s in big.index],
                    [money(v) for v in big[f.start]],
                    [money(v) for v in big[f.end]],
                    [
                        f"{v:+.0f}%" if np.isfinite(v) else "n/a"
                        for v in big["growth_ex5"]
                    ],
                ]
            ),
            hovertemplate="<b>%{customdata[0]}</b><br>"
            + str(f.start)
            + ": %{customdata[1]}<br>"
            + str(f.end)
            + ": %{customdata[2]}<br>Growth: %{z:+.1f}%<br>"
            + "Without its 5 fastest-growing plans: %{customdata[3]}<extra></extra>",
            colorbar=dict(
                title=dict(
                    text=f"Growth<br>{f.start}-{f.end}", side="top", font=dict(size=11)
                ),
                tickvals=[national - span, national, national + span],
                ticktext=[
                    f"{national - span:+.0f}% or less",
                    f"U.S. {national:+.0f}%",
                    f"{national + span:+.0f}% or more",
                ],
                thickness=12,
                len=0.7,
                x=0.9,
                tickfont=dict(size=10),
            ),
            unselected=dict(marker=dict(opacity=1)),
        )
    )
    labeled = big[f.end].sort_values(ascending=False).index[:15]
    fig.add_trace(
        go.Scattergeo(
            locations=labeled,
            locationmode="USA-states",
            mode="text",
            text=[f"<b>{s}</b><br>{big.loc[s, 'growth']:+.0f}%" for s in labeled],
            textfont=dict(
                size=10,
                color=[
                    "white"
                    if abs(big.loc[s, "growth"] - national) > span * 0.55
                    else BLACK
                    for s in labeled
                ],
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    if f.state in by_state.index:
        fig.add_trace(
            go.Choropleth(
                locations=[f.state],
                locationmode="USA-states",
                z=[1],
                colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                showscale=False,
                marker_line_color=BLACK,
                marker_line_width=2.5,
                hoverinfo="skip",
                unselected=dict(marker=dict(opacity=1)),
            )
        )
    fig.update_geos(
        domain=dict(x=[0, 0.9]),
        scope="usa",
        projection_type="albers usa",
        showlakes=False,
        bgcolor="white",
        landcolor=FAINT,
    )
    base_theme(fig, height, margin=dict(l=0, r=0, t=0, b=0))
    return Chart(headline, caption, fig)
