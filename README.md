# lexmount-python-sdk-quickstart

快速开始使用 Lexmount Python SDK 的示例项目。


## 🚀 快速开始


```bash
# 1. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS 或 venv\Scripts\activate (Windows)

# 2. 安装依赖
pip install -r requirements.txt

# 3. 创建 .env 文件
cat > .env << EOF
LEXMOUNT_API_KEY=your-api-key-here
LEXMOUNT_PROJECT_ID=your-project-id-here
LEXMOUNT_BASE_URL=https://api.lexmount.net
EOF

# 4. 运行示例
python main.py
```