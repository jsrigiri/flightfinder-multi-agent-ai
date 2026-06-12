from langgraph.graph import StateGraph, END

from app.agents.llm import safe_llm_response, planner_prompt, report_prompt
from app.models.schemas import AgentState
from app.browser.google_flights import search_google_flights

from app.config import settings


def supervisor_agent(state: AgentState) -> AgentState:
    if state.get("completed"):
        state["next_agent"] = "end"

    elif not state.get("plan"):
        state["next_agent"] = "planner"

    elif state.get("google_flights_results") is None:
        state["next_agent"] = "google_flights"

    elif state.get("expedia_results") is None:
        state["next_agent"] = "expedia"

    elif state.get("kayak_results") is None:
        state["next_agent"] = "kayak"

    elif state.get("merged_results") is None:
        state["next_agent"] = "merge"

    elif state.get("preferences") is None:
        state["next_agent"] = "preference"

    elif state.get("validated_results") is None:
        state["next_agent"] = "validator"

    elif state.get("scored_results") is None:
        state["next_agent"] = "scorer"

    elif not state.get("recommendation"):
        state["next_agent"] = "ranker"

    elif not state.get("report"):
        state["next_agent"] = "report"

    else:
        state["completed"] = True
        state["next_agent"] = "end"

    return state


def planner_agent(state: AgentState) -> AgentState:
    criteria = state["criteria"]

    fallback = (
        f"Search flights from {criteria['origin']} to "
        f"{criteria['destination']} departing {criteria['depart_date']} "
        f"with max price ${criteria.get('max_price')}, "
        f"max stops {criteria.get('max_stops')}, and at least "
        f"{criteria.get('required_checked_bags')} checked bag(s)."
    )

    state["plan"] = safe_llm_response(
        planner_prompt(criteria),
        fallback,
    )

    return state


def search_agent(state: AgentState) -> AgentState:
    criteria = state["criteria"]

    state["search_results"] = [
        {
            "airline": "United",
            "flight_number": "UA 2381",
            "aircraft_model": "Boeing 737-900",

            "origin": criteria["origin"],
            "origin_airport_name": "San Francisco International Airport",
            "destination": criteria["destination"],
            "destination_airport_name": "John F. Kennedy International Airport",

            "route": [
                {
                    "airport": "SFO",
                    "airport_name": "San Francisco International Airport",
                },
                {
                    "airport": "JFK",
                    "airport_name": "John F. Kennedy International Airport",
                },
            ],

            "departure_date_time": "2026-07-15 08:00",
            "arrival_date_time": "2026-07-15 16:30",

            "price": 420,
            "stops": 0,

            "checked_bags": 1,
            "carry_on_bags": 1,

            "duration_minutes": 330,

            "status": "On Time",
            "delay_minutes": 0,

            "legs": [],
            "layovers": [],
        },
        {
            "airline": "Delta",
            "flight_number": "DL 1432 / DL 921",
            "aircraft_model": "Airbus A321 / Boeing 757-200",

            "origin": criteria["origin"],
            "origin_airport_name": "San Francisco International Airport",
            "destination": criteria["destination"],
            "destination_airport_name": "John F. Kennedy International Airport",

            "route": [
                {
                    "airport": "SFO",
                    "airport_name": "San Francisco International Airport",
                },
                {
                    "airport": "ATL",
                    "airport_name": "Hartsfield-Jackson Atlanta International Airport",
                },
                {
                    "airport": "JFK",
                    "airport_name": "John F. Kennedy International Airport",
                },
            ],

            "departure_date_time": "2026-07-15 07:10",
            "arrival_date_time": "2026-07-15 17:20",

            "price": 390,
            "stops": 1,

            "checked_bags": 0,
            "carry_on_bags": 1,

            "duration_minutes": 370,

            "status": "Delayed",
            "delay_minutes": 20,

            "legs": [
                {
                    "leg_number": 1,
                    "airline": "Delta",
                    "flight_number": "DL 1432",
                    "aircraft_model": "Airbus A321",
                    "origin": "SFO",
                    "origin_airport_name": "San Francisco International Airport",
                    "destination": "ATL",
                    "destination_airport_name": "Hartsfield-Jackson Atlanta International Airport",
                    "departure_date_time": "2026-07-15 07:10",
                    "arrival_date_time": "2026-07-15 14:30",
                    "status": "Delayed",
                    "delay_minutes": 20,
                    "duration_minutes": 260,
                },
                {
                    "leg_number": 2,
                    "airline": "Delta",
                    "flight_number": "DL 921",
                    "aircraft_model": "Boeing 757-200",
                    "origin": "ATL",
                    "origin_airport_name": "Hartsfield-Jackson Atlanta International Airport",
                    "destination": "JFK",
                    "destination_airport_name": "John F. Kennedy International Airport",
                    "departure_date_time": "2026-07-15 15:25",
                    "arrival_date_time": "2026-07-15 17:20",
                    "status": "On Time",
                    "delay_minutes": 0,
                    "duration_minutes": 115,
                },
            ],

            "layovers": [
                {
                    "airport": "ATL",
                    "airport_name": "Hartsfield-Jackson Atlanta International Airport",
                    "duration_minutes": 55,
                }
            ],
        },
        {
            "airline": "American",
            "flight_number": "AA 87",
            "aircraft_model": "Airbus A321neo",

            "origin": criteria["origin"],
            "origin_airport_name": "San Francisco International Airport",
            "destination": criteria["destination"],
            "destination_airport_name": "John F. Kennedy International Airport",

            "route": [
                {
                    "airport": "SFO",
                    "airport_name": "San Francisco International Airport",
                },
                {
                    "airport": "JFK",
                    "airport_name": "John F. Kennedy International Airport",
                },
            ],

            "departure_date_time": "2026-07-15 09:30",
            "arrival_date_time": "2026-07-15 18:15",

            "price": 510,
            "stops": 0,

            "checked_bags": 2,
            "carry_on_bags": 1,

            "duration_minutes": 345,

            "status": "On Time",
            "delay_minutes": 0,

            "legs": [],
            "layovers": [],
        },
    ]

    return state


def validator_agent(state: AgentState) -> AgentState:
    criteria = state["criteria"]
    results = state["search_results"]

    max_price = criteria.get("max_price")
    if max_price is not None:
        results = [
            flight for flight in results
            if flight["price"] <= max_price
        ]

    max_stops = criteria.get("max_stops")
    if max_stops is not None:
        results = [
            flight for flight in results
            if flight["stops"] <= max_stops
        ]

    required_checked_bags = criteria.get("required_checked_bags")
    if required_checked_bags is not None:
        results = [
            flight for flight in results
            if flight["checked_bags"] >= required_checked_bags
        ]

    state["validated_results"] = results

    if not results:
        state["errors"].append("No flights matched the criteria.")

    return state


def scorer_agent(state: AgentState) -> AgentState:
    results = state["validated_results"]

    if not results:
        state["scored_results"] = []
        return state

    preferences = state.get("preferences") or {}

    preferred_airlines = preferences.get(
        "preferred_airlines",
        [],
    )

    avoid_airlines = preferences.get(
        "avoid_airlines",
        [],
    )

    prefer_nonstop = preferences.get(
        "prefer_nonstop",
        False,
    )

    max_layover_minutes = preferences.get(
        "max_layover_minutes",
        120,
    )

    scored = []

    for flight in results:

        # ----------------------------
        # Price Score (25 points)
        # ----------------------------

        price_score = max(
            0,
            25 - (flight["price"] / 25),
        )

        # ----------------------------
        # Stop Score (25 points)
        # ----------------------------

        stop_score = max(
            0,
            25 - (flight["stops"] * 12),
        )

        # ----------------------------
        # Duration Score (15 points)
        # ----------------------------

        duration_score = max(
            0,
            15 - (flight["duration_minutes"] / 60),
        )

        # ----------------------------
        # Baggage Score (10 points)
        # ----------------------------

        baggage_score = min(
            10,
            (
                flight["checked_bags"] * 5
                + flight["carry_on_bags"] * 2
            ),
        )

        # ----------------------------
        # Delay Score (10 points)
        # ----------------------------

        delay_score = max(
            0,
            10 - (flight["delay_minutes"] / 5),
        )

        # ----------------------------
        # Airline Preference Score
        # ----------------------------

        airline_preference_score = 0

        if flight["airline"] in preferred_airlines:
            airline_preference_score += 10

        if flight["airline"] in avoid_airlines:
            airline_preference_score -= 10

        # ----------------------------
        # Layover Score
        # ----------------------------

        layover_score = 5

        for layover in flight.get("layovers", []):

            if (
                layover["duration_minutes"]
                > max_layover_minutes
            ):
                layover_score -= 5

        layover_score = max(
            0,
            layover_score,
        )

        # ----------------------------
        # Nonstop Bonus
        # ----------------------------

        nonstop_bonus = 0

        if (
            prefer_nonstop
            and flight["stops"] == 0
        ):
            nonstop_bonus = 5

        # ----------------------------
        # Overall Score
        # ----------------------------

        overall_score = round(
            price_score
            + stop_score
            + duration_score
            + baggage_score
            + delay_score
            + airline_preference_score
            + layover_score
            + nonstop_bonus,
            2,
        )

        flight["score_breakdown"] = {
            "price_score": round(
                price_score,
                2,
            ),
            "stop_score": round(
                stop_score,
                2,
            ),
            "duration_score": round(
                duration_score,
                2,
            ),
            "baggage_score": round(
                baggage_score,
                2,
            ),
            "delay_score": round(
                delay_score,
                2,
            ),
            "airline_preference_score": round(
                airline_preference_score,
                2,
            ),
            "layover_score": round(
                layover_score,
                2,
            ),
            "nonstop_bonus": round(
                nonstop_bonus,
                2,
            ),
        }

        flight["overall_score"] = overall_score

        scored.append(flight)

    state["scored_results"] = scored

    return state


def ranker_agent(state: AgentState) -> AgentState:
    results = state["scored_results"]

    if not results:
        state["recommendation"] = "No valid flights found."
        state["report"] = """
FLIGHT SUMMARY
--------------
No flights matched your criteria.

FLIGHT DETAILS
--------------
Try increasing your max price, allowing more stops, or reducing the required checked baggage.

ALTERNATIVE OPTIONS
-------------------
None
""".strip()
        state["completed"] = True
        return state

    ranked = sorted(
        results,
        key=lambda flight: (
            -flight["overall_score"],
            flight["price"],
            flight["stops"],
            flight["duration_minutes"],
        ),
    )

    best = ranked[0]
    state["validated_results"] = ranked

    state["recommendation"] = (
        f"Best flight: {best['airline']} "
        f"{best['origin']}->{best['destination']} "
        f"for ${best['price']} | "
        f"Stops: {best['stops']} | "
        f"Checked Bags: {best['checked_bags']} | "
        f"Carry-on Bags: {best['carry_on_bags']} | "
        f"Score: {best['overall_score']} | "
        f"Duration: {best['duration_minutes']} mins"
    )

    return state


def preference_agent(state: AgentState) -> AgentState:
    criteria = state["criteria"]

    state["preferences"] = {
        "preferred_airlines": criteria.get(
            "preferred_airlines",
            ["United", "Delta"],
        ),
        "avoid_airlines": criteria.get(
            "avoid_airlines",
            ["Spirit", "Frontier"],
        ),
        "prefer_nonstop": criteria.get(
            "prefer_nonstop",
            True,
        ),
        "max_layover_minutes": criteria.get(
            "max_layover_minutes",
            120,
        ),
        "redeye_allowed": criteria.get(
            "redeye_allowed",
            False,
        ),
        "required_checked_bags": criteria.get(
            "required_checked_bags",
            0,
        ),
    }

    return state


def build_fallback_report(state: AgentState) -> str:
    flights = state["validated_results"]

    if not flights:
        return """
FLIGHT SUMMARY
--------------
No flights matched your criteria.

FLIGHT DETAILS
--------------
Try increasing your max price, allowing more stops, or reducing the required checked baggage.

ALTERNATIVE OPTIONS
-------------------
None
""".strip()

    best = flights[0]
    alternatives = flights[1:3]

    alternative_lines = []

    if alternatives:
        for index, flight in enumerate(alternatives, start=2):
            alternative_lines.append(
                f"{index}. {flight['airline']} | "
                f"${flight['price']} | "
                f"Stops: {flight['stops']} | "
                f"Checked Bags: {flight['checked_bags']} | "
                f"Duration: {flight['duration_minutes']} mins"
            )
    else:
        alternative_lines.append("None")

    alternatives_text = "\n".join(alternative_lines)

    return f"""
FLIGHT SUMMARY
--------------
Airline: {best['airline']}
Route: {best['origin']} -> {best['destination']}
Price: ${best['price']}
Stops: {best['stops']}
Checked Bags: {best['checked_bags']}
Carry-on Bags: {best['carry_on_bags']}
Duration: {best['duration_minutes']} minutes

FLIGHT DETAILS
--------------
This flight was selected because it has the best balance of fewer stops, lower price, baggage allowance, and shorter duration.

ALTERNATIVE OPTIONS
-------------------
{alternatives_text}
""".strip()


def format_flight_detail_block(title: str, flight: dict) -> str:
    route_text = " -> ".join(
        [
            airport["airport"]
            for airport in flight.get("route", [])
        ]
    )

    return f"""
{title}
{'-' * len(title)}
Airline: {flight.get('airline', 'N/A')}
Flight Number: {flight.get('flight_number', 'N/A')}
Aircraft Model: {flight.get('aircraft_model', 'N/A')}
Route: {route_text}
Departure: {flight.get('departure_date_time', 'N/A')}
Arrival: {flight.get('arrival_date_time', 'N/A')}
Price: ${flight.get('price', 'N/A')}
Stops: {flight.get('stops', 'N/A')}
Checked Bags: {flight.get('checked_bags', 'N/A')}
Carry-on Bags: {flight.get('carry_on_bags', 'N/A')}
Duration: {flight.get('duration_minutes', 'N/A')} minutes
Status: {flight.get('status', 'N/A')}
Delay: {flight.get('delay_minutes', 'N/A')} minutes
""".strip()


def report_agent(state: AgentState) -> AgentState:
    flights = state["scored_results"]

    if not flights:
        state["report"] = """
FLIGHT SUMMARY
--------------
No flights matched your criteria.

FLIGHT DETAILS
--------------
Try increasing your max price, allowing more stops, or reducing the required checked baggage.

ROUTE DETAILS
-------------
Not available

LEG DETAILS
-----------
Not available

LAYOVER DETAILS
---------------
Not available

ALTERNATIVE OPTIONS
-------------------
None
""".strip()

        state["completed"] = True
        return state

    best = flights[0]
    alternatives = flights[1:3]

    trip_type = best.get("trip_type", "One Way")

    route_text = " -> ".join(
        [
            airport["airport"]
            for airport in best.get("route", [])
        ]
    )

    score_breakdown = best.get("score_breakdown", {})

    if trip_type == "Round Trip":
        outbound = best.get("outbound_flight", {})
        return_flight = best.get("return_flight", {})

        round_trip_details = (
            format_flight_detail_block(
                "OUTBOUND FLIGHT",
                outbound,
            )
            + "\n\n"
            + format_flight_detail_block(
                "RETURN FLIGHT",
                return_flight,
            )
        )
    else:
        round_trip_details = ""

    if best.get("legs"):
        legs_text = "\n".join(
            [
                (
                    f"Leg {leg['leg_number']}: "
                    f"{leg['airline']} {leg['flight_number']} | "
                    f"Aircraft: {leg['aircraft_model']} | "
                    f"{leg['origin']} ({leg['origin_airport_name']}) -> "
                    f"{leg['destination']} ({leg['destination_airport_name']}) | "
                    f"Departure: {leg['departure_date_time']} | "
                    f"Arrival: {leg['arrival_date_time']} | "
                    f"Status: {leg['status']} | "
                    f"Delay: {leg['delay_minutes']} mins | "
                    f"Duration: {leg['duration_minutes']} mins"
                )
                for leg in best["legs"]
            ]
        )
    else:
        if trip_type == "Round Trip":
            legs_text = "Round trip itinerary. See outbound and return flight sections."
        else:
            legs_text = "Non-stop flight. No separate legs."

    if best.get("layovers"):
        layover_text = "\n".join(
            [
                (
                    f"{layover['airport']} - {layover['airport_name']} | "
                    f"Layover Duration: {layover['duration_minutes']} mins"
                )
                for layover in best["layovers"]
            ]
        )
    else:
        layover_text = "No layovers."

    if alternatives:
        alternative_lines = []

        for index, flight in enumerate(alternatives, start=2):
            alt_route = " -> ".join(
                [
                    airport["airport"]
                    for airport in flight.get("route", [])
                ]
            )

            alt_trip_type = flight.get("trip_type", "One Way")

            alternative_lines.append(
                f"{index}. Trip Type: {alt_trip_type} | "
                f"{flight['airline']} | "
                f"Flight: {flight['flight_number']} | "
                f"Aircraft: {flight['aircraft_model']} | "
                f"Route: {alt_route} | "
                f"Price: ${flight['price']} | "
                f"Stops: {flight['stops']} | "
                f"Checked Bags: {flight['checked_bags']} | "
                f"Carry-on Bags: {flight['carry_on_bags']} | "
                f"Duration: {flight['duration_minutes']} mins | "
                f"Status: {flight['status']} | "
                f"Delay: {flight['delay_minutes']} mins | "
                f"Score: {flight.get('overall_score', 'N/A')}/100"
            )

            if alt_trip_type == "Round Trip":
                outbound = flight.get("outbound_flight", {})
                return_flight = flight.get("return_flight", {})

                alternative_lines.append(
                    f"   Outbound: "
                    f"{outbound.get('airline', 'N/A')} "
                    f"{outbound.get('flight_number', 'N/A')} | "
                    f"{outbound.get('aircraft_model', 'N/A')} | "
                    f"{outbound.get('origin', 'N/A')} -> "
                    f"{outbound.get('destination', 'N/A')}"
                )

                alternative_lines.append(
                    f"   Return: "
                    f"{return_flight.get('airline', 'N/A')} "
                    f"{return_flight.get('flight_number', 'N/A')} | "
                    f"{return_flight.get('aircraft_model', 'N/A')} | "
                    f"{return_flight.get('origin', 'N/A')} -> "
                    f"{return_flight.get('destination', 'N/A')}"
                )

        alternatives_text = "\n".join(alternative_lines)
    else:
        alternatives_text = "None"

    explanation_prompt = f"""
Use ONLY this data:
Trip Type: {trip_type}
Airline: {best['airline']}
Price: {best['price']}
Stops: {best['stops']}
Checked Bags: {best['checked_bags']}
Carry-on Bags: {best['carry_on_bags']}
Duration: {best['duration_minutes']}
Delay Minutes: {best['delay_minutes']}
Overall Score: {best.get('overall_score')}

Write exactly 2 sentences.
Do not mention satisfaction.
Do not invent anything.
"""

    fallback_explanation = (
        "This itinerary was selected because it had the strongest deterministic score "
        "after comparing stops, price, baggage allowance, duration, and delay time. "
        "It also matched the user's required filters."
    )

    ai_explanation = safe_llm_response(
        explanation_prompt,
        fallback_explanation,
    )

    round_trip_section = ""

    if trip_type == "Round Trip":
        round_trip_section = f"""

ROUND TRIP DETAILS
------------------
{round_trip_details}
"""

    state["report"] = f"""
FLIGHT SUMMARY
--------------
Trip Type: {trip_type}
Airline: {best['airline']}
Flight Number: {best['flight_number']}
Aircraft Model: {best['aircraft_model']}
Route: {route_text}
Origin Airport: {best['origin']} - {best['origin_airport_name']}
Destination Airport: {best['destination']} - {best['destination_airport_name']}
Departure Date/Time: {best['departure_date_time']}
Arrival Date/Time: {best['arrival_date_time']}
Price: ${best['price']}
Stops: {best['stops']}
Checked Bags: {best['checked_bags']}
Carry-on Bags: {best['carry_on_bags']}
Duration: {best['duration_minutes']} minutes
Flight Status: {best['status']}
Delay: {best['delay_minutes']} minutes
Overall Score: {best.get('overall_score', 'N/A')}/100
{round_trip_section}
SCORE BREAKDOWN
---------------
Price Score: {score_breakdown.get('price_score', 'N/A')}
Stop Score: {score_breakdown.get('stop_score', 'N/A')}
Duration Score: {score_breakdown.get('duration_score', 'N/A')}
Baggage Score: {score_breakdown.get('baggage_score', 'N/A')}
Delay Score: {score_breakdown.get('delay_score', 'N/A')}
Airline Preference Score: {score_breakdown.get('airline_preference_score', 'N/A')}
Layover Score: {score_breakdown.get('layover_score', 'N/A')}
Nonstop Bonus: {score_breakdown.get('nonstop_bonus', 'N/A')}

FLIGHT DETAILS
--------------
{ai_explanation}

ROUTE DETAILS
-------------
{route_text}

LEG DETAILS
-----------
{legs_text}

LAYOVER DETAILS
---------------
{layover_text}

ALTERNATIVE OPTIONS
-------------------
{alternatives_text}
""".strip()

    state["completed"] = True
    return state


def route_next(state: AgentState) -> str:
    return state["next_agent"]


def google_flights_agent(state: AgentState) -> AgentState:
    criteria = state["criteria"]

    fallback_results = [
        {
            "source": "Google Flights",
            "airline": "United",
            "flight_number": "UA 2381",
            "aircraft_model": "Boeing 737-900",
            "origin": criteria["origin"],
            "origin_airport_name": "San Francisco International Airport",
            "destination": criteria["destination"],
            "destination_airport_name": "John F. Kennedy International Airport",
            "route": [
                {
                    "airport": criteria["origin"],
                    "airport_name": "San Francisco International Airport",
                },
                {
                    "airport": criteria["destination"],
                    "airport_name": "John F. Kennedy International Airport",
                },
            ],
            "departure_date_time": f"{criteria['depart_date']} 08:00",
            "arrival_date_time": f"{criteria['depart_date']} 16:30",
            "price": 420,
            "stops": 0,
            "checked_bags": 1,
            "carry_on_bags": 1,
            "duration_minutes": 330,
            "status": "On Time",
            "delay_minutes": 0,
            "legs": [],
            "layovers": [],
        }
    ]

    if settings.USE_LIVE_GOOGLE_FLIGHTS:
        google_result = search_google_flights(criteria)
    else:
        google_result = {
            "success": False,
            "results": [],
        }

    print(google_result)

    if google_result.get("success") and google_result.get("results"):
        state["google_flights_results"] = google_result["results"]
    else:
        state["google_flights_results"] = fallback_results

    return state


def expedia_agent(state: AgentState) -> AgentState:
    criteria = state["criteria"]

    state["expedia_results"] = [
        {
            "source": "Expedia",
            "airline": "Delta",
            "flight_number": "DL 1432 / DL 921",
            "aircraft_model": "Airbus A321 / Boeing 757-200",
            "origin": criteria["origin"],
            "origin_airport_name": "San Francisco International Airport",
            "destination": criteria["destination"],
            "destination_airport_name": "John F. Kennedy International Airport",
            "route": [
                {"airport": "SFO", "airport_name": "San Francisco International Airport"},
                {"airport": "ATL", "airport_name": "Hartsfield-Jackson Atlanta International Airport"},
                {"airport": "JFK", "airport_name": "John F. Kennedy International Airport"},
            ],
            "departure_date_time": "2026-07-15 07:10",
            "arrival_date_time": "2026-07-15 17:20",
            "price": 390,
            "stops": 1,
            "checked_bags": 0,
            "carry_on_bags": 1,
            "duration_minutes": 370,
            "status": "Delayed",
            "delay_minutes": 20,
            "legs": [
                {
                    "leg_number": 1,
                    "airline": "Delta",
                    "flight_number": "DL 1432",
                    "aircraft_model": "Airbus A321",
                    "origin": "SFO",
                    "origin_airport_name": "San Francisco International Airport",
                    "destination": "ATL",
                    "destination_airport_name": "Hartsfield-Jackson Atlanta International Airport",
                    "departure_date_time": "2026-07-15 07:10",
                    "arrival_date_time": "2026-07-15 14:30",
                    "status": "Delayed",
                    "delay_minutes": 20,
                    "duration_minutes": 260,
                },
                {
                    "leg_number": 2,
                    "airline": "Delta",
                    "flight_number": "DL 921",
                    "aircraft_model": "Boeing 757-200",
                    "origin": "ATL",
                    "origin_airport_name": "Hartsfield-Jackson Atlanta International Airport",
                    "destination": "JFK",
                    "destination_airport_name": "John F. Kennedy International Airport",
                    "departure_date_time": "2026-07-15 15:25",
                    "arrival_date_time": "2026-07-15 17:20",
                    "status": "On Time",
                    "delay_minutes": 0,
                    "duration_minutes": 115,
                },
            ],
            "layovers": [
                {
                    "airport": "ATL",
                    "airport_name": "Hartsfield-Jackson Atlanta International Airport",
                    "duration_minutes": 55,
                }
            ],
        }
    ]

    return state


def kayak_agent(state: AgentState) -> AgentState:
    criteria = state["criteria"]

    state["kayak_results"] = [
        {
            "source": "Kayak",
            "airline": "American",
            "flight_number": "AA 87",
            "aircraft_model": "Airbus A321neo",
            "origin": criteria["origin"],
            "origin_airport_name": "San Francisco International Airport",
            "destination": criteria["destination"],
            "destination_airport_name": "John F. Kennedy International Airport",
            "route": [
                {"airport": "SFO", "airport_name": "San Francisco International Airport"},
                {"airport": "JFK", "airport_name": "John F. Kennedy International Airport"},
            ],
            "departure_date_time": "2026-07-15 09:30",
            "arrival_date_time": "2026-07-15 18:15",
            "price": 510,
            "stops": 0,
            "checked_bags": 2,
            "carry_on_bags": 1,
            "duration_minutes": 345,
            "status": "On Time",
            "delay_minutes": 0,
            "legs": [],
            "layovers": [],
        }
    ]

    return state


def flight_key(flight: dict) -> tuple:
    return (
        flight["airline"],
        flight["flight_number"],
        flight["origin"],
        flight["destination"],
        flight["departure_date_time"],
        flight["arrival_date_time"],
    )


def merge_agent(state: AgentState) -> AgentState:
    if settings.USE_LIVE_GOOGLE_FLIGHTS:
        google_results = state.get("google_flights_results") or []

        state["merged_results"] = google_results
        state["search_results"] = google_results

        return state

    all_results = []

    all_results.extend(state.get("google_flights_results") or [])
    all_results.extend(state.get("expedia_results") or [])
    all_results.extend(state.get("kayak_results") or [])

    deduped = {}

    for flight in all_results:
        key = flight_key(flight)

        if key not in deduped:
            deduped[key] = flight
        else:
            existing = deduped[key]

            if flight["price"] < existing["price"]:
                flight["source"] = f"{existing['source']}, {flight['source']}"
                deduped[key] = flight
            else:
                existing["source"] = f"{existing['source']}, {flight['source']}"

    merged = list(deduped.values())

    state["merged_results"] = merged
    state["search_results"] = merged

    return state


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_agent)
    graph.add_node("planner", planner_agent)
    graph.add_node("search", search_agent)
    graph.add_node("validator", validator_agent)
    graph.add_node("scorer", scorer_agent)
    graph.add_node("ranker", ranker_agent)
    graph.add_node("report", report_agent)
    graph.add_node("preference", preference_agent)
    graph.add_node("google_flights", google_flights_agent)
    graph.add_node("expedia", expedia_agent)
    graph.add_node("kayak", kayak_agent)
    graph.add_node("merge", merge_agent)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_next,
        {
            "planner": "planner",
            "search": "search",
            "validator": "validator",
            "scorer": "scorer",
            "ranker": "ranker",
            "report": "report",
            "preference": "preference",
            "google_flights": "google_flights",
            "expedia": "expedia",
            "kayak": "kayak",
            "merge": "merge",
            "end": END,
        },
    )

    graph.add_edge("planner", "supervisor")
    graph.add_edge("search", "supervisor")
    graph.add_edge("validator", "supervisor")
    graph.add_edge("scorer", "supervisor")
    graph.add_edge("ranker", "supervisor")
    graph.add_edge("report", "supervisor")
    graph.add_edge("preference", "supervisor")
    graph.add_edge("google_flights", "supervisor")
    graph.add_edge("expedia", "supervisor")
    graph.add_edge("kayak", "supervisor")
    graph.add_edge("merge", "supervisor")

    return graph.compile()