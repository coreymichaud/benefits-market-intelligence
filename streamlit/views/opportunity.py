"""Opportunity: where broker pay is growing, and how employers are changing what they buy."""

import streamlit as st

from figures import analyses, kpis
from figures.data import load
from figures.layout import filters, panel, toggle_filter, view_switch

HEIGHT = 450

t = load()
f = filters()


def _pick_state(point: dict) -> None:
    if point.get("location"):
        toggle_filter("state", point["location"])


def _pick_industry(point: dict) -> None:
    if point.get("customdata"):
        toggle_filter("industry", point["customdata"])


kpis.render(kpis.opportunity(t, f))

left, right = st.columns([7, 5], gap="large")
with left:
    where = view_switch(["States", "Industries"], key="where_view")
    if where == "Industries":
        panel(
            analyses.industries(t, f, height=HEIGHT),
            key=f"industries_{f.industry}_{f.state}",
            on_click=_pick_industry,
            call="markets",
        )
    else:
        panel(
            analyses.state_map(t, f, height=HEIGHT),
            key=f"map_{f.state}_{f.industry}",
            on_click=_pick_state,
            call="markets",
        )
with right:
    buying = view_switch(["Self-funding", "Voluntary benefits"], key="design_view")
    if buying == "Voluntary benefits":
        panel(
            analyses.voluntary(t, f, height=HEIGHT), key="voluntary", call="voluntary"
        )
    else:
        panel(
            analyses.self_funding(t, f, height=HEIGHT),
            key="self_funding",
            call="self_funding",
        )
