.PHONY: help install data-bronze data-silver data all


# ============ MISC COMMANDS ============

help:  # Shows a help message, and is the default `make` target
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  help             Shows this help message"
	@echo "  install          Syncs the environment"
	@echo "  data-bronze      Extracts the data from DOL EFAST into bronze schema"
	@echo "  data-silver      Transforms the bronze data into combined, cleaned silver schema"
	@echo "  data-gold        Transforms the silver data into analytics-ready gold schema"
	@echo "  data             Runs full data pipeline"
	@echo "  all              Runs the full analytics pipeline"

install:  # Syncs the environment
	uv sync


# ============ DATA COMMANDS ============

data-bronze:  # Extracts the data from DOL EFAST into bronze schema
	uv run python -m benefits_market_intelligence.elt.01_bronze

data-silver: data-bronze  # Transforms the bronze data into combined, cleaned silver schema
	uv run python -m benefits_market_intelligence.elt.02_silver

data-gold: data-silver  # Transforms the silver data into analytics-ready gold schema
	uv run python -m benefits_market_intelligence.elt.03_gold

data: data-gold  # Runs full data pipeline


# ============ FULL PIPELINE COMMAND ============

all: install data  # Runs the full analytics pipeline