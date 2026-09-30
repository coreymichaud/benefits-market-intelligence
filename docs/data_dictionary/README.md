# Data Dictionary

One page per table in `data/processed/form_5500.duckdb`, grouped by medallion layer.

| Layer | Pages | What the tables are |
|---|---|---|
| Bronze | [F_5500](01_bronze/F_5500.md), [F_SCH_A](01_bronze/F_SCH_A.md), [F_SCH_C_PART1_ITEM2](01_bronze/F_SCH_C_PART1_ITEM2.md) | The DOL CSVs as downloaded, one table per dataset and form year (18 tables). Every column is `VARCHAR`. |
| Silver | [F_5500](02_silver/F_5500.md), [SCH_A](02_silver/SCH_A.md), [SCH_C_P1_I2](02_silver/SCH_C_P1_I2.md) | The six years of each dataset stacked into one table, with `FORM_YEAR` added and numeric and date columns cast. |
| Gold | [F_5500](03_gold/F_5500.md), [SCH_A](03_gold/SCH_A.md), [SCH_C_P1_I2](03_gold/SCH_C_P1_I2.md) | The columns the analysis uses, also exported to `data/exports/*.parquet`. |

## Conventions

- **Column names** are the CSV headers exactly as DOL publishes them (upper case). A few differ from the names in DOL's layout files; each bronze page lists those differences.
- **Types** are DuckDB types: `VARCHAR`, `DOUBLE`, `DATE` and `INTEGER`. Bronze pages also show the layout file's own TEXT/NUMERIC label, which is what silver's casts are based on.
- **Descriptions** come from DOL's layout files.
- **Row counts** are from the build behind the current `data/exports` files. DOL refreshes its files about monthly, so a new download will change them slightly.

## Keeping it accurate

`tests/test_data_dictionary.py` checks these pages against the code on every run: the gold pages must list exactly the columns `03_gold.py` selects, and every silver type must match the cast lists in `02_silver.py`. When `data/processed/form_5500.duckdb` exists (after `make data`), the same test file also compares every page against the real tables and fails on any column or type that doesn't match.
