# gold.SCH_A

A subset of `silver.SCH_A` columns chosen by `03_gold.py`, with every row kept. Types are unchanged from silver. `03_gold.py` also writes this table to `data/exports/SCH_A.parquet`, which the Streamlit dashboard reads.

- **Rows:** 2,015,924
- **Columns:** 35

| Column | Type | Description |
| --- | --- | --- |
| `ACK_ID` | VARCHAR | Acknowledgment ID (PK) |
| `INS_CARRIER_NAME` | VARCHAR | Insurance carrier name |
| `INS_CARRIER_EIN` | VARCHAR | Insurance carrier EIN |
| `INS_CARRIER_NAIC_CODE` | VARCHAR | Insurance carrier NAIC code |
| `INS_POLICY_FROM_DATE` | DATE | Policy start date |
| `INS_POLICY_TO_DATE` | DATE | Policy end date |
| `SCH_A_PLAN_YEAR_BEGIN_DATE` | DATE | Plan year start date |
| `SCH_A_PLAN_YEAR_END_DATE` | DATE | Plan year end date |
| `WLFR_BNFT_HEALTH_IND` | VARCHAR | Health benefit indicator |
| `WLFR_BNFT_DENTAL_IND` | VARCHAR | Dental benefit indicator |
| `WLFR_BNFT_VISION_IND` | VARCHAR | Vision benefit indicator |
| `WLFR_BNFT_LIFE_INSUR_IND` | VARCHAR | Life insurance benefit indicator |
| `WLFR_BNFT_TEMP_DISAB_IND` | VARCHAR | Temporary disability benefit indicator |
| `WLFR_BNFT_UNEMP_IND` | VARCHAR | Unemployment benefit indicator |
| `WLFR_BNFT_DRUG_IND` | VARCHAR | Prescription drug benefit indicator |
| `WLFR_BNFT_STOP_LOSS_IND` | VARCHAR | Stop-loss benefit indicator |
| `WLFR_BNFT_HMO_IND` | VARCHAR | HMO benefit indicator |
| `WLFR_BNFT_PPO_IND` | VARCHAR | PPO benefit indicator |
| `WLFR_BNFT_INDEMNITY_IND` | VARCHAR | Indemnity benefit indicator |
| `WLFR_BNFT_OTHER_IND` | VARCHAR | Other welfare benefit indicator |
| `WLFR_REFUND_CASH_IND` | VARCHAR | Cash refund indicator |
| `WLFR_REFUND_CREDIT_IND` | VARCHAR | Credit refund indicator |
| `INS_FAIL_PROVIDE_INFO_IND` | VARCHAR | Failure to provide information indicator |
| `PENSION_PREM_PAID_TOT_AMT` | DOUBLE | Total pension premiums paid |
| `PENSION_UNPAID_PREMIUM_AMT` | DOUBLE | Unpaid pension premiums |
| `WLFR_PREMIUM_RCVD_AMT` | DOUBLE | Premiums received |
| `WLFR_UNPAID_DUE_AMT` | DOUBLE | Unpaid premiums due |
| `WLFR_TOT_EARNED_PREM_AMT` | DOUBLE | Total earned premiums |
| `INS_BROKER_COMM_TOT_AMT` | DOUBLE | Total broker commissions |
| `INS_BROKER_FEES_TOT_AMT` | DOUBLE | Total broker fees |
| `INS_PRSN_COVERED_EOY_CNT` | VARCHAR | Persons covered at year end |
| `FORM_YEAR` | INTEGER | Form year of the source file, added in silver |
| `WLFR_TOT_CHARGES_PAID_AMT` | DOUBLE | Total charges paid |
| `WLFR_BNFT_LONG_TERM_DISAB_IND` | VARCHAR | Long-term disability benefit indicator |
| `FORM_ID` | DOUBLE | Form ID |
