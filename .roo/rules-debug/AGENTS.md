# Project Debug Rules (Non-Obvious Only)

- **Log location**: Check `proxy.log` in project root for request/response logs, not in src/ directory
- **Gemini CLI debugging**: The service tries 6 different command variations - check logs for which one succeeded
- **Test debugging**: Tests use legacy `proxy` module imports, not the new src/ package structure
- **Subprocess debugging**: Gemini CLI execution uses extensive subprocess mocking in tests
- **Error handling**: API errors use HTTPException with detailed error messages in response
- **Timeout debugging**: Both request timeout (60s) and Gemini CLI timeout (30s) are configurable
- **Stream debugging**: Stream responses use SSE format with chunked content delivery