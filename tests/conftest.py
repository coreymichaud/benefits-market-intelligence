"""Shared fixtures: a throwaway project folder and fake DOL downloads.

The pipeline scripts read their paths from benefits_market_intelligence.config.paths when
they run, so pointing those at tmp_path keeps every test away from the real data folder.
"""

import csv
import io
import re
import runpy
import zipfile

import pytest
import requests

from benefits_market_intelligence.config import paths

YEARS = range(2019, 2025)

# Columns in each fake CSV. They cover everything 03_gold.py selects plus a few extras, so
# silver's numeric, date, text and missing-column branches all run.
COLUMNS = {
    "F_5500": [
        "ACK_ID", "DATE_RECEIVED", "AMENDED_IND", "SPONS_DFE_EIN", "SPONS_DFE_PN",
        "SPONSOR_DFE_NAME", "SPONS_DFE_MAIL_US_CITY",
        "SPONS_DFE_MAIL_US_ADDRESS1", "SPONS_DFE_MAIL_US_STATE", "FORM_PLAN_YEAR_BEGIN_DATE",
        "SHORT_PLAN_YR_IND", "TOT_PARTCP_BOY_CNT",
        "TOT_ACTIVE_PARTCP_CNT", "BUSINESS_CODE", "TYPE_PLAN_ENTITY_CD",
        "TYPE_PENSION_BNFT_CODE", "TYPE_WELFARE_BNFT_CODE", "SCH_R_ATTACHED_IND",
        "SCH_MB_ATTACHED_IND", "SCH_SB_ATTACHED_IND", "SCH_H_ATTACHED_IND", "SCH_I_ATTACHED_IND",
        "SCH_A_ATTACHED_IND", "SCH_C_ATTACHED_IND", "SCH_D_ATTACHED_IND", "SCH_G_ATTACHED_IND",
        "SCH_DCG_ATTACHED_IND", "SCH_MEP_ATTACHED_IND", "PLAN_NAME",
    ],
    "F_SCH_A": [
        "ACK_ID", "FORM_ID", "INS_CARRIER_NAME", "INS_CARRIER_EIN", "INS_CARRIER_NAIC_CODE",
        "WLFR_BNFT_HEALTH_IND", "WLFR_BNFT_DENTAL_IND",
        "WLFR_BNFT_VISION_IND", "WLFR_BNFT_LIFE_INSUR_IND", "WLFR_BNFT_TEMP_DISAB_IND",
        "WLFR_BNFT_UNEMP_IND", "WLFR_BNFT_DRUG_IND", "WLFR_BNFT_STOP_LOSS_IND",
        "WLFR_BNFT_HMO_IND", "WLFR_BNFT_PPO_IND", "WLFR_BNFT_INDEMNITY_IND",
        "WLFR_BNFT_OTHER_IND", "WLFR_REFUND_CASH_IND", "WLFR_REFUND_CREDIT_IND",
        "INS_FAIL_PROVIDE_INFO_IND", "PENSION_PREM_PAID_TOT_AMT", "PENSION_UNPAID_PREMIUM_AMT",
        "WLFR_PREMIUM_RCVD_AMT", "WLFR_UNPAID_DUE_AMT", "WLFR_TOT_EARNED_PREM_AMT",
        "INS_BROKER_COMM_TOT_AMT", "INS_BROKER_FEES_TOT_AMT", "INS_PRSN_COVERED_EOY_CNT",
        "WLFR_TOT_CHARGES_PAID_AMT", "WLFR_BNFT_LONG_TERM_DISAB_IND", "INS_POLICY_FROM_DATE",
        "INS_POLICY_TO_DATE", "SCH_A_PLAN_YEAR_BEGIN_DATE", "SCH_A_PLAN_YEAR_END_DATE",
    ],
    "F_SCH_C_PART1_ITEM2": [
        "ACK_ID", "ROW_ORDER", "PROVIDER_OTHER_NAME", "PROVIDER_OTHER_EIN",
        "PROVIDER_OTHER_SRVC_CODES", "PROVIDER_OTHER_RELATION", "PROVIDER_OTHER_DIRECT_COMP_AMT",
        "PROV_OTHER_INDIRECT_COMP_IND", "PROV_OTHER_TOT_IND_COMP_AMT",
    ],
}  # fmt: skip

# DOL added these Form 5500 fields partway through the period; leaving them out of the first
# two years mimics that
LATE_COLUMNS = {"SCH_DCG_ATTACHED_IND", "SCH_MEP_ATTACHED_IND"}

SAMPLE_VALUES = {
    "FORM_PLAN_YEAR_BEGIN_DATE": "{year}-01-01",
    "INS_POLICY_FROM_DATE": "{year}-07-01",
    "INS_POLICY_TO_DATE": "{year}-12-31",  # a six-month policy year
    "SCH_A_PLAN_YEAR_BEGIN_DATE": "{year}-01-01",
    "SCH_A_PLAN_YEAR_END_DATE": "{year}-12-31",
    "DATE_RECEIVED": "{year}-09-15",
    "TOT_PARTCP_BOY_CNT": "150",
    "TOT_ACTIVE_PARTCP_CNT": "140",
    "FORM_ID": "1",
    "ROW_ORDER": "1",
    "INS_BROKER_COMM_TOT_AMT": "1250.50",
    "INS_BROKER_FEES_TOT_AMT": "not a number",  # silver's TRY_CAST should turn this into NULL
    "INS_PRSN_COVERED_EOY_CNT": "75",
    "SPONS_DFE_MAIL_US_STATE": "TX",
}


def columns_for(dataset: str, year: int) -> list[str]:
    columns = COLUMNS[dataset]
    return [c for c in columns if year >= 2021 or c not in LATE_COLUMNS]


def csv_text(dataset: str, year: int, rows: int = 2) -> str:
    columns = columns_for(dataset, year)
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(columns)
    for i in range(rows):
        writer.writerow(
            [
                f"{year}0915{i:04d}"
                if c == "ACK_ID"
                else SAMPLE_VALUES.get(c, "1").format(year=year)
                for c in columns
            ]
        )
    return out.getvalue()


def zip_bytes(files: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return buffer.getvalue()


class FakeResponse:
    def __init__(self, content: bytes, status: int = 200):
        self.content = content
        self.status = status

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise requests.HTTPError(f"{self.status} error")


def dol_zip(url: str) -> bytes:
    """What the DOL site would return for a dataset URL: one CSV plus a layout file."""
    dataset, year = re.search(r"/(F_[A-Z0-9_]+?)_(\d{4})_Latest\.zip$", url).groups()
    year = int(year)
    return zip_bytes(
        {
            f"{dataset.lower()}_{year}_latest.csv": csv_text(dataset, year),
            f"{dataset}_{year}_layout.txt": "layout",
        }
    )


@pytest.fixture
def project(tmp_path, monkeypatch):
    """Point every pipeline path at a temporary folder."""
    processed = tmp_path / "data" / "processed"
    monkeypatch.setattr(paths, "RAW_DATA_PATH", tmp_path / "data" / "raw")
    monkeypatch.setattr(paths, "PROCESSED_PATH", processed)
    monkeypatch.setattr(paths, "DB_PATH", processed / "form_5500.duckdb")
    monkeypatch.setattr(paths, "EXPORTS_PATH", tmp_path / "data" / "exports")
    return tmp_path


@pytest.fixture
def dol_site(monkeypatch):
    """Replace requests.get with a fake DOL site. Returns the list of URLs requested."""
    requested = []

    def fake_get(url, *args, **kwargs):
        requested.append(url)
        return FakeResponse(dol_zip(url))

    monkeypatch.setattr(requests, "get", fake_get)
    return requested


def run_step(step: str) -> dict:
    """Run one pipeline script the way `make` does (python -m) and return its globals."""
    return runpy.run_module(
        f"benefits_market_intelligence.elt.{step}", run_name="__main__"
    )


@pytest.fixture
def bronze(project, dol_site):
    run_step("01_bronze")
    return project


@pytest.fixture
def silver(bronze):
    return run_step("02_silver")
