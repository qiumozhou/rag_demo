import logging
import requests
import numpy as np
from typing import List, Dict, Any
import time

from ..core.config import settings

logger = logging.getLogger(__name__)

class RemoteEmbeddingService:
    """远程嵌入模型服务"""
    
    def __init__(self):
        self.config = settings.ai_config["embedding"]
        self.base_url = self.config["base_url"]
        self.model_name = self.config["model_name"]
        self.session = requests.Session()
        self.session.timeout = 30
        
        logger.info(f"初始化远程嵌入服务: {self.model_name}")
        logger.info(f"服务地址: {self.base_url}")
    
    async def encode(self, texts: List[str]) -> np.ndarray:
        """编码文本为向量"""
        try:
            if not texts:
                return np.array([])
            
            # 构建请求数据
            payload = {
                "input": texts,
                "model": self.model_name
            }
            
            # 发送请求
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/embeddings",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            embeddings = []
            
            for item in result.get("data", []):
                embedding = item.get("embedding", [])
                embeddings.append(embedding)
            
            embeddings_array = np.array(embeddings)
            
            elapsed_time = time.time() - start_time
            logger.info(f"编码 {len(texts)} 个文本，耗时: {elapsed_time:.2f}秒")
            
            return embeddings_array
            
        except requests.exceptions.RequestException as e:
            logger.error(f"远程嵌入请求失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"嵌入编码失败: {str(e)}")
            raise
    
    async def encode_single(self, text: str) -> np.ndarray:
        """编码单个文本"""
        result = await self.encode([text])
        return result[0] if len(result) > 0 else np.array([])
    
    def get_embedding_dimension(self) -> int:
        """获取嵌入维度"""
        # 对于text2vec-large-chinese，通常是1024维
        return 1024
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            test_text = "测试文本"
            embedding = await self.encode_single(test_text)
            return len(embedding) > 0
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False 