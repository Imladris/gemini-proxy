"""
Gemini 服务模块

负责执行 Gemini CLI 命令，处理多种参数格式和错误处理。
"""

import asyncio
import os
import shlex
import logging
from typing import List, Optional
from fastapi import HTTPException

from ..config import config


logger = logging.getLogger('gemini-proxy')


class GeminiService:
    """Gemini CLI 服务类"""
    
    def __init__(self, gemini_path: Optional[str] = None):
        self.gemini_path = gemini_path or config.gemini_path
        self.timeout = config.gemini_timeout
    
    async def execute(
        self, 
        prompt: str, 
        timeout: Optional[float] = None
    ) -> str:
        """
        执行 Gemini CLI 命令
        
        Args:
            prompt: 提示词
            timeout: 超时时间，如果为None则使用配置中的超时时间
        
        Returns:
            str: Gemini CLI 的输出
        
        Raises:
            HTTPException: 当执行失败时抛出
        """
        if timeout is None:
            timeout = self.timeout
        
        # 验证 Gemini CLI 路径
        if not os.path.exists(self.gemini_path):
            logger.error(f"Gemini CLI not found at {self.gemini_path}")
            raise HTTPException(
                status_code=500, 
                detail=f"Gemini CLI not found at {self.gemini_path}"
            )
        
        # 候选命令变体，支持不同的 Gemini CLI 版本
        strategies = [
            [self.gemini_path, '--prompt', prompt, '--approval-mode', 'yolo'],
            [self.gemini_path, '-p', prompt, '--approval-mode', 'yolo'],
            [self.gemini_path, prompt, '--approval-mode', 'yolo'],
            # 回退使用短参数 -y（批准模式）
            [self.gemini_path, '--prompt', prompt, '-y'],
            [self.gemini_path, '-p', prompt, '-y'],
            [self.gemini_path, prompt, '-y'],
        ]
        
        errors = []
        for cmd in strategies:
            safe_cmd = ' '.join(shlex.quote(str(c)) for c in cmd)
            logger.info(f"Trying Gemini CLI command: {safe_cmd}")
            
            try:
                result = await self._run_command(cmd, timeout)
                if result is not None:
                    logger.info(f"Gemini succeeded for cmd: {safe_cmd} (len_out={len(result)})")
                    return result
                else:
                    errors.append(f"rc=non-zero cmd={safe_cmd}")
                    
            except asyncio.TimeoutError:
                logger.warning(f"Gemini attempt timed out for cmd: {safe_cmd}")
                errors.append(f"timeout for cmd: {safe_cmd}")
                continue
                
            except Exception as e:
                logger.exception(f"Error running gemini cmd: {safe_cmd}")
                errors.append(f"exception for cmd={safe_cmd}: {str(e)}")
                continue
        
        # 所有策略都失败
        combined_errors = '\n'.join(errors)[:2000]
        logger.error(f"All Gemini strategies failed: {combined_errors}")
        raise HTTPException(
            status_code=500, 
            detail=f"Gemini CLI failed (tried multiple argument styles): {combined_errors}"
        )
    
    async def _run_command(
        self, 
        cmd: List[str], 
        timeout: float
    ) -> Optional[str]:
        """
        运行单个命令
        
        Args:
            cmd: 命令参数列表
            timeout: 超时时间
        
        Returns:
            Optional[str]: 命令输出，如果失败返回None
        """
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f"Command timed out: {' '.join(cmd)}")
                proc.kill()
                return None
            
            stdout_text = stdout.decode(errors='ignore')
            stderr_text = stderr.decode(errors='ignore')
            
            if proc.returncode == 0:
                return stdout_text
            else:
                logger.warning(
                    f"Gemini returned code {proc.returncode} for cmd: {' '.join(cmd)} "
                    f"stderr={stderr_text[:400]}"
                )
                return None
                
        except Exception as e:
            logger.exception(f"Exception running command: {' '.join(cmd)}")
            return None
    
    def validate_gemini_path(self) -> bool:
        """
        验证 Gemini CLI 路径是否有效
        
        Returns:
            bool: 路径是否有效
        """
        return os.path.exists(self.gemini_path) and os.access(self.gemini_path, os.X_OK)


# 全局服务实例
gemini_service = GeminiService()


def get_gemini_service() -> GeminiService:
    """获取全局 Gemini 服务实例"""
    return gemini_service