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

# 4. Run examples
python3 demo.py              # Basic demo
python3 light_demo.py        # Light browser demo
```
