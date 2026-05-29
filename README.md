# Lead Finder

Lead Finder is a small Python project scaffold for collecting and filtering business leads from CSV files.

## Features

- Load leads from CSV
- Filter by industry, employee count, and country
- Score leads by configurable weighting
- Export ranked leads to CSV

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
lead-finder --input examples/leads.csv --output ranked.csv --industry SaaS --country US
```

## Development

```bash
pytest
```
