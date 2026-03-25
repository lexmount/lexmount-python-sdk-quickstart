import os

from dotenv import load_dotenv
from lexmount import Lexmount
from playwright.sync_api import Playwright, sync_playwright

load_dotenv(override=True)


def build_proxy_config() -> dict:
    server = os.getenv("LEXMOUNT_PROXY_SERVER", "").strip()
    if not server:
        raise RuntimeError("LEXMOUNT_PROXY_SERVER is required for proxy_demo.py")

    return {
        "type": "external",
        "server": server,
        "username": os.getenv("LEXMOUNT_PROXY_USERNAME", ""),
        "password": os.getenv("LEXMOUNT_PROXY_PASSWORD", ""),
    }


def run(playwright: Playwright) -> None:
    lm = Lexmount()
    proxy = build_proxy_config()

    print("Creating session with proxy:")
    print(f"  server: {proxy['server']}")
    print(f"  username set: {'yes' if proxy['username'] else 'no'}")

    with lm.sessions.create(proxy=proxy) as session:
        chromium = playwright.chromium
        browser = chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]

        page.goto("https://example.com/", wait_until="domcontentloaded")
        print(f"Session ID: {session.id}")
        print(f"Page title: {page.title()}")
        page.screenshot(path="proxy_demo.png")
        print("Saved screenshot to proxy_demo.png")

        page.close()
        browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
