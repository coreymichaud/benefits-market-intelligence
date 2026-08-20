# Analyzing Form 5500 Data

Description WIP

---

## Overview

We created a decision-ready analytics solution that evaluates historical Form 5500 data to identify insurance broker trends and insights.

## Key Business Questions Addressed

1. WIP

## Key Insights

WIP

### Insight description

- WIP

---

## Recommendations

WIP

---

## Data Model & Technologies

WIP

---

## Code

WIP

### Prerequisites

It is assumed that you have:

- Python v3.14
- `uv` installed

### Setup

Clone the repository and change directories:

```
git clone REPO
cd REPO
```

### Running pipeline on Apple OS

Run the ELT data pipeline:

```
make all
```

### Running pipeline on Windows

Run the pipeline in order:

```
uv sync
uv run src/innovation_summit/elt/01_bronze.py
uv run src/innovation_summit/elt/02_silver.py
uv run src/innovation_summit/elt/03_gold.py
```