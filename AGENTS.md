# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Critical Project-Specific Patterns
- **Gemini CLI fallback strategies**: [`src/gemini_proxy/services/gemini_service.py`](src/gemini_proxy/services/gemini_service.py:57-65) implements 6 different command variations to handle different Gemini CLI versions
- **Logging location**: Logs go to `proxy.log` in project root, not in src/ directory as might be expected
- **Dual API endpoints**: Both `/v1/chat/completions` and `/chat/completions` are supported for backward compatibility
- **Token counting**: Uses simple word splitting in [`src/gemini_proxy/utils/response_utils.py`](src/gemini_proxy/utils/response_utils.py:123-136), not actual tokenization
- **Legacy structure**: Tests import from `proxy` module (legacy) not from src/ package
- **Service pattern**: All services use singleton pattern with `get_service()` functions
- **Configuration**: All config accessed via global `config` instance, not direct env var access