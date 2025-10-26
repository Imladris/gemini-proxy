"""
聊天路由模块

处理聊天补全请求，支持流式和非流式响应。
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

from ..models import ChatCompletionRequest
from ..services.gemini_service import get_gemini_service
from ..services.logging_service import get_logging_service
from ..utils.validation import (
    validate_chat_request, 
    extract_prompt_from_messages,
    validate_prompt
)
from ..utils.response_utils import (
    build_chat_completion_response,
    build_chat_completion_chunk,
    count_tokens
)
from ..utils.cleaning import clean_gemini_output


router = APIRouter()
gemini_service = get_gemini_service()
logging_service = get_logging_service()


@router.post('/v1/chat/completions')
@router.post('/chat/completions')
async def chat_completions(request: Request):
    """
    聊天补全端点
    
    支持两个路径：
    - /v1/chat/completions (OpenAI 兼容格式)
    - /chat/completions (简化格式)
    
    Args:
        request: FastAPI 请求对象
    
    Returns:
        StreamingResponse 或 JSONResponse: 流式或非流式响应
    """
    request_id = uuid.uuid4().hex
    start_time = time.time()
    
    logging_service.log_info(
        f"[REQUEST_START] id={request_id} path={request.url.path}"
    )
    
    try:
        # 解析请求体
        body = await request.json()
    except Exception:
        logging_service.log_error_message(
            f"[REQUEST_ERROR] id={request_id} invalid json"
        )
        raise HTTPException(status_code=400, detail='Invalid JSON body')
    
    # 验证请求数据
    try:
        chat_request = validate_chat_request(body)
    except HTTPException as e:
        logging_service.log_error_message(
            f"[REQUEST_VALIDATION_ERROR] id={request_id} detail={e.detail}"
        )
        raise e
    
    # 提取提示词
    try:
        if chat_request.messages:
            prompt = extract_prompt_from_messages(chat_request.messages)
        elif chat_request.prompt:
            prompt = validate_prompt(chat_request.prompt)
        else:
            raise HTTPException(status_code=400, detail='No messages or prompt provided')
    except HTTPException as e:
        logging_service.log_error_message(
            f"[PROMPT_EXTRACTION_ERROR] id={request_id} detail={e.detail}"
        )
        raise e
    
    logging_service.log_debug(
        f"[REQUEST_PROMPT] id={request_id} preview={prompt[:200]}"
    )
    
    # 执行 Gemini CLI
    try:
        raw_output = await gemini_service.execute(prompt, timeout=60.0)
        logging_service.log_debug(
            f"[GEMINI_RAW] id={request_id} len={len(raw_output)}"
        )
    except HTTPException as e:
        logging_service.log_error_message(
            f"[GEMINI_EXECUTION_ERROR] id={request_id} detail={e.detail}"
        )
        raise e
    
    # 清理输出
    cleaned_output = clean_gemini_output(raw_output)
    if not cleaned_output:
        cleaned_output = "I apologize, I couldn't generate a response."
    
    # 计算 token 数量
    prompt_tokens = count_tokens(prompt)
    completion_tokens = count_tokens(cleaned_output)
    
    # 处理流式响应
    if chat_request.stream:
        async def event_stream():
            """生成流式响应事件"""
            chunk_size = 64
            idx = 0
            
            # 分块发送内容
            while idx < len(cleaned_output):
                part = cleaned_output[idx:idx + chunk_size]
                idx += chunk_size
                
                chunk = build_chat_completion_chunk(
                    content=part,
                    request_id=request_id,
                    model=chat_request.model,
                    finish_reason=None
                )
                
                yield f"data: {json.dumps(chunk.dict(), ensure_ascii=False)}\n\n"
                await asyncio.sleep(0)
            
            # 发送完成事件
            yield "data: [DONE]\n\n"
        
        elapsed = time.time() - start_time
        logging_service.log_info(
            f"[REQUEST_END_STREAM] id={request_id} t={elapsed:.3f}s "
            f"tokens={prompt_tokens + completion_tokens}"
        )
        
        return StreamingResponse(
            event_stream(), 
            media_type='text/event-stream'
        )
    
    # 处理非流式响应
    response = build_chat_completion_response(
        content=cleaned_output,
        model=chat_request.model,
        request_id=request_id,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens
    )
    
    elapsed = time.time() - start_time
    logging_service.log_info(
        f"[REQUEST_END] id={request_id} t={elapsed:.3f}s "
        f"tokens={response.usage.total_tokens}"
    )
    
    return response