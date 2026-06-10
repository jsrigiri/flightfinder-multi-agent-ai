import os

from dotenv import load_dotenv

load_dotenv()

class Settings:

    # Debug
    DEBUG = os.getenv(
        "DEBUG",
        "false",
    ).lower() == "true"

    DEBUG_GOOGLE_FLIGHTS = os.getenv(
        "DEBUG_GOOGLE_FLIGHTS",
        "false",
    ).lower() == "true"

    # Ollama
    DISABLE_LLM = os.getenv(
        "DISABLE_LLM",
        "true",
    ).lower() == "true"

    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "llama3.2:1b",
    )

    # Selenium
    SELENIUM_HEADLESS = os.getenv(
        "SELENIUM_HEADLESS",
        "true",
    ).lower() == "true"

    KEEP_BROWSER_OPEN = os.getenv(
        "KEEP_BROWSER_OPEN",
        "false",
    ).lower() == "true"

    # Google Flights
    GOOGLE_FLIGHTS_MAX_RESULTS = int(
        os.getenv(
            "GOOGLE_FLIGHTS_MAX_RESULTS",
            "10",
        )
    )

    USE_LIVE_GOOGLE_FLIGHTS = os.getenv(
        "USE_LIVE_GOOGLE_FLIGHTS",
        "false",
    ).lower() == "true"


settings = Settings()