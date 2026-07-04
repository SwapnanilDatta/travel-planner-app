# Budget Predictor Microservice

This microservice provides intelligent, machine-learning-driven budget estimation for trips across India. Built as a standalone FastAPI application, it uses an XGBoost regressor trained on synthesized, realistic pricing logic.

## Deployment on Hugging Face Spaces

This application is containerized using Docker and is intended to be hosted on Hugging Face Spaces.

1. **Dockerfile:** Configured for Hugging Face (non-root `user` UID 1000, exposed on port `7860`).
2. **`.dockerignore`:** Excludes local virtual environments and heavy datasets from being uploaded to the space.

### API Usage
Send a `POST` request to `/predict` with the following JSON schema:
```json
{
  "destination": "Goa",
  "month": 12,
  "duration_days": 5,
  "group_size": 2,
  "pace": "Moderate"
}
```

## Data Analysis & ML Metrics

Since no historical dataset was readily available, we synthesized a dataset of **15,000 trips** reflecting real-world economic constraints.

### Dataset Logic (`synthetic_travel_data.csv`)
- **Base Costs:** Each destination has a baseline per-person daily cost (e.g., Goa is ₹4,500/day, Agra is ₹3,000/day).
- **Seasonality (Peak Multipliers):** 
  - Hill stations (Himachal, Uttarakhand) experience 1.4x multipliers in Summer/Winter.
  - Beach/Desert states (Goa, Kerala, Rajasthan) experience 1.5x multipliers in Winter.
- **Pace / Travel Style:**
  - Budget = 0.5x multiplier
  - Moderate = 1.0x multiplier
  - Luxury = 3.0x multiplier
- **Economies of Scale:** Larger groups receive slight per-person discounts (simulating shared cabs and twin-sharing hotel rooms). Max discount is capped at 0.6x.
- **Noise:** Random ±15% variance was added to mimic real-world unpredictability.

### Model Evaluation
We trained 5 different regression models to predict the total cost of a trip using this generated dataset. The dataset was preprocessed using `StandardScaler` for numeric features and `OneHotEncoder` for categorical strings (Destination, Pace). 

The target metric used to select the best model was **R² (R-Squared)**, which represents the proportion of the variance in the dependent variable that is predictable from the independent variables (1.0 being perfect accuracy).

| Model | MAE (Mean Absolute Error) | RMSE (Root Mean Sq Error) | R² Score |
| :--- | :--- | :--- | :--- |
| **Linear Regression** | Rs. 69,248.12 | Rs. 96,993.22 | 0.7229 |
| **Ridge Regression** | Rs. 69,243.84 | Rs. 96,992.41 | 0.7229 |
| **Random Forest** | Rs. 17,114.73 | Rs. 32,318.83 | 0.9692 |
| **Gradient Boosting** | Rs. 21,950.72 | Rs. 38,421.80 | 0.9565 |
| **XGBoost (Selected)** | **Rs. 14,263.61** | **Rs. 24,604.02** | **0.9822** |

XGBoost was automatically serialized using `joblib` into `budget_model.pkl` due to achieving the highest accuracy.
