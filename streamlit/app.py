"""Benefits Market Intelligence dashboard.

    uv run streamlit run streamlit/app.py

Streamlit reads .streamlit/config.toml from this file's folder, so it can be launched from
anywhere.
"""

import streamlit as st

from figures.data import load
from figures.layout import freshness, header

st.set_page_config(
    page_title="Benefits Market Intelligence",
    page_icon=":material/person:",
    layout="wide",
)

# Pages live in views/ rather than pages/: a pages/ folder next to the entrypoint turns on
# Streamlit's legacy navigation, which breaks direct links such as /brokers.
PAGES = [
    st.Page(
        "views/market.py", title="Market", icon=":material/payments:", default=True
    ),
    st.Page("views/brokers.py", title="Brokers", icon=":material/leaderboard:"),
    st.Page(
        "views/opportunity.py", title="Opportunity", icon=":material/travel_explore:"
    ),
    st.Page("views/accounts.py", title="Accounts", icon=":material/table_view:"),
]

# Page links go in the header row; Streamlit adds padding when they sit in its top bar
page = st.navigation(PAGES, position="hidden")
tables = load()
# Accounts lists each plan's latest filing, so the year range doesn't apply there
header(PAGES, show_years=page.title != "Accounts")
#freshness(tables.latest_received)
page.run()
