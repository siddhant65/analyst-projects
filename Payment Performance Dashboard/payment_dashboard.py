import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import sqlite3
import warnings
warnings.filterwarnings('ignore')

# Generate synthetic payment data
np.random.seed(42)
n = 5000

statuses = np.random.choice(
    ['SUCCESS','FAILED','PENDING','REVERSED'], n, p=[0.82, 0.10, 0.05, 0.03])
payment_types = np.random.choice(
    ['RETAIL_LOCKBOX','WHOLESALE_LOCKBOX','ACH','WIRE_TRANSFER'], n,
    p=[0.40, 0.25, 0.20, 0.15])
dates = pd.date_range('2025-01-01', periods=n, freq='2h')
amounts = np.where(
    payment_types == 'WHOLESALE_LOCKBOX',
    np.random.uniform(10000, 500000, n),
    np.random.uniform(100, 5000, n))
processing_times = np.where(
    statuses == 'SUCCESS',
    np.random.uniform(0.5, 3.0, n),
    np.random.uniform(2.0, 10.0, n))

df = pd.DataFrame({
    'payment_id': [f'PAY{i:06d}' for i in range(1, n+1)],
    'date': dates,
    'payment_type': payment_types,
    'status': statuses,
    'amount': np.round(amounts, 2),
    'processing_time_mins': np.round(processing_times, 2),
    'client_id': np.random.choice([f'CLIENT_{i:03d}' for i in range(1, 51)], n),
    'region': np.random.choice(['NORTHEAST','MIDWEST','SOUTH','WEST'], n)
})
df['month'] = df['date'].dt.to_period('M').astype(str)

print(f"Generated {len(df):,} payment records\n")

# Load into SQLite and run queries
conn = sqlite3.connect(':memory:')
df.to_sql('payments', conn, index=False)

print("--- Status Summary ---")
q1 = pd.read_sql("""
    SELECT status,
           COUNT(*) as count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as pct,
           ROUND(SUM(amount), 2) as total_amount
    FROM payments
    GROUP BY status
    ORDER BY count DESC
""", conn)
print(q1.to_string(index=False))

print("\n--- Performance by Payment Type ---")
q2 = pd.read_sql("""
    SELECT payment_type,
           COUNT(*) as total,
           ROUND(AVG(CASE WHEN status='SUCCESS' THEN 1.0 ELSE 0.0 END)*100, 1) as success_rate,
           ROUND(AVG(amount), 2) as avg_amount,
           ROUND(AVG(processing_time_mins), 2) as avg_processing_mins
    FROM payments
    GROUP BY payment_type
    ORDER BY total DESC
""", conn)
print(q2.to_string(index=False))

print("\n--- Monthly Trend (first 6 months) ---")
q3 = pd.read_sql("""
    SELECT month,
           COUNT(*) as payments,
           ROUND(AVG(CASE WHEN status='SUCCESS' THEN 1.0 ELSE 0.0 END)*100, 1) as success_rate,
           ROUND(SUM(amount)/1000000, 2) as revenue_millions
    FROM payments
    GROUP BY month ORDER BY month
""", conn)
print(q3.head(6).to_string(index=False))

print("\n--- Top Failure Segments ---")
q4 = pd.read_sql("""
    SELECT payment_type, region, COUNT(*) as failures,
           ROUND(AVG(amount), 2) as avg_amount
    FROM payments WHERE status = 'FAILED'
    GROUP BY payment_type, region
    ORDER BY failures DESC LIMIT 8
""", conn)
print(q4.to_string(index=False))
conn.close()

# Dashboard
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Payment Processing Dashboard', fontsize=15, fontweight='bold')
colors = ['#1F4E79', '#2E75B6', '#9DC3E6', '#D6E4F0']

df['status'].value_counts().plot(
    kind='pie', ax=axes[0,0], autopct='%1.1f%%', colors=colors)
axes[0,0].set_title('Payment Status Distribution')

success_rate = (df[df['status']=='SUCCESS'].groupby('payment_type').size() /
                df.groupby('payment_type').size() * 100)
success_rate.plot(kind='barh', ax=axes[0,1], color='#1F4E79')
axes[0,1].set_title('Success Rate by Payment Type (%)')
axes[0,1].axvline(x=82, color='red', linestyle='--', label='Overall avg')
axes[0,1].legend()

df.groupby('month').size().plot(
    kind='line', ax=axes[1,0], color='#1F4E79', linewidth=2, marker='o')
axes[1,0].set_title('Monthly Payment Volume')
axes[1,0].tick_params(axis='x', rotation=45)

df[df['status']=='SUCCESS']['processing_time_mins'].hist(
    ax=axes[1,1], alpha=0.7, label='Success', color='#1F4E79', bins=20)
df[df['status']=='FAILED']['processing_time_mins'].hist(
    ax=axes[1,1], alpha=0.7, label='Failed', color='red', bins=20)
axes[1,1].set_title('Processing Time — Success vs Failed')
axes[1,1].legend()

plt.tight_layout()
plt.savefig('payment_dashboard.png', dpi=150, bbox_inches='tight')
print("\nSaved: payment_dashboard.png")

# Summary KPIs
print(f"""
KPI Summary:
  Total payments    : {len(df):,}
  Success rate      : {(df['status']=='SUCCESS').mean()*100:.1f}%
  Total value       : ${df['amount'].sum():,.0f}
  Failed value      : ${df[df['status']=='FAILED']['amount'].sum():,.0f}
  Avg process time  : {df['processing_time_mins'].mean():.2f} mins
""")
