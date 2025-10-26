"""
响应工具模块

提供构建 OpenAI 兼容响应的工具函数。
"""

import time
import uuid
from typing import Dict, Any, List, Optional

from ..models import (
    ChatCompletionResponse, 
    ChatCompletionChoice, 
    ChatMessage, 
    ChatCompletionUsage,
    ChatCompletionChunk
)


def build_chat_completion_response(
    content: str,
    model: str = "gemini-local",
    request_id: Optional[str] = None,
    prompt_tokens: int = 0,
    completion_tokens: int = 0
) -> ChatCompletionResponse:
    """
    构建聊天补全响应
    
    Args:
        content: 助手回复内容
        model: 模型名称
        request_id: 请求ID，如果为None则自动生成
        prompt_tokens: 提示词token数
        completion_tokens: 补全token数
    
    Returns:
        ChatCompletionResponse: 聊天补全响应对象
    """
    if request_id is None:
        request_id = f"chatcmpl-{uuid.uuid4().hex}"
    
    return ChatCompletionResponse(
        id=request_id,
        created=int(time.time()),
        model=model,
        system_fingerprint=f"fp_{request_id[:8]}",
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(
                    role="assistant",
                    content=content
                ),
                finish_reason="stop"
            )
        ],
        usage=ChatCompletionUsage(
            prompt_tokens=max(0, prompt_tokens),
            completion_tokens=max(0, completion_tokens),
            total_tokens=max(0, prompt_tokens + completion_tokens)
        )
    )


def build_chat_completion_chunk(
    content: str,
    request_id: str,
    model: str = "gemini-local",
    finish_reason: Optional[str] = None
) -> ChatCompletionChunk:
    """
    构建聊天补全流式响应块
    
    Args:
        content: 内容块
        request_id: 请求ID
        model: 模型名称
        finish_reason: 完成原因，None表示继续
    
    Returns:
        ChatCompletionChunk: 流式响应块
    """
    return ChatCompletionChunk(
        id=f"chatcmpl-{request_id}",
        created=int(time.time()),
        model=model,
        choices=[
            {
                "delta": {"content": content},
                "index": 0,
                "finish_reason": finish_reason
            }
        ]
    )


def build_error_response(
    message: str,
    error_type: str = "internal_error",
    status_code: int = 500
) -> Dict[str, Any]:
    """
    构建错误响应
    
    Args:
        message: 错误消息
        error_type: 错误类型
        status_code: HTTP状态码
    
    Returns:
        Dict: 错误响应字典
    """
    return {
        "error": {
            "message": message,
            "type": error_type,
            "code": status_code
        }
    }


def count_tokens(text: str) -> int:
    """
    估算文本的token数量
    
    Args:
        text: 输入文本
    
    Returns:
        int: 估算的token数量
    """
    # 简单的token估算：按空格分割单词
    if not text:
        return 0
    return len(text.split())