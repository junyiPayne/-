import axios from 'axios'
import { ElMessage } from 'element-plus'

/**
 * 智能检测 API 基础地址
 * - 如果通过 localhost 访问，使用 http://localhost:8000/api
 * - 如果通过公网域名访问，自动使用对应域名的 8000 端口
 */
function getApiBaseURL() {
  // 如果环境变量已配置，优先使用
  if (process.env.VUE_APP_API_BASE_URL) {
    return process.env.VUE_APP_API_BASE_URL
  }
  
  // 获取当前访问的协议和主机
  const protocol = window.location.protocol // http: 或 https:
  const hostname = window.location.hostname // localhost 或 域名
  const port = window.location.port // 端口号（如果有）
  
  // 判断是否为本地访问
  const isLocalhost = hostname === 'localhost' || 
                      hostname === '127.0.0.1' || 
                      hostname === '0.0.0.0' ||
                      hostname === ''
  
  if (isLocalhost) {
    // 本地访问，使用 localhost:8000
    return 'http://localhost:8000/api'
  } else {
    // 公网域名访问，使用相同域名但端口改为 8000
    // 如果当前是 80 端口（http）或 443 端口（https），需要显式指定 8000
    if (!port || port === '80' || port === '443') {
      return `${protocol}//${hostname}:8000/api`
    } else {
      // 如果已经有端口（可能是内网穿透的自定义端口），替换为 8000
      return `${protocol}//${hostname}:8000/api`
    }
  }
}

const request = axios.create({
  baseURL: getApiBaseURL(),
  timeout: 150000  // AI生成可能需要较长时间，增加到150秒
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    // 对于不需要认证的接口（如登录、注册、获取维护状态、健康检查），不添加 token
    const url = config.url || ''
    const isPublicEndpoint = url.includes('/auth/login') || 
                             url.includes('/auth/register') || 
                             url.includes('/admin/maintenance') ||
                             url.includes('/api/health')
    
    // 如果有token，添加到请求头（公开接口除外）
    if (token && !isPublicEndpoint) {
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
    // 添加调试日志（仅开发环境）
    if (process.env.NODE_ENV === 'development') {
      console.log('🔵 响应拦截器 - response.data:', res)
      console.log('🔵 响应拦截器 - res.code:', res?.code)
      console.log('🔵 响应拦截器 - response.status:', response.status)
      console.log('🔵 响应拦截器 - response.config.url:', response.config?.url)
    }
    
    if (res && res.code === 200) {
      return response
    } else {
      const errorMsg = res?.message || '请求失败'
      console.error('❌ 响应拦截器 - code不是200:', res?.code, 'message:', errorMsg)
      // 如果是上传背景图片，显示更详细的错误信息
      const url = response.config?.url || ''
      if (url.includes('/admin/background-image') && (response.config?.method || '').toLowerCase() === 'post') {
        console.error('❌ 背景图片上传失败详情:', {
          code: res?.code,
          message: errorMsg,
          status: response.status,
          data: res
        })
      }
      ElMessage.error(errorMsg)
      return Promise.reject(new Error(errorMsg))
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
          // 401错误显示后端返回的具体消息
          // 但对于某些接口的401错误，不显示错误消息（静默处理）
          const requestUrl = response.config?.url || ''
          const isMeRequest = requestUrl.includes('/auth/me')
          const isSettingsRequest = requestUrl.includes('/api/settings') && response.config?.method?.toLowerCase() === 'get'
          
          if (!isMeRequest && !isSettingsRequest) {
            // 非静默接口的401错误，显示错误消息
            if (errorMessage) {
              ElMessage.error(errorMessage)
            } else {
              ElMessage.error('未授权，请先注册')
            }
          }
          // 清除token
          localStorage.removeItem('token')
          // 如果当前不在登录页，跳转到登录页
          // 使用 window.location 避免循环依赖
          if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          break
        case 403:
          ElMessage.error('权限不足')
          break
        case 404:
          // 404 错误处理
          const url = response.config?.url || ''
          const method = (response.config?.method || '').toLowerCase()
          
          // 如果是获取背景图片或系统logo的GET请求，没有设置是正常的，不显示错误
          if ((url.includes('/admin/background-image') || url.includes('/admin/system-logo')) && method === 'get' && !url.includes('/admin/background-image/')) {
            return Promise.reject(error)
          }
          
          // 如果是上传背景图片失败（POST请求返回404），说明路由不存在
          if (url.includes('/admin/background-image') && method === 'post') {
            ElMessage.error('背景图片上传失败：路由不存在（404），请检查后端服务')
            return Promise.reject(error)
          }
          
          // 如果是访问背景图片文件失败（GET请求返回404），可能是文件不存在
          if (url.includes('/admin/background-image/') && method === 'get') {
            ElMessage.error('背景图片文件不存在，可能文件还未保存完成')
            return Promise.reject(error)
          }
          
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

