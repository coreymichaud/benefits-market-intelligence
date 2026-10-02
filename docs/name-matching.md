# Name Matching

How the analysis decides that two records belong to the same plan, and which Schedule C providers belong to a national brokerage firm. Everything here uses only the names and IDs in the three DOL datasets. The patterns live in `BROKER_FIRMS`, which must stay identical in [`notebooks/analysis.ipynb`](../notebooks/analysis.ipynb) and [`streamlit/figures/constants.py`](../streamlit/figures/constants.py).

## Plans and Sponsors

- **A plan is its sponsor EIN plus plan number** (`SPONS_DFE_EIN` + `SPONS_DFE_PN`). Names are never used to identify a plan, so a sponsor that changes its name or spells it differently keeps its history.
- **EIN changes break a plan's history.** A sponsor that changes EIN (a merger, a restructuring, a new legal entity) or renumbers its plan gets a new plan key. The old key stops filing and the new one looks like a new plan. Nothing links the two in the data, so this isn't corrected. It mostly affects chart 9, where the plan drops out of the year-over-year comparison rather than counting as a broker switch.
- **One filing per plan and year:** see [Plan Identity & Deduplication](assumptions.md#plan-identity--deduplication).

## Brokerage Firms

### How a Name Is Matched

1. `PROVIDER_OTHER_NAME` is upper-cased and trimmed.
2. The name is tested against each firm's pattern, in the order of the table below. The first firm that matches wins.
3. If that firm also has an exclusion pattern and the name matches it, the firm is skipped and the next one is tried.
4. A name that matches no firm has no firm. See [Unmatched Names](#unmatched-names).

Patterns are regular expressions. `\b` is a word boundary, so `\bALERA\b` matches ALERA GROUP but not SALERA or CALERA, and `^` means the start of the name.

### Why Not Fuzzy Matching

There is no fuzzy matching and no similarity threshold. The companies that cause trouble have names only a letter or two apart from a national firm (SEGALL and SEGAL, SALERA and ALERA, WEDGEWOOD and EDGEWOOD), which is exactly what a similarity score treats as the same. The national firms' names are distinctive enough for exact rules, and rules give the same answer every run, can be read line by line, and can be tested against real names. The cost is that typos are missed: a name like ARTHER J GALLAGHER RISK MANAGMENT counts for no one. That affects a handful of rows.

### Patterns

| Firm | Counts when the name | Unless it |
|---|---|---|
| WTW | has the word WILLIS or TOWERS WATSON, starts with WTW, or reads WILLISTOWERSWATSON | contains INVESTMENT |
| Mercer | has the word MERCER | contains INVESTMENT, or is Mercer County, Island or University |
| Aon | starts with AON or AONHEWITT, or has AON CONSULTING, RISK or HEWITT | contains INVESTMENT |
| Gallagher | starts with GALLAGHER, or has ARTHUR (J.) GALLAGHER, A.J. GALLAGHER, GALLAGHER BENEFIT or ", A GALLAGHER" | contains FIDUCIARY or INVESTMENT |
| Marsh McLennan Agency | has MARSH & MC, MARSH AND MC, MARSH MC or MARSH USA | |
| Lockton | contains LOCKTON | |
| HUB International | starts with the word HUB or has HUB INT | |
| USI | starts with the word USI, or has USI INSURANCE or USI CONSULTING | |
| Brown & Brown | has BROWN & BROWN or BROWN AND BROWN | |
| OneDigital | has ONEDIGITAL, ONE DIGITAL or DIGITAL INSURANCE | contains INVESTMENT |
| AssuredPartners | has ASSUREDPARTNERS or ASSURED PARTNERS | |
| Alliant | has ALLIANT INS, ALLIANT EMPLOYEE or ALLIANT BEN | |
| NFP | starts with NFP or has NATIONAL FINANCIAL PARTNERS | |
| CBIZ | contains CBIZ | has the word CPA or CPAS |
| Segal | has the word SEGAL | has the word MARCO |
| McGriff | has MCGRIFF or TRUIST INSURANCE | |
| Acrisure | has ACRISURE | |
| Alera | has the word ALERA | |
| EPIC | has EDGEWOOD PARTNERS or starts with "EPIC " | |
| Holmes Murphy | has HOLMES MURPHY | |
| IMA | starts with the word IMA or has IMA FINANCIAL | |
| Hylant | has HYLANT | |

### What the Exclusions Remove

The firms are tracked as benefits brokers and consultants, so affiliates that do something else are left out. Across every Schedule C row from 2019 to 2024, the current patterns drop about 12,100 rows that looser substring patterns used to count:

- **Investment and fiduciary arms:** Mercer Investments, Aon Investments and Aon Hewitt Investment Consulting, Towers Watson Investment Services, OneDigital Investment Advisors, Gallagher Fiduciary Advisors and Segal Marco Advisors. These are most of the change.
- **Audit firms:** CBIZ CPAs, which audits plans rather than brokering their coverage.
- **Law firms:** Fusco Gallagher Porcaro Monro and Willkie Farr & Gallagher.
- **Look-alike names:** Segall Bryant & Hamill, Salera Employee Benefits, Calera Capital, Wedgewood Partners, Mercer University and people whose surname is Gallagher.

They also pick up about 330 rows the old patterns missed, such as names that are just USI or ONE DIGITAL, "... A DIVISION OF HUB INTER" and IMA, INC.

### Truncated Names

DOL cuts `PROVIDER_OTHER_NAME` off at 35 characters, so a name like FOX EVERETT A DIVISION OF HUB INTERNATIONAL arrives as FOX EVERETT A DIVISION OF HUB INTER. Patterns match the start of a firm's name where they can (HUB INT rather than HUB INTERNATIONAL) so truncated names still count.

### Unmatched Names

- **Nothing is guessed.** A name that matches no pattern is never assigned to the closest firm.
- **Broker-type providers become local brokers.** If an unmatched provider's relationship text contains BROKER, AGENT, CONSULT or ADVIS, chart 9 counts it as a local broker, which is how wins from local brokers are found. Any other unmatched provider (a TPA, an auditor, a law firm) is ignored.
- **Rankings only count matched names.** A national firm's plans filed under a name its pattern doesn't recognize are undercounted rather than given to someone else.

## Acquisitions and Rebrands

- **Rebrands are covered by the patterns.** Old and new names of the same firm are both in its pattern (for example, DIGITAL INSURANCE and ONEDIGITAL, WILLIS TOWERS WATSON and WTW).
- **Acquisitions are counted as reported.** Each filing counts toward the firm named on it in that year, and acquired firms aren't rolled into their buyer, because the acquisition dates aren't in the three datasets. When one tracked firm buys another (for example, NFP joining Aon in 2024), plans moving between the two names show as a loss for one and a win for the other, and the combined firm's history stays split.
- **Acquired local brokers can look like wins.** A national firm that buys a local agency shows up as winning that agency's plans from a local broker.

## Carriers

The dashboard's carrier view groups Schedule A contracts by `INS_CARRIER_NAIC_CODE`, the insurer's identifier from the filing. When the NAIC code is missing or all zeros it falls back to `INS_CARRIER_EIN`, then to the upper-cased name. Each group is labeled with the `INS_CARRIER_NAME` it files under most often. A NAIC code identifies one insurance company, so affiliates of the same parent (for example, separate state subsidiaries) show as separate carriers. Grouping them under a parent company would need outside information and isn't done. The Accounts page lists carrier names exactly as filed.

## Match Audit

Schedule C rows on the plans charts 5 and 9 use (single-employer, welfare-only filings that pass the filing window), from 2019 to 2024.

| Firm | Distinct names | Rows | Most common names (rows) |
|---|---:|---:|---|
| WTW | 90 | 931 | WILLIS TOWERS WATSON (299); WILLIS TOWERS WATSON US LLC (232) |
| OneDigital | 56 | 751 | DIGITAL INSURANCE, LLC (131); ONEDIGITAL (PHILADELPHIA) (131) |
| Gallagher | 38 | 565 | GALLAGHER BENEFIT SERVICES (179); GALLAGHER BENEFIT SERVICES INC (114) |
| Brown & Brown | 86 | 493 | BROWN & BROWN OF PA (54); BROWN & BROWN (PA) (44) |
| Marsh McLennan Agency | 76 | 481 | MARSH & MCLENNAN AGENCY LLC (171); MARSH & MCLENNAN AGENCY (48) |
| HUB International | 79 | 470 | HUB INTERNATIONAL MIDWEST LTD (83); HUB INTERNATIONAL MIDWEST LIMITED (75) |
| Aon | 39 | 451 | AON CONSULTING, INC. (101); AON CONSULTING (97) |
| Mercer | 24 | 444 | MERCER HEALTH & BENEFITS LLC (150); MERCER (118) |
| Lockton | 23 | 443 | LOCKTON COMPANIES, LLC (306); LOCKTON COMPANIES LLC (74) |
| AssuredPartners | 79 | 405 | ASSURED PARTNERS (CENTRAL PA) (145); ASSURED PARTNERS (44) |
| McGriff | 30 | 387 | MCGRIFF INSURANCE SERVICES (89); MCGRIFF INSURANCE SERVICES INC (89) |
| USI | 51 | 381 | USI INSURANCE SERVICES LLC (149); USI INSURANCE SERVICES (42) |
| Segal | 27 | 253 | THE SEGAL COMPANY (78); SEGAL CONSULTING (29) |
| CBIZ | 39 | 250 | CBIZ BENEFITS & INSURANCE SERVICES (42); CBIZ (25) |
| Acrisure | 39 | 206 | ACRISURE LLC (93); ACRISURE, LLC (26) |
| Alliant | 27 | 202 | ALLIANT INSURANCE SERVICES INC (76); ALLIANT INSURANCE SERVICES, INC. (44) |
| NFP | 51 | 199 | NFP CA INSURANCE SERVICES (34); NFP CORPORATE SERVICES (26) |
| Holmes Murphy | 19 | 145 | HOLMES MURPHY & ASSOCIATES (35); HOLMES MURPHY & ASSOCIATES INC (32) |
| Alera | 34 | 124 | DAVIDSON BENEFITS AN ALERA AGENCY (42); COURY HEALTH SERVICES (ALERA) (7) |
| IMA | 7 | 100 | IMA, INC. (63); IMA FINANCIAL GROUP (ECM SOLUTIONS) (14) |
| EPIC | 18 | 88 | EDGEWOOD PARTNERS INSURANCE CENTER (41); EPIC INSURANCE BROKERS (CENTRAL PA) (10) |
| Hylant | 8 | 85 | HYLANT GROUP INC (31); HYLANT GROUP (19) |

Of 123,400 rows, 7,854 match a firm (940 distinct names), and 18,842 rows (2,936 names) are broker-type providers with no match, counted as local brokers. The largest of those are regional firms whose names carry no tracked firm's name:

| Unmatched broker-type name | Rows |
|---|---:|
| THE BENECON GROUP (three spellings) | 5,626 |
| MCCONKEY BENEFITS & FINANCIAL SERV | 321 |
| BSI CORPORATE BENEFITS (two spellings) | 287 |
| EBENCONCEPTS COMPANY | 157 |
| EMERITI RETIREMENT HEALTH SOLUTIONS | 150 |
| PCI INSURANCE AGENCY | 145 |
| MCGOHAN BRABENDER, INC. | 130 |
| ENGLE HAMBRIGHT & DAVIES, INC. | 124 |
| BUKATY COMPANIES | 115 |