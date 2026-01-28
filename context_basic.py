"""
Basic context operations example.

This example demonstrates:
- Creating a session with context (read_write mode)
"""
from lexmount import Lexmount, ContextNotFoundError, set_log_level
from dotenv import load_dotenv
from pathlib import Path
import argparse
import sys
from playwright.sync_api import Playwright, sync_playwright

load_dotenv(override=True)

# Set logging to DEBUG to see detailed request/response
set_log_level("WARNING")

client = Lexmount()

def main():
    """Demonstrate basic context operations."""
    parser = argparse.ArgumentParser(description="Context management basic operations")
    parser.add_argument("--context-id", help="Use this context ID directly; if omitted, create a new context")
    args = parser.parse_args()

    print("=" * 60)
    print("Context Management - Basic Operations")
    print("=" * 60)

    try:
        if args.context_id:
            context_id = args.context_id
            print(f"\n1. Using existing context ID: {context_id}")
        else:
            context = client.contexts.create(
                metadata={
                    "user": "demo_user",
                    "environment": "development",
                    "created_by": "example_script"
                }
            )
            context_id = context.id

        with sync_playwright() as playwright:
            with client.sessions.create(context={"id": context_id, "mode": "read_write"}) as session:
                try:                
                    chromium = playwright.chromium
                    browser = chromium.connect_over_cdp(session.connect_url)
                    context = browser.contexts[0]
                    page = context.pages[0]
                    page.goto("https://www.baidu.com/")
                    print(f"   ✓ Context created with ID: {context_id}")
                    input("\n   Press Enter to continue...")
                except Exception as e:
                    print(f"   ✗ Failed to connect to the remote session: {e}")
                    return
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return

if __name__ == "__main__":
    main()
