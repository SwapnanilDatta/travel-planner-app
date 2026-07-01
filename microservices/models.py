from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class Member(BaseModel):
    name: str
    age_group: str
    mobility_constraints: bool
    preferences: List[str]

class TripRequest(BaseModel):
    destinations: List[str]
    total_days: int
    group_size: int
    pace: str
    budget_per_day_INR: str
    budget_type: str
    use_llm: bool = False
    hotel_name: str
    hotel_lat: float
    hotel_lng: float
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
    travel_plan: TravelPlanOutput

class RegenerateDayRequest(BaseModel):
    trip_details: TripRequest
    target_day_number: int
    existing_itinerary: str
