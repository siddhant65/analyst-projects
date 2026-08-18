# Sales & Revenue Analytics

Revenue breakdown and margin analysis using SQL and Python on the Superstore sales dataset.

## Overview
Analyses sales transactions by region, category, and customer segment.
Specifically looks at how discount levels affect profit margins.

## Dataset
Superstore dataset — auto-downloaded from GitHub.
Falls back to generated sample data if download fails (~3,000 rows).

**Key columns:** order_date, region, category, segment, sales, profit, discount, quantity

**Calculated:** profit_margin = (profit / sales) * 100

## Files
```
03_Sales_Revenue_Analytics/
├── sales_analytics.py   # Main script
├── README.md            # This file
├── data/                # Put any local data files here
└── sales_dashboard.png  # Output chart (generated on run)
```

## Setup
```bash
pip install pandas numpy matplotlib
```

## Run
```bash
python sales_analytics.py
```

## Output
- Console: SQL analysis results by region, category, segment, and discount tier
- `sales_dashboard.png`: 4-panel dashboard saved in this folder
