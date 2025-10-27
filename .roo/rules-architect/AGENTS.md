# Project Architecture Rules (Non-Obvious Only)

- **Gemini CLI fallback strategy**: The service implements 6 different command variations to handle different Gemini CLI versions - this is critical for compatibility
- **Dual API endpoints**: Both `/v1/chat/completions` and `/chat/completions` are maintained for backward compatibility
- **Legacy transition**: Tests still use legacy `proxy` module while new code uses `src/gemini_proxy` package structure
- **Singleton service pattern**: All services use singleton pattern with `get_service()` functions, not direct instantiation
- **Configuration centralization**: All config accessed via global `config` instance, never directly from environment variables
- **Token counting limitation**: Uses simple word splitting instead of actual tokenization - this is a known architectural trade-off
- **Logging strategy**: Logs go to `proxy.log` in project root, separate from source code directory
- **Error handling approach**: HTTPException preferred over generic exceptions for all API errors