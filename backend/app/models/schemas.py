from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# 文档相关模型
class DocumentBase(BaseModel):
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="文档内容")
    file_type: str = Field(..., description="文件类型")
    source: Optional[str] = Field(None, description="文档来源")

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: str = Field(..., description="文档唯一标识")
    created_at: datetime = Field(..., description="创建时间")
    chunk_count: int = Field(..., description="分块数量")

# 查询相关模型
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500, description="用户查询问题")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="返回相关文档数量")
    use_rerank: Optional[bool] = Field(False, description="是否使用重排序")

class RetrievedChunk(BaseModel):
    content: str = Field(..., description="文档片段内容")
    source: str = Field(..., description="来源文档")
    score: float = Field(..., description="相似度分数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

class QueryResponse(BaseModel):
    question: str = Field(..., description="原始问题")
    answer: str = Field(..., description="生成的答案")
    retrieved_chunks: List[RetrievedChunk] = Field(..., description="检索到的相关文档片段")
    response_time: float = Field(..., description="响应时间(秒)")
    confidence: float = Field(..., description="置信度分数")

# 系统状态模型
class SystemStatus(BaseModel):
    status: str = Field(..., description="系统状态")
    document_count: int = Field(..., description="文档总数")
    chunk_count: int = Field(..., description="文档片段总数")
    model_status: Dict[str, str] = Field(..., description="模型加载状态")
    memory_usage: float = Field(..., description="内存使用率")

# 文件上传模型
class FileUploadResponse(BaseModel):
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    document_id: str = Field(..., description="生成的文档ID")
    chunk_count: int = Field(..., description="分块数量")
    processing_time: float = Field(..., description="处理时间")

# 错误响应模型
class ErrorResponse(BaseModel):
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误信息")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")

# 批量操作模型
class BatchQueryRequest(BaseModel):
    questions: List[str] = Field(..., min_items=1, max_items=10, description="批量查询问题列表")
    top_k: Optional[int] = Field(5, description="每个问题返回的文档数量")

class BatchQueryResponse(BaseModel):
    results: List[QueryResponse] = Field(..., description="批量查询结果")
    total_time: float = Field(..., description="总处理时间") 