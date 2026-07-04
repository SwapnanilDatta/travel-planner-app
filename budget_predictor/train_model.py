import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import matplotlib.pyplot as plt

# 1. Generate Synthetic Data for Indian Travel (in INR)
np.random.seed(42)
num_samples = 15000

destinations = ["Goa", "Kerala", "Rajasthan", "Himachal Pradesh", "Uttarakhand", "Maharashtra", "Delhi", "Agra", "Karnataka", "Tamil Nadu"]
# Base daily costs per person (Moderate pace)
base_costs = {
    "Goa": 4500,
    "Kerala": 4000,
    "Rajasthan": 3500,
    "Himachal Pradesh": 3800,
    "Uttarakhand": 3200,
    "Maharashtra": 4200,
    "Delhi": 3500,
    "Agra": 3000,
    "Karnataka": 3700,
    "Tamil Nadu": 3300
}

months = list(range(1, 13))
# Peak season multipliers
def get_month_multiplier(month, dest):
    if dest in ["Himachal Pradesh", "Uttarakhand"]:
        return 1.4 if month in [5, 6, 12] else 1.0 # Summer and Winter peak
    elif dest in ["Goa", "Kerala", "Rajasthan"]:
        return 1.5 if month in [11, 12, 1] else 1.0 # Winter peak
    return 1.2 if month in [11, 12, 1] else 1.0

paces = ["Budget", "Moderate", "Luxury"]
pace_multipliers = {"Budget": 0.5, "Moderate": 1.0, "Luxury": 3.0}

data = {
    "destination": np.random.choice(destinations, num_samples),
    "month": np.random.choice(months, num_samples),
    "duration_days": np.random.randint(1, 15, num_samples),
    "group_size": np.random.randint(1, 10, num_samples),
    "pace": np.random.choice(paces, num_samples)
}

df = pd.DataFrame(data)

# Calculate Target (Total Cost)
total_costs = []
for idx, row in df.iterrows():
    base = base_costs[row["destination"]]
    month_mult = get_month_multiplier(row["month"], row["destination"])
    pace_mult = pace_multipliers[row["pace"]]
    
    # Economies of scale: bigger groups get a slight per-person discount (e.g. sharing cabs/rooms)
    group_discount = max(0.6, 1.0 - (row["group_size"] - 1) * 0.05)
    
    daily_cost_pp = base * month_mult * pace_mult * group_discount
    
    # Add some random noise (±15%)
    noise = np.random.uniform(0.85, 1.15)
    
    total_cost = daily_cost_pp * row["duration_days"] * row["group_size"] * noise
    total_costs.append(total_cost)

df["total_budget_inr"] = total_costs

# Save data to CSV
df.to_csv("synthetic_travel_data.csv", index=False)
print("Synthetic data saved to synthetic_travel_data.csv")

# 2. Preprocessing
categorical_features = ["destination", "pace"]
numeric_features = ["month", "duration_days", "group_size"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
    ]
)

X = df.drop("total_budget_inr", axis=1)
y = df["total_budget_inr"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Model Testing
models = {
    "Linear Regression": LinearRegression(),
    "Ridge Regression": Ridge(),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
    "XGBoost": XGBRegressor(n_estimators=100, random_state=42, objective='reg:squarederror')
}

best_model = None
best_r2 = -float("inf")
best_name = ""

results_r2 = {}

print("Evaluating Models...")
for name, model in models.items():
    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    results_r2[name] = r2

    print(f"\n{name}:")
    print(f"  MAE:  Rs. {mae:,.2f}")
    print(f"  RMSE: Rs. {rmse:,.2f}")
    print(f"  R2:   {r2:.4f}")
    
    if r2 > best_r2:
        best_r2 = r2
        best_model = pipeline
        best_name = name

print(f"\nBest Model: {best_name} (R2: {best_r2:.4f})")

# Plotting the metrics
plt.figure(figsize=(10, 5))
plt.bar(results_r2.keys(), results_r2.values(), color=['skyblue', 'lightgreen', 'salmon', 'gold', 'plum'])
plt.title('Model Comparison by R2 Score')
plt.ylabel('R2 Score (Higher is better)')
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig('model_metrics.png')
print("Model comparison diagram saved to model_metrics.png")

# 4. Save Best Model
joblib.dump(best_model, "budget_model.pkl")
joblib.dump(best_name, "model_name.pkl")
print("Model saved to budget_model.pkl")
