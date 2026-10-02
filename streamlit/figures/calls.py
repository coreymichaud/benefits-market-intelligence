"""The call and confidence level behind each recommendation in the README.

Calls are judgments about the full market from 2019 to 2024, so the badges only show when no
filter is applied. The rubric is in docs/assumptions.md (Confidence Ratings).
"""

from dataclasses import dataclass

import streamlit as st

from figures.data import Filters

CALL_COLORS = {"Go": "green", "No-go": "red", "Monitor": "orange"}
CONFIDENCE_COLORS = {"High": "green", "Medium": "blue", "Low": "gray"}


@dataclass(frozen=True)
class Call:
    verdict: str  # Go, No-go or Monitor
    subject: str  # what the call is about, shown on the badge
    confidence: str  # High, Medium or Low
    reason: str


CALLS = {
    "bundles": Call(
        "Go",
        "lead with bundles",
        "High",
        "Lead with multi-line bundles and ancillary lines. Bundle pay and take rate rose in "
        "every year, and the trend holds whether blank pay amounts are read as zero or left out.",
    ),
    "medical": Call(
        "No-go",
        "medical as a growth engine",
        "High",
        "Don't count on medical commissions for growth. Medical pay grew 14% against 41% for "
        "the market, and its take rate and fee adoption stayed flat.",
    ),
    "voluntary": Call(
        "Go",
        "voluntary under 1,000 participants",
        "Medium",
        "Build voluntary benefits for plans under 1,000 participants. Adoption rose in every "
        "size band, but voluntary is inferred from the other and indemnity benefit flags.",
    ),
    "self_funding": Call(
        "Go",
        "self-funding advice, 100-499",
        "Medium",
        "Bring self-funding advice to plans with 100 to 499 participants. The 100-249 share "
        "rose every year, but self-funding is read from a missing insured medical contract.",
    ),
    "markets": Call(
        "Go",
        "fastest-growing markets",
        "High",
        "Point sales capacity at the fastest-growing states and industries. Arizona, Texas, "
        "Michigan, Illinois, Florida and Virginia still beat the national rate with their five "
        "fastest-growing plans taken out.",
    ),
    "consolidators": Call(
        "Monitor",
        "consolidators",
        "Medium",
        "Track consolidators picking up local brokers' clients. The trend is consistent, but "
        "Schedule C covers only a thin slice of large plans.",
    ),
}


def show(key: str, f: Filters) -> None:
    """Badges for a recommendation, shown only on the unfiltered view the call is based on."""
    if f != Filters():
        return
    call = CALLS[key]
    with st.container(horizontal=True, gap="small"):
        st.badge(
            f"{call.verdict}: {call.subject}",
            color=CALL_COLORS[call.verdict],
            help=call.reason,
        )
        st.badge(
            f"{call.confidence} confidence",
            color=CONFIDENCE_COLORS[call.confidence],
            help="How the rating is set: docs/assumptions.md, Confidence Ratings.",
        )