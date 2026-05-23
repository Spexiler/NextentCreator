#!/usr/bin/env python3
"""
NextentCreator - LLM Client
支持多种大模型 API 的统一客户端
"""

import os
import httpx
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LLMClient:
    """统一的大模型 API 客户端"""
    
    def __init__(self):
        # 从环境变量读取配置
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.max_tokens = int(os.getenv("MAX_TOKENS", "3000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.timeout = int(os.getenv("API_TIMEOUT", "60"))
        
        # 初始化提供商配置
        self._init_provider()
    
    def _init_provider(self):
        """初始化 LLM 提供商配置"""
        if self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY", "")
            self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        elif self.provider == "claude":
            self.api_key = os.getenv("CLAUDE_API_KEY", "")
            self.base_url = os.getenv("CLAUDE_BASE_URL", "https://api.anthropic.com/v1")
            self.model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
        
        elif self.provider == "wenxin":
            self.api_key = os.getenv("WENXIN_API_KEY", "")
            self.secret_key = os.getenv("WENXIN_SECRET_KEY", "")
            self.model = os.getenv("WENXIN_MODEL", "ERNIE-Bot-4")
        
        elif self.provider == "qwen":
            self.api_key = os.getenv("QWEN_API_KEY", "")
            self.base_url = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
            self.model = os.getenv("QWEN_MODEL", "qwen-turbo")
        
        elif self.provider == "deepseek":
            self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
            self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
            self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        else:
            raise ValueError(f"不支持的 LLM 提供商: {self.provider}")
    
    async def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        生成文本
        
        Args:
            prompt: 输入提示词
            max_tokens: 最大生成 token 数（可选）
        
        Returns:
            生成的文本内容
        """
        max_tokens = max_tokens or self.max_tokens
        
        if self.provider == "openai":
            return await self._call_openai(prompt, max_tokens)
        elif self.provider == "claude":
            return await self._call_claude(prompt, max_tokens)
        elif self.provider == "wenxin":
            return await self._call_wenxin(prompt, max_tokens)
        elif self.provider == "qwen":
            return await self._call_qwen(prompt, max_tokens)
        elif self.provider == "deepseek":
            return await self._call_deepseek(prompt, max_tokens)
        else:
            raise ValueError(f"不支持的 LLM 提供商: {self.provider}")
    
    async def _call_openai(self, prompt: str, max_tokens: int) -> str:
        """调用 OpenAI API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": self.temperature
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _call_claude(self, prompt: str, max_tokens: int) -> str:
        """调用 Claude API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
    
    async def _call_wenxin(self, prompt: str, max_tokens: int) -> str:
        """调用文心一言 API"""
        # 文心一言需要先获取 access_token
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # 获取 access_token
            token_response = await client.post(
                "https://aip.baidubce.com/oauth/2.0/token",
                params={
                    "grant_type": "client_credentials",
                    "client_id": self.api_key,
                    "client_secret": self.secret_key
                }
            )
            token_response.raise_for_status()
            access_token = token_response.json()["access_token"]
            
            # 调用聊天 API
            response = await client.post(
                f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{self.model.lower()}",
                params={"access_token": access_token},
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "max_output_tokens": max_tokens
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["result"]
    
    async def _call_qwen(self, prompt: str, max_tokens: int) -> str:
        """调用通义千问 API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "input": {"messages": [{"role": "user", "content": prompt}]},
                    "parameters": {
                        "max_tokens": max_tokens,
                        "temperature": self.temperature
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["output"]["text"]
    
    async def _call_deepseek(self, prompt: str, max_tokens: int) -> str:
        """调用 DeepSeek API（兼容 OpenAI 格式）"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": self.temperature
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


# 全局 LLM 客户端实例
_llm_client: Optional[LLMClient] = None

def get_llm_client() -> LLMClient:
    """获取 LLM 客户端实例"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client

async def generate_text(prompt: str, max_tokens: Optional[int] = None) -> str:
    """
    生成文本的便捷函数
    
    Args:
        prompt: 输入提示词
        max_tokens: 最大生成 token 数
    
    Returns:
        生成的文本内容
    """
    client = get_llm_client()
    return await client.generate(prompt, max_tokens)
