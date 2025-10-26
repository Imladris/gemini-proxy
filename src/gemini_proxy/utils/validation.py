"""
验证工具模块

提供数据验证和参数校验功能。
"""

import re
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

from ..models import ChatCompletionRequest, ChatMessage


def validate_chat_request(body: Dict[str, Any]) -> ChatCompletionRequest:
    """
    验证聊天请求数据
    
    Args:
        body: 请求体数据
    
    Returns:
        ChatCompletionRequest: 验证后的请求对象
    
    Raises:
        HTTPException: 当验证失败时抛出
    """
    try:
        # 检查必需字段
        if not body.get('messages') and not body.get('prompt'):
            raise HTTPException(
                status_code=400, 
                detail='No messages or prompt provided'
            )
        
        # 验证消息格式
        messages = body.get('messages', [])
        if messages:
            if not isinstance(messages, list):
                raise HTTPException(
                    status_code=400, 
                    detail='Messages must be a list'
                )
            
            for msg in messages:
                if not isinstance(msg, dict):
                    raise HTTPException(
                        status_code=400, 
                        detail='Each message must be an object'
                    )
                if 'role' not in msg or 'content' not in msg:
                    raise HTTPException(
                        status_code=400, 
                        detail='Each message must have role and content fields'
                    )
        
        # 验证模型名称
        model = body.get('model', 'gemini-local')
        if not isinstance(model, str):
            raise HTTPException(
                status_code=400, 
                detail='Model must be a string'
            )
        
        # 验证流式参数
        stream = body.get('stream', False)
        if not isinstance(stream, bool):
            raise HTTPException(
                status_code=400, 
                detail='Stream must be a boolean'
            )
        
        # 创建请求对象
        return ChatCompletionRequest(**body)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f'Invalid request format: {str(e)}'
        )


def validate_prompt(prompt: str) -> str:
    """
    验证和清理提示词
    
    Args:
        prompt: 原始提示词
    
    Returns:
        str: 清理后的提示词
    
    Raises:
        HTTPException: 当提示词无效时抛出
    """
    if not prompt or not prompt.strip():
        raise HTTPException(
            status_code=400, 
            detail='Prompt cannot be empty'
        )
    
    # 限制提示词长度
    if len(prompt) > 10000:
        raise HTTPException(
            status_code=400, 
            detail='Prompt too long (max 10000 characters)'
        )
    
    # 移除潜在的恶意字符
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', prompt)
    
    return cleaned.strip()


def validate_model_name(model: str) -> str:
    """
    验证模型名称
    
    Args:
        model: 模型名称
    
    Returns:
        str: 验证后的模型名称
    
    Raises:
        HTTPException: 当模型名称无效时抛出
    """
    if not model or not isinstance(model, str):
        raise HTTPException(
            status_code=400, 
            detail='Invalid model name'
        )
    
    # 检查模型名称格式
    if not re.match(r'^[a-zA-Z0-9._-]+$', model):
        raise HTTPException(
            status_code=400, 
            detail='Invalid model name format'
        )
    
    return model


def extract_prompt_from_messages(messages: List[ChatMessage]) -> str:
    """
    从消息列表中提取提示词
    
    Args:
        messages: 消息列表
    
    Returns:
        str: 提取的提示词
    
    Raises:
        HTTPException: 当消息格式无效时抛出
    """
    if not messages:
        raise HTTPException(
            status_code=400,
            detail='No messages provided'
        )
    
    parts = []
    system_messages = [m for m in messages if m.role == 'system']
    
    if system_messages:
        system_content = '\n'.join(m.content for m in system_messages)
        parts.append('System: ' + system_content)
    
    for message in messages:
        role = message.role
        content = message.content
        
        if role == 'user':
            parts.append('Human: ' + content)
        elif role == 'assistant':
            parts.append('Assistant: ' + content)
    
    # 如果最后一条消息是用户消息，添加助手提示
    if messages and messages[-1].role == 'user':
        parts.append('Assistant:')
    
    return '\n\n'.join(parts)


def validate_gemini_path(gemini_path: str) -> None:
    """
    验证 Gemini CLI 路径
    
    Args:
        gemini_path: Gemini CLI 路径
    
    Raises:
        HTTPException: 当路径无效时抛出
    """
    import os
    
    if not os.path.exists(gemini_path):
        raise HTTPException(
            status_code=500, 
            detail=f'Gemini CLI not found at {gemini_path}'
        )
    
    if not os.access(gemini_path, os.X_OK):
        raise HTTPException(
            status_code=500, 
            detail=f'Gemini CLI is not executable at {gemini_path}'
        )