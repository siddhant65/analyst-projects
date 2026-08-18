import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import sqlite3
import warnings
warnings.filterwarnings('ignore')

# Load Superstore dataset
print("Loading data...")
url = "https://raw.githubusercontent.com/dsrscientist/dataset1/master/Superstore.csv"
try:
    df = pd.read_csv(url, encoding='latin-1')
    df.columns = [c.strip().lower().replace(' ', '_').replace('-', '_') for c in df.columns]
    print(f"Loaded {len(df):,} rows")
    use_generated = False
except:
    print("Download failed — generating sample data")
    use_generated = True

if use_generated:
    np.random.seed(42)
    n = 3000
    dates = pd.date_range('2022-01-01', '2025-12-31', periods=n)
    df = pd.DataFrame({
        'order_id': [f'ORD{i:05d}' for i in range(1, n+1)],
        'order_date': dates,
        'region': np.random.choice(['East','West','Central','South'], n),
        'category': np.random.choice(['Technology','Furniture','Office Supplies'], n),
        'segment': np.random.choice(['Consumer','Corporate','Home Office'], n),
        'sales': np.round(np.random.uniform(50, 5000, n), 2),
        'profit': np.round(np.random.uniform(-200, 1000, n), 2),
        'discount': np.round(np.random.uniform(0, 0.5, n), 2),
        'quantity': np.random.randint(1, 10, n),
    })

# Standardise column names
if not use_generated:
    for col in df.columns:
        if 'order' in col and 'date' in col:
            df = df.rename(columns={col: 'order_date'})

df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
df = df.dropna(subset=['order_date'])
df['year'] = df['order_date'].dt.year
df['month'] = df['order_date'].dt.month
df['year_month'] = df['order_date'].dt.to_period('M').astype(str)
df['profit_margin'] = (df['profit'] / df['sales'] * 100).round(2)

print(f"Records: {len(df):,} | Date range: {df['order_date'].min().date()} to {df['order_date'].max().date()}\n")

# SQL analysis
conn = sqlite3.connect(':memory:')
df.to_sql('sales', conn, index=False)

print("--- Revenue by Region ---")
q1 = pd.read_sql("""
    SELECT region,
           COUNT(*) as orders,
           ROUND(SUM(sales), 0) as revenue,
           ROUND(SUM(profit), 0) as profit,
           ROUND(AVG(profit_margin), 1) as margin_pct
    FROM sales GROUP BY region ORDER BY revenue DESC
""", conn)
print(q1.to_string(index=False))

print("\n--- Revenue by Category ---")
q2 = pd.read_sql("""
    SELECT category,
           ROUND(SUM(sales), 0) as revenue,
           ROUND(SUM(profit), 0) as profit,
           ROUND(SUM(profit)*100.0/SUM(sales), 1) as margin_pct,
           COUNT(*) as orders
    FROM sales GROUP BY category ORDER BY revenue DESC
""", conn)
print(q2.to_string(index=False))

print("\n--- Revenue by Segment ---")
q3 = pd.read_sql("""
    SELECT segment,
           ROUND(SUM(sales), 0) as revenue,
           ROUND(AVG(sales), 0) as avg_order_value,
           COUNT(*) as orders
    FROM sales GROUP BY segment ORDER BY revenue DESC
""", conn)
print(q3.to_string(index=False))

print("\n--- Discount Impact on Margin ---")
q4 = pd.read_sql("""
    SELECT
        CASE
            WHEN discount = 0 THEN 'No Discount'
            WHEN discount <= 0.2 THEN 'Low (0-20%)'
            WHEN discount <= 0.4 THEN 'Medium (20-40%)'
            ELSE 'High (40%+)'
        END as discount_tier,
        COUNT(*) as orders,
        ROUND(AVG(profit_margin), 1) as avg_margin_pct
    FROM sales
    GROUP BY discount_tier
    ORDER BY avg_margin_pct DESC
""", conn)
print(q4.to_string(index=False))
conn.close()

# Charts
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Sales & Revenue Dashboard', fontsize=15, fontweight='bold')
colors = ['#1F4E79', '#2E75B6', '#9DC3E6', '#D6E4F0']

df.groupby('region')['sales'].sum().sort_values().plot(
    kind='barh', ax=axes[0,0], color='#1F4E79')
axes[0,0].set_title('Revenue by Region')

cat_margin = df.groupby('category')['profit_margin'].mean()
cat_margin.plot(kind='bar', ax=axes[0,1], color=colors[:3])
axes[0,1].set_title('Avg Profit Margin by Category (%)')
axes[0,1].axhline(y=df['profit_margin'].mean(), color='red', linestyle='--', label='Overall avg')
axes[0,1].legend()
axes[0,1].set_xticklabels(axes[0,1].get_xticklabels(), rotation=15)

df.groupby('year_month')['sales'].sum().iloc[-24:].plot(
    kind='line', ax=axes[1,0], color='#1F4E79', linewidth=2, marker='o', markersize=4)
axes[1,0].set_title('Monthly Revenue Trend (Last 24 Months)')
axes[1,0].tick_params(axis='x', rotation=45)

df.groupby('segment')['sales'].sum().plot(
    kind='pie', ax=axes[1,1], autopct='%1.1f%%', colors=colors[:3])
axes[1,1].set_title('Revenue by Segment')
axes[1,1].set_ylabel('')

plt.tight_layout()
plt.savefig('sales_dashboard.png', dpi=150, bbox_inches='tight')
print("\nSaved: sales_dashboard.png")
