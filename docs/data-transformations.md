# Data Transformations

The data for this analysis was put into a **DuckDB** data warehouse following the **Medallion** (bronze/silver/gold) architecture.

- The **Bronze** layer only contains raw data.
- The **Silver** layer contains cleaned & transformed data taken from the **Bronze** layer.
- The **Gold** layer contains the final analytics-ready data, obtained by final transformations of the **Silver** layer.

## Bronze Layer (`form_5500.bronze.*`)

This is the raw data layer, so **no** transformations were done. This layer was created by extracting the Form 5500 zip files and putting the raw `CSV` files into the `bronze` schema, each as their own table.

Table names were derived from the name of the **folder** each `CSV` was contained in.

## Silver Layer (`form_5500.silver.*`)

Each of the **3** forms is made up of **6** files, one for each year. This layer combined those files into one per form, with an added `FORM_YEAR` column to show what form year that row was for.

The only other transformation for each table is the declaration of data types dictated by each extracted dataset's `layouts.txt` file. The only data types added were `string`, `numeric`, and (not shown in the layouts file) `datetime`. These show up differently when querying depending on the query method.

## Gold Layer (`form_5500.gold.*`)

Taking from the 3 form tables within the `silver` schema, each table had a great number of columns removed. This is because the columns that remain are the most valuable for getting insights from, while the ones removed are not very valuable for what we wanted to find. This also helps reduce query time and visualization lag.