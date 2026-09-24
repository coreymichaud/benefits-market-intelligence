from plotly.graph_objects import Figure
from pathlib import Path


def save_figure(fig: Figure, name: str, path: Path) -> None:
    """
    Save a Plotly figure as a PNG image.

    Args:
        fig: The Plotly figure to export.
        name: The output filename without the `.png` extension.
        path: The directory path where the image will be saved.

    Returns:
        None
    """
    fig.write_image(path / f"{name}.png", scale=2)
