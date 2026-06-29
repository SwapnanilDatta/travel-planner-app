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
        goal=(
            "Provide detailed information, attractions, and hidden gems about the given "
            "destinations that match the group's interests."
        ),
        backstory=(
            "A seasoned local guide who knows the ins and outs of every destination, "
            "keeping in mind the mobility and age constraints of the travelers."
        ),
        verbose=True,
        allow_delegation=False,
        max_iter=15,           # needs ~6+ searches before final answer
        tools=[search_tool],
        llm=get_llm(),
    )


def get_travel_trip_expert():
    return Agent(
        role="Travel Trip Expert",
        goal="Handle logistics, routing, pacing, and location-specific budget details.",
        backstory=(
            "An experienced travel agent who excels at creating realistic itineraries "
            "considering budget, pace, and group size constraints."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[search_tool],          # cache means repeated queries cost nothing
        llm=get_llm(),
    )


def get_travel_planning_expert():
    return Agent(
        role="Travel Planning Expert",
        goal=(
            "Coordinate insights from the other agents and compile the final "
            "comprehensive day-by-day itinerary."
        ),
        backstory=(
            "A master travel planner who synthesizes research and logistics into "
            "beautiful, actionable travel plans."
        ),
        verbose=False,
        allow_delegation=False,
        # No search tool needed – works only from prior agents' outputs
        llm=get_llm(),
    )
