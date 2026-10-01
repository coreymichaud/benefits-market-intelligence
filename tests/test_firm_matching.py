"""Firm name matching: the dashboard and the analysis notebook must agree, and known names
from the filings must land on the right firm (or on none)."""

import ast
import sys
from pathlib import Path

import duckdb
import nbformat
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "streamlit"))

from figures.data import BROKER_FIRMS, _firm_case  # noqa: E402

# Real provider names from Schedule C, with the firm each should count toward
CASES = {
    "WILLIS TOWERS WATSON US LLC": "WTW",
    "WILLISTOWERSWATSON": "WTW",
    "TOWERS WATSON INVESTMENT SERVICES": None,
    "MERCER HEALTH & BENEFITS LLC": "Mercer",
    "MERCER INVESTMENTS LLC": None,
    "CORPORATION OF MERCER UNIVERSITY": None,
    "AON CONSULTING, INC.": "Aon",
    "AONHEWITT ASSOCIATES": "Aon",
    "AON INVESTMENTS USA INC.": None,
    "ARTHUR J. GALLAGHER & CO.": "Gallagher",
    "GALLAGHER BENEFIT SERVICES, INC.": "Gallagher",
    "MCGREGOR & ASSOCIATES, A GALLAGHER": "Gallagher",
    "GALLAGHER FIDUCIARY ADVISORS, LLC": None,
    "FUSCO GALLAGHER PORCARO MONRO LLP": None,
    "WILLKIE FARR & GALLAGHER LLP": None,
    "JOHN M. GALLAGHER": None,
    "ACRISURE LLC DBA BRITTON-GALLAGHER": "Acrisure",
    "MARSH & MCLENNAN AGENCY LLC": "Marsh McLennan Agency",
    "FOX EVERETT A DIVISION OF HUB INTER": "HUB International",
    "USI": "USI",
    "FINDLEY A DIV OF USI CONSULTING GRP": "USI",
    "ONE DIGITAL": "OneDigital",
    "DIGITAL INSURANCE LLC": "OneDigital",
    "ONEDIGITAL INVESTMENT ADVISORS LLC": None,
    "THE SEGAL COMPANY": "Segal",
    "SEGAL MARCO ADVISORS": None,
    "SEGALL BRYANT & HAMILL": None,
    "ALERA GROUP, INC.": "Alera",
    "SALERA EMPLOYEE BENEFITS SOLUTIONS": None,
    "CALERA CAPITAL PARTNERS V": None,
    "EDGEWOOD PARTNERS INSURANCE CENTER": "EPIC",
    "WEDGEWOOD PARTNERS INC": None,
    "IMA FINANCIAL GROUP": "IMA",
    "CBIZ BENEFITS & INSURANCE SERVICES": "CBIZ",
    "CBIZ CPAS P.C.": None,
}


def notebook_firms() -> dict:
    """Read BROKER_FIRMS out of the analysis notebook without running it."""
    nb = nbformat.read(ROOT / "notebooks" / "analysis.ipynb", as_version=4)
    for cell in nb.cells:
        if cell.cell_type == "code" and "BROKER_FIRMS = {" in cell.source:
            for node in ast.parse(cell.source).body:
                if (
                    isinstance(node, ast.Assign)
                    and node.targets[0].id == "BROKER_FIRMS"
                ):
                    return ast.literal_eval(node.value)
    raise AssertionError("BROKER_FIRMS not found in notebooks/analysis.ipynb")


def test_notebook_and_dashboard_use_the_same_patterns():
    assert notebook_firms() == BROKER_FIRMS


@pytest.mark.parametrize("name, firm", CASES.items())
def test_known_names(name, firm):
    matched = duckdb.execute(
        f"SELECT {_firm_case()} FROM (SELECT ? AS provider)", [name]
    ).fetchone()[0]
    assert matched == firm