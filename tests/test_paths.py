from pathlib import Path

import benefits_market_intelligence
from benefits_market_intelligence.config import paths


def test_project_root_is_the_repository():
    package = Path(benefits_market_intelligence.__file__).resolve().parent
    assert paths.PROJECT_ROOT == package.parents[1]
    assert (paths.PROJECT_ROOT / "pyproject.toml").exists()


def test_data_paths_sit_under_data():
    assert paths.RAW_DATA_PATH == paths.DATA_PATH / "raw"
    assert paths.DB_PATH == paths.PROCESSED_PATH / "form_5500.duckdb"
    assert paths.EXPORTS_PATH == paths.DATA_PATH / "exports"


def test_figure_paths_sit_under_figures():
    assert paths.EDA_PATH == paths.FIGURES_PATH / "eda"
    assert paths.ANALYSIS_PATH == paths.FIGURES_PATH / "analysis"
