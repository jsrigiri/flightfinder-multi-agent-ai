import json
import requests

from app.config import settings
from app.browser.selector_registry import save_selector_map


def discover_google_flights_selectors():
    print("Skyvern URL:", settings.SKYVERN_API_URL)
    print("Skyvern Key Present:", bool(settings.SKYVERN_API_KEY))
    
    if not settings.USE_SKYVERN_DISCOVERY:
        return {
            "enabled": False,
            "updated": False,
            "selector_map": None,
        }

    if not settings.SKYVERN_API_KEY:
        print("Skyvern discovery enabled but SKYVERN_API_KEY is missing.")

        return {
            "enabled": True,
            "updated": False,
            "selector_map": None,
        }

    url = "https://www.google.com/travel/flights"

    payload = {
        "url": url,
        "engine": "skyvern-2.0",
        "title": "Discover Google Flights selectors",
        "prompt": (
            "Inspect Google Flights search results. "
            "Return a JSON object with CSS selectors and aria-label fragments "
            "needed for Selenium automation. "
            "Find: flight result list items, flight details button, "
            "select flight button, baggage button. "
            "Return only JSON."
        ),
        "data_extraction_schema": {
            "type": "object",
            "properties": {
                "flight_items": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "flight_details_button_aria_contains": {
                    "type": "string",
                },
                "select_button_aria_contains": {
                    "type": "string",
                },
                "baggage_button_aria_contains": {
                    "type": "string",
                },
            },
            "required": [
                "flight_items",
                "flight_details_button_aria_contains",
                "select_button_aria_contains",
                "baggage_button_aria_contains",
            ],
        },
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": settings.SKYVERN_API_KEY,
    }

    endpoint = (
        settings.SKYVERN_API_URL.rstrip("/")
        + "/v1/run/tasks"
    )

    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        selector_map = extract_selector_map_from_skyvern_response(data)

        if not selector_map:
            print("Skyvern response did not include a usable selector map.")

            return {
                "enabled": True,
                "updated": False,
                "selector_map": None,
                "raw_response": data,
            }

        save_selector_map(
            "google_flights",
            selector_map,
        )

        return {
            "enabled": True,
            "updated": True,
            "selector_map": selector_map,
        }

    except Exception as error:
        print(f"Skyvern discovery failed: {error}")

        return {
            "enabled": True,
            "updated": False,
            "selector_map": None,
            "error": str(error),
        }


def extract_selector_map_from_skyvern_response(data: dict):
    candidates = [
        data.get("extracted_data"),
        data.get("data"),
        data.get("result"),
        data.get("output"),
    ]

    for candidate in candidates:
        parsed = parse_possible_json(candidate)

        if is_valid_selector_map(parsed):
            return parsed

    parsed = parse_possible_json(data)

    if is_valid_selector_map(parsed):
        return parsed

    return None


def parse_possible_json(value):
    if isinstance(value, dict):
        return value

    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    return None


def is_valid_selector_map(value):
    if not isinstance(value, dict):
        return False

    required_keys = [
        "flight_items",
        "flight_details_button_aria_contains",
        "select_button_aria_contains",
        "baggage_button_aria_contains",
    ]

    for key in required_keys:
        if key not in value:
            return False

    if not isinstance(value["flight_items"], list):
        return False

    return True