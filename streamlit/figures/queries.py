"""SQL behind the dashboard's aggregate tables.

Same rules as notebooks/analysis.ipynb; table names point at parquet views instead of gold.*.
data.load runs these in order, since later queries read temp tables built by earlier ones.
"""

from figures.constants import BROKER_FIRMS, LAST

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

# Every Schedule A contract on a kept filing, with the notebook's screens as flags. The
# aggregates below filter on these flags, so each rule is written once.
CONTRACTS_ALL = f"""
    WITH flagged AS (
        SELECT
            a.ACK_ID,
            f.FORM_YEAR AS year,
            f.plan_key,
            f.naics_2,
            f.state,
            UPPER(TRIM(a.INS_CARRIER_NAME)) AS carrier_name,
            -- One carrier per NAIC code, else per EIN, else per name (see docs/name-matching.md)
            COALESCE(
                NULLIF(LTRIM(TRIM(a.INS_CARRIER_NAIC_CODE), '0'), ''),
                'EIN ' || NULLIF(TRIM(a.INS_CARRIER_EIN), ''),
                UPPER(TRIM(a.INS_CARRIER_NAME))
            ) AS carrier_key,
            COALESCE(a.INS_BROKER_COMM_TOT_AMT, 0) AS commissions,
            COALESCE(a.INS_BROKER_FEES_TOT_AMT, 0) AS fees,
            a.INS_BROKER_COMM_TOT_AMT IS NULL AND a.INS_BROKER_FEES_TOT_AMT IS NULL AS blank_pay,
            TRY_CAST(a.INS_PRSN_COVERED_EOY_CNT AS DOUBLE) AS lives,
            GREATEST(COALESCE(a.WLFR_TOT_CHARGES_PAID_AMT, 0),
                     COALESCE(a.WLFR_TOT_EARNED_PREM_AMT, 0)) AS premium,
            -- Policy year under 360 days; null when the dates are missing. Never annualized.
            DATE_DIFF('day', a.INS_POLICY_FROM_DATE, a.INS_POLICY_TO_DATE) + 1 < 360
                AS partial_year,
            COALESCE(a.WLFR_BNFT_OTHER_IND = '1' OR a.WLFR_BNFT_INDEMNITY_IND = '1', FALSE)
                AS other_or_indemnity,
            {COVERAGE_FLAGS}
        FROM SCH_A a
        JOIN filings f USING (ACK_ID)
    ),
    lined AS (
        SELECT
            *,
            {LINE_CASE} AS line,
            -- Same voluntary rule as the VOLUNTARY query: other or indemnity, no core line
            other_or_indemnity AND NOT (med OR sl OR den OR vis OR life OR dis) AS voluntary,
            -- Data-quality screen: drop negative amounts, missing lives, and implausible $/life
            commissions >= 0
                AND fees >= 0
                AND COALESCE(lives BETWEEN 1 AND 1000000, FALSE)
                AND (commissions + fees) / lives <= 2500 AS in_pool
        FROM flagged
    )
    SELECT
        * EXCLUDE (sl, den, vis, life, dis, oth, other_or_indemnity),
        in_pool
            AND line <> 'Unclassified'
            AND premium > 0
            AND premium / lives <= 50000
            AND (commissions + fees) / premium <= 1
            AND premium <= 250000000 AS take_rate_ok
    FROM lined
"""

# tr_* columns only count contracts that also pass the notebook's take-rate screen. blank_*
# columns let the take rate and fee adoption views leave out contracts with blank pay.
CONTRACTS = """
    SELECT
        year,
        line,
        naics_2,
        state,
        SUM(commissions) AS commissions,
        SUM(fees) AS fees,
        SUM(lives) AS lives,
        COUNT(*) AS contracts,
        COUNT(*) FILTER (WHERE fees > 0) AS fee_contracts,
        COALESCE(SUM(premium) FILTER (WHERE take_rate_ok), 0) AS tr_premium,
        COALESCE(SUM(commissions + fees) FILTER (WHERE take_rate_ok), 0) AS tr_compensation,
        COUNT(*) FILTER (WHERE blank_pay) AS blank_contracts,
        COALESCE(SUM(premium) FILTER (WHERE take_rate_ok AND blank_pay), 0) AS blank_tr_premium,
        COUNT(*) FILTER (WHERE partial_year) AS partial_contracts
    FROM contracts_all
    WHERE in_pool
    GROUP BY ALL
"""

# The 25 carriers with the most premium on the take-rate base, each labeled with the name it
# files under most often. Built as its own table first so the contracts are only scanned once
# per query, which keeps memory down.
TOP_CARRIERS = """
    SELECT
        carrier_key,
        MODE(carrier_name) AS carrier,
        SUM(premium) FILTER (WHERE take_rate_ok) AS premium
    FROM contracts_all
    WHERE carrier_key IS NOT NULL
    GROUP BY carrier_key
    ORDER BY premium DESC NULLS LAST
    LIMIT 25
"""

CARRIERS = """
    SELECT
        c.year,
        COALESCE(t.carrier, 'Other carriers') AS carrier,
        c.line,
        c.naics_2,
        c.state,
        COUNT(*) AS contracts,
        COALESCE(SUM(c.premium) FILTER (WHERE c.take_rate_ok), 0) AS tr_premium
    FROM contracts_all c
    LEFT JOIN top_carriers t USING (carrier_key)
    WHERE c.in_pool
    GROUP BY ALL
"""

# Broker pay per plan and year, for checking how much of a state's growth comes from a few plans.
# Plans are identified by a 64-bit hash of the plan key, which is all this needs and keeps it small.
PLAN_PAY = """
    SELECT year, HASH(plan_key) AS plan_id, naics_2, state, SUM(commissions + fees) AS pay
    FROM contracts_all
    WHERE in_pool
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
            WHEN participants < 250 THEN '100-249'
            WHEN participants < 500 THEN '250-499'
            WHEN participants < 1000 THEN '500-999'
            WHEN participants < 2500 THEN '1,000-2,499'
            WHEN participants < 5000 THEN '2,500-4,999'
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
            WHEN participants < 250 THEN '100-249'
            WHEN participants < 500 THEN '250-499'
            WHEN participants < 1000 THEN '500-999'
            WHEN participants < 5000 THEN '1,000-4,999'
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
        provider,
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

# The names that count toward each firm, with the plan-years they appear on
FIRM_NAMES = """
    SELECT firm, provider, COUNT(*) AS plan_years
    FROM providers
    WHERE firm IS NOT NULL
    GROUP BY ALL
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


# One row per single-employer plan with 100+ participants, from its latest kept filing in the
# last two form years: what it insures, with whom, what its brokers are paid and which national
# firm it names on Schedule C
ACCOUNTS = f"""
    WITH latest AS (
        SELECT ACK_ID, FORM_YEAR, plan_key, participants, naics_2, state, welfare_codes
        FROM filings
        WHERE entity_type = '2'
          AND participants >= 100
          AND FORM_YEAR >= {LAST - 1}
        QUALIFY ROW_NUMBER() OVER (PARTITION BY plan_key ORDER BY FORM_YEAR DESC) = 1
    ),
    per_filing AS (
        SELECT
            ACK_ID,
            STRING_AGG(DISTINCT line, ', ' ORDER BY line)
                FILTER (WHERE line <> 'Unclassified') AS lines,
            COUNT(*) AS contracts,
            COALESCE(SUM(commissions + fees) FILTER (WHERE in_pool), 0) AS broker_pay,
            SUM(premium) FILTER (WHERE take_rate_ok) AS tr_premium,
            SUM(commissions + fees) FILTER (WHERE take_rate_ok) AS tr_compensation,
            BOOL_OR(med) AS has_insured_medical,
            BOOL_OR(voluntary) AS has_voluntary,
            COALESCE(BOOL_OR(partial_year), FALSE) AS partial_year
        FROM contracts_all
        WHERE ACK_ID IN (SELECT ACK_ID FROM latest)
        GROUP BY ACK_ID
    ),
    carrier_premium AS (
        SELECT ACK_ID, carrier_name, SUM(premium) AS premium
        FROM contracts_all
        WHERE ACK_ID IN (SELECT ACK_ID FROM latest) AND carrier_name IS NOT NULL
        GROUP BY ALL
    ),
    plan_carriers AS (
        SELECT ACK_ID, STRING_AGG(carrier_name, '; ' ORDER BY premium DESC) AS carriers
        FROM (
            SELECT *
            FROM carrier_premium
            QUALIFY ROW_NUMBER() OVER (PARTITION BY ACK_ID ORDER BY premium DESC) <= 3
        )
        GROUP BY ACK_ID
    )
    SELECT
        l.plan_key,
        l.ACK_ID AS ack_id,
        l.FORM_YEAR AS year,
        f.SPONSOR_DFE_NAME AS sponsor,
        f.SPONS_DFE_MAIL_US_CITY AS city,
        l.state,
        l.naics_2,
        l.participants,
        p.lines,
        c.carriers,
        p.contracts,
        p.broker_pay,
        p.tr_compensation / NULLIF(p.tr_premium, 0) * 100 AS take_rate,
        ARRAY_TO_STRING(LIST_SORT(cur.firms), ', ') AS national_firms,
        COALESCE(LIST_SORT(cur.firms) <> LIST_SORT(prev.firms), FALSE) AS changed_firm,
        l.welfare_codes LIKE '%4A%' AS offers_health,
        l.welfare_codes LIKE '%4A%' AND NOT p.has_insured_medical AS self_funded,
        p.has_voluntary,
        COALESCE(f.AMENDED_IND = '1', FALSE) AS amended,
        p.partial_year
    FROM latest l
    JOIN per_filing p USING (ACK_ID)
    LEFT JOIN plan_carriers c USING (ACK_ID)
    LEFT JOIN F_5500 f USING (ACK_ID)
    LEFT JOIN plan_years cur ON cur.plan_key = l.plan_key AND cur.year = l.FORM_YEAR
    LEFT JOIN plan_years prev ON prev.plan_key = l.plan_key AND prev.year = l.FORM_YEAR - 1
"""

# Latest EFAST receipt date in the data, read from the first 8 digits of ACK_ID
LATEST_RECEIVED = "SELECT MAX(STRPTIME(LEFT(ACK_ID, 8), '%Y%m%d'))::DATE FROM F_5500"
