<template>
  <div class="chat-page">
    <div class="container">
      <!-- 聊天区域 -->
      <div class="chat-container">
        <div class="chat-header">
          <div class="header-info">
            <el-icon size="24" color="#409eff">
              <ChatLineSquare />
            </el-icon>
            <h2>智能问答</h2>
            <el-tag :type="statusTagType" size="small">
              {{ systemStatusText }}
            </el-tag>
          </div>
          
          <div class="header-actions">
            <el-tooltip content="清空对话" placement="bottom">
              <el-button 
                size="small" 
                type="danger" 
                @click="clearChat"
                :disabled="messages.length === 0"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
            
            <el-tooltip content="导出对话" placement="bottom">
              <el-button 
                size="small" 
                type="info" 
                @click="exportChat"
                :disabled="messages.length === 0"
              >
                <el-icon><Download /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>

        <!-- 消息列表 -->
        <div class="chat-messages" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-chat">
            <el-icon size="64" color="#c0c4cc">
              <ChatDotSquare />
            </el-icon>
            <h3>开始对话</h3>
            <p>向我提问任何关于已上传文档的问题</p>
            <div class="quick-questions">
              <el-button 
                v-for="question in quickQuestions" 
                :key="question"
                size="small"
                type="primary"
                plain
                @click="sendQuickQuestion(question)"
                class="quick-btn"
              >
                {{ question }}
              </el-button>
            </div>
          </div>

          <div v-else class="message-list">
            <div 
              v-for="message in messages" 
              :key="message.id"
              :class="['message-item', `message-${message.type}`]"
            >
              <!-- 用户消息 -->
              <div v-if="message.type === 'user'" class="user-message">
                <div class="message-content">
                  <div class="message-text">{{ message.content }}</div>
                  <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                </div>
                <div class="message-avatar">
                  <el-avatar size="small">
                    <el-icon><User /></el-icon>
                  </el-avatar>
                </div>
              </div>

              <!-- AI回复 -->
              <div v-else-if="message.type === 'assistant'" class="assistant-message">
                <div class="message-avatar">
                  <el-avatar size="small" style="background: #409eff">
                    <el-icon><Cpu /></el-icon>
                  </el-avatar>
                </div>
                <div class="message-content">
                  <div class="message-text" v-html="formatAnswer(message.content)"></div>
                  
                  <!-- 置信度和响应时间 -->
                  <div class="message-meta">
                    <div class="meta-item">
                      <el-icon><Timer /></el-icon>
                      <span>{{ message.response_time?.toFixed(2) }}s</span>
                    </div>
                    <div class="meta-item">
                      <el-icon><TrendCharts /></el-icon>
                      <span>置信度: {{ (message.confidence * 100).toFixed(1) }}%</span>
                    </div>
                  </div>

                  <!-- 引用来源 -->
                  <div v-if="message.sources && message.sources.length > 0" class="message-sources">
                    <el-collapse size="small">
                      <el-collapse-item title="查看引用来源" name="sources">
                        <div class="sources-list">
                          <div 
                            v-for="(source, index) in message.sources" 
                            :key="index"
                            class="source-item"
                          >
                            <div class="source-header">
                              <el-icon><Document /></el-icon>
                              <span class="source-name">{{ source.source }}</span>
                              <el-tag size="small" type="success">
                                {{ (source.score * 100).toFixed(1) }}%
                              </el-tag>
                            </div>
                            <div class="source-content">{{ source.content }}</div>
                          </div>
                        </div>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                  
                  <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                </div>
              </div>

              <!-- 错误消息 -->
              <div v-else-if="message.type === 'error'" class="error-message">
                <div class="message-avatar">
                  <el-avatar size="small" style="background: #f56c6c">
                    <el-icon><Warning /></el-icon>
                  </el-avatar>
                </div>
                <div class="message-content">
                  <div class="message-text">{{ message.content }}</div>
                  <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                </div>
              </div>
            </div>

            <!-- 加载中指示器 -->
            <div v-if="isLoading" class="loading-message">
              <div class="message-avatar">
                <el-avatar size="small" style="background: #409eff">
                  <el-icon><Loading /></el-icon>
                </el-avatar>
              </div>
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <div class="message-text">正在思考中...</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input">
          <div class="input-container">
            <el-input
              v-model="currentQuestion"
              type="textarea"
              :rows="3"
              placeholder="请输入您的问题..."
              @keydown.ctrl.enter="sendMessage"
              :disabled="!isSystemOnline || isLoading"
              class="question-input"
            />
            
            <div class="input-actions">
              <div class="input-options">
                <el-tooltip content="检索文档数量" placement="top">
                  <div class="option-item">
                    <el-icon><DataBoard /></el-icon>
                    <el-input-number 
                      v-model="queryOptions.top_k" 
                      :min="1" 
                      :max="10" 
                      size="small"
                      style="width: 80px"
                    />
                  </div>
                </el-tooltip>
                
                <el-tooltip content="启用重排序" placement="top">
                  <div class="option-item">
                    <el-switch 
                      v-model="queryOptions.use_rerank"
                      size="small"
                    />
                    <span>重排序</span>
                  </div>
                </el-tooltip>
              </div>
              
              <el-button 
                type="primary" 
                @click="sendMessage"
                :loading="isLoading"
                :disabled="!currentQuestion.trim() || !isSystemOnline"
                size="large"
              >
                <el-icon><Position /></el-icon>
                发送 (Ctrl+Enter)
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'

const chatStore = useChatStore()

// 响应式数据
const currentQuestion = ref('')
const messagesContainer = ref(null)
const queryOptions = ref({
  top_k: 5,
  use_rerank: false
})

const quickQuestions = ref([
  '这个文档的主要内容是什么？',
  '有哪些重要的概念？',
  '能否总结一下要点？'
])

// 计算属性
const messages = computed(() => chatStore.messages)
const isLoading = computed(() => chatStore.isLoading)
const isSystemOnline = computed(() => chatStore.isSystemOnline)

const systemStatusText = computed(() => {
  return isSystemOnline.value ? '系统正常' : '系统离线'
})

const statusTagType = computed(() => {
  return isSystemOnline.value ? 'success' : 'danger'
})

// 方法
const sendMessage = async () => {
  if (!currentQuestion.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }

  if (!isSystemOnline.value) {
    ElMessage.error('系统离线，无法发送消息')
    return
  }

  const question = currentQuestion.value.trim()
  currentQuestion.value = ''

  try {
    await chatStore.sendMessage(question, queryOptions.value)
    scrollToBottom()
  } catch (error) {
    console.error('发送消息失败:', error)
  }
}

const sendQuickQuestion = (question) => {
  currentQuestion.value = question
  sendMessage()
}

const clearChat = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有对话记录吗？',
      '清空对话',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    chatStore.clearMessages()
    ElMessage.success('对话已清空')
  } catch {
    // 用户取消
  }
}

const exportChat = () => {
  const chatData = {
    messages: messages.value,
    exportTime: new Date().toISOString(),
    totalMessages: messages.value.length
  }
  
  const blob = new Blob([JSON.stringify(chatData, null, 2)], {
    type: 'application/json;charset=utf-8'
  })
  
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `chat-export-${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('对话记录已导出')
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN')
}

const formatAnswer = (content) => {
  // 使用marked处理markdown格式
  return marked(content)
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 监听消息变化，自动滚动到底部
watch(messages, () => {
  scrollToBottom()
}, { deep: true })

// 生命周期
onMounted(() => {
  // 初始化系统状态
  if (!isSystemOnline.value) {
    chatStore.loadSystemStatus()
  }
})
</script>

<style scoped>
.chat-page {
  min-height: calc(100vh - 70px);
  background: #f5f7fa;
  padding: 20px 0;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
  height: calc(100vh - 110px);
}

/* 聊天容器 */
.chat-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #e4e7ed;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-info h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* 消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-chat {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-chat h3 {
  margin: 20px 0 10px;
  color: #606266;
  font-size: 20px;
}

.empty-chat p {
  margin-bottom: 30px;
  font-size: 14px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.quick-btn {
  border-radius: 20px;
}

/* 消息列表 */
.message-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.user-message {
  flex-direction: row-reverse;
}

.user-message .message-content {
  background: linear-gradient(135deg, #409eff, #67c23a);
  color: white;
  margin-left: auto;
  max-width: 70%;
}

.assistant-message .message-content,
.error-message .message-content {
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  max-width: 80%;
}

.error-message .message-content {
  background: #fef0f0;
  border-color: #fbc4c4;
}

.message-content {
  border-radius: 12px;
  padding: 15px;
  position: relative;
}

.message-text {
  line-height: 1.6;
  margin-bottom: 8px;
}

.message-text:last-child {
  margin-bottom: 0;
}

.message-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  text-align: right;
}

.assistant-message .message-time,
.error-message .message-time {
  color: #909399;
  text-align: left;
}

.message-meta {
  display: flex;
  gap: 15px;
  margin: 10px 0;
  font-size: 12px;
  color: #606266;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 引用来源 */
.message-sources {
  margin: 15px 0;
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.source-item {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
}

.source-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 500;
}

.source-name {
  flex: 1;
  color: #409eff;
}

.source-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  max-height: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 加载中 */
.loading-message .message-content {
  background: #f0f7ff;
  border-color: #b3d8ff;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 输入区域 */
.chat-input {
  border-top: 1px solid #e4e7ed;
  padding: 20px 25px;
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.question-input {
  resize: none;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-options {
  display: flex;
  align-items: center;
  gap: 20px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 0 10px;
  }
  
  .chat-header {
    padding: 15px 20px;
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .user-message .message-content,
  .assistant-message .message-content {
    max-width: 85%;
  }
  
  .input-actions {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .input-options {
    justify-content: space-around;
  }
}
</style> 