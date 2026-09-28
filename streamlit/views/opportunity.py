"""Opportunity: where broker pay is growing, and the plan design shifts behind it."""

import streamlit as st

from figures import analyses
from figures.data import load
from figures.layout import filters, panel, toggle_filter

t = load()
f = filters()


def _pick_state(point: dict) -> None:
    code = point.get("location")
    if code:
        toggle_filter("state", code)


def _pick_industry(point: dict) -> None:
    sector = point.get("customdata")
    if sector:
        toggle_filter("industry", sector)


top_left, top_right = st.columns(2, gap="large")
with top_left:
    panel(
        analyses.state_map(t, f, height=330),
        key=f"map_{f.state}_{f.industry}",
        on_click=_pick_state,
    )
with top_right:
    panel(
        analyses.industries(t, f, height=330),
        key=f"industries_{f.industry}_{f.state}",
        on_click=_pick_industry,
    )

bottom_left, bottom_right = st.columns(2, gap="large")
with bottom_left:
    panel(analyses.self_funding(t, f, height=245), key="self_funding")
with bottom_right:
    panel(analyses.voluntary(t, f, height=245), key="voluntary")
