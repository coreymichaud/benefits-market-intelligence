"""Dashboard versions of the analyses in notebooks/analysis.ipynb.

Each function returns a Chart with a headline based on the current filters. The numbers in the
comments match the analysis numbers in the notebook.
"""

from figures.analyses.carriers import carrier_share
from figures.analyses.common import Chart
from figures.analyses.compensation import growth_bridge, market_by_year, pay_pool
from figures.analyses.firms import firm_stats, leaderboard, leaderboard_firms, win_loss
from figures.analyses.geography import state_map
from figures.analyses.industry import industries
from figures.analyses.momentum import momentum_map, momentum_status
from figures.analyses.pay_structure import fee_adoption, take_rate
from figures.analyses.plan_size import self_funding, voluntary

__all__ = [
    "Chart",
    "carrier_share",
    "fee_adoption",
    "firm_stats",
    "growth_bridge",
    "industries",
    "leaderboard",
    "leaderboard_firms",
    "market_by_year",
    "momentum_map",
    "momentum_status",
    "pay_pool",
    "self_funding",
    "state_map",
    "take_rate",
    "voluntary",
    "win_loss",
]
