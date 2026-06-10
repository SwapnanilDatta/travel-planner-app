from ortools.linear_solver import pywraplp
from typing import List, Dict, Any

def schedule_itinerary(
    scored_places: List[dict],
    total_days: int,
    daily_hours_budget: float = 8.0,
    daily_money_budget: float = 2000.0,
    destinations: List[str] = None
) -> Dict[str, Any]:
    """
    Use Google OR-Tools to schedule the best places over `total_days`.
    scored_places is a list of {"place": Place, "score": float}
    """
    # Create the linear solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return {"error": "Solver not found."}

    num_places = len(scored_places)
    
    # x[p][d] = 1 if place p is visited on day d, else 0
    x = {}
    for p in range(num_places):
        for d in range(total_days):
            x[p, d] = solver.IntVar(0, 1, f'x_{p}_{d}')

    # Constraint 1: Each place visited at most once across all days
    for p in range(num_places):
        solver.Add(sum(x[p, d] for d in range(total_days)) <= 1)

    # Calculate day-city mapping simply by dividing days among destinations evenly
    day_to_city = {}
    if destinations and len(destinations) > 0:
        days_per_city = max(1, total_days // len(destinations))
        for d in range(total_days):
            city_idx = min(d // days_per_city, len(destinations) - 1)
            day_to_city[d] = destinations[city_idx].lower()

    # Per-day constraints
    for d in range(total_days):
        # Constraint 2: Daily time budget
        solver.Add(
            sum(
                (scored_places[p]["place"].time_needed_hours or 2.0) * x[p, d]
                for p in range(num_places)
            ) <= daily_hours_budget
        )

        # Constraint 3: Daily money budget
        solver.Add(
            sum(
                (scored_places[p]["place"].entrance_fee_inr or 0.0) * x[p, d]
                for p in range(num_places)
            ) <= daily_money_budget
        )

        # Constraint 4: City-day lock
        if day_to_city:
            target_city = day_to_city[d]
            for p in range(num_places):
                place_city = (scored_places[p]["place"].city or "").lower()
                # If the place is not in the target city for this day, x[p][d] must be 0
                if target_city not in place_city and place_city not in target_city:
                    solver.Add(x[p, d] == 0)

    # Objective: Maximize total score
    objective = solver.Objective()
    for p in range(num_places):
        for d in range(total_days):
            objective.SetCoefficient(x[p, d], scored_places[p]["score"])
    objective.SetMaximization()

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        itinerary = {}
        for d in range(total_days):
            day_places = []
            for p in range(num_places):
                if x[p, d].solution_value() > 0.5:
                    place_data = scored_places[p]["place"]
                    day_places.append({
                        "name": place_data.name,
                        "type": place_data.type,
                        "city": place_data.city,
                        "time_needed_hours": place_data.time_needed_hours,
                        "entrance_fee_inr": place_data.entrance_fee_inr,
                        "google_review_rating": place_data.google_review_rating,
                        "score_calculated": scored_places[p]["score"]
                    })
            itinerary[f"Day {d + 1}"] = day_places
        
        return {
            "status": "success",
            "total_score": objective.Value(),
            "itinerary": itinerary
        }
    else:
        return {"status": "failed", "message": "The problem does not have an optimal solution."}
