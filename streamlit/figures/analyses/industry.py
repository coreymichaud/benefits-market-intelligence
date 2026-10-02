"""Broker pay by industry (analysis 6)."""

import pandas as pd
import plotly.graph_objects as go

from figures.analyses.common import Chart, fit, unit
from figures.data import Filters, Tables, subset
from figures.theme import (
    BLACK,
    KEEP_STYLE,
    USD,
    base_theme,
    empty_figure,
    fade,
    growth,
    money,
    scale_color,
)

# 6. Which industries hold the largest and fastest-growing broker compensation pools?


def industries(t: Tables, f: Filters, height: int = 400, top_n: int = 12) -> Chart:
    df = subset(t.contracts, f, industry=False)
    df = df[(df["sector"] != "Unknown") & df["year"].isin([f.start, f.end])]
    industry = (
        df.assign(comp=df["commissions"] + df["fees"])
        .pivot_table(index="sector", columns="year", values="comp", aggfunc="sum")
        .reindex(columns=[f.start, f.end])
        .fillna(0)
    )
    industry = industry[(industry[f.start] > 0) & (industry[f.end] > 0)]
    if len(industry) < 3:
        return Chart(
            "Too few industries with broker pay for this selection",
            "",
            empty_figure("Too few industries", height),
        )

    industry["growth"] = growth(industry[f.end], industry[f.start])
    industry = industry.sort_values(f.end, ascending=False)
    largest = industry.index[0]
    fastest = industry.head(10)["growth"].idxmax()
    if fastest == largest:
        headline = f"{largest} is the largest and fastest-growing broker pay pool among the top 10"
    else:
        headline = fit(
            f"{largest} is the largest broker pay pool; {fastest} is growing fastest among the top 10",
            f"{largest} is the largest pool; {fastest} is growing fastest",
            limit=118,
        )
    caption = (
        f"Broker pay in {f.end} for the {min(top_n, len(industry))} largest sponsor industries, shaded by "
        f"growth since {f.start}. Click an industry to filter."
    )

    shown = industry.head(top_n)
    if f.industry in industry.index and f.industry not in shown.index:
        shown = pd.concat([shown.iloc[:-1], industry.loc[[f.industry]]])
    shown = shown.iloc[::-1]  # largest on top
    lo, hi = min(0, industry["growth"].min()), industry["growth"].max()
    colors = [
        scale_color(g, lo, hi)
        if (not f.industry or s == f.industry)
        else fade(scale_color(g, lo, hi), 0.7)
        for s, g in zip(shown.index, shown["growth"])
    ]
    ticks = [f"<b>{s}</b>" if s == f.industry else s for s in shown.index]
    scale, suffix = unit(shown[f.end].max())
    fig = go.Figure(
        go.Bar(
            y=ticks,
            x=shown[f.end] / scale,
            orientation="h",
            marker=dict(color=colors),
            text=[
                f"{money(v)}  {g:+.0f}%" for v, g in zip(shown[f.end], shown["growth"])
            ],
            textposition="outside",
            textfont=dict(size=11, color=BLACK),
            cliponaxis=False,
            customdata=shown.index,
            hovertemplate="<b>%{customdata}</b><br>"
            + str(f.end)
            + f" pool: {USD}%{{x:.2f}}{suffix}<extra></extra>",
            **KEEP_STYLE,
        )
    )
    base_theme(fig, height, margin=dict(l=10, r=10, t=10, b=10))
    fig.update_layout(
        bargap=0.25,
        xaxis=dict(visible=False, range=[0, shown[f.end].max() / scale * 1.35]),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
    )
    return Chart(headline, caption, fig)
