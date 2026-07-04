from fastapi import FastAPI, HTTPException
from models import BudgetRequest, BudgetResponse
import joblib
import pandas as pd
import os

app = FastAPI(title="Budget Predictor API (India)", version="1.0.0")

model = None
model_name = "Unknown"

@app.on_event("startup")
def load_model():
    global model, model_name
    model_path = "budget_model.pkl"
    name_path = "model_name.pkl"
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        if os.path.exists(name_path):
            model_name = joblib.load(name_path)
        print(f"Loaded model: {model_name}")
    else:
        print("Warning: budget_model.pkl not found. Run train_model.py first.")

@app.post("/predict", response_model=BudgetResponse)
def predict_budget(request: BudgetRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please train the model first.")
    
    # Convert request to DataFrame for the pipeline
    input_df = pd.DataFrame([{
        "destination": request.destination,
        "month": request.month,
        "duration_days": request.duration_days,
        "group_size": request.group_size,
        "pace": request.pace
    }])
    
    try:
        # Predict total budget
        total_pred = model.predict(input_df)[0]
        # Calculate daily budget
        daily_pred = total_pred / request.duration_days
        
        return BudgetResponse(
            estimated_daily_budget_inr=round(float(daily_pred), 2),
            estimated_total_budget_inr=round(float(total_pred), 2),
            model_used=model_name
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
