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
- 显式开启 LightMount layout，并展示单会话 `enable_lightmount_resource` 开关
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
# 本地 macOS/Windows 终端缺少凭据时会自动打开浏览器登录。
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


## 凭据检查与浏览器登录

所有 demo 都会在调用 API 前检查 `LEXMOUNT_PROJECT_ID` 和 `LEXMOUNT_API_KEY`。读取的是**当前工作目录**的 `.env`，其中的值优先于已导出的环境变量；空值及模板占位值视为未配置。已有完整凭据时直接运行，不打开浏览器。

- 默认 API 为 `https://api.lexmount.com`，对应官网为 `https://browser.lexmount.com`。
- 在本地 **macOS / Windows 交互式终端**中缺少凭据时，自动打开系统浏览器登录并授权。批准后返回终端，demo 自动继续。
- 使用临时 `127.0.0.1` 回调和 PKCE，通过 HTTPS 用一次性 code 换取凭据。Project ID、API Key 和匹配的 API 地址成对写入 `.env`，保留其他配置。POSIX 下新写入文件仅当前用户可读写；Windows 下请用当前用户的目录访问权限保护项目。
- Linux、SSH、CI、非交互终端、无法打开浏览器或授权超时（3 分钟）时，程序退出并提示官网和手动配置方法；填写两个值后重跑。CI 也可直接设置两个环境变量而不创建 `.env`。
- 显式设置 `https://api.lexmount.cn` 时，授权使用 `https://browser.lexmount.cn`。其他自定义 API 地址保持不变，请从对应环境手动获取凭据，不会自动切换到 `.com`。
- 交换失败时不写入凭据；若授权期间修改了 `.env`，请重跑以免覆盖改动。不要提交 `.env`。

请在仓库目录执行各 demo，让它们共用同一个 `.env`。
