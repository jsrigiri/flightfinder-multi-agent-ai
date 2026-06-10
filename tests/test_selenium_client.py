from app.browser.selenium_client import browser_session


def test_browser_session_opens_page():
    with browser_session(headless=True) as (driver, wait):
        driver.get("data:text/html,<html><title>FlightFinder Test</title><body>Hello</body></html>")

        assert "FlightFinder Test" in driver.title