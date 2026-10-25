import argparse
import os
from typing import Optional

from quickstart_auth import load_environment, prepare_demo
from lexmount import Lexmount
from playwright.sync_api import Playwright, sync_playwright

load_environment()


def build_client(region: Optional[str]) -> Lexmount:
    if region:
        return Lexmount(region=region)
    return Lexmount()


def target_site() -> str:
    base_url = os.environ.get("LEXMOUNT_BASE_URL", "").rstrip("/")
    if base_url == "https://api.lexmount.cn":
        return "https://browser.lexmount.cn/"
    return "https://browser.lexmount.com/"


def run(playwright: Playwright, region: Optional[str] = None) -> None:
    lm = build_client(region)

    with lm.sessions.create() as session:
        chromium = playwright.chromium
        browser = chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]

        page.goto(target_site(), wait_until="domcontentloaded")
        page_title = page.title()
        assert "Lexmount" in page_title, f"Unexpected page title: {page_title}"
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
    prepare_demo()
    with sync_playwright() as playwright:
        run(playwright, region=args.region)
