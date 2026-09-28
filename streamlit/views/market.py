"""Market: size of the broker pay pool, what is driving it, and how brokers get paid."""

import streamlit as st

from figures import analyses, kpis
from figures.data import LINES, load
from figures.layout import filters, panel, view_switch

HEIGHT = 450

t = load()
f = filters()


def _toggle_line(point: dict) -> None:
    line = point.get("customdata")
    if line:
        current = st.session_state.get("lines") or []
        st.session_state["lines"] = (
            [x for x in current if x != line] if line in current else [*current, line]
        )


# The KPIs sit above the line filter but depend on it, so they are filled in at the end
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
    panel(analyses.pay_pool(t, f, lines, height=HEIGHT), key="pool")
with right:
    view = view_switch(
        ["Growth by line", "Take rate", "Fee adoption"], key="market_view"
    )
    if view == "Take rate":
        panel(analyses.take_rate(t, f, lines, height=HEIGHT), key="take_rate")
    elif view == "Fee adoption":
        panel(analyses.fee_adoption(t, f, lines, height=HEIGHT), key="fees")
    else:
        panel(
            analyses.growth_bridge(t, f, lines, height=HEIGHT),
            key=f"bridge_{'_'.join(sorted(lines))}",
            on_click=_toggle_line,
        )

with kpi_strip:
    kpis.render(kpis.market(t, f, lines))
