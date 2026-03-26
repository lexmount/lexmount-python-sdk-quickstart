from pathlib import Path

from dotenv import load_dotenv
from lexmount import Lexmount
from playwright.sync_api import Playwright, sync_playwright

load_dotenv(override=True)


def run(playwright: Playwright) -> None:
    client = Lexmount()

    with client.sessions.create() as session:
        browser = playwright.chromium.connect_over_cdp(session.connect_url)
        cdp = browser.new_browser_cdp_session()
        cdp.send("Browser.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": "/config/Downloads",
            "eventsEnabled": True,
        })
        context = browser.contexts[0]
        page = context.pages[0]

        page.goto("https://file-examples.com/index.php/sample-documents-download/")
        with page.expect_download() as download_info:
            page.get_by_role("link", name="Download sample DOC file").click()
        download_info.value

        downloads = client.sessions.downloads.list(session.id)
        print(f"download count: {downloads.summary['count']}")
        for item in downloads.downloads:
            print(f"- {item.id}: {item.filename} ({item.size} bytes)")

        archive_bytes = client.sessions.downloads.archive(session.id)
        Path(f"session-{session.id}-downloads.zip").write_bytes(archive_bytes)

        browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
