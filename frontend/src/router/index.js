import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/theory',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/UserList.vue')
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/ProfileForm.vue')
      },
      {
        path: 'daily-log',
        name: 'DailyLog',
        component: () => import('@/views/daily-log/LogForm.vue')
      },
      {
        path: 'exercise-log',
        name: 'ExerciseLog',
        component: () => import('@/views/daily-log/LogForm.vue')
      },
      {
        path: 'intervention',
        name: 'Intervention',
        component: () => import('@/views/intervention/Intervention.vue')
      },
      {
        path: 'theory',
        name: 'BasicTheory',
        component: () => import('@/views/theory/BasicTheory.vue')
      },
      {
        path: 'prediction',
        name: 'Prediction',
        component: () => import('@/views/statistics/Statistics.vue')
      },
      {
        path: 'help',
        name: 'Help',
        component: () => import('@/views/help/Help.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/Settings.vue')
      },
      // Keep statistics for backward compatibility if needed, or redirect
      {
        path: 'statistics',
        redirect: 'prediction'
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果有token但没有用户信息，尝试获取用户信息
  // 但只在访问需要认证的路由时才尝试，避免在登录页也发送请求
  if (authStore.isAuthenticated && !authStore.user && to.meta.requiresAuth) {
    try {
      await authStore.fetchUserInfo()
      // 获取成功，继续导航
    } catch (error) {
      // 获取用户信息失败，清除认证状态
      // 注意：对于 /auth/me 的401错误，request.js 已经静默处理了，不会显示错误消息
      // request.js 也会清除 token 并跳转到登录页，所以这里只需要确保状态一致
      authStore.clearAuth()
      // 如果目标路由需要认证，跳转到登录页
      if (to.meta.requiresAuth) {
        next('/login')
        return
      }
      // 如果已经在登录页，允许继续
      if (to.path === '/login') {
        next()
        return
      }
      // 其他情况继续导航
      next()
      return
    }
  }
  
  // 检查路由权限
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/theory')
  } else {
    next()
  }
})

export default router
