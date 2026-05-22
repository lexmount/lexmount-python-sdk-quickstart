import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from dotenv import load_dotenv
from lexmount import Lexmount
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

load_dotenv(override=True)

DEFAULT_WPT_RUNNER_URL = "https://wpt.live/tools/runner/index.html"
DEFAULT_TEST_PATH = "/dom/historical.html"
DEFAULT_TIMEOUT_MS = 180_000


def build_client(region: Optional[str]) -> Lexmount:
    if region:
        return Lexmount(region=region)
    return Lexmount()


def session_id(session) -> str:
    return getattr(session, "id", None) or getattr(session, "session_id", "")


def configure_runner(page, test_path: str, timeout_ms: int) -> None:
    page.goto(DEFAULT_WPT_RUNNER_URL, wait_until="domcontentloaded", timeout=timeout_ms)
    path_input = page.locator("#path")
    path_input.wait_for(state="visible", timeout=timeout_ms)
    page.wait_for_function(
        "document.querySelector('#path') && !document.querySelector('#path').disabled",
        timeout=timeout_ms,
    )
    path_input.fill(test_path)

    # Keep the quickstart fully automated. Reftests/manual tests often require manual decisions.
    page.locator("#ref").uncheck()
    page.locator("#man").uncheck()


def start_runner(page, timeout_ms: int) -> None:
    start_button = page.locator("button.toggleStart")
    start_button.wait_for(state="visible", timeout=timeout_ms)
    page.wait_for_function(
        "document.querySelector('button.toggleStart') && !document.querySelector('button.toggleStart').disabled",
        timeout=timeout_ms,
    )
    start_button.click()


def collect_summary(page) -> str:
    passed = page.locator("td.PASS").first.inner_text().strip()
    failed = page.locator("td.FAIL").first.inner_text().strip()
    timeouts = page.locator("td.TIMEOUT").first.inner_text().strip()
    errors = page.locator("td.ERROR").first.inner_text().strip()
    not_run = page.locator("td.NOTRUN").first.inner_text().strip()
    progress = page.locator(".progress-bar").first.inner_text().strip()
    return f"progress={progress} pass={passed} fail={failed} timeout={timeouts} error={errors} notrun={not_run}"


def run_one(index: int, region: Optional[str], test_path: str, timeout_ms: int) -> str:
    client = build_client(region)

    with sync_playwright() as playwright:
        with client.sessions.create() as session:
            sid = session_id(session)
            browser = playwright.chromium.connect_over_cdp(session.connect_url)
            try:
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else context.new_page()

                configure_runner(page, test_path, timeout_ms)
                start_runner(page, timeout_ms)

                try:
                    page.wait_for_function(
                        "Number(document.querySelector('.progress-bar')?.getAttribute('aria-valuemax')) > 0 && "
                        "document.querySelector('.progress-bar')?.getAttribute('aria-valuenow') === "
                        "document.querySelector('.progress-bar')?.getAttribute('aria-valuemax')",
                        timeout=timeout_ms,
                    )
                except PlaywrightTimeoutError:
                    return f"[{index}] session={sid} timed out {collect_summary(page)}"

                return f"[{index}] session={sid} completed {collect_summary(page)}"
            finally:
                browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run web-platform-tests from Lexmount browser sessions.")
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of concurrent Lexmount browser instances to open.",
    )
    parser.add_argument(
        "--path",
        default=DEFAULT_TEST_PATH,
        help=f"WPT path to run in the web runner. Default: {DEFAULT_TEST_PATH}",
    )
    parser.add_argument(
        "--region",
        default=None,
        help="Optional catalog region id, for example office-beijing. Omit to use the default region.",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=DEFAULT_TIMEOUT_MS,
        help="Navigation and WPT execution timeout in milliseconds.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.count <= 0:
        raise ValueError("--count must be greater than 0")
    if not args.path.startswith("/"):
        raise ValueError("--path must start with '/', for example /dom/historical.html")

    print(f"Starting {args.count} concurrent WPT run(s) for path {args.path}")
    with ThreadPoolExecutor(max_workers=args.count) as executor:
        futures = [
            executor.submit(run_one, index, args.region, args.path, args.timeout_ms)
            for index in range(1, args.count + 1)
        ]

        for future in as_completed(futures):
            print(future.result())


if __name__ == "__main__":
    main()
