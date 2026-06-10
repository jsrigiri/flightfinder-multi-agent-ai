from typing import TypedDict, List, Dict, Any, Optional


class FlightCriteria(TypedDict):
    origin: str
    destination: str
    depart_date: str
    return_date: Optional[str]
    passengers: int
    max_price: Optional[float]
    max_stops: Optional[int]
    required_checked_bags: Optional[int]


class AgentState(TypedDict):
    criteria: FlightCriteria
    preferences: Optional[Dict[str, Any]]
    plan: str
    search_results: List[Dict[str, Any]]
    validated_results: Optional[List[Dict[str, Any]]]
    recommendation: str
    report: str
    next_agent: str
    errors: List[str]
    completed: bool
    scored_results: Optional[List[Dict[str, Any]]]
    google_flights_results: Optional[List[Dict[str, Any]]]
    expedia_results: Optional[List[Dict[str, Any]]]
    kayak_results: Optional[List[Dict[str, Any]]]
    merged_results: Optional[List[Dict[str, Any]]]