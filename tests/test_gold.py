import duckdb
import pandas as pd
from conftest import run_step

from benefits_market_intelligence.config import paths


def test_gold_keeps_only_the_selected_columns_and_exports_parquet(silver):
    gold = run_step("03_gold")
    for table, columns in gold["tables_tcols"].items():
        with duckdb.connect(paths.DB_PATH) as con:
            actual = [r[0] for r in con.execute(f"describe gold.{table}").fetchall()]
        assert actual == columns

        export = pd.read_parquet(paths.EXPORTS_PATH / f"{table}.parquet")
        assert list(export.columns) == columns
        assert len(export) == 12  # 2 rows x 6 years


def test_gold_types_come_from_silver(silver):
    run_step("03_gold")
    export = pd.read_parquet(paths.EXPORTS_PATH / "F_5500.parquet")
    assert str(export["TOT_PARTCP_BOY_CNT"].dtype) == "float64"
    assert str(export["FORM_YEAR"].dtype) == "int32"
