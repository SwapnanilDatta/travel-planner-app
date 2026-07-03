import os
from crewai import Agent, LLM
from crewai.tools import tool
from search import cached_search          # ← our caching wrapper
from dotenv import load_dotenv

load_dotenv()


# ── Single shared tool; all three agents reuse it ──────────────────────────
@tool("DuckDuckGoSearch")
def search_tool(query: str) -> str:
    """Search the web for information about places, attractions, and logistics."""
    return cached_search(query)


# ── LLM factory ────────────────────────────────────────────────────────────
def get_llm():
    api_key = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
    return LLM(
        model="openai/gpt-oss-20b",
        provider="openai",
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    )


# ── Agent factories ─────────────────────────────────────────────────────────
def get_city_local_guide():
    return Agent(
        role="City Local Guide Expert",
        goal="Find specific attractions for the destinations matching group interests.",
        backstory="A concise local guide focusing on core attractions.",
        verbose=True,
        allow_delegation=False,
        max_iter=2,
        tools=[search_tool],
        llm=get_llm(),
    )


def get_travel_trip_expert():
    return Agent(
        role="Travel Trip Expert",
        goal="Handle logistics and compile the final day-by-day concise itinerary.",
        backstory="An efficient travel agent who outputs brief, structured itineraries.",
        verbose=True,
        allow_delegation=False,
        max_iter=4,
        tools=[search_tool],
        llm=get_llm(),
    )
