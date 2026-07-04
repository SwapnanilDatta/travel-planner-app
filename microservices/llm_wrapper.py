import os

from dotenv import load_dotenv

load_dotenv()

def _build_member_string(trip_details: dict) -> str:
    member_lines = []
    for m in trip_details.get("members", []):
        prefs = m.get("preferences", [])
        if isinstance(prefs, dict):
            prefs_str = ", ".join(f"{k}" for k in prefs.keys())
        elif isinstance(prefs, list):
            prefs_str = ", ".join(str(p) for p in prefs if p)
        else:
            prefs_str = str(prefs)
            
        member_lines.append(
            f"- Member Name: {m.get('name', 'Unknown')} (Age: {m.get('age_group', 'unknown')}) | "
            f"Mobility Constraints: {m.get('mobility_constraints', False)} | "
            f"This member's personal preferences: {prefs_str}"
        )
    return "\n".join(member_lines) if member_lines else "No specific members."


import httpx
import re
import asyncio

async def _call_llm(prompt: str, retries: int = 3) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here")
    headers = {
        "Content-Type": "application/json"
    }
   
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 3000
        }
    }
    
    async with httpx.AsyncClient() as client:
        for attempt in range(retries):
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=120.0
                )
                
                if response.status_code == 429:
                    print(f"Rate limited on attempt {attempt+1}. Sleeping for 15 seconds...")
                    await asyncio.sleep(15)
                    continue
                    
                if response.status_code != 200:
                    print(f"LLM Error {response.status_code}: {response.text}")
                    return f"Error from Gemini API: {response.text}"
                    
                data = response.json()
                
                try:
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    return "Error: Unexpected response format from Gemini API."
                
                print("================ RAW LLM OUTPUT ================")
                print(content)
                print("================================================")
                
                # Failsafe: Strip any remaining conversational/reasoning text before the first "### Day"
                if '### Day' in content:
                    content = '### Day' + content.split('### Day', 1)[1]
                else:
                    print("WARNING: LLM did not output any '### Day' headings. Retrying...")
                    if attempt < retries - 1:
                        await asyncio.sleep(5)
                        continue
                    else:
                        return "Error: LLM failed to generate the required headings."
                
                return content.strip()
            except Exception as e:
                print(f"HTTPX Error: {e}")
                if attempt == retries - 1:
                    return f"Error making LLM call: {e}"
                await asyncio.sleep(5)
        
        return "Error: Exceeded max retries for LLM call."


async def generate_full_itinerary(trip_details: dict) -> str:
    destinations = trip_details.get("destinations", [])
    total_days = trip_details.get("total_days", 3)
    
    members_str = _build_member_string(trip_details)
    
    hotel_name = trip_details.get("hotel_name", "Unknown Hotel")
    hotel_lat  = trip_details.get("hotel_lat", 0.0)
    hotel_lng  = trip_details.get("hotel_lng", 0.0)
    hotel_str  = f"{hotel_name} (lat={hotel_lat}, lng={hotel_lng})"
    
    # Chunking logic (generate in chunks of 3 days to avoid token cutoffs)
    chunk_size = 3
    final_itinerary = []
    
    for start_day in range(1, total_days + 1, chunk_size):
        end_day = min(start_day + chunk_size - 1, total_days)
        
        # If we already generated previous days, pass them as context to avoid repetition
        previous_days_context = ""
        if final_itinerary:
            previous_text = "\n".join(final_itinerary)
            previous_days_context = f"""
PREVIOUSLY PLANNED DAYS (DO NOT REPEAT ANY ATTRACTIONS OR RESTAURANTS FROM HERE):
{previous_text}
"""
        
        prompt = f"""
You are an expert travel planner. Create a highly detailed, geographically clustered itinerary for Days {start_day} to {end_day} of a {total_days}-day trip to {", ".join(destinations)}.

Group Details:
{len(trip_details.get('members', []))} travelers.
{members_str}
Pace: {trip_details.get('pace', 'Medium')}
Hotel: {hotel_str} (Initial hotel. You may suggest up to 2 hotel changes if it reduces travel time significantly.)

{previous_days_context}

CRITICAL RULES:
1. Cluster attractions geographically to minimize inefficient routing and travel time.
2. Every day MUST include a full schedule starting from the morning and ending with the night stay.
3. Every single group member's preferences MUST be explicitly represented in every single day.
4. DO NOT repeat places that have already been visited.
5. NEVER use the phrase "Day 1", "Day 2", etc. ANYWHERE in your text EXCEPT in the required headings. The parser will break if you use the word Day followed by a number in normal descriptions.
6. Skip all reasoning and thinking. Output the final itinerary immediately.

OUTPUT FORMAT INSTRUCTIONS:
CRITICAL: You must output ONLY valid Markdown. DO NOT use tables. DO NOT output any introductory text or conclusions.
Use an unordered list (bullet points starting with an asterisk `*`) for every activity.
Follow this EXACT format template for each day (replace <Day Number> with the actual digit, e.g. 1, 2, 3):

### Day <Day Number>: [Theme or Location]
* **[Time] - [Activity Name]** ([Duration]): [1-2 sentences of description]. *Appeals to: [Member Name]*
* **[Time] - [Activity Name]** ([Duration]): [1-2 sentences of description]. *Appeals to: [Member Name]*
"""
        
        chunk_result = await _call_llm(prompt)
        final_itinerary.append(chunk_result.strip())
        
    return "\n\n".join(final_itinerary)


async def regenerate_single_day(trip_details: dict, target_day: int, existing_itinerary: str) -> str:
    members_str = _build_member_string(trip_details)
    destinations = trip_details.get("destinations", [])
    
    prompt = f"""
You are an expert travel planner. Rewrite ONLY Day {target_day} for a trip to {", ".join(destinations)}.

Group Details:
{len(trip_details.get('members', []))} travelers.
{members_str}

Context (Existing Itinerary):
{existing_itinerary}

CRITICAL RULES:
1. Keep it BRIEF and concise.
2. Do NOT reuse any attractions, restaurants, or activities that are already planned on the OTHER days in the context. Recommend completely NEW spots.
3. Ensure the day includes a full schedule from morning to night stay.
4. Preserve continuity with the previous and next days (e.g. start from the hotel you ended at on the previous day).
5. NEVER use the phrase "Day 1", "Day 2", etc. ANYWHERE in your text EXCEPT in the required headings.
6. Skip all reasoning and thinking. Output the final itinerary immediately.

OUTPUT FORMAT INSTRUCTIONS:
CRITICAL: You must output ONLY valid Markdown. DO NOT use tables. DO NOT output any introductory text.
Use an unordered list (bullet points starting with an asterisk `*`) for every activity.
Follow this EXACT format template:

### Day {target_day}: [Theme or Location]
* **[Time] - [Activity Name]** ([Duration]): [1-2 sentences of description]. *Appeals to: [Member Name]*
"""
    return await _call_llm(prompt)
