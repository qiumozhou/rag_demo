import logging
import time
from typing import List, Dict, Any, Optional

from .vector_store import VectorStore
from .document_processor import DocumentProcessor
from .remote_llm import RemoteLLMService
from .reranker_service import RerankerService
from ..models.schemas import QueryRequest, QueryResponse, RetrievedChunk
from ..core.config import settings

logger = logging.getLogger(__name__)

class RAGService:
    """RAG核心服务，整合检索增强生成功能"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.document_processor = DocumentProcessor()
        self.llm_service = None
        self.reranker_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """初始化各种服务"""
        # 初始化语言模型
        try:
            logger.info("初始化远程LLM服务...")
            self.llm_service = RemoteLLMService()
            logger.info("远程LLM服务初始化成功")
            
        except Exception as e:
            logger.error(f"远程LLM服务初始化失败: {str(e)}")
            self.llm_service = None
            logger.warning("将使用基于检索的简单回答模式")
        
        # 初始化重排序服务
        try:
            logger.info("初始化重排序服务...")
            self.reranker_service = RerankerService()
            
            if self.reranker_service.is_enabled():
                logger.info("重排序服务初始化成功")
            else:
                logger.info("重排序服务已禁用")
                self.reranker_service = None
                
        except Exception as e:
            logger.error(f"重排序服务初始化失败: {str(e)}")
            self.reranker_service = None
            logger.warning("将跳过重排序步骤")
    
    async def query(self, request: QueryRequest) -> QueryResponse:
        """处理用户查询，返回RAG结果"""
        start_time = time.time()
        
        try:
            # 1. 向量检索相关文档（如果启用重排序，使用更大的top_k进行初步检索）
            if self.reranker_service and self.reranker_service.is_enabled():
                initial_top_k = int(request.top_k * settings.rerank_initial_top_k_multiplier)
                logger.info(f"启用重排序，初始检索数量: {initial_top_k}")
            else:
                initial_top_k = request.top_k
                logger.info(f"未启用重排序，检索数量: {initial_top_k}")
                
            retrieved_docs = await self.vector_store.similarity_search(
                query=request.question,
                top_k=initial_top_k
            )
            
            if not retrieved_docs:
                return QueryResponse(
                    question=request.question,
                    answer="抱歉，没有找到相关信息来回答您的问题。请尝试重新表述或上传相关文档。",
                    retrieved_chunks=[],
                    response_time=time.time() - start_time,
                    confidence=0.0
                )
            
            # 2. 重排序（如果服务可用且启用）
            if self.reranker_service and self.reranker_service.is_enabled():
                logger.info(f"使用重排序服务对 {len(retrieved_docs)} 个文档进行重新排序")
                
                # 保存原始文档用于性能分析
                original_docs = retrieved_docs.copy()
                
                retrieved_docs = await self.reranker_service.rerank_documents(
                    query=request.question,
                    documents=retrieved_docs,
                    top_k=request.top_k
                )
                logger.info(f"重排序完成，最终使用 {len(retrieved_docs)} 个文档")
                
                # 可选：分析重排序性能（在调试模式下）
                if settings.debug:
                    performance_analysis = self.reranker_service.analyze_rerank_performance(
                        original_docs, retrieved_docs
                    )
                    logger.debug(f"重排序性能分析: {performance_analysis}")
            else:
                # 如果没有重排序服务，直接截取前top_k个文档
                retrieved_docs = retrieved_docs[:request.top_k]
                logger.info(f"跳过重排序，使用前 {len(retrieved_docs)} 个文档")
            
            # 3. 构建上下文
            context = self._build_context(retrieved_docs)
            
            # 4. 生成回答
            answer = await self._generate_answer(request.question, context)
            
            # 5. 计算置信度
            confidence = self._calculate_confidence(retrieved_docs, answer)
            
            # 6. 构建响应
            retrieved_chunks = [
                RetrievedChunk(
                    content=doc["content"],
                    source=doc["source"],
                    score=doc["score"],
                    metadata=doc["metadata"]
                )
                for doc in retrieved_docs
            ]
            
            response_time = time.time() - start_time
            
            logger.info(f"查询处理完成，耗时: {response_time:.2f}秒")
            
            return QueryResponse(
                question=request.question,
                answer=answer,
                retrieved_chunks=retrieved_chunks,
                response_time=response_time,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"查询处理失败: {str(e)}")
            return QueryResponse(
                question=request.question,
                answer=f"抱歉，处理您的查询时发生错误: {str(e)}",
                retrieved_chunks=[],
                response_time=time.time() - start_time,
                confidence=0.0
            )
    
    def _build_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """构建上下文信息"""
        context_parts = []
        for i, doc in enumerate(retrieved_docs):
            # 如果有重排序分数，显示它
            score_info = f"(相关度: {doc['score']:.4f}"
            if 'rerank_score' in doc and 'original_score' in doc:
                score_info += f", 重排序分数: {doc['rerank_score']:.4f}, 原始分数: {doc['original_score']:.4f}"
            score_info += ")"
            
            context_parts.append(f"相关信息 {i+1} {score_info}:\n{doc['content']}\n")
        
        return "\n".join(context_parts)
    
    async def _generate_answer(self, question: str, context: str) -> str:
        """生成答案"""
        if self.llm_service is None:
            # 简单的基于检索的回答
            return self._simple_retrieval_answer(question, context)
        
        try:
            # 使用远程LLM生成回答
            answer = await self.llm_service.generate_with_context(question, context)
            return answer
            
        except Exception as e:
            logger.error(f"LLM生成失败: {str(e)}")
            return self._simple_retrieval_answer(question, context)
    
    def _simple_retrieval_answer(self, question: str, context: str) -> str:
        """基于检索的简单回答生成"""
        if not context.strip():
            return "抱歉，没有找到相关信息来回答您的问题。"
        
        # 提取最相关的段落作为答案
        lines = context.split('\n')
        relevant_lines = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10]
        
        if relevant_lines:
            # 返回前几个最相关的段落
            answer_parts = relevant_lines[:3]  # 取前3个段落
            answer = "\n\n".join(answer_parts)
            
            # 添加前缀说明
            answer = f"根据文档内容，{answer}"
            
            return answer
        
        return "找到了相关文档，但无法提取有效信息来回答您的问题。"
    
    def _calculate_confidence(self, retrieved_docs: List[Dict[str, Any]], answer: str) -> float:
        """计算回答的置信度"""
        if not retrieved_docs:
            return 0.0
        
        # 基于检索文档的平均相似度分数
        avg_score = sum(doc["score"] for doc in retrieved_docs) / len(retrieved_docs)
        
        # 基于检索到的文档数量
        doc_count_factor = min(len(retrieved_docs) / settings.top_k, 1.0)
        
        # 基于答案长度（过短或过长都降低置信度）
        answer_length = len(answer.strip())
        if answer_length < 10:
            length_factor = 0.3
        elif answer_length > 500:
            length_factor = 0.8
        else:
            length_factor = 1.0
        
        # 如果使用了重排序，给予额外的置信度加成
        rerank_bonus = 1.1 if any('rerank_score' in doc for doc in retrieved_docs) else 1.0
        
        # 综合计算置信度
        confidence = avg_score * doc_count_factor * length_factor * rerank_bonus
        
        return min(confidence, 0.95)  # 最高置信度不超过95%
    
    async def add_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """添加文档到知识库"""
        try:
            # 处理文档
            doc_info = await self.document_processor.process_file(file_path, filename)
            
            # 添加到向量存储
            store_result = await self.vector_store.add_documents(doc_info["chunks"])
            
            # 清理临时文件
            await self.document_processor.cleanup_temp_file(file_path)
            
            return {
                **doc_info,
                "vector_store_result": store_result
            }
            
        except Exception as e:
            # 确保清理临时文件
            await self.document_processor.cleanup_temp_file(file_path)
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            # 获取向量存储统计
            vector_stats = self.vector_store.get_collection_stats()
            
            # 模型状态
            model_status = {
                "embedding_model": "loaded" if self.vector_store.embedding_service else "error",
                "llm_model": "loaded" if self.llm_service else "fallback",
                "reranker_model": "loaded" if (self.reranker_service and self.reranker_service.is_enabled()) else "disabled"
            }
            
            return {
                "status": "running",
                "document_count": vector_stats.get("total_documents", 0),
                "chunk_count": vector_stats.get("total_chunks", 0),
                "model_status": model_status,
                "memory_usage": 0.0,  # 远程服务不占用本地内存
                "vector_store_stats": vector_stats,
                "rerank_enabled": self.reranker_service and self.reranker_service.is_enabled()
            }
            
        except Exception as e:
            logger.error(f"获取系统状态失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def test_services(self) -> Dict[str, bool]:
        """测试所有服务连接"""
        results = {}
        
        # 测试嵌入服务
        try:
            results["embedding"] = await self.vector_store.test_embedding_service()
        except Exception as e:
            logger.error(f"嵌入服务测试失败: {str(e)}")
            results["embedding"] = False
        
        # 测试LLM服务
        try:
            results["llm"] = await self.llm_service.test_connection() if self.llm_service else False
        except Exception as e:
            logger.error(f"LLM服务测试失败: {str(e)}")
            results["llm"] = False
        
        # 测试重排序服务
        try:
            results["reranker"] = self.reranker_service.test_connection() if (self.reranker_service and self.reranker_service.is_enabled()) else False
        except Exception as e:
            logger.error(f"重排序服务测试失败: {str(e)}")
            results["reranker"] = False
        
        return results 