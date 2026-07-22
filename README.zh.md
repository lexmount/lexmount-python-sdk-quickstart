# lexmount-python-sdk-quickstart

> 🇬🇧 [English](./README.md)

快速开始使用 Lexmount Python SDK 的示例项目。

---

## 📋 示例说明

### demo.py - 基础演示
- 访问 Lexmount 官网
- 验证页面标题
- 截图保存

### light-demo.py - 轻量浏览器演示
- 使用 `chrome-light-docker` 模式
- 访问新浪新闻
- 提取所有链接并保存到 `links.txt`

### extension_basic.py - 插件演示
- 上传 `test_extension.zip`
- 查看已上传插件列表
- 使用 `extension_ids` 创建浏览器会话

### proxy_demo.py - 代理演示
- 使用 `proxy` 参数创建浏览器会话
- 验证远端浏览器通过带认证的上游代理访问外网

### official_proxy_demo.py - 官方代理演示
- 使用 `official_proxy=True` 创建浏览器会话
- 验证远端浏览器可以使用 Lexmount 官方代理池

### inspect_url_demo.py - Inspect URL 演示
- 创建浏览器会话
- 打印 `inspect_url` 供用户手动打开检查
- 等待用户输入后再关闭会话

### session_targets.py - Session Targets 演示
- 创建浏览器会话
- 通过 SDK 查询 `/json` target 列表
- 打印每个 target 的 `inspectUrl`、页面 URL 和 websocket URL

### catalog_info.py - Catalog Info 演示
- 使用 `requirements.txt` 中的 SDK 版本
- 通过 `client.catalog_info()` 查询 public endpoint catalog
- 打印可用 region、host 和 endpoint IP

### context_basic.py - Context 描述演示
- 创建带 `description` 的 context
- 使用该 context 启动 `read_write` 会话
- 打印 context 展示名称和 ID

### context_list_get.py - Context 列表与详情演示
- 列出 context 并打印 `display_name`
- 获取指定 context 详情
- 存在 `description` 时打印描述

### context_fork.py - Context Fork 演示
- 传入一个已有的 source `context_id`
- 基于 source fork 出新的 context
- 打印 fork 后的新 id

### connection_demo.py - 直连 websocket 演示
- 根据 `LEXMOUNT_BASE_URL` 组装直连 websocket 地址
- 通过 `/connection?project_id=...&api_key=...` 连接
- 访问 `https://example.com` 并保存 `connection_demo.png`

### custom_image_demo.py - 自定义镜像演示
- 使用 `custom_image_id` 创建浏览器会话
- 支持从命令行传入 `--custom_image_id`
- 连接会话并验证浏览器可以打开页面

### window_size_demo.py - 窗口尺寸演示
- 使用 `window_size` 创建浏览器会话
- 支持从命令行传入 `--window_size`，默认 `1920,1080`
- 连接会话并打印初始 viewport

### wpt_demo.py - Web Platform Tests 演示
- 在 Lexmount 浏览器会话中打开 web-platform-tests runner
- 支持 `--count` 并发打开多个浏览器实例执行测试
- 支持 `--path` 指定要执行的 WPT 路径

### cpu_load_demo.py - CPU 负载演示
- 支持 `--count` 并发创建多个 Lexmount 浏览器会话
- 支持 `--pages` 控制每个会话打开的页面数量，默认 4 个
- 每个页面注入持续执行 `Math.sqrt(Math.random())` 的 JavaScript，提高浏览器 CPU 负载

---

## 🚀 快速开始

```bash
# 1. 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS 或 venv\Scripts\activate (Windows)

# 2. 安装依赖
pip install -r requirements.txt

# 3. 创建 .env 文件
cp .env.example .env
# 编辑 .env 填入实际的 API Key 和 Project ID
# office 测试环境可设置:
# LEXMOUNT_BASE_URL=https://apitest.local.lexmount.net

# 4. 运行示例
python3 demo.py              # 基础演示
python3 light_demo.py        # 轻量浏览器演示
python3 context_basic.py     # Context 描述演示
python3 context_list_get.py  # Context 列表与详情演示
python3 context_fork.py <context_id>  # Context Fork 演示
python3 extension_basic.py   # 插件演示
python3 proxy_demo.py        # 代理演示
python3 official_proxy_demo.py # 官方代理演示
python3 inspect_url_demo.py  # Inspect URL 演示
python3 session_targets.py   # Session targets 演示
python3 catalog_info.py      # Public endpoint catalog 演示
python3 connection_demo.py   # 直连 websocket 演示
python3 custom_image_demo.py --custom_image_id code.lexmount.net/neng/chrome:tag
python3 window_size_demo.py --window_size 1920,1080
python3 wpt_demo.py --count 2 --path /dom/historical.html
python3 cpu_load_demo.py --count 1 --pages 4 --duration-seconds 300
```
