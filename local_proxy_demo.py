"""Use the SDK machine's network and DNS from a normal cloud browser."""

import argparse
import os
from typing import Optional
from urllib.parse import urlsplit

from lexmount import Lexmount
from playwright.sync_api import sync_playwright
from quickstart_auth import prepare_demo


def run(target: str, region: Optional[str] = None) -> None:
    url = urlsplit(target)
    if url.scheme not in ("http", "https") or not url.hostname:
        raise ValueError("The local proxy demo requires an HTTP(S) URL.")

    with Lexmount(region=region) as client:
        # The connector uses local OS/VPN DNS and stays alive through browser work.
        with client.tunnels.open() as tunnel:
            print(f"Local tunnel ready in region {tunnel.region_id}")
            with client.sessions.create(
                browser_mode="normal",
                proxy={"type": "local", "tunnel_id": tunnel.id},
            ) as session:
                print(f"Session created: {session.id}")
                with sync_playwright() as playwright:
                    browser = playwright.chromium.connect_over_cdp(session.connect_url)
                    try:
                        if not browser.contexts:
                            raise RuntimeError("No browser context available after connecting.")
                        context = browser.contexts[0]
                        page = context.pages[0] if context.pages else context.new_page()
                        page.goto(target, wait_until="domcontentloaded", timeout=60_000)
                        print(f"Page title: {page.title()}")
                        page.screenshot(path="local_proxy_demo.png")
                        print("Saved screenshot to local_proxy_demo.png")
                    finally:
                        browser.close()
            # Session context exits before the tunnel context, including on errors.


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Internal HTTP(S) URL; defaults to LEXMOUNT_LOCAL_PROXY_URL in .env.")
    parser.add_argument("--region", help="Catalog region ID; defaults to LEXMOUNT_REGION in .env.")
    args = parser.parse_args()
    prepare_demo()
    target = args.url or os.getenv("LEXMOUNT_LOCAL_PROXY_URL", "").strip()
    if not target:
        parser.error("Set LEXMOUNT_LOCAL_PROXY_URL or pass --url with an HTTP(S) URL reachable from this machine.")
    run(target, args.region or os.getenv("LEXMOUNT_REGION", "").strip() or None)


if __name__ == "__main__":
    main()
