.PHONY: help install data-extract data-combine data all

help:  # Shows a help message, and is the default `make` target
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  help             Shows this help message"
	@echo "  install          Syncs the environment"
	@echo "  data-extract     Extracts the data from DOL EFAST"
	@echo "  data-combine     Combines the extracted data"
	@echo "  data             Runs all data commands"
	@echo "  all              Runs the full pipeline"

install:  # Syncs the environment
	uv sync

data-extract:  # Extracts the data from DOL EFAST
	uv run python -m innovation_summit.etl.extract

data-combine: data-extract  # Combines the extracted data into separate parquet files
	uv run python -m innovation_summit.etl.combine

data: data-combine  # Runs all data commands to get the full data pipeline

all: install data  # Runs the full pipeline