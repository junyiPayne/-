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
              <el-button type="primary" @click="handleManageClassrooms">班级管理</el-button>
            </template>
            <!-- 教师特有按钮 -->
            <template v-if="authStore.user?.role_code === 'teacher'">
              <el-button type="success" @click="handleCaseDistribution">案例分发</el-button>
            </template>
            <el-button type="primary" @click="handleAdd" v-if="authStore.user?.role_code === 'admin'">新增用户</el-button>
          </div>
        </div>
      </template>
      
      <!-- 使用提示 -->
      <el-alert
        v-if="authStore.user?.role_code === 'admin'"
        type="info"
        :closable="false"
        style="margin-bottom: 15px;"
      >
        <template #default>
          <div style="font-size: 12px;">
            💡 <strong>提示：</strong>双击单元格可直接编辑（管理员权限），点击列标题可排序，点击列标题的筛选图标可筛选数据
          </div>
        </template>
      </el-alert>

      <el-form :inline="true" class="search-form" @submit.prevent>
        <el-form-item label="搜索">
          <el-input
            v-model="searchKeyword"
            placeholder="账号/邮箱/姓名/班级名称"
            clearable
            @keyup.enter.prevent="handleSearch"
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="班级筛选" v-if="authStore.user?.role_code === 'admin'">
          <el-select
            v-model="selectedClassId"
            placeholder="全部班级"
            clearable
            style="width: 200px"
            @change="handleSearch"
          >
            <el-option label="全部班级" :value="null" />
            <el-option
              v-for="classroom in classrooms"
              :key="classroom.id"
              :label="classroom.name"
              :value="classroom.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button v-if="selectedClassId !== null || searchKeyword" @click="handleResetFilter">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 班级管理区域（仅管理员可见） -->
      <div v-if="authStore.user?.role_code === 'admin' && classrooms.length > 0" style="margin-bottom: 20px; padding: 15px; background: #f5f7fa; border-radius: 4px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <strong>班级列表</strong>
          <el-button type="primary" size="small" @click="handleManageClassrooms">新增班级</el-button>
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
          <el-tag
            v-for="classroom in classrooms"
            :key="classroom.id"
            :type="selectedClassId === classroom.id ? 'primary' : ''"
            closable
            @close.stop="handleDeleteClassroom(classroom)"
            @click.stop="handleFilterByClassroom(classroom)"
            style="cursor: pointer;"
            size="large"
          >
            {{ classroom.name }}
            <span style="margin-left: 5px; color: #909399; font-size: 12px;">
              ({{ classroom.student_count || 0 }}学生 / {{ classroom.teacher_count || 0 }}教师)
            </span>
          </el-tag>
        </div>
      </div>

      <!-- 批量操作工具栏（仅管理员可见） -->
      <div v-if="authStore.user?.role_code === 'admin' && selectedUsers.length > 0" 
           style="margin-bottom: 15px; padding: 15px; background: #f0f9ff; border: 1px solid #b3d8ff; border-radius: 4px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="color: #409eff; font-weight: 500;">
            <el-icon style="margin-right: 5px;"><Select /></el-icon>
            已选择 <strong>{{ selectedUsers.length }}</strong> 个用户
          </div>
          <div>
            <el-button type="primary" @click="handleBatchAssignClassroom">
              <el-icon style="margin-right: 5px;"><School /></el-icon>
              批量分配班级
            </el-button>
            <el-button @click="clearSelection">取消选择</el-button>
          </div>
        </div>
      </div>

      <el-table 
        ref="userTableRef"
        :data="users" 
        v-loading="loading" 
        border
        @selection-change="handleSelectionChange"
        :default-sort="{ prop: 'role_name', order: 'ascending' }"
      >
        <el-table-column 
          v-if="authStore.user?.role_code === 'admin'"
          type="selection" 
          width="55" 
        />
        <el-table-column 
          prop="id" 
          label="ID" 
          width="80"
          sortable
          :filters="idFilters"
          :filter-method="filterById"
        />
        <el-table-column 
          prop="username" 
          label="账号（学号）"
          sortable
          :filters="usernameFilters"
          :filter-method="filterByUsername"
        >
          <template #default="{ row }">
            <span 
              v-if="editingCell !== `${row.id}_username`"
              @dblclick="startEdit(row.id, 'username', row.username)"
              style="cursor: pointer; padding: 2px 4px; border-radius: 3px;"
              :style="{ backgroundColor: canEdit(row) ? '#f0f9ff' : 'transparent' }"
            >
              {{ row.username }}
            </span>
            <el-input
              v-else
              v-model="editingValue"
              @blur="saveEdit(row.id, 'username', editingValue)"
              @keyup.enter="saveEdit(row.id, 'username', editingValue)"
              @keyup.esc="cancelEdit"
              size="small"
            />
          </template>
        </el-table-column>
        <el-table-column 
          prop="email" 
          label="邮箱"
          sortable
          :filters="emailFilters"
          :filter-method="filterByEmail"
        >
          <template #default="{ row }">
            <span 
              v-if="editingCell !== `${row.id}_email`"
              @dblclick="startEdit(row.id, 'email', row.email)"
              style="cursor: pointer; padding: 2px 4px; border-radius: 3px;"
              :style="{ backgroundColor: canEdit(row) ? '#f0f9ff' : 'transparent' }"
            >
              {{ row.email }}
            </span>
            <el-input
              v-else
              v-model="editingValue"
              @blur="saveEdit(row.id, 'email', editingValue)"
              @keyup.enter="saveEdit(row.id, 'email', editingValue)"
              @keyup.esc="cancelEdit"
              size="small"
            />
          </template>
        </el-table-column>
        <el-table-column 
          prop="real_name" 
          label="真实姓名"
          sortable
          :filters="realNameFilters"
          :filter-method="filterByRealName"
        >
          <template #default="{ row }">
            <span 
              v-if="editingCell !== `${row.id}_real_name`"
              @dblclick="startEdit(row.id, 'real_name', row.real_name)"
              style="cursor: pointer; padding: 2px 4px; border-radius: 3px;"
              :style="{ backgroundColor: canEdit(row) ? '#f0f9ff' : 'transparent' }"
            >
              {{ row.real_name || '-' }}
            </span>
            <el-input
              v-else
              v-model="editingValue"
              @blur="saveEdit(row.id, 'real_name', editingValue)"
              @keyup.enter="saveEdit(row.id, 'real_name', editingValue)"
              @keyup.esc="cancelEdit"
              size="small"
            />
          </template>
        </el-table-column>
        <el-table-column 
          prop="role_name" 
          label="角色"
          sortable
          :filters="roleFilters"
          :filter-method="filterByRole"
        >
          <template #default="{ row }">
            <span 
              v-if="editingCell !== `${row.id}_role_id`"
              @dblclick="canEdit(row) && startEditRole(row)"
              style="cursor: pointer; padding: 2px 4px; border-radius: 3px;"
              :style="{ backgroundColor: canEdit(row) ? '#f0f9ff' : 'transparent' }"
            >
              {{ row.role_name }}
            </span>
            <el-select
              v-else
              v-model="editingValue"
              @change="saveEdit(row.id, 'role_id', editingValue)"
              @blur="cancelEdit"
              size="small"
              style="width: 100%"
            >
              <el-option label="管理员" :value="1" />
              <el-option label="普通用户" :value="2" />
              <el-option label="教师" :value="3" />
              <el-option label="学生" :value="4" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column 
          label="班级" 
          width="150"
          sortable="custom"
          :sort-method="sortByClassroom"
          :filters="classroomFilters"
          :filter-method="filterByClassroom"
        >
          <template #default="{ row }">
            <span 
              v-if="editingCell !== `${row.id}_class_id`"
              @dblclick="canEdit(row) && startEditClassroom(row)"
              style="cursor: pointer; padding: 2px 4px; border-radius: 3px;"
              :style="{ backgroundColor: canEdit(row) ? '#f0f9ff' : 'transparent' }"
            >
              {{ row.classroom_name || '未分配' }}
            </span>
            <el-select
              v-else
              v-model="editingValue"
              @change="saveEdit(row.id, 'class_id', editingValue)"
              @blur="cancelEdit"
              size="small"
              style="width: 100%"
              clearable
            >
              <el-option label="未分配" :value="null" />
              <el-option
                v-for="classroom in classrooms"
                :key="classroom.id"
                :label="classroom.name"
                :value="classroom.id"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column 
          prop="is_active" 
          label="状态"
          sortable
          :filters="statusFilters"
          :filter-method="filterByStatus"
        >
          <template #default="{ row }">
            <template v-if="maintenanceMode && row.role_code !== 'admin'">
              <el-tag type="info" effect="dark">维护中</el-tag>
            </template>
            <template v-else>
              <el-tag 
                v-if="editingCell !== `${row.id}_is_active`"
                :type="row.is_active ? 'success' : 'danger'"
                @dblclick="canEdit(row) && startEditStatus(row)"
                style="cursor: pointer;"
              >
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
              <el-select
                v-else
                v-model="editingValue"
                @change="saveEdit(row.id, 'is_active', editingValue)"
                @blur="cancelEdit"
                size="small"
                style="width: 100%"
              >
                <el-option label="启用" :value="true" />
                <el-option label="禁用" :value="false" />
              </el-select>
            </template>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="400" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button-group>
                <el-button size="small" @click="handleEdit(row)">编辑</el-button>
                <!-- 查看报告按钮：管理员可以查看所有，老师只能查看学生 -->
                <el-button 
                  v-if="canViewReports(row)"
                  size="small" 
                  type="primary" 
                  @click="handleViewReports(row)"
                >查看报告</el-button>
              </el-button-group>
              <!-- 教师和管理员特有操作 -->
              <el-button 
                v-if="authStore.user?.role_code === 'teacher' || authStore.user?.role_code === 'admin'" 
                size="small" 
                type="warning" 
                @click="handleResetStudent(row)"
              >重置学生</el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
            </div>
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
        <el-form-item label="账号（学号）" prop="username">
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
        <el-form-item label="班级" prop="class_id" v-if="authStore.user?.role_code === 'admin'">
          <el-select v-model="userForm.class_id" placeholder="请选择班级" clearable filterable>
            <el-option label="未分配" :value="null" />
            <el-option
              v-for="classroom in classrooms"
              :key="classroom.id"
              :label="classroom.name"
              :value="classroom.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="班级" v-else-if="isEdit && userForm.class_id">
          <el-input :value="classrooms.find(c => c.id === userForm.class_id)?.name || '未知'" disabled />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            只有管理员可以修改班级归属
          </div>
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

    <!-- 批量分配班级对话框 -->
    <el-dialog
      v-model="batchAssignDialogVisible"
      title="批量分配班级"
      width="500px"
    >
      <div style="margin-bottom: 20px;">
        <p>已选择 <strong>{{ selectedUsers.length }}</strong> 个用户，请选择要分配的班级：</p>
        <el-alert
          type="info"
          :closable="false"
          style="margin-top: 10px;"
        >
          <template #default>
            <div style="font-size: 12px;">
              <div>• 分配后，所选用户将被分配到指定班级</div>
              <div>• 如果用户已有班级，将被覆盖</div>
            </div>
          </template>
        </el-alert>
      </div>
      <el-form label-width="100px">
        <el-form-item label="选择班级">
          <el-select
            v-model="batchAssignClassId"
            placeholder="请选择班级"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="classroom in classrooms"
              :key="classroom.id"
              :label="classroom.name"
              :value="classroom.id"
            />
            <el-option label="取消分配（设为未分配）" :value="null" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchAssignDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitBatchAssign" 
            :loading="batchAssigning"
            :disabled="batchAssignClassId === undefined"
          >
            确定分配
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 班级管理对话框 -->
    <el-dialog
      v-model="classroomDialogVisible"
      :title="isEditClassroom ? '编辑班级' : '新增班级'"
      width="500px"
      @close="resetClassroomForm"
    >
      <el-form
        ref="classroomFormRef"
        :model="classroomForm"
        :rules="classroomRules"
        label-width="80px"
      >
        <el-form-item label="班级名称" prop="name">
          <el-input v-model="classroomForm.name" placeholder="请输入班级名称" />
        </el-form-item>
        <el-form-item label="班级描述" prop="description">
          <el-input 
            v-model="classroomForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入班级描述（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="classroomDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitClassroomForm" :loading="submitting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Warning, CircleCheck, Select, School } from '@element-plus/icons-vue'
import { getUserList, deleteUser, createUser, updateUser, resetUser, batchUpdateUsers } from '@/api/users'
import { getMaintenanceStatus, toggleMaintenance, createBackup } from '@/api/admin'
import { getReports, viewReport } from '@/api/report'
import { getClassrooms, createClassroom, updateClassroom, deleteClassroom } from '@/api/classrooms'
import { getAvailableClassrooms } from '@/api/classrooms'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const users = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const selectedClassId = ref(null)
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
const userTableRef = ref(null)

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
  role_id: 2,
  class_id: null
})

const classrooms = ref([])
const classroomDialogVisible = ref(false)
const classroomForm = reactive({
  id: null,
  name: '',
  description: ''
})
const isEditClassroom = ref(false)

// 批量操作相关
const selectedUsers = ref([])
const batchAssignDialogVisible = ref(false)
const batchAssignClassId = ref(null)
const batchAssigning = ref(false)

// 内联编辑相关
const editingCell = ref(null)
const editingValue = ref('')
const editingRowId = ref(null)
const editingField = ref(null)

// 筛选器数据
const idFilters = ref([])
const usernameFilters = ref([])
const emailFilters = ref([])
const realNameFilters = ref([])
const roleFilters = ref([])
const classroomFilters = ref([])
const statusFilters = ref([
  { text: '启用', value: true },
  { text: '禁用', value: false }
])

// 验证用户名格式：只能包含字母和数字
const validateUsername = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入账号（学号）'))
  } else if (!/^[a-zA-Z0-9]+$/.test(value)) {
    callback(new Error('账号（学号）只能输入字母和数字'))
  } else {
    callback()
  }
}

const rules = {
  username: [{ required: true, validator: validateUsername, trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  role_id: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const classroomRules = {
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }]
}

const classroomFormRef = ref(null)

const handleSearch = () => {
  pagination.page = 1
  loadUsers()
}

const handleResetFilter = () => {
  searchKeyword.value = ''
  selectedClassId.value = null
  pagination.page = 1
  loadUsers()
}

const handleFilterByClassroom = (classroom) => {
  selectedClassId.value = classroom.id
  pagination.page = 1
  loadUsers()
}

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      search: searchKeyword.value || undefined
    }
    
    // 如果选择了班级，添加class_id参数
    if (selectedClassId.value !== null) {
      params.class_id = selectedClassId.value
    }
    
    const response = await getUserList(params)
    users.value = response.data.data.items
    pagination.total = response.data.data.total
    
    // 更新筛选器选项
    updateFilters()
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// 更新筛选器选项
const updateFilters = () => {
  // ID筛选器
  const uniqueIds = [...new Set(users.value.map(u => u.id))].sort((a, b) => a - b)
  idFilters.value = uniqueIds.slice(0, 20).map(id => ({ text: String(id), value: id }))
  
  // 用户名筛选器
  const uniqueUsernames = [...new Set(users.value.map(u => u.username).filter(Boolean))]
  usernameFilters.value = uniqueUsernames.slice(0, 20).map(u => ({ text: u, value: u }))
  
  // 邮箱筛选器
  const uniqueEmails = [...new Set(users.value.map(u => u.email).filter(Boolean))]
  emailFilters.value = uniqueEmails.slice(0, 20).map(e => ({ text: e, value: e }))
  
  // 真实姓名筛选器
  const uniqueNames = [...new Set(users.value.map(u => u.real_name).filter(Boolean))]
  realNameFilters.value = uniqueNames.slice(0, 20).map(n => ({ text: n, value: n }))
  
  // 角色筛选器
  const uniqueRoles = [...new Set(users.value.map(u => u.role_name).filter(Boolean))]
  roleFilters.value = uniqueRoles.map(r => ({ text: r, value: r }))
  
  // 班级筛选器
  const uniqueClassrooms = [...new Set(users.value.map(u => u.classroom_name).filter(Boolean))]
  classroomFilters.value = uniqueClassrooms.map(c => ({ text: c, value: c }))
  if (users.value.some(u => !u.classroom_name)) {
    classroomFilters.value.push({ text: '未分配', value: null })
  }
}

const handleAdd = async () => {
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
    role_id: 2,
    class_id: null
  })
  // 加载班级列表
  await loadClassrooms()
}

const handleEdit = async (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑用户'
  dialogVisible.value = true
  Object.assign(userForm, {
    id: row.id,
    username: row.username,
    email: row.email,
    real_name: row.real_name,
    role_id: row.role_id || 2,
    class_id: row.class_id || null
  })
  // 加载班级列表
  await loadClassrooms()
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

// 加载班级列表
const loadClassrooms = async () => {
  try {
    const res = await getClassrooms()
    if (res.data && res.data.code === 200) {
      classrooms.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载班级列表失败:', error)
  }
}

// 班级管理
const handleManageClassrooms = async () => {
  await loadClassrooms()
  classroomDialogVisible.value = true
  isEditClassroom.value = false
  resetClassroomForm()
}

// 编辑班级
const handleEditClassroom = (classroom) => {
  isEditClassroom.value = true
  Object.assign(classroomForm, {
    id: classroom.id,
    name: classroom.name,
    description: classroom.description || ''
  })
  classroomDialogVisible.value = true
}

// 删除班级
const handleDeleteClassroom = async (classroom) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除班级"${classroom.name}"吗？\n删除前请确保该班级没有用户。`,
      '删除班级',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteClassroom(classroom.id)
    ElMessage.success('班级删除成功')
    await loadClassrooms()
    await loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除班级失败:', error)
    }
  }
}

// 提交班级表单
const submitClassroomForm = async () => {
  if (!classroomFormRef.value) return
  
  await classroomFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEditClassroom.value) {
          await updateClassroom(classroomForm.id, classroomForm)
          ElMessage.success('班级更新成功')
        } else {
          await createClassroom(classroomForm)
          ElMessage.success('班级创建成功')
        }
        classroomDialogVisible.value = false
        await loadClassrooms()
        await loadUsers() // 刷新用户列表
      } catch (error) {
        // Error handled by interceptor
      } finally {
        submitting.value = false
      }
    }
  })
}

// 重置班级表单
const resetClassroomForm = () => {
  if (classroomFormRef.value) {
    classroomFormRef.value.resetFields()
  }
  Object.assign(classroomForm, {
    id: null,
    name: '',
    description: ''
  })
  isEditClassroom.value = false
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
    ElMessage.success(`备份成功，文件名为: ${res.data.filename}`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '备份失败')
    }
  }
}

const handleCaseDistribution = () => {
  ElMessage.success('案例已分发给所有学生')
}

// 批量选择相关方法
const handleSelectionChange = (selection) => {
  selectedUsers.value = selection
}

const clearSelection = () => {
  selectedUsers.value = []
  // 清除表格选择
  if (userTableRef.value) {
    userTableRef.value.clearSelection()
  }
}

const handleBatchAssignClassroom = async () => {
  if (selectedUsers.value.length === 0) {
    ElMessage.warning('请先选择要分配班级的用户')
    return
  }
  
  // 确保班级列表已加载
  if (classrooms.value.length === 0) {
    await loadClassrooms()
  }
  
  batchAssignClassId.value = null
  batchAssignDialogVisible.value = true
}

const submitBatchAssign = async () => {
  if (selectedUsers.value.length === 0) {
    ElMessage.warning('请先选择要分配班级的用户')
    return
  }
  
  batchAssigning.value = true
  try {
    const userIds = selectedUsers.value.map(user => user.id)
    await batchUpdateUsers({
      user_ids: userIds,
      updates: {
        class_id: batchAssignClassId.value
      }
    })
    
    const className = batchAssignClassId.value 
      ? classrooms.value.find(c => c.id === batchAssignClassId.value)?.name || '指定班级'
      : '未分配'
    
    ElMessage.success(`成功为 ${userIds.length} 个用户分配班级：${className}`)
    batchAssignDialogVisible.value = false
    selectedUsers.value = []
    await loadUsers()
    await loadClassrooms() // 刷新班级统计
  } catch (error) {
    // Error handled by interceptor
  } finally {
    batchAssigning.value = false
  }
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
  const currentUser = authStore.user
  
  // 管理员可以查看所有用户的报告
  if (currentRole === 'admin') {
    return true
  }
  
  // 老师只能查看自己班级的学生的报告
  if (currentRole === 'teacher' && targetRole === 'student') {
    // 检查是否是同一班级
    if (currentUser?.class_id && row.class_id && currentUser.class_id === row.class_id) {
      return true
    }
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

// 内联编辑方法
const canEdit = (row) => {
  // 管理员可以编辑所有用户，但不能编辑自己的一些关键字段
  if (authStore.user?.role_code === 'admin') {
    return true
  }
  // 教师可以编辑自己班级的学生
  if (authStore.user?.role_code === 'teacher' && row.role_code === 'student') {
    return row.class_id === authStore.user.class_id
  }
  return false
}

const startEdit = (rowId, field, value) => {
  if (!canEdit(users.value.find(u => u.id === rowId))) return
  editingCell.value = `${rowId}_${field}`
  editingValue.value = value || ''
  editingRowId.value = rowId
  editingField.value = field
}

const startEditRole = (row) => {
  if (!canEdit(row)) return
  editingCell.value = `${row.id}_role_id`
  // 角色ID映射
  const roleMap = {
    '管理员': 1,
    '普通用户': 2,
    '教师': 3,
    '学生': 4
  }
  editingValue.value = roleMap[row.role_name] || row.role_id
  editingRowId.value = row.id
  editingField.value = 'role_id'
}

const startEditClassroom = (row) => {
  if (!canEdit(row)) return
  editingCell.value = `${row.id}_class_id`
  editingValue.value = row.class_id || null
  editingRowId.value = row.id
  editingField.value = 'class_id'
}

const startEditStatus = (row) => {
  if (!canEdit(row)) return
  editingCell.value = `${row.id}_is_active`
  editingValue.value = row.is_active
  editingRowId.value = row.id
  editingField.value = 'is_active'
}

const saveEdit = async (rowId, field, value) => {
  if (editingCell.value !== `${rowId}_${field}`) return
  
  const row = users.value.find(u => u.id === rowId)
  if (!row) return
  
  // 如果值没有变化，直接取消编辑
  const originalValue = field === 'role_id' ? row.role_id : 
                        field === 'class_id' ? (row.class_id || null) :
                        field === 'is_active' ? row.is_active :
                        row[field]
  
  if (originalValue === value || (originalValue === null && value === '')) {
    cancelEdit()
    return
  }
  
  try {
    // 构建更新数据
    const updateData = {}
    
    // 字段映射
    if (field === 'role_id') {
      updateData.role_id = value
    } else if (field === 'class_id') {
      updateData.class_id = value
    } else if (field === 'is_active') {
      updateData.is_active = value
    } else {
      updateData[field] = value
    }
    
    await updateUser(rowId, updateData)
    ElMessage.success('更新成功')
    
    // 更新本地数据
    if (field === 'role_id') {
      const roleMap = {
        1: '管理员',
        2: '普通用户',
        3: '教师',
        4: '学生'
      }
      row.role_id = value
      row.role_name = roleMap[value] || row.role_name
    } else if (field === 'class_id') {
      row.class_id = value
      const classroom = classrooms.value.find(c => c.id === value)
      row.classroom_name = classroom ? classroom.name : null
    } else if (field === 'is_active') {
      row.is_active = value
    } else {
      row[field] = value
    }
    
    cancelEdit()
    // 更新筛选器
    updateFilters()
  } catch (error) {
    ElMessage.error('更新失败')
    cancelEdit()
  }
}

const cancelEdit = () => {
  editingCell.value = null
  editingValue.value = ''
  editingRowId.value = null
  editingField.value = null
}

// 筛选方法
const filterById = (value, row) => {
  return row.id === value
}

const filterByUsername = (value, row) => {
  return row.username === value
}

const filterByEmail = (value, row) => {
  return row.email === value
}

const filterByRealName = (value, row) => {
  return row.real_name === value
}

const filterByRole = (value, row) => {
  return row.role_name === value
}

const filterByClassroom = (value, row) => {
  if (value === null) {
    return !row.classroom_name
  }
  return row.classroom_name === value
}

const filterByStatus = (value, row) => {
  return row.is_active === value
}

// 排序方法
const sortByClassroom = (a, b) => {
  const aName = a.classroom_name || '未分配'
  const bName = b.classroom_name || '未分配'
  return aName.localeCompare(bName, 'zh-CN')
}

onMounted(() => {
  loadUsers()
  loadMaintenanceStatus()
  // 如果是管理员，加载班级列表
  if (authStore.user?.role_code === 'admin') {
    loadClassrooms()
  }
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

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  justify-content: flex-start;
}

.action-buttons .el-button,
.action-buttons .el-button-group {
  margin: 0;
}

.action-buttons .el-button-group .el-button {
  margin-left: 0;
}
</style>

