microservice works, from the moment a request comes in, to the moment the final itinerary is generated:

### 1. The Request Arrives (`main.py`)
When a user submits their JSON payload to the `POST /api/v1/plan-itinerary` endpoint, FastAPI validates the structure (making sure destinations, days, budgets, and member preferences are correctly formatted) using the Pydantic models. 
Once validated, it queries your **Neon PostgreSQL database** to fetch all the tourist places that match the requested cities (e.g., Delhi and Agra).

### 2. Preference Aggregation & Scoring (`scoring.py`)
Now we have a list of places, but we need to know which ones the group will like best.
*   **Aggregation:** It looks at every member's ratings (e.g., Ankit gave "Historical" a 5, Neha gave it a 3) and averages them to create a unified "Group Profile".
*   **Scoring:** It iterates through every single place fetched from the DB and assigns it a mathematical score based on how closely its tags (Heritage, Nature, etc.) match the Group Profile.
*   **Penalties & Bonuses:** It adds bonus points if a place has a high Google Review rating, and deducts points if the entry fee exceeds your budget cap.

### 3. The OR-Tools Optimizer (`scheduler.py`)
This is the core mathematical engine. It takes the list of scored places and sets up a complex **Integer Programming problem** using Google OR-Tools. Its goal is to maximize the total "fun" (highest sum of scores) while strictly obeying these rules:
*   **Time Constraint:** You can't spend more hours visiting places in a day than your "Pace" allows (e.g., Moderate = 8 hours max).
*   **Budget Constraint:** The sum of entry fees for the day cannot exceed the daily budget.
*   **Duplication Constraint:** A place can only be visited once.
*   **City-Day Locking:** It maps specific days to specific cities (e.g., Days 1 & 2 for Delhi, Days 3-5 for Agra) so you aren't bouncing back and forth between cities on the same day.

*At this stage, you have a mathematically perfect, day-by-day schedule. But if a city lacked enough places in the database (like Agra did), those days will be empty.*

### 4. The LLM Web-Search Enhancer (`llm_enhancer.py`)
If `use_llm` is set to `True`, the itinerary gets passed here for the final magical touch:
*   **Detecting Gaps:** The code checks the generated itinerary. If it sees `Day 4: []` (an empty array), it looks up which city was supposed to be scheduled for Day 4 (Agra).
*   **Live Web Search:** It uses the `duckduckgo-search` library to programmatically search the live internet for *"top places to visit in Agra tourism spots"*.
*   **Prompting Groq:** It bundles the original itinerary, the group's preferences, and the live web search results into a massive prompt.
*   **LLM Generation:** It sends this to the Groq `llama-3.1-8b-instant` model, asking it to act as an expert travel planner. The LLM processes the search results, picks the best spots for the group, formats them as JSON, and adds a `reason`, `tip`, and a `url` for every place.

### 5. Final Output
FastAPI takes the LLM's beautifully formatted JSON (which now perfectly blends your static database data with real-time web data) and sends it back to the user as the final response!

dataset link: https://www.kaggle.com/datasets/dhrubangtalukdar/top-indian-places-to-visit-indian-tourism