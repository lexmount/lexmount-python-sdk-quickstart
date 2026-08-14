from dotenv import load_dotenv
from lexmount import Lexmount
from playwright.sync_api import Playwright, sync_playwright

# Load environment variables first
load_dotenv(override=True)


def run(playwright: Playwright) -> None:
    """演示使用 chrome-light-docker 提取网页链接"""
    print("🔗 提取新闻链接演示")
    
    # Initialize Lexmount client
    lm = Lexmount()  # Reads credentials from environment variables
    
    # Create a session with chrome-light-docker
    with lm.sessions.create(
        browser_mode="light",
        # Set False to disable MOLI_RESOURCE for only this Light session.
        enable_lightmount_resource=True,
    ) as session:
    
        # Connect to the remote session
        chromium = playwright.chromium
        browser = chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]
        
        # Execute Playwright actions on the remote browser tab
        page.goto("https://news.sina.cn/")
        
        # Extract all links
        links = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a[href]')).map(a => a.href);
        }''')
        
        # Save to file
        with open("links.txt", "w", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")
        
        print(f"✅ 已提取 {len(links)} 个链接，保存到: links.txt")
        
        page.close()
        browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
