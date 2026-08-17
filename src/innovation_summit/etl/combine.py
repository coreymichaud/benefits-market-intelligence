import pandas as pd
from collections import defaultdict
from innovation_summit.config import RAW_DATA_PATH, COMBINED_DATA_PATH

# Creating combined folder
COMBINED_DATA_PATH.mkdir(parents=True, exist_ok=True)

# Load Form 5500 data and combine them
F5500_PATH = RAW_DATA_PATH / "Form 5500"
COMBINED_F5500_PATH = COMBINED_DATA_PATH / "F5500.parquet"

# All `NUMERIC` columns from data from the folder `Form 5500/`
F5500_numeric_cols = [
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
    "NUM_SCH_DCG_ATTACHED_CNT"   
]

# All `DATE` columns from data from the folder `Form 5500/`
F5500_date_cols = [
    "FORM_PLAN_YEAR_BEGIN_DATE",
    "PLAN_EFF_DATE",
    "ADMIN_SIGNED_DATE",
    "SPONS_SIGNED_DATE",
    "DFE_SIGNED_DATE",
    "DATE_RECEIVED",
    "ADMIN_MANUAL_SIGNED_DATE",
    "SPONS_MANUAL_SIGNED_DATE",
    "DFE_MANUAL_SIGNED_DATE"
]

# Set all dtypes to string
dtypes = defaultdict(lambda: "string")

# Set all dtypes where the column is NUMERIC from the `.txt` file to Float64
dtypes.update({
    column: "Float64"
    for column in F5500_numeric_cols
})

print("[READING] Form 5500 data...")

# Read all data
F5500_19 = pd.read_csv(F5500_PATH / "F_5500_2019_Latest/f_5500_2019_latest.csv", dtype=dtypes, parse_dates=F5500_date_cols)
F5500_20 = pd.read_csv(F5500_PATH / "F_5500_2020_Latest/f_5500_2020_latest.csv", dtype=dtypes, parse_dates=F5500_date_cols)
F5500_21 = pd.read_csv(F5500_PATH / "F_5500_2021_Latest/f_5500_2021_latest.csv", dtype=dtypes, parse_dates=F5500_date_cols)
F5500_22 = pd.read_csv(F5500_PATH / "F_5500_2022_Latest/f_5500_2022_latest.csv", dtype=dtypes, parse_dates=F5500_date_cols)
F5500_23 = pd.read_csv(F5500_PATH / "F_5500_2023_Latest/f_5500_2023_latest.csv", dtype=dtypes, parse_dates=F5500_date_cols)
F5500_24 = pd.read_csv(F5500_PATH / "F_5500_2024_Latest/f_5500_2024_latest.csv", dtype=dtypes, parse_dates=F5500_date_cols)

# Add the year this data was given
F5500_19["FORM_YEAR"] = "2019"
F5500_20["FORM_YEAR"] = "2020"
F5500_21["FORM_YEAR"] = "2021"
F5500_22["FORM_YEAR"] = "2022"
F5500_23["FORM_YEAR"] = "2023"
F5500_24["FORM_YEAR"] = "2024"

# Concatenate all dataframes into one for ease of use
F5500 = pd.concat([F5500_19, F5500_20, F5500_21, F5500_22, F5500_23, F5500_24], ignore_index=True)

print(f"[SUCCESSFUL] Rows: {F5500.shape[0]} & Columns: {F5500.shape[1]}")

# Save dataframe to parquet
print("[SAVING] F5500 dataframe to parquet...\n")
F5500.to_parquet(COMBINED_F5500_PATH)


# Load Form 5500 Schedule A data and combine them
SCH_A_PATH = RAW_DATA_PATH / "Form 5500 Schedule A"
COMBINED_SCH_A_PATH = COMBINED_DATA_PATH / "SCH_A.parquet"

# All `NUMERIC` columns from data from the folder `Form 5500 Schedule A/`
SCH_A_numeric_cols = [
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
    "WLFR_ACQUIS_COST_AMT"
]

# All `DATE` columns from data from the folder `Form 5500 Schedule A/`
SCH_A_date_cols = [
    "SCH_A_PLAN_YEAR_BEGIN_DATE",
    "SCH_A_PLAN_YEAR_END_DATE",
    "INS_POLICY_FROM_DATE",
    "INS_POLICY_TO_DATE"
]

# Set all dtypes to string
dtypes = defaultdict(lambda: "string")

# Set all dtypes where the column is NUMERIC from the `.txt` file to Float64
dtypes.update({
    column: "Float64"
    for column in SCH_A_numeric_cols
})

print("[READING] Form 5500 Schedule A data...")

# Read all data
SCH_A_19 = pd.read_csv(SCH_A_PATH / "F_SCH_A_2019_Latest/F_SCH_A_2019_latest.csv", dtype=dtypes, parse_dates=SCH_A_date_cols)
SCH_A_20 = pd.read_csv(SCH_A_PATH / "F_SCH_A_2020_Latest/F_SCH_A_2020_latest.csv", dtype=dtypes, parse_dates=SCH_A_date_cols)
SCH_A_21 = pd.read_csv(SCH_A_PATH / "F_SCH_A_2021_Latest/F_SCH_A_2021_latest.csv", dtype=dtypes, parse_dates=SCH_A_date_cols)
SCH_A_22 = pd.read_csv(SCH_A_PATH / "F_SCH_A_2022_Latest/F_SCH_A_2022_latest.csv", dtype=dtypes, parse_dates=SCH_A_date_cols)
SCH_A_23 = pd.read_csv(SCH_A_PATH / "F_SCH_A_2023_Latest/F_SCH_A_2023_latest.csv", dtype=dtypes, parse_dates=SCH_A_date_cols)
SCH_A_24 = pd.read_csv(SCH_A_PATH / "F_SCH_A_2024_Latest/F_SCH_A_2024_latest.csv", dtype=dtypes, parse_dates=SCH_A_date_cols)

# Add the year this data was given
SCH_A_19["FORM_YEAR"] = "2019"
SCH_A_20["FORM_YEAR"] = "2020"
SCH_A_21["FORM_YEAR"] = "2021"
SCH_A_22["FORM_YEAR"] = "2022"
SCH_A_23["FORM_YEAR"] = "2023"
SCH_A_24["FORM_YEAR"] = "2024"

# Concatenate all dataframes into one for ease of use
SCH_A = pd.concat([SCH_A_19, SCH_A_20, SCH_A_21, SCH_A_22, SCH_A_23, SCH_A_24], ignore_index=True)

print(f"[SUCCESSFUL] Rows: {SCH_A.shape[0]} & Columns: {SCH_A.shape[1]}")

# Save dataframe to parquet
print("[SAVING] SCH_A dataframe to parquet...\n")
SCH_A.to_parquet(COMBINED_SCH_A_PATH)


# Load Form 5500 Schedule C Part 1, Item 2 data and combine them
SCH_C_P1_I2_PATH = RAW_DATA_PATH / "Form 5500 Schedule C Part 1, Item 2"
COMBINED_SCH_C_P1_I2_PATH = COMBINED_DATA_PATH / "SCH_C_P1_I2.parquet"

# All `NUMERIC` columns from data from the folder `Form 5500 Schedule C Part 1, Item 2/`
SCH_C_P1_I2_numeric_cols = [
    "ROW_ORDER",
    "PROVIDER_OTHER_DIRECT_COMP_AMT",
    "PROV_OTHER_TOT_IND_COMP_AMT"
]

# Set all dtypes to string
dtypes = defaultdict(lambda: "string")

# Set all dtypes where the column is NUMERIC from the `.txt` file to Float64
dtypes.update({
    column: "Float64"
    for column in SCH_C_P1_I2_numeric_cols
})

print("[READING] Form 5500 Schedule C Part 1, Item 2 data...")

# Read all data
SCH_C_P1_I2_19 = pd.read_csv(SCH_C_P1_I2_PATH / "F_SCH_C_PART1_ITEM2_2019_Latest/F_SCH_C_PART1_ITEM2_2019_Latest.csv", dtype=dtypes)
SCH_C_P1_I2_20 = pd.read_csv(SCH_C_P1_I2_PATH / "F_SCH_C_PART1_ITEM2_2020_Latest/F_SCH_C_PART1_ITEM2_2020_Latest.csv", dtype=dtypes)
SCH_C_P1_I2_21 = pd.read_csv(SCH_C_P1_I2_PATH / "F_SCH_C_PART1_ITEM2_2021_Latest/F_SCH_C_PART1_ITEM2_2021_Latest.csv", dtype=dtypes)
SCH_C_P1_I2_22 = pd.read_csv(SCH_C_P1_I2_PATH / "F_SCH_C_PART1_ITEM2_2022_Latest/F_SCH_C_PART1_ITEM2_2022_Latest.csv", dtype=dtypes)
SCH_C_P1_I2_23 = pd.read_csv(SCH_C_P1_I2_PATH / "F_SCH_C_PART1_ITEM2_2023_Latest/F_SCH_C_PART1_ITEM2_2023_Latest.csv", dtype=dtypes)
SCH_C_P1_I2_24 = pd.read_csv(SCH_C_P1_I2_PATH / "F_SCH_C_PART1_ITEM2_2024_Latest/F_SCH_C_PART1_ITEM2_2024_Latest.csv", dtype=dtypes)

# Add the year this data was given
SCH_C_P1_I2_19["FORM_YEAR"] = "2019"
SCH_C_P1_I2_20["FORM_YEAR"] = "2020"
SCH_C_P1_I2_21["FORM_YEAR"] = "2021"
SCH_C_P1_I2_22["FORM_YEAR"] = "2022"
SCH_C_P1_I2_23["FORM_YEAR"] = "2023"
SCH_C_P1_I2_24["FORM_YEAR"] = "2024"

# Concatenate all dataframes into one for ease of use
SCH_C_P1_I2 = pd.concat([SCH_C_P1_I2_19, SCH_C_P1_I2_20, SCH_C_P1_I2_21, SCH_C_P1_I2_22, SCH_C_P1_I2_23, SCH_C_P1_I2_24], ignore_index=True)

print(f"[SUCCESSFUL] Rows: {SCH_C_P1_I2.shape[0]} & Columns: {SCH_C_P1_I2.shape[1]}")

# Save dataframe to parquet
print("[SAVING] SCH_C_P1_I2 dataframe to parquet...")
SCH_C_P1_I2.to_parquet(COMBINED_SCH_C_P1_I2_PATH)