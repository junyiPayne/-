import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '/api',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  async response => {
    // Handle blob response (e.g. PDF preview)
    if (response.config.responseType === 'blob') {
      // Check if the response is actually a JSON error (content-type check)
      const contentType = response.headers['content-type'] || ''
      if (contentType.includes('application/json')) {
        // It's a JSON error, not a blob - parse it
        try {
          const text = await response.data.text()
          const errorData = JSON.parse(text)
          ElMessage.error(errorData.message || '请求失败')
          return Promise.reject(new Error(errorData.message || '请求失败'))
        } catch (e) {
          ElMessage.error('服务器错误')
          return Promise.reject(new Error('服务器错误'))
        }
      }
      // It's a real blob (PDF), return as is
      return response
    }

    const res = response.data
    if (res.code === 200) {
      return response
    } else {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
  },
  async error => {
    const { response } = error
    if (response) {
      // Handle blob error response - when backend returns JSON error but frontend expects blob
      if (response.config?.responseType === 'blob' && response.data instanceof Blob) {
        const contentType = response.headers?.['content-type'] || ''
        if (contentType.includes('application/json')) {
          // Parse JSON error from blob
          try {
            const text = await response.data.text()
            const errorData = JSON.parse(text)
            ElMessage.error(errorData.message || '请求失败')
            return Promise.reject(new Error(errorData.message || '请求失败'))
          } catch (e) {
            ElMessage.error('服务器错误')
            return Promise.reject(new Error('服务器错误'))
          }
        }
      }
      
      // Handle normal JSON error response
      let errorMessage = '请求失败'
      if (response.data) {
        if (typeof response.data === 'object' && response.data.message) {
          errorMessage = response.data.message
        } else if (typeof response.data === 'string') {
          errorMessage = response.data
        }
      }
      
      const { code } = response.data || {}
      switch (code || response.status) {
        case 400:
          // 400错误直接显示后端返回的消息
          ElMessage.error(errorMessage || '请求参数错误')
          break
        case 401:
          ElMessage.error('未授权，请先登录')
          localStorage.removeItem('token')
          router.push('/login')
          break
        case 403:
          ElMessage.error('权限不足')
          break
        case 404:
          ElMessage.error('资源不存在')
          break
        case 500:
          ElMessage.error(errorMessage || '服务器错误')
          break
        default:
          ElMessage.error(errorMessage || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default request

