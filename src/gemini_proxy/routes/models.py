"""
模型列表路由模块

提供模型列表查询端点，返回支持的模型信息。
"""

from fastapi import APIRouter

from ..models import ModelListResponse, SUPPORTED_MODELS


router = APIRouter()


@router.get('/v1/models', response_model=ModelListResponse)
@router.get('/models', response_model=ModelListResponse)
async def list_models():
    """
    获取模型列表端点
    
    支持两个路径：
    - /v1/models (OpenAI 兼容格式)
    - /models (简化格式)
    
    Returns:
        ModelListResponse: 模型列表响应
    """
    return ModelListResponse(
        object="list",
        data=SUPPORTED_MODELS
    )