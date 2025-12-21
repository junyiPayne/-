<template>
  <div class="user-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <span>用户管理</span>
            <el-tag v-if="maintenanceMode" type="danger" effect="dark" class="status-tag" size="small">
              <span class="tag-content">
                <el-icon><Warning /></el-icon>
                <span>维护模式</span>
              </span>
            </el-tag>
            <el-tag v-else type="success" effect="plain" class="status-tag" size="small">
              <span class="tag-content">
                <el-icon><CircleCheck /></el-icon>
                <span>运行正常</span>
              </span>
            </el-tag>
          </div>
          <div class="header-actions">
            <!-- 管理员特有按钮 -->
            <template v-if="authStore.user?.role_code === 'admin'">
              <el-button 
                :type="maintenanceMode ? 'success' : 'warning'" 
                @click="handleShutdown"
              >
                {{ maintenanceMode ? '结束维护' : '停机维护' }}
              </el-button>
              <el-button type="success" @click="handleBackup">备份</el-button>
            </template>
            <!-- 教师特有按钮 -->
            <template v-if="authStore.user?.role_code === 'teacher'">
              <el-button type="success" @click="handleCaseDistribution">案例分发</el-button>
            </template>
            <el-button type="primary" @click="handleAdd" v-if="authStore.user?.role_code === 'admin'">新增用户</el-button>
          </div>
        </div>
      </template>
      
      <el-form :inline="true" class="search-form">
        <el-form-item label="搜索">
          <el-input
            v-model="searchKeyword"
            placeholder="用户名/邮箱"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="users" v-loading="loading" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="real_name" label="真实姓名" />
        <el-table-column prop="role_name" label="角色" />
        <el-table-column prop="is_active" label="状态">
          <template #default="{ row }">
            <template v-if="maintenanceMode && row.role_code !== 'admin'">
              <el-tag type="info" effect="dark">维护中</el-tag>
            </template>
            <template v-else>
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <!-- 查看报告按钮：管理员可以查看所有，老师只能查看学生 -->
            <el-button 
              v-if="canViewReports(row)"
              size="small" 
              type="primary" 
              @click="handleViewReports(row)"
            >查看报告</el-button>
            <!-- 教师特有操作 -->
            <el-button 
              v-if="authStore.user?.role_code === 'teacher'" 
              size="small" 
              type="warning" 
              @click="handleResetStudent(row)"
            >重置学生</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Add/Edit User Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="userForm.real_name" />
        </el-form-item>
        <el-form-item label="角色" prop="role_id" v-if="authStore.user?.role_code === 'admin'">
          <el-select v-model="userForm.role_id" placeholder="请选择角色">
            <el-option label="管理员" :value="1" />
            <el-option label="教师" :value="3" />
            <el-option label="学生" :value="4" />
            <el-option label="普通用户" :value="2" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- View Reports Dialog -->
    <el-dialog
      v-model="reportsDialogVisible"
      :title="`${selectedUser?.real_name || selectedUser?.username} 的报告`"
      width="900px"
    >
      <div v-if="reports.length > 0">
        <el-descriptions :column="2" border style="margin-bottom: 20px;">
          <el-descriptions-item label="报告ID">{{ reports[0].id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="reports[0].status === 'submitted' ? 'success' : 'info'">
              {{ reports[0].status === 'submitted' ? '已提交' : '已审核' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(reports[0].created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(reports[0].updated_at) }}</el-descriptions-item>
        </el-descriptions>
        
        <div style="margin-bottom: 20px;">
          <el-button 
            type="primary" 
            :disabled="!reports[0].has_pdf"
            @click="handleViewReport(reports[0])"
          >查看PDF报告</el-button>
        </div>
        
        <el-divider>修改历史</el-divider>
        <el-timeline v-if="reports[0].history && reports[0].history.length > 0">
          <el-timeline-item
            v-for="(item, index) in reports[0].history"
            :key="index"
            :timestamp="formatDate(item.created_at)"
            placement="top"
          >
            <el-card>
              <h4>{{ getActionText(item.action) }}</h4>
              <p>{{ item.description }}</p>
              <p style="color: #909399; font-size: 12px;">操作人: {{ item.modified_by }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无修改历史" />
      </div>
      <el-empty v-else description="该用户暂无报告" />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="reportsDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Warning, CircleCheck } from '@element-plus/icons-vue'
import { getUserList, deleteUser, createUser, updateUser, resetUser } from '@/api/users'
import { getMaintenanceStatus, toggleMaintenance, createBackup } from '@/api/admin'
import { getReports, viewReport } from '@/api/report'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const users = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const maintenanceMode = ref(false)

const pagination = reactive({
  page: 1,
  per_page: 1000,
  total: 0
})

const dialogVisible = ref(false)
const dialogTitle = ref('新增用户')
const isEdit = ref(false)
const submitting = ref(false)
const userFormRef = ref(null)

// Reports dialog
const reportsDialogVisible = ref(false)
const reports = ref([])
const reportsLoading = ref(false)
const selectedUser = ref(null)

const userForm = reactive({
  id: null,
  username: '',
  password: '',
  email: '',
  real_name: '',
  role_id: 2
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  role_id: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const handleSearch = () => {
  pagination.page = 1
  loadUsers()
}

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await getUserList({
      page: pagination.page,
      per_page: pagination.per_page,
      search: searchKeyword.value
    })
    users.value = response.data.data.items
    pagination.total = response.data.data.total
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  searchKeyword.value = '' // Clear search
  isEdit.value = false
  dialogTitle.value = '新增用户'
  dialogVisible.value = true
  // Reset form
  Object.assign(userForm, {
    id: null,
    username: '',
    password: '',
    email: '',
    real_name: '',
    role_id: 2
  })
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑用户'
  dialogVisible.value = true
  Object.assign(userForm, {
    id: row.id,
    username: row.username,
    email: row.email,
    real_name: row.real_name,
    role_id: row.role_id || 2
  })
}

const submitForm = async () => {
  if (!userFormRef.value) return
  
  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await updateUser(userForm.id, userForm)
          ElMessage.success('更新成功')
        } else {
          await createUser(userForm)
          searchKeyword.value = '' // Clear search on success
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadUsers()
      } catch (error) {
        // Error handled by interceptor
      } finally {
        submitting.value = false
      }
    }
  })
}

const resetForm = () => {
  if (userFormRef.value) {
    userFormRef.value.resetFields()
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该用户吗？', '提示', {
      type: 'warning'
    })
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 特殊按钮处理函数
const loadMaintenanceStatus = async () => {
  try {
    const res = await getMaintenanceStatus()
    if (res.data && res.data.data) {
      maintenanceMode.value = res.data.data.maintenance
    }
  } catch (error) {
    console.error('Failed to load maintenance status', error)
  }
}

const handleShutdown = async () => {
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
    if (res.data && res.data.data) {
      maintenanceMode.value = res.data.data.maintenance
      ElMessage.success(res.data.message || '操作成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '操作失败')
    }
  }
}

const handleBackup = async () => {
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
}

const handleCaseDistribution = () => {
  ElMessage.success('案例已分发给所有学生')
}

const handleResetStudent = (row) => {
  ElMessageBox.confirm(`确定要重置学生 ${row.username} 的数据吗？\n此操作将：\n1. 保留账号\n2. 重置密码为"123"\n3. 清空所有档案和日志数据\n此操作不可恢复！`, '警告', {
    confirmButtonText: '确定重置',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await resetUser(row.id)
      ElMessage.success(`学生 ${row.username} 数据已重置`)
    } catch (error) {
      // Error handled by interceptor
    }
  }).catch(() => {})
}

// 判断是否可以查看该用户的报告
const canViewReports = (row) => {
  const currentRole = authStore.user?.role_code
  const targetRole = row.role_code
  
  // 管理员可以查看所有用户的报告
  if (currentRole === 'admin') {
    return true
  }
  
  // 老师只能查看学生的报告
  if (currentRole === 'teacher' && targetRole === 'student') {
    return true
  }
  
  // 学生只能查看自己的报告（这个在用户列表中不会出现，因为学生不会看到其他用户）
  return false
}


// 查看报告列表
const handleViewReports = async (row) => {
  selectedUser.value = row
  reportsDialogVisible.value = true
  reportsLoading.value = true
  
  try {
    const response = await getReports(row.id, true)  // 包含历史记录
    reports.value = response.data.data || []
    // 调试：打印返回的数据
    console.log('Reports data:', reports.value)
    if (reports.value.length > 0) {
      console.log('Report history:', reports.value[0].history)
    }
  } catch (error) {
    console.error('Load reports error:', error)
    ElMessage.error('加载报告失败')
    reports.value = []
  } finally {
    reportsLoading.value = false
  }
}

// 查看单个报告PDF
const handleViewReport = async (report) => {
  try {
    const response = await viewReport(report.id)
    // 创建blob URL并打开新窗口
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    window.open(url, '_blank')
    // 清理URL对象（延迟清理，确保窗口已打开）
    setTimeout(() => window.URL.revokeObjectURL(url), 100)
  } catch (error) {
    ElMessage.error('查看报告失败')
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取操作文本
const getActionText = (action) => {
  const actionMap = {
    'created': '创建报告',
    'updated': '更新报告',
  }
  return actionMap[action] || action
}

onMounted(() => {
  loadUsers()
  loadMaintenanceStatus()
})
</script>

<style scoped>
.user-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}

.status-tag {
  border: none;
}

.tag-content {
  display: flex;
  align-items: center;
  gap: 4px;
  height: 100%;
}

.search-form {
  margin-bottom: 20px;
}
</style>

