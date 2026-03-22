# Money-Manage

A complete local, offline-first personal finance intelligence system built in Python. All data is stored locally in a SQLite database — no cloud, no tracking, full privacy.

## Features

- **PDF Statement Parsing** — Auto-detects and parses HDFC Regalia, HDFC Swiggy, HDFC Bank, and SBI Bank statements
- **Smart Categorization** — Automatically categorizes transactions (food, travel, shopping, entertainment, etc.) with custom keyword overrides
- **Monthly Summaries** — Aggregated spending breakdowns by category, EMI, and lifestyle
- **Burn Rate & Runway** — Calculate your average monthly burn rate and how long your liquid savings last
- **Financial Simulations** — Model scenarios: new EMI impact, expense reduction, no-income runway
- **Net Worth Tracking** — Track assets and liabilities for net worth calculation
- **Goal Planning** — Set savings goals and check feasibility against current burn rate
- **CSV Export** — Export monthly transactions to CSV for further analysis
- **Duplicate Detection** — Prevents duplicate transactions on re-import

## Project Structure

```
Money-Manage/
├── finance/
│   ├── db/             # SQLite schema and database layer
│   ├── ingestion/      # File upload and management
│   ├── classification/ # Statement type detection
│   ├── parsers/        # PDF parsers (Regalia, Swiggy, Bank)
│   ├── transactions/   # Transaction classification and normalization
│   ├── validation/     # Stated vs computed total validation
│   ├── categorization/ # Keyword-based transaction categorization
│   ├── aggregation/    # Monthly spend aggregation
│   ├── analytics/      # Burn rate, runway, net worth, goal feasibility
│   └── simulation/     # What-if scenario simulations
├── cli/                # Command-line interface (argparse)
├── tests/              # Pytest test suite
├── requirements.txt
└── setup.py
```

## Setup

### Requirements
- Python 3.8+

### Install

```bash
pip install -r requirements.txt
pip install -e .
```

Or install dependencies directly:

```bash
pip install pdfplumber PyMuPDF openpyxl tabulate
```

## CLI Usage

### Upload a Statement

```bash
finance-cli upload /path/to/statement.pdf
```

Copies the file to `uploads/`, auto-detects statement type (HDFC Regalia, HDFC Swiggy, HDFC Bank, SBI Bank).

### Parse Uploaded Statements

```bash
# Parse all uploaded files
finance-cli parse

# Parse a specific file by ID
finance-cli parse --file-id 1
```

Extracts transactions, classifies them (expense/refund/EMI/cashback/payment), and categorizes them.

### View Monthly Summary

```bash
# All months
finance-cli summary

# Specific month
finance-cli summary --month 2024-01
```

### Burn Rate & Runway

```bash
finance-cli runway --liquid 500000
```

Output:
```
Burn Rate:     ₹32000.00/month
Runway:        15.6 months
```

### Financial Simulations

```bash
# Basic simulation with liquid savings
finance-cli simulate --liquid 500000

# With new EMI scenario
finance-cli simulate --liquid 500000 --new-emi CarLoan,15000,60

# With expense reduction scenario
finance-cli simulate --liquid 500000 --reduce-expense 20
```

### Add Asset

```bash
finance-cli add-asset --name "Savings Account" --value 500000
finance-cli add-asset --name "Mutual Funds" --value 200000
```

### Add Liability

```bash
finance-cli add-liability --name "Home Loan" --total 2000000 --frequency monthly --monthly 20000
```

### Add Savings Goal

```bash
finance-cli add-goal --name "Emergency Fund" --target 300000 --months 12
```

### Export Transactions to CSV

```bash
finance-cli export --month 2024-01
finance-cli export --month 2024-01 --output my_jan_2024.csv
```

### List Uploaded Files

```bash
finance-cli list-files
```

### Add Custom Category Mapping

```bash
finance-cli categorize --keyword "bigbasket" --category "groceries"
finance-cli categorize --keyword "apollo" --category "health"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Supported Statement Types

| Type | Description |
|------|-------------|
| `HDFC_CC_REGALIA` | HDFC Regalia Gold Credit Card |
| `HDFC_CC_SWIGGY` | HDFC Swiggy Credit Card |
| `HDFC_BANK` | HDFC Bank Account Statement |
| `SBI_BANK` | SBI Bank Account Statement |

## Default Categories

| Keyword | Category |
|---------|----------|
| swiggy, zomato, dominos | food |
| uber, ola | travel |
| amazon, flipkart | shopping |
| netflix, spotify | entertainment |
| electricity | utilities |
| gym, pharmacy, hospital | health |
| petrol, fuel | fuel |
| atm | cash |

Custom mappings added via `finance-cli categorize` take priority over defaults.

## Data Storage

All data is stored in `finance.db` (SQLite) in the current working directory. The database includes:

- `raw_files` — Uploaded statement metadata
- `transactions` — Parsed and categorized transactions
- `assets` — Asset values for net worth
- `liabilities` — Liabilities with monthly equivalents
- `goals` — Savings goals
- `category_mappings` — Custom keyword→category mappings