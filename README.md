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

### context_fork.py - Context Fork Demo
- Create a source context
- Fork it into a new context
- Query the forked context details
- Clean up both source and forked contexts

### connection_demo.py - Direct Connection Demo
- Build a direct websocket URL from `LEXMOUNT_BASE_URL`
- Connect through `/connection?project_id=...&api_key=...`
- Visit `https://example.com` and save `connection_demo.png`

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
python3 context_fork.py      # Context fork demo
python3 extension_basic.py   # Extension demo
python3 proxy_demo.py        # Proxy demo
python3 inspect_url_demo.py  # Inspect URL demo
python3 connection_demo.py   # Direct connection demo
python3 session_downloads.py # Session downloads demo
```
