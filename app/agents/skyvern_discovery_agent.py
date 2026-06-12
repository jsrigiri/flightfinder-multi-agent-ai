from app.config import settings


def discover_google_flights_selectors():
    """
    Placeholder for future Skyvern integration.

    Goal:
    - Ask Skyvern to inspect Google Flights
    - Identify flight card containers
    - Identify detail buttons
    - Identify select-flight buttons
    - Save updated selector map
    """

    if not settings.USE_SKYVERN_DISCOVERY:
        return {
            "enabled": False,
            "updated": False,
            "selector_map": None,
        }

    return {
        "enabled": True,
        "updated": False,
        "selector_map": None,
        "message": "Skyvern discovery is enabled, but implementation is not wired yet.",
    }