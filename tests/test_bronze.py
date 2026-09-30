import duckdb
import pytest
import requests
from conftest import YEARS, FakeResponse, run_step, zip_bytes

from benefits_market_intelligence.config import paths

DATASETS = ["F_5500", "F_SCH_A", "F_SCH_C_PART1_ITEM2"]


def bronze_tables() -> dict[str, int]:
    with duckdb.connect(paths.DB_PATH) as con:
        names = [
            r[0]
            for r in con.execute(
                "select table_name from information_schema.tables where table_schema = 'bronze'"
            ).fetchall()
        ]
        return {
            n: con.execute(f'select count(*) from bronze."{n}"').fetchone()[0]
            for n in names
        }


def test_downloads_every_dataset_and_year(bronze, dol_site):
    expected = {
        f"https://askebsa.dol.gov/FOIA%20Files/{year}/Latest/{name}_{year}_Latest.zip"
        for name in DATASETS
        for year in YEARS
    }
    assert set(dol_site) == expected
    assert len(dol_site) == 18


def test_loads_one_bronze_table_per_file(bronze):
    tables = bronze_tables()
    assert set(tables) == {
        f"{name}_{year}_Latest" for name in DATASETS for year in YEARS
    }
    assert set(tables.values()) == {2}


def test_bronze_keeps_every_value_as_text(bronze):
    with duckdb.connect(paths.DB_PATH) as con:
        types = {
            r[1]
            for r in con.execute('describe bronze."F_SCH_A_2024_Latest"').fetchall()
        }
    assert types == {"VARCHAR"}


def test_extracts_files_and_deletes_the_zips(bronze):
    folder = paths.RAW_DATA_PATH / "Form 5500 Schedule A" / "F_SCH_A_2019_Latest"
    assert (folder / "f_sch_a_2019_latest.csv").exists()
    assert (folder / "F_SCH_A_2019_layout.txt").exists()
    assert not list(paths.RAW_DATA_PATH.rglob("*.zip"))


def serve(monkeypatch, content: bytes, status: int = 200) -> None:
    monkeypatch.setattr(
        requests, "get", lambda url, *a, **k: FakeResponse(content, status)
    )


def test_zip_without_a_csv_stops_the_run(project, monkeypatch):
    serve(monkeypatch, zip_bytes({"layout.txt": "layout"}))
    with pytest.raises(FileNotFoundError, match="No CSV found"):
        run_step("01_bronze")


def test_zip_with_two_csvs_stops_the_run(project, monkeypatch):
    serve(monkeypatch, zip_bytes({"a.csv": "ACK_ID\n1\n", "b.csv": "ACK_ID\n2\n"}))
    with pytest.raises(ValueError, match="Multiple CSV files"):
        run_step("01_bronze")


def test_http_errors_are_not_swallowed(project, monkeypatch):
    serve(monkeypatch, b"", status=404)
    with pytest.raises(requests.HTTPError):
        run_step("01_bronze")
