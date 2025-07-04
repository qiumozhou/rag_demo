import os
import tempfile
import logging
import time
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..services.rag_service import RAGService
from ..models.schemas import (
    QueryRequest, QueryResponse, SystemStatus, 
    FileUploadResponse, BatchQueryRequest, BatchQueryResponse,
    ErrorResponse
)
from ..core.config import settings

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

# 全局RAG服务实例
rag_service = RAGService()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """上传文档到知识库"""
    try:
        # 验证文件
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 获取文件大小
        file_content = await file.read()
        file_size = len(file_content)
        
        # 验证文件格式和大小
        rag_service.document_processor.validate_file(file.filename, file_size)
        
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        # 处理文档
        start_time = time.time()
        result = await rag_service.add_document(tmp_file_path, file.filename)
        processing_time = time.time() - start_time
        
        return FileUploadResponse(
            filename=file.filename,
            file_size=file_size,
            document_id=result["id"],
            chunk_count=result["chunk_count"],
            processing_time=processing_time
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"文档上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail="文档处理失败")

@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """查询知识库"""
    try:
        response = await rag_service.query(request)
        return response
        
    except Exception as e:
        logger.error(f"查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail="查询处理失败")

@router.post("/batch_query", response_model=BatchQueryResponse)
async def batch_query_knowledge_base(request: BatchQueryRequest):
    """批量查询知识库"""
    try:
        start_time = time.time()
        
        results = []
        for question in request.questions:
            query_req = QueryRequest(question=question, top_k=request.top_k)
            response = await rag_service.query(query_req)
            results.append(response)
        
        total_time = time.time() - start_time
        
        return BatchQueryResponse(
            results=results,
            total_time=total_time
        )
        
    except Exception as e:
        logger.error(f"批量查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail="批量查询处理失败")

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """获取系统状态"""
    try:
        status = rag_service.get_system_status()
        return SystemStatus(**status)
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail="无法获取系统状态")

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """删除指定文档"""
    try:
        success = await rag_service.vector_store.delete_document(document_id)
        
        if success:
            return {"message": f"文档 {document_id} 删除成功"}
        else:
            raise HTTPException(status_code=404, detail="文档不存在")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail="删除文档失败")

@router.delete("/documents")
async def clear_knowledge_base():
    """清空整个知识库"""
    try:
        success = await rag_service.vector_store.clear_collection()
        
        if success:
            return {"message": "知识库已清空"}
        else:
            raise HTTPException(status_code=500, detail="清空知识库失败")
            
    except Exception as e:
        logger.error(f"清空知识库失败: {str(e)}")
        raise HTTPException(status_code=500, detail="清空知识库失败")

@router.get("/documents")
async def list_documents():
    """列出所有文档"""
    try:
        # 获取统计信息
        stats = rag_service.vector_store.get_collection_stats()
        
        # 检查是否有错误
        if "error" in stats:
            logger.error(f"获取集合统计失败: {stats['error']}")
            raise HTTPException(status_code=500, detail="获取文档列表失败")
        
        # 获取所有文档的详细信息
        documents = []
        if stats.get("total_documents", 0) > 0 and stats.get("total_chunks", 0) > 0:
            try:
                # 从向量存储中获取所有文档
                results = rag_service.vector_store.collection.get(
                    include=["documents", "metadatas"]
                )
                
                # 按文档ID/source分组
                doc_groups = {}
                for i, (content, metadata) in enumerate(zip(
                    results.get("documents", []),
                    results.get("metadatas", [])
                )):
                    group_key = metadata.get("document_id") or metadata.get("source") or f"doc_{i}"
                    if group_key not in doc_groups:
                        doc_groups[group_key] = {
                            "id": group_key,
                            "source": metadata.get("source", "未知文档"),
                            "file_type": metadata.get("file_type", ".txt"),
                            "chunk_count": 0,
                            "created_at": metadata.get("created_at", ""),
                            "content": content[:200] + "..." if len(content) > 200 else content
                        }
                    doc_groups[group_key]["chunk_count"] += 1
                
                documents = list(doc_groups.values())
            except Exception as e:
                logger.error(f"获取文档详情失败: {str(e)}")
                # 如果获取详情失败，至少返回统计信息
                documents = []
        
        return {
            "total_documents": stats.get("total_documents", 0),
            "total_chunks": stats.get("total_chunks", 0),
            "sources": stats.get("sources", {}),
            "embedding_model": stats.get("embedding_model", "unknown"),
            "documents": documents
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文档列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取文档列表失败")

@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version
    }

@router.get("/documents/{document_id}/chunks")
async def get_document_chunks(document_id: str):
    """获取指定文档的块信息"""
    try:
        # 从向量存储中获取文档块
        results = rag_service.vector_store.collection.get(
            where={"document_id": document_id},
            include=["documents", "metadatas"]
        )
        
        chunks = []
        for i, (content, metadata) in enumerate(zip(
            results.get("documents", []),
            results.get("metadatas", [])
        )):
            chunks.append({
                "content": content,
                "chunk_index": metadata.get("chunk_index", i),
                "chunk_size": len(content),
                "metadata": metadata
            })
        
        # 按块索引排序
        chunks.sort(key=lambda x: x["chunk_index"])
        
        return {
            "document_id": document_id,
            "total_chunks": len(chunks),
            "chunks": chunks
        }
        
    except Exception as e:
        logger.error(f"获取文档块失败 {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="获取文档块失败")

@router.post("/test_services")
async def test_services():
    """测试所有AI服务连接"""
    try:
        results = await rag_service.test_services()
        return {
            "embedding_service": results.get("embedding", False),
            "llm_service": results.get("llm", False),
            "overall_status": all(results.values())
        }
    except Exception as e:
        logger.error(f"服务测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail="服务测试失败") 