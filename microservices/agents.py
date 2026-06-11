import os
from crewai import Agent, LLM
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv

load_dotenv()

search_run = DuckDuckGoSearchRun()

@tool("DuckDuckGoSearch")
def search_tool(query: str) -> str:
    """Search the web for information about places, attractions, and logistics."""
    return search_run.run(query)

# Initialize the Groq LLM natively for CrewAI
def get_llm():
    # Use OpenAI native provider mapped to Groq endpoint to bypass LiteLLM cache_breakpoint bug
    api_key = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
    return LLM(
        model="llama-3.1-8b-instant",
        provider="openai",
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

def get_city_local_guide():
    return Agent(
        role="City Local Guide Expert",
        goal="Provide detailed information, attractions, and hidden gems about the given destinations that match the group's interests.",
        backstory="A seasoned local guide who knows the ins and outs of every destination, keeping in mind the mobility and age constraints of the travelers.",
        verbose=True,
        allow_delegation=False,
        tools=[search_tool],
        llm=get_llm()
    )

def get_travel_trip_expert():
    return Agent(
        role="Travel Trip Expert",
        goal="Handle logistics, routing, pacing, and location-specific budget details.",
        backstory="An experienced travel agent who excels at creating realistic itineraries considering budget, pace, and group size constraints.",
        verbose=True,
        allow_delegation=False,
        tools=[search_tool],
        llm=get_llm()
    )

def get_travel_planning_expert():
    return Agent(
        role="Travel Planning Expert",
        goal="Coordinate insights from the other agents and compile the final comprehensive day-by-day itinerary.",
        backstory="A master travel planner who synthesizes research and logistics into beautiful, actionable travel plans.",
        verbose=False,
        allow_delegation=False,
        llm=get_llm()
    )
