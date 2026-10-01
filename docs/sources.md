# Sources

## Data

This project uses three U.S. Department of Labor datasets and nothing else. Each is downloaded as one "Latest" zip per form year from 2019 to 2024 by [`01_bronze.py`](../src/benefits_market_intelligence/elt/01_bronze.py).

| Dataset | Contents | File pattern |
|---|---|---|
| `F_5500` | Main Form 5500 | `https://askebsa.dol.gov/FOIA%20Files/{year}/Latest/F_5500_{year}_Latest.zip` |
| `F_SCH_A` | Schedule A insurance contracts | `https://askebsa.dol.gov/FOIA%20Files/{year}/Latest/F_SCH_A_{year}_Latest.zip` |
| `F_SCH_C_PART1_ITEM2` | Schedule C Part 1 Item 2 service providers | `https://askebsa.dol.gov/FOIA%20Files/{year}/Latest/F_SCH_C_PART1_ITEM2_{year}_Latest.zip` |

- U.S. Department of Labor, Employee Benefits Security Administration. [Form 5500 Datasets](https://www.dol.gov/agencies/ebsa/about-ebsa/our-activities/public-disclosure/foia/form-5500-datasets). The landing page for the files above.
- Each zip includes DOL's layout file for that dataset and year. The column descriptions in the [data dictionary](data_dictionary/README.md) come from those layout files.

## Documentation

These explain the data; no values are taken from them.

- U.S. Department of Labor. [Form 5500 Datasets Guide](https://www.dol.gov/sites/dolgov/files/EBSA/about-ebsa/our-activities/public-disclosure/foia/form-5500-dataset-guide.pdf). Form year versus plan year, "All" versus "Latest" files, and how schedules join to the main form.
- U.S. Department of Labor. [Reporting and Filing](https://www.dol.gov/agencies/ebsa/employers-and-advisers/plan-administration-and-compliance/reporting-and-filing). The Form 5500 series forms and instructions, including Schedules A and C, used for filing deadlines, field meanings and who must file.
- U.S. Department of Labor. [EFAST2 Form 5500 Search](https://www.efast.dol.gov/5500Search/). Public lookup of individual filings, used to trace a row back to its filed form by `ACK_ID`.

## Reference Codes

- U.S. Census Bureau. [North American Industry Classification System](https://www.census.gov/naics/). The sector names used to group the two-digit `BUSINESS_CODE` prefixes. The business code itself comes from the filing.