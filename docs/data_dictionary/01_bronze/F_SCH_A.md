# bronze.F_SCH_A_{year}_Latest

One table per form year, loaded as-is from DOL's "Latest" zip for that year by `01_bronze.py`. The CSV is read with `read_csv_auto(..., all_varchar = true)`, so every column in every bronze table is `VARCHAR`. The zip and CSV are stored in `data/raw/Form 5500 Schedule A/`.

## Tables

| Table | Rows | Columns | Source |
| --- | --- | --- | --- |
| `bronze."F_SCH_A_2019_Latest"` | 329,205 | 90 | [F_SCH_A_2019_Latest.zip](https://askebsa.dol.gov/FOIA%20Files/2019/Latest/F_SCH_A_2019_Latest.zip) |
| `bronze."F_SCH_A_2020_Latest"` | 337,515 | 90 | [F_SCH_A_2020_Latest.zip](https://askebsa.dol.gov/FOIA%20Files/2020/Latest/F_SCH_A_2020_Latest.zip) |
| `bronze."F_SCH_A_2021_Latest"` | 333,425 | 90 | [F_SCH_A_2021_Latest.zip](https://askebsa.dol.gov/FOIA%20Files/2021/Latest/F_SCH_A_2021_Latest.zip) |
| `bronze."F_SCH_A_2022_Latest"` | 339,557 | 90 | [F_SCH_A_2022_Latest.zip](https://askebsa.dol.gov/FOIA%20Files/2022/Latest/F_SCH_A_2022_Latest.zip) |
| `bronze."F_SCH_A_2023_Latest"` | 339,966 | 90 | [F_SCH_A_2023_Latest.zip](https://askebsa.dol.gov/FOIA%20Files/2023/Latest/F_SCH_A_2023_Latest.zip) |
| `bronze."F_SCH_A_2024_Latest"` | 337,663 | 90 | [F_SCH_A_2024_Latest.zip](https://askebsa.dol.gov/FOIA%20Files/2024/Latest/F_SCH_A_2024_Latest.zip) |

## Columns

Column names are the CSV headers. Descriptions, layout types and maximum lengths come from the layout file DOL ships in each zip. "Layout type" is what the layout says the field holds; silver uses it to decide casts (see [02_silver/SCH_A.md](../02_silver/SCH_A.md)). "Years" shows which form years include the column; a column added partway through the period is null for earlier years in silver.

| Column | Description | Layout type | Max length | Years |
| --- | --- | --- | --- | --- |
| `ACK_ID` | Acknowledgment ID (PK) | TEXT | 30 | All |
| `FORM_ID` | Form ID | NUMERIC |  | All |
| `SCH_A_PLAN_YEAR_BEGIN_DATE` | Plan year start date | TEXT | 10 | All |
| `SCH_A_PLAN_YEAR_END_DATE` | Plan year end date | TEXT | 10 | All |
| `SCH_A_PLAN_NUM` | Schedule A plan number | TEXT | 3 | All |
| `SCH_A_EIN` | Schedule A EIN | TEXT | 9 | All |
| `INS_CARRIER_NAME` | Insurance carrier name | TEXT | 70 | All |
| `INS_CARRIER_EIN` | Insurance carrier EIN | TEXT | 9 | All |
| `INS_CARRIER_NAIC_CODE` | Insurance carrier NAIC code | TEXT | 5 | All |
| `INS_CONTRACT_NUM` | Insurance contract number | TEXT | 15 | All |
| `INS_PRSN_COVERED_EOY_CNT` | Persons covered at year end | TEXT | 7 | All |
| `INS_POLICY_FROM_DATE` | Policy start date | TEXT | 10 | All |
| `INS_POLICY_TO_DATE` | Policy end date | TEXT | 10 | All |
| `INS_BROKER_COMM_TOT_AMT` | Total broker commissions | NUMERIC |  | All |
| `INS_BROKER_FEES_TOT_AMT` | Total broker fees | NUMERIC |  | All |
| `PENSION_EOY_GEN_ACCT_AMT` | Pension general account balance | NUMERIC |  | All |
| `PENSION_EOY_SEP_ACCT_AMT` | Pension separate account balance | NUMERIC |  | All |
| `PENSION_BASIS_RATES_TEXT` | Pension basis and rates | TEXT | 105 | All |
| `PENSION_PREM_PAID_TOT_AMT` | Total pension premiums paid | NUMERIC |  | All |
| `PENSION_UNPAID_PREMIUM_AMT` | Unpaid pension premiums | NUMERIC |  | All |
| `PENSION_CONTRACT_COST_AMT` | Pension contract cost | NUMERIC |  | All |
| `PENSION_COST_TEXT` | Pension contract cost details | TEXT | 105 | All |
| `ALLOC_CONTRACTS_INDIV_IND` | Individual allocated contracts | TEXT | 1 | All |
| `ALLOC_CONTRACTS_GROUP_IND` | Group allocated contracts | TEXT | 1 | All |
| `ALLOC_CONTRACTS_OTHER_IND` | Other allocated contracts | TEXT | 1 | All |
| `ALLOC_CONTRACTS_OTHER_TEXT` | Other allocated contracts details | TEXT | 105 | All |
| `PENS_DISTR_BNFT_TERM_PLN_IND` | Benefit distribution termination plan | TEXT | 1 | All |
| `UNALLOC_CONTRACTS_DEP_ADM_IND` | Unallocated contracts dependent on administrator | TEXT | 1 | All |
| `UNAL_CONTRAC_IMM_PART_GUAR_IND` | Unallocated contracts with immediate participation guarantee | TEXT | 1 | All |
| `UNAL_CONTRACTS_GUAR_INVEST_IND` | Unallocated guaranteed investment contracts | TEXT | 1 | All |
| `UNALLOC_CONTRACTS_OTHER_IND` | Other unallocated contracts | TEXT | 1 | All |
| `UNALLOC_CONTRACTS_OTHER_TEXT` | Other unallocated contracts details | TEXT | 105 | All |
| `PENSION_END_PREV_BAL_AMT` | Pension prior year ending balance | NUMERIC |  | All |
| `PENSION_CONTRIB_DEP_AMT` | Pension deposits/contributions | NUMERIC |  | All |
| `PENSION_DIVND_CR_DEP_AMT` | Pension dividends and credits deposited | NUMERIC |  | All |
| `PENSION_INT_CR_DUR_YR_AMT` | Pension interest credited during year | NUMERIC |  | All |
| `PENSION_TRANSFER_FROM_AMT` | Pension transfers in | NUMERIC |  | All |
| `PENSION_OTHER_AMT` | Other pension additions | NUMERIC |  | All |
| `PENSION_OTHER_TEXT` | Other pension additions details | TEXT | 105 | All |
| `PENSION_TOT_ADDITIONS_AMT` | Total pension additions | NUMERIC |  | All |
| `PENSION_TOT_BAL_ADDN_AMT` | Total balance additions | NUMERIC |  | All |
| `PENSION_BNFTS_DSBRSD_AMT` | Pension benefits distributed | NUMERIC |  | All |
| `PENSION_ADMIN_CHRG_AMT` | Pension administrative charges | NUMERIC |  | All |
| `PENSION_TRANSFER_TO_AMT` | Pension transfers out | NUMERIC |  | All |
| `PENSION_OTH_DED_AMT` | Other pension deductions | NUMERIC |  | All |
| `PENSION_OTH_DED_TEXT` | Other pension deductions details | TEXT | 105 | All |
| `PENSION_TOT_DED_AMT` | Total pension deductions | NUMERIC |  | All |
| `PENSION_EOY_BAL_AMT` | Pension ending balance | NUMERIC |  | All |
| `WLFR_BNFT_HEALTH_IND` | Health benefit indicator | TEXT | 1 | All |
| `WLFR_BNFT_DENTAL_IND` | Dental benefit indicator | TEXT | 1 | All |
| `WLFR_BNFT_VISION_IND` | Vision benefit indicator | TEXT | 1 | All |
| `WLFR_BNFT_LIFE_INSUR_IND` | Life insurance benefit indicator | TEXT | 1 | All |
| `WLFR_BNFT_TEMP_DISAB_IND` | Temporary disability benefit indicator | TEXT | 1 | All |
| `WLFR_BNFT_LONG_TERM_DISAB_IND` | Long-term disability benefit indicator | TEXT | 1 | All |
| `WLFR_BNFT_UNEMP_IND` | Unemployment benefit indicator | TEXT | 1 | All |
| `WLFR_BNFT_DRUG_IND` | Prescription drug benefit indicator | TEXT | 1 | All |
| `WLFR_BNFT_STOP_LOSS_IND` | Stop-loss benefit indicator | TEXT | 1 | All |
| `WLFR_BNFT_HMO_IND` | HMO benefit indicator | TEXT | 1 | All |
| `WLFR_BNFT_PPO_IND` | PPO benefit indicator | TEXT | 1 | All |
| `WLFR_BNFT_INDEMNITY_IND` | Indemnity benefit indicator | TEXT | 1 | All |
| `WLFR_BNFT_OTHER_IND` | Other welfare benefit indicator | TEXT | 1 | All |
| `WLFR_TYPE_BNFT_OTH_TEXT` | Other welfare benefit details | TEXT | 105 | All |
| `WLFR_PREMIUM_RCVD_AMT` | Premiums received | NUMERIC |  | All |
| `WLFR_UNPAID_DUE_AMT` | Unpaid premiums due | NUMERIC |  | All |
| `WLFR_RESERVE_AMT` | Reserve amount | NUMERIC |  | All |
| `WLFR_TOT_EARNED_PREM_AMT` | Total earned premiums | NUMERIC |  | All |
| `WLFR_CLAIMS_PAID_AMT` | Claims paid | NUMERIC |  | All |
| `WLFR_INCR_RESERVE_AMT` | Increase in reserves | NUMERIC |  | All |
| `WLFR_INCURRED_CLAIM_AMT` | Incurred claims | NUMERIC |  | All |
| `WLFR_CLAIMS_CHRGD_AMT` | Claims charged | NUMERIC |  | All |
| `WLFR_RET_COMMISSIONS_AMT` | Retained commissions | NUMERIC |  | All |
| `WLFR_RET_ADMIN_AMT` | Retained administrative amount | NUMERIC |  | All |
| `WLFR_RET_OTH_COST_AMT` | Retained other costs | NUMERIC |  | All |
| `WLFR_RET_OTH_EXPENSE_AMT` | Retained other expenses | NUMERIC |  | All |
| `WLFR_RET_TAXES_AMT` | Retained taxes | NUMERIC |  | All |
| `WLFR_RET_CHARGES_AMT` | Retained charges | NUMERIC |  | All |
| `WLFR_RET_OTH_CHRGS_AMT` | Retained other charges | NUMERIC |  | All |
| `WLFR_RET_TOT_AMT` | Total retained amount | NUMERIC |  | All |
| `WLFR_REFUND_CASH_IND` | Cash refund indicator | TEXT | 1 | All |
| `WLFR_REFUND_CREDIT_IND` | Credit refund indicator | TEXT | 1 | All |
| `WLFR_REFUND_AMT` | Refund amount | NUMERIC |  | All |
| `WLFR_HELD_BNFTS_AMT` | Benefits held | NUMERIC |  | All |
| `WLFR_CLAIMS_RESERVE_AMT` | Claims reserve | NUMERIC |  | All |
| `WLFR_OTH_RESERVE_AMT` | Other reserve | NUMERIC |  | All |
| `WLFR_DIVNDS_DUE_AMT` | Dividends due | NUMERIC |  | All |
| `WLFR_TOT_CHARGES_PAID_AMT` | Total charges paid | NUMERIC |  | All |
| `WLFR_ACQUIS_COST_AMT` | Acquisition cost | NUMERIC |  | All |
| `WLFR_ACQUIS_COST_TEXT` | Acquisition cost details | TEXT | 1000 | All |
| `INS_FAIL_PROVIDE_INFO_IND` | Failure to provide information indicator | TEXT | 1 | All |
| `INS_FAIL_PROVIDE_INFO_TEXT` | Failure to provide information details | TEXT | 105 | All |

## Layout names that differ from the CSV

The layout file spells these fields differently from the CSV header. The CSV name is what the tables use.

| Layout name | CSV column | Layout years |
| --- | --- | --- |
| `PENS_DISTRIB_BNFT_TERM_PLN_IND` | `PENS_DISTR_BNFT_TERM_PLN_IND` | All |
| `WLFR_DIVNNDS_DUE_AMT` | `WLFR_DIVNDS_DUE_AMT` | 2020-2024 |
| `WLFR_DIVNDDS_DUE_AMT` | `WLFR_DIVNDS_DUE_AMT` | 2019 |
