from app.agents.graph import build_graph


def main():
    graph = build_graph()

    initial_state = {
        "criteria": {
            "origin": "SFO",
            "destination": "JFK",
            "depart_date": "2026-07-15",
            "return_date": None,
            "passengers": 1,
            "max_price": 500,
            "max_stops": 1,
            "required_checked_bags": 1,
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
    }

    result = graph.invoke(initial_state)

    print("\nFlightFinder Result")
    print("===================")
    print(result["report"])


if __name__ == "__main__":
    main()