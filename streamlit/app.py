"""Broker Market Intelligence: entrypoint and navigation.

Run from the repository root so `.streamlit/config.toml` is picked up (Community Cloud does the same):

    streamlit run streamlit/app.py
"""

import streamlit as st

from figures.data import load
from figures.layout import header

st.set_page_config(
    page_title="Broker Market Intelligence",
    page_icon=":material/insights:",
    layout="wide",
)

# Page scripts live in views/, not pages/: a folder named pages/ next to the entrypoint switches on
# Streamlit's legacy auto-navigation, which breaks deep links like /brokers on a fresh server.
PAGES = [
    st.Page(
        "views/market.py", title="Market", icon=":material/payments:", default=True
    ),
    st.Page("views/brokers.py", title="Brokers", icon=":material/leaderboard:"),
    st.Page(
        "views/opportunity.py", title="Opportunity", icon=":material/travel_explore:"
    ),
]

# Title and one-line summary shown in each page's header, next to the global filters
COPY = {
    "Market": (
        "How is broker pay changing?",
        "Commissions and carrier-paid fees on employer health and welfare plans, from Form 5500 filings.",
    ),
    "Brokers": (
        "Which brokers are gaining ground?",
        "22 national brokers and consultants, tracked by the large employer plans that name them.",
    ),
    "Opportunity": (
        "Where is the market moving?",
        "Where broker pay is growing fastest, and how employers are changing what they buy.",
    ),
}

page = st.navigation(PAGES, position="top")
load()  # read the parquet files once per server process, with a loading message on first visit
header(*COPY[page.title])
page.run()
