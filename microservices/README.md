{
  "destinations": ["Delhi", "Agra"],
  "total_days": 5,
  "group_size": 4,
  "pace": "Moderate", 
  "budget_per_day_INR": "1500-3000",
  "budget_type": "per_group", 
  "use_llm": false,
  "members": [
    {
      "name": "Ankit",
      "age_group": "25-35",
      "mobility_constraints": false,
      "preferences": {
        "Historical & Heritage": 5,
        "Nature & Outdoors": 3,
        "Shopping": 1
      }
    },
    {
      "name": "Grandpa",
      "age_group": "65+",
      "mobility_constraints": true,
      "preferences": {
        "Religious & Spiritual": 5,
        "Food & Local Culture": 4
      }
    }
  ]
}
How it works:

Agent Framework: The system utilizes three distinct AI agents that work collaboratively to plan a trip:
City Local Guide Expert: Researches and provides information on things to do based on user interests (9:43).
Travel Trip Expert: Handles logistics and location-specific details (10:29).
Travel Planning Expert: Acts as the primary coordinator, gathering insights from the other two agents to compile the final itinerary (11:16).

Technology Stack:
Grow llm.
DuckDuckGo Search: An integrated tool that allows the agents to fetch real-time data from the web (8:59, 9:35).
Fastapi json Powers the where users input their destination, dates, and interests
. (22:32).

Workflow: When a user triggers the "Generate Travel Plan" button (23:34), the agents execute tasks in a sequential process (17:35). They gather data, create files (like `cityreport.md` and `travelplan.md`), and finally present a comprehensive, day-by-day itinerary directly in the app (18:41, 19:16).