from typing import List, Dict, Any
from models import Place

# Map abstract preference tags to dataset 'Type' or 'Significance' keywords
TAG_MAPPING = {
    "Historical & Heritage": ["heritage", "monument", "fort", "tomb", "cave", "historical"],
    "Religious & Spiritual": ["temple", "mosque", "church", "religious", "spiritual", "shrine"],
    "Nature & Outdoors": ["nature", "garden", "wildlife", "lake", "park", "botanical", "waterfall", "beach"],
    "Adventure & Sports": ["adventure", "trekking", "sports"],
    "Food & Local Culture": ["food", "market", "street", "cultural"],
    "Shopping": ["market", "bazaar", "shopping", "mall"],
    "Art & Museums": ["museum", "gallery", "artistic"],
    "Family-friendly": ["family", "amusement park", "theme park", "zoo", "recreational"]
}

def calculate_group_tag_scores(members: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate the average rating for each preference tag across the group.
    members = [{"name": "Ankit", "preferences": {"Historical & Heritage": 5, "Nature & Outdoors": 3, ...}}, ...]
    """
    tag_sums = {}
    tag_counts = {}

    for member in members:
        prefs = member.get("preferences", {})
        for tag, rating in prefs.items():
            tag_sums[tag] = tag_sums.get(tag, 0) + rating
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    group_scores = {}
    for tag in tag_sums:
        if tag_counts[tag] > 0:
            group_scores[tag] = tag_sums[tag] / tag_counts[tag]
    return group_scores

def compute_place_score(place: Place, group_tag_scores: Dict[str, float], budget_cap: float = None, pace: str = "Moderate") -> float:
    """
    Compute score for a specific place based on aggregated group preferences and constraints.
    """
    score = 0.0
    place_type = str(place.type).lower() if place.type else ""
    place_sig = str(place.significance).lower() if place.significance else ""
    
    # 1. Add score based on tag matches
    matched_any = False
    for tag, group_score in group_tag_scores.items():
        keywords = TAG_MAPPING.get(tag, [])
        # Check if place type or significance matches the tag's keywords
        if any(kw in place_type for kw in keywords) or any(kw in place_sig for kw in keywords):
            score += group_score * 2.0  # Weight multiplier
            matched_any = True
            
    # Default small score if no tags matched to avoid 0
    if not matched_any:
        score += 1.0

    # 2. Add bonus for Google rating
    rating = place.google_review_rating or 3.0
    score += rating * 0.2

    # 3. Penalty for entry fee exceeding budget
    fee = place.entrance_fee_inr or 0.0
    if budget_cap and fee > budget_cap:
        score -= (fee - budget_cap) * 0.01  # Small penalty proportional to excess fee

    return score

def get_budget_cap(budget_str: str) -> float:
    # Under 500 / 500-1500 / 1500-3000 / 3000+
    if not budget_str:
        return 1500.0
    if "Under" in budget_str:
        return 500.0
    elif "500-1500" in budget_str:
        return 1500.0
    elif "1500-3000" in budget_str:
        return 3000.0
    else:
        return 5000.0

def score_places(places: List[Place], members: List[Dict[str, Any]], group_budget: str) -> List[dict]:
    group_scores = calculate_group_tag_scores(members)
    budget_cap = get_budget_cap(group_budget)
    
    scored_places = []
    for p in places:
        s = compute_place_score(p, group_scores, budget_cap)
        scored_places.append({
            "place": p,
            "score": s
        })
        
    # Sort by score descending
    scored_places.sort(key=lambda x: x["score"], reverse=True)
    return scored_places
