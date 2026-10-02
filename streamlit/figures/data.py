"""Aggregate tables built from the Form 5500 parquet exports.

The SQL lives in queries.py and follows notebooks/analysis.ipynb. DuckDB reads the parquet files
once per server process and only the aggregates (plus one row per plan for the account list)
stay in memory.
"""

import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

from figures.constants import FIRST, LAST, NAICS_SECTORS, SELF_FUNDING_BANDS
from figures.queries import (
    ACCOUNTS,
    CARRIERS,
    CONTRACTS,
    CONTRACTS_ALL,
    FILINGS,
    FIRM_EVENTS,
    FIRM_NAMES,
    FIRM_PLANS,
    HEALTH_PLANS,
    LATEST_RECEIVED,
    PLAN_PAY,
    PLAN_YEARS,
    PROVIDERS,
    TOP_CARRIERS,
    VOLUNTARY,
)

EXPORTS = Path(__file__).resolve().parents[2] / "data" / "exports"


@dataclass(frozen=True)
class Tables:
    """Aggregates behind every chart. Shared across sessions, so never modify them."""

    contracts: pd.DataFrame  # year, line, sector, state, commissions, fees, lives, ...
    carriers: pd.DataFrame  # year, carrier, line, sector, state, contracts, tr_premium
    plan_pay: pd.DataFrame  # year, plan_id, sector, state, pay
    health: pd.DataFrame  # year, band, sector, state, plans, self_funded
    voluntary: pd.DataFrame  # year, band, sector, state, plans, with_voluntary
    firm_plans: pd.DataFrame  # year, firm, sector, state, plans
    firm_events: pd.DataFrame  # year, firm, event, sector, state, plans
    firm_names: pd.DataFrame  # firm, provider, plan_years
    accounts: pd.DataFrame  # one row per plan; see ACCOUNTS in queries.py
    latest_received: date  # latest EFAST receipt date in the data


def _with_sector(df: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    """Replace 2-digit NAICS with a sector name and collapse to the smaller grain."""
    df = df.assign(sector=df["naics_2"].map(NAICS_SECTORS).fillna("Unknown"))
    df["state"] = df["state"].fillna("")
    keys = [c for c in df.columns if c not in value_cols and c != "naics_2"]
    return df.groupby(keys, as_index=False, observed=True)[value_cols].sum()


def _band(participants: pd.Series) -> pd.Series:
    """The self-funding size bands, for the account list."""
    return pd.cut(
        participants,
        [100, 250, 500, 1000, 2500, 5000, float("inf")],
        right=False,
        labels=SELF_FUNDING_BANDS,
    ).astype(str)


def _accounts(df: pd.DataFrame) -> pd.DataFrame:
    df = df.assign(
        sector=df["naics_2"].map(NAICS_SECTORS).fillna("Unknown"),
        band=_band(df["participants"]),
    ).drop(columns="naics_2")
    df["state"] = df["state"].fillna("")
    # Peer benchmark: the median take rate among plans in the same size band
    df["band_take_rate"] = df.groupby("band")["take_rate"].transform("median")
    return df.sort_values("broker_pay", ascending=False, ignore_index=True)


@st.cache_resource(show_spinner="Reading 2019-2024 Form 5500 filings")
def load() -> Tables:
    with duckdb.connect() as con:
        con.execute("SET threads = 2")
        con.execute("SET memory_limit = '600MB'")
        con.execute("SET preserve_insertion_order = false")
        con.execute(f"SET temp_directory = '{Path(tempfile.gettempdir()) / 'duckdb'}'")
        for table in ["F_5500", "SCH_A", "SCH_C_P1_I2"]:
            path = (EXPORTS / f"{table}.parquet").as_posix().replace("'", "''")
            con.execute(f"CREATE VIEW {table} AS SELECT * FROM read_parquet('{path}')")

        con.execute(f"CREATE TEMP TABLE filings AS {FILINGS}")
        con.execute(f"CREATE TEMP VIEW contracts_all AS {CONTRACTS_ALL}")
        contracts = con.sql(CONTRACTS).df()
        con.execute(f"CREATE TEMP TABLE top_carriers AS {TOP_CARRIERS}")
        carriers = con.sql(CARRIERS).df()
        plan_pay = con.sql(PLAN_PAY).df()
        health = con.sql(HEALTH_PLANS).df()
        voluntary = con.sql(VOLUNTARY).df()

        con.execute(f"CREATE TEMP TABLE providers AS {PROVIDERS}")
        con.execute(f"CREATE TEMP TABLE plan_years AS {PLAN_YEARS}")
        firm_plans = con.sql(FIRM_PLANS).df()
        firm_events = con.sql(FIRM_EVENTS).df()
        firm_names = con.sql(FIRM_NAMES).df()
        accounts = con.sql(ACCOUNTS).df()
        latest_received = con.sql(LATEST_RECEIVED).fetchone()[0]

    plan_pay = _with_sector(plan_pay, ["pay"])
    return Tables(
        contracts=_with_sector(
            contracts,
            [
                "commissions",
                "fees",
                "lives",
                "contracts",
                "fee_contracts",
                "tr_premium",
                "tr_compensation",
                "blank_contracts",
                "blank_tr_premium",
                "partial_contracts",
            ],
        ),
        carriers=_with_sector(carriers, ["contracts", "tr_premium"]),
        plan_pay=plan_pay,
        health=_with_sector(health, ["plans", "self_funded"]),
        voluntary=_with_sector(voluntary, ["plans", "with_voluntary"]),
        firm_plans=_with_sector(firm_plans, ["plans"]),
        firm_events=_with_sector(firm_events, ["plans"]),
        firm_names=firm_names,
        accounts=_accounts(accounts),
        latest_received=latest_received,
    )


@dataclass(frozen=True)
class Filters:
    start: int = FIRST
    end: int = LAST
    industry: str | None = None  # sector name, or None for all industries
    state: str | None = None  # two-letter code, or None for all states

    @property
    def years(self) -> list[int]:
        return list(range(self.start, self.end + 1))


def subset(
    df: pd.DataFrame,
    f: Filters,
    *,
    industry: bool = True,
    state: bool = True,
    years: bool = True,
) -> pd.DataFrame:
    """Apply the global filters. Charts that are the filter's own picker opt out of that filter."""
    mask = pd.Series(True, index=df.index)
    if years:
        mask &= df["year"].between(f.start, f.end)
    if industry and f.industry:
        mask &= df["sector"] == f.industry
    if state and f.state:
        mask &= df["state"] == f.state
    return df[mask]
