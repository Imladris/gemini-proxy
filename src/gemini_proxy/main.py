"""
主应用入口模块

创建 FastAPI 应用实例，配置中间件和路由。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import config
from .services.logging_service import log_requests_middleware
from .routes import health, models, chat


def create_app() -> FastAPI:
    """
    创建 FastAPI 应用实例
    
    Returns:
        FastAPI: 配置好的应用实例
    """
    # 创建应用
    app = FastAPI(
        title="Gemini Proxy",
        description="FastAPI reverse proxy that adapts OpenAI-style requests to a local Gemini CLI",
        version="0.1.0"
    )
    
    # 配置 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_allow_origins,
        allow_credentials=config.cors_allow_credentials,
        allow_methods=config.cors_allow_methods,
        allow_headers=config.cors_allow_headers,
    )
    
    # 添加请求日志中间件
    app.middleware("http")(log_requests_middleware)
    
    # 注册路由
    app.include_router(health.router)
    app.include_router(models.router)
    app.include_router(chat.router)
    
    return app


# 创建全局应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    # 验证配置
    try:
        config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        exit(1)
    
    # 启动服务器
    uvicorn.run(
        "src.gemini_proxy.main:app",
        host=config.host,
        port=config.port,
        reload=False
    )