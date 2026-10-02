"""Carrier share of insured premium."""

import plotly.graph_objects as go

from figures.analyses.common import Chart, fit, line_name
from figures.data import Filters, Tables, subset
from figures.theme import (
    BLACK,
    MUTED,
    base_theme,
    empty_figure,
    join_names,
    trend_color,
)

# Carriers: who writes the insured premium


def _carrier_label(name: str, width: int = 34) -> str:
    """Title-cases and shortens the filed carrier names for the axis."""
    label = name.title()
    return label if len(label) <= width else label[: width - 3].rstrip() + "..."


def carrier_share(
    t: Tables,
    f: Filters,
    lines: list[str] | None = None,
    height: int = 400,
    top_n: int = 10,
) -> Chart:
    df = subset(t.carriers, f)
    if lines:
        df = df[df["line"].isin(lines)]
    df = df[df["year"].isin([f.start, f.end])]
    premium = (
        df.pivot_table(
            index="carrier", columns="year", values="tr_premium", aggfunc="sum"
        )
        .reindex(columns=[f.start, f.end])
        .fillna(0)
    )
    if premium.empty or premium[f.start].sum() <= 0 or premium[f.end].sum() <= 0:
        return Chart(
            "Not enough premium data for this selection",
            "",
            empty_figure("Too few contracts", height),
        )

    share = premium / premium.sum() * 100
    share["delta"] = share[f.end] - share[f.start]
    contracts = (
        df[df["year"] == f.end]
        .groupby("carrier")["contracts"]
        .sum()
        .reindex(share.index)
    )
    named = share.drop("Other carriers", errors="ignore").sort_values(
        f.end, ascending=False
    )
    top5 = named[f.end].head(5).sum()
    gainers = named[named["delta"] >= 0.5].sort_values("delta", ascending=False)
    scope = (
        f" for {join_names([line_name(x) for x in lines])}"
        if lines and len(lines) <= 2
        else ""
    )
    gain = (
        f"; {_carrier_label(gainers.index[0])} gained the most share"
        if len(gainers)
        else ""
    )
    headline = fit(
        f"The five largest carriers write {top5:.0f}% of insured premium{scope}{gain}",
        f"The five largest carriers write {top5:.0f}% of insured premium{scope}",
        limit=100,
    )
    caption = (
        f"Share of premium by carrier in {f.end}, with the change since {f.start}. Each carrier "
        "is one NAIC code, labeled with the name it files under most often, so affiliates of "
        "the same parent company show separately."
    )

    shown = named.head(top_n).iloc[::-1]
    colors = [trend_color(d, 0.3) if abs(d) >= 0.3 else MUTED for d in shown["delta"]]
    fig = go.Figure(
        go.Bar(
            y=list(shown.index),
            x=shown[f.end],
            orientation="h",
            marker=dict(color=colors),
            text=[
                f"{v:.1f}%  ({d:+.1f} pts)"
                for v, d in zip(shown[f.end], shown["delta"])
            ],
            textposition="outside",
            textfont=dict(size=11, color=BLACK),
            cliponaxis=False,
            # List of pairs so the counts stay numbers and the hover can format them
            customdata=[
                [name, n]
                for name, n in zip(
                    shown.index, contracts.reindex(shown.index).fillna(0)
                )
            ],
            hovertemplate="<b>%{customdata[0]}</b><br>%{x:.1f}% of premium"
            "<br>%{customdata[1]:,.0f} contracts<extra></extra>",
        )
    )
    base_theme(fig, height, margin=dict(l=10, r=10, t=10, b=10))
    fig.update_layout(
        bargap=0.25,
        xaxis=dict(visible=False, range=[0, shown[f.end].max() * 1.45]),
        # Full names as categories so two carriers don't merge after trimming
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=11),
            tickvals=list(shown.index),
            ticktext=[_carrier_label(c) for c in shown.index],
        ),
    )
    return Chart(headline, caption, fig)
