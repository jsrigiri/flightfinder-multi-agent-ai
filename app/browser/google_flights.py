from app.browser.selenium_client import browser_session


def search_google_flights(criteria: dict):
    """
    Phase 1:
    Open Google Flights and verify Selenium works.

    Phase 2:
    Extract actual flights.

    For now:
    Return mock fallback data if extraction is not implemented.
    """

    url = "https://www.google.com/travel/flights"

    try:
        with browser_session(headless=True) as (driver, wait):
            driver.get(url)

            page_title = driver.title

            return {
                "success": True,
                "source": "Google Flights",
                "page_title": page_title,
                "results": [],
            }

    except Exception as e:
        return {
            "success": False,
            "source": "Google Flights",
            "error": str(e),
            "results": [],
        }
        