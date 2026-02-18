# Maple Return

Canadian rental property investment analyzer for cross-border landlords.

## What It Does

Maple Return helps Canadian citizens (including those living in the US) model the financial performance of Canadian rental properties. It handles the nuances that generic tools miss: semi-annual compounding mortgages with 5-year renewal cycles, CAD/USD conversion, and Canadian-specific tax and operating assumptions.

Enter your property details through a guided wizard, and the app produces a full investment analysis — year-by-year cashflow projections, mortgage amortization schedules, exit strategy modeling, and key return metrics like IRR, ROI, and cap rate.

## Features

- **Canadian mortgage engine** — semi-annual compounding, 5-year term renewals over a 25-year amortization
- **Operating model** — rent and expense escalation with vacancy and maintenance reserves
- **FX conversion** — CAD to USD projections for cross-border investors
- **Exit strategy modeling** — sell vs. hold analysis with appreciation and disposition costs
- **Return metrics** — IRR, total ROI, cash-on-cash return, cap rate
- **5-step wizard** — guided input with HTMX auto-save so you never lose progress
- **Results dashboard** — summary metrics, P&L table, and amortization schedule

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy (async), SQLite
- **Frontend:** Jinja2, HTMX, vanilla CSS
- **Language:** Python 3.12
- **Task runner:** [just](https://github.com/casey/just)

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Install & Run

```bash
# Clone the repo
git clone https://github.com/<your-username>/maple-return.git
cd maple-return

# Install dependencies
just install

# Start the dev server
just run
```

Open [http://127.0.0.1:8001](http://127.0.0.1:8001) in your browser.

## Testing

```bash
just test    # run pytest suite
just lint    # run ruff linter
```

## Project Structure

```
maple_return/
├── main.py              # FastAPI app entry point
├── routes.py            # Route handlers
├── models.py            # Pydantic models
├── db_models.py         # SQLAlchemy ORM models
├── database.py          # Async DB setup
├── mortgage.py          # Canadian mortgage engine
├── mortgage_summary.py  # Mortgage summary calculations
├── operating.py         # Operating model (rent, expenses)
├── cashflow.py          # Year-by-year cashflow projections
├── exit_model.py        # Exit strategy modeling
├── metrics.py           # IRR, ROI, cap rate calculations
├── analysis.py          # Orchestrates full analysis
├── templates/           # Jinja2 templates (wizard, results, partials)
└── static/              # CSS
tests/                   # pytest test suite
```

## Built with GSD

The `.planning/` directory contains the full planning artifacts from [claude-gsd](https://github.com/anthropics/claude-gsd), showing the structured development process used to build this project.
