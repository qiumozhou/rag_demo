from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
import os

class Settings(BaseSettings):
    # 应用基本配置
    app_name: str = "RAG Knowledge System"
    version: str = "1.0.0"
    debug: bool = True
    api_prefix: str = "/api/v1"
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 数据库配置
    chroma_persist_directory: str = "./data/chroma"
    chroma_collection_name: str = "knowledge_base"
    
    # AI模型配置
    ai_config: Dict[str, Any] = {
        "embedding": {
            "factory_name": "openai",
            "model_name": "text2vec-large-chinese",
            "base_url": "",
            "description": "Text2Vec Large 中文模型"
        },
        "chat": {
            "model_type": "openai",
            "model_name": "deepseek-v3",
            "api_key": "",
            "api_base": "",
            "description": "DeepSeek V3 远程模型",
            "temperature": 0.7,
            "max_tokens": 30000
        },
        "rerank": {
            "enabled": True,
            "model_type": "http",
            "model_name": "jina-reranker-v2",
            "api_base": "",
            "description": "Xinference Jina Reranker V2",
            "top_k": 10,
            "timeout": 60
        }
    }
    
    # 检索配置
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    similarity_threshold: float = 0.3
    
    # 重排序配置
    rerank_enabled: bool = True
    rerank_initial_top_k_multiplier: float = 2.0  # 初始检索数量的倍数
    
    # 文件上传配置
    upload_directory: str = "./data/uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = [".pdf", ".docx", ".txt", ".md"]
    
    # 安全配置
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

    def __init__(self):
        super().__init__()
        # 确保数据目录存在
        os.makedirs(self.chroma_persist_directory, exist_ok=True)
        os.makedirs(self.upload_directory, exist_ok=True)

settings = Settings() 