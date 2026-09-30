# gold.SCH_C_P1_I2

A subset of `silver.SCH_C_P1_I2` columns chosen by `03_gold.py`, with every row kept. Types are unchanged from silver. `03_gold.py` also writes this table to `data/exports/SCH_C_P1_I2.parquet`, which the Streamlit dashboard reads.

- **Rows:** 1,675,037
- **Columns:** 9

| Column | Type | Description |
| --- | --- | --- |
| `ACK_ID` | VARCHAR | Acknowledgment ID (PK) |
| `PROVIDER_OTHER_NAME` | VARCHAR | Other provider name |
| `PROVIDER_OTHER_EIN` | VARCHAR | Other provider EIN |
| `PROVIDER_OTHER_SRVC_CODES` | VARCHAR | Other provider service codes |
| `PROVIDER_OTHER_RELATION` | VARCHAR | Other provider relationship |
| `PROVIDER_OTHER_DIRECT_COMP_AMT` | DOUBLE | Other provider direct compensation |
| `PROV_OTHER_INDIRECT_COMP_IND` | VARCHAR | Other provider indirect compensation indicator |
| `PROV_OTHER_TOT_IND_COMP_AMT` | DOUBLE | Other provider total indirect compensation |
| `FORM_YEAR` | INTEGER | Form year of the source file, added in silver |
