<template>
  <div id="app">
    <!-- 导航栏 -->
    <el-container>
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo-section">
            <el-icon size="32" color="#fff">
              <ChatLineSquare />
            </el-icon>
            <h1 class="app-title">RAG 智能问答系统</h1>
          </div>
          
          <div class="nav-section">
            <el-menu
              :default-active="activeRoute"
              mode="horizontal"
              background-color="transparent"
              text-color="#fff"
              active-text-color="#a8edea"
              class="nav-menu"
              @select="handleMenuSelect"
            >
              <el-menu-item v-for="route in routes" :key="route.name" :index="route.name">
                <el-icon><component :is="route.meta.icon" /></el-icon>
                <span>{{ route.meta.title }}</span>
              </el-menu-item>
            </el-menu>
          </div>
          
          <div class="status-section">
            <el-tooltip content="系统状态" placement="bottom">
              <div class="status-indicator" :class="systemStatusClass">
                <el-icon><component :is="systemStatusIcon" /></el-icon>
              </div>
            </el-tooltip>
            
            <el-dropdown @command="handleCommand">
              <el-icon size="24" color="#fff" class="settings-icon">
                <MoreFilled />
              </el-icon>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="refresh">
                    <el-icon><Refresh /></el-icon>
                    刷新系统
                  </el-dropdown-item>
                  <el-dropdown-item command="about">
                    <el-icon><InfoFilled /></el-icon>
                    关于系统
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
    
    <!-- 关于对话框 -->
    <el-dialog v-model="aboutDialogVisible" title="关于系统" width="500px">
      <div class="about-content">
        <div class="about-logo">
          <el-icon size="64" color="#667eea">
            <ChatLineSquare />
          </el-icon>
        </div>
        <h3>RAG 智能问答系统</h3>
        <p class="version">版本：{{ systemInfo.version || '1.0.0' }}</p>
        <p class="description">
          基于检索增强生成(RAG)技术的智能问答系统，结合文档检索和大语言模型，
          为用户提供准确、相关的知识问答服务。
        </p>
        <div class="tech-stack">
          <h4>技术栈</h4>
          <el-tag type="primary" class="tech-tag">Vue 3</el-tag>
          <el-tag type="success" class="tech-tag">FastAPI</el-tag>
          <el-tag type="info" class="tech-tag">Python</el-tag>
          <el-tag type="warning" class="tech-tag">Chroma DB</el-tag>
          <el-tag type="danger" class="tech-tag">LangChain</el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()

// 响应式数据
const aboutDialogVisible = ref(false)
const systemInfo = ref({})

// 路由信息
const routes = router.options.routes.filter(r => r.meta?.title)

// 计算属性
const activeRoute = computed(() => route.name)

const systemStatusClass = computed(() => {
  const status = chatStore.systemStatus.status
  return {
    'online': status === 'running',
    'offline': status === 'error',
    'loading': status === 'unknown'
  }
})

const systemStatusIcon = computed(() => {
  const status = chatStore.systemStatus.status
  switch (status) {
    case 'running': return 'CircleCheckFilled'
    case 'error': return 'CircleCloseFilled'
    default: return 'Loading'
  }
})

// 方法
const handleMenuSelect = (index) => {
  router.push({ name: index })
}

const handleCommand = async (command) => {
  switch (command) {
    case 'refresh':
      await refreshSystem()
      break
    case 'about':
      aboutDialogVisible.value = true
      break
  }
}

const refreshSystem = async () => {
  try {
    await chatStore.initialize()
    ElMessage.success('系统刷新成功')
  } catch (error) {
    ElMessage.error('系统刷新失败')
  }
}

const loadSystemInfo = async () => {
  try {
    const health = await chatStore.checkHealth()
    systemInfo.value = health
  } catch (error) {
    console.error('加载系统信息失败:', error)
  }
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    chatStore.initialize(),
    loadSystemInfo()
  ])
})
</script>

<style scoped>
.app-header {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  padding: 0;
  height: 70px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0 20px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-title {
  color: white;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.nav-section {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-menu {
  border: none !important;
}

.nav-menu .el-menu-item {
  border: none !important;
  color: rgba(255, 255, 255, 0.8) !important;
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-menu .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
}

.nav-menu .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.15) !important;
  color: #a8edea !important;
  border-radius: 8px;
}

.status-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.status-indicator.online {
  background-color: rgba(103, 194, 58, 0.2);
  color: #67c23a;
}

.status-indicator.offline {
  background-color: rgba(245, 108, 108, 0.2);
  color: #f56c6c;
}

.status-indicator.loading {
  background-color: rgba(230, 162, 60, 0.2);
  color: #e6a23c;
}

.settings-icon {
  cursor: pointer;
  transition: transform 0.3s ease;
}

.settings-icon:hover {
  transform: rotate(90deg);
}

.app-main {
  padding: 0;
  background: #f5f7fa;
  min-height: calc(100vh - 70px);
}

/* 关于对话框样式 */
.about-content {
  text-align: center;
  padding: 20px;
}

.about-logo {
  margin-bottom: 20px;
}

.about-content h3 {
  margin: 10px 0;
  color: #2c3e50;
  font-size: 24px;
}

.version {
  color: #909399;
  margin-bottom: 20px;
}

.description {
  line-height: 1.8;
  color: #606266;
  margin-bottom: 30px;
}

.tech-stack h4 {
  margin-bottom: 15px;
  color: #409eff;
}

.tech-tag {
  margin: 4px;
}

/* 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 15px;
  }
  
  .app-title {
    font-size: 18px;
  }
  
  .nav-menu .el-menu-item span {
    display: none;
  }
  
  .status-section {
    gap: 10px;
  }
}
</style> 