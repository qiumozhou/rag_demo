<template>
  <div class="home-page">
    <div class="container">
      <!-- 欢迎区域 -->
      <div class="welcome-section">
        <div class="welcome-content">
          <h1 class="welcome-title">
            欢迎使用 RAG 智能问答系统
          </h1>
          <p class="welcome-subtitle">
            基于检索增强生成技术，为您提供精准的知识问答服务
          </p>
          <div class="quick-actions">
            <el-button 
              type="primary" 
              size="large" 
              @click="$router.push('/chat')"
              class="action-btn"
            >
              <el-icon><ChatLineSquare /></el-icon>
              开始问答
            </el-button>
            <el-button 
              type="success" 
              size="large" 
              @click="$router.push('/documents')"
              class="action-btn"
            >
              <el-icon><UploadFilled /></el-icon>
              上传文档
            </el-button>
          </div>
        </div>
        <div class="welcome-illustration">
          <div class="floating-card">
            <el-icon size="48" color="#667eea">
              <ChatDotSquare />
            </el-icon>
          </div>
        </div>
      </div>

      <!-- 系统状态卡片 -->
      <div class="status-grid">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6">
            <div class="status-card card-shadow">
              <div class="card-header">
                <el-icon size="32" color="#67c23a">
                  <CircleCheckFilled />
                </el-icon>
                <span class="card-title">系统状态</span>
              </div>
              <div class="card-content">
                <div class="status-value" :class="systemStatusClass">
                  {{ systemStatusText }}
                </div>
                <div class="status-detail">
                  {{ systemStatusDetail }}
                </div>
              </div>
            </div>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <div class="status-card card-shadow">
              <div class="card-header">
                <el-icon size="32" color="#409eff">
                  <Document />
                </el-icon>
                <span class="card-title">文档数量</span>
              </div>
              <div class="card-content">
                <div class="status-value">
                  {{ chatStore.totalDocuments }}
                </div>
                <div class="status-detail">
                  {{ chatStore.systemStatus.chunk_count }} 个文档块
                </div>
              </div>
            </div>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <div class="status-card card-shadow">
              <div class="card-header">
                <el-icon size="32" color="#e6a23c">
                  <Cpu />
                </el-icon>
                <span class="card-title">模型状态</span>
              </div>
              <div class="card-content">
                <div class="status-value model-status">
                  {{ modelStatusText }}
                </div>
                <div class="status-detail">
                  内存使用: {{ memoryUsage }}
                </div>
              </div>
            </div>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <div class="status-card card-shadow">
              <div class="card-header">
                <el-icon size="32" color="#f56c6c">
                  <ChatDotRound />
                </el-icon>
                <span class="card-title">会话数量</span>
              </div>
              <div class="card-content">
                <div class="status-value">
                  {{ chatStore.messages.length }}
                </div>
                <div class="status-detail">
                  历史消息记录
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 功能特性 -->
      <div class="features-section">
        <h2 class="section-title">核心功能</h2>
        <el-row :gutter="30">
          <el-col :xs="24" :md="8">
            <div class="feature-card card-shadow">
              <div class="feature-icon">
                <el-icon size="48" color="#409eff">
                  <Search />
                </el-icon>
              </div>
              <h3 class="feature-title">智能检索</h3>
              <p class="feature-description">
                基于语义相似度的文档检索，快速找到最相关的信息片段
              </p>
            </div>
          </el-col>

          <el-col :xs="24" :md="8">
            <div class="feature-card card-shadow">
              <div class="feature-icon">
                <el-icon size="48" color="#67c23a">
                  <ChatDotSquare />
                </el-icon>
              </div>
              <h3 class="feature-title">生成回答</h3>
              <p class="feature-description">
                结合检索结果与语言模型，生成准确、连贯的回答内容
              </p>
            </div>
          </el-col>

          <el-col :xs="24" :md="8">
            <div class="feature-card card-shadow">
              <div class="feature-icon">
                <el-icon size="48" color="#e6a23c">
                  <Document />
                </el-icon>
              </div>
              <h3 class="feature-title">文档管理</h3>
              <p class="feature-description">
                支持多种文档格式，自动分块处理，构建知识库
              </p>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 使用统计 -->
      <div class="usage-section" v-if="showUsageStats">
        <h2 class="section-title">使用统计</h2>
        <div class="usage-grid">
          <el-row :gutter="20">
            <el-col :xs="24" :md="12">
              <div class="usage-card card-shadow">
                <h3>最近活动</h3>
                <div class="activity-list">
                  <div v-for="(activity, index) in recentActivities" :key="index" class="activity-item">
                    <el-icon :color="activity.color">
                      <component :is="activity.icon" />
                    </el-icon>
                    <div class="activity-content">
                      <div class="activity-text">{{ activity.text }}</div>
                      <div class="activity-time">{{ activity.time }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </el-col>

            <el-col :xs="24" :md="12">
              <div class="usage-card card-shadow">
                <h3>快速操作</h3>
                <div class="quick-operations">
                  <el-button 
                    v-for="operation in quickOperations" 
                    :key="operation.name"
                    :type="operation.type"
                    class="operation-btn"
                    @click="operation.action"
                  >
                    <el-icon>
                      <component :is="operation.icon" />
                    </el-icon>
                    {{ operation.name }}
                  </el-button>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { ElMessage } from 'element-plus'

const router = useRouter()
const chatStore = useChatStore()

// 响应式数据
const showUsageStats = ref(true)
const recentActivities = ref([
  {
    icon: 'Upload',
    color: '#409eff',
    text: '上传了新文档',
    time: '2分钟前'
  },
  {
    icon: 'ChatDotSquare',
    color: '#67c23a',
    text: '进行了智能问答',
    time: '5分钟前'
  },
  {
    icon: 'Refresh',
    color: '#e6a23c',
    text: '刷新了系统状态',
    time: '10分钟前'
  }
])

// 计算属性
const systemStatusClass = computed(() => {
  const status = chatStore.systemStatus.status
  return {
    'status-online': status === 'running',
    'status-offline': status === 'error',
    'status-loading': status === 'unknown'
  }
})

const systemStatusText = computed(() => {
  const status = chatStore.systemStatus.status
  switch (status) {
    case 'running': return '正常运行'
    case 'error': return '系统错误'
    default: return '检查中...'
  }
})

const systemStatusDetail = computed(() => {
  const status = chatStore.systemStatus.status
  switch (status) {
    case 'running': return '所有服务正常'
    case 'error': return '需要检查配置'
    default: return '正在连接...'
  }
})

const modelStatusText = computed(() => {
  const embeddingStatus = chatStore.systemStatus.model_status?.embedding_model
  const llmStatus = chatStore.systemStatus.model_status?.llm_model
  
  if (embeddingStatus === 'loaded' && llmStatus === 'loaded') {
    return '已加载'
  } else if (embeddingStatus === 'loaded' && llmStatus === 'fallback') {
    return '部分加载'
  } else {
    return '加载中'
  }
})

const memoryUsage = computed(() => {
  const usage = chatStore.systemStatus.memory_usage
  return usage > 0 ? `${usage.toFixed(1)}%` : 'N/A'
})

const quickOperations = computed(() => [
  {
    name: '开始问答',
    type: 'primary',
    icon: 'ChatLineSquare',
    action: () => router.push('/chat')
  },
  {
    name: '上传文档',
    type: 'success',
    icon: 'Upload',
    action: () => router.push('/documents')
  },
  {
    name: '系统设置',
    type: 'info',
    icon: 'Setting',
    action: () => router.push('/settings')
  },
  {
    name: '刷新状态',
    type: 'warning',
    icon: 'Refresh',
    action: refreshSystem
  }
])

// 方法
const refreshSystem = async () => {
  try {
    await chatStore.loadSystemStatus()
    ElMessage.success('系统状态已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

// 生命周期
onMounted(() => {
  // 页面加载时检查系统状态
  if (chatStore.systemStatus.status === 'unknown') {
    chatStore.loadSystemStatus()
  }
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 40px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 欢迎区域 */
.welcome-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 60px;
  align-items: center;
  margin-bottom: 80px;
  padding: 60px 40px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.welcome-title {
  font-size: 3rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 20px;
  line-height: 1.2;
}

.welcome-subtitle {
  font-size: 1.2rem;
  color: #606266;
  margin-bottom: 40px;
  line-height: 1.6;
}

.quick-actions {
  display: flex;
  gap: 20px;
}

.action-btn {
  height: 50px;
  padding: 0 30px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 25px;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.welcome-illustration {
  display: flex;
  justify-content: center;
  align-items: center;
}

.floating-card {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: float 3s ease-in-out infinite;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

/* 状态卡片 */
.status-grid {
  margin-bottom: 60px;
}

.status-card {
  background: white;
  border-radius: 15px;
  padding: 25px;
  height: 140px;
  transition: all 0.3s ease;
}

.status-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
}

.card-title {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

.card-content {
  margin-left: 44px;
}

.status-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 5px;
}

.status-value.status-online {
  color: #67c23a;
}

.status-value.status-offline {
  color: #f56c6c;
}

.status-value.status-loading {
  color: #e6a23c;
}

.status-value.model-status {
  color: #409eff;
}

.status-detail {
  font-size: 12px;
  color: #c0c4cc;
}

/* 功能特性 */
.features-section {
  margin-bottom: 60px;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 50px;
}

.feature-card {
  background: white;
  border-radius: 15px;
  padding: 40px 30px;
  text-align: center;
  height: 280px;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
}

.feature-icon {
  margin-bottom: 25px;
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 15px;
}

.feature-description {
  color: #606266;
  line-height: 1.8;
  font-size: 14px;
}

/* 使用统计 */
.usage-section {
  margin-bottom: 40px;
}

.usage-grid {
  margin-top: 30px;
}

.usage-card {
  background: white;
  border-radius: 15px;
  padding: 30px;
  height: 320px;
}

.usage-card h3 {
  color: #2c3e50;
  margin-bottom: 25px;
  font-size: 1.2rem;
  font-weight: 600;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.activity-item:hover {
  background: #e9ecef;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 5px;
}

.activity-time {
  font-size: 12px;
  color: #909399;
}

.quick-operations {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.operation-btn {
  height: 50px;
  border-radius: 10px;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-section {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
    padding: 40px 20px;
  }
  
  .welcome-title {
    font-size: 2rem;
  }
  
  .welcome-subtitle {
    font-size: 1rem;
  }
  
  .quick-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .quick-operations {
    grid-template-columns: 1fr;
  }
}
</style> 