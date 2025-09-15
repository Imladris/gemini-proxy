# Changelog

## [0.1.0] - 2025-09-15

- 初始版本
  - 使用 FastAPI 暴露 OpenAI 兼容接口
  - 通过本地 Gemini CLI（由 `GEMINI_PATH` 配置）执行推理
  - 支持流式（SSE）与非流式响应
  - 请求/响应 JSONL 日志记录到 `proxy.log`，并启用日志轮转
  - 模型清单包含 `gemini-2.5-pro-preview-06-05`
# Changelog

## [0.1.0] - 2025-09-15
- Initial release
  - FastAPI proxy exposing OpenAI-compatible endpoints
  - Calls local Gemini CLI (configurable via GEMINI_PATH)
  - Supports streaming (SSE) and non-streaming responses
  - Request/response logging to `proxy.log`
  - Models list includes `gemini-2.5-pro-preview-06-05`
