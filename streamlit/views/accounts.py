"""Accounts: one row per employer plan, for finding and sizing prospects."""

import pandas as pd
import streamlit as st

from figures import kpis
from figures.data import SELF_FUNDING_BANDS, load
from figures.layout import filters
from figures.theme import money

t = load()
f = filters()

FLAGS = {
    "Self-funded": lambda d: d["self_funded"],
    "No voluntary benefits": lambda d: ~d["has_voluntary"],
    "Take rate above size-band median": lambda d: d["take_rate"] > d["band_take_rate"],
    "Changed national firm": lambda d: d["changed_firm"],
    "Amended filing": lambda d: d["amended"],
    "Partial-year contract": lambda d: d["partial_year"],
}

accounts = t.accounts
if f.industry:
    accounts = accounts[accounts["sector"] == f.industry]
if f.state:
    accounts = accounts[accounts["state"] == f.state]

search, sizes, flags = st.columns([2, 2, 4], gap="medium")
with search:
    query = st.text_input(
        "Search",
        placeholder="Sponsor, city or EIN",
        key="account_search",
        label_visibility="collapsed",
    )
with sizes:
    picked_sizes = st.multiselect(
        "Participants",
        SELF_FUNDING_BANDS,
        placeholder="All plan sizes",
        key="account_sizes",
        label_visibility="collapsed",
    )
with flags:
    picked_flags = (
        st.pills(
            "Flags",
            list(FLAGS),
            selection_mode="multi",
            key="account_flags",
            label_visibility="collapsed",
            wrap=True,
        )
        or []
    )

if query:
    q = query.strip().upper()
    text = (
        accounts["sponsor"].fillna("")
        + " "
        + accounts["city"].fillna("")
        + " "
        + accounts["plan_key"]
    ).str.upper()
    accounts = accounts[text.str.contains(q, regex=False)]
if picked_sizes:
    accounts = accounts[accounts["band"].isin(picked_sizes)]
for flag in picked_flags:
    accounts = accounts[FLAGS[flag](accounts).fillna(False).astype(bool)]

kpis.render(
    [
        kpis.Kpi(
            "Plans listed",
            f"{len(accounts):,}",
            help="Single-employer plans with 100+ participants and at least one Schedule A "
            "contract, from each plan's latest filing in the last two form years.",
        ),
        kpis.Kpi(
            "Broker pay",
            money(accounts["broker_pay"].sum(), plotly=False),
            help="Commissions and carrier-paid fees across the listed plans.",
        ),
        kpis.Kpi(
            "Median take rate",
            f"{accounts['take_rate'].median():.1f}%"
            if accounts["take_rate"].notna().any()
            else "n/a",
            help="Broker pay as a share of premium, per plan.",
        ),
        kpis.Kpi(
            "Self-funded",
            f"{accounts['self_funded'].sum() / accounts['offers_health'].sum() * 100:.0f}%"
            if accounts["offers_health"].any()
            else "n/a",
            help="Share of the listed health plans with no insured medical contract on "
            "Schedule A.",
        ),
    ]
)

table = pd.DataFrame(
    {
        "Sponsor": accounts["sponsor"].fillna(accounts["plan_key"]),
        "City": accounts["city"],
        "State": accounts["state"],
        "Industry": accounts["sector"],
        "Participants": accounts["participants"],
        "Lines": accounts["lines"],
        "Top carriers": accounts["carriers"],
        "Broker pay": accounts["broker_pay"],
        "Take rate": accounts["take_rate"],
        "Band median": accounts["band_take_rate"],
        "National firm": accounts["national_firms"].replace("", None),
        "Self-funded": accounts["self_funded"],
        "Voluntary": accounts["has_voluntary"],
        "Changed firm": accounts["changed_firm"],
        "Amended": accounts["amended"],
        "Partial year": accounts["partial_year"],
        "Form year": accounts["year"],
        "ACK ID": accounts["ack_id"],
    }
)
st.dataframe(
    table,
    hide_index=True,
    height=520,
    column_config={
        "Sponsor": st.column_config.TextColumn(width="medium", pinned=True),
        "Participants": st.column_config.NumberColumn(format="localized"),
        "Lines": st.column_config.TextColumn(width="medium"),
        "Top carriers": st.column_config.TextColumn(width="medium"),
        "Broker pay": st.column_config.NumberColumn(
            "Broker pay ($)",
            format="compact",
            help="Commissions plus carrier-paid fees",
        ),
        "Take rate": st.column_config.NumberColumn(
            format="%.1f%%", help="Broker pay as a share of premium"
        ),
        "Band median": st.column_config.NumberColumn(
            format="%.1f%%", help="Median take rate for plans of the same size"
        ),
        "National firm": st.column_config.TextColumn(
            help="National brokers and consultants named on Schedule C"
        ),
        "Changed firm": st.column_config.CheckboxColumn(
            help="The national firms on Schedule C changed from the year before"
        ),
        "Partial year": st.column_config.CheckboxColumn(
            help="At least one contract covers a policy year under 12 months"
        ),
        "Form year": st.column_config.NumberColumn(format="%d"),
        "ACK ID": st.column_config.TextColumn(
            help="Look up the filing by this ID at efast.dol.gov/5500Search"
        ),
    },
)
with st.container(horizontal=True, vertical_alignment="center"):
    st.download_button(
        "Download CSV",
        table.to_csv(index=False).encode(),
        file_name="accounts.csv",
        mime="text/csv",
        icon=":material/download:",
    )
    st.caption(
        "Sorted by broker pay. Broker pay, take rate, lines and carriers come from Schedule A; "
        "national firms come from Schedule C, which many plans don't file. Any row can be "
        "traced to its filing on DOL's EFAST2 search with the ACK ID."
    )
