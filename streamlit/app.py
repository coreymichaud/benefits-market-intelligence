"""Benefits Market Intelligence dashboard.

Run from the repository root so `.streamlit/config.toml` is picked up:

    streamlit run streamlit/app.py
"""

import streamlit as st

from figures.data import load
from figures.layout import header

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
]

# Page links go in the header row; Streamlit adds padding when they sit in its top bar
page = st.navigation(PAGES, position="hidden")
load()
header(PAGES)
page.run()
