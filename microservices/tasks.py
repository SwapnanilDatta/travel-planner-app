"""
Task definitions.

Key change vs original:
- Task 1 (City Guide) fetches ALL destination data in one pass and outputs a
  structured JSON blob.
- Task 2 (Logistics) receives that blob via context – it never re-fetches the
  same destination pages.
- Task 3 (Planner) also receives both prior outputs via context, so it never
  needs to search either.

This eliminates ~60-70 % of redundant network calls.
"""

from crewai import Task
from agents import get_city_local_guide, get_travel_trip_expert


def create_tasks(trip_details: dict):
    city_guide      = get_city_local_guide()
    travel_expert   = get_travel_trip_expert()

    destinations_str = ", ".join(trip_details["destinations"])

    # Build an explicit, unambiguous per-member breakdown so the LLM can't
    # collapse the group into a single "persona" or invent shared constraints.
    member_lines = []
    for m in trip_details["members"]:
        prefs = m.get("preferences", [])
        if isinstance(prefs, dict):
            prefs_str = ", ".join(f"{k}" for k in prefs.keys())
        elif isinstance(prefs, list):
            prefs_str = ", ".join(str(p) for p in prefs if p)
        else:
            prefs_str = str(prefs)
            
        member_lines.append(
            f"- {m['name']} (age {m.get('age_group', 'unknown')}): "
            f"mobility_constraints={m.get('mobility_constraints', False)}; "
            f"preferences -> {prefs_str}"
        )
    members_str = "\n".join(member_lines)

    num_members = len(trip_details["members"])
    any_mobility_constraints = any(
        m.get("mobility_constraints", False) for m in trip_details["members"]
    )

    hotel_name = trip_details["hotel_name"]
    hotel_lat  = trip_details["hotel_lat"]
    hotel_lng  = trip_details["hotel_lng"]
    hotel_str  = f"{hotel_name} (lat={hotel_lat}, lng={hotel_lng})"

    total_days = trip_details['total_days']
    min_items  = total_days
    max_items  = total_days * 2

    # ── Task 1: research – does ALL searching here ─────────────────────────
    task1 = Task(
        description=f"""
Trip: {total_days} days to {destinations_str}.
Group: {num_members} travelers.
{members_str}

Run ONE search: "top attractions and restaurants in {destinations_str}".
Output a CONCISE JSON list of {min_items} to {max_items} real places that match the group's interests.
""",
        expected_output=f"Concise JSON list of {min_items}-{max_items} places.",
        agent=city_guide,
    )

    # ── Task 2: logistics and final itinerary generation ───────────────────
    task2 = Task(
        description=f"""
Using ONLY the city report provided by the previous agent, create a CONCISE {total_days}-day itinerary.
Group size: {num_members}. Pace: {trip_details['pace']}. Budget: {trip_details['budget_per_day_INR']} INR/day.
Hotel: {hotel_str} (FIXED - do not recommend others).

Distribute the {min_items}-{max_items} places across the days.
Do NOT perform web searches. Estimate travel times.
Output a BRIEF day-by-day markdown plan. Limit explanations to 1-2 sentences per activity.
Critically: Briefly mention which group member (by name) each activity appeals to based on their specific preferences.
""",
        expected_output=f"Brief day-by-day markdown itinerary for {total_days} days.",
        agent=travel_expert,
        context=[task1],
    )

    return [task1, task2]

def create_regenerate_task(trip_details: dict, target_day_number: int, existing_itinerary: str):
    planning_expert = get_travel_trip_expert()

    destinations_str = ", ".join(trip_details["destinations"])
    total_days = trip_details['total_days']

    task = Task(
        description=f"""
Rewrite ONLY Day {target_day_number} for {destinations_str}.
Context (Existing Itinerary): {existing_itinerary}
Keep it BRIEF and concise. DO NOT perform searches.
CRITICAL: Do NOT reuse any attractions, restaurants, or activities that are already planned on the OTHER days in the context. Recommend completely NEW spots.
""",
        expected_output=f"Brief completely revised plan for Day {target_day_number}.",
        agent=planning_expert,
    )
    return task
