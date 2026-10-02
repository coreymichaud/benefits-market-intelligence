"""Smoke tests: every dashboard page renders against the committed exports without an error.

The dashboard is not part of the coverage target; these only catch pages that break.
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "streamlit" / "app.py"


def run(page: str, **state) -> AppTest:
    at = AppTest.from_file(str(APP), default_timeout=180)
    at.switch_page(f"views/{page}.py")
    for key, value in state.items():
        at.session_state[key] = value
    at.run()
    assert not at.exception, at.exception[0].value
    return at


@pytest.mark.parametrize("page", ["market", "brokers", "opportunity"])
def test_chart_pages_render(page):
    assert run(page).subheader, "page rendered no chart headlines"


@pytest.mark.parametrize(
    "view", ["Growth by line", "Take rate", "Fee adoption", "Carriers"]
)
def test_market_views_render(view):
    run("market", market_view=view, exclude_blank=True)


def test_accounts_page_lists_plans():
    at = run("accounts")
    assert len(at.dataframe[0].value) > 0


def test_filters_narrow_every_page():
    for page in ["market", "brokers", "opportunity", "accounts"]:
        run(page, state="TX", industry="Manufacturing")