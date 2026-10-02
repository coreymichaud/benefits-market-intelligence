from plotly.graph_objects import Figure
from pathlib import Path


def save_figure(fig: Figure, name: str, path: Path) -> None:
    """Saves a Plotly figure to path/name.png."""
    fig.write_image(path / f"{name}.png", scale=2)
