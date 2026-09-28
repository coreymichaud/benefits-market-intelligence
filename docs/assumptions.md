## Assumptions, caveats and limitations

**Filing lag and extensions**
- **The window:** each year keeps only filings received within 9.5 months of plan year end, which puts every year on equal footing.
- **Receipt date:** it comes from the first 8 digits of `ACK_ID`, which is the EFAST receipt timestamp.
- **Plan year end:** assumed to be 12 months after the begin date, because the actual end date isn't in gold. Short plan years get a slightly generous window.
- **Amended filings are a known leak.** DOL's "Latest" dataset keeps only the most recent version of each filing, so a plan that filed on time but amended later looks late and is dropped. The 12–17% excluded each year mixes truly late or delinquent filings with these late amendments.
- **2024 may be slightly incomplete.** The data snapshot ends August 24, 2026, so 2024 plan years that end after roughly October 2025 aren't fully observed. This affects a small share of non-calendar-year plans.

**Small plans (under 100 participants)**
- **Mostly excluded, because of the source data.** Fully insured and unfunded welfare plans with fewer than 100 participants are generally exempt from filing, so they never appear.
- **5500-SF filers are also missing.** Small plans that file the 5500-SF aren't loaded, and SF filers don't attach Schedule A.
- **Some small plans are included but not separately segmented.** Small plans that file the full Form 5500 anyway make up about 6–7% of welfare filings and appear in charts 1, 2, 3, 6 and 7.
- **Charts 4 and 5 are large-plan only.** Chart 4 excludes plans under 100 explicitly, and Schedule C (chart 5) is only required for large plans.
- **How to present it:** treat the findings as a view of the large-group market (100+ participants), not the small-group market.

**Covered counts**
- **What the lives field measures:** `INS_PRSN_COVERED_EOY_CNT` is the carrier-reported "persons covered" per contract. Some carriers report employees or certificates; others report total members including dependents. The data can't tell which. Medical and dental are more likely to include dependents, while life and disability are typically employee-only.
- **Per-life figures aren't comparable across lines** (charts 1 and 7 screens). Pay per covered life is understated for lines that count dependents and overstated for employee-only lines, and it isn't a per-employee-per-month figure.
- **Summed lives double-count people.** Someone with medical, dental and life counts three times, so the covered-lives total measures coverage volume, not unique people.
- **Trends are still valid** as long as each carrier's counting convention stays stable over time.
- **Plan-size bands use a different count.** `TOT_PARTCP_BOY_CNT` counts participants (employees and former employees), not dependents.

**Data quality**
- Self-reported dollar fields contain extreme errors, including single contracts reporting over $500 trillion in commissions. The analysis excludes:
  - negative amounts
  - contracts with zero, missing or over 1M lives
  - pay above $2,500 per covered life
  - for chart 7 only: premium above $50K per life, or pay above 100% of premium

  These screens remove about 2.5% of contracts, and totals barely move whether the pay cap is $1K or $5K.
- **Plans are deduplicated** to one filing per sponsor EIN, plan number and year, keeping the latest submission.
- **Multiemployer (Taft-Hartley) plans** are included in charts 1–3, 6 and 7 but excluded from charts 4 and 5.

**Definitions**
- **Line of coverage** is assigned per contract from the benefit flags. Contracts covering more than one line are grouped as "Multi-line bundle." "Voluntary & other" also captures AD&D-only and indemnity contracts.
- **"Carrier-paid fees"** are Schedule A fees paid by the insurer (bonuses, overrides, service fees). They are not fees paid directly by the employer, which don't appear on Schedule A.
- **Premium** is the non-experience-rated premium, or earned premium for experience-rated contracts, whichever is reported.
- **Chart 4's self-funding measure** is plans with no insured medical contract at all. That understates self-funding among large employers, who often keep an insured HMO alongside a self-funded plan.
- **Chart 5 counts firms by name matching** against 22 national brokers and consultants, and only where the firm received at least $5K and is listed on Schedule C. Rebrands and acquisitions (for example, NFP joining Aon in 2024) can shift counts.
- **Industry** comes from the sponsor's self-reported business code, grouped to top-level NAICS sectors.