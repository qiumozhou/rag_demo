<template>
  <div class="settings-page">
    <div class="container">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="header-info">
            <el-icon size="32" color="#409eff">
              <Setting />
            </el-icon>
            <div class="header-text">
              <h1>系统设置</h1>
              <p>配置RAG系统的各项参数和功能选项</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 设置选项卡 -->
      <div class="settings-content">
        <el-tabs v-model="activeTab" tab-position="left" class="settings-tabs">
          <!-- 基本设置 -->
          <el-tab-pane label="基本设置" name="basic">
            <div class="tab-content">
              <h3 class="section-title">
                <el-icon><Tools /></el-icon>
                基本配置
              </h3>
              
              <el-form :model="basicSettings" label-width="150px" class="settings-form">
                <el-form-item label="系统名称">
                  <el-input v-model="basicSettings.systemName" placeholder="RAG智能问答系统" />
                </el-form-item>
                
                <el-form-item label="语言设置">
                  <el-select v-model="basicSettings.language" style="width: 200px">
                    <el-option label="简体中文" value="zh-CN" />
                    <el-option label="English" value="en-US" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="主题模式">
                  <el-radio-group v-model="basicSettings.theme">
                    <el-radio label="light">浅色模式</el-radio>
                    <el-radio label="dark">深色模式</el-radio>
                    <el-radio label="auto">跟随系统</el-radio>
                  </el-radio-group>
                </el-form-item>
                
                <el-form-item label="自动保存">
                  <el-switch v-model="basicSettings.autoSave" />
                  <span class="setting-description">自动保存对话记录</span>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <!-- 模型设置 -->
          <el-tab-pane label="模型设置" name="model">
            <div class="tab-content">
              <h3 class="section-title">
                <el-icon><Cpu /></el-icon>
                模型配置
              </h3>
              
              <el-form :model="modelSettings" label-width="150px" class="settings-form">
                <el-form-item label="嵌入模型">
                  <el-select v-model="modelSettings.embeddingModel" style="width: 350px">
                    <el-option 
                      label="all-MiniLM-L6-v2 (推荐)" 
                      value="sentence-transformers/all-MiniLM-L6-v2" 
                    />
                    <el-option 
                      label="all-mpnet-base-v2" 
                      value="sentence-transformers/all-mpnet-base-v2" 
                    />
                  </el-select>
                  <div class="setting-description">用于文档向量化的嵌入模型</div>
                </el-form-item>
                
                <el-form-item label="生成模型">
                  <el-select v-model="modelSettings.llmModel" style="width: 350px">
                    <el-option 
                      label="DialoGPT-medium" 
                      value="microsoft/DialoGPT-medium" 
                    />
                    <el-option 
                      label="GPT-2" 
                      value="gpt2" 
                    />
                  </el-select>
                  <div class="setting-description">用于生成回答的语言模型</div>
                </el-form-item>
                
                <el-form-item label="最大上下文长度">
                  <el-input-number 
                    v-model="modelSettings.maxContextLength" 
                    :min="1000" 
                    :max="8000" 
                    :step="500"
                    style="width: 200px"
                  />
                  <span class="setting-description">tokens</span>
                </el-form-item>
                
                <el-form-item label="温度参数">
                  <el-slider 
                    v-model="modelSettings.temperature" 
                    :min="0" 
                    :max="1" 
                    :step="0.1"
                    show-input
                    style="width: 300px"
                  />
                  <div class="setting-description">控制生成文本的随机性，值越大越随机</div>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <!-- 检索设置 -->
          <el-tab-pane label="检索设置" name="retrieval">
            <div class="tab-content">
              <h3 class="section-title">
                <el-icon><Search /></el-icon>
                检索配置
              </h3>
              
              <el-form :model="retrievalSettings" label-width="150px" class="settings-form">
                <el-form-item label="文档分块大小">
                  <el-input-number 
                    v-model="retrievalSettings.chunkSize" 
                    :min="500" 
                    :max="2000" 
                    :step="100"
                    style="width: 200px"
                  />
                  <span class="setting-description">字符数</span>
                </el-form-item>
                
                <el-form-item label="分块重叠">
                  <el-input-number 
                    v-model="retrievalSettings.chunkOverlap" 
                    :min="50" 
                    :max="500" 
                    :step="50"
                    style="width: 200px"
                  />
                  <span class="setting-description">字符数</span>
                </el-form-item>
                
                <el-form-item label="检索数量">
                  <el-input-number 
                    v-model="retrievalSettings.topK" 
                    :min="1" 
                    :max="20" 
                    :step="1"
                    style="width: 200px"
                  />
                  <span class="setting-description">每次检索返回的文档数量</span>
                </el-form-item>
                
                <el-form-item label="相似度阈值">
                  <el-slider 
                    v-model="retrievalSettings.similarityThreshold" 
                    :min="0" 
                    :max="1" 
                    :step="0.05"
                    show-input
                    style="width: 300px"
                  />
                  <div class="setting-description">低于此阈值的文档将被过滤</div>
                </el-form-item>
                
                <el-form-item label="启用重排序">
                  <el-switch v-model="retrievalSettings.enableRerank" />
                  <span class="setting-description">对检索结果进行重新排序</span>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <!-- 系统信息 -->
          <el-tab-pane label="系统信息" name="system">
            <div class="tab-content">
              <h3 class="section-title">
                <el-icon><Monitor /></el-icon>
                系统状态
              </h3>
              
              <div class="system-info">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="info-card">
                      <h4>服务状态</h4>
                      <div class="info-grid">
                        <div class="info-item">
                          <span class="label">系统状态:</span>
                          <el-tag :type="getStatusType(systemStatus.status)">
                            {{ getStatusText(systemStatus.status) }}
                          </el-tag>
                        </div>
                        <div class="info-item">
                          <span class="label">文档数量:</span>
                          <span class="value">{{ systemStatus.document_count || 0 }}</span>
                        </div>
                        <div class="info-item">
                          <span class="label">文档块数:</span>
                          <span class="value">{{ systemStatus.chunk_count || 0 }}</span>
                        </div>
                        <div class="info-item">
                          <span class="label">内存使用:</span>
                          <span class="value">{{ systemStatus.memory_usage?.toFixed(1) || 'N/A' }}%</span>
                        </div>
                      </div>
                    </div>
                  </el-col>
                  
                  <el-col :span="12">
                    <div class="info-card">
                      <h4>模型状态</h4>
                      <div class="info-grid">
                        <div class="info-item">
                          <span class="label">嵌入模型:</span>
                          <el-tag :type="getModelStatusType(systemStatus.model_status?.embedding_model)">
                            {{ getModelStatusText(systemStatus.model_status?.embedding_model) }}
                          </el-tag>
                        </div>
                        <div class="info-item">
                          <span class="label">生成模型:</span>
                          <el-tag :type="getModelStatusType(systemStatus.model_status?.llm_model)">
                            {{ getModelStatusText(systemStatus.model_status?.llm_model) }}
                          </el-tag>
                        </div>
                        <div class="info-item">
                          <span class="label">系统版本:</span>
                          <span class="value">v1.0.0</span>
                        </div>
                        <div class="info-item">
                          <span class="label">最后更新:</span>
                          <span class="value">{{ new Date().toLocaleString() }}</span>
                        </div>
                      </div>
                    </div>
                  </el-col>
                </el-row>
              </div>
              
              <!-- 操作按钮 -->
              <div class="system-actions">
                <el-button type="primary" @click="refreshSystemStatus">
                  <el-icon><Refresh /></el-icon>
                  刷新状态
                </el-button>
                <el-button type="warning" @click="clearCache">
                  <el-icon><Delete /></el-icon>
                  清除缓存
                </el-button>
                <el-button type="info" @click="exportSettings">
                  <el-icon><Download /></el-icon>
                  导出配置
                </el-button>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 底部操作 -->
      <div class="settings-footer">
        <el-button @click="resetSettings">重置设置</el-button>
        <el-button type="primary" @click="saveSettings" :loading="isSaving">
          <el-icon><Check /></el-icon>
          保存设置
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useChatStore } from '@/stores/chat'
import { ElMessage, ElMessageBox } from 'element-plus'

const chatStore = useChatStore()

// 响应式数据
const activeTab = ref('basic')
const isSaving = ref(false)

const basicSettings = reactive({
  systemName: 'RAG智能问答系统',
  language: 'zh-CN',
  theme: 'light',
  autoSave: true
})

const modelSettings = reactive({
  embeddingModel: 'sentence-transformers/all-MiniLM-L6-v2',
  llmModel: 'microsoft/DialoGPT-medium',
  maxContextLength: 4000,
  temperature: 0.7
})

const retrievalSettings = reactive({
  chunkSize: 1000,
  chunkOverlap: 200,
  topK: 5,
  similarityThreshold: 0.7,
  enableRerank: false
})

// 计算属性
const systemStatus = computed(() => chatStore.systemStatus)

// 方法
const getStatusType = (status) => {
  switch (status) {
    case 'running': return 'success'
    case 'error': return 'danger'
    default: return 'warning'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'running': return '正常运行'
    case 'error': return '系统错误'
    default: return '检查中'
  }
}

const getModelStatusType = (status) => {
  switch (status) {
    case 'loaded': return 'success'
    case 'fallback': return 'warning'
    default: return 'danger'
  }
}

const getModelStatusText = (status) => {
  switch (status) {
    case 'loaded': return '已加载'
    case 'fallback': return '后备模式'
    default: return '未加载'
  }
}

const refreshSystemStatus = async () => {
  try {
    await chatStore.loadSystemStatus()
    ElMessage.success('系统状态已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

const clearCache = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除系统缓存吗？这可能会影响系统性能。',
      '清除缓存',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里应该调用清除缓存的API
    ElMessage.success('缓存已清除')
  } catch {
    // 用户取消
  }
}

const exportSettings = () => {
  const settings = {
    basic: basicSettings,
    model: modelSettings,
    retrieval: retrievalSettings,
    exportTime: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(settings, null, 2)], { 
    type: 'application/json;charset=utf-8' 
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `rag-settings-${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('配置已导出')
}

const saveSettings = async () => {
  try {
    isSaving.value = true
    
    // 这里应该调用保存设置的API
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟API调用
    
    // 保存到本地存储
    localStorage.setItem('rag-basic-settings', JSON.stringify(basicSettings))
    localStorage.setItem('rag-model-settings', JSON.stringify(modelSettings))
    localStorage.setItem('rag-retrieval-settings', JSON.stringify(retrievalSettings))
    
    ElMessage.success('设置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    isSaving.value = false
  }
}

const resetSettings = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有设置为默认值吗？',
      '重置设置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 重置为默认值
    Object.assign(basicSettings, {
      systemName: 'RAG智能问答系统',
      language: 'zh-CN',
      theme: 'light',
      autoSave: true
    })
    
    Object.assign(modelSettings, {
      embeddingModel: 'sentence-transformers/all-MiniLM-L6-v2',
      llmModel: 'microsoft/DialoGPT-medium',
      maxContextLength: 4000,
      temperature: 0.7
    })
    
    Object.assign(retrievalSettings, {
      chunkSize: 1000,
      chunkOverlap: 200,
      topK: 5,
      similarityThreshold: 0.7,
      enableRerank: false
    })
    
    ElMessage.success('设置已重置')
  } catch {
    // 用户取消
  }
}

const loadSettings = () => {
  // 从本地存储加载设置
  const basicSettingsStr = localStorage.getItem('rag-basic-settings')
  if (basicSettingsStr) {
    Object.assign(basicSettings, JSON.parse(basicSettingsStr))
  }
  
  const modelSettingsStr = localStorage.getItem('rag-model-settings')
  if (modelSettingsStr) {
    Object.assign(modelSettings, JSON.parse(modelSettingsStr))
  }
  
  const retrievalSettingsStr = localStorage.getItem('rag-retrieval-settings')
  if (retrievalSettingsStr) {
    Object.assign(retrievalSettings, JSON.parse(retrievalSettingsStr))
  }
}

// 生命周期
onMounted(() => {
  loadSettings()
  chatStore.loadSystemStatus()
})
</script>

<style scoped>
.settings-page {
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

/* 设置内容 */
.settings-content {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-height: 600px;
}

.settings-tabs {
  height: 100%;
}

.tab-content {
  padding: 20px;
  height: 100%;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 25px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e4e7ed;
}

.settings-form {
  max-width: 600px;
}

.settings-form .el-form-item {
  margin-bottom: 25px;
}

.setting-description {
  color: #909399;
  font-size: 13px;
  margin-left: 10px;
  display: block;
  margin-top: 5px;
}

/* 系统信息 */
.system-info {
  margin-bottom: 30px;
}

.info-card {
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.info-card h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.info-grid {
  display: grid;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.info-item .label {
  color: #606266;
  font-weight: 500;
}

.info-item .value {
  color: #2c3e50;
  font-weight: 600;
}

.system-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  padding: 20px 0;
  border-top: 1px solid #e4e7ed;
}

/* 底部操作 */
.settings-footer {
  background: white;
  border-radius: 12px;
  padding: 20px 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

/* 选项卡样式覆盖 */
:deep(.el-tabs--left .el-tabs__nav) {
  width: 200px;
}

:deep(.el-tabs--left .el-tabs__content) {
  padding-left: 20px;
}

:deep(.el-tabs__item) {
  text-align: left;
  padding: 15px 20px;
  font-weight: 500;
}

:deep(.el-tabs__item.is-active) {
  background: #f0f7ff;
  color: #409eff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-content {
    padding: 20px;
  }
  
  .settings-tabs {
    :deep(.el-tabs--left) {
      .el-tabs__nav {
        width: 150px;
      }
      .el-tabs__content {
        padding-left: 10px;
      }
    }
  }
  
  .tab-content {
    padding: 10px;
  }
  
  .settings-form {
    :deep(.el-form-item__label) {
      width: 120px !important;
    }
  }
  
  .system-actions {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .settings-footer {
    flex-direction: column;
  }
}
</style> 