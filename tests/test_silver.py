import datetime

import duckdb
from conftest import YEARS

from benefits_market_intelligence.config import paths


def query(sql: str) -> list[tuple]:
    with duckdb.connect(paths.DB_PATH) as con:
        return con.execute(sql).fetchall()


def column_types(table: str) -> dict[str, str]:
    return {r[0]: r[1] for r in query(f'describe silver."{table}"')}


def test_combines_the_six_years_into_one_table_per_form(silver):
    for table in ["F_5500", "SCH_A", "SCH_C_P1_I2"]:
        rows = query(
            f'select FORM_YEAR, count(*) from silver."{table}" group by 1 order by 1'
        )
        assert rows == [(year, 2) for year in YEARS]


def test_casts_numeric_date_and_year_columns(silver):
    types = column_types("SCH_A")
    assert types["INS_BROKER_COMM_TOT_AMT"] == "DOUBLE"
    assert types["INS_POLICY_FROM_DATE"] == "DATE"
    assert types["FORM_YEAR"] == "INTEGER"
    assert types["INS_CARRIER_NAME"] == "VARCHAR"
    # Not in the numeric list, so it stays text
    assert types["INS_PRSN_COVERED_EOY_CNT"] == "VARCHAR"


def test_numeric_values_that_do_not_parse_become_null(silver):
    rows = query(
        'select distinct INS_BROKER_COMM_TOT_AMT, INS_BROKER_FEES_TOT_AMT from silver."SCH_A"'
    )
    assert rows == [(1250.5, None)]


def test_dates_are_parsed(silver):
    rows = query(
        'select distinct FORM_PLAN_YEAR_BEGIN_DATE from silver."F_5500" where FORM_YEAR = 2020'
    )
    assert rows == [(datetime.date(2020, 1, 1),)]


def test_columns_missing_from_a_year_are_null_for_that_year(silver):
    rows = query(
        'select FORM_YEAR, count(SCH_DCG_ATTACHED_IND) from silver."F_5500" group by 1 order by 1'
    )
    assert rows == [(2019, 0), (2020, 0), (2021, 2), (2022, 2), (2023, 2), (2024, 2)]


def test_columns_are_sorted_with_form_year_last(silver):
    names = list(column_types("SCH_C_P1_I2"))
    assert names[-1] == "FORM_YEAR"
    assert names[:-1] == sorted(names[:-1])


def test_helper_ignores_listed_columns_that_do_not_exist(silver):
    # SCH_A's numeric list names many pension columns the fake files leave out
    assert "PENSION_EOY_BAL_AMT" in silver["SCH_A_NUMERIC_COLS"]
    assert "PENSION_EOY_BAL_AMT" not in column_types("SCH_A")
