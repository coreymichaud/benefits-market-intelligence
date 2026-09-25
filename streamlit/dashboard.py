import streamlit as st

from figures.analyses import (
    carrier_share_chart,
    commission_intensity_chart,
    commission_outlier_chart,
    load_data,
    plan_size_sankey,
)
from figures.kpis import (
    calculate_kpis,
    render_kpi_cards,
)


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
    st.metric(
        "Analysis year",
        "2023",
    )


st.divider()


# ---------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------

render_kpi_cards(st, kpis)


st.divider()


# ---------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------

left, right = st.columns(2, gap="medium")

with left:
    st.subheader("Commission intensity")
    st.plotly_chart(
        commission_intensity_chart(
            data,
            height=285,
        ),
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

with right:
    st.subheader("Carrier premium-share movement")
    st.plotly_chart(
        carrier_share_chart(
            data,
            height=285,
        ),
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


left, right = st.columns(2, gap="medium")

with left:
    st.subheader("Commission outliers")
    st.plotly_chart(
        commission_outlier_chart(
            data,
            height=285,
        ),
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )

with right:
    st.subheader("Plan-size transitions")
    st.plotly_chart(
        plan_size_sankey(
            data,
            height=285,
        ),
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


# ---------------------------------------------------------------------
# Methodology note
# ---------------------------------------------------------------------

st.caption(
    "Methodology: Core commission rate excludes flagged Schedule A rows. "
    "Flagged contracts use the analysis notebook's year-specific 3×IQR "
    "commission outlier rule. Plan-size transitions include plans observed "
    "in both 2022 and 2023."
)
