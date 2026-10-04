.DEFAULT_GOAL := help
.PHONY: help install data-bronze data-silver data-gold data figures dashboard tests lint typecheck format all


# ============ MISC COMMANDS ============

help:  ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-13s %s\n", $$1, $$2}'


install:  ## Syncs the environment
	uv sync


# ============ DATA COMMANDS ============

data-bronze:  ## Extracts the data from DOL EFAST into bronze schema
	uv run python -m benefits_market_intelligence.elt.01_bronze

data-silver: data-bronze  ## Transforms the bronze data into combined, cleaned silver schema
	uv run python -m benefits_market_intelligence.elt.02_silver

data-gold: data-silver  ## Transforms the silver data into analytics-ready gold schema
	uv run python -m benefits_market_intelligence.elt.03_gold

data: data-gold  ## Runs full data pipeline


# ============ ANALYSIS ============

figures:  ## Re-run the analysis notebook and regenerate every chart
	uv run jupyter nbconvert --to notebook --execute --inplace notebooks/analysis.ipynb

dashboard:  ## Launch the Streamlit dashboard
	uv run streamlit run streamlit/app.py


# ============ QUALITY ============

tests:  ## Run the test suite with coverage (fails under 100%)
	uv run pytest

lint:  ## Check linting and formatting, the same checks CI runs
	uv run ruff check .
	uv run ruff format --check .

typecheck:  ## Type check the code with ty, the same check CI runs
	uv run ty check

format:  ## Fix lint issues and reformat the code
	uv run ruff check --fix .
	uv run ruff format .


# ============ FULL PIPELINE COMMAND ============

all: install data figures dashboard  ## Runs the full analytics pipeline