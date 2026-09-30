# Data Transformations

The pipeline loads three DOL datasets into a **DuckDB** warehouse (`data/processed/form_5500.duckdb`) in three **medallion** layers. Each layer is one script in `src/benefits_market_intelligence/elt/`, run in order by `make data`. Column-level details for every table are in the [data dictionary](data_dictionary/README.md).

```
DOL "Latest" zips (3 datasets x 6 form years)
  -> bronze: 18 raw tables, all text
  -> silver: 3 tables, one per dataset, years stacked and types cast
  -> gold:   3 tables with the columns the analysis uses, exported to data/exports/*.parquet
  -> analysis notebook and Streamlit dashboard
```

| Dataset | Bronze tables | Silver table | Gold table and export |
|---|---|---|---|
| Form 5500 | `bronze."F_5500_{year}_Latest"` | `silver.F_5500` | `gold.F_5500`, `data/exports/F_5500.parquet` |
| Schedule A | `bronze."F_SCH_A_{year}_Latest"` | `silver.SCH_A` | `gold.SCH_A`, `data/exports/SCH_A.parquet` |
| Schedule C Part 1 Item 2 | `bronze."F_SCH_C_PART1_ITEM2_{year}_Latest"` | `silver.SCH_C_P1_I2` | `gold.SCH_C_P1_I2`, `data/exports/SCH_C_P1_I2.parquet` |

No layer removes, deduplicates or filters rows. Every analysis rule (the filing window, one filing per plan per year, the data quality screens, line of coverage and broker firm matching) is applied later, in the SQL shared by the analysis notebook and the dashboard, and is documented in [assumptions.md](assumptions.md).

## Bronze (`01_bronze.py`)

For each dataset and each form year from 2019 to 2024, the script:

1. Downloads `https://askebsa.dol.gov/FOIA%20Files/{year}/Latest/{dataset}_{year}_Latest.zip` into `data/raw/<dataset folder>/`.
2. Checks the zip holds exactly one CSV and stops with an error if it holds none or several.
3. Extracts the zip (the CSV and DOL's layout file) into a folder named after the zip.
4. Loads the CSV into `bronze."{dataset}_{year}_Latest"` with `read_csv_auto(header = true, all_varchar = true)`, so every column is `VARCHAR` and nothing is lost to a bad type guess.
5. Deletes the zip.

Column names are the CSV headers exactly as DOL publishes them. A few differ from the names in DOL's layout file; the bronze dictionary pages list them. Every run downloads all 18 files again.

## Silver (`02_silver.py`)

For each dataset, the script stacks the six yearly bronze tables into one silver table:

- **Columns:** the union of every year's columns, in alphabetical order. A column missing from a year's file (DOL added a few Form 5500 fields partway through the period) is `NULL` for that year.
- **Types:** columns in the script's numeric lists are cast to `DOUBLE` and columns in its date lists to `DATE`, both with `TRY_CAST`, so a value that doesn't parse becomes `NULL` rather than failing the load. Everything else stays `VARCHAR`. The numeric lists are the fields DOL's layout files mark as NUMERIC; the date lists were picked by hand, since the layouts label dates as text. `INS_PRSN_COVERED_EOY_CNT` is text in the layout, so it stays `VARCHAR` and the analysis casts it when it needs a number.
- **`FORM_YEAR`:** an `INTEGER` column holding the year of the bronze table each row came from, added last.
- **Rows:** every bronze row, combined with `UNION ALL`.

The script prints the row and column count of each silver table when it finishes.

## Gold (`03_gold.py`)

Each gold table is a `SELECT` of named columns from its silver table, with every row kept and types unchanged:

| Table | Columns kept | Why |
|---|---|---|
| `gold.F_5500` | 24 of 141 | Plan identity (`ACK_ID`, sponsor EIN, plan number), plan year begin date, participant counts, business code, plan entity type, pension and welfare benefit codes, schedule-attached flags, mailing state and `FORM_YEAR` |
| `gold.SCH_A` | 29 of 91 | Carrier name, benefit type flags, premium fields, broker commission and fee totals, persons covered, `FORM_ID` and `FORM_YEAR` |
| `gold.SCH_C_P1_I2` | 9 of 23 | Provider name, EIN, relationship, service code field, direct and indirect compensation and `FORM_YEAR` |

The script then writes each gold table to `data/exports/<table>.parquet`. Those files are committed so the dashboard can run without rebuilding the warehouse.

## Row Counts

From the build behind the current `data/exports` files:

| Dataset | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | Silver and gold |
|---|---:|---:|---:|---:|---:|---:|---:|
| Form 5500 | 247,906 | 249,386 | 243,798 | 243,474 | 231,872 | 225,591 | 1,442,027 |
| Schedule A | 329,228 | 337,555 | 333,481 | 339,654 | 339,696 | 336,310 | 2,015,924 |
| Schedule C Part 1 Item 2 | 283,445 | 289,894 | 294,522 | 280,495 | 263,253 | 263,428 | 1,675,037 |
