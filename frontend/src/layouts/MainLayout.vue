<template>
  <el-container class="layout-container">
    <el-header class="header">
      <div class="header-left">
        <div class="logo-container">
          <!-- 系统图标 -->
          <div class="system-logo-wrapper" @click="handleLogoClick" v-if="isAdmin">
            <img 
              v-if="systemLogoUrl" 
              :src="systemLogoUrl" 
              alt="系统图标" 
              class="system-logo"
              :style="{ width: logoSize + 'px', height: logoSize + 'px' }"
            />
            <el-icon v-else class="logo-placeholder" :style="{ fontSize: logoSize + 'px' }"><Picture /></el-icon>
            <input 
              ref="logoInputRef" 
              type="file" 
              accept="image/*" 
              style="display: none" 
              @change="handleLogoUpload"
            />
          </div>
          <div class="system-logo-wrapper" v-else>
            <img 
              v-if="systemLogoUrl" 
              :src="systemLogoUrl" 
              alt="系统图标" 
              class="system-logo"
              :style="{ width: logoSize + 'px', height: logoSize + 'px' }"
            />
          </div>
          <div class="logo">学生健康管理系统</div>
        </div>
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
          :text-color="settingsStore.fontColor"
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
            <span>AI体重助手</span>
          </el-menu-item>
          <el-menu-item index="/prediction">
            <el-icon><TrendCharts /></el-icon>
            <span>预测报告</span>
          </el-menu-item>
          <el-menu-item index="/help">
            <el-icon><QuestionFilled /></el-icon>
            <span>帮助</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>个性化设置</span>
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
import { useSettingsStore } from '@/stores/settings'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  House, User, Document, ArrowDown, UserFilled, 
  Food, Bicycle, MagicStick, TrendCharts, QuestionFilled, Setting, Picture 
} from '@element-plus/icons-vue'
import { submitReport, previewReport } from '@/api/report'
import { uploadSystemLogo, getSystemLogoUrl } from '@/api/admin'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const submitting = ref(false)
const previewing = ref(false)
const systemLogoUrl = ref(null)
const logoInputRef = ref(null)
const logoUploading = ref(false)

const isAdmin = computed(() => authStore.user?.role_code === 'admin')
const logoSize = computed(() => settingsStore.logoSize || 40)

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

// 加载系统图标
const loadSystemLogo = async () => {
  try {
    const res = await getSystemLogoUrl()
    if (res.data && res.data.code === 200 && res.data.data && res.data.data.url) {
      // 使用相对路径，axios会自动添加baseURL
      systemLogoUrl.value = res.data.data.url
    }
  } catch (error) {
    console.error('加载系统图标失败:', error)
  }
}

// 处理图标点击（仅管理员）
const handleLogoClick = () => {
  if (isAdmin.value && logoInputRef.value) {
    logoInputRef.value.click()
  }
}

// 处理图标上传
const handleLogoUpload = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  // 验证文件类型
  const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/svg+xml', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('不支持的文件类型，请上传图片文件（png, jpg, jpeg, gif, svg, webp）')
    return
  }

  // 验证文件大小（最大2MB）
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过2MB')
    return
  }

  logoUploading.value = true
  try {
    const res = await uploadSystemLogo(file)
    if (res.data && res.data.code === 200) {
      // 使用相对路径，axios会自动添加baseURL
      systemLogoUrl.value = res.data.data.url
      ElMessage.success('系统图标上传成功')
    } else {
      ElMessage.error(res.data?.message || '上传失败')
    }
  } catch (error) {
    console.error('上传系统图标失败:', error)
    ElMessage.error('上传失败，请稍后重试')
  } finally {
    logoUploading.value = false
    // 清空input，以便可以重复上传同一文件
    if (logoInputRef.value) {
      logoInputRef.value.value = ''
    }
  }
}

// 组件加载时，如果有token但没有用户信息，尝试获取
onMounted(async () => {
  // 只有在已认证且有token时才尝试获取用户信息
  if (authStore.isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchUserInfo()
    } catch (error) {
      // 401错误已经在request.js中处理（清除token并跳转登录页）
      // 这里只记录非401错误
      if (error?.response?.status !== 401) {
        console.error('加载用户信息失败:', error)
      }
    }
  }
  // 应用用户设置（只在已登录时）
  if (authStore.isAuthenticated) {
    settingsStore.applySettings()
    // 加载系统图标（只在已登录时）
    try {
      await loadSystemLogo()
    } catch (error) {
      // 静默处理错误，不影响页面显示
      if (error?.response?.status !== 401) {
        console.error('加载系统图标失败:', error)
      }
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
  background-color: var(--user-header-color, #304156) !important;
  background: var(--user-header-background, var(--user-header-color, #304156)) !important;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}

/* 确保导航栏所有部分都应用背景色 */
:deep(.el-header) {
  background-color: var(--user-header-color, #304156) !important;
  background: var(--user-header-background, var(--user-header-color, #304156)) !important;
}

:deep(.el-header .top-menu) {
  background-color: transparent !important;
}

.header-left {
  display: flex;
  align-items: center;
  height: 100%;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.system-logo-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.system-logo-wrapper:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.system-logo {
  width: var(--user-logo-size, 40px);
  height: var(--user-logo-size, 40px);
  object-fit: contain;
  border-radius: 4px;
  /* 提高清晰度 - 使用高质量渲染 */
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
  image-rendering: high-quality;
  /* 防止图片模糊 */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* 确保图片以原始质量显示 */
  image-rendering: auto;
}

.logo-placeholder {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.7);
}

.logo {
  font-size: 20px;
  font-weight: bold;
  margin-right: 40px;
  font-family: var(--user-font-family, inherit);
  color: var(--user-font-color, #fff);
}

.top-menu {
  border-bottom: none;
  height: 60px;
  line-height: 60px;
}

.sidebar {
  background-color: var(--user-sidebar-color, #fff) !important;
  border-right: 1px solid #e6e6e6;
}

.sidebar-menu {
  border-right: none;
  background-color: var(--user-sidebar-color, #fff) !important;
}

/* 确保侧边栏所有部分都应用背景色 */
:deep(.el-aside) {
  background-color: var(--user-sidebar-color, #fff) !important;
}

:deep(.el-aside .el-menu) {
  background-color: var(--user-sidebar-color, #fff) !important;
}

:deep(.el-aside .el-menu-item) {
  background-color: transparent !important;
}

:deep(.el-aside .el-sub-menu) {
  background-color: transparent !important;
}

:deep(.el-aside .el-sub-menu__title) {
  background-color: transparent !important;
}

/* 确保侧边栏容器也应用背景色 */
.el-aside.sidebar {
  background-color: var(--user-sidebar-color, #fff) !important;
}

.user-info {
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.main-content {
  background-color: var(--user-content-bg-color, #f0f2f5);
  padding: 20px;
  font-size: var(--user-font-size, 14px) !important;
  font-family: var(--user-font-family, Arial, sans-serif) !important;
  color: var(--user-font-color, #303133) !important;
}

/* 背景图片样式 - 应用到 body，但导航栏保持不透明 */
.layout-container {
  position: relative;
}

/* 确保导航栏不透明，覆盖背景图片 */
.header,
:deep(.el-header) {
  position: relative;
  z-index: 1000;
  background: var(--user-header-background, var(--user-header-color, #304156)) !important;
  background-color: var(--user-header-color, #304156) !important;
}

/* 确保侧边栏菜单项应用字体设置 */
:deep(.sidebar-menu .el-menu-item),
:deep(.sidebar-menu .el-sub-menu__title) {
  font-family: var(--user-font-family, inherit) !important;
  font-size: var(--user-font-size, 14px) !important;
  color: var(--user-font-color, #303133) !important;
}

:deep(.sidebar-menu .el-menu-item.is-active) {
  color: #409EFF !important;
}
</style>
