<template>
  <el-container class="layout-container">
    <el-header class="header">
      <div class="header-left">
        <div class="logo">学生健康管理系统</div>
        <el-menu
          mode="horizontal"
          :default-active="activeTopMenu"
          class="top-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          @select="handleTopMenuSelect"
        >
          <el-menu-item index="1">基础理论</el-menu-item>
          <el-menu-item index="2">AI 体重虚拟实验</el-menu-item>
          <el-menu-item index="3">研究报告</el-menu-item>
        </el-menu>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          size="small" 
          @click="handlePreviewReport" 
          :loading="previewing"
          style="margin-right: 10px"
        >
          预览报告
        </el-button>
        <el-button 
          type="success" 
          size="small" 
          @click="handleSubmitReport" 
          :loading="submitting"
          style="margin-right: 20px"
        >
          提交报告
        </el-button>
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-tag size="small" effect="dark" type="info" style="margin-right: 8px">{{ userRoleName }}</el-tag>
            <span class="real-name">{{ authStore.user?.real_name || authStore.user?.username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">我的档案</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    
    <el-container>
      <el-aside width="200px" class="sidebar">
        <el-menu
          :default-active="activeMenu"
          router
          class="sidebar-menu"
          background-color="#fff"
          text-color="#303133"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/theory">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/profile">
            <el-icon><UserFilled /></el-icon>
            <span>我的档案</span>
          </el-menu-item>
          <el-menu-item index="/daily-log">
            <el-icon><Food /></el-icon>
            <span>饮食日志</span>
          </el-menu-item>
          <el-menu-item index="/exercise-log">
            <el-icon><Bicycle /></el-icon>
            <span>运动日志</span>
          </el-menu-item>
          <el-menu-item index="/intervention">
            <el-icon><MagicStick /></el-icon>
            <span>干预工坊</span>
          </el-menu-item>
          <el-menu-item index="/prediction">
            <el-icon><TrendCharts /></el-icon>
            <span>预测报告</span>
          </el-menu-item>
          <el-menu-item index="/help">
            <el-icon><QuestionFilled /></el-icon>
            <span>帮助</span>
          </el-menu-item>
          
          <!-- 管理员和教师可见 -->
          <el-sub-menu index="admin" v-if="authStore.user?.role_code === 'admin' || authStore.user?.role_code === 'teacher'">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/users">用户管理</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  House, User, Document, ArrowDown, UserFilled, 
  Food, Bicycle, MagicStick, TrendCharts, QuestionFilled, Setting 
} from '@element-plus/icons-vue'
import { submitReport, previewReport } from '@/api/report'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const submitting = ref(false)
const previewing = ref(false)

const activeMenu = computed(() => route.path)
const activeTopMenu = computed(() => {
  if (route.path.includes('/theory')) return '1'
  if (route.path.includes('/intervention')) return '2'
  if (route.path.includes('/prediction') || route.path.includes('/statistics')) return '3'
  return '2'
})

const userRoleName = computed(() => {
  const role = authStore.user?.role_code
  const map = {
    'student': '学生',
    'teacher': '教师',
    'admin': '管理员'
  }
  return map[role] || role || '用户'
})

// 组件加载时，如果有token但没有用户信息，尝试获取
onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchUserInfo()
    } catch (error) {
      console.error('加载用户信息失败:', error)
    }
  }
})

const handleTopMenuSelect = (index) => {
  switch (index) {
    case '1':
      router.push('/theory')
      break
    case '2':
      router.push('/intervention')
      break
    case '3':
      router.push('/prediction') // or /statistics
      break
  }
}

const handlePreviewReport = async () => {
  previewing.value = true
  try {
    const res = await previewReport()
    // Create a blob URL and open it
    const blob = new Blob([res.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    window.open(url)
  } catch (error) {
    console.error(error)
    ElMessage.error('预览失败，请稍后重试')
  } finally {
    previewing.value = false
  }
}

const handleSubmitReport = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要提交当前的健康与运动监测报告吗？提交后将生成PDF并发送给教师。',
      '提交报告',
      {
        confirmButtonText: '确定提交',
        cancelButtonText: '取消',
        type: 'info',
      }
    )
    
    submitting.value = true
    const res = await submitReport()
    if (res.data.code === 200) {
      ElMessage.success('报告提交成功！')
    } else {
      ElMessage.error(res.data.message || '提交失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error('操作失败，请稍后重试')
    }
  } finally {
    submitting.value = false
  }
}

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.header {
  background-color: #304156;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  height: 100%;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  margin-right: 40px;
}

.top-menu {
  border-bottom: none;
  height: 60px;
  line-height: 60px;
}

.sidebar {
  background-color: #fff;
  border-right: 1px solid #e6e6e6;
}

.sidebar-menu {
  border-right: none;
}

.user-info {
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
