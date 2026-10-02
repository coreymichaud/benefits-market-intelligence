"""The Chart every builder returns, plus the headline and axis helpers they share."""

from dataclasses import dataclass

import numpy as np
import plotly.graph_objects as go


@dataclass
class Chart:
    headline: str
    caption: str
    figure: go.Figure


# Friendlier names when a line of coverage sits mid-sentence
LINE_NAMES = {
    "Multi-line bundle": "multi-line bundles",
    "Voluntary & other": "voluntary benefits",
    "Life & AD&D": "life & AD&D",
    "Stop-loss": "stop-loss",
}


def line_name(line: str) -> str:
    return LINE_NAMES.get(line, line.lower())


def moved(pct: float, only: bool = False) -> str:
    """'grew 41%', 'grew only 17%', 'fell 5%', 'held flat' for headlines."""
    if abs(pct) < 0.5:
        return "held flat"
    if pct > 0:
        return f"grew {'only ' if only else ''}{pct:.0f}%"
    return f"fell {abs(pct):.0f}%"


def fit(*candidates: str, limit: int) -> str:
    """First headline that fits on one line of its panel (candidates go from richest to shortest)."""
    for text in candidates:
        if len(text) <= limit:
            return text
    return candidates[-1]


def nice_step(span: float, target_ticks: int = 4) -> float:
    raw = span / target_ticks
    magnitude = 10 ** np.floor(np.log10(raw))
    for m in [1, 2, 2.5, 5, 10]:
        if m * magnitude >= raw:
            return m * magnitude
    return 10 * magnitude


def unit(value: float) -> tuple[float, str]:
    return (1e9, "B") if value >= 1e9 else (1e6, "M") if value >= 1e6 else (1e3, "K")
