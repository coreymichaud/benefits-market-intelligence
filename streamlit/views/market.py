"""Market: how big the broker pay pool is, what is driving it, and how brokers get paid."""

import streamlit as st

from figures import analyses, kpis
from figures.data import LINES, load
from figures.layout import filters, panel

t = load()
f = filters()


def _toggle_line(point: dict) -> None:
    """Clicking a bar in the bridge adds or removes that line from the line filter."""
    line = point.get("customdata")
    if line:
        current = st.session_state.get("lines") or []
        st.session_state["lines"] = (
            [x for x in current if x != line] if line in current else current + [line]
        )


# The KPI strip sits above the line filter but depends on it, so reserve its slot and fill it later
kpi_strip = st.container()

left, right = st.columns([7, 5], gap="large")
with left:
    with st.container(horizontal=True, vertical_alignment="center", gap="small"):
        st.markdown("**Line of coverage**", width="content")
        lines = (
            st.pills(
                "Line of coverage",
                LINES,
                selection_mode="multi",
                key="lines",
                label_visibility="collapsed",
                bind="query-params",
                persist_state="session",
            )
            or []
        )
    panel(analyses.pay_pool(t, f, lines, height=430), key="pool")
with right:
    view = st.segmented_control(
        "View",
        ["Growth by line", "Take rate", "Fee adoption"],
        default="Growth by line",
        required=True,
        key="market_view",
        label_visibility="collapsed",
        bind="query-params",
        persist_state="session",
    )
    if view == "Take rate":
        panel(analyses.take_rate(t, f, lines, height=430), key="take_rate")
    elif view == "Fee adoption":
        panel(analyses.fee_adoption(t, f, lines, height=430), key="fees")
    else:
        panel(
            analyses.growth_bridge(t, f, lines, height=430),
            key=f"bridge_{'_'.join(sorted(lines))}",
            on_click=_toggle_line,
        )

with kpi_strip:
    kpis.render(kpis.market(t, f, lines))
