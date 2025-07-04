"""
重排序服务

用于对检索结果进行重新排序，提高相关性
参考通用重排序模型实现，提供多种格式兼容性
"""

import logging
import time
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ..core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RerankResult:
    """重排序结果"""
    index: int
    score: float
    text: str
    metadata: Optional[Dict[str, Any]] = None


class RerankerService:
    """重排序服务，用于对检索结果进行重新排序"""
    
    def __init__(self):
        self.config = settings.ai_config["rerank"]
        self.enabled = self.config.get("enabled", True) and settings.rerank_enabled
        
        if not self.enabled:
            logger.info("重排序服务已禁用")
            return
            
        self.api_base = self.config["api_base"]
        self.model_name = self.config["model_name"]
        self.top_k = self.config["top_k"]
        self.timeout = self.config.get("timeout", 60)
        
    def is_enabled(self) -> bool:
        """检查重排序服务是否启用"""
        return self.enabled
        
    async def rerank_documents(self, query: str, documents: List[Dict[str, Any]], top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        对检索到的文档进行重排序
        
        Args:
            query: 用户查询
            documents: 检索到的文档列表
            top_k: 返回的文档数量，默认使用配置中的值
            
        Returns:
            重排序后的文档列表
        """
        if not self.enabled:
            logger.warning("重排序服务未启用，返回原始文档")
            return documents[:top_k] if top_k else documents
            
        if not documents:
            return []
            
        if top_k is None:
            top_k = self.top_k
            
        # 如果文档数量少于等于top_k，直接返回
        if len(documents) <= top_k:
            logger.info(f"文档数量({len(documents)})不超过top_k({top_k})，跳过重排序")
            return documents
            
        try:
            # 提取文档内容
            doc_texts = [doc["content"] for doc in documents]
            
            # 调用重排序
            rerank_results = self._http_rerank(query, doc_texts, top_k)
            
            # 转换回原始文档格式
            reranked_documents = []
            for result in rerank_results:
                if 0 <= result.index < len(documents):
                    doc = documents[result.index].copy()
                    doc["rerank_score"] = result.score
                    doc["original_score"] = doc.get("score", 0.0)
                    doc["score"] = result.score  # 使用重排序分数作为主要分数
                    reranked_documents.append(doc)
                    
            if reranked_documents:
                logger.info(f"重排序成功，返回 {len(reranked_documents)} 个文档")
                return reranked_documents
            else:
                logger.warning("重排序结果为空，返回原始文档")
                return documents[:top_k]
                
        except Exception as e:
            logger.error(f"重排序过程中发生错误: {str(e)}")
            return documents[:top_k]  # 发生错误时返回原始排序的前top_k个文档
    
    def _http_rerank(self, query: str, documents: List[str], top_k: int) -> List[RerankResult]:
        """
        使用 HTTP API 重排序
        参考通用HTTPRerank实现，支持多种请求格式
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        # 优先使用兼容性最好的请求格式
        request_formats = [
            # 格式1: 标准格式，包含model
            {
                "model": self.model_name,
                "query": query,
                "documents": documents,
                "top_n": top_k
            },
            # 格式2: 使用top_k而不是top_n
            {
                "model": self.model_name,
                "query": query,
                "documents": documents,
                "top_k": top_k
            },
            # 格式3: 不包含model参数
            {
                "query": query,
                "documents": documents,
                "top_n": top_k
            },
            # 格式4: 最简格式
            {
                "query": query,
                "documents": documents
            }
        ]
        
        last_error = None
        max_retries = 2
        retry_delay = 1  # seconds
        
        for i, data in enumerate(request_formats):
            for attempt in range(1, max_retries + 1):
                try:
                    logger.debug(f"尝试请求格式 {i+1}（第{attempt}次）: {list(data.keys())}")
                    
                    response = requests.post(
                        self.api_base,
                        headers=headers,
                        json=data,
                        timeout=self.timeout
                    )
                    
                    logger.debug(f"响应状态码: {response.status_code}")
                    
                    if response.status_code == 500:
                        try:
                            error_info = response.json()
                            logger.warning(f"格式 {i+1} 服务器错误: {error_info}")
                        except Exception:
                            logger.warning(f"格式 {i+1} 服务器错误: {response.text}")
                        
                        # 500错误，尝试下一个格式或重试
                        if i < len(request_formats) - 1:
                            break
                        elif attempt < max_retries:
                            logger.info(f"500错误，等待{retry_delay}秒后重试...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            break
                    
                    response.raise_for_status()
                    result_data = response.json()
                    logger.debug(f"响应数据结构: {type(result_data)}")
                    
                    # 解析响应结果
                    results = self._parse_rerank_response(result_data, documents, top_k)
                    
                    if results:
                        logger.info(f"使用格式 {i+1} 成功获取 {len(results)} 个重排序结果")
                        return results
                    else:
                        logger.warning(f"格式 {i+1} 返回空结果")
                        break
                        
                except requests.exceptions.RequestException as e:
                    last_error = e
                    logger.warning(f"请求格式 {i+1} 网络请求失败（第{attempt}次）: {e}")
                except Exception as e:
                    last_error = e
                    logger.warning(f"处理格式 {i+1} 响应时出错（第{attempt}次）: {e}")
                
                # 重试或切换格式
                if attempt < max_retries:
                    logger.info(f"等待{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                elif i < len(request_formats) - 1:
                    logger.info(f"尝试下一种请求格式...")
                    break
                else:
                    break
        
        # 全部失败，返回降序默认分数
        logger.error(f"所有请求格式都失败，最后一个错误: {last_error}")
        return [
            RerankResult(index=i, score=1.0/(i+1), text=doc)
            for i, doc in enumerate(documents[:top_k])
        ]
    
    def _parse_rerank_response(self, result_data: Any, documents: List[str], top_k: int) -> List[RerankResult]:
        """解析不同格式的重排序响应"""
        results = []
        
        try:
            # 格式1: {"results": [{"index": 0, "relevance_score": 0.8}, ...]}
            if isinstance(result_data, dict) and "results" in result_data:
                for result in result_data["results"]:
                    idx = result.get("index", 0)
                    score = result.get("relevance_score", result.get("score", 0.0))
                    text = documents[idx] if 0 <= idx < len(documents) else ""
                    results.append(RerankResult(index=idx, score=score, text=text))
            
            # 格式2: {"rankings": [{"index": 0, "score": 0.8}, ...]}
            elif isinstance(result_data, dict) and "rankings" in result_data:
                for rank in result_data["rankings"]:
                    idx = rank.get("index", 0)
                    score = rank.get("score", 0.0)
                    text = documents[idx] if 0 <= idx < len(documents) else ""
                    results.append(RerankResult(index=idx, score=score, text=text))
            
            # 格式3: {"data": [{"index": 0, "relevance_score": 0.8}, ...]}
            elif isinstance(result_data, dict) and "data" in result_data:
                for result in result_data["data"]:
                    idx = result.get("index", 0)
                    score = result.get("relevance_score", result.get("score", 0.0))
                    text = documents[idx] if 0 <= idx < len(documents) else ""
                    results.append(RerankResult(index=idx, score=score, text=text))
            
            # 格式4: 直接返回列表 [{"index": 0, "score": 0.8}, ...]
            elif isinstance(result_data, list):
                for j, result in enumerate(result_data):
                    if isinstance(result, dict):
                        idx = result.get("index", j)
                        score = result.get("score", result.get("relevance_score", 1.0/(j+1)))
                        text = documents[idx] if 0 <= idx < len(documents) else ""
                        results.append(RerankResult(index=idx, score=score, text=text))
            
            else:
                logger.warning(f"未知响应格式: {type(result_data)}")
                return []
            
            # 排序并限制数量
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"解析重排序响应失败: {e}")
            return []
    
    async def test_connection(self) -> bool:
        """测试重排序服务连接"""
        if not self.enabled:
            logger.info("重排序服务未启用，跳过连接测试")
            return False
            
        try:
            # 使用简单的测试调用
            test_docs = ["这是一个测试文档"]
            results = self._http_rerank("测试查询", test_docs, 1)
            
            if results and len(results) > 0:
                logger.info("重排序服务连接测试成功")
                return True
            else:
                logger.error("重排序服务连接测试失败：返回空结果")
                return False
                
        except Exception as e:
            logger.error(f"重排序服务连接测试失败: {str(e)}")
            return False 