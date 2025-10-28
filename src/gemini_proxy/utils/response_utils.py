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

    使用改进的平衡算法来估算token数量，适用于中英文混合文本：
    - 基于OpenAI tokenizer的特点进行优化
    - 对短文本使用更精确的估算
    - 对特殊内容（代码、JSON）进行合理处理

    Args:
        text: 输入文本

    Returns:
        int: 估算的token数量
    """
    if not text:
        return 0

    import re

    # 极短文本特殊处理
    if len(text) <= 5:
        return 1
    elif len(text) <= 15:
        # 短文本按字符密度估算
        chinese_count = len(re.findall(r'[\u4e00-\u9fff]', text))
        if chinese_count > len(text) * 0.5:
            # 以中文为主
            return max(1, chinese_count // 2 + len(text) // 6)
        else:
            # 以英文为主
            return max(1, len(text) // 5)

    # 统计各种类型的字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))

    # 更精确的英文单词统计（不包括单个字符）
    english_words = len([w for w in re.findall(r'\b[a-zA-Z]+\b', text) if len(w) > 1])

    # 统计数字序列
    digit_groups = len(re.findall(r'\b\d+\b', text))

    # 检测结构化内容
    has_code_blocks = bool(re.search(r'```[\s\S]*?```', text))
    has_json = bool(re.search(r'\{[^{}]*\}|\[[^\[\]]*\]', text))

    # 基础token估算
    chinese_tokens = max(1, chinese_chars // 2)  # 中文：约2字符/token
    english_tokens = max(0, english_words)      # 英文：约1单词/token
    digit_tokens = digit_groups                  # 数字：1组/token

    # 结构化内容特殊处理
    structure_tokens = 0
    if has_code_blocks or has_json:
        # 对代码块和JSON使用更宽松的字符/token比
        structure_chars = len(re.sub(r'[a-zA-Z0-9\s\u4e00-\u9fff]', '', text))
        structure_tokens = structure_chars // 6  # 特殊字符密度低

    # 组合计算，避免重复计算
    # 计算基础token数
    base_tokens = chinese_tokens + english_tokens + digit_tokens + structure_tokens

    # 使用字符密度作为对比和修正
    char_based_tokens = len(text) // 4  # 平均4字符/token的估算

    # 智能融合两种方法
    if base_tokens > char_based_tokens * 1.5:
        # 如果基础估算过高，使用字符密度修正
        final_tokens = max(char_based_tokens, base_tokens - (base_tokens - char_based_tokens) // 2)
    else:
        # 否则使用两者的加权平均
        final_tokens = int(base_tokens * 0.7 + char_based_tokens * 0.3)

    # 确保最小值
    return max(1, final_tokens)