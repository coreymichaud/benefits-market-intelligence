# silver.SCH_C_P1_I2

The six `bronze."F_SCH_C_PART1_ITEM2_{year}_Latest"` tables stacked into one by `02_silver.py`, with `FORM_YEAR` added. Columns are in alphabetical order with `FORM_YEAR` last. A column missing from a year's file is null for that year. Columns in the script's numeric list are cast to `DOUBLE` and columns in its date list to `DATE` with `TRY_CAST`, so values that don't parse become null; everything else stays `VARCHAR`. No rows are filtered.

- **Rows:** 1,676,372
- **Columns:** 23

| Column | Type | Description |
| --- | --- | --- |
| `ACK_ID` | VARCHAR | Acknowledgment ID (PK) |
| `PROVIDER_OTHER_AMT_FORMULA_IND` | VARCHAR | Other provider amount formula indicator |
| `PROVIDER_OTHER_DIRECT_COMP_AMT` | DOUBLE | Other provider direct compensation |
| `PROVIDER_OTHER_EIN` | VARCHAR | Other provider EIN |
| `PROVIDER_OTHER_NAME` | VARCHAR | Other provider name |
| `PROVIDER_OTHER_RELATION` | VARCHAR | Other provider relationship |
| `PROVIDER_OTHER_SRVC_CODES` | VARCHAR | Other provider service codes |
| `PROVIDER_OTHER_US_ADDRESS1` | VARCHAR | Other provider US address |
| `PROVIDER_OTHER_US_ADDRESS2` | VARCHAR | Other provider US address |
| `PROVIDER_OTHER_US_CITY` | VARCHAR | Other provider US city |
| `PROVIDER_OTHER_US_STATE` | VARCHAR | Other provider US state |
| `PROVIDER_OTHER_US_ZIP` | VARCHAR | Other provider US ZIP code |
| `PROV_OTHER_ELIG_IND_COMP_IND` | VARCHAR | Other provider eligible indirect compensation indicator |
| `PROV_OTHER_FOREIGN_ADDRESS1` | VARCHAR | Other provider foreign address |
| `PROV_OTHER_FOREIGN_ADDRESS2` | VARCHAR | Other provider foreign address |
| `PROV_OTHER_FOREIGN_CITY` | VARCHAR | Other provider foreign city |
| `PROV_OTHER_FOREIGN_CNTRY` | VARCHAR | Other provider foreign country |
| `PROV_OTHER_FOREIGN_POSTAL_CD` | VARCHAR | Other provider foreign postal code |
| `PROV_OTHER_FOREIGN_PROV_STATE` | VARCHAR | Other provider foreign province/state |
| `PROV_OTHER_INDIRECT_COMP_IND` | VARCHAR | Other provider indirect compensation indicator |
| `PROV_OTHER_TOT_IND_COMP_AMT` | DOUBLE | Other provider total indirect compensation |
| `ROW_ORDER` | DOUBLE | Row order |
| `FORM_YEAR` | INTEGER | Form year of the source file, added in silver |
