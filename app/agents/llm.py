import os
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"


def safe_llm_response(
    prompt: str,
    fallback: str,
) -> str:
    """
    Generates a response from Ollama.

    Safety features:
    - Can be disabled during tests.
    - Uses small context.
    - Unloads model immediately after inference.
    - Falls back gracefully if Ollama is unavailable.
    """

    if os.getenv("DISABLE_LLM", "false").lower() == "true":
        return fallback

    model = os.getenv(
        "OLLAMA_MODEL",
        "llama3.2:1b",
    )

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,

                # Immediately unload model after completion
                "keep_alive": 0,

                "options": {
                    "num_ctx": 1024,
                    "temperature": 0.2,
                },
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "response",
            fallback,
        ).strip()

    except Exception as e:
        print(f"LLM fallback used. Reason: {type(e).__name__}: {e}")
        return fallback


def planner_prompt(criteria: dict) -> str:
    return f"""
You are a flight search planning agent.

Create a concise search plan.

Origin: {criteria['origin']}
Destination: {criteria['destination']}
Departure: {criteria['depart_date']}
Return: {criteria.get('return_date')}
Passengers: {criteria['passengers']}
Max Price: {criteria.get('max_price')}
Max Stops: {criteria.get('max_stops')}
Required Checked Bags: {criteria.get('required_checked_bags')}

Return only the plan.
"""


def report_prompt(
    criteria: dict,
    recommendation: str,
    flights: list,
) -> str:
    return f"""
You are a flight recommendation reporting agent.

CRITICAL RULES:
- Do not invent flights.
- Do not invent airlines.
- Do not invent prices.
- Do not invent flight numbers.
- Do not invent aircraft models.
- Only use the flights listed in Available Flights.
- If a field is missing, write "Not available".
- If there are no alternatives, write "None".

Generate the response in EXACTLY this format:

FLIGHT SUMMARY
--------------
Airline:
Flight Number:
Aircraft Model:
Route:
Origin Airport:
Destination Airport:
Departure Date/Time:
Arrival Date/Time:
Price:
Stops:
Checked Bags:
Carry-on Bags:
Duration:
Flight Status:
Delay:
Layovers:
Overall Score:

FLIGHT DETAILS
--------------
Explain why this flight was selected using only the available flight data.

ROUTE DETAILS
-------------
List the route airports in order.

LEG DETAILS
-----------
If this is a non-stop flight, write:
Non-stop flight. No separate legs.

If this flight has stops, list each leg with:
- Leg Number
- Airline
- Flight Number
- Aircraft Model
- Origin Airport
- Destination Airport
- Departure Date/Time
- Arrival Date/Time
- Flight Status
- Delay
- Duration

LAYOVER DETAILS
---------------
If there are no layovers, write:
No layovers.

If there are layovers, list:
- Airport
- Airport Name
- Layover Duration

ALTERNATIVE OPTIONS
-------------------
List up to 2 alternative flights from Available Flights only.
Each alternative must include:
- Airline
- Flight Number
- Aircraft Model
- Route
- Price
- Stops
- Checked Bags
- Carry-on Bags
- Duration
- Status
- Delay

User Criteria:
{criteria}

Available Flights:
{flights}

Best Recommendation:
{recommendation}
"""