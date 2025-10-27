# Project Coding Rules (Non-Obvious Only)

- **Gemini CLI fallback strategies**: Always use the 6-command fallback pattern in [`src/gemini_proxy/services/gemini_service.py`](src/gemini_proxy/services/gemini_service.py:57-65) - different Gemini CLI versions require different argument formats
- **Service instantiation**: Use singleton pattern with `get_service()` functions, not direct class instantiation
- **Error handling**: Always use HTTPException for API errors, not generic exceptions
- **Configuration access**: Use global `config` instance, never access environment variables directly
- **Module imports**: Use relative imports within src/ package (e.g., `from ..config import config`)
- **Logging location**: Logs are written to `proxy.log` in project root, not src/ directory
- **Token counting**: Uses simple word splitting, not actual tokenization - be aware of this limitation
- **Output cleaning**: ASCII art and formatting characters are automatically removed by cleaning utilities