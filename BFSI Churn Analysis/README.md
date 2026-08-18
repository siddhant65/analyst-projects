# Bank Customer Churn Analysis

Exploratory analysis and prediction of customer churn using the Bank Customer Churn dataset.

## Overview
Analysed customer data to identify churn patterns and built a simple classification model
to predict which customers are likely to leave.

## Dataset
Bank Customer Churn dataset (~10,000 rows) — auto-downloaded from GitHub.
Falls back to generated sample data if download fails.

**Features used:** CreditScore, Geography, Gender, Age, Tenure, Balance,
NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary

**Target:** Exited (1 = churned, 0 = retained)

## Files
```
01_BFSI_Churn_Analysis/
├── churn_analysis.py   # Main analysis script
├── README.md           # This file
├── data/               # Put any local data files here
└── churn_dashboard.png # Output chart (generated on run)
```

## Setup
```bash
pip install pandas numpy matplotlib scikit-learn
```

## Run
```bash
python churn_analysis.py
```

## Output
- Console: churn rates by segment, model accuracy, feature importance
- `churn_dashboard.png`: 4-panel chart saved in this folder
