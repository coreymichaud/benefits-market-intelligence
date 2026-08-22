# Form 5500 Data

The Form 5500 Series is the annual return/report that employee benefit plans use to satisfy filing requirements under the Employee Retirement Income Security Act (ERISA), with joint oversight from the Internal Revenue Service (IRS), the Department of Labor's Employee Benefits Security Administration (EBSA), and the Pension Benefit Guaranty Corporation (PBGC). Plan sponsors and administrators file electronically through **EFAST2** (the ERISA Filing Acceptance System), and completed filings become part of the public record.

At its core, each Form 5500 filing identifies who sponsors a benefit plan, what type of plan it is, which insurance carriers and brokers are involved, what the plan pays in premiums and compensation, and how many people are covered. Assembled across employers, years, benefit lines, industries, and geographies, this data can surface which brokers and carriers dominate specific market segments, how disclosed premiums, commissions, and fees trend over time, and where compensation patterns or broker-carrier relationships look unusual relative to peers. Typical downstream uses include broker leaderboards, carrier market-share views, employer-level plan economics, geographic and sector heat maps, and multi-year switching or growth analyses.

## Data Source & Coverage

- **Source:** [DOL EFAST Form 5500 Datasets](https://www.dol.gov/agencies/ebsa/about-ebsa/our-activities/public-disclosure/foia/form-5500-datasets)
- **Plan years covered:** 2019–2024
- **Form version:** Latest published revision of each form/schedule for the corresponding plan year
- **Filing lag:** Because plans can request extensions, a given plan year's filings continue to trickle in for up to several months after the nominal deadline, and the most recent plan year(s) in this dataset should be treated as still-maturing rather than final

## Forms & Schedules in This Dataset

This analysis draws on three components of the Form 5500 filing package. Each has a different filing trigger and a different grain (unit of record), summarized below:

| Component | Required When | Grain (One Row Per) | Primarily Captures |
|---|---|---|---|
| **Form 5500 (Main)** | All ERISA-covered pension and welfare plans filing the full form (as opposed to the abbreviated 5500-SF) | Plan, per plan year | Sponsor, plan type, participant counts, financial summary |
| **Schedule A** | Plan provides benefits in whole or in part through an insurance contract | Insurance contract, per plan, per plan year | Carrier, coverage, premiums, commissions/fees paid to agents and brokers |
| **Schedule C, Part I, Item 2** | "Large" plans (generally 100+ participants at the start of the plan year) that compensate a service provider $5,000 or more | Service provider, per plan, per plan year | Direct and indirect compensation, services rendered, provider relationship to the plan |

A single plan/year can generate multiple Schedule A and Schedule C rows — for example, a plan with medical, dental, and life coverage through three different carriers will file three Schedule As, each potentially listing several commission recipients.

## Form 5500 (Main) — Annual Return/Report

The Main form is the annual filing required of most retirement and welfare benefit plans covered by ERISA. It establishes the plan-level record that the Schedule A and Schedule C rows attach to, and includes:

- **Plan identification:** plan name, three-digit plan number, and the sponsor's Employer Identification Number (EIN)
- **Sponsor and administrator details:** legal name, address, and administrator information (if different from the sponsor)
- **Plan classification::** pension vs. welfare plan, plan features/benefit codes, and funding arrangement
- **Participant counts:** active participants, retired or separated participants receiving or entitled to benefits, and total covered lives at the start and end of the plan year
- **Financial summary:** high-level assets, liabilities, contributions, and benefit payments (drawn from the corresponding Schedule H or I, which are not part of this dataset)
- **Filing metadata:** plan year begin/end dates and a unique acknowledgment ID (ACK ID) assigned by EFAST2 to each filing

## Schedule A — Insurance Information

Schedule A is filed for each insurance contract a plan uses to provide benefits — common for fully insured medical, dental, vision, life, disability, and stop-loss arrangements. It discloses:

- **Carrier and contract details:** insurance company name, NAIC code, and contract/policy number
- **Coverage particulars:** type of benefit, policy period, and approximate number of persons covered
- **Premium activity:** premiums paid during the policy year
- **Commission and fee detail (Line 3):** every agent, broker, or other person who received a commission or fee, listed in descending order of amount paid, along with an organization/relationship code (e.g., "insurance agent or broker") and a purpose code

A useful distinction for analysis: **commissions** are sales or base amounts tied directly to placing or retaining a contract, while **fees** cover other forms of compensation such as service fees, consulting fees, finder's fees, and persistency or profitability bonuses. Because Line 3 entries are broker/recipient-level, Schedule A is the primary source for broker- and carrier-level market analysis.

## Schedule C, Part I, Item 2 — Service Provider Compensation

Schedule C applies only to large plans (generally 100 or more participants at the beginning of the plan year) and certain direct filing entities. Part I, Item 2 requires the plan to list every person who received, directly or indirectly, **$5,000 or more** in reportable compensation in connection with services rendered to the plan or their position with the plan. It documents:

- **Provider identity:** name and EIN (or address, for individuals without one)
- **Relationship and service codes:** whether the provider acted as a fiduciary, contract administrator, consultant, recordkeeper, broker, investment adviser, or in another capacity, and which services were performed
- **Compensation detail:** direct compensation (paid directly by the plan) reported separately from indirect compensation (received from a third party, such as revenue sharing, 12b-1 fees, or sub-transfer-agency fees)
- **Formula vs. fixed-amount reporting:** indirect compensation reported either as a dollar amount or, in some cases, by the formula used to calculate it

Notable exclusions from this reporting requirement include payments the plan sponsor makes directly and does not get reimbursed for by the plan, and plan employees whose only plan-related compensation falls below a minimum threshold. Because Schedule C captures compensation regardless of whether it flowed through an insurance contract, it complements Schedule A by surfacing broker and consultant compensation on self-insured or administrative-services-only arrangements that Schedule A would not otherwise reveal.

## Analytical Applications

Combining these three components, typically joined on ACK ID or on the sponsor EIN, plan number, and plan year, supports analyses such as:

- **Broker and carrier leaderboards** ranked by premium volume, commission income, or plan count
- **Market share views** by carrier, broker, industry (via sponsor NAICS code, where available), or geography
- **Employer-level plan economics:** premiums, participant counts, and cost per participant over time
- **Compensation transparency:** cross-referencing Schedule A and Schedule C to compare insurance-based commissions against service-provider fees for the same broker or consultant
- **Multi-year trend and switching analysis:** tracking carrier or broker changes at the plan level, and identifying compensation patterns that diverge from peer norms

## Out of Scope

This dataset intentionally excludes the other Form 5500 schedules, including Schedule H (large plan financial information), Schedule I (small plan financial information), Schedule R (retirement plan distributions and other information), Schedule MB and Schedule SB (actuarial information for multiemployer and single-employer defined benefit plans, respectively), Schedule D (DFE/participating plan information), and Schedule C Parts II and III. Each of these has analytical value in its own right, but falls outside the current scope of this analysis.

## Limitations & Considerations

- All figures are **self-reported** by plan sponsors, administrators, and service providers, and are subject to filer error or inconsistent interpretation of instructions.
- Reporting thresholds and instructions have changed over time (for example, Schedule C's indirect-compensation disclosure requirements were substantially revised for plan years beginning in 2009), so care should be taken when comparing filings across years with different form versions.
- Not every plan is required to file every schedule; the absence of a Schedule A or Schedule C for a given plan/year may reflect a self-insured arrangement or a plan below the large-plan threshold rather than a data gap.
- The most recent plan year(s) in this dataset may be incomplete due to filing extensions.