import argparse
import os
from typing import Optional

from dotenv import load_dotenv
from lexmount import Lexmount
from playwright.sync_api import Playwright, sync_playwright

load_dotenv(override=True)


def build_client(region: Optional[str]) -> Lexmount:
    if region:
        return Lexmount(region=region)
    return Lexmount()


def run(playwright: Playwright, window_size: str, region: Optional[str] = None) -> None:
    lm = build_client(region)

    with lm.sessions.create(browser_mode="normal", window_size=window_size) as session:
        print(f"Session created with window_size={window_size}: {session.session_id}")

        chromium = playwright.chromium
        browser = chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]

        print(f"Initial viewport: {page.viewport_size}")
        page.goto("https://browser.lexmount.cn/")
        print(f"Page title: {page.title()}")
        input("Press Enter to continue....")

        page.close()
        browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Lexmount session with window_size.")
    parser.add_argument(
        "--window_size",
        default=os.getenv("LEXMOUNT_WINDOW_SIZE", "1920,1080"),
        help="Browser window size in width,height format, default 1920,1080.",
    )
    parser.add_argument(
        "--region",
        default=None,
        help="Optional catalog region id, for example office-beijing. Omit to use the default region.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    with sync_playwright() as playwright:
        run(playwright, window_size=args.window_size, region=args.region)
