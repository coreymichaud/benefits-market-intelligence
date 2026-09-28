"""Page chrome shared by every page: the header with global filters, and chart panels.

Global filters live in `app.py` (the entrypoint runs on every page), so their values carry across
pages and are mirrored in the URL. Any view can be shared as a link.
"""

from collections.abc import Callable

import streamlit as st

from figures.analyses import Chart
from figures.data import FIRST, LAST, SECTORS, STATE_NAMES, YEARS, Filters
from figures.theme import PLOTLY_CONFIG

ALL = "ALL"
FILTER_DEFAULTS = {"years": (FIRST, LAST), "industry": ALL, "state": ALL}

DATA_NOTES = f"""
**Source.** Department of Labor Form 5500 filings for plan years {FIRST}–{LAST}: the main form,
Schedule A (insurance contracts, commissions and fees) and Schedule C Part I (service providers).

**How the data is prepared**
- Filings received more than 9.5 months after plan year end are excluded, so every year is
  measured on the same filing window (the 7-month deadline plus the 2.5-month extension).
- One filing per sponsor EIN, plan number and year, keeping the latest submission.
- Contracts with negative amounts, fewer than 1 or more than 1M covered lives, or more than
  \\$2,500 of broker pay per covered life are dropped.
- Take rate also drops contracts with premium above \\$50K per life, broker pay above 100% of
  premium, or more than \\$250M premium.

**Keep in mind**
- Covered lives can include dependents, so per-life figures are per person, not per employee.
- Small fully insured plans file the short-form 5500-SF and are mostly absent.
- Broker firms are identified by matching provider names on Schedule C, which only large plans
  (generally 100+ participants) file. A switch from a local broker to a national firm can
  reflect an acquisition rather than a competitive win.
"""


def _keep_range() -> None:
    """A single-year range has no trend to show, so widen it by one year."""
    start, end = st.session_state["years"]
    if start == end:
        st.session_state["years"] = (start, end + 1) if end < LAST else (start - 1, end)


def _reset() -> None:
    for key, value in FILTER_DEFAULTS.items():
        st.session_state[key] = value
    st.session_state["lines"] = []  # the Market page's line-of-coverage filter


def header(title: str, dek: str) -> Filters:
    """Title on the left, global filters on the right. Returns the active filters.

    Labels are collapsed to keep the header to one line: the widgets read "2019 ... 2024",
    "All industries" and "All states", and each has a tooltip.
    """
    left, years, industry, state, reset, notes = st.columns(
        [3.1, 1.5, 1.3, 1.1, 0.26, 0.26], vertical_alignment="center", gap="medium"
    )
    with left:
        st.title(title, anchor=False, help=dek)
    with years:
        start, end = st.select_slider(
            "Plan years",
            options=YEARS,
            value=FILTER_DEFAULTS["years"],
            key="years",
            on_change=_keep_range,
            bind="query-params",
            label_visibility="collapsed",
        )
    with industry:
        sector = st.selectbox(
            "Industry",
            [ALL] + SECTORS,
            key="industry",
            format_func=lambda s: "All industries" if s == ALL else s,
            bind="query-params",
            label_visibility="collapsed",
        )
    with state:
        code = st.selectbox(
            "State",
            [ALL] + sorted(STATE_NAMES, key=STATE_NAMES.get),
            key="state",
            format_func=lambda s: "All states" if s == ALL else STATE_NAMES[s],
            bind="query-params",
            label_visibility="collapsed",
        )
    with reset:
        st.button(
            "",
            icon=":material/restart_alt:",
            help="Reset filters",
            on_click=_reset,
            width="stretch",
        )
    with (
        notes,
        st.popover("", icon=":material/info:", help="About the data", width="stretch"),
    ):
        st.markdown(DATA_NOTES)
    return Filters(
        start=start,
        end=end,
        industry=None if sector == ALL else sector,
        state=None if code == ALL else code,
    )


def filters() -> Filters:
    """Read the active filters inside a page (the header has already rendered them)."""
    start, end = st.session_state.get("years", FILTER_DEFAULTS["years"])
    sector = st.session_state.get("industry", ALL)
    code = st.session_state.get("state", ALL)
    return Filters(
        start, end, None if sector == ALL else sector, None if code == ALL else code
    )


def panel(
    chart: Chart, key: str, on_click: Callable[[dict], None] | None = None
) -> None:
    """Headline, caption and chart. `on_click` receives the first clicked point."""
    st.subheader(chart.headline, anchor=False)
    if chart.caption:
        st.caption(chart.caption)

    def _handle() -> None:
        points = st.session_state[key].selection.get("points", [])
        if points and on_click:
            on_click(points[0])

    st.plotly_chart(
        chart.figure,
        key=key,
        on_select=_handle if on_click else "ignore",
        selection_mode="points",
        config=PLOTLY_CONFIG,
        theme=None,
    )


def toggle_filter(key: str, value: str) -> None:
    """Click a filtered item again to clear it, or a new one to switch to it."""
    st.session_state[key] = ALL if st.session_state.get(key) == value else value
