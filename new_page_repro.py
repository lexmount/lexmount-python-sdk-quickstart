"""
Temporary repro script for multi-tab creation via Playwright CDP.

This script is intended to verify whether `context.new_page()` works
correctly for different browser modes.
"""
import argparse
from dotenv import load_dotenv

load_dotenv(override=True)

from lexmount import Lexmount
from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reproduce context.new_page() behavior for a given browser mode"
    )
    parser.add_argument(
        "--browser-mode",
        default="normal",
        choices=["normal", "light"],
        help="Browser mode to test (default: normal)",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=2,
        help="How many new pages to attempt creating (default: 2)",
    )
    args = parser.parse_args()

    client = Lexmount()
    session = client.sessions.create(browser_mode=args.browser_mode)
    print(f"session_id: {session.id}")
    print(f"browser_mode: {args.browser_mode}")
    print(f"connect_url: {session.connect_url}")

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(session.connect_url)
            try:
                context = browser.contexts[0] if browser.contexts else browser.new_context()

                print(f"existing_contexts: {len(browser.contexts)}")
                print(f"existing_pages: {len(context.pages)}")

                for index in range(args.pages):
                    try:
                        page = context.new_page()
                        print(f"new_page[{index}] ok: {page.url}")
                        page.close()
                    except Exception as error:
                        print(f"new_page[{index}] failed: {error}")
                        raise
            finally:
                browser.close()
    finally:
        if hasattr(session, "close"):
            session.close()


if __name__ == "__main__":
    main()
