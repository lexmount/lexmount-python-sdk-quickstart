from dotenv import load_dotenv

from lexmount import Lexmount
from playwright.sync_api import Playwright, sync_playwright

# Load environment variables first
load_dotenv(override=True)


def run(playwright: Playwright) -> None:
    # Initialize Lexmount client
    
    connect_url = 'wss://apitest.local.lexmount.net/connection?project_id=11872275-f529-4b63-bbce-eba62c4257e1&api_key=SABG5D4NStyRFeFLLRNSEeyUIRABeLm5'
    # connect_url = 'wss://apitest.local.lexmount.net/connection?project_id=11872275-f529-4b63-bbce-eba62c4257e2&api_key=SABG5D4NStyRFeFLLRNSEeyUIRABeLm5'
    # connect_url = 'wss://apitest.local.lexmount.net/connection?project_id=11872275-f529-4b63-bbce-eba62c4257e1&api_key=SABG5D4NStyRFeFLLRNSEeyUIRABeLm1'
    print(connect_url)
    chromium = playwright.chromium
    browser = chromium.connect_over_cdp(connect_url)
    context = browser.contexts[0]
    page = context.pages[0]

    # Execute Playwright actions on the remote browser tab
    page.goto("https://browser.lexmount.cn/")
    page_title = page.title()
    assert page_title == "Lexmount Browser - AI-Powered Cloud Browser Service", f"Page title is not 'Lexmount Browser - AI-Powered Cloud Browser Service', it is '{page_title}'"
    page.screenshot(path="screenshot.png")
    input("\n   Press Enter to continue...")

    # page.close()
    # browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)

