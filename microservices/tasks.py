from crewai import Task
from agents import get_city_local_guide, get_travel_trip_expert, get_travel_planning_expert

def create_tasks(trip_details: dict):
    city_guide = get_city_local_guide()
    travel_expert = get_travel_trip_expert()
    planning_expert = get_travel_planning_expert()

    task1 = Task(
        description=f"""
        Research actual, specific attractions, and activities in {trip_details['destinations']} 
        that match the following group members' preferences and constraints: {trip_details['members']}.
        CRITICAL: Do NOT hallucinate or use generic names like "City Museum" or "National Park". Use EXACT, real-world names of places in {trip_details['destinations']}.
        Ensure you output a comprehensive city report.
        """,
        expected_output="A detailed JSON report of the cities, attractions, and activities tailored to the group.",
        agent=city_guide
    )

    task2 = Task(
        description=f"""
        Based on the city report, analyze the logistics for a {trip_details['total_days']} day trip. 
        The group size is {trip_details['group_size']}. Pace: {trip_details['pace']}. 
        Budget: {trip_details['budget_per_day_INR']} INR {trip_details['budget_type']}.
        """,
        expected_output="A logistics plan outlining feasible travel routes, pacing, and budget estimations.",
        agent=travel_expert
    )

    task3 = Task(
        description=f"""
        Coordinate the city report and logistics plan into a final {trip_details['total_days']}-day itinerary. 
        CRITICAL: Use ONLY the exact locations and details provided by the other agents. DO NOT invent generic places (e.g., "City Park", "Local Restaurant").
        Make sure it's realistic and addresses all constraints.
        """,
        expected_output="A comprehensive day-by-day travel plan.",
        agent=planning_expert
    )

    return [task1, task2, task3]
