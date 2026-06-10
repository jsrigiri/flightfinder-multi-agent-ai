import time, os
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from app.browser.selenium_client import browser_session

from app.config import settings


def parse_duration_minutes(duration_text: str) -> int:
    hours = 0
    minutes = 0

    hour_match = re.search(r"(\d+)\s*hr", duration_text)
    minute_match = re.search(r"(\d+)\s*min", duration_text)

    if hour_match:
        hours = int(hour_match.group(1))

    if minute_match:
        minutes = int(minute_match.group(1))

    return hours * 60 + minutes


def parse_google_flights_text(
    body_text: str,
    criteria: dict,
    max_results: int = 10,
):
    lines = [
        line.strip()
        for line in body_text.splitlines()
        if line.strip()
    ]

    flights = []

    airlines = {
        "United",
        "Delta",
        "American",
        "Alaska",
        "JetBlue",
        "Southwest",
        "Frontier",
        "Spirit",
    }

    for i, line in enumerate(lines):
        if line not in airlines:
            continue

        try:
            departure_time = lines[i - 3]
            arrival_time = lines[i - 1]
            airline = line
            duration = lines[i + 1]
            route = lines[i + 2]
            stop_text = lines[i + 3]

            price = None
            layover_text = None

            for j in range(i + 4, min(i + 12, len(lines))):
                if lines[j].startswith("$"):
                    price = int(
                        lines[j]
                        .replace("$", "")
                        .replace(",", "")
                    )
                    break

                if "min" in lines[j] and any(
                    airport in lines[j]
                    for airport in ["PDX", "BOS", "ORD", "LAX", "ATL", "DEN"]
                ):
                    layover_text = lines[j]

            if price is None:
                continue

            stops = 0
            layovers = []

            if "Nonstop" in stop_text:
                stops = 0
            elif "1 stop" in stop_text:
                stops = 1
            elif "2 stops" in stop_text:
                stops = 2

            if layover_text:
                parts = layover_text.split()
                layover_airport = parts[-1]
                layover_duration = parse_duration_minutes(
                    " ".join(parts[:-1])
                )

                layovers.append(
                    {
                        "airport": layover_airport,
                        "airport_name": layover_airport,
                        "duration_minutes": layover_duration,
                    }
                )

            flight = {
                "source": "Google Flights",
                "airline": airline,
                "flight_number": "Not available",
                "aircraft_model": "Not available",
                "origin": criteria["origin"],
                "origin_airport_name": criteria["origin"],
                "destination": criteria["destination"],
                "destination_airport_name": criteria["destination"],
                "route": [
                    {
                        "airport": criteria["origin"],
                        "airport_name": criteria["origin"],
                    },
                    {
                        "airport": criteria["destination"],
                        "airport_name": criteria["destination"],
                    },
                ],
                "departure_date_time": (
                    f"{criteria['depart_date']} {departure_time}"
                ),
                "arrival_date_time": (
                    f"{criteria['depart_date']} {arrival_time}"
                ),
                "price": price,
                "stops": stops,
                "checked_bags": 0,
                "carry_on_bags": 1,
                "duration_minutes": parse_duration_minutes(duration),
                "status": "Scheduled",
                "delay_minutes": 0,
                "legs": [],
                "layovers": layovers,
            }

            if stops > 0 and layovers:
                flight["route"] = [
                    {
                        "airport": criteria["origin"],
                        "airport_name": criteria["origin"],
                    },
                    {
                        "airport": layovers[0]["airport"],
                        "airport_name": layovers[0]["airport_name"],
                    },
                    {
                        "airport": criteria["destination"],
                        "airport_name": criteria["destination"],
                    },
                ]

            flights.append(flight)

            if len(flights) >= max_results:
                break

        except Exception:
            continue

    return flights


def click_button_by_aria(driver, label_contains: str):
    buttons = driver.find_elements(By.TAG_NAME, "button")

    for button in buttons:
        aria_label = button.get_attribute("aria-label") or ""
        text = button.text or ""

        if (
            label_contains.lower() in aria_label.lower()
            or label_contains.lower() in text.lower()
        ):
            if button.is_displayed() and button.is_enabled():
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    button,
                )
                driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
                return

    raise RuntimeError(f"Could not find button containing: {label_contains}")


def enter_airport_in_active_dialog(driver, airport_code: str):
    active = driver.switch_to.active_element

    active.send_keys(Keys.CONTROL, "a")
    active.send_keys(Keys.BACKSPACE)

    for char in airport_code:
        active.send_keys(char)
        time.sleep(0.2)

    time.sleep(2)

    active.send_keys(Keys.ARROW_DOWN)
    time.sleep(0.5)
    active.send_keys(Keys.ENTER)
    time.sleep(1)


def print_buttons(driver):
    buttons = driver.find_elements(By.TAG_NAME, "button")

    print("\nVISIBLE BUTTONS")
    print("---------------")

    for i, button in enumerate(buttons):
        try:
            if button.is_displayed():
                print(
                    i,
                    "TEXT:",
                    repr(button.text),
                    "| ARIA:",
                    repr(button.get_attribute("aria-label")),
                )
        except Exception:
            pass


def set_text_input(driver, label_contains: str, value: str):
    inputs = driver.find_elements(By.TAG_NAME, "input")

    candidates = []

    for element in inputs:
        aria_label = element.get_attribute("aria-label") or ""
        placeholder = element.get_attribute("placeholder") or ""

        if (
            label_contains.lower() in aria_label.lower()
            or label_contains.lower() in placeholder.lower()
        ):
            if element.is_displayed() and element.is_enabled():
                candidates.append(element)

    if not candidates:
        raise RuntimeError(f"No input found for {label_contains}")

    selected = candidates[0]

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        selected,
    )

    driver.execute_script("arguments[0].click();", selected)

    time.sleep(1)

    # Clear existing text
    selected.send_keys(Keys.CONTROL, "a")
    selected.send_keys(Keys.BACKSPACE)

    time.sleep(0.5)

    # Type airport code slowly
    for char in value:
        selected.send_keys(char)
        time.sleep(0.2)

    time.sleep(2)

    # Select first suggestion
    selected.send_keys(Keys.ARROW_DOWN)
    time.sleep(0.5)
    selected.send_keys(Keys.ENTER)

    time.sleep(1)


def search_google_flights(criteria: dict):
    print("Google Flights Selenium adapter called")

    origin = criteria["origin"]
    destination = criteria["destination"]

    url = (
        "https://www.google.com/travel/flights"
        f"?q=Flights%20from%20{origin}%20to%20{destination}"
    )

    try:
        with browser_session(headless=settings.SELENIUM_HEADLESS, keep_open=settings.KEEP_BROWSER_OPEN) as (driver, wait):
            driver.get(url)

            print("Loaded:", driver.title)
            print("Current URL:", driver.current_url)

            time.sleep(5)

            body_text = driver.find_element(By.TAG_NAME, "body").text

            parsed_results = parse_google_flights_text(
                body_text,
                criteria,
                max_results=settings.GOOGLE_FLIGHTS_MAX_RESULTS,
            )

            print(f"Parsed Google Flights results: {len(parsed_results)}")

            if settings.DEBUG_GOOGLE_FLIGHTS:
                print("BODY TEXT SAMPLE")
                print("----------------")
                print(body_text[:3000])

            return {
                "success": True,
                "source": "Google Flights",
                "page_title": driver.title,
                "current_url": driver.current_url,
                "results": parsed_results,
            }

    except Exception as e:
        print("Google Flights error:", e)

        return {
            "success": False,
            "source": "Google Flights",
            "error": str(e),
            "results": [],
        }