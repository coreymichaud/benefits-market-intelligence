"""Aggregate tables built from the Form 5500 parquet exports.

The SQL follows notebooks/analysis.ipynb. DuckDB reads the parquet files once per server
process and only the small aggregates are kept in memory.
"""

import tempfile
from dataclasses import dataclass
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

EXPORTS = Path(__file__).resolve().parents[2] / "data" / "exports"

YEARS = list(range(2019, 2025))
FIRST, LAST = YEARS[0], YEARS[-1]

LINES = [
    "Medical",
    "Stop-loss",
    "Dental",
    "Vision",
    "Life & AD&D",
    "Disability",
    "Multi-line bundle",
    "Voluntary & other",
]

SELF_FUNDING_BANDS = [
    "100–249",
    "250–499",
    "500–999",
    "1,000–2,499",
    "2,500–4,999",
    "5,000+",
]
VOLUNTARY_BANDS = ["100–249", "250–499", "500–999", "1,000–4,999", "5,000+"]

NAICS_SECTORS = {
    "11": "Agriculture",
    "21": "Mining, Oil & Gas",
    "22": "Utilities",
    "23": "Construction",
    "31": "Manufacturing",
    "32": "Manufacturing",
    "33": "Manufacturing",
    "42": "Wholesale Trade",
    "44": "Retail Trade",
    "45": "Retail Trade",
    "48": "Transportation & Warehousing",
    "49": "Transportation & Warehousing",
    "51": "Information",
    "52": "Finance & Insurance",
    "53": "Real Estate",
    "54": "Professional & Technical Services",
    "55": "Management of Companies",
    "56": "Admin & Support Services",
    "61": "Educational Services",
    "62": "Health Care & Social Assistance",
    "71": "Arts & Recreation",
    "72": "Accommodation & Food Services",
    "81": "Other Services",
    "92": "Public Administration",
}
SECTORS = sorted(set(NAICS_SECTORS.values()))

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia",
    "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}  # fmt: skip

# Order matters: a provider name takes the first firm whose pattern matches (as np.select does)
BROKER_FIRMS = {
    "WTW": (r"\bWILLIS\b|\bTOWERS WATSON\b|^WTW\b|WILLISTOWERSWATSON", r"INVESTMENT"),
    "Mercer": (r"\bMERCER\b", r"INVESTMENT|\bMERCER (?:COUNTY|ISLAND|UNIVERSITY)\b"),
    "Aon": (r"^AON\b|^AONHEWITT|\bAON (?:CONSULTING|RISK|HEWITT)\b", r"INVESTMENT"),
    "Gallagher": (
        r"^GALLAGHER\b|\bARTHUR (?:J\.? )?GALLAGHER\b|\bA\.? ?J\.? GALLAGHER\b"
        r"|\bGALLAGHER BENEFIT|, A GALLAGHER\b",
        r"FIDUCIARY|INVESTMENT",
    ),
    "Marsh McLennan Agency": (r"\bMARSH (?:&|AND) ?MC|\bMARSH MC|\bMARSH USA\b", None),
    "Lockton": (r"LOCKTON", None),
    "HUB International": (r"^HUB\b|\bHUB INT", None),
    "USI": (r"^USI\b|\bUSI (?:INSURANCE|CONSULTING)\b", None),
    "Brown & Brown": (r"\bBROWN (?:&|AND) BROWN\b", None),
    "OneDigital": (r"\bONE ?DIGITAL\b|\bDIGITAL INSURANCE\b", r"INVESTMENT"),
    "AssuredPartners": (r"\bASSURED ?PARTNERS\b", None),
    "Alliant": (r"\bALLIANT (?:INS|EMPLOYEE|BEN)", None),
    "NFP": (r"^NFP|\bNATIONAL FINANCIAL PARTNERS\b", None),
    "CBIZ": (r"CBIZ", r"\bCPAS?\b"),
    "Segal": (r"\bSEGAL\b", r"\bMARCO\b"),
    "McGriff": (r"\bMCGRIFF\b|\bTRUIST INSURANCE\b", None),
    "Acrisure": (r"\bACRISURE\b", None),
    "Alera": (r"\bALERA\b", None),
    "EPIC": (r"\bEDGEWOOD PARTNERS\b|^EPIC ", None),
    "Holmes Murphy": (r"\bHOLMES MURPHY\b", None),
    "IMA": (r"^IMA\b|\bIMA FINANCIAL\b", None),
    "Hylant": (r"\bHYLANT\b", None),
}


# SQL (same rules as the notebook; table names point at parquet views instead of gold.*)

FILINGS = """
    SELECT
        ACK_ID,
        FORM_YEAR,
        SPONS_DFE_EIN || '-' || SPONS_DFE_PN AS plan_key,
        TYPE_PLAN_ENTITY_CD AS entity_type,
        TYPE_WELFARE_BNFT_CODE AS welfare_codes,
        TYPE_PENSION_BNFT_CODE AS pension_codes,
        TOT_PARTCP_BOY_CNT AS participants,
        LEFT(BUSINESS_CODE, 2) AS naics_2,
        SPONS_DFE_MAIL_US_STATE AS state
    FROM F_5500
    WHERE TYPE_WELFARE_BNFT_CODE IS NOT NULL
      -- Filing-lag control: keep filings received within 9.5 months of plan year end
      -- (7-month deadline + 2.5-month extension); ACK_ID starts with the EFAST receipt date
      AND STRPTIME(LEFT(ACK_ID, 8), '%Y%m%d')
          <= FORM_PLAN_YEAR_BEGIN_DATE + INTERVAL 21 MONTH + INTERVAL 14 DAY
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY SPONS_DFE_EIN, SPONS_DFE_PN, FORM_YEAR ORDER BY ACK_ID DESC
    ) = 1
"""

COVERAGE_FLAGS = """
    COALESCE(a.WLFR_BNFT_HEALTH_IND = '1' OR a.WLFR_BNFT_HMO_IND = '1'
        OR a.WLFR_BNFT_PPO_IND = '1' OR a.WLFR_BNFT_DRUG_IND = '1', FALSE) AS med,
    COALESCE(a.WLFR_BNFT_STOP_LOSS_IND = '1', FALSE) AS sl,
    COALESCE(a.WLFR_BNFT_DENTAL_IND = '1', FALSE) AS den,
    COALESCE(a.WLFR_BNFT_VISION_IND = '1', FALSE) AS vis,
    COALESCE(a.WLFR_BNFT_LIFE_INSUR_IND = '1', FALSE) AS life,
    COALESCE(a.WLFR_BNFT_TEMP_DISAB_IND = '1' OR a.WLFR_BNFT_LONG_TERM_DISAB_IND = '1', FALSE) AS dis,
    COALESCE(a.WLFR_BNFT_OTHER_IND = '1' OR a.WLFR_BNFT_INDEMNITY_IND = '1'
        OR a.WLFR_BNFT_UNEMP_IND = '1', FALSE) AS oth
"""

LINE_CASE = """
    CASE
        WHEN sl THEN 'Stop-loss'
        WHEN med AND NOT (den OR vis OR life OR dis) THEN 'Medical'
        WHEN den AND NOT (med OR vis OR life OR dis) THEN 'Dental'
        WHEN vis AND NOT (med OR den OR life OR dis) THEN 'Vision'
        WHEN life AND NOT (med OR den OR vis OR dis) THEN 'Life & AD&D'
        WHEN dis AND NOT (med OR den OR vis OR life) THEN 'Disability'
        WHEN med OR den OR vis OR life OR dis THEN 'Multi-line bundle'
        WHEN oth THEN 'Voluntary & other'
        ELSE 'Unclassified'
    END
"""

# tr_* columns only count contracts that also pass the notebook's take-rate screen
CONTRACTS = f"""
    WITH flagged AS (
        SELECT
            f.FORM_YEAR,
            f.naics_2,
            f.state,
            a.INS_BROKER_COMM_TOT_AMT AS commissions,
            a.INS_BROKER_FEES_TOT_AMT AS fees,
            TRY_CAST(a.INS_PRSN_COVERED_EOY_CNT AS DOUBLE) AS lives,
            GREATEST(COALESCE(a.WLFR_TOT_CHARGES_PAID_AMT, 0),
                     COALESCE(a.WLFR_TOT_EARNED_PREM_AMT, 0)) AS premium,
            {COVERAGE_FLAGS}
        FROM SCH_A a
        JOIN filings f USING (ACK_ID)
    ),
    screened AS (
        SELECT
            FORM_YEAR,
            naics_2,
            state,
            COALESCE(commissions, 0) AS commissions,
            COALESCE(fees, 0) AS fees,
            lives,
            premium,
            {LINE_CASE} AS line
        FROM flagged
        -- Data-quality screen: drop negative amounts, missing lives, and implausible $/life
        WHERE COALESCE(commissions, 0) >= 0
          AND COALESCE(fees, 0) >= 0
          AND lives BETWEEN 1 AND 1000000
          AND (COALESCE(commissions, 0) + COALESCE(fees, 0)) / lives <= 2500
    ),
    tagged AS (
        SELECT
            *,
            line <> 'Unclassified'
                AND premium > 0
                AND premium / lives <= 50000
                AND (commissions + fees) / premium <= 1
                AND premium <= 250000000 AS take_rate_ok
        FROM screened
    )
    SELECT
        FORM_YEAR AS year,
        line,
        naics_2,
        state,
        SUM(commissions) AS commissions,
        SUM(fees) AS fees,
        SUM(lives) AS lives,
        COUNT(*) AS contracts,
        COUNT(*) FILTER (WHERE fees > 0) AS fee_contracts,
        COALESCE(SUM(premium) FILTER (WHERE take_rate_ok), 0) AS tr_premium,
        COALESCE(SUM(commissions + fees) FILTER (WHERE take_rate_ok), 0) AS tr_compensation
    FROM tagged
    GROUP BY ALL
"""

HEALTH_PLANS = """
    WITH plans AS (
        SELECT
            f.FORM_YEAR,
            f.plan_key,
            f.participants,
            f.naics_2,
            f.state,
            COALESCE(BOOL_OR(
                a.WLFR_BNFT_HEALTH_IND = '1' OR a.WLFR_BNFT_HMO_IND = '1'
                OR a.WLFR_BNFT_PPO_IND = '1' OR a.WLFR_BNFT_DRUG_IND = '1'
            ), FALSE) AS has_insured_medical
        FROM filings f
        LEFT JOIN SCH_A a USING (ACK_ID)
        WHERE f.welfare_codes LIKE '%4A%'
          AND f.entity_type = '2'
          AND f.participants >= 100
        GROUP BY ALL
    )
    SELECT
        FORM_YEAR AS year,
        CASE
            WHEN participants < 250 THEN '100–249'
            WHEN participants < 500 THEN '250–499'
            WHEN participants < 1000 THEN '500–999'
            WHEN participants < 2500 THEN '1,000–2,499'
            WHEN participants < 5000 THEN '2,500–4,999'
            ELSE '5,000+'
        END AS band,
        naics_2,
        state,
        COUNT(*) AS plans,
        COUNT(*) FILTER (WHERE NOT has_insured_medical) AS self_funded
    FROM plans
    GROUP BY ALL
"""

VOLUNTARY = """
    WITH plans AS (
        SELECT
            f.FORM_YEAR,
            f.plan_key,
            ANY_VALUE(f.participants) AS participants,
            ANY_VALUE(f.naics_2) AS naics_2,
            ANY_VALUE(f.state) AS state,
            BOOL_OR(
                COALESCE(a.WLFR_BNFT_OTHER_IND = '1' OR a.WLFR_BNFT_INDEMNITY_IND = '1', FALSE)
                AND NOT COALESCE(
                    a.WLFR_BNFT_HEALTH_IND = '1' OR a.WLFR_BNFT_HMO_IND = '1' OR a.WLFR_BNFT_PPO_IND = '1'
                    OR a.WLFR_BNFT_DRUG_IND = '1' OR a.WLFR_BNFT_STOP_LOSS_IND = '1'
                    OR a.WLFR_BNFT_DENTAL_IND = '1' OR a.WLFR_BNFT_VISION_IND = '1'
                    OR a.WLFR_BNFT_LIFE_INSUR_IND = '1' OR a.WLFR_BNFT_TEMP_DISAB_IND = '1'
                    OR a.WLFR_BNFT_LONG_TERM_DISAB_IND = '1', FALSE)
            ) AS has_voluntary
        FROM filings f
        JOIN SCH_A a USING (ACK_ID)
        WHERE f.entity_type = '2'
          AND f.participants >= 100
        GROUP BY 1, 2
    )
    SELECT
        FORM_YEAR AS year,
        CASE
            WHEN participants < 250 THEN '100–249'
            WHEN participants < 500 THEN '250–499'
            WHEN participants < 1000 THEN '500–999'
            WHEN participants < 5000 THEN '1,000–4,999'
            ELSE '5,000+'
        END AS band,
        naics_2,
        state,
        COUNT(*) AS plans,
        COUNT(*) FILTER (WHERE has_voluntary) AS with_voluntary
    FROM plans
    GROUP BY ALL
"""


def _firm_case() -> str:
    whens = []
    for firm, (include, exclude) in BROKER_FIRMS.items():
        test = f"regexp_matches(provider, '{include}')"
        if exclude:
            test += f" AND NOT regexp_matches(provider, '{exclude}')"
        whens.append(f"WHEN {test} THEN '{firm}'")
    return "CASE " + "\n".join(whens) + " END"


# Schedule C providers on single-employer welfare plans, tagged to a national firm by name
PROVIDERS = f"""
    SELECT
        f.FORM_YEAR AS year,
        f.plan_key,
        f.naics_2,
        f.state,
        {_firm_case()} AS firm,
        broker_role
    FROM (
        SELECT
            ACK_ID,
            UPPER(TRIM(PROVIDER_OTHER_NAME)) AS provider,
            REGEXP_MATCHES(
                UPPER(COALESCE(PROVIDER_OTHER_RELATION, '')), 'BROKER|AGENT|CONSULT|ADVIS'
            ) AS broker_role
        FROM SCH_C_P1_I2
    ) c
    JOIN filings f USING (ACK_ID)
    WHERE f.entity_type = '2'
      AND f.pension_codes IS NULL
"""

FIRM_PLANS = """
    SELECT year, firm, naics_2, state, COUNT(DISTINCT plan_key) AS plans
    FROM providers
    WHERE firm IS NOT NULL
    GROUP BY ALL
"""

# A plan counts as served by a local broker when it names a broker/agent/consultant on
# Schedule C but none of the national firms
PLAN_YEARS = """
    SELECT
        plan_key,
        year,
        ANY_VALUE(naics_2) AS naics_2,
        ANY_VALUE(state) AS state,
        COALESCE(LIST(DISTINCT firm) FILTER (WHERE firm IS NOT NULL), []) AS firms,
        BOOL_OR(broker_role) AND COUNT(firm) = 0 AS local_broker
    FROM providers
    GROUP BY plan_key, year
"""

# Year-over-year broker moves among plans that file in consecutive years
FIRM_EVENTS = """
    WITH pairs AS (
        SELECT
            cur.year,
            cur.naics_2,
            cur.state,
            cur.firms,
            prev.firms AS firms_prev,
            prev.local_broker AS local_prev
        FROM plan_years cur
        JOIN plan_years prev
          ON prev.plan_key = cur.plan_key AND prev.year = cur.year - 1
    ),
    moves AS (
        SELECT
            year, naics_2, state,
            UNNEST(list_filter(firms, lambda x: NOT list_contains(firms_prev, x))) AS firm,
            CASE
                WHEN local_prev THEN 'won_local'
                WHEN len(firms_prev) > 0 THEN 'won_national'
                ELSE 'won_other'
            END AS event
        FROM pairs
        UNION ALL
        SELECT
            year, naics_2, state,
            UNNEST(list_filter(firms_prev, lambda x: NOT list_contains(firms, x))) AS firm,
            'lost' AS event
        FROM pairs
        UNION ALL
        SELECT
            year, naics_2, state,
            UNNEST(list_filter(firms_prev, lambda x: list_contains(firms, x))) AS firm,
            'kept' AS event
        FROM pairs
    )
    SELECT year, firm, event, naics_2, state, COUNT(*) AS plans
    FROM moves
    GROUP BY ALL
"""


@dataclass(frozen=True)
class Tables:
    """Aggregates behind every chart. Shared across sessions, so never modify them."""

    contracts: pd.DataFrame  # year, line, sector, state, commissions, fees, lives, ...
    health: pd.DataFrame  # year, band, sector, state, plans, self_funded
    voluntary: pd.DataFrame  # year, band, sector, state, plans, with_voluntary
    firm_plans: pd.DataFrame  # year, firm, sector, state, plans
    firm_events: pd.DataFrame  # year, firm, event, sector, state, plans


def _with_sector(df: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    """Replace 2-digit NAICS with a sector name and collapse to the smaller grain."""
    df = df.assign(sector=df["naics_2"].map(NAICS_SECTORS).fillna("Unknown"))
    df["state"] = df["state"].fillna("")
    keys = [c for c in df.columns if c not in value_cols and c != "naics_2"]
    return df.groupby(keys, as_index=False, observed=True)[value_cols].sum()


@st.cache_resource(show_spinner="Reading 2019–2024 Form 5500 filings…")
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
        contracts = con.sql(CONTRACTS).df()
        health = con.sql(HEALTH_PLANS).df()
        voluntary = con.sql(VOLUNTARY).df()

        con.execute(f"CREATE TEMP TABLE providers AS {PROVIDERS}")
        con.execute(f"CREATE TEMP TABLE plan_years AS {PLAN_YEARS}")
        firm_plans = con.sql(FIRM_PLANS).df()
        firm_events = con.sql(FIRM_EVENTS).df()

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
            ],
        ),
        health=_with_sector(health, ["plans", "self_funded"]),
        voluntary=_with_sector(voluntary, ["plans", "with_voluntary"]),
        firm_plans=_with_sector(firm_plans, ["plans"]),
        firm_events=_with_sector(firm_events, ["plans"]),
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
