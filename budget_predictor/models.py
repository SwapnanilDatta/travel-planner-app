from pydantic import BaseModel, Field

class BudgetRequest(BaseModel):
    destination: str = Field(..., description="The city or state in India, e.g., 'Goa', 'Kerala'")
    month: int = Field(..., ge=1, le=12, description="Month of travel (1-12)")
    duration_days: int = Field(..., ge=1, description="Total days of the trip")
    group_size: int = Field(..., ge=1, description="Number of people traveling")
    pace: str = Field(..., description="Pace/Style of the trip: 'Budget', 'Moderate', or 'Luxury'")

class BudgetResponse(BaseModel):
    estimated_daily_budget_inr: float
    estimated_total_budget_inr: float
    model_used: str
