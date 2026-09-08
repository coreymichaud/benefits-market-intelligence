import duckdb
from benefits_market_intelligence.config.paths import DB_PATH, EXPORTS_PATH

# F_5500 columns to include
F_5500_top_cols = [
    "ACK_ID",
    "SPONS_DFE_EIN",
    "SPONS_DFE_PN",
    "SPONS_DFE_MAIL_US_ADDRESS1",
    "FORM_PLAN_YEAR_BEGIN_DATE",
    "TOT_PARTCP_BOY_CNT",
    "TOT_ACTIVE_PARTCP_CNT",
    "BUSINESS_CODE",
    "TYPE_PLAN_ENTITY_CD",
    "TYPE_PENSION_BNFT_CODE",
    "TYPE_WELFARE_BNFT_CODE",
    "SCH_R_ATTACHED_IND",
    "SCH_MB_ATTACHED_IND",
    "SCH_SB_ATTACHED_IND",
    "SCH_H_ATTACHED_IND",
    "SCH_I_ATTACHED_IND",
    "SCH_A_ATTACHED_IND",
    "SCH_C_ATTACHED_IND",
    "SCH_D_ATTACHED_IND",
    "SCH_G_ATTACHED_IND",
    "SCH_DCG_ATTACHED_IND",
    "SCH_MEP_ATTACHED_IND",
    "FORM_YEAR",
]

# SCH_A columns to include
SCH_A_top_cols = [
    "ACK_ID",
    "INS_CARRIER_NAME",
    "WLFR_BNFT_HEALTH_IND",
    "WLFR_BNFT_DENTAL_IND",
    "WLFR_BNFT_VISION_IND",
    "WLFR_BNFT_LIFE_INSUR_IND",
    "WLFR_BNFT_TEMP_DISAB_IND",
    "WLFR_BNFT_UNEMP_IND",
    "WLFR_BNFT_DRUG_IND",
    "WLFR_BNFT_STOP_LOSS_IND",
    "WLFR_BNFT_HMO_IND",
    "WLFR_BNFT_PPO_IND",
    "WLFR_BNFT_INDEMNITY_IND",
    "WLFR_BNFT_OTHER_IND",
    "WLFR_REFUND_CASH_IND",
    "WLFR_REFUND_CREDIT_IND",
    "INS_FAIL_PROVIDE_INFO_IND",
    "PENSION_PREM_PAID_TOT_AMT",
    "PENSION_UNPAID_PREMIUM_AMT",
    "WLFR_PREMIUM_RCVD_AMT",
    "WLFR_UNPAID_DUE_AMT",
    "WLFR_TOT_EARNED_PREM_AMT",
    "INS_CARRIER_NAME",
    "INS_BROKER_COMM_TOT_AMT",
    "INS_BROKER_FEES_TOT_AMT",
    "INS_PRSN_COVERED_EOY_CNT",
    "FORM_YEAR",
]

# SCH_C_P1_I2 columns to include
SCH_C_P1_I2_top_cols = [
    "ACK_ID",
    "PROVIDER_OTHER_NAME",
    "PROVIDER_OTHER_EIN",
    "PROVIDER_OTHER_SRVC_CODES",
    "PROVIDER_OTHER_RELATION",
    "PROVIDER_OTHER_DIRECT_COMP_AMT",
    "PROV_OTHER_INDIRECT_COMP_IND",
    "PROV_OTHER_TOT_IND_COMP_AMT",
    "FORM_YEAR",
]

# Mapping of tables to their top columns
tables_tcols = {
    "F_5500": F_5500_top_cols,
    "SCH_A": SCH_A_top_cols,
    "SCH_C_P1_I2": SCH_C_P1_I2_top_cols,
}


with duckdb.connect(DB_PATH) as con:
    con.execute("CREATE SCHEMA IF NOT EXISTS gold")

    for table, columns in tables_tcols.items():
        con.execute(
            f"""
        CREATE OR REPLACE TABLE gold.{table} AS
        SELECT {", ".join(columns)}
        FROM silver.{table};
        """
        )

        # Saving exports to share
        EXPORTS_PATH.mkdir(parents=True, exist_ok=True)
        con.execute(
            f"COPY gold.{table} TO '{EXPORTS_PATH / table}.parquet' (FORMAT PARQUET);"
        )


print("[FINISHED] Gold schema successfully created!")
