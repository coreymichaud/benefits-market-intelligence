# bronze.F_SCH_A_2020_Latest

This data was taken from DOL EFAST's [2020 Form 5500 Schedule A](https://askebsa.dol.gov/FOIA%20Files/2020/Latest/F_SCH_A_2020_Latest.zip).

## Overview

* **rows:** 337,584

* **columns:** 90

## Table Information

| field_name                     | field_description                                            | bronze_dtype | notated_dtype | size |
| ------------------------------ | ------------------------------------------------------------ | ------------ | ------------- | ---: |
| ack_id                         | Acknowledgment ID (PK)                                       | VARCHAR      | TEXT          |   30 |
| form_id                        | Form ID                                                      | VARCHAR      | NUMERIC       |    — |
| sch_a_plan_year_begin_date     | Plan year start date                                         | VARCHAR      | TEXT          |   10 |
| sch_a_plan_year_end_date       | Plan year end date                                           | VARCHAR      | TEXT          |   10 |
| sch_a_plan_num                 | Schedule A plan number                                       | VARCHAR      | TEXT          |    3 |
| sch_a_ein                      | Schedule A EIN                                               | VARCHAR      | TEXT          |    9 |
| ins_carrier_name               | Insurance carrier name                                       | VARCHAR      | TEXT          |   70 |
| ins_carrier_ein                | Insurance carrier EIN                                        | VARCHAR      | TEXT          |    9 |
| ins_carrier_naic_code          | Insurance carrier NAIC code                                  | VARCHAR      | TEXT          |    5 |
| ins_contract_num               | Insurance contract number                                    | VARCHAR      | TEXT          |   15 |
| ins_prsn_covered_eoy_cnt       | Persons covered at year end                                  | VARCHAR      | TEXT          |    7 |
| ins_policy_from_date           | Policy start date                                            | VARCHAR      | TEXT          |   10 |
| ins_policy_to_date             | Policy end date                                              | VARCHAR      | TEXT          |   10 |
| ins_broker_comm_tot_amt        | Total broker commissions                                     | VARCHAR      | NUMERIC       |    — |
| ins_broker_fees_tot_amt        | Total broker fees                                            | VARCHAR      | NUMERIC       |    — |
| pension_eoy_gen_acct_amt       | Pension general account balance                              | VARCHAR      | NUMERIC       |    — |
| pension_eoy_sep_acct_amt       | Pension separate account balance                             | VARCHAR      | NUMERIC       |    — |
| pension_basis_rates_text       | Pension basis and rates                                      | VARCHAR      | TEXT          |  105 |
| pension_prem_paid_tot_amt      | Total pension premiums paid                                  | VARCHAR      | NUMERIC       |    — |
| pension_unpaid_premium_amt     | Unpaid pension premiums                                      | VARCHAR      | NUMERIC       |    — |
| pension_contract_cost_amt      | Pension contract cost                                        | VARCHAR      | NUMERIC       |    — |
| pension_cost_text              | Pension contract cost details                                | VARCHAR      | TEXT          |  105 |
| alloc_contracts_indiv_ind      | Individual allocated contracts                               | VARCHAR      | TEXT          |    1 |
| alloc_contracts_group_ind      | Group allocated contracts                                    | VARCHAR      | TEXT          |    1 |
| alloc_contracts_other_ind      | Other allocated contracts                                    | VARCHAR      | TEXT          |    1 |
| alloc_contracts_other_text     | Other allocated contracts details                            | VARCHAR      | TEXT          |  105 |
| pens_distrib_bnft_term_pln_ind | Benefit distribution termination plan                        | VARCHAR      | TEXT          |    1 |
| unalloc_contracts_dep_adm_ind  | Unallocated contracts dependent on administrator             | VARCHAR      | TEXT          |    1 |
| unal_contrac_imm_part_guar_ind | Unallocated contracts with immediate participation guarantee | VARCHAR      | TEXT          |    1 |
| unal_contracts_guar_invest_ind | Unallocated guaranteed investment contracts                  | VARCHAR      | TEXT          |    1 |
| unalloc_contracts_other_ind    | Other unallocated contracts                                  | VARCHAR      | TEXT          |    1 |
| unalloc_contracts_other_text   | Other unallocated contracts details                          | VARCHAR      | TEXT          |  105 |
| pension_end_prev_bal_amt       | Pension prior year ending balance                            | VARCHAR      | NUMERIC       |    — |
| pension_contrib_dep_amt        | Pension deposits/contributions                               | VARCHAR      | NUMERIC       |    — |
| pension_divnd_cr_dep_amt       | Pension dividends and credits deposited                      | VARCHAR      | NUMERIC       |    — |
| pension_int_cr_dur_yr_amt      | Pension interest credited during year                        | VARCHAR      | NUMERIC       |    — |
| pension_transfer_from_amt      | Pension transfers in                                         | VARCHAR      | NUMERIC       |    — |
| pension_other_amt              | Other pension additions                                      | VARCHAR      | NUMERIC       |    — |
| pension_other_text             | Other pension additions details                              | VARCHAR      | TEXT          |  105 |
| pension_tot_additions_amt      | Total pension additions                                      | VARCHAR      | NUMERIC       |    — |
| pension_tot_bal_addn_amt       | Total balance additions                                      | VARCHAR      | NUMERIC       |    — |
| pension_bnfts_dsbrsd_amt       | Pension benefits distributed                                 | VARCHAR      | NUMERIC       |    — |
| pension_admin_chrg_amt         | Pension administrative charges                               | VARCHAR      | NUMERIC       |    — |
| pension_transfer_to_amt        | Pension transfers out                                        | VARCHAR      | NUMERIC       |    — |
| pension_oth_ded_amt            | Other pension deductions                                     | VARCHAR      | NUMERIC       |    — |
| pension_oth_ded_text           | Other pension deductions details                             | VARCHAR      | TEXT          |  105 |
| pension_tot_ded_amt            | Total pension deductions                                     | VARCHAR      | NUMERIC       |    — |
| pension_eoy_bal_amt            | Pension ending balance                                       | VARCHAR      | NUMERIC       |    — |
| wlfr_bnft_health_ind           | Health benefit indicator                                     | VARCHAR      | TEXT          |    1 |
| wlfr_bnft_dental_ind           | Dental benefit indicator                                     | VARCHAR      | TEXT          |    1 |
| wlfr_bnft_vision_ind           | Vision benefit indicator                                     | VARCHAR      | TEXT          |    1 |
| wlfr_bnft_life_insur_ind       | Life insurance benefit indicator                             | VARCHAR      | TEXT          |    1 |
| wlfr_bnft_temp_disab_ind       | Temporary disability benefit indicator                       | VARCHAR      | TEXT          |    1 |
| wlfr_bnft_long_term_disab_ind  | Long-term disability benefit indicator                       | VARCHAR      | TEXT          |    1 |
| wlfr_bnft_unemp_ind            | Unemployment benefit indicator                               | VARCHAR      | TEXT          |    1 |
| wlfr_bnft_drug_ind             | Prescription drug benefit indicator                          | VARCHAR      | TEXT          |    1 |
| wlfr_bnft_stop_loss_ind        | Stop-loss benefit indicator                                  | VARCHAR      | TEXT          |    1 |
| wlfr_bnft_hmo_ind              | HMO benefit indicator                                        | VARCHAR      | TEXT          |    1 |
| wlfr_bnft_ppo_ind              | PPO benefit indicator                                        | VARCHAR      | TEXT          |    1 |
| wlfr_bnft_indemnity_ind        | Indemnity benefit indicator                                  | VARCHAR      | TEXT          |    1 |
| wlfr_bnft_other_ind            | Other welfare benefit indicator                              | VARCHAR      | TEXT          |    1 |
| wlfr_type_bnft_oth_text        | Other welfare benefit details                                | VARCHAR      | TEXT          |  105 |
| wlfr_premium_rcvd_amt          | Premiums received                                            | VARCHAR      | NUMERIC       |    — |
| wlfr_unpaid_due_amt            | Unpaid premiums due                                          | VARCHAR      | NUMERIC       |    — |
| wlfr_reserve_amt               | Reserve amount                                               | VARCHAR      | NUMERIC       |    — |
| wlfr_tot_earned_prem_amt       | Total earned premiums                                        | VARCHAR      | NUMERIC       |    — |
| wlfr_claims_paid_amt           | Claims paid                                                  | VARCHAR      | NUMERIC       |    — |
| wlfr_incr_reserve_amt          | Increase in reserves                                         | VARCHAR      | NUMERIC       |    — |
| wlfr_incurred_claim_amt        | Incurred claims                                              | VARCHAR      | NUMERIC       |    — |
| wlfr_claims_chrgd_amt          | Claims charged                                               | VARCHAR      | NUMERIC       |    — |
| wlfr_ret_commissions_amt       | Retained commissions                                         | VARCHAR      | NUMERIC       |    — |
| wlfr_ret_admin_amt             | Retained administrative amount                               | VARCHAR      | NUMERIC       |    — |
| wlfr_ret_oth_cost_amt          | Retained other costs                                         | VARCHAR      | NUMERIC       |    — |
| wlfr_ret_oth_expense_amt       | Retained other expenses                                      | VARCHAR      | NUMERIC       |    — |
| wlfr_ret_taxes_amt             | Retained taxes                                               | VARCHAR      | NUMERIC       |    — |
| wlfr_ret_charges_amt           | Retained charges                                             | VARCHAR      | NUMERIC       |    — |
| wlfr_ret_oth_chrgs_amt         | Retained other charges                                       | VARCHAR      | NUMERIC       |    — |
| wlfr_ret_tot_amt               | Total retained amount                                        | VARCHAR      | NUMERIC       |    — |
| wlfr_refund_cash_ind           | Cash refund indicator                                        | VARCHAR      | TEXT          |    1 |
| wlfr_refund_credit_ind         | Credit refund indicator                                      | VARCHAR      | TEXT          |    1 |
| wlfr_refund_amt                | Refund amount                                                | VARCHAR      | NUMERIC       |    — |
| wlfr_held_bnfts_amt            | Benefits held                                                | VARCHAR      | NUMERIC       |    — |
| wlfr_claims_reserve_amt        | Claims reserve                                               | VARCHAR      | NUMERIC       |    — |
| wlfr_oth_reserve_amt           | Other reserve                                                | VARCHAR      | NUMERIC       |    — |
| wlfr_divnnds_due_amt           | Dividends due                                                | VARCHAR      | NUMERIC       |    — |
| wlfr_tot_charges_paid_amt      | Total charges paid                                           | VARCHAR      | NUMERIC       |    — |
| wlfr_acquis_cost_amt           | Acquisition cost                                             | VARCHAR      | NUMERIC       |    — |
| wlfr_acquis_cost_text          | Acquisition cost details                                     | VARCHAR      | TEXT          | 1000 |
| ins_fail_provide_info_ind      | Failure to provide information indicator                     | VARCHAR      | TEXT          |    1 |
| ins_fail_provide_info_text     | Failure to provide information details                       | VARCHAR      | TEXT          |  105 |
