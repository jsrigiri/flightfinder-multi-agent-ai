from app.agents.graph import build_graph


def main():
    graph = build_graph()

    initial_state = {
        "criteria": {
            "trip_type": "Round Trip",
            "origin": "SFO",
            "destination": "JFK",
            "depart_date": "2026-07-15",
            "return_date": "2026-11-11",
            "passengers": 1,
            "max_price": 1000,
            "max_stops": 1,
            "required_checked_bags": 0,
        },
        "preferences": None,
        "plan": "",
        "search_results": [],
        "validated_results": None,
        "recommendation": "",
        "next_agent": "",
        "errors": [],
        "completed": False,
        "report": "",
        "scored_results": None,
        "google_flights_results": None,
        "expedia_results": None,
        "kayak_results": None,
        "merged_results": None,
    }

    result = graph.invoke(initial_state)

    print("\nFlightFinder Result")
    print("===================")
    print(result["report"])


if __name__ == "__main__":
    main()