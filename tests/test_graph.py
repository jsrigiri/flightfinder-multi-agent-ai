import os

os.environ["DISABLE_LLM"] = "true"
os.environ["OLLAMA_MODEL"] = "llama3.2:1b"

from app.agents.graph import build_graph


def base_state(
    max_price=500,
    max_stops=1,
    required_checked_bags=1,
):
    return {
        "criteria": {
            "origin": "SFO",
            "destination": "JFK",
            "depart_date": "2026-07-15",
            "return_date": None,
            "passengers": 1,
            "max_price": max_price,
            "max_stops": max_stops,
            "required_checked_bags": required_checked_bags,
            "preferred_airlines": ["United", "Delta"],
            "avoid_airlines": ["Spirit", "Frontier"],
            "prefer_nonstop": True,
            "max_layover_minutes": 120,
            "redeye_allowed": False,
        },
        "preferences": None,
        "plan": "",
        "search_results": [],
        "validated_results": None,
        "scored_results": None,
        "recommendation": "",
        "report": "",
        "next_agent": "",
        "errors": [],
        "completed": False,
    }


def test_graph_returns_recommendation():
    graph = build_graph()
    result = graph.invoke(base_state())

    assert result["completed"] is True
    assert "Best flight" in result["recommendation"]


def test_recommendation_includes_stops_and_baggage():
    graph = build_graph()
    result = graph.invoke(base_state())

    recommendation = result["recommendation"]

    assert "Stops:" in recommendation
    assert "Checked Bags:" in recommendation
    assert "Carry-on Bags:" in recommendation


def test_filters_by_max_stops():
    graph = build_graph()
    result = graph.invoke(
        base_state(
            max_price=500,
            max_stops=0,
            required_checked_bags=1,
        )
    )

    for flight in result["validated_results"]:
        assert flight["stops"] <= 0


def test_filters_by_required_checked_bags():
    graph = build_graph()
    result = graph.invoke(
        base_state(
            max_price=500,
            max_stops=1,
            required_checked_bags=1,
        )
    )

    for flight in result["validated_results"]:
        assert flight["checked_bags"] >= 1


def test_no_valid_flights_when_constraints_too_strict():
    graph = build_graph()
    result = graph.invoke(
        base_state(
            max_price=300,
            max_stops=0,
            required_checked_bags=2,
        )
    )

    assert result["recommendation"] == "No valid flights found."
    assert "No flights matched the criteria." in result["errors"]
    assert result["scored_results"] == []
    assert result["completed"] is True


def test_graph_returns_report():
    graph = build_graph()
    result = graph.invoke(base_state())

    assert result["completed"] is True
    assert result["report"]
    assert "FLIGHT SUMMARY" in result["report"]
    assert "SCORE BREAKDOWN" in result["report"]


def test_flight_details_include_legs_and_layovers():
    graph = build_graph()
    result = graph.invoke(base_state())

    best = result["scored_results"][0]

    assert "flight_number" in best
    assert "aircraft_model" in best
    assert "departure_date_time" in best
    assert "arrival_date_time" in best
    assert "status" in best
    assert "delay_minutes" in best
    assert "route" in best
    assert "legs" in best
    assert "layovers" in best

    if best["stops"] == 0:
        assert best["legs"] == []
        assert best["layovers"] == []
    else:
        assert len(best["legs"]) >= 1
        assert len(best["layovers"]) == best["stops"]


def test_preference_agent_creates_preferences():
    graph = build_graph()
    result = graph.invoke(base_state())

    preferences = result["preferences"]

    assert preferences["preferred_airlines"] == ["United", "Delta"]
    assert preferences["avoid_airlines"] == ["Spirit", "Frontier"]
    assert preferences["prefer_nonstop"] is True
    assert preferences["max_layover_minutes"] == 120
    assert preferences["redeye_allowed"] is False


def test_scorer_adds_score_breakdown():
    graph = build_graph()
    result = graph.invoke(base_state())

    best = result["scored_results"][0]

    assert "overall_score" in best
    assert "score_breakdown" in best

    breakdown = best["score_breakdown"]

    assert "price_score" in breakdown
    assert "stop_score" in breakdown
    assert "duration_score" in breakdown
    assert "baggage_score" in breakdown
    assert "delay_score" in breakdown
    assert "airline_preference_score" in breakdown
    assert "layover_score" in breakdown
    assert "nonstop_bonus" in breakdown


def test_preferred_airline_and_nonstop_bonus_affect_score():
    graph = build_graph()
    result = graph.invoke(base_state())

    best = result["scored_results"][0]
    breakdown = best["score_breakdown"]

    assert breakdown["airline_preference_score"] >= 0

    if best["airline"] in result["preferences"]["preferred_airlines"]:
        assert breakdown["airline_preference_score"] == 10

    if best["stops"] == 0 and result["preferences"]["prefer_nonstop"]:
        assert breakdown["nonstop_bonus"] == 5