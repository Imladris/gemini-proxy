"""
配置管理模块

集中管理所有配置项，支持环境变量和默认值。
"""

import os
from typing import Optional


class Config:
    """配置管理类"""
    
    def __init__(self):
        # Gemini CLI 路径
        self.gemini_path: str = os.getenv('GEMINI_PATH', '/opt/homebrew/bin/gemini')
        
        # 日志配置
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file: str = os.getenv('LOG_FILE', 'proxy.log')
        self.max_log_size: int = int(os.getenv('MAX_LOG_SIZE', '5242880'))  # 5MB
        self.log_backup_count: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        
        # 服务器配置
        self.host: str = os.getenv('HOST', '127.0.0.1')
        self.port: int = int(os.getenv('PORT', '7777'))
        
        # 请求超时配置
        self.request_timeout: float = float(os.getenv('REQUEST_TIMEOUT', '60.0'))
        self.gemini_timeout: float = float(os.getenv('GEMINI_TIMEOUT', '30.0'))
        
        # CORS 配置
        self.cors_allow_origins: list = os.getenv('CORS_ALLOW_ORIGINS', '*').split(',')
        self.cors_allow_credentials: bool = os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true'
        self.cors_allow_methods: list = os.getenv('CORS_ALLOW_METHODS', '*').split(',')
        self.cors_allow_headers: list = os.getenv('CORS_ALLOW_HEADERS', '*').split(',')
    
    def validate(self) -> None:
        """验证配置的有效性"""
        if not os.path.exists(self.gemini_path):
            raise ValueError(f"Gemini CLI not found at {self.gemini_path}")
        
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port number: {self.port}")
        
        if self.request_timeout <= 0:
            raise ValueError(f"Invalid request timeout: {self.request_timeout}")
        
        if self.gemini_timeout <= 0:
            raise ValueError(f"Invalid Gemini timeout: {self.gemini_timeout}")
    
    def __str__(self) -> str:
        """返回配置的字符串表示"""
        return (
            f"Config("
            f"gemini_path={self.gemini_path}, "
            f"host={self.host}, "
            f"port={self.port}, "
            f"log_level={self.log_level}, "
            f"request_timeout={self.request_timeout}"
            f")"
        )


# 全局配置实例
config = Config()


def get_config() -> Config:
    """获取全局配置实例"""
    return config