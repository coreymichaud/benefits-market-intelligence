"""Brokers: who is climbing, who is slipping, and how each firm wins and keeps clients."""

import streamlit as st

from figures import analyses, kpis
from figures.data import BROKER_FIRMS, load
from figures.layout import filters, panel, view_switch

HEIGHT = 460

t = load()
f = filters()
stats = analyses.firm_stats(t, f)

# Firms present in the current slice, leaders first. The focus defaults to the leader.
firms = (
    stats.index[(stats["plans_last"] > 0) | (stats["plans_first"] > 0)].tolist()
    if len(stats)
    else []
)
firms = firms or list(BROKER_FIRMS)
if st.session_state.get("firm") not in firms:
    st.session_state["firm"] = firms[0]


def _focus(point: dict) -> None:
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
    if firm in stats.index:
        rank = int(stats.loc[firm, "rank_last"])
        st.caption(
            f"Ranked {rank} of {len(BROKER_FIRMS)} national firms by plans served in {f.end}."
        )
    # The provider names that count toward this firm, so a reader can check the matching
    names = t.firm_names[t.firm_names["firm"] == firm].nlargest(12, "plan_years")
    with st.popover("Names counted", icon=":material/badge:", width="content"):
        st.caption(
            f"Schedule C provider names matched to {firm}, 2019-2024, by plan-years. "
            "Rules and exclusions: docs/name-matching.md."
        )
        st.dataframe(
            names[["provider", "plan_years"]],
            hide_index=True,
            column_config={
                "provider": st.column_config.TextColumn("Name on the filing"),
                "plan_years": st.column_config.NumberColumn("Plan-years", format="%d"),
            },
        )
kpis.render(kpis.broker(stats, firm, f), cols[1:])

left, right = st.columns([5.5, 6.5], gap="large")
with left:
    view = view_switch(["Momentum", "Wins and losses"], key="broker_view")
    if view == "Wins and losses":
        panel(
            analyses.win_loss(t, f, firm, height=HEIGHT),
            key=f"wins_{firm}",
            on_click=_focus,
            call="consolidators",
        )
    else:
        panel(
            analyses.momentum_map(t, f, firm, height=HEIGHT),
            key=f"momentum_{firm}",
            on_click=_focus,
            call="consolidators",
        )
with right:
    st.space(28)  # lines the headline up with the one under the view switch
    panel(
        analyses.leaderboard(t, f, firm, height=HEIGHT),
        key=f"bump_{firm}",
        on_click=_focus,
    )
