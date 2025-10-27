# Project Documentation Rules (Non-Obvious Only)

- **Dual API endpoints**: Both `/v1/chat/completions` and `/chat/completions` are supported for backward compatibility
- **Legacy vs new structure**: Tests use legacy `proxy` module, while new code uses `src/gemini_proxy` package
- **Token counting**: Uses simple word splitting, not actual tokenization - this is a known limitation
- **Output cleaning**: Removes ASCII art and formatting characters automatically
- **Gemini CLI compatibility**: Supports 6 different command variations for different Gemini CLI versions
- **Configuration approach**: All config accessed via global `config` instance, not direct env vars
- **Service pattern**: Uses singleton pattern with `get_service()` functions for all services