# Payment Processing Performance Dashboard

SQL-based analysis of payment transaction data to track processing KPIs and identify failure patterns.

## Overview
Generates synthetic payment data, loads it into an in-memory SQLite database,
and runs SQL queries to compute success rates, processing times, and failure breakdowns by type and region.

## Dataset
Synthetic — generated within the script (5,000 payment records).

**Columns:** payment_id, date, payment_type, status, amount, processing_time_mins, client_id, region

**Payment types:** RETAIL_LOCKBOX, WHOLESALE_LOCKBOX, ACH, WIRE_TRANSFER

**Statuses:** SUCCESS, FAILED, PENDING, REVERSED

## Files
```
02_Payment_Performance_Dashboard/
├── payment_dashboard.py   # Main script
├── README.md              # This file
├── data/                  # Put any local data files here
└── payment_dashboard.png  # Output chart (generated on run)
```

## Setup
```bash
pip install pandas numpy matplotlib
```

## Run
```bash
python payment_dashboard.py
```

## Output
- Console: SQL query results and KPI summary
- `payment_dashboard.png`: 4-panel dashboard saved in this folder
