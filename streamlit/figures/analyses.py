import warnings

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from benefits_market_intelligence.config.paths import EXPORTS_PATH

warnings.filterwarnings("ignore", category=FutureWarning)

ACCENT = "#1f77b4"
MUTED = "#7f8c8d"
GOOD = "#2ca02c"
DARK = "#243447"


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def money(v, decimals=1):
    if pd.isna(v):
        return "—"

    sign = "-" if v < 0 else ""
    v = abs(float(v))

    if v >= 1_000_000_000:
        return f"{sign}${v / 1_000_000_000:.{decimals}f}B"
    if v >= 1_000_000:
        return f"{sign}${v / 1_000_000:.{decimals}f}M"
    if v >= 1_000:
        return f"{sign}${v / 1_000:.{decimals}f}K"

    return f"{sign}${v:,.0f}"


def style(fig, title, subtitle=None, height=300):
    title_text = title if not subtitle else f"{title}<br><sup>{subtitle}</sup>"

    fig.update_layout(
        template="plotly_white",
        title={"text": title_text, "x": 0.01, "xanchor": "left", "font": {"size": 16}},
        height=height,
        margin=dict(l=45, r=20, t=65, b=40),
        font=dict(family="Arial, sans-serif", color=DARK),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1, font=dict(size=9)
        ),
        hoverlabel=dict(bgcolor="white"),
    )

    return fig


def num(df, cols):
    """Coerce to numeric, downcasting to float32 where possible to cut memory roughly in half."""

    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce", downcast="float")

    return df


def clean_text(s, fallback="Not reported"):
    out = s.astype("string").str.strip()

    out = out.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "<NA>": pd.NA})

    return out.fillna(fallback)


# ---------------------------------------------------------------------
# Data loading
#
# Only the columns this dashboard actually renders are read from disk,
# and SCH_C is skipped entirely — nothing on this page uses it. On
# Streamlit Community Cloud (limited RAM), this is the single biggest
# lever: reading every column of three 40-60MB parquet files as
# float64/object can blow well past the memory ceiling before a single
# chart is drawn.
# ---------------------------------------------------------------------


@st.cache_data(show_spinner="Loading Form 5500 data…")
def load_data():
    f_5500 = pd.read_parquet(
        EXPORTS_PATH / "F_5500.parquet",
        columns=["SPONS_DFE_EIN", "SPONS_DFE_PN", "ACK_ID", "FORM_YEAR", "TOT_PARTCP_BOY_CNT"],
    )

    sch_a = pd.read_parquet(
        EXPORTS_PATH / "SCH_A.parquet",
        columns=[
            "ACK_ID",
            "FORM_YEAR",
            "INS_CARRIER_NAME",
            "PENSION_PREM_PAID_TOT_AMT",
            "WLFR_PREMIUM_RCVD_AMT",
            "INS_BROKER_COMM_TOT_AMT",
        ],
    )

    f_5500 = num(f_5500, ["TOT_PARTCP_BOY_CNT"])
    sch_a = num(
        sch_a, ["PENSION_PREM_PAID_TOT_AMT", "WLFR_PREMIUM_RCVD_AMT", "INS_BROKER_COMM_TOT_AMT"]
    )

    for df in (f_5500, sch_a):
        df["FORM_YEAR"] = pd.to_numeric(df["FORM_YEAR"], errors="coerce").astype("Int64")

    f_5500["SPONS_DFE_EIN"] = clean_text(f_5500["SPONS_DFE_EIN"], fallback="")
    f_5500["SPONS_DFE_PN"] = clean_text(f_5500["SPONS_DFE_PN"], fallback="")
    f_5500["ACK_ID"] = clean_text(f_5500["ACK_ID"], fallback="")

    f_5500["plan_key"] = np.where(
        (f_5500["SPONS_DFE_EIN"] != "") & (f_5500["SPONS_DFE_PN"] != ""),
        f_5500["SPONS_DFE_EIN"] + "|" + f_5500["SPONS_DFE_PN"],
        f_5500["ACK_ID"],
    )

    sch_a["ACK_ID"] = clean_text(sch_a["ACK_ID"], fallback="")
    sch_a["carrier"] = clean_text(sch_a["INS_CARRIER_NAME"]).astype("category")

    plans = f_5500.drop_duplicates(["plan_key", "FORM_YEAR"])[
        ["plan_key", "ACK_ID", "FORM_YEAR", "TOT_PARTCP_BOY_CNT"]
    ].copy()

    sch_a["reported_premium"] = sch_a["WLFR_PREMIUM_RCVD_AMT"].fillna(0) + sch_a[
        "PENSION_PREM_PAID_TOT_AMT"
    ].fillna(0)
    sch_a["commission"] = sch_a["INS_BROKER_COMM_TOT_AMT"].fillna(0)

    # -------------------------------------------------------------
    # Outlier logic: year-specific 3xIQR commission rule, applied to
    # rows with positive premium and non-negative commission.
    # -------------------------------------------------------------

    valid_base = sch_a[(sch_a["reported_premium"] > 0) & (sch_a["commission"] >= 0)].copy()

    fences = (
        valid_base.groupby("FORM_YEAR")["commission"]
        .agg(q1=lambda s: s.quantile(0.25), q3=lambda s: s.quantile(0.75))
        .assign(iqr=lambda d: d["q3"] - d["q1"], fence=lambda d: d["q3"] + 3 * d["iqr"])
    )

    valid_base = valid_base.merge(
        fences["fence"], left_on="FORM_YEAR", right_index=True, how="left"
    )
    valid_base["suspect"] = valid_base["commission"] > valid_base["fence"]

    plan_contracts = valid_base.groupby(["ACK_ID", "FORM_YEAR"], as_index=False).agg(
        reported_premium=("reported_premium", "sum"),
        reported_commission=("commission", "sum"),
        suspect_commission=("suspect", "sum"),
    )
    plan_contracts["commission_rate"] = np.where(
        plan_contracts["reported_premium"] > 0,
        plan_contracts["reported_commission"] / plan_contracts["reported_premium"],
        np.nan,
    )

    core = valid_base[~valid_base["suspect"]].copy()

    core_annual = core.groupby("FORM_YEAR", as_index=False).agg(
        core_premium=("reported_premium", "sum"), core_commission=("commission", "sum")
    )
    core_annual["core_weighted_rate"] = core_annual["core_commission"] / core_annual["core_premium"]

    raw_annual = valid_base.groupby("FORM_YEAR", as_index=False).agg(
        reported_premium=("reported_premium", "sum"), reported_commission=("commission", "sum")
    )
    raw_annual["reported_weighted_rate"] = (
        raw_annual["reported_commission"] / raw_annual["reported_premium"]
    )

    plan_rate = (
        plan_contracts.loc[plan_contracts["suspect_commission"] == 0]
        .groupby("FORM_YEAR")["commission_rate"]
        .median()
        .reset_index(name="median_plan_rate")
    )

    trend = (
        raw_annual.merge(
            core_annual[["FORM_YEAR", "core_weighted_rate"]], on="FORM_YEAR", how="outer"
        )
        .merge(plan_rate, on="FORM_YEAR", how="left")
        .sort_values("FORM_YEAR")
    )

    return {
        "SCH_A": sch_a,
        "plans": plans,
        "valid_base": valid_base,
        "core": core,
        "plan_contracts": plan_contracts,
        "trend": trend,
    }


# ---------------------------------------------------------------------
# Chart 1 — Commission intensity
# ---------------------------------------------------------------------


def commission_intensity_chart(data, height=300):
    trend = data["trend"]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=trend["FORM_YEAR"],
            y=trend["reported_weighted_rate"] * 100,
            mode="lines+markers",
            name="Reported",
            line=dict(color=MUTED, dash="dot", width=2),
            hovertemplate="Year %{x}<br>Reported rate %{y:.2f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=trend["FORM_YEAR"],
            y=trend["core_weighted_rate"] * 100,
            mode="lines+markers",
            name="Core",
            line=dict(color=ACCENT, width=3),
            hovertemplate="Year %{x}<br>Core rate %{y:.2f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=trend["FORM_YEAR"],
            y=trend["median_plan_rate"] * 100,
            mode="lines+markers",
            name="Median plan",
            line=dict(color=GOOD, width=2),
            hovertemplate="Year %{x}<br>Median plan rate %{y:.2f}%<extra></extra>",
        )
    )

    fig.update_yaxes(title="Commission / premium (%)", tickformat=".1f")
    fig.update_xaxes(dtick=1, title="")

    return style(
        fig,
        "Commission intensity over time",
        "Core rate excludes flagged Schedule A rows.",
        height=height,
    )


# ---------------------------------------------------------------------
# Chart 2 — Carrier share slopegraph
# ---------------------------------------------------------------------


def carrier_share_chart(data, height=280):
    sch_a = data["SCH_A"]

    carrier_year = sch_a.groupby(["FORM_YEAR", "carrier"], as_index=False, observed=True).agg(
        premium=("reported_premium", "sum")
    )
    carrier_year = carrier_year[carrier_year["premium"] > 0]

    carrier_year["share"] = carrier_year["premium"] / carrier_year.groupby("FORM_YEAR")[
        "premium"
    ].transform("sum")

    latest = carrier_year[carrier_year["FORM_YEAR"] == 2023].nlargest(8, "premium")["carrier"]

    compare = carrier_year[
        carrier_year["FORM_YEAR"].isin([2019, 2023]) & carrier_year["carrier"].isin(latest)
    ]

    wide = compare.pivot(index="carrier", columns="FORM_YEAR", values="share").dropna().reset_index()

    if wide.empty:
        return go.Figure()

    wide = wide.sort_values(2023, ascending=False)

    fig = go.Figure()
    for _, row in wide.iterrows():
        carrier = row["carrier"]
        fig.add_trace(
            go.Scatter(
                x=[2019, 2023],
                y=[row[2019] * 100, row[2023] * 100],
                mode="lines+markers",
                name=str(carrier),
                line=dict(width=2),
                marker=dict(size=7),
                hovertemplate=f"{carrier}<br>%{{x}}: %{{y:.2f}}%<extra></extra>",
            )
        )

    fig.update_xaxes(range=[2018.6, 2023.4], tickvals=[2019, 2023], title="")
    fig.update_yaxes(title="Premium share (%)", ticksuffix="%", rangemode="tozero")
    fig.update_layout(showlegend=False)

    return style(
        fig,
        "Carrier premium-share movement",
        "Top eight carriers by 2023 reported premium.",
        height=height,
    )


# ---------------------------------------------------------------------
# Chart 3 — Plan-size Sankey
# ---------------------------------------------------------------------


def plan_size_sankey(data, height=280):
    plans = data["plans"]

    size_bins = [-np.inf, 99, 499, 999, 4_999, 9_999, np.inf]
    size_labels = ["<100", "100–499", "500–999", "1k–4.9k", "5k–9.9k", "10k+"]

    plan_size = plans[["plan_key", "FORM_YEAR", "TOT_PARTCP_BOY_CNT"]]
    plan_size = plan_size[
        plan_size["TOT_PARTCP_BOY_CNT"].notna() & (plan_size["TOT_PARTCP_BOY_CNT"] >= 0)
    ]

    plan_size = plan_size.assign(
        size_bucket=pd.cut(plan_size["TOT_PARTCP_BOY_CNT"], bins=size_bins, labels=size_labels)
    )

    base = (
        plan_size[plan_size["FORM_YEAR"].isin([2022, 2023])]
        .pivot(index="plan_key", columns="FORM_YEAR", values="size_bucket")
        .dropna()
    )

    if base.empty:
        return go.Figure()

    transitions = base.reset_index().rename(columns={2022: "from", 2023: "to"})

    links = (
        transitions.groupby(["from", "to"], observed=True).size().reset_index(name="plans")
    )

    left_nodes = [f"2022 | {x}" for x in size_labels]
    right_nodes = [f"2023 | {x}" for x in size_labels]
    node_labels = left_nodes + right_nodes
    node_index = {label: i for i, label in enumerate(node_labels)}

    fig = go.Figure(
        go.Sankey(
            arrangement="snap",
            node=dict(
                label=node_labels,
                pad=12,
                thickness=13,
                line=dict(color="rgba(50,50,50,0.25)", width=0.5),
            ),
            link=dict(
                source=[node_index[f"2022 | {r['from']}"] for _, r in links.iterrows()],
                target=[node_index[f"2023 | {r['to']}"] for _, r in links.iterrows()],
                value=links["plans"].tolist(),
                customdata=links[["from", "to"]].astype(str).values,
                hovertemplate=(
                    "From %{customdata[0]}<br>To %{customdata[1]}<br>%{value:,} plans<extra></extra>"
                ),
            ),
        )
    )

    return style(
        fig,
        "Plan-size transitions: 2022 → 2023",
        "Matched plans using beginning-of-year participant bands.",
        height=height,
    )