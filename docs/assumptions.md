# Assumptions, Caveats & Limitations

This document covers the rules and judgment calls behind the analysis in [`notebooks/analysis.ipynb`](../notebooks/analysis.ipynb) and the Streamlit dashboard, along with the limits they put on what the charts can say. Chart numbers follow the notebook sections. For background on the forms themselves, see [about-the-data.md](about-the-data.md). For how the tables were built, see [data-transformations.md](data-transformations.md).

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
- **Receipt date:** taken from the first 8 digits of `ACK_ID`, which is the EFAST receipt timestamp.
- **Plan year end:** assumed to be 12 months after `FORM_PLAN_YEAR_BEGIN_DATE`, because the actual end date isn't in gold. In SQL the cutoff is the begin date plus 21 months and 14 days. Short plan years get a slightly generous window.
- **What gets dropped:** between about 11% and 17% of welfare filings in each year from 2019 to 2023, and about 8% for 2024. That group mixes three things: filings that really were late or delinquent, on-time filings that were amended later (see below), and catch-up filings for plan years several years back that DOL files under a newer form year. The catch-up group is about 27,000 welfare filings. Since the window is measured from the plan year begin date, all of them fall out, which also keeps them from being counted in the wrong year.
- **Amended filings are a known leak.** DOL's "Latest" dataset keeps only the most recent version of each filing, so a plan that filed on time but amended later looks late and is dropped. Older years have had longer to pick up amendments, so the leak is probably a bit larger for them than for 2023 and 2024.
- **2024's lower exclusion rate isn't better compliance.** Late 2024 filings are still coming in, so fewer of them exist yet to be excluded.
- **2024 may be slightly incomplete.** The data snapshot ends August 24, 2026. 2024 plan years that begin after about mid-November 2024 haven't reached the end of their window, so some of their on-time filings may not be in the data yet. That's about 2.5% of 2024 welfare filings, all of them non-calendar-year plans.

## Plan Identity & Deduplication

- **Plan key:** a plan is its sponsor EIN plus its three-digit plan number (`SPONS_DFE_EIN` + `SPONS_DFE_PN`).
- **One filing per plan per year:** filings are deduplicated to one per sponsor EIN, plan number and year, keeping the latest submission (highest `ACK_ID`). This runs after the filing window, so the filing that's kept is the latest on-time one.
- **Plan year:** `FORM_YEAR` is used as the plan year. After the filing window, the plan year begins in `FORM_YEAR` for all but about 1,100 filings.
- **Mergers and renumbering:** if a sponsor changes its EIN or renumbers a plan, the plan looks brand new. This mostly matters for chart 9, which follows plans from one year to the next.

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

## Dollar Amounts

- **Self-reported, and sometimes badly wrong.** Dollar fields contain extreme errors, including single contracts reporting over $500 trillion in commissions. The screens in the next section handle these.
- **Blanks count as zero.** A missing commission or fee amount is treated as $0.
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

- The first three screens remove just under 2.5% of contracts. Yearly totals move by less than 4% whether the pay cap is $1K or $5K.
- Charts 4 and 8 don't use these screens. They only look at which benefits a contract covers, not at dollar amounts.
- Charts 5 and 9 come from Schedule C and don't use them either.

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

- **The measure:** the share of single-employer health plans (welfare code `4A`) with 100+ participants that have no insured medical contract on Schedule A. Stop-loss contracts don't count as insured medical, so level-funded plans read as self-funded.
- **It understates self-funding among large employers,** who often keep an insured HMO alongside a self-funded plan under the same plan number.
- **Missing schedules read as self-funded.** A health plan with no Schedule A at all counts as self-funded, so a filer that should have attached one and didn't gets misclassified.

### Chart 5: Broker Leaderboard

- **Firms are found by name.** Schedule C provider names are upper-cased, trimmed and matched against patterns for 22 national brokers and consultants (`BROKER_FIRMS` in the notebook). A name takes the first firm whose pattern matches.
- **Matching is loose.** Most patterns are plain substrings, so a local agency that happens to share a name with a national firm gets counted with it. A firm also counts regardless of its role on the plan, so a consulting or actuarial relationship counts the same as a brokerage one.
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