from dotenv import load_dotenv
from lexmount import Lexmount
from playwright.sync_api import Playwright, sync_playwright

load_dotenv(override=True)


def run(playwright: Playwright) -> None:
    lm = Lexmount()

    print("Creating session with official proxy")
    with lm.sessions.create(official_proxy=True) as session:
        browser = playwright.chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]

        page.goto("https://example.com/", wait_until="domcontentloaded")
        print(f"Session ID: {session.id}")
        print(f"Page title: {page.title()}")
        page.screenshot(path="official_proxy_demo.png")
        print("Saved screenshot to official_proxy_demo.png")

        page.close()
        browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
