# Gemini-CLI FastAPI 代理

将 OpenAI-style 请求适配为本地 `gemini` / Gemini CLI 的代理服务，方便把 SillyTavern 或其他只支持 OpenAI API 的客户端接入本地 Gemini 模型。

## 🚀 主要功能

- **OpenAI 兼容 API** - 暴露 OpenAI 风格的端点（`/v1/chat/completions`、`/chat/completions`、`/v1/models`、`/models`、`/health`）
- **流式和非流式响应** - 支持 SSE/text-event-stream 和标准 JSON 响应
- **模块化架构** - 清晰的分层设计，易于维护和扩展
- **本地 Gemini CLI 集成** - 通过本地 Gemini CLI 进行推理（可通过 `GEMINI_PATH` 环境变量配置）
- **结构化日志记录** - 请求/响应记录到 `proxy.log`，默认启用日志轮转
- **配置管理** - 支持环境变量配置，类型安全的配置访问

## 🏗️ 项目架构

```
gemini-proxy/
├── src/
│   └── gemini_proxy/
│       ├── __init__.py
│       ├── main.py              # FastAPI 应用入口
│       ├── config.py            # 配置管理
│       ├── models.py            # Pydantic 数据模型
│       ├── routes/              # 路由层
│       │   ├── __init__.py
│       │   ├── health.py        # 健康检查路由
│       │   ├── models.py        # 模型列表路由
│       │   └── chat.py          # 聊天补全路由
│       ├── services/            # 服务层
│       │   ├── __init__.py
│       │   ├── gemini_service.py # Gemini CLI 服务
│       │   └── logging_service.py # 日志服务
│       └── utils/               # 工具类
│           ├── __init__.py
│           ├── response_utils.py # 响应构建工具
│           ├── validation.py     # 数据验证工具
│           └── cleaning.py       # 输出清理工具
├── tests/                       # 测试目录
├── examples/                    # 使用示例
├── pyproject.toml              # 项目配置
└── README.md                   # 项目文档
```

## 📋 要求

- Python 3.9+
- 本地安装的 Gemini CLI（可通过 `GEMINI_PATH` 环境变量配置路径）

## 🚀 快速开始

### 方法一：从源码运行

```bash
# 克隆项目
git clone https://github.com/Imladris/gemini-proxy.git
cd gemini-proxy

# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
python -m pip install -U pip
python -m pip install -e .

# 启动代理服务
GEMINI_PATH=/path/to/gemini python3 -m uvicorn src.gemini_proxy.main:app --host 127.0.0.1 --port 7777 --log-level info
```

### 方法二：使用命令行脚本

```bash
# 安装后可直接使用 proxy 命令
GEMINI_PATH=/path/to/gemini proxy --host 127.0.0.1 --port 7777
```

### 方法三：从 PyPI 安装（未来版本）

```bash
pip install gemini-proxy
GEMINI_PATH=/path/to/gemini proxy
```

## ⚙️ 配置选项

### 环境变量

| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| `GEMINI_PATH` | `/opt/homebrew/bin/gemini` | Gemini CLI 可执行文件路径 |
| `HOST` | `127.0.0.1` | 服务器监听地址 |
| `PORT` | `7777` | 服务器监听端口 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `LOG_FILE` | `proxy.log` | 日志文件路径 |
| `MAX_LOG_SIZE` | `5242880` | 日志文件最大大小（5MB） |
| `LOG_BACKUP_COUNT` | `5` | 日志备份文件数量 |
| `REQUEST_TIMEOUT` | `60.0` | 请求超时时间（秒） |
| `GEMINI_TIMEOUT` | `30.0` | Gemini CLI 执行超时时间（秒） |

## 📡 API 端点

### 健康检查
```bash
curl http://127.0.0.1:7777/health
```

### 获取模型列表
```bash
curl http://127.0.0.1:7777/v1/models
# 或
curl http://127.0.0.1:7777/models
```

### 聊天补全（非流式）
```bash
curl -sS -X POST http://127.0.0.1:7777/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-local",
    "messages": [
      {"role": "user", "content": "你好，请用中文回答"}
    ]
  }'
```

### 聊天补全（流式）
```bash
curl -N -X POST http://127.0.0.1:7777/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-local",
    "stream": true,
    "messages": [
      {"role": "user", "content": "写一首关于秋天的短诗"}
    ]
  }'
```

## 🧪 测试

运行单元测试：

```bash
python -m unittest discover -v
```

## 📦 打包与发布

### 构建包
```bash
python -m pip install --upgrade build
python -m build
# 产物位于 dist/ 目录
```

### 本地测试安装
```bash
python3 -m venv /tmp/gp-venv && source /tmp/gp-venv/bin/activate
pip install dist/gemini_proxy-0.2.0-py3-none-any.whl
python -c "from src.gemini_proxy.main import app; print('App imported successfully')"
```

## 🔧 开发

### 项目结构说明

- **`config.py`** - 配置管理，支持环境变量和默认值
- **`models.py`** - 数据模型定义，使用 Pydantic 进行验证
- **`routes/`** - API 路由处理，分离不同端点的逻辑
- **`services/`** - 业务逻辑服务，包括 Gemini CLI 执行和日志记录
- **`utils/`** - 工具函数，包括响应构建、数据验证和输出清理

### 添加新功能

1. 在相应的模块中添加功能
2. 更新路由以暴露新的端点
3. 添加相应的数据模型
4. 编写单元测试
5. 更新文档

## 📄 许可证

[添加许可证信息]

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请通过以下方式联系：
- 创建 GitHub Issue
- [其他联系方式]

---

更多信息请参阅 [`CHANGELOG.md`](CHANGELOG.md) 和 [`ARCHITECTURE.md`](ARCHITECTURE.md)。