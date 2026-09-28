"""Brokers: who is climbing, who is slipping, and how each firm wins and keeps clients."""

import streamlit as st

from figures import analyses, kpis
from figures.data import BROKER_FIRMS, load
from figures.layout import filters, panel

t = load()
f = filters()
stats = analyses.firm_stats(t, f)

# Firms present in the current slice, leaders first; focus defaults to the current leader
firms = (
    stats.index[(stats["plans_last"] > 0) | (stats["plans_first"] > 0)].tolist()
    if len(stats)
    else []
)
firms = firms or list(BROKER_FIRMS)
if st.session_state.get("firm") not in firms:
    st.session_state["firm"] = firms[0]


def _focus(point: dict) -> None:
    """Clicking a firm in any chart makes it the focus firm."""
    data = point.get("customdata")
    firm = data[0] if isinstance(data, list) else data
    if firm in BROKER_FIRMS:
        st.session_state["firm"] = firm


cols = st.columns([1.2, 1, 1, 1, 1, 1], gap="small")
with cols[0]:
    firm = st.selectbox(
        "Focus firm", firms, key="firm", bind="query-params", persist_state="session"
    )
    status = analyses.momentum_status(stats, firm)
    if status:
        label, color, icon = status
        st.badge(
            label,
            color=color,
            icon=icon,
            help="Where the firm sits on the momentum map",
        )
    rank = int(stats.loc[firm, "rank_last"]) if firm in stats.index else None
    if rank:
        st.caption(
            f"Ranked {rank} of {len(BROKER_FIRMS)} national firms by plans served in {f.end}."
        )
kpis.render(kpis.broker(stats, firm, f), cols[1:])

left, right = st.columns([5.5, 6.5], gap="large")
with left:
    view = st.segmented_control(
        "View",
        ["Momentum", "Wins and losses"],
        default="Momentum",
        required=True,
        key="broker_view",
        label_visibility="collapsed",
        bind="query-params",
        persist_state="session",
    )
    if view == "Wins and losses":
        panel(
            analyses.win_loss(t, f, firm, height=440),
            key=f"wins_{firm}",
            on_click=_focus,
        )
    else:
        panel(
            analyses.momentum_map(t, f, firm, height=440),
            key=f"momentum_{firm}",
            on_click=_focus,
        )
with right:
    st.space("medium")  # line up with the view switch on the left
    panel(
        analyses.leaderboard(t, f, firm, height=440),
        key=f"bump_{firm}",
        on_click=_focus,
    )
