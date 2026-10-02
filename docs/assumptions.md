# Assumptions, Caveats & Limitations

This document covers the rules and judgment calls behind the analysis in [`notebooks/analysis.ipynb`](../notebooks/analysis.ipynb) and the Streamlit dashboard, along with the limits they put on what the charts can say. Chart numbers follow the notebook sections. For background on the forms themselves, see [about-the-data.md](about-the-data.md). For how the tables were built, see [data-transformations.md](data-transformations.md). How firm and plan names are matched is in [name-matching.md](name-matching.md), and every source is listed in [sources.md](sources.md).

## Chart Reference

| Chart | Question | Source | Plans Included |
|---|---|---|---|
| [1](../figures/analysis/01-compensation-pool-vs-lives.png) | Is broker pay growing faster than the lives it covers? | Schedule A | All welfare filings |
| [2](../figures/analysis/02-compensation-growth-bridge.png) | Which lines of coverage are driving the growth? | Schedule A | All welfare filings |
| [3](../figures/analysis/03-fee-adoption-heatmap.png) | Is broker pay shifting from commissions toward carrier-paid fees? | Schedule A | All welfare filings |
| [4](../figures/analysis/04-self-funding-by-plan-size.png) | Is self-funding moving down-market? | Main form, Schedule A | Single-employer health plans, 100+ participants |
| [5](../figures/analysis/05-broker-leaderboard-bump.png) | Which brokerage firms are winning large-employer plans? | Schedule C | Single-employer, welfare-only plans |
| [6](../figures/analysis/06-industry-opportunity-treemap.png) | Which industries hold the largest and fastest-growing pay pools? | Schedule A | All welfare filings with a known industry |
| [7](../figures/analysis/07-broker-take-rate-by-line.png) | What share of premium are brokers capturing, by line? | Schedule A | All welfare filings, plus premium screens |
| [8](../figures/analysis/08-voluntary-adoption-by-size.png) | Is voluntary benefits adoption spreading across employer sizes? | Schedule A | Single-employer plans, 100+ participants, with a Schedule A |
| [9](../figures/analysis/09-broker-win-loss.png) | How are the fastest-growing brokers winning new plans? | Schedule C | Single-employer, welfare-only plans filing in consecutive years |
| [10](../figures/analysis/10-broker-pay-growth-map.png) | Where is broker pay growing fastest? | Schedule A | All welfare filings with a U.S. state address |

"All welfare filings" means every filing with a welfare benefit code that passes the filing window and deduplication rules below, whatever the plan type. "Welfare-only" means the filing reports no pension benefit code.

## Filing Window

- **The rule:** each year keeps only filings received within 9.5 months of plan year end, which is the 7-month deadline plus the 2.5-month extension. Older years have had more time to collect late filings, so this puts every year on equal footing.
- **Receipt date:** taken from the first 8 digits of `ACK_ID`, which is the EFAST receipt timestamp. Gold also keeps `DATE_RECEIVED`, the receipt date DOL records for each filing; the two agree on 99.6% of filings.
- **Plan year end:** assumed to be 12 months after `FORM_PLAN_YEAR_BEGIN_DATE`, because `gold.F_5500` doesn't carry an end date. In SQL the cutoff is the begin date plus 21 months and 14 days. Short plan years (flagged by `SHORT_PLAN_YR_IND`) get a slightly generous window.
- **What gets dropped:** between about 11% and 17% of welfare filings in each year from 2019 to 2023, and about 9% for 2024. That group mixes three things: filings that really were late or delinquent, on-time filings that were amended later (see below), and catch-up filings for plan years several years back that DOL files under a newer form year. The catch-up group is about 27,000 welfare filings. Since the window is measured from the plan year begin date, all of them fall out, which also keeps them from being counted in the wrong year.
- **Amended filings are a known leak.** DOL's "Latest" dataset keeps only the most recent version of each filing, so a plan that filed on time but amended later looks late and is dropped. Older years have had longer to pick up amendments, so the leak is probably a bit larger for them than for 2023 and 2024. See [Amended Filings & Traceability](#amended-filings--traceability).
- **2024's lower exclusion rate isn't better compliance.** Late 2024 filings are still coming in, so fewer of them exist yet to be excluded.
- **2024 is nearly complete.** The data snapshot ends September 24, 2026. 2024 plan years that begin after December 10, 2024 haven't reached the end of their window, so some of their on-time filings may not be in the data yet. That's about 0.3% of 2024 welfare filings, all of them non-calendar-year plans.

## Plan Identity & Deduplication

- **Plan key:** a plan is its sponsor EIN plus its three-digit plan number (`SPONS_DFE_EIN` + `SPONS_DFE_PN`).
- **One filing per plan per year:** filings are deduplicated to one per sponsor EIN, plan number and year, keeping the latest submission (highest `ACK_ID`). This runs after the filing window, so the filing that's kept is the latest on-time one.
- **Form year as plan year:** DOL files every filing under its form year, the year printed on the form, and the analysis uses `FORM_YEAR` as the plan year. After the filing window, the plan year begins in `FORM_YEAR` for all but about 1,100 filings.
- **Mergers and renumbering:** if a sponsor changes its EIN or renumbers a plan, the plan looks brand new. This mostly matters for chart 9, which follows plans from one year to the next.

## Amended Filings & Traceability

- **Default version:** the "Latest" files hold only the most recent filing DOL has received for each plan and year, and deduplication keeps the latest on-time one. An amended return therefore replaces the original, so every number uses the most recent accepted version.
- **Counting amendments:** gold keeps `AMENDED_IND` from the main form (1 when the filer checked the amended return box). About 2% of kept filings each year are amendments (1.9% to 2.5%).
- **Tracing a number to a filing:** every gold row keeps the IDs needed to find its source: `ACK_ID` in all three tables, plus `FORM_ID` for a Schedule A contract and `ROW_ORDER` for a Schedule C provider. An `ACK_ID` can be looked up on DOL's public [EFAST2 Form 5500 search](https://www.efast.dol.gov/5500Search/) to see the filed form.
- **Earlier versions aren't loaded.** The original filing an amendment replaced is only in DOL's "All" files, which this project doesn't download. The limits that creates for the filing window are covered above.

## Plan Types

- **Welfare filings only:** a filing is kept if `TYPE_WELFARE_BNFT_CODE` has at least one welfare benefit code. Pension-only filings drop out.
- **Charts 1, 2, 3, 6, 7 and 10** include every plan type: single-employer, multiemployer (Taft-Hartley) and multiple-employer plans.
- **Charts 4, 5, 8 and 9** keep single-employer plans only (`TYPE_PLAN_ENTITY_CD = 2`).
- **Charts 5 and 9** also drop filings that report a pension benefit code alongside the welfare codes, so the Schedule C providers they count belong to a welfare plan and not a combined retirement filing. This removes under 1% of welfare filings.

## Small Plans (Under 100 Participants)

- **Mostly excluded, because of the source data.** Fully insured and unfunded welfare plans with fewer than 100 participants are generally exempt from filing, so they never appear.
- **5500-SF filers are also missing.** Small plans that file the 5500-SF aren't loaded, and SF filers don't attach Schedule A.
- **Some small plans are included but not separately segmented.** Small plans that file the full Form 5500 anyway make up about 6% to 7% of welfare filings (about 3% of Schedule A contracts) and appear in charts 1, 2, 3, 6, 7 and 10.
- **Charts 4, 5, 8 and 9 are large-plan only.** Charts 4 and 8 drop plans under 100 participants directly. Charts 5 and 9 use Schedule C, which is generally only required for large plans.
- **How to present it:** treat the findings as a view of the large-group market (100+ participants), not the small-group market.

## Covered Lives

- **What the lives field measures:** `INS_PRSN_COVERED_EOY_CNT` is the carrier-reported "persons covered" per contract at the end of the policy year. Some carriers report employees or certificates; others report total members including dependents. The data can't tell which. Medical and dental are more likely to include dependents, while life and disability are typically employee-only.
- **Per-life figures aren't comparable across lines.** Pay per covered life is understated for lines that count dependents and overstated for employee-only lines, and it isn't a per-employee-per-month figure. This applies to the per-life line in chart 1 and the per-life checks in [Data Quality Screens](#data-quality-screens).
- **Summed lives double-count people.** Someone with medical, dental and life counts three times, so the covered-lives total measures coverage volume, not unique people.
- **Trends are still valid** as long as each carrier's counting convention stays stable over time.
- **Plan-size bands use a different count.** `TOT_PARTCP_BOY_CNT` counts participants (employees and former employees) at the start of the plan year, not dependents. It sets the size bands in charts 4 and 8 and the 100-participant cutoff.

## Policy Periods & Partial Years

- **Two different periods.** Each Schedule A contract reports its policy year (`INS_POLICY_FROM_DATE` to `INS_POLICY_TO_DATE`) on the filing for the plan year (`SCH_A_PLAN_YEAR_BEGIN_DATE` to `SCH_A_PLAN_YEAR_END_DATE`) in which that policy year ends. A contract that renews July 1 lands on the plan year it ends in, so one plan year's Schedule A can cover parts of two calendar years.
- **Partial years are flagged, never annualized.** A contract with a policy year shorter than 12 months (a new contract, a mid-year carrier change or a cancellation) reports only the premium and pay for that shorter period. A contract counts as partial-year when its policy period is under 360 days, and a filing counts as a short plan year when `SHORT_PLAN_YR_IND = 1`. All of these fields are in gold. About 4% to 5% of contracts in the pay pool are partial-year each year, and about 4% to 5% of kept filings are short plan years. No amount is ever scaled up to a full year; the charts count partial-year records as reported.
- **Schedule A and Schedule C are never added together.** Schedule A amounts follow the policy year, while Schedule C reports what a provider was paid during the plan year. The analysis only uses Schedule C to see which firms a plan names, never for dollars, so no number mixes the two periods.
- **Year-over-year comparisons hold** as long as a plan keeps the same renewal date from one year to the next, which most do.

## Dollar Amounts

- **Self-reported, and sometimes badly wrong.** Dollar fields contain extreme errors, including single contracts reporting over $500 trillion in commissions. The screens in the next section handle these.
- **Blanks count as zero, after checking.** A missing commission or fee amount is treated as $0. See [Blank Amounts](#blank-amounts) for the checks and what changes if blanks are dropped instead.
- **Nominal dollars.** Nothing is adjusted for inflation, so the growth figures from 2019 to 2024 include it.

## Data Quality Screens

Schedule A contracts that fail any of these checks are dropped. The chart 7 screens only apply to the take rate calculation.

| Screen | Charts |
|---|---|
| Negative commissions or fees | 1, 2, 3, 6, 7, 10 |
| Covered lives missing, zero or above 1M | 1, 2, 3, 6, 7, 10 |
| Broker pay above $2,500 per covered life | 1, 2, 3, 6, 7, 10 |
| No premium above $0 reported | 7 |
| Premium above $50K per covered life | 7 |
| Broker pay above 100% of premium | 7 |
| Premium above $250M on a single contract | 7 |

- The first three screens remove about 2.3% to 2.5% of contracts a year. Yearly totals move by less than 3% whether the pay cap is $1K or $5K.
- Charts 4 and 8 don't use these screens. They only look at which benefits a contract covers, not at dollar amounts.
- Charts 5 and 9 come from Schedule C and don't use them either.

### Record Funnel

What each rule keeps and removes, by form year. Filings are counted before any rule; plans kept are after the filing window and deduplication. The three Schedule A screens are applied in the order shown, so each contract is counted once.

| Form year | Welfare filings | Plans kept | Schedule A contracts | Negative amounts | No usable lives | Over $2,500 per life | Contracts kept | Broker pay kept |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 87,291 | 76,854 | 250,385 | 587 | 4,927 | 465 | 244,406 | $5.35B |
| 2020 | 89,486 | 74,953 | 247,088 | 556 | 4,527 | 555 | 241,450 | $5.40B |
| 2021 | 87,517 | 72,726 | 243,916 | 601 | 4,777 | 464 | 238,074 | $5.52B |
| 2022 | 88,533 | 74,446 | 250,993 | 564 | 4,576 | 591 | 245,262 | $6.14B |
| 2023 | 89,364 | 77,223 | 265,770 | 628 | 5,421 | 528 | 259,193 | $6.83B |
| 2024 | 85,970 | 78,182 | 274,660 | 642 | 5,769 | 478 | 267,771 | $7.56B |

Contracts dropped for having no usable lives count also carry $36M to $54M a year of broker pay under $5M per contract, which is left out of the pool along with them.

## Blank Amounts

A blank commission or fee on a filed Schedule A is read as $0. Before relying on that, the blanks were checked (contracts on kept filings, before the screens):

| Form year | Commission blank | Fee blank | Both blank | Carrier withheld info, both blank | Carrier withheld info, amounts filled in |
|---|---:|---:|---:|---:|---:|
| 2019 | 11.3% | 15.8% | 10.8% | 2.9% | 3.8% |
| 2020 | 11.4% | 15.7% | 11.0% | 3.2% | 4.3% |
| 2021 | 11.0% | 14.7% | 10.6% | 3.0% | 4.6% |
| 2022 | 11.0% | 14.3% | 10.6% | 4.2% | 5.2% |
| 2023 | 10.5% | 13.5% | 10.2% | 5.0% | 5.7% |
| 2024 | 9.9% | 12.5% | 9.6% | 5.5% | 6.1% |

- **Blanks are steady,** so they don't drive the trends.
- **They aren't carriers refusing to report.** The "carrier failed to provide information" box (`INS_FAIL_PROVIDE_INFO_IND`) is checked about as often when the amounts are filled in as when they're blank.
- **They behave like zeros.** Another 13% to 14% of contracts report an explicit $0 commission, and blanks cluster where carriers rarely pay brokers: in 2024, 47% of screened stop-loss contracts and 14% of medical contracts leave both amounts blank, against 4% to 5% of life and disability contracts.
- **Totals are the same either way.** A zero adds nothing, so broker pay in charts 1, 2, 6 and 10 doesn't change if blank contracts are dropped instead.
- **Rates do change.** A blank contract still adds premium to take rate and a "no fee" to fee adoption. With blank contracts dropped instead of read as zero:

| Measure, 2019 to 2024 | Blanks as $0 (reported) | Blank contracts dropped |
|---|---|---|
| Market take rate | 3.32% to 3.78% | 4.12% to 4.57% |
| Medical take rate | 2.12% to 2.08% | 2.75% to 2.73% |
| Multi-line bundle take rate | 4.40% to 5.18% | 4.95% to 5.55% |
| Voluntary & other take rate | 10.40% to 13.54% | 13.18% to 16.14% |
| Stop-loss take rate | 3.56% to 3.26% | 4.80% to 4.89% |
| Stop-loss fee adoption | 17.4% to 18.5% | 27.0% to 35.0% |

- **What's reported:** blanks as $0, since the filer submitted the schedule and left the amount empty. Take rates and fee adoption are a floor. The direction of every trend holds either way except stop-loss: its take rate falls with blanks as zero and rises slightly with them dropped, so any stop-loss compression finding is low confidence.

## Minimum Bases

Every rule that hides or refuses to name a thin slice, in one place.

| Where | Rule |
|---|---|
| Chart 4 (notebook) | No minimum needed: the smallest size band holds at least 1,478 plans in every year |
| Chart 5 (notebook) | Shows only firms ranked in the top 10 in 2019 or 2024 |
| Chart 6 (notebook) | The fastest-growing sector is picked from the 10 largest sectors by 2024 broker pay |
| Chart 8 (notebook) | No minimum needed: the smallest size band holds at least 2,019 plans in every year |
| Chart 9 (notebook) | Shows the 10 firms with the best 2024 rank |
| Chart 10 (notebook) | States under $25M of 2024 broker pay are grey; only states with at least $50M in 2019 can be named fastest-growing |
| Fee adoption (dashboard) | A line needs at least 20 contracts in a year to be shown |
| Self-funding and voluntary (dashboard) | A size band needs at least 25 plans in a year to be shown |
| State map (dashboard) | Grey under 0.33% of end-year broker pay; fastest-growing needs at least 0.93% of start-year pay |
| Leaderboard (dashboard) | Needs at least 3 firms with plans in the end year |
| Wins and losses (dashboard) | Needs at least 5 wins and losses combined |
| Momentum map (dashboard) | A firm needs at least 3 plans in the start year and at least 5 plans kept or lost |

## Metric Lineage

How each measure is built. Every one starts from the kept filings: `gold.F_5500` filtered to welfare filings inside the filing window and deduplicated to one per plan and year.

| Measure | Join | Rows used | Calculation |
|---|---|---|---|
| Broker pay (charts 1, 2, 6, 10) | Kept filings inner join `gold.SCH_A` on `ACK_ID` | Contracts passing the first three screens | Sum of `INS_BROKER_COMM_TOT_AMT` + `INS_BROKER_FEES_TOT_AMT`, blanks as $0 |
| Covered lives (chart 1) | Same | Same | Sum of `INS_PRSN_COVERED_EOY_CNT`, cast to a number |
| Pay per covered life (chart 1) | Same | Same | Broker pay divided by covered lives |
| Fee share | Same | Same | Fees divided by broker pay |
| Fee adoption (chart 3) | Same | Same, excluding unclassified contracts | Share of contracts in a line with fees above $0 |
| Take rate (chart 7) | Same | Contracts passing all seven screens | Broker pay divided by premium (the larger of `WLFR_TOT_CHARGES_PAID_AMT` and `WLFR_TOT_EARNED_PREM_AMT`) |
| Self-funding (chart 4) | Kept filings left join `gold.SCH_A` on `ACK_ID`, grouped per plan | Single-employer plans with welfare code 4A and 100+ participants | Share of plans with no contract flagged health, HMO, PPO or drug |
| Voluntary adoption (chart 8) | Kept filings inner join `gold.SCH_A` on `ACK_ID`, grouped per plan | Single-employer plans with 100+ participants | Share of plans with a voluntary & other contract |
| Plans served (chart 5) | Kept filings inner join `gold.SCH_C_P1_I2` on `ACK_ID` | Single-employer, welfare-only plans; providers matched to a firm | Distinct plan keys per firm and year |
| Wins and losses (chart 9) | Each plan's firms joined to the same plan's firms the year before, on plan key and `FORM_YEAR - 1` | Plans listing a Schedule C provider in both years | Wins, losses and net as defined in chart 9 |
| Industry and state (charts 6, 10) | From the kept filing | All of the above | First two digits of `BUSINESS_CODE` mapped to a NAICS sector; `SPONS_DFE_MAIL_US_STATE` |

## Confidence Ratings

Each recommendation carries a call and a confidence level, so a reader can tell a firm conclusion from a lead worth watching.

- **Go:** the evidence supports acting on it now.
- **No-go:** the evidence argues against investing in it.
- **Monitor:** worth tracking, but not strong enough to act on yet.

| Confidence | What it takes |
|---|---|
| High | Moves the same way in at least 4 of the 5 year-over-year steps, still holds with the five plans that moved most taken out, rests on reported amounts or counts rather than an inferred label, and clears the minimum bases |
| Medium | Consistent, but relies on a proxy (self-funding read from a missing insured medical contract), an inferred label (voluntary benefits), a thin slice of filings (Schedule C), or changes size with how blanks are treated |
| Low | Driven by a handful of sponsors, resting on a thin base, or changing direction under a reasonable alternative, such as the stop-loss take rate with blank contracts dropped |

## Definitions

### Line of Coverage

Each contract gets one line from its Schedule A benefit flags, checked top to bottom. "Core lines" here means medical, dental, vision, life and disability.

| Line | Rule |
|---|---|
| Stop-loss | Stop-loss flag set, whatever else is flagged |
| Medical | Health, HMO, PPO or prescription drug flag, and no other core line |
| Dental | Dental flag, and no other core line |
| Vision | Vision flag, and no other core line |
| Life & AD&D | Life insurance flag, and no other core line |
| Disability | Temporary or long-term disability flag, and no other core line |
| Multi-line bundle | Two or more core lines |
| Voluntary & other | No core line, but an other, indemnity or supplemental unemployment flag. AD&D-only contracts land here when the filer marks them as other |
| Unclassified | No benefit flags set |

Unclassified contracts are counted in the totals for charts 1, 6 and 10, shown as their own bar in chart 2, and left out of charts 3 and 7.

### Other Terms

- **Broker compensation (broker pay):** Schedule A commissions plus carrier-paid fees (`INS_BROKER_COMM_TOT_AMT` + `INS_BROKER_FEES_TOT_AMT`). Both are totals across every agent and broker listed on the contract.
- **Carrier-paid fees:** Schedule A fees paid by the insurer (bonuses, overrides, service fees). They are not fees paid directly by the employer, which don't appear on Schedule A.
- **Premium:** the non-experience-rated premium (`WLFR_TOT_CHARGES_PAID_AMT`) or the earned premium for experience-rated contracts (`WLFR_TOT_EARNED_PREM_AMT`), whichever is reported. If both are filled in, the larger one is used.
- **Take rate (chart 7):** broker pay divided by premium, on contracts that pass the chart 7 screens. Changes by line are relative, so a move from 4.00% to 4.20% shows as +5%, not +0.2 points.
- **Fee adoption (chart 3):** the share of contracts in a line where carrier-paid fees are above zero.
- **Industry (chart 6):** the first two digits of the sponsor's self-reported `BUSINESS_CODE`, grouped into top-level NAICS sectors (31 to 33 become Manufacturing, 44 and 45 Retail Trade, 48 and 49 Transportation & Warehousing). Codes that don't map to a sector are left out.
- **State (chart 10):** the state on the sponsor's mailing address (`SPONS_DFE_MAIL_US_STATE`), limited to the 50 states and DC. For a multi-state employer this is often headquarters, so all of its broker pay lands in one state.

## Chart Notes

### Chart 4: Self-Funding

- **The measure:** the share of single-employer health plans (welfare code `4A`) with 100+ participants that have no insured medical contract on Schedule A. A stop-loss contract only counts as insured medical if the filer also checked a health, HMO, PPO or drug box on it, which about a quarter of stop-loss contracts do. So most level-funded plans read as self-funded, but some read as insured.
- **It understates self-funding among large employers,** who often keep an insured HMO alongside a self-funded plan under the same plan number.
- **Missing schedules read as self-funded.** A health plan with no Schedule A at all counts as self-funded, so a filer that should have attached one and didn't gets misclassified.

### Chart 5: Broker Leaderboard

- **Firms are found by name.** Schedule C provider names are upper-cased, trimmed and matched against patterns for 22 national brokers and consultants (`BROKER_FIRMS`, identical in the notebook and `streamlit/figures/data.py`). A name takes the first firm whose pattern matches. The rules, exclusions and a match audit are in [name-matching.md](name-matching.md).
- **Strict on names, loose on roles.** Patterns use word boundaries and rule out known look-alikes (investment arms, law firms, similarly spelled companies), but a firm counts regardless of its role on the plan, so a consulting or actuarial relationship counts the same as a brokerage one.
- **Schedule C doesn't list every broker.** Providers only show up if they received at least $5K. The instructions also leave out anyone whose only pay was commissions and fees already listed on Schedule A, along with fees the employer paid directly and the plan didn't reimburse. A broker paid only through commissions on a fully insured plan can be missing entirely, so the chart counts relationships visible on Schedule C, not every plan a firm serves.
- **Ranking:** firms are ranked each year by the number of plans naming them, with ties broken alphabetically. The chart shows any firm in the top 10 in either 2019 or 2024.
- **Rebrands and acquisitions** (for example, NFP joining Aon in 2024) can shift counts.

### Chart 6: Industries

- The fastest-growing sector in the headline is picked from the 10 largest sectors by 2024 broker pay.

### Chart 8: Voluntary Benefits

- **The measure:** the share of single-employer plans with 100+ participants where at least one Schedule A contract is flagged other or indemnity and has no core line or stop-loss flag.
- **Voluntary is inferred from the benefit type.** Schedule A doesn't say who pays the premium, so an employer-paid accident or indemnity policy counts, and a voluntary product bundled into a contract with a core line doesn't.
- **Only plans with a Schedule A are counted.** Plans with no insured contracts at all, mostly fully self-funded ones, are left out of the base instead of counting as having no voluntary benefits.
- **Size bands differ from chart 4.** 1,000 to 4,999 participants is a single band here.

### Chart 9: Broker Wins & Losses

- **Who's included:** single-employer, welfare-only plans that name at least one Schedule C provider in two consecutive years. Each move is counted in the later year, and the totals cover every pair from 2019-2020 through 2023-2024.
- **Win:** a plan names the firm this year but didn't last year.
  - **From a local broker:** last year the plan named a provider whose relationship text contains BROKER, AGENT, CONSULT or ADVIS, but none of the 22 national firms.
  - **From a national rival:** last year the plan named at least one of the 22 firms.
  - Wins where the plan had neither last year (for example, only a TPA was listed) aren't shown.
- **Loss:** a plan named the firm last year but doesn't this year.
- **A win isn't always a switch.** The plan may keep its old firm and add the new one.
- **Exits aren't losses.** A plan that stops filing, falls outside the filing window or stops listing Schedule C providers drops out of the pair and isn't counted.
- **The chart 5 gaps apply here too.** If a firm's pay moves entirely to Schedule A commissions or to fees the employer pays directly, the firm disappears from Schedule C and looks like a loss.
- **Acquisitions can look like wins.** A move from a local broker to a national firm may be an acquisition rather than a competitive win.
- **Firms shown:** the 10 firms with the best 2024 rank on the chart 5 leaderboard.

### Chart 10: State Growth

- **The measure:** growth in broker pay from 2019 to 2024 by sponsor mailing state (see [Other Terms](#other-terms)).
- **Small markets are greyed out.** States with under $25M of broker pay in 2024 are shown in grey.
- **Fastest-growing needs scale.** Only states with at least $50M in 2019 can be named fastest-growing, so small states with big percentage swings don't take the headline.
- **Labels:** the 15 largest markets are labeled.

## Dashboard Differences

The Streamlit app runs the notebook's SQL against the parquet files in `data/exports` (see [`streamlit/figures/data.py`](../streamlit/figures/data.py)), so everything above applies to it. A few things work differently:

- **Filters:** every headline and chart recomputes for the selected year range, industry and state. The start and end of the range take the place of 2019 and 2024.
- **Thin size bands are hidden.** The self-funding and voluntary views skip any size band with fewer than 25 plans in a year.
- **State map cutoffs scale with the selection.** Grey marks states under 0.33% of end-year pay, and fastest-growing is limited to states with at least 0.93% of start-year pay. On the full market these come out to about the notebook's $25M and $50M.
- **Wins and losses:** the dashboard also counts wins from plans that had no broker the year before, plus plans kept. Net wins still only use wins from local brokers and national rivals, minus losses.
- **Retention:** plans kept divided by plans kept plus plans lost.
- **Momentum map:** only firms with at least 3 plans in the start year and at least 5 plans kept or lost are placed. The retention split is the median across those firms.
- **Every minimum base** the notebook and dashboard use is listed in [Minimum Bases](#minimum-bases).
- **Blank pay switch:** the take rate and fee adoption views can leave out contracts that left both commission and fees blank, instead of counting them as $0 (see [Blank Amounts](#blank-amounts)). Broker pay totals are the same either way.
- **Partial-year share:** the pay pool caption reports the share of contracts in the end year whose policy year is under 12 months. They stay in every total, as reported.
- **State growth without the top 5 plans:** the state map's tooltip and caption recompute each state's growth after removing the five plans whose broker pay rose the most, using each plan's state as filed in each year.
- **Carriers:** the carrier view groups contracts by `INS_CARRIER_NAIC_CODE`, then by `INS_CARRIER_EIN` when the NAIC code is missing, then by name, and labels each group with the name it files under most often. The 25 carriers with the most premium on the take-rate base are named and the rest are grouped as other carriers. Shares use premium on the take-rate base.
- **Calls:** the call and confidence badges (see [Confidence Ratings](#confidence-ratings)) describe the full market from 2019 to 2024, so they only show when no filter is applied.

### Accounts Page

One row per single-employer plan with 100+ participants and at least one Schedule A contract, taken from the plan's latest kept filing in the last two form years (2023 or 2024). The year filter doesn't apply; industry and state do.

| Column | How it's built |
|---|---|
| Sponsor, city | `SPONSOR_DFE_NAME` and `SPONS_DFE_MAIL_US_CITY` from the same filing. The EIN and plan number show when no name was filed |
| Lines | Every line of coverage on the filing's Schedule A contracts |
| Top carriers | Up to three carriers by premium, as filed |
| Broker pay | Commissions plus fees on contracts that pass the first three screens |
| Take rate | Broker pay divided by premium on contracts in the take-rate base |
| Band median | The median take rate among listed plans in the same size band |
| National firm | Tracked firms named on that year's Schedule C. Empty when the plan files no Schedule C, names no tracked firm, or also reports a pension benefit code (as in chart 5) |
| Self-funded | Offers health coverage (welfare code 4A) with no insured medical contract, as in chart 4 |
| Voluntary | Has a contract with only the other or indemnity flag, as in chart 8 |
| Changed firm | The tracked firms on Schedule C differ from the year before, for plans that list Schedule C providers in both years. A move from a local broker to a national firm counts |
| Amended | `AMENDED_IND` is 1 on the filing |
| Partial year | At least one contract's policy year is under 360 days |
| ACK ID | The filing the row comes from, for lookup on [EFAST2](https://www.efast.dol.gov/5500Search/) |