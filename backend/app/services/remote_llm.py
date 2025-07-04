import logging
import requests
import json
from typing import List, Dict, Any, Optional
import time

from ..core.config import settings

logger = logging.getLogger(__name__)

class RemoteLLMService:
    """远程语言模型服务"""
    
    def __init__(self):
        self.config = settings.ai_config["chat"]
        self.api_base = self.config["api_base"]
        self.api_key = self.config["api_key"]
        self.model_name = self.config["model_name"]
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 30000)
        
        self.session = requests.Session()
        self.session.timeout = 60
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        logger.info(f"初始化远程LLM服务: {self.model_name}")
        logger.info(f"服务地址: {self.api_base}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        try:
            # 构建请求数据
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "stream": False
            }
            
            # 发送请求
            start_time = time.time()
            response = self.session.post(
                f"{self.api_base}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            elapsed_time = time.time() - start_time
            logger.info(f"生成回答，耗时: {elapsed_time:.2f}秒")
            
            return content.strip()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"远程LLM请求失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"文本生成失败: {str(e)}")
            raise
    
    async def generate_with_context(self, question: str, context: str) -> str:
        """基于上下文生成回答"""
        prompt = f"""基于以下信息，请回答用户的问题。请确保回答准确、简洁且有帮助。

上下文信息：
{context}

用户问题：{question}

回答："""
        
        return await self.generate(prompt)
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            test_prompt = "你好，请简单介绍一下自己。"
            response = await self.generate(test_prompt, max_tokens=50)
            return len(response) > 0
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False 