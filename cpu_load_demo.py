import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from dotenv import load_dotenv
from lexmount import Lexmount
from playwright.sync_api import sync_playwright

load_dotenv(override=True)

DEFAULT_URL = "https://browser.lexmount.cn/"
DEFAULT_PAGES_PER_SESSION = 4
DEFAULT_DURATION_SECONDS = 300
CPU_LOAD_SCRIPT = """
() => {
  window.__lexmountCpuLoadStarted = true;
  while (true) {
    Math.sqrt(Math.random());
  }
}
"""


def build_client(region: Optional[str]) -> Lexmount:
    if region:
        return Lexmount(region=region)
    return Lexmount()


def session_id(session) -> str:
    return getattr(session, "id", None) or getattr(session, "session_id", "")


def run_one(index: int, region: Optional[str], url: str, pages: int, duration_seconds: int) -> str:
    client = build_client(region)

    with sync_playwright() as playwright:
        with client.sessions.create() as session:
            sid = session_id(session)
            browser = playwright.chromium.connect_over_cdp(session.connect_url)
            try:
                context = browser.contexts[0]
                opened_pages = []
                for page_index in range(1, pages + 1):
                    page = context.pages[0] if page_index == 1 and context.pages else context.new_page()
                    page.goto(url, wait_until="domcontentloaded")
                    page.evaluate(CPU_LOAD_SCRIPT)
                    opened_pages.append(page)
                    print(f"[{index}] session={sid} page={page_index} cpu load started")

                time.sleep(duration_seconds)
                return f"[{index}] session={sid} completed pages={len(opened_pages)} duration={duration_seconds}s"
            finally:
                browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run CPU load pages in Lexmount browser sessions.")
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of concurrent Lexmount browser sessions to create.",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=DEFAULT_PAGES_PER_SESSION,
        help="Number of pages to open per session. Default: 4.",
    )
    parser.add_argument(
        "--duration-seconds",
        type=int,
        default=DEFAULT_DURATION_SECONDS,
        help="How long to keep the CPU load running before closing sessions.",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"Page URL to open before injecting CPU load. Default: {DEFAULT_URL}",
    )
    parser.add_argument(
        "--region",
        default=None,
        help="Optional catalog region id, for example office-beijing. Omit to use the default region.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.count <= 0:
        raise ValueError("--count must be greater than 0")
    if args.pages <= 0:
        raise ValueError("--pages must be greater than 0")
    if args.duration_seconds <= 0:
        raise ValueError("--duration-seconds must be greater than 0")

    print(
        f"Starting CPU load: sessions={args.count}, pages_per_session={args.pages}, "
        f"duration={args.duration_seconds}s, url={args.url}"
    )
    with ThreadPoolExecutor(max_workers=args.count) as executor:
        futures = [
            executor.submit(run_one, index, args.region, args.url, args.pages, args.duration_seconds)
            for index in range(1, args.count + 1)
        ]

        for future in as_completed(futures):
            print(future.result())


if __name__ == "__main__":
    main()
