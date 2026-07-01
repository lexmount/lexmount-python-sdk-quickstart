import argparse
from typing import Optional

from dotenv import load_dotenv
from lexmount import Lexmount
from playwright.sync_api import Playwright, sync_playwright

load_dotenv(override=True)


def build_client(region: Optional[str]) -> Lexmount:
    if region:
        return Lexmount(region=region)
    return Lexmount()


def run(playwright: Playwright, region: Optional[str] = None) -> None:
    lm = build_client(region)

    with lm.sessions.create() as session:
        chromium = playwright.chromium
        browser = chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]

        page.goto("https://browser.lexmount.cn/")
        page_title = page.title()
        assert "Lexmount Browser" in page_title, f"Unexpected page title: {page_title}"
        page.screenshot(path="screenshot.png")
        input("Press Enter to continue....")

        page.close()
        browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Lexmount Playwright quickstart demo.")
    parser.add_argument(
        "--region",
        default=None,
        help="Optional catalog region id, for example office-beijing. Omit to use the default region.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    with sync_playwright() as playwright:
        run(playwright, region=args.region)
