import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.schema import Document
import numpy as np

from ..core.config import settings
from .remote_embedding import RemoteEmbeddingService

logger = logging.getLogger(__name__)

class VectorStore:
    """向量存储服务，负责文档向量化和相似性检索"""
    
    def __init__(self):
        self.embedding_service = None
        self.chroma_client = None
        self.collection = None
        self._initialize_store()
    
    def _initialize_store(self):
        """初始化向量存储"""
        try:
            # 初始化远程嵌入服务
            logger.info("初始化远程嵌入服务...")
            self.embedding_service = RemoteEmbeddingService()
            
            # 初始化Chroma客户端
            self.chroma_client = chromadb.PersistentClient(
                path=settings.chroma_persist_directory,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            # 获取或创建集合
            self.collection = self.chroma_client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"description": "RAG Knowledge Base Collection"}
            )
            
            logger.info("向量存储初始化成功")
            
        except Exception as e:
            logger.error(f"向量存储初始化失败: {str(e)}")
            raise
    
    async def add_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """添加文档到向量存储"""
        try:
            if not documents:
                return {"added_count": 0}
            
            # 提取文本内容
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            # 生成唯一ID
            ids = [f"{doc.metadata.get('document_id', 'unknown')}_{doc.metadata.get('chunk_index', i)}" 
                   for i, doc in enumerate(documents)]
            
            # 生成嵌入向量
            logger.info(f"生成 {len(texts)} 个文档块的嵌入向量")
            embeddings = await self.embedding_service.encode(texts)
            embeddings_list = embeddings.tolist()
            
            # 添加到Chroma
            self.collection.add(
                embeddings=embeddings_list,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"成功添加 {len(documents)} 个文档块到向量存储")
            
            return {
                "added_count": len(documents),
                "collection_size": self.collection.count()
            }
            
        except Exception as e:
            logger.error(f"添加文档到向量存储失败: {str(e)}")
            raise
    
    async def similarity_search(
        self, 
        query: str, 
        top_k: int = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """相似性检索"""
        try:
            top_k = top_k or settings.top_k
            
            # 生成查询向量
            query_embedding = await self.embedding_service.encode_single(query)
            query_embedding_list = query_embedding.tolist()
            
            # 构建查询参数
            query_params = {
                "query_embeddings": [query_embedding_list],
                "n_results": top_k,
                "include": ["documents", "metadatas", "distances"]
            }
            
            # 添加过滤条件
            if filter_metadata:
                query_params["where"] = filter_metadata
            
            # 执行检索
            results = self.collection.query(**query_params)
            
            # 处理结果
            retrieved_docs = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0], 
                    results["distances"][0]
                )):
                    # 转换距离为相似度分数 (距离越小，相似度越高)
                    similarity_score = 1 / (1 + distance)
                    
                    # 过滤低相似度结果
                    if similarity_score >= settings.similarity_threshold:
                        retrieved_docs.append({
                            "content": doc,
                            "metadata": metadata,
                            "score": float(similarity_score),
                            "source": metadata.get("source", "unknown"),
                            "document_id": metadata.get("document_id"),
                            "chunk_index": metadata.get("chunk_index")
                        })
            
            logger.info(f"检索到 {len(retrieved_docs)} 个相关文档块")
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"相似性检索失败: {str(e)}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """删除指定文档的所有块"""
        try:
            # 查找该文档的所有块
            results = self.collection.get(
                where={"document_id": document_id},
                include=["metadatas"]
            )
            
            if results["ids"]:
                # 删除所有相关块
                self.collection.delete(ids=results["ids"])
                logger.info(f"成功删除文档 {document_id} 的 {len(results['ids'])} 个块")
                return True
            else:
                logger.warning(f"未找到文档 {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除文档失败 {document_id}: {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            total_count = self.collection.count()
            
            # 如果集合为空，返回默认值
            if total_count == 0:
                return {
                    "total_chunks": 0,
                    "total_documents": 0,
                    "sources": {},
                    "embedding_model": settings.ai_config["embedding"]["model_name"]
                }
            
            # 获取文档源统计
            results = self.collection.get(include=["metadatas"])
            sources = {}
            document_ids = set()
            
            for metadata in results.get("metadatas", []):
                source = metadata.get("source", "unknown")
                sources[source] = sources.get(source, 0) + 1
                document_ids.add(metadata.get("document_id", metadata.get("source", "unknown")))
            
            return {
                "total_chunks": total_count,
                "total_documents": len(document_ids),
                "sources": sources,
                "embedding_model": settings.ai_config["embedding"]["model_name"]
            }
            
        except Exception as e:
            logger.error(f"获取集合统计失败: {str(e)}")
            return {
                "total_chunks": 0,
                "total_documents": 0,
                "sources": {},
                "embedding_model": "unknown",
                "error": str(e)
            }
    
    async def clear_collection(self) -> bool:
        """清空整个集合"""
        try:
            # 删除并重新创建集合
            self.chroma_client.delete_collection(settings.chroma_collection_name)
            self.collection = self.chroma_client.create_collection(
                name=settings.chroma_collection_name,
                metadata={"description": "RAG Knowledge Base Collection"}
            )
            logger.info("成功清空向量存储集合")
            return True
            
        except Exception as e:
            logger.error(f"清空集合失败: {str(e)}")
            raise
    
    async def test_embedding_service(self) -> bool:
        """测试嵌入服务连接"""
        if self.embedding_service:
            return await self.embedding_service.test_connection()
        return False 