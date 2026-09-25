import streamlit as st

from figures.analyses import (
    available_years,
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

# Tightened spacing so the page fits on one screen without scrolling.
st.markdown(
    """
    <style>
        .block-container { padding-top: 1.6rem; padding-bottom: 1rem; }
        h3 { margin-top: 0.2rem !important; margin-bottom: 0.4rem !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 1.2rem; }
        hr { margin: 0.6rem 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------

data = load_data()
years = available_years(data)  # latest first
if not years:
    st.error("No plan years found in the loaded data.")
    st.stop()


# ---------------------------------------------------------------------
# Header + year selector
# ---------------------------------------------------------------------

title_col, year_col = st.columns([5, 1])

with title_col:
    st.title("Benefits Market Intelligence")
    st.caption(
        "ERISA Form 5500 market view · premium, broker compensation, "
        "plan scale, and carrier dynamics"
    )

with year_col:
    selected_year = st.selectbox("Analysis year", years, index=0)

kpis = calculate_kpis(data, year=selected_year)

st.divider()


# ---------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------

render_kpi_cards(st, kpis)

st.divider()


# ---------------------------------------------------------------------
# Main analysis
#
# One full-width trend covering every year in the data, plus two
# secondary views in tabs (rather than stacked) so the page stays on
# one screen regardless of how many years are loaded.
# ---------------------------------------------------------------------

CHART_CONFIG = {"displayModeBar": False, "responsive": True}

st.markdown("##### Commission intensity, all years")
st.plotly_chart(
    commission_intensity_chart(data, height=260),
    use_container_width=True,
    config=CHART_CONFIG,
)

first_year, last_year = years[-1], years[0]
prior_year = years[1] if len(years) > 1 else last_year

tab_carriers, tab_plan_size = st.tabs(["Carrier premium share", "Plan-size transitions"])

with tab_carriers:
    st.plotly_chart(
        carrier_share_chart(data, year_from=first_year, year_to=last_year, height=260),
        use_container_width=True,
        config=CHART_CONFIG,
    )

with tab_plan_size:
    st.plotly_chart(
        plan_size_sankey(data, year_from=prior_year, year_to=last_year, height=260),
        use_container_width=True,
        config=CHART_CONFIG,
    )


# ---------------------------------------------------------------------
# Methodology note
# ---------------------------------------------------------------------

st.caption(
    f"Methodology: Core commission rate excludes flagged Schedule A rows. Flagged contracts use "
    f"a year-specific 3×IQR commission outlier rule on rows with positive premium and "
    f"non-negative commission. Carrier share compares {first_year} to {last_year}; "
    f"plan-size transitions compare {prior_year} to {last_year}."
)