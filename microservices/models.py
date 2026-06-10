from sqlalchemy import Column, Integer, String, Float, Boolean, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    zone = Column(String, nullable=True)
    state = Column(String, nullable=True)
    city = Column(String, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True)
    establishment_year = Column(String, nullable=True)
    time_needed_hours = Column(Float, nullable=True)
    google_review_rating = Column(Float, nullable=True)
    entrance_fee_inr = Column(Float, nullable=True)
    airport_with_50km_radius = Column(String, nullable=True)
    weekly_off = Column(String, nullable=True)
    significance = Column(String, nullable=True)
    dslr_allowed = Column(String, nullable=True)
    number_of_google_reviews_in_lakhs = Column(Float, nullable=True)
    best_time_to_visit = Column(String, nullable=True)
    
    # Derivable fields not in original CSV
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
