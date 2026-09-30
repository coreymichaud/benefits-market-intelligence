"""Smoke test: every dashboard page renders against the committed exports without an error.

The dashboard is not part of the coverage target; this only catches pages that break.
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "streamlit" / "app.py"


@pytest.mark.parametrize("page", ["market", "brokers", "opportunity"])
def test_page_renders(page):
    at = AppTest.from_file(str(APP), default_timeout=180)
    at.switch_page(f"views/{page}.py")
    at.run()
    assert not at.exception, at.exception[0].value
    assert at.subheader, "page rendered no chart headlines"
