from app.browser.google_flights import search_google_flights


def test_google_flights_page_opens():
    result = search_google_flights(
        {
            "origin": "SFO",
            "destination": "JFK",
        }
    )

    assert "success" in result
    assert "source" in result