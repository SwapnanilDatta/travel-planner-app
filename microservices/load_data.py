import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base, Place

# Load environment variables
load_dotenv()

# Get DB URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment.")

# Create engine and tables
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def load_data(csv_path: str):
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    session = SessionLocal()
    
    # Check if data already exists to avoid duplication
    if session.query(Place).first() is not None:
        print("Data already exists in the database. Skipping load.")
        session.close()
        return

    places_to_insert = []
    for _, row in df.iterrows():
        # Handle "time needed to visit in hrs" string parsing
        time_needed = row.get("time needed to visit in hrs")
        if isinstance(time_needed, str):
            # Sometimes it might be '1.5-2.0', we can take the max or just float it
            try:
                time_needed = float(time_needed.split('-')[0])
            except:
                time_needed = None
        else:
            time_needed = safe_float(time_needed)

        place = Place(
            zone=str(row.get("Zone")),
            state=str(row.get("State")),
            city=str(row.get("City")),
            name=str(row.get("Name")),
            type=str(row.get("Type")),
            establishment_year=str(row.get("Establishment Year")),
            time_needed_hours=time_needed,
            google_review_rating=safe_float(row.get("Google review rating")),
            entrance_fee_inr=safe_float(row.get("Entrance Fee in INR")),
            airport_with_50km_radius=str(row.get("Airport with 50km Radius")),
            weekly_off=str(row.get("Weekly Off")),
            significance=str(row.get("Significance")),
            dslr_allowed=str(row.get("DSLR Allowed")),
            number_of_google_reviews_in_lakhs=safe_float(row.get("Number of google review in lakhs")),
            best_time_to_visit=str(row.get("Best Time to visit"))
        )
        places_to_insert.append(place)
    
    session.add_all(places_to_insert)
    session.commit()
    session.close()
    print(f"Successfully loaded {len(places_to_insert)} places into the database.")

if __name__ == "__main__":
    csv_file = os.path.join(os.path.dirname(__file__), "archive", "Top Indian Places to Visit.csv")
    load_data(csv_file)
