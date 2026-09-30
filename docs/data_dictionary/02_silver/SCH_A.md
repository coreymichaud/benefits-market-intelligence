# silver.SCH_A

The six `bronze."F_SCH_A_{year}_Latest"` tables stacked into one by `02_silver.py`, with `FORM_YEAR` added. Columns are in alphabetical order with `FORM_YEAR` last. A column missing from a year's file is null for that year. Columns in the script's numeric list are cast to `DOUBLE` and columns in its date list to `DATE` with `TRY_CAST`, so values that don't parse become null; everything else stays `VARCHAR`. No rows are filtered.

- **Rows:** 2,015,924
- **Columns:** 91

| Column | Type | Description |
| --- | --- | --- |
| `ACK_ID` | VARCHAR | Acknowledgment ID (PK) |
| `ALLOC_CONTRACTS_GROUP_IND` | VARCHAR | Group allocated contracts |
| `ALLOC_CONTRACTS_INDIV_IND` | VARCHAR | Individual allocated contracts |
| `ALLOC_CONTRACTS_OTHER_IND` | VARCHAR | Other allocated contracts |
| `ALLOC_CONTRACTS_OTHER_TEXT` | VARCHAR | Other allocated contracts details |
| `FORM_ID` | DOUBLE | Form ID |
| `INS_BROKER_COMM_TOT_AMT` | DOUBLE | Total broker commissions |
| `INS_BROKER_FEES_TOT_AMT` | DOUBLE | Total broker fees |
| `INS_CARRIER_EIN` | VARCHAR | Insurance carrier EIN |
| `INS_CARRIER_NAIC_CODE` | VARCHAR | Insurance carrier NAIC code |
| `INS_CARRIER_NAME` | VARCHAR | Insurance carrier name |
| `INS_CONTRACT_NUM` | VARCHAR | Insurance contract number |
| `INS_FAIL_PROVIDE_INFO_IND` | VARCHAR | Failure to provide information indicator |
| `INS_FAIL_PROVIDE_INFO_TEXT` | VARCHAR | Failure to provide information details |
| `INS_POLICY_FROM_DATE` | DATE | Policy start date |
| `INS_POLICY_TO_DATE` | DATE | Policy end date |
| `INS_PRSN_COVERED_EOY_CNT` | VARCHAR | Persons covered at year end |
| `PENSION_ADMIN_CHRG_AMT` | DOUBLE | Pension administrative charges |
| `PENSION_BASIS_RATES_TEXT` | VARCHAR | Pension basis and rates |
| `PENSION_BNFTS_DSBRSD_AMT` | DOUBLE | Pension benefits distributed |
| `PENSION_CONTRACT_COST_AMT` | DOUBLE | Pension contract cost |
| `PENSION_CONTRIB_DEP_AMT` | DOUBLE | Pension deposits/contributions |
| `PENSION_COST_TEXT` | VARCHAR | Pension contract cost details |
| `PENSION_DIVND_CR_DEP_AMT` | DOUBLE | Pension dividends and credits deposited |
| `PENSION_END_PREV_BAL_AMT` | DOUBLE | Pension prior year ending balance |
| `PENSION_EOY_BAL_AMT` | DOUBLE | Pension ending balance |
| `PENSION_EOY_GEN_ACCT_AMT` | DOUBLE | Pension general account balance |
| `PENSION_EOY_SEP_ACCT_AMT` | DOUBLE | Pension separate account balance |
| `PENSION_INT_CR_DUR_YR_AMT` | DOUBLE | Pension interest credited during year |
| `PENSION_OTHER_AMT` | DOUBLE | Other pension additions |
| `PENSION_OTHER_TEXT` | VARCHAR | Other pension additions details |
| `PENSION_OTH_DED_AMT` | DOUBLE | Other pension deductions |
| `PENSION_OTH_DED_TEXT` | VARCHAR | Other pension deductions details |
| `PENSION_PREM_PAID_TOT_AMT` | DOUBLE | Total pension premiums paid |
| `PENSION_TOT_ADDITIONS_AMT` | DOUBLE | Total pension additions |
| `PENSION_TOT_BAL_ADDN_AMT` | DOUBLE | Total balance additions |
| `PENSION_TOT_DED_AMT` | DOUBLE | Total pension deductions |
| `PENSION_TRANSFER_FROM_AMT` | DOUBLE | Pension transfers in |
| `PENSION_TRANSFER_TO_AMT` | DOUBLE | Pension transfers out |
| `PENSION_UNPAID_PREMIUM_AMT` | DOUBLE | Unpaid pension premiums |
| `PENS_DISTR_BNFT_TERM_PLN_IND` | VARCHAR | Benefit distribution termination plan |
| `SCH_A_EIN` | VARCHAR | Schedule A EIN |
| `SCH_A_PLAN_NUM` | VARCHAR | Schedule A plan number |
| `SCH_A_PLAN_YEAR_BEGIN_DATE` | DATE | Plan year start date |
| `SCH_A_PLAN_YEAR_END_DATE` | DATE | Plan year end date |
| `UNALLOC_CONTRACTS_DEP_ADM_IND` | VARCHAR | Unallocated contracts dependent on administrator |
| `UNALLOC_CONTRACTS_OTHER_IND` | VARCHAR | Other unallocated contracts |
| `UNALLOC_CONTRACTS_OTHER_TEXT` | VARCHAR | Other unallocated contracts details |
| `UNAL_CONTRACTS_GUAR_INVEST_IND` | VARCHAR | Unallocated guaranteed investment contracts |
| `UNAL_CONTRAC_IMM_PART_GUAR_IND` | VARCHAR | Unallocated contracts with immediate participation guarantee |
| `WLFR_ACQUIS_COST_AMT` | DOUBLE | Acquisition cost |
| `WLFR_ACQUIS_COST_TEXT` | VARCHAR | Acquisition cost details |
| `WLFR_BNFT_DENTAL_IND` | VARCHAR | Dental benefit indicator |
| `WLFR_BNFT_DRUG_IND` | VARCHAR | Prescription drug benefit indicator |
| `WLFR_BNFT_HEALTH_IND` | VARCHAR | Health benefit indicator |
| `WLFR_BNFT_HMO_IND` | VARCHAR | HMO benefit indicator |
| `WLFR_BNFT_INDEMNITY_IND` | VARCHAR | Indemnity benefit indicator |
| `WLFR_BNFT_LIFE_INSUR_IND` | VARCHAR | Life insurance benefit indicator |
| `WLFR_BNFT_LONG_TERM_DISAB_IND` | VARCHAR | Long-term disability benefit indicator |
| `WLFR_BNFT_OTHER_IND` | VARCHAR | Other welfare benefit indicator |
| `WLFR_BNFT_PPO_IND` | VARCHAR | PPO benefit indicator |
| `WLFR_BNFT_STOP_LOSS_IND` | VARCHAR | Stop-loss benefit indicator |
| `WLFR_BNFT_TEMP_DISAB_IND` | VARCHAR | Temporary disability benefit indicator |
| `WLFR_BNFT_UNEMP_IND` | VARCHAR | Unemployment benefit indicator |
| `WLFR_BNFT_VISION_IND` | VARCHAR | Vision benefit indicator |
| `WLFR_CLAIMS_CHRGD_AMT` | DOUBLE | Claims charged |
| `WLFR_CLAIMS_PAID_AMT` | DOUBLE | Claims paid |
| `WLFR_CLAIMS_RESERVE_AMT` | DOUBLE | Claims reserve |
| `WLFR_DIVNDS_DUE_AMT` | DOUBLE | Dividends due |
| `WLFR_HELD_BNFTS_AMT` | DOUBLE | Benefits held |
| `WLFR_INCR_RESERVE_AMT` | DOUBLE | Increase in reserves |
| `WLFR_INCURRED_CLAIM_AMT` | DOUBLE | Incurred claims |
| `WLFR_OTH_RESERVE_AMT` | DOUBLE | Other reserve |
| `WLFR_PREMIUM_RCVD_AMT` | DOUBLE | Premiums received |
| `WLFR_REFUND_AMT` | DOUBLE | Refund amount |
| `WLFR_REFUND_CASH_IND` | VARCHAR | Cash refund indicator |
| `WLFR_REFUND_CREDIT_IND` | VARCHAR | Credit refund indicator |
| `WLFR_RESERVE_AMT` | DOUBLE | Reserve amount |
| `WLFR_RET_ADMIN_AMT` | DOUBLE | Retained administrative amount |
| `WLFR_RET_CHARGES_AMT` | DOUBLE | Retained charges |
| `WLFR_RET_COMMISSIONS_AMT` | DOUBLE | Retained commissions |
| `WLFR_RET_OTH_CHRGS_AMT` | DOUBLE | Retained other charges |
| `WLFR_RET_OTH_COST_AMT` | DOUBLE | Retained other costs |
| `WLFR_RET_OTH_EXPENSE_AMT` | DOUBLE | Retained other expenses |
| `WLFR_RET_TAXES_AMT` | DOUBLE | Retained taxes |
| `WLFR_RET_TOT_AMT` | DOUBLE | Total retained amount |
| `WLFR_TOT_CHARGES_PAID_AMT` | DOUBLE | Total charges paid |
| `WLFR_TOT_EARNED_PREM_AMT` | DOUBLE | Total earned premiums |
| `WLFR_TYPE_BNFT_OTH_TEXT` | VARCHAR | Other welfare benefit details |
| `WLFR_UNPAID_DUE_AMT` | DOUBLE | Unpaid premiums due |
| `FORM_YEAR` | INTEGER | Form year of the source file, added in silver |
