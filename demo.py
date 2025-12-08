from dotenv import load_dotenv

from lexmount import Lexmount
from playwright.sync_api import Playwright, sync_playwright

# Load environment variables first
load_dotenv(override=True)


def run(playwright: Playwright) -> None:
    # Initialize Lexmount client
    lm = Lexmount()  # Reads credentials from environment variables
    
    # Create a session on Lexmount
    session = lm.sessions.create()

    # Connect to the remote session
    chromium = playwright.chromium
    browser = chromium.connect_over_cdp(session.connect_url)
    context = browser.contexts[0]
    page = context.pages[0]

    # Execute Playwright actions on the remote browser tab
    page.goto("https://dev.lexmount.com/")
    page_title = page.title()
    assert page_title == "Lexmount Browser - AI-Powered Cloud Browser Service", f"Page title is not 'Lexmount Browser - AI-Powered Cloud Browser Service', it is '{page_title}'"
    page.screenshot(path="screenshot.png")

    page.close()
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)

