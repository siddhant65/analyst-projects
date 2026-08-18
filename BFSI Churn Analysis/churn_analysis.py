import pandas as pd
import numpy as np
import matplotlib
from pathlib import Path
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import warnings
warnings.filterwarnings('ignore')

# Load dataset
print("Loading data...")
DATA_URL = "https://raw.githubusercontent.com/sharmaroshan/Churn-Modelling-Dataset/master/Churn_Modelling.csv"
OUTPUT_PATH = Path(__file__).with_name("churn_dashboard.png")
try:
    df = pd.read_csv(DATA_URL)
    print(f"Loaded {len(df):,} rows")
except Exception as error:
    print(f"Download failed ({error})")
    print("Download failed — generating sample data")
    np.random.seed(42)
    n = 1000
    df = pd.DataFrame({
        'CustomerId': range(1, n+1),
        'Surname': ['Customer'] * n,
        'CreditScore': np.random.randint(350, 850, n),
        'Geography': np.random.choice(['France', 'Germany', 'Spain'], n),
        'Gender': np.random.choice(['Male', 'Female'], n),
        'Age': np.random.randint(18, 70, n),
        'Tenure': np.random.randint(0, 10, n),
        'Balance': np.random.uniform(0, 200000, n),
        'NumOfProducts': np.random.randint(1, 4, n),
        'HasCrCard': np.random.randint(0, 2, n),
        'IsActiveMember': np.random.randint(0, 2, n),
        'EstimatedSalary': np.random.uniform(10000, 200000, n),
        'Exited': np.random.choice([0, 1], n, p=[0.8, 0.2])
    })

# Basic stats
print(f"\nTotal customers   : {len(df):,}")
print(f"Churned           : {df['Exited'].sum():,} ({df['Exited'].mean()*100:.1f}%)")
print(f"Retained          : {(df['Exited']==0).sum():,}")

# Churn by geography
print("\nChurn rate by country:")
geo = df.groupby('Geography')['Exited'].mean().sort_values(ascending=False)
for k, v in geo.items():
    print(f"  {k:<10}: {v*100:.1f}%")

# Churn by gender
print("\nChurn rate by gender:")
for k, v in df.groupby('Gender')['Exited'].mean().items():
    print(f"  {k:<10}: {v*100:.1f}%")

# Churn by active status
active = df.groupby('IsActiveMember')['Exited'].mean()
print(f"\nActive members    : {active[1]*100:.1f}% churn")
print(f"Inactive members  : {active[0]*100:.1f}% churn")

# Churn by age group
df['AgeGroup'] = pd.cut(df['Age'], bins=[0,30,40,50,60,100],
                         labels=['<30','30-40','40-50','50-60','60+'])
print("\nChurn by age group:")
for k, v in df.groupby('AgeGroup', observed=True)['Exited'].mean().items():
    print(f"  {k:<8}: {v*100:.1f}%")

# Train a simple decision tree to identify key churn drivers
features = ['CreditScore','Age','Tenure','Balance','NumOfProducts',
            'HasCrCard','IsActiveMember','EstimatedSalary']
df['geo_num'] = df['Geography'].map({'France':0,'Germany':1,'Spain':2})
df['gender_num'] = df['Gender'].map({'Male':0,'Female':1})
all_features = features + ['geo_num','gender_num']

X = df[all_features].fillna(0)
y = df['Exited']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeClassifier(max_depth=5, random_state=42)
model.fit(X_train, y_train)
print(f"\nModel accuracy: {model.score(X_test, y_test)*100:.1f}%")

importance = pd.Series(model.feature_importances_, index=all_features).sort_values(ascending=False)
print("\nTop churn predictors:")
for feat, imp in importance.head(5).items():
    print(f"  {feat:<25}: {imp*100:.1f}%")

# Charts
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Bank Customer Churn Analysis', fontsize=15, fontweight='bold')

geo.plot(kind='bar', ax=axes[0,0], color=['#1F4E79','#2E75B6','#9DC3E6'])
axes[0,0].set_title('Churn Rate by Country')
axes[0,0].set_ylabel('Churn Rate')
axes[0,0].set_xticklabels(axes[0,0].get_xticklabels(), rotation=0)

df[df['Exited']==1]['Age'].hist(ax=axes[0,1], alpha=0.7, label='Churned', color='red', bins=20)
df[df['Exited']==0]['Age'].hist(ax=axes[0,1], alpha=0.7, label='Retained', color='#1F4E79', bins=20)
axes[0,1].set_title('Age Distribution — Churned vs Retained')
axes[0,1].legend()

importance.head(6).plot(kind='barh', ax=axes[1,0], color='#1F4E79')
axes[1,0].set_title('Top Churn Predictors')

df.groupby('NumOfProducts')['Exited'].mean().plot(
    kind='bar', ax=axes[1,1], color='#2E75B6')
axes[1,1].set_title('Churn Rate by Number of Products')
axes[1,1].set_xticklabels(axes[1,1].get_xticklabels(), rotation=0)

plt.tight_layout()
# plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches='tight')
# print(f"\nSaved: {OUTPUT_PATH}")
plt.show()
