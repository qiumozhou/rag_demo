import axios from 'axios'
import { ElMessage, ElNotification } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 在发送请求之前可以做一些处理
    console.log(`发送请求: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('请求配置错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 成功响应处理
    const { status, data, config } = response
    
    console.log(`请求成功: ${config.method?.toUpperCase()} ${config.url} (${status})`)
    
    // 如果响应中有处理时间，显示在控制台
    if (response.headers['x-process-time']) {
      console.log(`处理时间: ${response.headers['x-process-time']}秒`)
    }
    
    return response
  },
  (error) => {
    // 错误响应处理
    const { response, config, message } = error
    
    console.error(`请求失败: ${config?.method?.toUpperCase()} ${config?.url}`, error)
    
    if (response) {
      // 服务器返回错误状态码
      const { status, data } = response
      
      let errorMessage = '请求失败'
      
      switch (status) {
        case 400:
          errorMessage = data?.detail || data?.message || '请求参数错误'
          break
        case 401:
          errorMessage = '未授权，请重新登录'
          break
        case 403:
          errorMessage = '权限不足'
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 413:
          errorMessage = '文件大小超出限制'
          break
        case 422:
          errorMessage = '数据验证失败'
          break
        case 500:
          errorMessage = data?.detail || data?.message || '服务器内部错误'
          break
        case 502:
          errorMessage = '服务网关错误'
          break
        case 503:
          errorMessage = '服务暂时不可用'
          break
        default:
          errorMessage = data?.detail || data?.message || `请求失败 (${status})`
      }
      
      // 显示错误消息
      if (status >= 500) {
        ElNotification({
          title: '系统错误',
          message: errorMessage,
          type: 'error',
          duration: 5000
        })
      } else {
        ElMessage.error(errorMessage)
      }
      
    } else if (error.code === 'ECONNABORTED') {
      // 请求超时
      ElMessage.error('请求超时，请稍后重试')
    } else if (error.code === 'ERR_NETWORK') {
      // 网络错误
      ElNotification({
        title: '网络错误',
        message: '无法连接到服务器，请检查网络连接',
        type: 'error',
        duration: 0 // 不自动关闭
      })
    } else {
      // 其他错误
      ElMessage.error(message || '网络请求失败')
    }
    
    return Promise.reject(error)
  }
)

// 通用请求方法
export const request = {
  get: (url, config) => api.get(url, config),
  post: (url, data, config) => api.post(url, data, config),
  put: (url, data, config) => api.put(url, data, config),
  delete: (url, config) => api.delete(url, config),
  patch: (url, data, config) => api.patch(url, data, config)
}

// 文件上传的专用方法
export const uploadFile = (url, file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  
  return api.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
        onProgress(percent)
      }
    }
  })
}

// 检查API连接状态
export const checkApiConnection = async () => {
  try {
    const response = await api.get('/health', { timeout: 5000 })
    return {
      connected: true,
      status: response.status,
      data: response.data
    }
  } catch (error) {
    return {
      connected: false,
      error: error.message
    }
  }
}

export default api 