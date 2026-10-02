"""Header, filters and chart panels shared by every page."""

from collections.abc import Callable
from datetime import date

import streamlit as st

from figures import calls
from figures.analyses import Chart
from figures.data import FIRST, LAST, SECTORS, STATE_NAMES, YEARS, Filters
from figures.theme import PLOTLY_CONFIG

ALL = "ALL"
FILTER_DEFAULTS = {"years": (FIRST, LAST), "industry": ALL, "state": ALL}
LINK_OFFSET = 15

REPO = "https://github.com/coreymichaud/benefits-market-intelligence/blob/main/docs"

DATA_NOTES = f"""
**Source.** Department of Labor Form 5500 filings for form years {FIRST} to {LAST}: the main
form, Schedule A (insurance contracts, commissions and fees) and Schedule C Part 1 Item 2
(service providers). Nothing else is used.

**Preparation**
- Filings received more than 9.5 months after plan year end are excluded, so every year is
  measured on the same filing window (the 7-month deadline plus the 2.5-month extension).
- One filing per sponsor EIN, plan number and year, keeping the latest submission.
- Contracts with negative amounts, fewer than 1 or more than 1M covered lives, or more than
  \\$2,500 of broker pay per covered life are dropped.
- Take rate also drops unclassified contracts and contracts with no premium, premium above
  \\$50K per life or \\$250M in total, or broker pay above 100% of premium.
- A blank commission or fee counts as \\$0. Take rate and fee adoption can leave those
  contracts out instead.

**Caveats**
- Covered lives can include dependents, so per-life figures are per person, not per employee.
- Small fully insured plans are generally exempt from filing, and small plans that file the
  short Form 5500-SF aren't loaded, so the data describes the large-group market.
- Contracts with a policy year under 12 months are counted as reported, never annualized.
- Broker firms are matched by name on Schedule C, which only large plans file. A switch from a
  local broker to a national firm can reflect an acquisition rather than a competitive win.

More: [assumptions]({REPO}/assumptions.md), [name matching]({REPO}/name-matching.md),
[sources]({REPO}/sources.md).
"""


def _keep_range() -> None:
    # A single year has nothing to compare against, so widen it
    start, end = st.session_state["years"]
    if start == end:
        st.session_state["years"] = (start, end + 1) if end < LAST else (start - 1, end)


def _reset() -> None:
    for key, value in FILTER_DEFAULTS.items():
        st.session_state[key] = value
    st.session_state["lines"] = []


def header(pages: list, show_years: bool = True) -> Filters:
    """App name and page links on the left, global filters on the right."""
    brand, years, industry, state, buttons = st.columns(
        [4.8, 1.35, 1.2, 1.0, 1.0], vertical_alignment="center", gap="medium"
    )
    with years:
        # Always drawn so the selection survives a visit to a page that ignores it
        start, end = st.select_slider(
            "Form years",
            options=YEARS,
            value=FILTER_DEFAULTS["years"],
            key="years",
            on_change=_keep_range,
            bind="query-params",
            label_visibility="collapsed",
            disabled=not show_years,
            help=None if show_years else "Accounts uses each plan's latest filing",
        )
    with industry:
        sector = st.selectbox(
            "Industry",
            [ALL, *SECTORS],
            key="industry",
            format_func=lambda s: "All industries" if s == ALL else s,
            bind="query-params",
            label_visibility="collapsed",
        )
    with state:
        code = st.selectbox(
            "State",
            [ALL, *sorted(STATE_NAMES, key=STATE_NAMES.get)],
            key="state",
            format_func=lambda s: "All states" if s == ALL else STATE_NAMES[s],
            bind="query-params",
            label_visibility="collapsed",
        )
    # Sized to their icons rather than to a column share, so they keep their shape on any width
    with (
        buttons,
        st.container(
            horizontal=True, gap="small", horizontal_alignment="right", wrap=False
        ),
    ):
        st.button(
            "",
            icon=":material/restart_alt:",
            help="Reset filters",
            on_click=_reset,
            width="content",
        )
        with st.popover(
            "", icon=":material/info:", help="About the data", width="content"
        ):
            st.markdown(DATA_NOTES)

    f = Filters(
        start=start,
        end=end,
        industry=None if sector == ALL else sector,
        state=None if code == ALL else code,
    )
    with (
        brand,
        st.container(horizontal=True, vertical_alignment="top", gap="medium"),
    ):
        st.title(
            "Benefits Market Intelligence",
            icon=":material/person:",
            anchor=False,
            width="content",
        )
        # Drop the links so they sit level with the middle of the title's lowercase letters.
        # Tuned for the 2.45rem title: raise it with a bigger title, lower it with a smaller one.
        with st.container(gap=0, width="content"):
            st.space(LINK_OFFSET)
            with st.container(horizontal=True, gap="medium", width="content"):
                for page in pages:
                    st.page_link(page)
    return f


def freshness(latest_received: date) -> None:
    """One line saying how current the filings are."""
    st.caption(
        f"Form years {FIRST} to {LAST}, using filings DOL had received by "
        f"{latest_received:%B} {latest_received.day}, {latest_received.year}."
    )


def filters() -> Filters:
    """The active filters, for use inside a page after the header has run."""
    start, end = st.session_state.get("years", FILTER_DEFAULTS["years"])
    sector = st.session_state.get("industry", ALL)
    code = st.session_state.get("state", ALL)
    return Filters(
        start, end, None if sector == ALL else sector, None if code == ALL else code
    )


def panel(
    chart: Chart,
    key: str,
    on_click: Callable[[dict], None] | None = None,
    call: str | None = None,
) -> None:
    """Headline, call badges, caption and chart. `on_click` receives the clicked point."""
    st.subheader(chart.headline, anchor=False)
    if call:
        calls.show(call, filters())
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


def view_switch(options: list[str], key: str) -> str:
    """Segmented control that swaps the chart in a panel."""
    return st.segmented_control(
        "View",
        options,
        default=options[0],
        required=True,
        key=key,
        label_visibility="collapsed",
        bind="query-params",
        persist_state="session",
    )


def toggle_filter(key: str, value: str) -> None:
    """Clicking the active item clears the filter; clicking another switches to it."""
    st.session_state[key] = ALL if st.session_state.get(key) == value else value