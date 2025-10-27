# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Build/Test Commands
- **Run tests**: `python -m unittest discover -v` (tests must be run from project root)
- **Install in development mode**: `python -m pip install -e .` (uses pyproject.toml)
- **Start proxy**: `GEMINI_PATH=/path/to/gemini python3 -m uvicorn src.gemini_proxy.main:app --host 127.0.0.1 --port 7777`

## Critical Project-Specific Patterns
- **Gemini CLI fallback strategies**: [`src/gemini_proxy/services/gemini_service.py`](src/gemini_proxy/services/gemini_service.py:57-65) implements 6 different command variations to handle different Gemini CLI versions
- **Logging location**: Logs go to `proxy.log` in project root, not in src/ directory as might be expected
- **Dual API endpoints**: Both `/v1/chat/completions` and `/chat/completions` are supported for backward compatibility
- **Token counting**: Uses simple word splitting in [`src/gemini_proxy/utils/response_utils.py`](src/gemini_proxy/utils/response_utils.py:123-136), not actual tokenization
- **Output cleaning**: Removes ASCII art and formatting characters in [`src/gemini_proxy/utils/cleaning.py`](src/gemini_proxy/utils/cleaning.py)

## Code Style & Architecture
- **Module imports**: Use relative imports within src/ package (e.g., `from ..config import config`)
- **Service pattern**: All services use singleton pattern with `get_service()` functions
- **Error handling**: HTTPException is preferred over generic exceptions for API errors
- **Configuration**: All config accessed via global `config` instance, not direct env var access

## Testing Gotchas
- **Test imports**: Tests import from `proxy` module (legacy) not from src/ package
- **Mock strategy**: Tests use extensive mocking of subprocess execution
- **Test data**: No test fixtures - all test data created inline