"""
Basic extension workflow example.

This example demonstrates:
- Uploading a browser extension zip/crx
- Listing uploaded extensions
- Creating a session with extension_ids
"""
from pathlib import Path

from dotenv import load_dotenv
from lexmount import Lexmount, set_log_level
from playwright.sync_api import sync_playwright

load_dotenv(override=True)
set_log_level("WARNING")

client = Lexmount()


def main():
    base_dir = Path(__file__).resolve().parent.parent
    extension_zip = base_dir / "test_extension.zip"

    print("=" * 60)
    print("Extension Management - Basic Demo")
    print("=" * 60)

    if not extension_zip.exists():
        print(f"   ✗ test_extension.zip not found: {extension_zip}")
        return

    try:
        print("\n1. Upload extension...")
        extension = client.extensions.upload(str(extension_zip), name="quickstart-extension")
        print(f"   ✓ Uploaded extension: {extension.id}")

        print("\n2. List extensions...")
        extensions = client.extensions.list(limit=10)
        print(f"   ✓ Found {len(extensions)} extension(s)")
        for item in extensions:
            print(f"      - {item.id}: {item.name}")

        print("\n3. Create session with extension...")
        with client.sessions.create(
            browser_mode="normal",
            extension_ids=[extension.id],
        ) as session:
            print(f"   ✓ Session created: {session.id}")
            print(f"   ✓ Inspect URL: {session.inspect_url}")

            with sync_playwright() as playwright:
                browser = playwright.chromium.connect_over_cdp(session.connect_url)
                context = browser.contexts[0]
                page = context.pages[0]
                page.goto("https://www.baidu.com/")
                print("   ✓ Browser connected successfully")
                input("\n   Press Enter to close session...")

    except Exception as e:
        print(f"   ✗ Failed: {e}")


if __name__ == "__main__":
    main()
