"""
Gemini-CLI reverse proxy for SillyTavern / OpenAI-compatible clients.

This is a compact, robust FastAPI implementation that:
- exposes health, models, and chat completion endpoints compatible with SillyTavern/OpenAI
- runs a local Gemini CLI executable (configurable via GEMINI_PATH)
- cleans CLI output and returns an OpenAI-shaped JSON response

Usage:
    GEMINI_PATH=/path/to/gemini python3 -m uvicorn proxy:app --host 0.0.0.0 --port 8888
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import os
import uuid
import logging
from logging.handlers import RotatingFileHandler
import time
import shlex
import json

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('gemini-proxy')

# Log file path (define before handlers)
LOG_PATH = os.path.join(os.path.dirname(__file__), 'proxy.log')

# Attach rotating file handler for request/response logs
try:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
except Exception:
    pass

file_handler = RotatingFileHandler(LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# App + CORS
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """Middleware that logs incoming requests and outgoing responses to a file.

    Each entry is a JSON line with: timestamp, id, method, path, request_body, status_code, response_body_preview, duration.
    """
    req_id = uuid.uuid4().hex
    ts = int(time.time())
    try:
        body_bytes = await request.body()
        request_text = body_bytes.decode(errors='ignore') if body_bytes else ''
    except Exception:
        request_text = ''

    start = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        # Log the exception as a response
        duration = time.time() - start
        entry = {
            'ts': ts,
            'id': req_id,
            'method': request.method,
            'path': str(request.url.path),
            'request': request_text,
            'status': 500,
            'response': str(e),
            'duration': duration,
        }
        try:
            with open(LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception:
            logger.exception('Failed to write log entry')
        raise

    duration = time.time() - start

    # Try to extract response body if available (JSONResponse/PlainTextResponse expose .body)
    response_body = ''
    try:
        if hasattr(response, 'body') and response.body is not None:
            response_body = response.body.decode(errors='ignore') if isinstance(response.body, (bytes, bytearray)) else str(response.body)
        else:
            # best-effort fallback
            response_body = ''
    except Exception:
        response_body = ''

    entry = {
        'ts': ts,
        'id': req_id,
        'method': request.method,
        'path': str(request.url.path),
        'request': request_text,
        'status': getattr(response, 'status_code', None),
        'response': response_body[:2000],
        'duration': duration,
    }

    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception:
        logger.exception('Failed to write log entry')

    return response

# Pydantic response models (minimal)
class ChatMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = "stop"

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int



def clean_gemini_output(output: str) -> str:
    """Simple cleaning heuristic for Gemini CLI output."""
    if not output:
        return ""

    lines = [ln.strip() for ln in output.splitlines()]
    lines = [ln for ln in lines if ln]

    cleaned = []
    for ln in lines:
        if set(ln) <= set("-_=*~ ") and len(ln) > 3:
            continue
        if any(c in ln for c in '█░╭╮╯╰│─┌┐└┘'):
            continue
        cleaned.append(ln)

    return ' '.join(cleaned).strip()


async def run_gemini_cli(prompt: str, timeout: float = 30.0) -> str:
    """Try multiple invocation strategies to support different Gemini CLI versions.

    Strategies tried (in order):
    1. --prompt <prompt>
    2. -p <prompt>
    3. positional prompt (as a single argument)
    """
    gemini_path = os.getenv('GEMINI_PATH', '/opt/homebrew/bin/gemini')
    logger.debug(f"GEMINI_PATH={gemini_path}")

    if not os.path.exists(gemini_path):
        logger.error(f"Gemini CLI not found at {gemini_path}")
        raise HTTPException(status_code=500, detail=f"Gemini CLI not found at {gemini_path}")

    # candidate command variations
    strategies = [
        [gemini_path, '--prompt', prompt, '--approval-mode', 'yolo'],
        [gemini_path, '-p', prompt, '--approval-mode', 'yolo'],
        [gemini_path, prompt, '--approval-mode', 'yolo'],
        # fallback using short -y (approval mode) without separate approval-mode value
        [gemini_path, '--prompt', prompt, '-y'],
        [gemini_path, '-p', prompt, '-y'],
        [gemini_path, prompt, '-y'],
    ]

    errors = []
    for cmd in strategies:
        safe_cmd = ' '.join(shlex.quote(str(c)) for c in cmd)
        logger.info(f"Trying Gemini CLI command: {safe_cmd}")
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(f"Gemini attempt timed out for cmd: {safe_cmd}")
                proc.kill()
                errors.append(f"timeout for cmd: {safe_cmd}")
                continue

            stdout_text = stdout.decode(errors='ignore')
            stderr_text = stderr.decode(errors='ignore')

            if proc.returncode == 0:
                logger.info(f"Gemini succeeded for cmd: {safe_cmd} (len_out={len(stdout_text)})")
                return stdout_text
            else:
                logger.warning(f"Gemini returned code {proc.returncode} for cmd: {safe_cmd} stderr={stderr_text[:400]}")
                errors.append(f"rc={proc.returncode} cmd={safe_cmd} stderr={stderr_text[:400]}")
                continue

        except Exception as e:
            logger.exception(f"Error running gemini cmd: {safe_cmd}")
            errors.append(f"exception for cmd={safe_cmd}: {str(e)}")
            continue

    # All strategies failed
    combined = '\n'.join(errors)[:2000]
    logger.error(f"All Gemini strategies failed: {combined}")
    raise HTTPException(status_code=500, detail=f"Gemini CLI failed (tried multiple argument styles): {combined}")


@app.get('/health')
async def health():
    return {"status": "ok", "ts": int(time.time())}


@app.get('/v1/models')
@app.get('/models')
async def list_models():
    return {
        "object": "list",
        "data": [
            {"id": "gemini-local", "object": "model", "owned_by": "local"},
            {"id": "gemini-2.5-pro-preview-06-05", "object": "model", "owned_by": "local"},
        ],
    }


@app.post('/v1/chat/completions')
@app.post('/chat/completions')
async def chat_completions(request: Request):
    request_id = uuid.uuid4().hex
    start = time.time()
    logger.info(f"[REQUEST_START] id={request_id} path={request.url.path}")

    try:
        body = await request.json()
    except Exception:
        logger.error(f"[REQUEST_ERROR] id={request_id} invalid json")
        raise HTTPException(status_code=400, detail='Invalid JSON body')

    model = body.get('model', 'gemini-local')
    messages = body.get('messages')
    prompt_field = body.get('prompt')

    if messages and isinstance(messages, list):
        parts = []
        system_messages = [m for m in messages if m.get('role') == 'system']
        if system_messages:
            parts.append('System: ' + '\n'.join(m.get('content','') for m in system_messages))
        for m in messages:
            role = m.get('role')
            content = m.get('content','')
            if role == 'user':
                parts.append('Human: ' + content)
            elif role == 'assistant':
                parts.append('Assistant: ' + content)
        if messages[-1].get('role') == 'user':
            parts.append('Assistant:')
        prompt = '\n\n'.join(parts)
    elif prompt_field:
        prompt = '\n'.join(prompt_field) if isinstance(prompt_field, list) else str(prompt_field)
    else:
        raise HTTPException(status_code=400, detail='No messages or prompt provided')

    logger.debug(f"[REQUEST_PROMPT] id={request_id} preview={prompt[:200]}")

    raw = await run_gemini_cli(prompt, timeout=60.0)
    logger.debug(f"[GEMINI_RAW] id={request_id} len={len(raw)}")

    cleaned = clean_gemini_output(raw)
    if not cleaned:
        cleaned = "I apologize, I couldn't generate a response."

    # If client requested streaming, return an SSE/text-event-stream compatible stream
    if body.get('stream'):
        async def event_stream():
            # OpenAI-style streaming: send chunks as JSON lines prefixed with `data: `
            # We'll split the cleaned text into small chunks to simulate token streaming.
            chunk_size = 64
            idx = 0
            # initial meta chunk (optional)
            # stream content in increments
            while idx < len(cleaned):
                part = cleaned[idx:idx+chunk_size]
                idx += chunk_size
                data = {
                    "id": f"chatcmpl-{request_id}",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [
                        {"delta": {"content": part}, "index": 0, "finish_reason": None}
                    ]
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0)

            # final DONE event
            yield "data: [DONE]\n\n"

        elapsed = time.time() - start
        logger.info(f"[REQUEST_END_STREAM] id={request_id} t={elapsed:.3f}s tokens={max(0, len(prompt.split()) + len(cleaned.split()))}")
        return StreamingResponse(event_stream(), media_type='text/event-stream')

    response_obj = {
        "id": f"chatcmpl-{request_id}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "system_fingerprint": f"fp_{request_id[:8]}",
        "choices": [
            {"index": 0, "message": {"role": "assistant", "content": cleaned}, "finish_reason": "stop"}
        ],
        "usage": {
            "prompt_tokens": max(0, len(prompt.split())),
            "completion_tokens": max(0, len(cleaned.split())),
            "total_tokens": max(0, len(prompt.split()) + len(cleaned.split())),
        },
    }

    elapsed = time.time() - start
    logger.info(f"[REQUEST_END] id={request_id} t={elapsed:.3f}s tokens={response_obj['usage']['total_tokens']}")

    return JSONResponse(status_code=200, content=response_obj)

