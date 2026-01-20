<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ stats.user_count }}</div>
            <div class="stat-label">总用户数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ stats.active_user_count }}</div>
            <div class="stat-label">活跃用户</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ stats.role_count }}</div>
            <div class="stat-label">系统角色</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Role Specific Actions -->
    <el-row :gutter="20" style="margin-top: 20px" v-if="userRole">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>快捷操作 ({{ userRoleName }})</span>
          </template>
          
          <!-- Student Actions -->
          <div v-if="userRole === 'student'">
            <el-button type="primary" icon="Document" @click="handleAction('submitReport')">提交报告</el-button>
          </div>

          <!-- Teacher Actions -->
          <div v-if="userRole === 'teacher'">
            <el-button type="warning" icon="Refresh" @click="handleAction('resetStudent')">重置学生</el-button>
            <el-button type="primary" icon="Share" @click="handleAction('distributeCase')">案例分发</el-button>
          </div>

          <!-- Admin Actions -->
          <div v-if="userRole === 'admin'">
            <el-button 
              :type="maintenanceMode ? 'success' : 'danger'" 
              icon="SwitchButton" 
              @click="handleAction('maintenance')"
            >
              {{ maintenanceMode ? '结束维护' : '停机维护' }}
            </el-button>
            <el-button type="primary" icon="Files" @click="handleAction('backup')">备份</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>欢迎使用学生健康系统</span>
          </template>
          <p>这是一个基于Vue 3 + Flask的运动健康架构管理系统</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getStatistics } from '@/api/business'
import { createBackup, getMaintenanceStatus, toggleMaintenance } from '@/api/admin'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const authStore = useAuthStore()
const stats = ref({
  user_count: 0,
  active_user_count: 0,
  role_count: 0
})
const maintenanceMode = ref(false)

const userRole = computed(() => authStore.user?.role_code)
const userRoleName = computed(() => {
  const map = {
    'student': '学生',
    'teacher': '教师',
    'admin': '系统管理员'
  }
  return map[userRole.value] || userRole.value
})

const loadStats = async () => {
  try {
    const response = await getStatistics()
    stats.value = response.data.data
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  }
}

const loadMaintenanceStatus = async () => {
  if (userRole.value === 'admin') {
    try {
      const res = await getMaintenanceStatus()
      maintenanceMode.value = res.data.maintenance
    } catch (error) {
      console.error('Failed to load maintenance status', error)
    }
  }
}

const handleAction = async (action) => {
  if (action === 'backup') {
    try {
      await ElMessageBox.confirm('确定要备份当前系统数据吗？', '系统备份', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      })
      
      const res = await createBackup()
      ElMessage.success(`备份成功: ${res.data.filename}`)
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error(error.response?.data?.message || '备份失败')
      }
    }
  } else if (action === 'maintenance') {
    const actionText = maintenanceMode.value ? '关闭' : '开启'
    try {
      await ElMessageBox.confirm(
        `确定要${actionText}系统维护模式吗？\n${!maintenanceMode.value ? '开启后，除管理员外其他用户将无法登录。' : '关闭后，所有用户可正常使用系统。'}`, 
        '系统维护', 
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      const res = await toggleMaintenance(!maintenanceMode.value)
      maintenanceMode.value = res.data.maintenance
      ElMessage.success(res.message)
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error(error.response?.data?.message || '操作失败')
      }
    }
  } else {
    ElMessage.info(`点击了功能: ${action} (功能开发中)`)
  }
}

onMounted(() => {
  loadStats()
  loadMaintenanceStatus()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  text-align: center;
}

.stat-item {
  padding: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}
</style>

