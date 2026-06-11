from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class Member(BaseModel):
    name: str
    age_group: str
    mobility_constraints: bool
    preferences: Dict[str, int]

class TripRequest(BaseModel):
    destinations: List[str]
    total_days: int
    group_size: int
    pace: str
    budget_per_day_INR: str
    budget_type: str
    use_llm: bool = False
    members: List[Member]

# Output schemas for the 2 JSONs
class CityReportOutput(BaseModel):
    destinations: List[str]
    attractions_and_activities: str
    recommendations: str

class TravelPlanOutput(BaseModel):
    overall_plan: str
    daily_itinerary: str

class TripResponse(BaseModel):
    city_report: CityReportOutput
    travel_plan: TravelPlanOutput
