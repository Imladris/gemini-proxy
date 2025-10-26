"""
日志服务模块

负责请求/响应日志记录、日志轮转管理和结构化日志输出。
"""

import logging
import time
import uuid
import json
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional
from fastapi import Request, Response

from ..config import config


class LoggingService:
    """日志服务类"""
    
    def __init__(self):
        self.log_path = config.log_file
        self.max_log_size = config.max_log_size
        self.backup_count = config.log_backup_count
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """设置日志配置"""
        # 创建日志目录
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        except Exception:
            pass
        
        # 配置根日志记录器
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format='%(asctime)s %(levelname)s %(message)s'
        )
        
        # 为代理服务添加文件处理器
        logger = logging.getLogger('gemini-proxy')
        file_handler = RotatingFileHandler(
            self.log_path,
            maxBytes=self.max_log_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    async def log_request_response(
        self,
        request: Request,
        response: Response,
        request_body: str = '',
        response_body: str = '',
        duration: float = 0.0
    ) -> None:
        """
        记录请求和响应日志
        
        Args:
            request: FastAPI 请求对象
            response: FastAPI 响应对象
            request_body: 请求体内容
            response_body: 响应体内容
            duration: 请求处理时长
        """
        log_entry = {
            'ts': int(time.time()),
            'id': uuid.uuid4().hex,
            'method': request.method,
            'path': str(request.url.path),
            'request': request_body,
            'status': getattr(response, 'status_code', None),
            'response': response_body[:2000],  # 限制响应体长度
            'duration': duration,
        }
        
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logging.error(f"Failed to write log entry: {str(e)}")
    
    async def log_error(
        self,
        request: Request,
        error: Exception,
        request_body: str = '',
        duration: float = 0.0
    ) -> None:
        """
        记录错误日志
        
        Args:
            request: FastAPI 请求对象
            error: 异常对象
            request_body: 请求体内容
            duration: 请求处理时长
        """
        log_entry = {
            'ts': int(time.time()),
            'id': uuid.uuid4().hex,
            'method': request.method,
            'path': str(request.url.path),
            'request': request_body,
            'status': 500,
            'response': str(error),
            'duration': duration,
        }
        
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logging.error(f"Failed to write error log entry: {str(e)}")
    
    def log_info(self, message: str, **kwargs) -> None:
        """
        记录信息日志
        
        Args:
            message: 日志消息
            **kwargs: 额外参数
        """
        logger = logging.getLogger('gemini-proxy')
        if kwargs:
            message = f"{message} {kwargs}"
        logger.info(message)
    
    def log_error_message(self, message: str, **kwargs) -> None:
        """
        记录错误消息
        
        Args:
            message: 错误消息
            **kwargs: 额外参数
        """
        logger = logging.getLogger('gemini-proxy')
        if kwargs:
            message = f"{message} {kwargs}"
        logger.error(message)
    
    def log_warning(self, message: str, **kwargs) -> None:
        """
        记录警告日志
        
        Args:
            message: 警告消息
            **kwargs: 额外参数
        """
        logger = logging.getLogger('gemini-proxy')
        if kwargs:
            message = f"{message} {kwargs}"
        logger.warning(message)
    
    def log_debug(self, message: str, **kwargs) -> None:
        """
        记录调试日志
        
        Args:
            message: 调试消息
            **kwargs: 额外参数
        """
        logger = logging.getLogger('gemini-proxy')
        if kwargs:
            message = f"{message} {kwargs}"
        logger.debug(message)


# 全局日志服务实例
logging_service = LoggingService()


def get_logging_service() -> LoggingService:
    """获取全局日志服务实例"""
    return logging_service


async def log_requests_middleware(request: Request, call_next):
    """
    请求日志中间件
    
    Args:
        request: FastAPI 请求对象
        call_next: 下一个中间件或路由处理函数
    
    Returns:
        Response: 响应对象
    """
    request_id = uuid.uuid4().hex
    start_time = time.time()
    
    try:
        # 读取请求体
        body_bytes = await request.body()
        request_body = body_bytes.decode(errors='ignore') if body_bytes else ''
    except Exception:
        request_body = ''
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # 提取响应体
        response_body = ''
        try:
            if hasattr(response, 'body') and response.body is not None:
                response_body = response.body.decode(errors='ignore') if isinstance(response.body, (bytes, bytearray)) else str(response.body)
        except Exception:
            response_body = ''
        
        # 记录成功日志
        await logging_service.log_request_response(
            request, response, request_body, response_body, duration
        )
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        # 记录错误日志
        await logging_service.log_error(request, e, request_body, duration)
        raise