import streamlit as st

from figures.analyses import (
    carrier_share_chart,
    commission_intensity_chart,
    load_data,
    plan_size_sankey,
)
from figures.kpis import calculate_kpis, render_kpi_cards


# ---------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Benefits Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------

data = load_data()
kpis = calculate_kpis(data, year=2023)


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

title_col, year_col = st.columns([5, 1])

with title_col:
    st.title("Benefits Market Intelligence")
    st.caption(
        "ERISA Form 5500 market view · premium, broker compensation, "
        "plan scale, and carrier dynamics"
    )

with year_col:
    st.metric("Analysis year", str(kpis["year"]))

st.divider()


# ---------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------

render_kpi_cards(st, kpis)

st.divider()


# ---------------------------------------------------------------------
# Main analysis — 3 charts: one headline trend, two side by side
# ---------------------------------------------------------------------

CHART_CONFIG = {"displayModeBar": False, "responsive": True}

st.subheader("Commission intensity")
st.plotly_chart(
    commission_intensity_chart(data, height=300),
    use_container_width=True,
    config=CHART_CONFIG,
)

left, right = st.columns(2, gap="medium")

with left:
    st.subheader("Carrier premium-share movement")
    st.plotly_chart(
        carrier_share_chart(data, height=280),
        use_container_width=True,
        config=CHART_CONFIG,
    )

with right:
    st.subheader("Plan-size transitions")
    st.plotly_chart(
        plan_size_sankey(data, height=280),
        use_container_width=True,
        config=CHART_CONFIG,
    )


# ---------------------------------------------------------------------
# Methodology note
# ---------------------------------------------------------------------

st.caption(
    "Methodology: Core commission rate excludes flagged Schedule A rows. "
    "Flagged contracts use a year-specific 3×IQR commission outlier rule, "
    "applied to rows with positive premium and non-negative commission. "
    "Plan-size transitions include plans observed in both 2022 and 2023."
)