# Benefits Market Intelligence

Every year, employer-sponsored benefit plans disclose who insures them, who gets paid to place and service those plans, and how much changes hands, all through the Department of Labor's **Form 5500** filings. That data is public, but it's scattered across millions of rows, multiple schedules, and inconsistent formats, which makes it impractical for a broker, carrier, or analyst to use as-is.

This project builds an end-to-end pipeline that turns raw Form 5500 filings (2019–2024) into an analytics-ready dataset, then mines it for **broker leaderboards, carrier market share, compensation trends, and plan-level economics**, the kind of market intelligence benefits brokers and consultants would otherwise pay a data vendor for.

**What this project demonstrates:**
- Designing and building a **Medallion (bronze/silver/gold)** ELT pipeline on top of a local analytical warehouse
- Working with large, messy, real-world government data (multi-year, multi-schedule, self-reported)
- Translating raw filings into business-relevant questions about market share, compensation, and trends
- Producing reproducible, notebook-driven exploratory analysis backed by a documented data model

---

## Key Business Questions Addressed

> 🚧 **Work in progress — check back soon.**

1. WIP

---

## Key Insights

> 🚧 **Work in progress — check back soon.**

WIP

### Insight Description

- WIP

---

## Recommendations

> 🚧 **Work in progress — check back soon.**

WIP

---

## Data Model & Technologies

### Data

The analysis is built on three components of the **DOL Form 5500 filing package:** the Main form, Schedule A (insurance/commission detail), and Schedule C Part I Item 2 (service provider compensation). This covers **plan years 2019–2024**. See [`docs/about-the-data.md`](docs/about-the-data.md) for a full breakdown of what each form captures and how they relate.

### Pipeline

Raw filings are loaded into a **DuckDB** warehouse and progressively refined using a **Medallion architecture**:

| Layer | Contents | Purpose |
|---|---|---|
| **Bronze** | Raw extracted CSVs, one table per source file | Unmodified system of record |
| **Silver** | Six years combined per form, typed and standardized | Clean, query-ready history |
| **Gold** | Trimmed to analysis-relevant columns | Fast, analytics-ready tables |

Full details on each transformation are documented in [`docs/data-transformations.md`](docs/data-transformations.md), and column-level definitions live in [`docs/data_dictionary/`](docs/data_dictionary).

### Stack

| Tool | Role |
|---|---|
| **DuckDB** | Analytical warehouse for the bronze/silver/gold pipeline |
| **pandas / PyArrow** | Data wrangling and columnar I/O |
| **Plotly + Kaleido** | Chart generation and static export (see [`/figures`](figures)) |
| **Jupyter Notebooks** | Exploratory data analysis per form/schedule |
| **uv** | Python environment and dependency management |

### Repository Structure

```
benefits-market-intelligence/
├── docs/                     # Data documentation (source, transformations, data dictionary)
├── figures/                  # Exported charts supporting the analysis
├── notebooks/                # Exploratory data analysis, one notebook per form/schedule
├── src/benefits_market_intelligence/
│   ├── config/               # Paths and shared configuration
│   └── elt/                  # Bronze → silver → gold pipeline scripts
├── Makefile                  # Pipeline entry points (macOS/Linux)
└── pyproject.toml            # Dependencies and project metadata
```

---

## Code

### Prerequisites

- Python 3.14
- [`uv`](https://docs.astral.sh/uv/) installed

### Setup

Clone the repository and change directories:

```bash
git clone https://github.com/coreymichaud/benefits-market-intelligence.git
cd benefits-market-intelligence
```

### Running the Pipeline (macOS/Linux)

```bash
make all
```

This syncs the environment and runs the full bronze → silver → gold pipeline. Run `make help` to see all available targets.

### Running the Pipeline (Windows)

```bash
uv sync
uv run src/benefits_market_intelligence/elt/01_bronze.py
uv run src/benefits_market_intelligence/elt/02_silver.py
uv run src/benefits_market_intelligence/elt/03_gold.py
```

---

## License

This project is licensed under the [MIT License](LICENSE).