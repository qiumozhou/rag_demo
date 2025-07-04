import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const messages = ref([])
  const isLoading = ref(false)
  const systemStatus = ref({
    status: 'unknown',
    document_count: 0,
    chunk_count: 0,
    model_status: {},
    memory_usage: 0
  })
  const documents = ref({
    documents: [],
    sources: {},
    total_documents: 0,
    total_chunks: 0,
    chunks: []
  })

  // 计算属性
  const isSystemOnline = computed(() => systemStatus.value.status === 'running')
  const hasDocuments = computed(() => documents.value.total_documents > 0)
  const totalDocuments = computed(() => documents.value.total_documents)

  // 方法
  const addMessage = (message) => {
    messages.value.push({
      id: Date.now(),
      timestamp: new Date(),
      ...message
    })
  }

  const clearMessages = () => {
    messages.value = []
  }

  const sendMessage = async (question, options = {}) => {
    try {
      isLoading.value = true
      
      // 添加用户消息
      addMessage({
        type: 'user',
        content: question
      })

      // 发送API请求
      const response = await api.post('/query', {
        question,
        top_k: options.top_k || 5,
        use_rerank: options.use_rerank || false
      })

      // 添加AI回复
      addMessage({
        type: 'assistant',
        content: response.data.answer,
        sources: response.data.retrieved_chunks,
        confidence: response.data.confidence,
        response_time: response.data.response_time
      })

      return response.data
    } catch (error) {
      console.error('发送消息失败:', error)
      
      // 添加错误消息
      addMessage({
        type: 'error',
        content: '抱歉，发生了错误，请稍后重试。'
      })
      
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const batchQuery = async (questions, options = {}) => {
    try {
      isLoading.value = true
      
      const response = await api.post('/batch_query', {
        questions,
        top_k: options.top_k || 5
      })

      return response.data
    } catch (error) {
      console.error('批量查询失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const uploadDocument = async (file, onProgress) => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress) {
            const percent = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
            onProgress(percent)
          }
        }
      })

      // 刷新文档列表和系统状态
      await Promise.all([
        loadDocuments(),
        loadSystemStatus()
      ])

      return response.data
    } catch (error) {
      console.error('文档上传失败:', error)
      throw error
    }
  }

  const loadDocuments = async () => {
    try {
      const response = await api.get('/documents')
      documents.value = response.data
      return response.data
    } catch (error) {
      console.error('加载文档失败:', error)
      throw error
    }
  }

  const deleteDocument = async (documentId) => {
    try {
      await api.delete(`/documents/${documentId}`)
      
      // 刷新文档列表和系统状态
      await Promise.all([
        loadDocuments(),
        loadSystemStatus()
      ])
      
      return true
    } catch (error) {
      console.error('删除文档失败:', error)
      throw error
    }
  }

  const clearDocuments = async () => {
    try {
      await api.delete('/documents')
      
      // 刷新状态
      await Promise.all([
        loadDocuments(),
        loadSystemStatus()
      ])
      
      // 清空对话记录
      clearMessages()
      
      return true
    } catch (error) {
      console.error('清空文档失败:', error)
      throw error
    }
  }

  const loadSystemStatus = async () => {
    try {
      const response = await api.get('/status')
      systemStatus.value = response.data
      return response.data
    } catch (error) {
      console.error('加载系统状态失败:', error)
      systemStatus.value.status = 'error'
      throw error
    }
  }

  const checkHealth = async () => {
    try {
      const response = await api.get('/health')
      return response.data
    } catch (error) {
      console.error('健康检查失败:', error)
      throw error
    }
  }

  const loadDocumentChunks = async (documentId) => {
    try {
      const response = await api.get(`/documents/${documentId}/chunks`)
      return response.data
    } catch (error) {
      console.error('加载文档块失败:', error)
      throw error
    }
  }

  // 初始化数据
  const initialize = async () => {
    try {
      await Promise.all([
        loadSystemStatus(),
        loadDocuments()
      ])
    } catch (error) {
      console.error('初始化失败:', error)
    }
  }

  return {
    // 状态
    messages,
    isLoading,
    systemStatus,
    documents,
    
    // 计算属性
    isSystemOnline,
    hasDocuments,
    totalDocuments,
    
    // 方法
    addMessage,
    clearMessages,
    sendMessage,
    batchQuery,
    uploadDocument,
    loadDocuments,
    deleteDocument,
    clearDocuments,
    loadSystemStatus,
    checkHealth,
    loadDocumentChunks,
    initialize
  }
}) 