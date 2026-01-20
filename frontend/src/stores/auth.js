import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register as registerApi, getCurrentUser } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function setUser(userData) {
    user.value = userData
  }

  function clearAuth() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  async function loginAction(credentials) {
    try {
      const response = await login(credentials)
      // 后端返回格式: {code: 200, message: "...", data: {access_token: "...", user: {...}}}
      const responseData = response.data.data
      setToken(responseData.access_token)
      setUser(responseData.user)
      ElMessage.success('登录成功')
      return response
    } catch (error) {
      // 401错误（账号不存在、密码错误）的消息已经在request.js拦截器中显示
      // 这里不再重复显示，直接抛出错误
      // 如果是网络错误等特殊情况，request.js拦截器也会处理
      throw error
    }
  }

  async function registerAction(userData) {
    try {
      const response = await registerApi(userData)
      ElMessage.success('注册成功')
      return response
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '注册失败')
      throw error
    }
  }

  async function fetchUserInfo() {
    try {
      const response = await getCurrentUser()
      // 后端返回格式: {code: 200, message: "...", data: {...}}
      setUser(response.data.data)
      return response
    } catch (error) {
      // 如果获取用户信息失败（如token无效），清除认证状态
      // 错误消息已经在 request.js 拦截器中处理（对于非 /auth/me 的401会显示）
      clearAuth()
      throw error
    }
  }

  function logout() {
    clearAuth()
    ElMessage.success('已退出登录')
  }

  return {
    token,
    user,
    isAuthenticated,
    login: loginAction,
    register: registerAction,
    logout,
    fetchUserInfo,
    setToken,
    setUser,
    clearAuth
  }
})

