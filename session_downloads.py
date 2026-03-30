from pathlib import Path
import time

from dotenv import load_dotenv
from lexmount import Lexmount
from playwright.sync_api import Playwright, sync_playwright

load_dotenv(override=True)

DOWNLOAD_URL = "https://proof.ovh.net/files/1Mb.dat"
DOWNLOAD_TIMEOUT_SECONDS = 60


def wait_for_completed_download(client: Lexmount, session_id: str, timeout_seconds: int = DOWNLOAD_TIMEOUT_SECONDS):
    deadline = time.monotonic() + timeout_seconds
    latest = None

    while time.monotonic() < deadline:
        latest = client.sessions.downloads.list(session_id)
        if latest.downloads and all(
            item.filename and not item.filename.endswith(".crdownload") and item.size > 0
            for item in latest.downloads
        ):
            return latest
        time.sleep(1)

    raise TimeoutError(f"Timed out waiting for completed downloads for session {session_id}")


def run(playwright: Playwright) -> None:
    client = Lexmount()

    with client.sessions.create() as session:
        print(f"session_id: {session.id}")
        browser = playwright.chromium.connect_over_cdp(session.connect_url)
        cdp = browser.new_browser_cdp_session()
        cdp.send("Browser.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": "/config/Downloads",
            "eventsEnabled": True,
        })
        context = browser.contexts[0]
        page = context.pages[0]

        page.set_content(f'<a id="dl" href="{DOWNLOAD_URL}" download>Download</a>')
        with page.expect_download() as download_info:
            page.locator("#dl").click()
        download = download_info.value
        print(f"suggested_filename: {download.suggested_filename}")

        downloads = wait_for_completed_download(client, session.id)
        print(f"download count: {downloads.summary['count']}")
        print(f"download total_size: {downloads.summary['total_size']}")
        for item in downloads.downloads:
            print(f"- {item.id}: {item.filename} ({item.size} bytes)")

        archive_bytes = client.sessions.downloads.archive(session.id)
        archive_path = Path(f"session-{session.id}-downloads.zip")
        archive_path.write_bytes(archive_bytes)
        print(f"archive_path: {archive_path}")
        print(f"archive_size: {archive_path.stat().st_size}")

        browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
