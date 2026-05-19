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


def run(playwright: Playwright, custom_image_id: str, region: Optional[str] = None) -> None:
    lm = build_client(region)

    with lm.sessions.create(custom_image_id=custom_image_id) as session:
        print(f"Session created with custom image: {session.session_id}")

        chromium = playwright.chromium
        browser = chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]

        page.goto("https://browser.lexmount.cn/")
        print(f"Page title: {page.title()}")

        page.close()
        browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Lexmount session with custom_image_id.")
    parser.add_argument(
        "--custom_image_id",
        required=True,
        help="Custom browser image id, for example code.lexmount.net/neng/chrome:tag.",
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
        run(playwright, custom_image_id=args.custom_image_id, region=args.region)
