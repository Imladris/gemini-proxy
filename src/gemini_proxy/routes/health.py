"""
健康检查路由模块

提供服务健康状态检查端点。
"""

import time
from fastapi import APIRouter

from ..models import HealthResponse


router = APIRouter()


@router.get('/health', response_model=HealthResponse)
async def health():
    """
    健康检查端点
    
    Returns:
        HealthResponse: 健康状态响应
    """
    return HealthResponse(
        status="ok",
        ts=int(time.time())
    )