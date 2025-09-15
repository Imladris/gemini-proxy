# Example Python Project

这是一个最小的 Python 包示例，包含一个命令行入口和单元测试。

要求:
- Python 3.8+

快速开始:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
python -m unittest discover -v
```

命令行用法:

```bash
python -m example_pkg.cli --name Alice
```


代理（将 OpenAI-style 请求适配为 geminicli）:

本项目包含 `proxy.py`，它实现了一个非常小的 Flask 应用，监听 POST /v1/chat/completions，将 OpenAI-style 的 `messages` 或 `prompt` 转换为对本地 `gemini-cli` 的调用，并返回 OpenAI 风格的 JSON 响应。

快速运行代理：

```bash
# 安装依赖
python -m pip install -r requirements.txt
```markdown
# Gemini-CLI FastAPI 代理

将 OpenAI-style 请求适配为本地 `gemini` / Gemini CLI 的代理服务，方便把 SillyTavern 或其他只支持 OpenAI API 的客户端接入本地 Gemini 模型。

主要功能
- FastAPI 应用，暴露 OpenAI 风格的端点（例如 `/v1/chat/completions` 和 `/chat/completions`）
- 支持流式（SSE/text-event-stream）和非流式响应
- 通过本地 Gemini CLI 进行推理（可通过 `GEMINI_PATH` 环境变量配置）
- 请求/响应记录到 `proxy.log`，默认启用日志轮转

要求
- Python 3.9+

快速开始

```bash
# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装运行时依赖（或使用 requirements.txt）
python -m pip install -U pip
python -m pip install fastapi uvicorn pydantic httpx

# 启动代理（示例：端口 7777）
GEMINI_PATH=/path/to/gemini python3 -m uvicorn proxy:app --host 127.0.0.1 --port 7777 --log-level info
```

示例请求（非流式）

```bash
curl -sS -X POST http://127.0.0.1:7777/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-2.5-pro-preview-06-05","messages":[{"role":"user","content":"你好"}]}'
```

示例请求（流式）

```bash
curl -N -X POST http://127.0.0.1:7777/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-2.5-pro-preview-06-05","stream":true,"messages":[{"role":"user","content":"写一首短诗"}]}'
```

打包与安装

构建 wheel / sdist（在项目根目录）：

```bash
python3 -m pip install --upgrade build
python3 -m build
# 产物位于 dist/
```

本地测试安装：

```bash
python3 -m venv /tmp/gp-venv && source /tmp/gp-venv/bin/activate
pip install dist/gemini_proxy-0.1.0-py3-none-any.whl
python -c "import proxy; print('proxy.app exists:', hasattr(proxy,'app'))"
```

更多信息请参阅 `CHANGELOG.md` 和 `RELEASE.md`。
```