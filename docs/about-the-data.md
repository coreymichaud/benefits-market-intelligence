# Form 5500 Data

The Form 5500 Series is the annual return/report that employee benefit plans use to satisfy filing requirements under the Employee Retirement Income Security Act (ERISA), with joint oversight from the Internal Revenue Service (IRS), the Department of Labor's Employee Benefits Security Administration (EBSA), and the Pension Benefit Guaranty Corporation (PBGC). Plan sponsors and administrators file electronically through **EFAST2** (the ERISA Filing Acceptance System), and completed filings become part of the public record.

At its core, each Form 5500 filing identifies who sponsors a benefit plan, what type of plan it is, which insurance carriers and brokers are involved, what the plan pays in premiums and compensation, and how many people are covered. Assembled across employers, years, benefit lines, industries, and geographies, this data can surface which brokers and carriers dominate specific market segments, how disclosed premiums, commissions, and fees trend over time, and where compensation patterns or broker-carrier relationships look unusual relative to peers. Typical downstream uses include broker leaderboards, carrier market-share views, employer-level plan economics, geographic and sector heat maps, and multi-year switching or growth analyses.

## Data Source & Coverage

- **Source:** [DOL EFAST Form 5500 Datasets](https://www.dol.gov/agencies/ebsa/about-ebsa/our-activities/public-disclosure/foia/form-5500-datasets)
- **Form years covered:** 2019 to 2024. DOL organizes these files by *form year*, the year printed on the form, not by the plan year the filer entered. A late filing for an old plan year can land in a newer form year's file, which is one reason the analysis applies a filing window (see [assumptions.md](assumptions.md)).
- **"Latest" files:** DOL publishes two versions of each dataset. The "All" files keep every submission, including amended and duplicate filings. The "Latest" files, which this project downloads, keep only the most recent filing for each plan and year, so an amended return replaces the original.
- **Refresh cycle:** DOL rebuilds the files roughly monthly as new filings arrive, so row counts change slightly between downloads.
- **Filing lag:** because plans can request extensions, a form year's filings keep arriving for months after the nominal deadline. Treat the most recent form year as still filling in.

## Forms & Schedules in This Dataset

This analysis uses three datasets from the Form 5500 filing package and nothing else. Each has a different filing trigger and a different grain (unit of record), summarized below:

| Component | Required When | Grain | Primarily Captures |
|---|---|---|---|
| **Form 5500 (Main)** | All ERISA-covered pension and welfare plans filing the full form (as opposed to the abbreviated 5500-SF) | Plan, per plan year | Sponsor, plan type, participant counts, financial summary |
| **Schedule A** | Plan provides benefits in whole or in part through an insurance contract | Insurance contract, per filing | Carrier, coverage, premiums, total commissions and fees paid to agents and brokers |
| **Schedule C, Part I, Item 2** | "Large" plans (generally 100+ participants at the start of the plan year) that compensate a service provider $5,000 or more | Service provider, per plan, per plan year | Direct and indirect compensation, services rendered, provider relationship to the plan |

A single filing can have several Schedule A and Schedule C rows. For example, a plan with medical, dental and life coverage through three carriers files three Schedule As, one row each in the Schedule A dataset.

## Form 5500 (Main): Annual Return/Report

The Main form is the annual filing required of most retirement and welfare benefit plans covered by ERISA. It establishes the plan-level record that the Schedule A and Schedule C rows attach to, and includes:

- **Plan identification:** plan name, three-digit plan number, and the sponsor's Employer Identification Number (EIN)
- **Sponsor and administrator details:** legal name, address, and administrator information (if different from the sponsor)
- **Plan classification:** pension vs. welfare plan, plan features/benefit codes, and funding arrangement
- **Participant counts:** active participants, retired or separated participants receiving or entitled to benefits, and total covered lives at the start and end of the plan year
- **Filing metadata:** plan year begin/end dates and a unique acknowledgment ID (ACK ID) assigned by EFAST2 to each filing

## Schedule A: Insurance Information

Schedule A is filed for each insurance contract a plan uses to provide benefits. This is common for fully insured medical, dental, vision, life, disability, and stop-loss arrangements. It discloses:

- **Carrier and contract details:** insurance company name, NAIC code, and contract/policy number
- **Coverage particulars:** type of benefit, policy period, and approximate number of persons covered
- **Premium activity:** premiums paid during the policy year
- **Commission and fee totals:** the total commissions and total fees paid to all agents and brokers on the contract (`INS_BROKER_COMM_TOT_AMT` and `INS_BROKER_FEES_TOT_AMT`)

A useful distinction for analysis: **commissions** are sales or base amounts tied directly to placing or retaining a contract, while **fees** cover other forms of compensation such as service fees, consulting fees, finder's fees, and persistency or profitability bonuses.

The paper form also lists each individual broker and what that broker was paid (line 3), but DOL publishes those rows as a separate dataset that this project does not use. The Schedule A dataset used here has one row per contract with the totals only, so it supports carrier and line-of-coverage analysis but does not name brokers. Broker firms in this project come from Schedule C.

## Schedule C, Part I, Item 2: Service Provider Compensation

Schedule C applies only to large plans (generally 100 or more participants at the beginning of the plan year) and certain direct filing entities. Part I, Item 2 requires the plan to list every person who received, directly or indirectly, **$5,000 or more** in reportable compensation in connection with services rendered to the plan or their position with the plan. It documents:

- **Provider identity:** name and EIN (or address, for individuals without one)
- **Relationship:** free text describing the provider's relationship to the employer or plan (for example, "broker" or "consultant"). The form also asks for service codes, but the code field in this dataset (PROVIDER_OTHER_SRVC_CODES) is empty in every year, so it is dropped from gold; DOL publishes the codes in a separate file that this project does not use, so the analysis reads the relationship text instead
- **Compensation detail:** direct compensation (paid directly by the plan) reported separately from indirect compensation (received from a third party, such as revenue sharing, 12b-1 fees, or sub-transfer-agency fees)
- **Formula vs. fixed-amount reporting:** indirect compensation reported either as a dollar amount or, in some cases, by the formula used to calculate it

Notable exclusions from this reporting requirement include payments the plan sponsor makes directly and does not get reimbursed for by the plan, and plan employees whose only plan-related compensation falls below a minimum threshold. Because Schedule C captures compensation regardless of whether it flowed through an insurance contract, it complements Schedule A by surfacing broker and consultant compensation on self-insured or administrative-services-only arrangements that Schedule A would not otherwise reveal.

## Analytical Applications

Joining these three datasets on `ACK_ID` (and on the sponsor EIN, plan number and form year across years) supports analyses such as:

- **Broker and carrier leaderboards:** carriers by premium or broker pay from Schedule A, and broker firms by plans served from Schedule C
- **Market share views** by carrier, broker, industry (via sponsor NAICS code, where available), or geography
- **Employer-level plan economics:** premiums, participant counts, and cost per participant over time
- **Compensation transparency:** comparing a plan's insurance-based broker pay on Schedule A with the service-provider pay it reports on Schedule C
- **Multi-year trend and switching analysis:** tracking carrier or broker changes at the plan level, and identifying compensation patterns that diverge from peer norms

## Out of Scope

This project leaves out every other Form 5500 dataset, including the short Form 5500-SF, Schedule H (large plan financial information), Schedule I (small plan financial information), Schedule R (retirement plan distributions and other information), Schedule MB and Schedule SB (actuarial information for multiemployer and single-employer defined benefit plans, respectively), Schedule D (DFE/participating plan information), and Schedule C Parts II and III. Each of these has analytical value in its own right, but falls outside the current scope of this analysis.

## Limitations & Considerations

- All figures are **self-reported** by plan sponsors, administrators, and service providers, and are subject to filer error or inconsistent interpretation of instructions.
- Reporting thresholds and instructions have changed over time (for example, Schedule C's indirect-compensation disclosure requirements were substantially revised for plan years beginning in 2009), so care should be taken when comparing filings across years with different form versions.
- Not every plan is required to file every schedule; the absence of a Schedule A or Schedule C for a given plan/year may reflect a self-insured arrangement or a plan below the large-plan threshold rather than a data gap.
- The most recent form year may be incomplete because of filing extensions.