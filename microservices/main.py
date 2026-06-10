import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

from models import Base, Place
from scoring import score_places
from scheduler import schedule_itinerary
from llm_enhancer import enhance_itinerary_with_groq

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set in the environment")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(
    title="Group Travel Itinerary Planner API",
    description="Microservice to plan optimal group travel itineraries using OR-Tools.",
    version="1.0.0"
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models for Request
class MemberPreferences(BaseModel):
    name: str
    age_group: str
    mobility_constraints: bool
    preferences: Dict[str, int] # e.g. {"Historical & Heritage": 5, "Nature & Outdoors": 3}

class TripRequest(BaseModel):
    destinations: List[str] # e.g. ["Delhi", "Agra"]
    total_days: int
    group_size: int
    pace: str # Slow, Moderate, Fast
    budget_per_day_INR: str # Under 500, 500-1500, 1500-3000, 3000+
    members: List[MemberPreferences]
    use_llm: bool = False

@app.post("/api/v1/plan-itinerary")
def plan_itinerary(request: TripRequest, db: Session = Depends(get_db)):
    if not request.destinations:
        raise HTTPException(status_code=400, detail="At least one destination is required.")
        
    # 1. Fetch available places for the given destinations
    city_filters = [Place.city.ilike(f"%{dest}%") for dest in request.destinations]
    places = db.query(Place).filter(or_(*city_filters)).all()
    
    if not places:
        raise HTTPException(status_code=404, detail="No places found for the specified destinations.")
        
    # Convert Pydantic members to dicts for our scoring module
    members_dict = [m.model_dump() for m in request.members]
    
    # 2. Score places based on group preferences
    scored_places = score_places(
        places=places,
        members=members_dict,
        group_budget=request.budget_per_day_INR
    )
    
    # Map pace to hours
    pace_hours = 8.0
    if request.pace.lower() == "slow":
        pace_hours = 5.0
    elif request.pace.lower() == "fast":
        pace_hours = 12.0
        
    # Get budget cap as float
    budget_cap = 2000.0
    if "Under" in request.budget_per_day_INR:
        budget_cap = 500.0
    elif "500-1500" in request.budget_per_day_INR:
        budget_cap = 1500.0
    elif "1500-3000" in request.budget_per_day_INR:
        budget_cap = 3000.0
    else:
        budget_cap = 10000.0
        
    # 3. Schedule itinerary using OR-Tools
    schedule_result = schedule_itinerary(
        scored_places=scored_places,
        total_days=request.total_days,
        daily_hours_budget=pace_hours,
        daily_money_budget=budget_cap * request.group_size,  # budget per day could be per group or per person, assuming total here
        destinations=request.destinations
    )
    
    if schedule_result.get("status") != "success":
        raise HTTPException(status_code=400, detail=schedule_result.get("message", "Failed to schedule itinerary."))
        
    final_itinerary = schedule_result["itinerary"]
    
    # 4. (Option C) Enhance with LLM if requested
    if request.use_llm:
        final_itinerary = enhance_itinerary_with_groq(
            final_itinerary, 
            request.model_dump(), 
            request.destinations, 
            request.total_days
        )
        
    return {
        "status": "success",
        "trip_details": {
            "destinations": request.destinations,
            "total_days": request.total_days,
            "group_size": request.group_size
        },
        "itinerary": final_itinerary
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
