import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from benefits_market_intelligence.config.paths import EXPORTS_PATH

warnings.filterwarnings("ignore", category=FutureWarning)

PALETTE = px.colors.qualitative.Safe
ACCENT = "#1f77b4"
MUTED = "#7f8c8d"
ALERT = "#d62728"
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
        title={
            "text": title_text,
            "x": 0.01,
            "xanchor": "left",
            "font": {"size": 16},
        },
        height=height,
        margin=dict(l=45, r=20, t=65, b=40),
        font=dict(
            family="Arial, sans-serif",
            color=DARK,
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
            font=dict(size=9),
        ),
        hoverlabel=dict(bgcolor="white"),
    )

    return fig


def num(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def clean_text(s, fallback="Not reported"):
    out = s.astype("string").str.strip()

    out = out.replace(
        {
            "": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
            "<NA>": pd.NA,
        }
    )

    return out.fillna(fallback)


def yes_flag(series):
    return series.astype("string").str.upper().isin(["1", "Y", "YES", "TRUE", "X"])


# ---------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def load_data():
    f_5500 = pd.read_parquet(EXPORTS_PATH / "F_5500.parquet")
    sch_a = pd.read_parquet(EXPORTS_PATH / "SCH_A.parquet")
    sch_c = pd.read_parquet(EXPORTS_PATH / "SCH_C_P1_I2.parquet")

    f_5500 = num(
        f_5500,
        [
            "TOT_PARTCP_BOY_CNT",
            "TOT_ACTIVE_PARTCP_CNT",
        ],
    )

    sch_a = num(
        sch_a,
        [
            "PENSION_PREM_PAID_TOT_AMT",
            "WLFR_PREMIUM_RCVD_AMT",
            "WLFR_TOT_EARNED_PREM_AMT",
            "INS_BROKER_COMM_TOT_AMT",
            "INS_BROKER_FEES_TOT_AMT",
            "INS_PRSN_COVERED_EOY_CNT",
        ],
    )

    sch_c = num(
        sch_c,
        [
            "PROVIDER_OTHER_DIRECT_COMP_AMT",
            "PROV_OTHER_TOT_IND_COMP_AMT",
        ],
    )

    for df in [f_5500, sch_a, sch_c]:
        df["FORM_YEAR"] = pd.to_numeric(
            df["FORM_YEAR"],
            errors="coerce",
        ).astype("Int64")

    f_5500["SPONS_DFE_EIN"] = clean_text(
        f_5500["SPONS_DFE_EIN"],
        fallback="",
    )

    f_5500["SPONS_DFE_PN"] = clean_text(
        f_5500["SPONS_DFE_PN"],
        fallback="",
    )

    f_5500["ACK_ID"] = clean_text(
        f_5500["ACK_ID"],
        fallback="",
    )

    f_5500["plan_key"] = np.where(
        (f_5500["SPONS_DFE_EIN"] != "") & (f_5500["SPONS_DFE_PN"] != ""),
        f_5500["SPONS_DFE_EIN"] + "|" + f_5500["SPONS_DFE_PN"],
        f_5500["ACK_ID"],
    )

    sch_a["ACK_ID"] = clean_text(
        sch_a["ACK_ID"],
        fallback="",
    )

    sch_c["ACK_ID"] = clean_text(
        sch_c["ACK_ID"],
        fallback="",
    )

    sch_a["carrier"] = clean_text(
        sch_a["INS_CARRIER_NAME"],
    )

    plans = f_5500.drop_duplicates(["plan_key", "FORM_YEAR"])[
        [
            "plan_key",
            "ACK_ID",
            "FORM_YEAR",
            "TOT_PARTCP_BOY_CNT",
            "TOT_ACTIVE_PARTCP_CNT",
            "BUSINESS_CODE",
        ]
    ].copy()

    # Premium concept used in the notebook.
    sch_a["reported_premium"] = sch_a["WLFR_PREMIUM_RCVD_AMT"].fillna(0) + sch_a[
        "PENSION_PREM_PAID_TOT_AMT"
    ].fillna(0)

    sch_a["commission"] = sch_a["INS_BROKER_COMM_TOT_AMT"].fillna(0)

    sch_a["fees"] = sch_a["INS_BROKER_FEES_TOT_AMT"].fillna(0)

    sch_a["commission_rate"] = np.where(
        sch_a["reported_premium"] > 0,
        sch_a["commission"] / sch_a["reported_premium"],
        np.nan,
    )

    sch_a["commission_rate_pct"] = sch_a["commission_rate"] * 100

    # -------------------------------------------------------------
    # Outlier logic from notebook
    # -------------------------------------------------------------

    valid = sch_a.copy()

    valid["positive_premium"] = valid["reported_premium"] > 0

    valid["nonnegative_commission"] = valid["commission"] >= 0

    valid_base = valid[
        valid["positive_premium"] & valid["nonnegative_commission"]
    ].copy()

    fences = (
        valid_base.groupby("FORM_YEAR")["commission"]
        .agg(
            q1=lambda s: s.quantile(0.25),
            q3=lambda s: s.quantile(0.75),
        )
        .assign(
            iqr=lambda d: d["q3"] - d["q1"],
            fence=lambda d: d["q3"] + 3 * d["iqr"],
        )
    )

    valid = valid.merge(
        fences["fence"],
        left_on="FORM_YEAR",
        right_index=True,
        how="left",
    )

    valid["distribution_outlier"] = valid["commission"] > valid["fence"]

    valid["invalid_premium_base"] = (valid["reported_premium"] <= 0) & (
        valid["commission"] != 0
    )

    valid["suspect"] = valid["distribution_outlier"] | valid["invalid_premium_base"]

    valid_base = valid[
        valid["positive_premium"] & valid["nonnegative_commission"]
    ].copy()

    # Plan/year aggregation.
    plan_contracts = valid_base.groupby(
        ["ACK_ID", "FORM_YEAR"],
        as_index=False,
    ).agg(
        reported_premium=("reported_premium", "sum"),
        reported_commission=("commission", "sum"),
        suspect_commission=("suspect", "sum"),
        contract_count=("ACK_ID", "size"),
    )

    plan_contracts["commission_rate"] = np.where(
        plan_contracts["reported_premium"] > 0,
        plan_contracts["reported_commission"] / plan_contracts["reported_premium"],
        np.nan,
    )

    # Core data excludes flagged contract rows.
    core = valid_base[~valid_base["suspect"]].copy()

    core_annual = core.groupby("FORM_YEAR", as_index=False).agg(
        core_premium=("reported_premium", "sum"),
        core_commission=("commission", "sum"),
    )

    core_annual["core_weighted_rate"] = (
        core_annual["core_commission"] / core_annual["core_premium"]
    )

    raw_annual = valid_base.groupby("FORM_YEAR", as_index=False).agg(
        reported_premium=("reported_premium", "sum"),
        reported_commission=("commission", "sum"),
    )

    raw_annual["reported_weighted_rate"] = (
        raw_annual["reported_commission"] / raw_annual["reported_premium"]
    )

    plan_rate = (
        plan_contracts.loc[plan_contracts["suspect_commission"] == 0]
        .groupby("FORM_YEAR")[["commission_rate"]]
        .agg(
            median_plan_rate=(
                "commission_rate",
                "median",
            ),
            p90_plan_rate=(
                "commission_rate",
                lambda s: s.quantile(0.90),
            ),
        )
        .reset_index()
    )

    trend = (
        raw_annual.merge(
            core_annual[
                [
                    "FORM_YEAR",
                    "core_weighted_rate",
                ]
            ],
            on="FORM_YEAR",
            how="outer",
        )
        .merge(
            plan_rate,
            on="FORM_YEAR",
            how="left",
        )
        .sort_values("FORM_YEAR")
    )

    participants = (
        plans.groupby("FORM_YEAR", as_index=False)["TOT_PARTCP_BOY_CNT"]
        .sum(min_count=1)
        .rename(columns={"TOT_PARTCP_BOY_CNT": "participants_boy"})
    )

    trend = trend.merge(
        participants,
        on="FORM_YEAR",
        how="left",
    )

    return {
        "F_5500": f_5500,
        "SCH_A": sch_a,
        "SCH_C": sch_c,
        "plans": plans,
        "valid": valid,
        "valid_base": valid_base,
        "core": core,
        "plan_contracts": plan_contracts,
        "trend": trend,
    }


# ---------------------------------------------------------------------
# Chart 1 — Commission intensity
# ---------------------------------------------------------------------


def commission_intensity_chart(data, height=260):
    trend = data["trend"].copy()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=trend["FORM_YEAR"],
            y=trend["reported_weighted_rate"] * 100,
            mode="lines+markers",
            name="Reported",
            line=dict(
                color=MUTED,
                dash="dot",
                width=2,
            ),
            hovertemplate=("Year %{x}<br>Reported rate %{y:.2f}%<extra></extra>"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=trend["FORM_YEAR"],
            y=trend["core_weighted_rate"] * 100,
            mode="lines+markers",
            name="Core",
            line=dict(
                color=ACCENT,
                width=3,
            ),
            hovertemplate=("Year %{x}<br>Core rate %{y:.2f}%<extra></extra>"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=trend["FORM_YEAR"],
            y=trend["median_plan_rate"] * 100,
            mode="lines+markers",
            name="Median plan",
            line=dict(
                color=GOOD,
                width=2,
            ),
            hovertemplate=("Year %{x}<br>Median plan rate %{y:.2f}%<extra></extra>"),
        )
    )

    fig.update_yaxes(
        title="Commission / premium (%)",
        tickformat=".1f",
    )

    fig.update_xaxes(
        dtick=1,
        title="",
    )

    return style(
        fig,
        "Commission intensity over time",
        "Core rate excludes flagged Schedule A rows.",
        height=height,
    )


# ---------------------------------------------------------------------
# Chart 2 — Carrier share slopegraph
# ---------------------------------------------------------------------


def carrier_share_chart(data, height=260):
    sch_a = data["SCH_A"].copy()

    carrier_year = sch_a.groupby(
        ["FORM_YEAR", "carrier"],
        as_index=False,
    ).agg(premium=("reported_premium", "sum"))

    carrier_year = carrier_year[carrier_year["premium"] > 0]

    carrier_year["share"] = carrier_year["premium"] / carrier_year.groupby("FORM_YEAR")[
        "premium"
    ].transform("sum")

    latest = carrier_year[carrier_year["FORM_YEAR"] == 2023].nlargest(8, "premium")[
        "carrier"
    ]

    compare = carrier_year[
        carrier_year["FORM_YEAR"].isin([2019, 2023])
        & carrier_year["carrier"].isin(latest)
    ].copy()

    wide = (
        compare.pivot(
            index="carrier",
            columns="FORM_YEAR",
            values="share",
        )
        .dropna()
        .reset_index()
    )

    if wide.empty:
        return go.Figure()

    wide = wide.sort_values(
        2023,
        ascending=False,
    )

    fig = go.Figure()

    for _, row in wide.iterrows():
        carrier = row["carrier"]

        fig.add_trace(
            go.Scatter(
                x=[2019, 2023],
                y=[
                    row[2019] * 100,
                    row[2023] * 100,
                ],
                mode="lines+markers",
                name=carrier,
                line=dict(width=2),
                marker=dict(size=7),
                hovertemplate=(f"{carrier}<br>%{{x}}: %{{y:.2f}}%<extra></extra>"),
            )
        )

    fig.update_xaxes(
        range=[2018.6, 2023.4],
        tickvals=[2019, 2023],
        title="",
    )

    fig.update_yaxes(
        title="Premium share (%)",
        ticksuffix="%",
        rangemode="tozero",
    )

    fig.update_layout(
        showlegend=False,
    )

    return style(
        fig,
        "Carrier premium-share movement",
        "Top eight carriers by 2023 reported premium.",
        height=height,
    )


# ---------------------------------------------------------------------
# Chart 3 — Commission outlier map
# ---------------------------------------------------------------------


def commission_outlier_chart(data, height=260):
    sch_a = data["SCH_A"].copy()

    scatter = sch_a[(sch_a["reported_premium"] > 0) & (sch_a["commission"] > 0)].copy()

    scatter = scatter[scatter["commission_rate_pct"] > 0].copy()

    fences = scatter.groupby("FORM_YEAR")["commission"].agg(
        q1=lambda s: s.quantile(0.25),
        q3=lambda s: s.quantile(0.75),
    )

    fences["iqr"] = fences["q3"] - fences["q1"]

    fences["fence"] = fences["q3"] + 3 * fences["iqr"]

    scatter = scatter.merge(
        fences["fence"],
        left_on="FORM_YEAR",
        right_index=True,
        how="left",
    )

    scatter["suspect"] = scatter["commission"] > scatter["fence"]

    suspect = scatter[scatter["suspect"]].copy()

    ordinary = scatter[~scatter["suspect"]].copy()

    sample_n = min(
        15_000,
        len(ordinary),
    )

    if sample_n:
        ordinary = ordinary.sample(
            sample_n,
            random_state=42,
        )

    scatter_plot = (
        pd.concat(
            [ordinary, suspect],
            ignore_index=True,
        )
        .drop_duplicates(
            subset=[
                "ACK_ID",
                "FORM_YEAR",
                "carrier",
                "reported_premium",
                "commission",
            ]
        )
        .copy()
    )

    scatter_plot["status"] = np.where(
        scatter_plot["suspect"],
        "Flagged",
        "Core",
    )

    scatter_plot["covered"] = pd.to_numeric(
        scatter_plot["INS_PRSN_COVERED_EOY_CNT"],
        errors="coerce",
    )

    scatter_plot["covered"] = scatter_plot["covered"].clip(lower=1)

    scatter_plot = scatter_plot[
        pd.to_numeric(
            scatter_plot["reported_premium"],
            errors="coerce",
        ).gt(0)
        & pd.to_numeric(
            scatter_plot["commission_rate_pct"],
            errors="coerce",
        ).gt(0)
        & scatter_plot["covered"].notna()
    ].copy()

    if scatter_plot.empty:
        return go.Figure()

    fig = px.scatter(
        scatter_plot,
        x="reported_premium",
        y="commission_rate_pct",
        size="covered",
        color="status",
        symbol="status",
        hover_name="carrier",
        hover_data={
            "FORM_YEAR": True,
            "ACK_ID": True,
            "reported_premium": ":$,.0f",
            "commission": ":$,.0f",
            "commission_rate_pct": ":.2f",
            "covered": ":,.0f",
            "status": True,
        },
        color_discrete_map={
            "Core": ACCENT,
            "Flagged": ALERT,
        },
        render_mode="webgl",
    )

    fig.update_xaxes(
        type="log",
        title="Premium — log scale",
    )

    fig.update_yaxes(
        type="log",
        title="Commission rate — log",
    )

    return style(
        fig,
        "Commission outlier map",
        "Flagged contracts are retained; ordinary contracts are sampled.",
        height=height,
    )


# ---------------------------------------------------------------------
# Chart 4 — Plan-size Sankey
# ---------------------------------------------------------------------


def plan_size_sankey(data, height=260):
    plans = data["plans"].copy()

    size_bins = [
        -np.inf,
        99,
        499,
        999,
        4_999,
        9_999,
        np.inf,
    ]

    size_labels = [
        "<100",
        "100–499",
        "500–999",
        "1k–4.9k",
        "5k–9.9k",
        "10k+",
    ]

    plan_size = plans[
        [
            "plan_key",
            "FORM_YEAR",
            "TOT_PARTCP_BOY_CNT",
        ]
    ].copy()

    plan_size = plan_size[
        plan_size["TOT_PARTCP_BOY_CNT"].notna() & (plan_size["TOT_PARTCP_BOY_CNT"] >= 0)
    ]

    plan_size["size_bucket"] = pd.cut(
        plan_size["TOT_PARTCP_BOY_CNT"],
        bins=size_bins,
        labels=size_labels,
    )

    base = (
        plan_size[plan_size["FORM_YEAR"].isin([2022, 2023])]
        .pivot(
            index="plan_key",
            columns="FORM_YEAR",
            values="size_bucket",
        )
        .dropna()
    )

    if base.empty:
        return go.Figure()

    transitions = base.reset_index().rename(
        columns={
            2022: "from",
            2023: "to",
        }
    )

    links = (
        transitions.groupby(
            ["from", "to"],
            observed=True,
        )
        .size()
        .reset_index(name="plans")
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
                line=dict(
                    color="rgba(50,50,50,0.25)",
                    width=0.5,
                ),
            ),
            link=dict(
                source=[node_index[f"2022 | {r['from']}"] for _, r in links.iterrows()],
                target=[node_index[f"2023 | {r['to']}"] for _, r in links.iterrows()],
                value=links["plans"].tolist(),
                customdata=links[["from", "to"]].astype(str).values,
                hovertemplate=(
                    "From %{customdata[0]}"
                    "<br>To %{customdata[1]}"
                    "<br>%{value:,} plans"
                    "<extra></extra>"
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


# ---------------------------------------------------------------------
# Additional notebook analyses
# These are retained here but are not placed on the one-page dashboard.
# ---------------------------------------------------------------------


def premium_per_participant_chart(data, height=500):
    sch_a = data["SCH_A"]
    plans = data["plans"]

    plan_premium = (
        sch_a.groupby(
            ["ACK_ID", "FORM_YEAR"],
            as_index=False,
        )["reported_premium"]
        .sum()
        .rename(columns={"reported_premium": "insured_premium"})
    )

    plan_econ = (
        plans[
            [
                "ACK_ID",
                "FORM_YEAR",
                "TOT_PARTCP_BOY_CNT",
            ]
        ]
        .drop_duplicates(["ACK_ID", "FORM_YEAR"])
        .merge(
            plan_premium,
            on=[
                "ACK_ID",
                "FORM_YEAR",
            ],
            how="inner",
        )
        .copy()
    )

    plan_econ["insured_premium"] = pd.to_numeric(
        plan_econ["insured_premium"],
        errors="coerce",
    )

    plan_econ["TOT_PARTCP_BOY_CNT"] = pd.to_numeric(
        plan_econ["TOT_PARTCP_BOY_CNT"],
        errors="coerce",
    )

    plan_econ = plan_econ[
        plan_econ["insured_premium"].gt(0) & plan_econ["TOT_PARTCP_BOY_CNT"].gt(0)
    ].copy()

    plan_econ["premium_per_participant"] = (
        plan_econ["insured_premium"] / plan_econ["TOT_PARTCP_BOY_CNT"]
    )

    plan_econ = plan_econ[plan_econ["premium_per_participant"].gt(0)].copy()

    plan_econ["log_participants"] = np.log10(plan_econ["TOT_PARTCP_BOY_CNT"])

    plan_econ["log_premium_pp"] = np.log10(plan_econ["premium_per_participant"])

    plan_econ = plan_econ.replace(
        [np.inf, -np.inf],
        np.nan,
    ).dropna(
        subset=[
            "log_participants",
            "log_premium_pp",
        ]
    )

    fig = px.density_heatmap(
        plan_econ,
        x="log_participants",
        y="log_premium_pp",
        nbinsx=30,
        nbinsy=30,
    )

    fig.update_xaxes(
        title="Participants at beginning of year",
        tickmode="array",
        tickvals=[0, 1, 2, 3, 4, 5],
        ticktext=[
            "1",
            "10",
            "100",
            "1K",
            "10K",
            "100K",
        ],
    )

    fig.update_yaxes(
        title="Insured premium per participant",
        tickmode="array",
        tickvals=[0, 1, 2, 3, 4, 5],
        ticktext=[
            "$1",
            "$10",
            "$100",
            "$1K",
            "$10K",
            "$100K",
        ],
    )

    return style(
        fig,
        "Plan size vs. insured premium per participant",
        height=height,
    )


def benefit_premium_chart(data, height=500):
    sch_a = data["SCH_A"]

    benefit_flags = {
        "Health": "WLFR_BNFT_HEALTH_IND",
        "Dental": "WLFR_BNFT_DENTAL_IND",
        "Vision": "WLFR_BNFT_VISION_IND",
        "Life": "WLFR_BNFT_LIFE_INSUR_IND",
        "Temporary disability": "WLFR_BNFT_TEMP_DISAB_IND",
        "Unemployment": "WLFR_BNFT_UNEMP_IND",
        "Drug": "WLFR_BNFT_DRUG_IND",
        "Stop loss": "WLFR_BNFT_STOP_LOSS_IND",
        "HMO": "WLFR_BNFT_HMO_IND",
        "PPO": "WLFR_BNFT_PPO_IND",
        "Indemnity": "WLFR_BNFT_INDEMNITY_IND",
        "Other": "WLFR_BNFT_OTHER_IND",
    }

    latest = sch_a[sch_a["FORM_YEAR"] == 2023].copy()

    rows = []

    for label, col in benefit_flags.items():
        if col not in latest.columns:
            continue

        flag = yes_flag(latest[col])

        tmp = latest.loc[
            flag,
            ["reported_premium"],
        ].copy()

        tmp["benefit_type"] = label
        rows.append(tmp)

    if not rows:
        return go.Figure()

    summary = (
        pd.concat(
            rows,
            ignore_index=True,
        )
        .groupby(
            "benefit_type",
            as_index=False,
        )["reported_premium"]
        .sum()
        .sort_values(
            "reported_premium",
            ascending=False,
        )
    )

    fig = go.Figure(
        go.Barpolar(
            r=summary["reported_premium"],
            theta=summary["benefit_type"],
            text=[money(v) for v in summary["reported_premium"]],
            hovertemplate=("%{theta}<br>Tagged premium %{r:$,.0f}<extra></extra>"),
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                tickprefix="$",
                tickformat=",.0s",
            )
        )
    )

    return style(
        fig,
        "Premium tagged by benefit category, 2023",
        "Categories are non-additive because a contract can have multiple tags.",
        height=height,
    )


def service_provider_waterfall(data, height=450):
    sch_c = data["SCH_C"]

    comp = sch_c[sch_c["FORM_YEAR"] == 2023].copy()

    direct = comp["PROVIDER_OTHER_DIRECT_COMP_AMT"].fillna(0).clip(lower=0).sum()

    indirect = comp["PROV_OTHER_TOT_IND_COMP_AMT"].fillna(0).clip(lower=0).sum()

    total = direct + indirect

    fig = go.Figure(
        go.Waterfall(
            orientation="v",
            measure=[
                "relative",
                "relative",
                "total",
            ],
            x=[
                "Direct compensation",
                "Indirect compensation",
                "Total",
            ],
            y=[
                direct,
                indirect,
                0,
            ],
            text=[
                money(direct),
                money(indirect),
                money(total),
            ],
            textposition="outside",
            connector={"line": {"color": "rgba(80,80,80,0.4)"}},
        )
    )

    fig.update_yaxes(
        title="Reported compensation ($)",
        tickprefix="$",
        tickformat=",.0s",
    )

    return style(
        fig,
        "2023 service-provider compensation mix",
        "Direct and indirect compensation are separated before the total.",
        height=height,
    )


def carrier_footprint_chart(data, height=450):
    sch_a = data["SCH_A"]
    plans = data["plans"]

    carrier_sets = (
        sch_a[sch_a["carrier"] != "Not reported"]
        .groupby(["ACK_ID", "FORM_YEAR"])["carrier"]
        .apply(
            lambda s: frozenset(
                x for x in s.dropna().unique() if x and x != "Not reported"
            )
        )
        .reset_index(name="carrier_set")
    )

    carrier_sets = carrier_sets.merge(
        plans[
            [
                "ACK_ID",
                "FORM_YEAR",
                "plan_key",
            ]
        ],
        on=[
            "ACK_ID",
            "FORM_YEAR",
        ],
        how="left",
    ).dropna(subset=["plan_key"])

    pairs = []

    for y0, y1 in [
        (2019, 2020),
        (2020, 2021),
        (2021, 2022),
        (2022, 2023),
    ]:
        a = carrier_sets[carrier_sets["FORM_YEAR"] == y0][
            ["plan_key", "carrier_set"]
        ].rename(columns={"carrier_set": "set0"})

        b = carrier_sets[carrier_sets["FORM_YEAR"] == y1][
            ["plan_key", "carrier_set"]
        ].rename(columns={"carrier_set": "set1"})

        pair = a.merge(
            b,
            on="plan_key",
            how="inner",
        )

        if pair.empty:
            continue

        pair["change"] = np.where(
            pair["set0"] == pair["set1"],
            "No carrier-footprint change",
            "Carrier-footprint changed",
        )

        pair["year"] = f"{y0}→{y1}"

        pairs.append(pair[["year", "change"]])

    if not pairs:
        return go.Figure()

    footprint = pd.concat(
        pairs,
        ignore_index=True,
    )

    summary = (
        footprint.groupby(
            ["year", "change"],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "plans"})
    )

    summary["share"] = summary["plans"] / summary.groupby("year")["plans"].transform(
        "sum"
    )

    year_order = [
        "2019→2020",
        "2020→2021",
        "2021→2022",
        "2022→2023",
    ]

    fig = px.area(
        summary,
        x="year",
        y="share",
        color="change",
        category_orders={"year": year_order},
        groupnorm="fraction",
        line_group="change",
        hover_data={
            "plans": ":,d",
            "share": ":.1%",
        },
    )

    fig.update_yaxes(
        title="Share of matched plans",
        tickformat=".0%",
        range=[0, 1],
    )

    fig.update_xaxes(title="Adjacent plan years")

    return style(
        fig,
        "Year-over-year carrier-footprint change",
        "Among plans observed in both adjacent years.",
        height=height,
    )
