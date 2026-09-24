import numpy as np
import pandas as pd

from .analyses import money


def calculate_kpis(data, year=2023):
    """
    Calculate the dashboard KPIs using the same definitions
    established in the analysis notebook.
    """

    valid_base = data["valid_base"]
    core = data["core"]
    plans = data["plans"]

    # -------------------------------------------------------------
    # Core commission / premium rate
    # -------------------------------------------------------------

    year_core = core[
        core["FORM_YEAR"] == year
    ].copy()

    core_premium = year_core[
        "reported_premium"
    ].sum()

    core_commission = year_core[
        "commission"
    ].sum()

    core_rate = (
        core_commission / core_premium
        if core_premium > 0
        else np.nan
    )

    # -------------------------------------------------------------
    # Raw reported totals
    # -------------------------------------------------------------

    year_valid = valid_base[
        valid_base["FORM_YEAR"] == year
    ].copy()

    reported_premium = year_valid[
        "reported_premium"
    ].sum()

    reported_commission = year_valid[
        "commission"
    ].sum()

    reported_rate = (
        reported_commission / reported_premium
        if reported_premium > 0
        else np.nan
    )

    # -------------------------------------------------------------
    # Participants
    # -------------------------------------------------------------

    year_plans = plans[
        plans["FORM_YEAR"] == year
    ].copy()

    participants = year_plans[
        "TOT_PARTCP_BOY_CNT"
    ].sum(min_count=1)

    # -------------------------------------------------------------
    # Suspected contracts
    # -------------------------------------------------------------

    year_suspect = data["valid"][
        (data["valid"]["FORM_YEAR"] == year)
        & (data["valid"]["suspect"])
    ].copy()

    flagged_contracts = len(year_suspect)

    total_contracts = len(
        data["valid"][
            data["valid"]["FORM_YEAR"] == year
        ]
    )

    flagged_share = (
        flagged_contracts / total_contracts
        if total_contracts > 0
        else np.nan
    )

    # -------------------------------------------------------------
    # Median plan rate
    # -------------------------------------------------------------

    plan_contracts = data["plan_contracts"]

    year_plan_rates = plan_contracts[
        (plan_contracts["FORM_YEAR"] == year)
        & (
            plan_contracts[
                "suspect_commission"
            ] == 0
        )
    ].copy()

    median_plan_rate = (
        year_plan_rates["commission_rate"]
        .median()
        if not year_plan_rates.empty
        else np.nan
    )

    p90_plan_rate = (
        year_plan_rates["commission_rate"]
        .quantile(0.90)
        if not year_plan_rates.empty
        else np.nan
    )

    return {
        "year": year,
        "core_rate": core_rate,
        "core_rate_pct": core_rate * 100
        if pd.notna(core_rate)
        else np.nan,
        "core_premium": core_premium,
        "core_commission": core_commission,
        "reported_premium": reported_premium,
        "reported_commission": reported_commission,
        "reported_rate": reported_rate,
        "reported_rate_pct": reported_rate * 100
        if pd.notna(reported_rate)
        else np.nan,
        "participants": participants,
        "flagged_contracts": flagged_contracts,
        "total_contracts": total_contracts,
        "flagged_share": flagged_share,
        "flagged_share_pct": flagged_share * 100
        if pd.notna(flagged_share)
        else np.nan,
        "median_plan_rate": median_plan_rate,
        "median_plan_rate_pct": median_plan_rate * 100
        if pd.notna(median_plan_rate)
        else np.nan,
        "p90_plan_rate": p90_plan_rate,
        "p90_plan_rate_pct": p90_plan_rate * 100
        if pd.notna(p90_plan_rate)
        else np.nan,
    }


def render_kpi_cards(st, kpis):
    """
    Render the five KPI cards used by dashboard.py.

    The function takes Streamlit as an argument so kpis.py
    remains independent of the Streamlit page itself.
    """

    cards = [
        (
            "Core commission rate",
            (
                f"{kpis['core_rate_pct']:.2f}%"
                if pd.notna(kpis["core_rate_pct"])
                else "—"
            ),
            "Commission / premium",
        ),
        (
            "Reported premium",
            money(kpis["reported_premium"]),
            "2023 Schedule A",
        ),
        (
            "Reported commission",
            money(kpis["reported_commission"]),
            "2023 Schedule A",
        ),
        (
            "Participants",
            (
                f"{kpis['participants']:,.0f}"
                if pd.notna(kpis["participants"])
                else "—"
            ),
            "Beginning-of-year count",
        ),
        (
            "Flagged contracts",
            (
                f"{kpis['flagged_contracts']:,}"
                if pd.notna(kpis["flagged_contracts"])
                else "—"
            ),
            (
                f"{kpis['flagged_share_pct']:.1f}% of "
                f"{kpis['total_contracts']:,}"
                if pd.notna(kpis["flagged_share_pct"])
                else "—"
            ),
        ),
    ]

    cols = st.columns(5)

    for col, (label, value, detail) in zip(
        cols,
        cards,
    ):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-detail">{detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )