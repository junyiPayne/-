<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2>{{ isRegister ? '学生健康管理系统注册' : '学生健康管理系统登录' }}</h2>
      </div>
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        class="login-form"
        label-width="0"
      >
        <el-form-item prop="username">
          <el-input
            v-model="formData.username"
            :placeholder="isRegister ? '账号（学号）' : '账号（学号）'"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="real_name" v-if="isRegister">
          <el-input
            v-model="formData.real_name"
            placeholder="真实姓名（学生姓名）"
            size="large"
            prefix-icon="UserFilled"
          />
        </el-form-item>
        
        <el-form-item prop="email" v-if="isRegister">
          <el-input
            v-model="formData.email"
            placeholder="邮箱"
            size="large"
            prefix-icon="Message"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="密码"
            size="large"
            prefix-icon="Lock"
            @keyup.enter="handleSubmit"
          />
        </el-form-item>

        <el-form-item prop="confirmPassword" v-if="isRegister">
          <el-input
            v-model="formData.confirmPassword"
            type="password"
            placeholder="确认密码"
            size="large"
            prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item prop="role" v-if="isRegister">
          <el-radio-group v-model="formData.role" style="width: 100%; justify-content: center;">
            <el-radio value="student">学生</el-radio>
            <el-radio value="teacher">教师</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleSubmit"
            style="width: 100%"
          >
            {{ isRegister ? '注册' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        <el-link type="primary" @click="toggleMode">
          {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
        </el-link>
        <div v-if="!isRegister" style="margin-top: 10px; font-size: 12px; color: #999;">
          <span>默认账户: admin / admin123</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { register } from '@/api/auth'
import { getMaintenanceStatus } from '@/api/admin'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const isRegister = ref(false)
const maintenanceMode = ref(false)

const formData = reactive({
  username: '',
  real_name: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: 'student'
})

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== formData.password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

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

// 验证真实姓名：只能包含中文字符
const validateRealName = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入真实姓名（学生姓名）'))
  } else if (!/^[\u4e00-\u9fa5]+$/.test(value)) {
    callback(new Error('真实姓名只能输入中文字符'))
  } else {
    callback()
  }
}

const rules = computed(() => {
  const baseRules = {
    username: [
      { required: true, validator: validateUsername, trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' }
    ]
  }
  
  if (isRegister.value) {
    return {
      ...baseRules,
      real_name: [
        { required: true, validator: validateRealName, trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
      ],
      confirmPassword: [
        { required: true, validator: validatePass2, trigger: 'blur' }
      ],
      role: [{ required: true, message: '请选择角色', trigger: 'change' }]
    }
  }
  
  return baseRules
})

const toggleMode = async () => {
  // 如果要切换到注册模式，先检查维护状态
  if (!isRegister.value) {
    // 检查维护模式
    if (maintenanceMode.value) {
      ElMessage.warning('系统维护中，请耐心等候')
      return
    }
  }
  
  isRegister.value = !isRegister.value
  formRef.value?.resetFields()
  formData.role = 'student' // Reset role default
  formData.real_name = '' // Reset real_name
}

// 加载维护状态
const loadMaintenanceStatus = async () => {
  try {
    const response = await getMaintenanceStatus()
    maintenanceMode.value = response.data.data.maintenance || false
  } catch (error) {
    // 如果获取失败，不影响登录功能，默认为false
    console.error('获取维护状态失败:', error)
    maintenanceMode.value = false
  }
}

onMounted(() => {
  loadMaintenanceStatus()
})

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (isRegister.value) {
          // Register logic
          await register({
            username: formData.username,
            real_name: formData.real_name,
            email: formData.email,
            password: formData.password,
            role: formData.role
          })
          ElMessage.success('注册成功，请登录')
          toggleMode()
        } else {
          // Login logic
          await authStore.login({
            username: formData.username,
            password: formData.password
          })
          router.push('/theory')
        }
      } catch (error) {
        console.error(isRegister.value ? '注册失败:' : '登录失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  color: #333;
  font-size: 24px;
  font-weight: 500;
}

.login-form {
  margin-top: 20px;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  color: #999;
  font-size: 12px;
}
</style>

