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
        prefs_str = ", ".join(f"{k}={v}/10" for k, v in m.get("preferences", {}).items())
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
    min_items  = total_days * 3
    max_items  = total_days * 4

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

CRITICAL — SEARCH STRATEGY: A single generic search will NOT return enough
data for a {total_days}-day trip. You MUST run SEPARATE searches for EACH of
the following categories before writing your final answer (do not skip any):
  1. "top tourist attractions in {destinations_str}"
  2. "best museums and monuments in {destinations_str}"
  3. "best restaurants and cafes in {destinations_str}"
  4. "famous markets and shopping areas in {destinations_str}"
  5. "things to do near {hotel_name}, {destinations_str}"
  6. At least ONE more search tailored to the group's highest-rated
     preference (e.g. "best photography spots in {destinations_str}" if
     photography is a top preference)

CRITICAL: Since this is a {total_days}-day trip, you MUST find and list enough
UNIQUE attractions, restaurants, and activities to fill morning, afternoon, and
evening slots for EVERY day of the trip (roughly {min_items} to {max_items} items).
If after all the searches above you STILL have fewer than {min_items} unique
items, run 1-2 additional searches with different phrasing (e.g. "hidden
gems in {destinations_str}", "best parks and gardens in {destinations_str}")
until you have enough.

CRITICAL:
- Do NOT use generic names like "City Museum", "National Park", "local
  market", or "a wheelchair-accessible restaurant". Use EXACT, real-world,
  verifiable names of places (museums, monuments, restaurants, markets,
  parks, etc.) as found via search.
- Mobility constraints in the group: {any_mobility_constraints}. Only
  factor in accessibility notes if this is True — do NOT invent mobility
  constraints that aren't in the data above.
- The group is ALREADY STAYING at: {hotel_str}. Do NOT research, suggest,
  rate, or mention any other hotels or accommodations. Accommodation is
  fixed and out of scope for this report.
- When relevant, prefer attractions that are reasonably reachable from the
  above hotel location.
- Each numbered search above is a DIFFERENT query — do not repeat the same
  query twice.
- Output a single structured JSON report listing ALL items found (aim for
  {min_items}-{max_items} unique entries total) so the next agents can reuse
  it without any additional searches.
""",
        expected_output=(
            f"A structured JSON report containing for each destination: "
            f"name, a list of AT LEAST {min_items} top attractions/restaurants/"
            f"activities/markets with EXACT real-world names, opening hours, "
            f"entry fees, which group member preference(s) each option serves, "
            f"and notes on accessibility/mobility (only if relevant to this group)."
        ),
        agent=city_guide,
    )

    # ── Task 2: logistics – consumes task1 output, minimal extra searches ──
    task2 = Task(
        description=f"""
Using ONLY the city report provided by the previous agent (do NOT re-search
destinations already covered), analyse logistics for a
{total_days}-day trip.

Group size  : {trip_details['group_size']} ({num_members} members, each with their own preferences)
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
covering all {total_days} days (morning/afternoon/evening each) — do not
discard items as "extra"; if there are more items than slots, group nearby
ones together per day.

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
- This is a group of {num_members} member(s) with individually-set
  preferences (not a solo trip) — make sure the plan reflects a mix that
  serves everyone, not a single averaged "persona".
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
