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
                    original_score = doc.get("score", 0.0)
                    rerank_score = result.score
                    
                    # 保存原始分数和重排序分数
                    doc["rerank_score"] = rerank_score
                    doc["original_score"] = original_score
                    
                    # 使用加权组合分数而不是完全替换
                    # 这样既保留了初检的语义信息，又利用了重排序的优势
                    rerank_weight = settings.rerank_score_weight
                    original_weight = settings.original_score_weight
                    combined_score = rerank_weight * rerank_score + original_weight * original_score
                    doc["score"] = combined_score
                    doc["score_type"] = "rerank_combined"
                    
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
    
    def analyze_rerank_performance(self, original_docs: List[Dict[str, Any]], reranked_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析重排序性能，检测是否破坏了排序效果
        
        Args:
            original_docs: 原始排序的文档
            reranked_docs: 重排序后的文档
            
        Returns:
            性能分析结果
        """
        if not original_docs or not reranked_docs:
            return {"status": "no_data"}
        
        analysis = {
            "total_docs": len(original_docs),
            "reranked_docs": len(reranked_docs),
            "rerank_changes": 0,
            "score_improvements": 0,
            "position_changes": [],
            "avg_score_change": 0.0,
            "top_position_stability": 0.0
        }
        
        # 创建原始文档的位置映射
        original_positions = {doc.get("source", f"doc_{i}"): i for i, doc in enumerate(original_docs)}
        
        # 分析位置变化
        position_changes = []
        score_changes = []
        
        for new_pos, doc in enumerate(reranked_docs):
            doc_id = doc.get("source", f"doc_{new_pos}")
            original_pos = original_positions.get(doc_id, -1)
            
            if original_pos != -1 and original_pos != new_pos:
                analysis["rerank_changes"] += 1
                change = {
                    "doc_id": doc_id,
                    "original_position": original_pos,
                    "new_position": new_pos,
                    "position_change": original_pos - new_pos,  # 负值表示排名提升
                    "original_score": doc.get("original_score", 0.0),
                    "rerank_score": doc.get("rerank_score", 0.0),
                    "combined_score": doc.get("score", 0.0)
                }
                position_changes.append(change)
                
                # 计算分数变化
                if doc.get("rerank_score", 0) > doc.get("original_score", 0):
                    analysis["score_improvements"] += 1
                
                score_change = doc.get("score", 0) - doc.get("original_score", 0)
                score_changes.append(score_change)
        
        analysis["position_changes"] = position_changes
        
        # 计算平均分数变化
        if score_changes:
            analysis["avg_score_change"] = sum(score_changes) / len(score_changes)
        
        # 计算TOP位置稳定性（前3位的变化程度）
        top_k = min(3, len(reranked_docs))
        top_stable = 0
        for i in range(top_k):
            if i < len(original_docs):
                original_top_doc = original_docs[i].get("source", f"doc_{i}")
                reranked_top_doc = reranked_docs[i].get("source", f"doc_{i}")
                if original_top_doc == reranked_top_doc:
                    top_stable += 1
        
        analysis["top_position_stability"] = top_stable / top_k if top_k > 0 else 0.0
        
        # 评估重排序质量
        if analysis["avg_score_change"] > 0.1 and analysis["score_improvements"] > len(reranked_docs) * 0.3:
            analysis["quality_assessment"] = "good"
        elif analysis["avg_score_change"] > 0:
            analysis["quality_assessment"] = "moderate"
        else:
            analysis["quality_assessment"] = "poor"
        
        return analysis
    
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