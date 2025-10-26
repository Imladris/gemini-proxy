"""
数据模型模块

定义所有 Pydantic 数据模型，包括请求和响应数据结构。
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str
    content: str
    name: Optional[str] = None


class ChatCompletionChoice(BaseModel):
    """聊天补全选择模型"""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = "stop"


class ChatCompletionUsage(BaseModel):
    """使用量统计模型"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionRequest(BaseModel):
    """聊天补全请求模型"""
    model: str = "gemini-local"
    messages: List[ChatMessage]
    prompt: Optional[str] = None
    stream: Optional[bool] = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[List[str]] = None
    user: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    """聊天补全响应模型（非流式）"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    system_fingerprint: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage


class ChatCompletionChunk(BaseModel):
    """聊天补全流式响应块模型"""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict[str, Any]]


class ModelInfo(BaseModel):
    """模型信息模型"""
    id: str
    object: str = "model"
    owned_by: str = "local"


class ModelListResponse(BaseModel):
    """模型列表响应模型"""
    object: str = "list"
    data: List[ModelInfo]


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    ts: int


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: Dict[str, Any]
    detail: Optional[str] = None


# 支持的模型列表
SUPPORTED_MODELS = [
    ModelInfo(id="gemini-local", owned_by="local"),
    ModelInfo(id="gemini-2.5-pro-preview-06-05", owned_by="local"),
]