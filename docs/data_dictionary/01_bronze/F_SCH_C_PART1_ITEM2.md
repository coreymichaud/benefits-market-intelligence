# bronze.F_SCH_C_PART1_ITEM2_{year}_Latest

One table per form year, loaded as-is from DOL's "Latest" zip for that year by `01_bronze.py`. The CSV is read with `read_csv_auto(..., all_varchar = true)`, so every column in every bronze table is `VARCHAR`. The zip and CSV are stored in `data/raw/Form 5500 Schedule C Part 1, Item 2/`.

## Tables

| Table | Rows | Columns | Source |
| --- | --- | --- | --- |
| `bronze."F_SCH_C_PART1_ITEM2_2019_Latest"` | 283,445 | 22 | [F_SCH_C_PART1_ITEM2_2019_Latest.zip](https://askebsa.dol.gov/FOIA%20Files/2019/Latest/F_SCH_C_PART1_ITEM2_2019_Latest.zip) |
| `bronze."F_SCH_C_PART1_ITEM2_2020_Latest"` | 289,894 | 22 | [F_SCH_C_PART1_ITEM2_2020_Latest.zip](https://askebsa.dol.gov/FOIA%20Files/2020/Latest/F_SCH_C_PART1_ITEM2_2020_Latest.zip) |
| `bronze."F_SCH_C_PART1_ITEM2_2021_Latest"` | 294,522 | 22 | [F_SCH_C_PART1_ITEM2_2021_Latest.zip](https://askebsa.dol.gov/FOIA%20Files/2021/Latest/F_SCH_C_PART1_ITEM2_2021_Latest.zip) |
| `bronze."F_SCH_C_PART1_ITEM2_2022_Latest"` | 280,495 | 22 | [F_SCH_C_PART1_ITEM2_2022_Latest.zip](https://askebsa.dol.gov/FOIA%20Files/2022/Latest/F_SCH_C_PART1_ITEM2_2022_Latest.zip) |
| `bronze."F_SCH_C_PART1_ITEM2_2023_Latest"` | 263,253 | 22 | [F_SCH_C_PART1_ITEM2_2023_Latest.zip](https://askebsa.dol.gov/FOIA%20Files/2023/Latest/F_SCH_C_PART1_ITEM2_2023_Latest.zip) |
| `bronze."F_SCH_C_PART1_ITEM2_2024_Latest"` | 263,428 | 22 | [F_SCH_C_PART1_ITEM2_2024_Latest.zip](https://askebsa.dol.gov/FOIA%20Files/2024/Latest/F_SCH_C_PART1_ITEM2_2024_Latest.zip) |

## Columns

Column names are the CSV headers. Descriptions, layout types and maximum lengths come from the layout file DOL ships in each zip. "Layout type" is what the layout says the field holds; silver uses it to decide casts (see [02_silver/SCH_C_P1_I2.md](../02_silver/SCH_C_P1_I2.md)). "Years" shows which form years include the column; a column added partway through the period is null for earlier years in silver.

| Column | Description | Layout type | Max length | Years |
| --- | --- | --- | --- | --- |
| `ACK_ID` | Acknowledgment ID (PK) | TEXT | 30 | All |
| `ROW_ORDER` | Row order | NUMERIC |  | All |
| `PROVIDER_OTHER_NAME` | Other provider name | TEXT | 35 | All |
| `PROVIDER_OTHER_EIN` | Other provider EIN | TEXT | 9 | All |
| `PROVIDER_OTHER_US_ADDRESS1` | Other provider US address | TEXT | 35 | All |
| `PROVIDER_OTHER_US_ADDRESS2` | Other provider US address | TEXT | 35 | All |
| `PROVIDER_OTHER_US_CITY` | Other provider US city | TEXT | 22 | All |
| `PROVIDER_OTHER_US_STATE` | Other provider US state | TEXT | 2 | All |
| `PROVIDER_OTHER_US_ZIP` | Other provider US ZIP code | TEXT | 12 | All |
| `PROV_OTHER_FOREIGN_ADDRESS1` | Other provider foreign address | TEXT | 35 | All |
| `PROV_OTHER_FOREIGN_ADDRESS2` | Other provider foreign address | TEXT | 35 | All |
| `PROV_OTHER_FOREIGN_CITY` | Other provider foreign city | TEXT | 22 | All |
| `PROV_OTHER_FOREIGN_PROV_STATE` | Other provider foreign province/state | TEXT | 22 | All |
| `PROV_OTHER_FOREIGN_CNTRY` | Other provider foreign country | TEXT | 2 | All |
| `PROV_OTHER_FOREIGN_POSTAL_CD` | Other provider foreign postal code | TEXT | 22 | All |
| `PROVIDER_OTHER_SRVC_CODES` | Other provider service codes | TEXT | 0 | All |
| `PROVIDER_OTHER_RELATION` | Other provider relationship | TEXT | 25 | All |
| `PROVIDER_OTHER_DIRECT_COMP_AMT` | Other provider direct compensation | NUMERIC |  | All |
| `PROV_OTHER_INDIRECT_COMP_IND` | Other provider indirect compensation indicator | TEXT | 1 | All |
| `PROV_OTHER_ELIG_IND_COMP_IND` | Other provider eligible indirect compensation indicator | TEXT | 1 | All |
| `PROV_OTHER_TOT_IND_COMP_AMT` | Other provider total indirect compensation | NUMERIC |  | All |
| `PROVIDER_OTHER_AMT_FORMULA_IND` | Other provider amount formula indicator | TEXT | 1 | All |
