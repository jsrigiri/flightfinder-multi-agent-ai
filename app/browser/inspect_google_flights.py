from selenium.webdriver.common.by import By

from app.browser.selenium_client import browser_session


with browser_session(headless=False) as (driver, wait):
    driver.get("https://www.google.com/travel/flights")

    print("TITLE:", driver.title)
    print("URL:", driver.current_url)

    inputs = driver.find_elements(By.TAG_NAME, "input")
    buttons = driver.find_elements(By.TAG_NAME, "button")

    print("\nINPUTS")
    print("------")
    for i, element in enumerate(inputs):
        print(
            i,
            element.get_attribute("aria-label"),
            element.get_attribute("placeholder"),
            element.get_attribute("value"),
        )

    print("\nBUTTONS")
    print("-------")
    for i, element in enumerate(buttons[:50]):
        print(
            i,
            element.text,
            element.get_attribute("aria-label"),
        )

    input("\nPress Enter to close...")