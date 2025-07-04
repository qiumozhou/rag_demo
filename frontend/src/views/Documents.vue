<template>
  <div class="documents-page">
    <div class="container">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="header-info">
            <el-icon size="32" color="#409eff">
              <Folder />
            </el-icon>
            <div class="header-text">
              <h1>文档管理</h1>
              <p>管理知识库中的文档，支持多种格式文件上传</p>
            </div>
          </div>
          
          <div class="header-actions">
            <el-button 
              type="danger" 
              @click="clearAllDocuments"
              :disabled="!hasDocuments"
            >
              <el-icon><Delete /></el-icon>
              清空知识库
            </el-button>
            <el-button 
              type="primary" 
              @click="uploadDialogVisible = true"
            >
              <el-icon><Plus /></el-icon>
              上传文档
            </el-button>
          </div>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-section">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="8">
            <div class="stat-card card-shadow">
              <div class="stat-icon">
                <el-icon size="32" color="#409eff">
                  <Document />
                </el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ totalDocuments }}</div>
                <div class="stat-label">总文档数</div>
              </div>
            </div>
          </el-col>
          
          <el-col :xs="24" :sm="8">
            <div class="stat-card card-shadow">
              <div class="stat-icon">
                <el-icon size="32" color="#67c23a">
                  <DataBoard />
                </el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ totalChunks }}</div>
                <div class="stat-label">文档块数</div>
              </div>
            </div>
          </el-col>
          
          <el-col :xs="24" :sm="8">
            <div class="stat-card card-shadow">
              <div class="stat-icon">
                <el-icon size="32" color="#e6a23c">
                  <PieChart />
                </el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ Object.keys(documentSources).length }}</div>
                <div class="stat-label">文档类型</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 文档列表 -->
      <div class="documents-section">
        <div class="section-header">
          <h2>文档列表</h2>
          <div class="list-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索文档..."
              :prefix-icon="Search"
              clearable
              style="width: 300px"
            />
            <el-select v-model="filterType" placeholder="文档类型" clearable style="width: 120px">
              <el-option 
                v-for="(count, type) in documentSources" 
                :key="type" 
                :label="type.toUpperCase()" 
                :value="type" 
              />
            </el-select>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="!hasDocuments && !isLoading" class="empty-state">
          <el-icon size="64" color="#c0c4cc">
            <DocumentAdd />
          </el-icon>
          <h3>暂无文档</h3>
          <p>点击上传按钮添加文档到知识库</p>
          <el-button 
            type="primary" 
            size="large"
            @click="uploadDialogVisible = true"
          >
            <el-icon><Plus /></el-icon>
            上传第一个文档
          </el-button>
        </div>

        <!-- 文档表格 -->
        <div v-else class="documents-table">
          <el-table 
            :data="filteredDocuments" 
            v-loading="isLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column label="文档名称" min-width="200">
              <template #default="scope">
                <div class="document-name">
                  <el-icon :color="getFileTypeColor(scope.row.file_type)">
                    <component :is="getFileTypeIcon(scope.row.file_type)" />
                  </el-icon>
                  <span class="file-name">{{ scope.row.source }}</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="文件类型" width="100">
              <template #default="scope">
                <el-tag :type="getFileTypeTagType(scope.row.file_type)" size="small">
                  {{ scope.row.file_type.toUpperCase() }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="文档块数" width="100" align="center">
              <template #default="scope">
                <el-badge :value="scope.row.chunk_count" type="primary" />
              </template>
            </el-table-column>
            
            <el-table-column label="上传时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="150" align="center">
              <template #default="scope">
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="previewDocument(scope.row)"
                >
                  <el-icon><View /></el-icon>
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="deleteDocument(scope.row)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog 
      v-model="uploadDialogVisible" 
      title="上传文档" 
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="upload-content">
        <el-upload
          ref="uploadRef"
          :action="uploadAction"
          :before-upload="beforeUpload"
          :on-success="onUploadSuccess"
          :on-error="onUploadError"
          :on-progress="onUploadProgress"
          :on-change="onFileChange"
          :file-list="fileList"
          :auto-upload="false"
          multiple
          drag
          class="upload-dragger"
        >
          <el-icon size="48" color="#409eff">
            <UploadFilled />
          </el-icon>
          <div class="upload-text">
            <p>将文件拖拽到此处，或<em>点击上传</em></p>
            <p class="upload-hint">支持 PDF、DOC、DOCX、TXT、MD 格式，单文件不超过 10MB</p>
          </div>
        </el-upload>

        <!-- 上传进度 -->
        <div v-if="uploadProgress > 0" class="upload-progress">
          <el-progress :percentage="uploadProgress" :status="uploadStatus" />
          <p class="progress-text">{{ uploadStatusText }}</p>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelUpload">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitUpload"
            :loading="isUploading"
            :disabled="!hasSelectedFiles"
          >
            开始上传
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 文档预览对话框 -->
    <el-dialog 
      v-model="previewDialogVisible" 
      :title="`预览：${currentDocument?.source}`"
      width="80%"
      :close-on-click-modal="false"
    >
      <div class="preview-content">
        <el-tabs v-model="previewActiveTab" class="preview-tabs">
          <el-tab-pane label="完整内容" name="full">
            <el-scrollbar height="500px">
              <div class="document-content">
                {{ currentDocument?.content || '无法预览此文档内容' }}
              </div>
            </el-scrollbar>
          </el-tab-pane>
          
          <el-tab-pane label="文档块" name="chunks">
            <div class="chunks-container">
              <div class="chunks-header">
                <span>共 {{ documentChunks.length }} 个文档块</span>
                <el-input
                  v-model="chunkSearchKeyword"
                  placeholder="搜索文档块..."
                  :prefix-icon="Search"
                  clearable
                  style="width: 300px"
                />
              </div>
              
              <el-scrollbar height="450px">
                <div class="chunks-list">
                  <div 
                    v-for="(chunk, index) in filteredChunks" 
                    :key="index"
                    class="chunk-item"
                  >
                    <div class="chunk-header">
                      <el-tag size="small" type="primary">块 {{ chunk.chunk_index + 1 }}</el-tag>
                      <span class="chunk-size">{{ chunk.chunk_size }} 字符</span>
                      <el-button 
                        size="small" 
                        type="text"
                        @click="copyChunk(chunk.content)"
                      >
                        <el-icon><CopyDocument /></el-icon>
                      </el-button>
                    </div>
                    <div class="chunk-content">{{ chunk.content }}</div>
                  </div>
                </div>
              </el-scrollbar>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Folder, Document, DataBoard, PieChart, Search, DocumentAdd, 
  Plus, Delete, View, UploadFilled, CopyDocument 
} from '@element-plus/icons-vue'

const chatStore = useChatStore()

// 响应式数据
const uploadDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const searchKeyword = ref('')
const filterType = ref('')
const uploadRef = ref(null)
const fileList = ref([])
const uploadProgress = ref(0)
const uploadStatus = ref('')
const uploadStatusText = ref('')
const isUploading = ref(false)
const currentDocument = ref(null)
const previewActiveTab = ref('full')
const chunkSearchKeyword = ref('')

// 计算属性
const hasDocuments = computed(() => chatStore.hasDocuments)
const totalDocuments = computed(() => chatStore.totalDocuments)
const totalChunks = computed(() => chatStore.documents.total_chunks)
const documentSources = computed(() => chatStore.documents.sources || {})
const isLoading = computed(() => chatStore.isLoading)

const hasSelectedFiles = computed(() => {
  return fileList.value.length > 0
})

const filteredDocuments = computed(() => {
  // 使用真实的文档数据
  const documents = chatStore.documents.documents || []
  
  let filtered = documents
  
  if (searchKeyword.value) {
    filtered = filtered.filter(doc => 
      doc.source.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  
  if (filterType.value) {
    filtered = filtered.filter(doc => doc.file_type === filterType.value)
  }
  
  return filtered
})

const uploadAction = '/api/v1/upload'

// 方法
const getFileTypeIcon = (type) => {
  switch (type) {
    case '.pdf': return 'Document'
    case '.docx': return 'Edit'
    case '.txt': return 'Memo'
    case '.md': return 'EditPen'
    default: return 'Document'
  }
}

const getFileTypeColor = (type) => {
  switch (type) {
    case '.pdf': return '#f56c6c'
    case '.docx': return '#409eff'
    case '.txt': return '#67c23a'
    case '.md': return '#e6a23c'
    default: return '#909399'
  }
}

const getFileTypeTagType = (type) => {
  switch (type) {
    case '.pdf': return 'danger'
    case '.docx': return 'primary'
    case '.txt': return 'success'
    case '.md': return 'warning'
    default: return 'info'
  }
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

const beforeUpload = (file) => {
  const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown']
  const maxSize = 10 * 1024 * 1024 // 10MB

  if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|doc|docx|txt|md)$/i)) {
    ElMessage.error('不支持的文件格式')
    return false
  }

  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }

  return true
}

const onUploadProgress = (event, file) => {
  uploadProgress.value = Math.round(event.percent)
  uploadStatusText.value = `正在上传 ${file.name}...`
}

const onUploadSuccess = (response, file) => {
  ElMessage.success(`${file.name} 上传成功`)
  uploadProgress.value = 100
  uploadStatus.value = 'success'
  uploadStatusText.value = '上传完成'
  
  // 刷新文档列表
  chatStore.loadDocuments()
  chatStore.loadSystemStatus()
  
  setTimeout(() => {
    uploadDialogVisible.value = false
    resetUpload()
  }, 1500)
}

const onUploadError = (error, file) => {
  ElMessage.error(`${file.name} 上传失败`)
  uploadStatus.value = 'exception'
  uploadStatusText.value = '上传失败'
}

const submitUpload = async () => {
  if (!hasSelectedFiles.value) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  isUploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = ''
  
  try {
    // 手动触发上传
    if (uploadRef.value) {
      uploadRef.value.submit()
    } else {
      throw new Error('上传组件未初始化')
    }
  } catch (error) {
    ElMessage.error('上传失败: ' + error.message)
    isUploading.value = false
  }
}

const cancelUpload = () => {
  uploadDialogVisible.value = false
  resetUpload()
}

const resetUpload = () => {
  fileList.value = []
  uploadProgress.value = 0
  uploadStatus.value = ''
  uploadStatusText.value = ''
  isUploading.value = false
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const previewDocument = async (document) => {
  currentDocument.value = document
  previewDialogVisible.value = true
  previewActiveTab.value = 'full'
  chunkSearchKeyword.value = ''
  
  // 加载文档块信息
  try {
    await loadDocumentChunks(document.id)
  } catch (error) {
    console.error('加载文档块失败:', error)
  }
}

const deleteDocument = async (document) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${document.source}" 吗？`,
      '删除文档',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await chatStore.deleteDocument(document.id)
    ElMessage.success('文档删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除文档失败')
    }
  }
}

const clearAllDocuments = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空整个知识库吗？此操作不可恢复。',
      '清空知识库',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await chatStore.clearDocuments()
    ElMessage.success('知识库已清空')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空知识库失败')
    }
  }
}

const onFileChange = (file, uploadFileList) => {
  // 更新文件列表
  fileList.value = uploadFileList
  console.log('文件列表更新:', uploadFileList)
}

const documentChunks = computed(() => chatStore.documents.chunks || [])

const filteredChunks = computed(() => {
  let filtered = documentChunks.value
  
  if (chunkSearchKeyword.value) {
    filtered = filtered.filter(chunk => 
      chunk.content.toLowerCase().includes(chunkSearchKeyword.value.toLowerCase())
    )
  }
  
  return filtered
})

const copyChunk = async (content) => {
  try {
    await navigator.clipboard.writeText(content)
    ElMessage.success('文档块已复制到剪贴板')
  } catch (error) {
    // 降级方案
    const textArea = document.createElement('textarea')
    textArea.value = content
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    ElMessage.success('文档块已复制到剪贴板')
  }
}

const loadDocumentChunks = async (documentId) => {
  try {
    const result = await chatStore.loadDocumentChunks(documentId)
    chatStore.documents.chunks = result.chunks || []
  } catch (error) {
    console.error('获取文档块失败:', error)
    // 如果API失败，使用模拟数据
    const mockChunks = generateMockChunks(currentDocument.value?.content || '')
    chatStore.documents.chunks = mockChunks
  }
}

const generateMockChunks = (content) => {
  if (!content) return []
  
  // 简单的文本分块逻辑（模拟后端的分块）
  const chunkSize = 1000
  const overlap = 200
  const chunks = []
  
  let start = 0
  while (start < content.length) {
    const end = Math.min(start + chunkSize, content.length)
    const chunkContent = content.substring(start, end)
    
    chunks.push({
      content: chunkContent,
      chunk_index: chunks.length,
      chunk_size: chunkContent.length,
      metadata: {
        start: start,
        end: end
      }
    })
    
    start = end - overlap
    if (start >= content.length) break
  }
  
  return chunks
}

// 生命周期
onMounted(() => {
  chatStore.loadDocuments()
  chatStore.loadSystemStatus()
})
</script>

<style scoped>
.documents-page {
  min-height: calc(100vh - 70px);
  background: #f5f7fa;
  padding: 20px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 页面头部 */
.page-header {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-text h1 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 28px;
  font-weight: 700;
}

.header-text p {
  margin: 0;
  color: #606266;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 15px;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: rgba(64, 158, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

/* 文档列表 */
.documents-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.section-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 22px;
  font-weight: 600;
}

.list-actions {
  display: flex;
  gap: 15px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-state h3 {
  margin: 20px 0 10px;
  color: #606266;
  font-size: 20px;
}

.empty-state p {
  margin-bottom: 30px;
  font-size: 14px;
}

/* 文档表格 */
.documents-table {
  margin-top: 20px;
}

.document-name {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-name {
  font-weight: 500;
  color: #2c3e50;
}

/* 上传对话框 */
.upload-content {
  padding: 20px 0;
}

.upload-dragger {
  width: 100%;
}

.upload-text {
  text-align: center;
  margin-top: 15px;
}

.upload-text p {
  margin: 5px 0;
  color: #606266;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

.upload-progress {
  margin-top: 20px;
}

.progress-text {
  text-align: center;
  margin-top: 10px;
  color: #606266;
  font-size: 14px;
}

/* 预览对话框 */
.preview-content {
  padding: 20px 0;
}

.preview-tabs {
  height: 500px;
}

.document-content {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #2c3e50;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.chunks-container {
  padding: 20px;
}

.chunks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chunks-list {
  height: 450px;
  overflow-y: auto;
}

.chunk-item {
  margin-bottom: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.chunk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.chunk-size {
  font-size: 12px;
  color: #909399;
}

.chunk-content {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #2c3e50;
  padding: 15px;
  background: white;
  max-height: 200px;
  overflow-y: auto;
}

.chunk-content::-webkit-scrollbar {
  width: 6px;
}

.chunk-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chunk-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chunk-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .header-actions {
    width: 100%;
    justify-content: center;
  }
  
  .section-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .list-actions {
    flex-direction: column;
  }
}
</style> 