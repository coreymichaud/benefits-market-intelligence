"""Checks that docs/data_dictionary matches the pipeline code and the warehouse if it exists."""

import ast
import re
from pathlib import Path

import duckdb
import pytest

from benefits_market_intelligence.config import paths

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "data_dictionary"
ELT = ROOT / "src" / "benefits_market_intelligence" / "elt"

# silver/gold table, bronze prefix, prefix of the column lists in the scripts
TABLES = [
    ("F_5500", "F_5500", "F_5500"),
    ("SCH_A", "F_SCH_A", "SCH_A"),
    ("SCH_C_P1_I2", "F_SCH_C_PART1_ITEM2", "SCH_C_P1_I2"),
]


def script_lists(name: str) -> dict[str, list[str]]:
    """Read the column lists from a pipeline script without running it."""
    tree = ast.parse((ELT / name).read_text())
    return {
        node.targets[0].id: ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List)
    }


SILVER_LISTS = script_lists("02_silver.py")
GOLD_LISTS = script_lists("03_gold.py")


def documented(page: Path, section: str | None = None) -> dict[str, str]:
    """Column name to second cell (type or description) from a dictionary page's table."""
    text = page.read_text()
    if section:
        text = text.split(f"## {section}")[1].split("\n## ")[0]
    rows = re.findall(r"^\| `([A-Z0-9_]+)` \| ([^|]*) \|", text, flags=re.M)
    return {name: value.strip() for name, value in rows}


def expected_type(prefix: str, column: str) -> str:
    if column == "FORM_YEAR":
        return "INTEGER"
    if column in SILVER_LISTS[f"{prefix}_NUMERIC_COLS"]:
        return "DOUBLE"
    if column in SILVER_LISTS[f"{prefix}_DATE_COLS"]:
        return "DATE"
    return "VARCHAR"


@pytest.mark.parametrize("table, bronze, prefix", TABLES)
def test_gold_page_lists_exactly_what_the_gold_script_selects(table, bronze, prefix):
    page = documented(DOCS / "03_gold" / f"{table}.md")
    assert list(page) == GOLD_LISTS[f"{prefix}_top_cols"]


@pytest.mark.parametrize("table, bronze, prefix", TABLES)
def test_silver_and_gold_types_follow_the_silver_cast_lists(table, bronze, prefix):
    for layer in ["02_silver", "03_gold"]:
        page = documented(DOCS / layer / f"{table}.md")
        assert page == {c: expected_type(prefix, c) for c in page}, layer


@pytest.mark.parametrize("table, bronze, prefix", TABLES)
def test_every_cast_column_is_documented(table, bronze, prefix):
    silver = documented(DOCS / "02_silver" / f"{table}.md")
    listed = (
        SILVER_LISTS[f"{prefix}_NUMERIC_COLS"] + SILVER_LISTS[f"{prefix}_DATE_COLS"]
    )
    assert set(listed) <= set(silver)


@pytest.mark.parametrize("table, bronze, prefix", TABLES)
def test_bronze_and_silver_pages_cover_the_same_columns(table, bronze, prefix):
    bronze_cols = set(documented(DOCS / "01_bronze" / f"{bronze}.md", "Columns"))
    silver_cols = set(documented(DOCS / "02_silver" / f"{table}.md"))
    assert bronze_cols == silver_cols - {"FORM_YEAR"}


warehouse = pytest.mark.skipif(
    not paths.DB_PATH.exists(),
    reason="needs data/processed/form_5500.duckdb (run make data)",
)


def describe(schema: str, table: str) -> dict[str, str]:
    with duckdb.connect(paths.DB_PATH, read_only=True) as con:
        return {
            r[0]: r[1] for r in con.execute(f'describe {schema}."{table}"').fetchall()
        }


@warehouse
@pytest.mark.parametrize("table, bronze, prefix", TABLES)
def test_pages_match_the_warehouse(table, bronze, prefix):
    for schema, layer in [("silver", "02_silver"), ("gold", "03_gold")]:
        assert describe(schema, table) == documented(DOCS / layer / f"{table}.md"), (
            schema
        )

    bronze_cols = documented(DOCS / "01_bronze" / f"{bronze}.md", "Columns")
    for year in range(2019, 2025):
        actual = describe("bronze", f"{bronze}_{year}_Latest")
        assert set(actual) <= set(bronze_cols), year
        assert set(actual.values()) == {"VARCHAR"}, year
