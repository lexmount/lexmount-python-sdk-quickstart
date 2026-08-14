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
- Enable LightMount layout and show its per-session `enable_lightmount_resource` switch
- Visit Sina News
- Extract all links and save to `links.txt`

### extension_basic.py - Extension Demo
- Upload `test_extension.zip`
- List uploaded extensions
- Create a browser session with `extension_ids`

### proxy_demo.py - Proxy Demo
- Create a browser session with `proxy`
- Verify the remote browser can use authenticated upstream proxy

### official_proxy_demo.py - Official Proxy Demo
- Create a browser session with `official_proxy=True`
- Verify the remote browser can use the Lexmount official proxy pool

### inspect_url_demo.py - Inspect URL Demo
- Create a browser session
- Print the `inspect_url` for manual inspection
- Wait for user input before closing the session

### session_targets.py - Session Targets Demo
- Create a browser session
- Query `/json` targets through the SDK
- Print each target's `inspectUrl`, page URL, and websocket URL

### catalog_info.py - Catalog Info Demo
- Uses the SDK version from `requirements.txt`
- Query the public endpoint catalog through `client.catalog_info()`
- Print available regions, host, and endpoint IPs

### context_basic.py - Context Description Demo
- Create a context with `description`
- Start a `read_write` session with that context
- Print the context display name and ID

### context_list_get.py - Context List/Get Demo
- List contexts and print `display_name`
- Get details for a specific context
- Print `description` when present

### context_fork.py - Context Fork Demo
- Accept an existing source `context_id`
- Fork it into a new context
- Print the forked context id

### connection_demo.py - Direct Connection Demo
- Build a direct websocket URL from `LEXMOUNT_BASE_URL`
- Connect through `/connection?project_id=...&api_key=...`
- Visit `https://example.com` and save `connection_demo.png`

### custom_image_demo.py - Custom Image Demo
- Create a browser session with `custom_image_id`
- Accept `--custom_image_id` from the command line
- Connect to the session and verify the browser can open a page

### window_size_demo.py - Window Size Demo
- Create a browser session with `window_size`
- Accept `--window_size`, defaulting to `1920,1080`
- Connect to the session and print the initial viewport

### wpt_demo.py - Web Platform Tests Demo
- Open the web-platform-tests runner in Lexmount browser sessions
- Accept `--count` to run multiple concurrent browser instances
- Accept `--path` to choose the WPT path being tested

### cpu_load_demo.py - CPU Load Demo
- Create concurrent Lexmount browser sessions with `--count`
- Open multiple pages in each session with `--pages`, defaulting to 4
- Inject continuous `Math.sqrt(Math.random())` JavaScript to increase browser CPU load

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
python3 light_demo.py        # Light browser + per-session layout resource switch
python3 context_basic.py     # Context description demo
python3 context_list_get.py  # Context list/get demo
python3 context_fork.py <context_id>  # Context fork demo
python3 extension_basic.py   # Extension demo
python3 proxy_demo.py        # Proxy demo
python3 official_proxy_demo.py # Official proxy demo
python3 inspect_url_demo.py  # Inspect URL demo
python3 session_targets.py   # Session targets demo
python3 catalog_info.py      # Public endpoint catalog demo
python3 connection_demo.py   # Direct connection demo
python3 custom_image_demo.py --custom_image_id code.lexmount.net/neng/chrome:tag
python3 window_size_demo.py --window_size 1920,1080
python3 wpt_demo.py --count 2 --path /dom/historical.html
python3 cpu_load_demo.py --count 1 --pages 4 --duration-seconds 300
python3 session_downloads.py # Session downloads demo
```
