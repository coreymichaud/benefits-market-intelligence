import duckdb
from benefits_market_intelligence.config.paths import DB_PATH

# Column definitions from the layout.txt file packaged with the data from DOL EFAST
F_5500_NUMERIC_COLS = [
    "TOT_PARTCP_BOY_CNT",
    "TOT_ACTIVE_PARTCP_CNT",
    "RTD_SEP_PARTCP_RCVG_CNT",
    "RTD_SEP_PARTCP_FUT_CNT",
    "SUBTL_ACT_RTD_SEP_CNT",
    "BENEF_RCVG_BNFT_CNT",
    "TOT_ACT_RTD_SEP_BENEF_CNT",
    "PARTCP_ACCOUNT_BAL_CNT",
    "SEP_PARTCP_PARTL_VSTD_CNT",
    "CONTRIB_EMPLRS_CNT",
    "TOT_ACT_PARTCP_BOY_CNT",
    "PARTCP_ACCOUNT_BAL_CNT_BOY",
    "NUM_SCH_DCG_ATTACHED_CNT",
]

F_5500_DATE_COLS = [
    "FORM_PLAN_YEAR_BEGIN_DATE",
    "PLAN_EFF_DATE",
    "ADMIN_SIGNED_DATE",
    "SPONS_SIGNED_DATE",
    "DFE_SIGNED_DATE",
    "DATE_RECEIVED",
    "ADMIN_MANUAL_SIGNED_DATE",
    "SPONS_MANUAL_SIGNED_DATE",
    "DFE_MANUAL_SIGNED_DATE",
]

SCH_A_NUMERIC_COLS = [
    "FORM_ID",
    "INS_BROKER_COMM_TOT_AMT",
    "INS_BROKER_FEES_TOT_AMT",
    "PENSION_EOY_GEN_ACCT_AMT",
    "PENSION_EOY_SEP_ACCT_AMT",
    "PENSION_PREM_PAID_TOT_AMT",
    "PENSION_UNPAID_PREMIUM_AMT",
    "PENSION_CONTRACT_COST_AMT",
    "PENSION_END_PREV_BAL_AMT",
    "PENSION_CONTRIB_DEP_AMT",
    "PENSION_DIVND_CR_DEP_AMT",
    "PENSION_INT_CR_DUR_YR_AMT",
    "PENSION_TRANSFER_FROM_AMT",
    "PENSION_OTHER_AMT",
    "PENSION_TOT_ADDITIONS_AMT",
    "PENSION_TOT_BAL_ADDN_AMT",
    "PENSION_BNFTS_DSBRSD_AMT",
    "PENSION_ADMIN_CHRG_AMT",
    "PENSION_TRANSFER_TO_AMT",
    "PENSION_OTH_DED_AMT",
    "PENSION_TOT_DED_AMT",
    "PENSION_EOY_BAL_AMT",
    "WLFR_PREMIUM_RCVD_AMT",
    "WLFR_UNPAID_DUE_AMT",
    "WLFR_RESERVE_AMT",
    "WLFR_TOT_EARNED_PREM_AMT",
    "WLFR_CLAIMS_PAID_AMT",
    "WLFR_INCR_RESERVE_AMT",
    "WLFR_INCURRED_CLAIM_AMT",
    "WLFR_CLAIMS_CHRGD_AMT",
    "WLFR_RET_COMMISSIONS_AMT",
    "WLFR_RET_ADMIN_AMT",
    "WLFR_RET_OTH_COST_AMT",
    "WLFR_RET_OTH_EXPENSE_AMT",
    "WLFR_RET_TAXES_AMT",
    "WLFR_RET_CHARGES_AMT",
    "WLFR_RET_OTH_CHRGS_AMT",
    "WLFR_RET_TOT_AMT",
    "WLFR_REFUND_AMT",
    "WLFR_HELD_BNFTS_AMT",
    "WLFR_CLAIMS_RESERVE_AMT",
    "WLFR_OTH_RESERVE_AMT",
    "WLFR_DIVNDS_DUE_AMT",
    "WLFR_TOT_CHARGES_PAID_AMT",
    "WLFR_ACQUIS_COST_AMT",
]

SCH_A_DATE_COLS = [
    "SCH_A_PLAN_YEAR_BEGIN_DATE",
    "SCH_A_PLAN_YEAR_END_DATE",
    "INS_POLICY_FROM_DATE",
    "INS_POLICY_TO_DATE",
]

SCH_C_P1_I2_NUMERIC_COLS = [
    "ROW_ORDER",
    "PROVIDER_OTHER_DIRECT_COMP_AMT",
    "PROV_OTHER_TOT_IND_COMP_AMT",
]

SCH_C_P1_I2_DATE_COLS = []


# Helper definitions
def create_silver_table(
    con: duckdb.DuckDBPyConnection,
    silver_table: str,
    bronze_prefix: str,
    numeric_cols: list[str],
    date_cols: list[str],
) -> None:
    """
    Combine yearly bronze tables into one silver table.

    Handles schema differences between years:
    - Columns present in all years are combined normally.
    - Columns missing from a year become NULL for that year.
    - Numeric columns are cast to DOUBLE.
    - Date columns are cast to DATE.
    - All other columns remain VARCHAR.
    - FORM_YEAR is added as an INTEGER.
    """

    years = range(2019, 2025)

    numeric_cols = set(numeric_cols)
    date_cols = set(date_cols)

    all_columns = set()
    year_columns = {}

    for year in years:
        bronze_table = f"{bronze_prefix}_{year}_Latest"

        columns = con.execute(f'DESCRIBE bronze."{bronze_table}"').fetchall()

        column_names = {column[0] for column in columns}

        year_columns[year] = column_names
        all_columns.update(column_names)

    # Sort for consistent column ordering
    all_columns = sorted(all_columns)

    selects = []

    for year in years:
        bronze_table = f"{bronze_prefix}_{year}_Latest"

        select_columns = []

        for column_name in all_columns:
            quoted_column = f'"{column_name}"'

            # Column does not exist in this year's table
            if column_name not in year_columns[year]:
                expression = f"NULL AS {quoted_column}"

            # Numeric column
            elif column_name in numeric_cols:
                expression = f"TRY_CAST({quoted_column} AS DOUBLE) AS {quoted_column}"

            # Date column
            elif column_name in date_cols:
                expression = f"TRY_CAST({quoted_column} AS DATE) AS {quoted_column}"

            # Everything else stays VARCHAR
            else:
                expression = quoted_column

            select_columns.append(expression)

        # Add the year represented by this source table
        select_columns.append(f"{year} AS FORM_YEAR")

        selects.append(
            f"""
            SELECT
                {", ".join(select_columns)}
            FROM bronze."{bronze_table}"
            """
        )

    union_query = "\nUNION ALL\n".join(selects)

    con.execute(
        f"""
        CREATE OR REPLACE TABLE silver."{silver_table}" AS
        {union_query}
        """
    )


print("[STARTING] Silver transformation...")

with duckdb.connect(DB_PATH) as con:
    # Create silver schema
    con.execute("CREATE SCHEMA IF NOT EXISTS silver")

    # Form 5500
    print("[PROCESSING] Form 5500...")

    create_silver_table(
        con=con,
        silver_table="F_5500",
        bronze_prefix="F_5500",
        numeric_cols=F_5500_NUMERIC_COLS,
        date_cols=F_5500_DATE_COLS,
    )

    f5500_rows = con.execute("SELECT COUNT(*) FROM silver.F_5500").fetchone()[0]

    f5500_columns = con.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_schema = 'silver'
          AND table_name = 'F_5500'
        """
    ).fetchone()[0]

    print(f"[SUCCESSFUL] F_5500: {f5500_rows:,} rows × {f5500_columns} columns")

    # Form 5500 Schedule A
    print("[PROCESSING] Form 5500 Schedule A...")

    create_silver_table(
        con=con,
        silver_table="SCH_A",
        bronze_prefix="F_SCH_A",
        numeric_cols=SCH_A_NUMERIC_COLS,
        date_cols=SCH_A_DATE_COLS,
    )

    sch_a_rows = con.execute("SELECT COUNT(*) FROM silver.SCH_A").fetchone()[0]

    sch_a_columns = con.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_schema = 'silver'
          AND table_name = 'SCH_A'
        """
    ).fetchone()[0]

    print(f"[SUCCESSFUL] SCH_A: {sch_a_rows:,} rows × {sch_a_columns} columns")

    # Form 5500 Schedule C Part 1 Item 2
    print("[PROCESSING] Form 5500 Schedule C Part 1 Item 2...")

    create_silver_table(
        con=con,
        silver_table="SCH_C_P1_I2",
        bronze_prefix="F_SCH_C_PART1_ITEM2",
        numeric_cols=SCH_C_P1_I2_NUMERIC_COLS,
        date_cols=SCH_C_P1_I2_DATE_COLS,
    )

    sch_c_rows = con.execute("SELECT COUNT(*) FROM silver.SCH_C_P1_I2").fetchone()[0]

    sch_c_columns = con.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_schema = 'silver'
          AND table_name = 'SCH_C_P1_I2'
        """
    ).fetchone()[0]

    print(f"[SUCCESSFUL] SCH_C_P1_I2: {sch_c_rows:,} rows x {sch_c_columns} columns")


print("[FINISHED] Silver tables successfully created!")
