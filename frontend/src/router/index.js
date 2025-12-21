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
  if (authStore.isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchUserInfo()
    } catch (error) {
      // 获取用户信息失败，清除认证状态
      authStore.clearAuth()
      next('/login')
      return
    }
  }
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/theory')
  } else {
    next()
  }
})

export default router
