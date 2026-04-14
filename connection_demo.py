from urllib.parse import urlencode, urlparse, urlunparse

from dotenv import load_dotenv

from lexmount import Lexmount
from playwright.sync_api import Playwright, sync_playwright

load_dotenv(override=True)


def build_connection_url(client: Lexmount) -> str:
    parsed = urlparse(client.base_url)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    query = urlencode(
        {
            "project_id": client.project_id,
            "api_key": client.api_key,
        }
    )
    return urlunparse((scheme, parsed.netloc, "/connection", "", query, ""))


def run(playwright: Playwright) -> None:
    client = Lexmount()
    connection_url = build_connection_url(client)

    print(f"connection_url: {connection_url}")

    browser = playwright.chromium.connect_over_cdp(connection_url)
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://example.com")
    page_title = page.title()
    assert page_title == "Example Domain", (
        "Page title is not 'Example Domain', "
        f"it is '{page_title}'"
    )
    page.screenshot(path="connection_demo.png")

    input("Press Enter to continue...")


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
