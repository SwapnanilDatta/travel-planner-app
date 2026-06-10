import os
import json
from groq import Groq
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

# Placeholder for Groq client
client = None
if os.getenv("GROQ_API_KEY"):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def enhance_itinerary_with_groq(itinerary: dict, group_prefs: dict, destinations: list, total_days: int) -> dict:
    if not client:
        return itinerary

    # Determine empty days and their corresponding cities
    day_to_city = {}
    if destinations and len(destinations) > 0:
        days_per_city = max(1, total_days // len(destinations))
        for d in range(total_days):
            city_idx = min(d // days_per_city, len(destinations) - 1)
            day_to_city[f"Day {d+1}"] = destinations[city_idx]

    search_context = {}
    with DDGS() as ddgs:
        for day_str, places in itinerary.items():
            if len(places) == 0:
                city = day_to_city.get(day_str, "India")
                query = f"top places to visit in {city} tourism spots"
                print(f"[{day_str} is empty] Searching Web for: {query}")
                
                results = []
                try:
                    for r in ddgs.text(query, max_results=5):
                        results.append({
                            "title": r.get("title"),
                            "snippet": r.get("body"),
                            "url": r.get("href")
                        })
                except Exception as e:
                    print(f"Web search failed for {city}: {e}")
                    
                search_context[day_str] = {
                    "city": city,
                    "web_results": results
                }

    prompt = f"""
    Given the following initial itinerary schedule:
    {json.dumps(itinerary, indent=2)}
    
    And the following group preferences:
    {json.dumps(group_prefs, indent=2)}
    
    Notice that some days are completely empty due to a lack of data in our database. 
    I have performed a web search for those empty days. Here are the search results:
    {json.dumps(search_context, indent=2)}
    
    Create a complete narrative-rich {total_days}-day itinerary.
    1. Keep all the existing places for the non-empty days (you can add reasons/tips for them).
    2. For the empty days, use the provided `web_results` to fill in 3-4 appropriate tourist spots that match the group's preferences.
    3. Include a URL for the new places if available in the search results.
    4. Return ONLY valid JSON in this exact structure:
    {{
        "Day 1": [
            {{
                "name": "...",
                "city": "...",
                "reason": "...",
                "tip": "...",
                "url": "..."
            }}
        ]
    }}
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert travel planner. You always return valid JSON without any markdown formatting blocks like ```json."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=8000
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        # Clean up any potential markdown code blocks if the LLM ignores instructions
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()

        enhanced_json = json.loads(response_text)
        return enhanced_json
    except Exception as e:
        print(f"Failed to enhance itinerary with Groq: {e}")
        return itinerary
