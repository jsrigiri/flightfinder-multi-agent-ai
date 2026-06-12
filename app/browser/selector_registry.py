import json
from pathlib import Path


SELECTOR_MAP_DIR = Path(__file__).parent / "selector_maps"


def load_selector_map(site_name: str) -> dict:
    path = SELECTOR_MAP_DIR / f"{site_name}.json"

    if not path.exists():
        raise FileNotFoundError(
            f"Selector map not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_selector_map(site_name: str, selector_map: dict) -> None:
    SELECTOR_MAP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = SELECTOR_MAP_DIR / f"{site_name}.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            selector_map,
            file,
            indent=2,
        )


def find_elements_by_selector_list(driver, selectors: list):
    for selector in selectors:
        elements = driver.find_elements(
            "css selector",
            selector,
        )

        if elements:
            return elements

    from app.agents.skyvern_discovery_agent import (
        discover_google_flights_selectors,
    )

    discovery = discover_google_flights_selectors()

    if discovery.get("updated"):
        print(
            "Skyvern updated selector map. "
            "Retry Selenium extraction."
        )
    else:
        print(
            "Skyvern discovery did not update selector map."
        )

    return []