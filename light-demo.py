from dotenv import load_dotenv
from lexmount import Lexmount
from playwright.sync_api import sync_playwright

load_dotenv(override=True)


def main():
    """演示使用 chrome-light-docker 提取网页链接"""
    print("🔗 提取新闻链接演示")
    
    # 初始化 Lexmount 客户端
    lm = Lexmount()
    
    # 创建 chrome-light-docker 会话
    session = lm.sessions.create(browser_mode="chrome-light-docker")
    
    with sync_playwright() as playwright:
        # 连接到远程浏览器
        browser = playwright.chromium.connect_over_cdp(session.connect_url)
        page = browser.contexts[0].pages[0]
        
        # 访问新浪新闻
        page.goto("https://news.sina.cn/")
        
        # 提取所有链接
        links = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a[href]')).map(a => a.href);
        }''')
        
        # 保存到文件
        with open("links.txt", "w", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")
        
        print(f"✅ 已提取 {len(links)} 个链接，保存到: links.txt")
        
        page.close()
        browser.close()


if __name__ == "__main__":
    main()
