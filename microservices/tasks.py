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
    min_items  = total_days * 2
    max_items  = total_days * 3

    # ── Task 1: research – does ALL searching here ─────────────────────────
    task1 = Task(
        description=f"""
This is a {total_days}-day GROUP trip to {destinations_str} with {num_members} traveler(s).
Each member has set THEIR OWN preferences independently — do not merge them
into one "persona" or assume they all want the same thing. Here is the
group's exact, verbatim data (do not alter or reinterpret it):

{members_str}

Research actual, specific attractions and activities that, TOGETHER, cover
the range of interests above (e.g. if one member rates "photography" high
and another rates "history" high, include options for both).

CRITICAL — SEARCH STRATEGY: You MUST run SEPARATE searches for EACH of
the following categories before writing your final answer (do not skip any):
  1. "top attractions in {destinations_str}"
  2. "best restaurants in {destinations_str}"
  3. "things to do near {hotel_name}, {destinations_str}"

CRITICAL:
- Keep the output extremely CONCISE to save tokens. Do not write long paragraphs.
- Output a single structured JSON report listing AT LEAST {min_items} items found.
""",
        expected_output=(
            f"A concise JSON report listing AT LEAST {min_items} items with real names, "
            f"member preference mapping, and mobility notes (if relevant)."
        ),
        agent=city_guide,
    )

    # ── Task 2: logistics – consumes task1 output, minimal extra searches ──
    task2 = Task(
        description=f"""
Using ONLY the city report provided by the previous agent (do NOT re-search
destinations already covered), analyse logistics for a
{total_days}-day trip.

Group size  : {trip_details['group_size']} ({num_members} members)
Group Details:
{members_str}

Pace        : {trip_details['pace']}
Budget      : {trip_details['budget_per_day_INR']} INR ({trip_details['budget_type']})

The group is ALREADY STAYING at: {hotel_str}. This is FIXED — do NOT
research, suggest, compare, or recommend any hotels or accommodation tiers.
Use this hotel's location only as the start/end point for daily routing and
travel-time/cost estimates.

Make sure the route grouping accounts for the fact that different members
prioritize different things (e.g. don't drop a high-priority option for one
member just because it doesn't suit another — instead, sequence/pair
activities so everyone's top interests are covered across the trip).

You MUST organize ALL items from the city report into a day-by-day grouping
covering all {total_days} days. Be concise to save tokens.

You MAY do a targeted search ONLY for transport fares or hotel-to-attraction
travel times that are not in the city report. Keep additional searches to a
minimum.
""",
        expected_output=(
            "A logistics plan: feasible travel routes between attractions "
            "(starting/ending each day at the given hotel), daily pacing, and "
            "transport options with estimated costs in INR, organized "
            f"day-by-day for all {total_days} days. Do NOT include any "
            "hotel or accommodation recommendations."
        ),
        agent=travel_expert,
        context=[task1],              # receives task1 output – no re-fetching
    )

    # ── Task 3: final planner – pure synthesis, zero searches ─────────────
    task3 = Task(
        description=f"""
Using ONLY the city report and logistics plan from the previous agents,
compile the final {total_days}-day itinerary.

CRITICAL:
- Use ONLY the exact locations already identified – do NOT invent generic
  places (e.g., "City Park", "Local Restaurant", "local market", "Local
  Bazaars", "local park", or any place name containing the word "local").
- The city report contains roughly {min_items}-{max_items} unique items —
  that is enough for {total_days} days at 3 slots/day. Do NOT recommend the
  same place twice on consecutive days or multiple times in the itinerary.
  Distribute the unique attractions across the days without repetition.
  Only use "Free Time" as an absolute last resort if you have truly
  exhausted every unique item from the city report — check the full list
  again before doing so.
- Do NOT perform any web searches.
- Do NOT invent constraints (e.g. mobility issues) that aren't explicitly
  in the group's data. Mobility constraints in this group: {any_mobility_constraints}.
- This is a group of {num_members} member(s). Here are their specific details and preferences:
{members_str}
- You MUST explicitly mention the members by NAME in the daily itinerary. For example, explain how an activity specifically caters to John's high rating for History, while the next activity caters to Sarah's love for Food. Do NOT write a generic solo itinerary!
- If preferences strongly diverge, you can suggest that the group temporarily splits up for an afternoon (e.g., "While John visits the Museum, Sarah can explore the Shopping district").
- Make the plan realistic and address all group constraints.
- The group's accommodation is FIXED at {hotel_str}. Do NOT mention, name,
  suggest, or recommend any other hotel/accommodation. You may reference
  "the hotel" or "{hotel_name}" only as a start/end point for the day.
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

def create_regenerate_task(trip_details: dict, target_day_number: int, existing_itinerary: str):
    planning_expert = get_travel_planning_expert()

    destinations_str = ", ".join(trip_details["destinations"])
    total_days = trip_details['total_days']

    task = Task(
        description=f"""
You are given an existing {total_days}-day group trip itinerary to {destinations_str}.
Your task is to REWRITE ONLY Day {target_day_number} of this itinerary.

Existing Itinerary Context (Do NOT change other days):
{existing_itinerary}

CRITICAL INSTRUCTIONS:
- You must rewrite Day {target_day_number} to provide alternative attractions and activities that fit the same destination and group constraints.
- Do NOT repeat any attractions or activities that are already planned on the OTHER days.
- Ensure the pacing and logistics still make sense.
- Keep the output format exactly as a Day block (e.g. "### Day {target_day_number}: ...").
- ONLY output the content for Day {target_day_number}. Do not output the rest of the itinerary.
""",
        expected_output=(
            f"A completely revised plan for Day {target_day_number} with morning/afternoon/evening slots."
        ),
        agent=planning_expert,
    )
    return task
