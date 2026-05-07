# lexmount-python-sdk-quickstart

> 🇨🇳 [中文版](./README.zh.md)

Quick start examples for Lexmount Python SDK.

---

## 📋 Examples

### demo.py - Basic Demo
- Visit Lexmount website
- Verify page title
- Take screenshot

### light-demo.py - Light Browser Demo
- Use `chrome-light-docker` mode
- Visit Sina News
- Extract all links and save to `links.txt`

### extension_basic.py - Extension Demo
- Upload `test_extension.zip`
- List uploaded extensions
- Create a browser session with `extension_ids`

### proxy_demo.py - Proxy Demo
- Create a browser session with `proxy`
- Verify the remote browser can use authenticated upstream proxy

### inspect_url_demo.py - Inspect URL Demo
- Create a browser session
- Print the `inspect_url` for manual inspection
- Wait for user input before closing the session

### session_targets.py - Session Targets Demo
- Create a browser session
- Query `/json` targets through the SDK
- Print each target's `inspectUrl`, page URL, and websocket URL

### catalog_info.py - Catalog Info Demo
- Uses `lexmount==0.5.0`
- Query the public endpoint catalog through `client.catalog_info()`
- Print available regions, host, and endpoint IPs

### context_fork.py - Context Fork Demo
- Accept an existing source `context_id`
- Fork it into a new context
- Print the forked context id

### connection_demo.py - Direct Connection Demo
- Build a direct websocket URL from `LEXMOUNT_BASE_URL`
- Connect through `/connection?project_id=...&api_key=...`
- Visit `https://example.com` and save `connection_demo.png`

### new_page_repro.py - new_page Repro Demo
- Create a session in `normal` or `light` mode
- Connect over CDP with Playwright
- Attempt `context.new_page()` multiple times and print the result

### session_downloads.py - Session Downloads Demo
- Explicitly configure `Browser.setDownloadBehavior` to `/config/Downloads`
- Trigger a file download in the remote browser
- Query the session downloads list via SDK
- Fetch the session downloads zip via SDK

---

## 🚀 Quick Start

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS or venv\Scripts\activate (Windows)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env and fill in your actual API Key and Project ID
# For office test environment:
# LEXMOUNT_BASE_URL=https://apitest.local.lexmount.net

# 4. Run examples
python3 demo.py              # Basic demo
python3 light_demo.py        # Light browser demo
python3 context_fork.py <context_id>  # Context fork demo
python3 extension_basic.py   # Extension demo
python3 proxy_demo.py        # Proxy demo
python3 inspect_url_demo.py  # Inspect URL demo
python3 session_targets.py   # Session targets demo
python3 catalog_info.py      # Public endpoint catalog demo
python3 connection_demo.py   # Direct connection demo
python3 new_page_repro.py --browser-mode normal  # Reproduce new_page issue
python3 session_downloads.py # Session downloads demo
```
