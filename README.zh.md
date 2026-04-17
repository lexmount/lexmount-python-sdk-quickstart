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

### inspect_url_demo.py - Inspect URL 演示
- 创建浏览器会话
- 打印 `inspect_url` 供用户手动打开检查
- 等待用户输入后再关闭会话

### session_targets.py - Session Targets 演示
- 创建浏览器会话
- 通过 SDK 查询 `/json` target 列表
- 打印每个 target 的 `inspectUrl`、页面 URL 和 websocket URL

### context_fork.py - Context Fork 演示
- 传入一个已有的 source `context_id`
- 基于 source fork 出新的 context
- 打印 fork 后的新 id

### connection_demo.py - 直连 websocket 演示
- 根据 `LEXMOUNT_BASE_URL` 组装直连 websocket 地址
- 通过 `/connection?project_id=...&api_key=...` 连接
- 访问 `https://example.com` 并保存 `connection_demo.png`

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
python3 context_fork.py <context_id>  # Context Fork 演示
python3 extension_basic.py   # 插件演示
python3 proxy_demo.py        # 代理演示
python3 inspect_url_demo.py  # Inspect URL 演示
python3 session_targets.py   # Session targets 演示
python3 connection_demo.py   # 直连 websocket 演示
```
