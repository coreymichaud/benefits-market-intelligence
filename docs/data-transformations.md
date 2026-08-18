# Data Transformations

The data for this analysis was put into a **DuckDB** data warehouse following the **Medallion** (bronze/silver/gold) architecture.

- The **Bronze** layer only contains raw data.
- The **Silver** layer contains cleaned & transformed data taken from the **Bronze** layer.
- The **Gold** layer contains the final analytics-ready data, obtained by final transformations of the **Silver** layer.

## Bronze Layer (`form_5500.bronze.*`)

This is the raw data layer, so **no** transformations were done. This layer was created by extracting the Form 5500 zip files and putting the raw `CSV` files into the `bronze` schema, each as their own table.

Table names were derived from the name of the **folder** each `CSV` was contained in.

## Silver Layer (`form_5500.silver.*`)

WIP!

## Gold Layer (`form_5500.gold.*`)

WIP!