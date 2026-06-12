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
from agents import get_city_local_guide, get_travel_trip_expert, get_travel_planning_expert


def create_tasks(trip_details: dict):
    city_guide      = get_city_local_guide()
    travel_expert   = get_travel_trip_expert()
    planning_expert = get_travel_planning_expert()

    destinations_str = ", ".join(trip_details["destinations"])
    members_str      = str(trip_details["members"])

    # ── Task 1: research – does ALL searching here ─────────────────────────
    task1 = Task(
        description=f"""
Research actual, specific attractions and activities in {destinations_str}
that match the following group members' preferences and constraints:
{members_str}

CRITICAL:
- Do NOT use generic names like "City Museum" or "National Park".
- Use EXACT, real-world names.
- Search each destination ONCE; do not repeat the same query.
- Output a single structured JSON report so the next agents can reuse it
  without any additional searches.
""",
        expected_output=(
            "A structured JSON report containing for each destination: "
            "name, top attractions (with exact names, opening hours, entry fees), "
            "recommended activities, and notes on accessibility/mobility."
        ),
        agent=city_guide,
    )

    # ── Task 2: logistics – consumes task1 output, minimal extra searches ──
    task2 = Task(
        description=f"""
Using ONLY the city report provided by the previous agent (do NOT re-search
destinations already covered), analyse logistics for a
{trip_details['total_days']}-day trip.

Group size  : {trip_details['group_size']}
Pace        : {trip_details['pace']}
Budget      : {trip_details['budget_per_day_INR']} INR ({trip_details['budget_type']})

You MAY do a targeted search ONLY for transport fares or hotel prices that
are not in the city report. Keep additional searches to a minimum.
""",
        expected_output=(
            "A logistics plan: feasible travel routes between attractions, "
            "daily pacing, transport options with estimated costs in INR, "
            "and accommodation tier recommendations."
        ),
        agent=travel_expert,
        context=[task1],              # receives task1 output – no re-fetching
    )

    # ── Task 3: final planner – pure synthesis, zero searches ─────────────
    task3 = Task(
        description=f"""
Using ONLY the city report and logistics plan from the previous agents,
compile the final {trip_details['total_days']}-day itinerary.

CRITICAL:
- Use ONLY the exact locations already identified – do NOT invent generic
  places (e.g., "City Park", "Local Restaurant").
- Do NOT perform any web searches.
- Make the plan realistic and address all group constraints.
""",
        expected_output=(
            "A comprehensive, day-by-day travel plan with morning/afternoon/"
            "evening slots, exact venue names, travel times, and daily budget "
            "breakdown in INR."
        ),
        agent=planning_expert,
        context=[task1, task2],       # full context – no searches needed
    )

    return [task1, task2, task3]
