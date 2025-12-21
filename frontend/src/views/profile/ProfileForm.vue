<template>
  <div class="profile-form">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>{{ profile ? '更新档案' : '创建档案' }}</span>
          <el-button type="primary" @click="handleSubmit" :loading="loading">保存修改</el-button>
        </div>
      </template>
      
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px" label-position="right">
        <el-row :gutter="40">
          <!-- 左侧：头像区域 -->
          <el-col :span="8" class="avatar-column">
            <div class="avatar-wrapper">
              <el-upload
                class="avatar-uploader"
                action="/api/profile/avatar"
                :show-file-list="false"
                :on-success="handleAvatarSuccess"
                :before-upload="beforeAvatarUpload"
                :headers="uploadHeaders"
              >
                <div v-if="avatarUrl" class="avatar-container">
                  <img :src="avatarUrl" class="avatar" />
                  <div class="avatar-mask">
                    <el-icon><Camera /></el-icon>
                    <span>更换头像</span>
                  </div>
                </div>
                <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
              </el-upload>
              <div class="avatar-tip">
                点击图片上传头像
                <el-tooltip content="支持 jpg/png 格式，大小 ≤ 2MB，系统将自动压缩为 400x400" placement="top">
                  <el-icon class="tip-icon"><QuestionFilled /></el-icon>
                </el-tooltip>
              </div>
            </div>
          </el-col>
          
          <!-- 右侧：信息编辑区域 -->
          <el-col :span="16">
            <div class="form-section-title">基本信息</div>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="真实姓名" prop="real_name">
                  <el-input v-model="formData.real_name" placeholder="请输入真实姓名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="出生日期" prop="birthday">
                  <el-date-picker
                    v-model="formData.birthday"
                    type="date"
                    placeholder="选择日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                    @change="handleBirthdayChange"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item prop="age">
                  <template #label>
                    <span>
                      年龄
                      <el-tooltip content="合法区间：18 - 64 岁" placement="top">
                        <el-icon><QuestionFilled /></el-icon>
                      </el-tooltip>
                    </span>
                  </template>
                  <el-input-number 
                    v-model="formData.age" 
                    style="width: 100%" 
                    @blur="validateRange('age', 18, 64, '年龄', '自动带出出生年月')"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="gender">
                  <template #label>
                    <span>
                      性别
                      <el-tooltip content="影响 BMR (基础代谢率) 公式计算" placement="top">
                        <el-icon><QuestionFilled /></el-icon>
                      </el-tooltip>
                    </span>
                  </template>
                  <el-radio-group v-model="formData.gender">
                    <el-radio value="male">男</el-radio>
                    <el-radio value="female">女</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
            </el-row>

            <div class="form-section-title">身体指标</div>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item prop="height_cm">
                  <template #label>
                    <span>
                      身高(cm)
                      <el-tooltip content="合法区间：120 - 230 cm" placement="top">
                        <el-icon><QuestionFilled /></el-icon>
                      </el-tooltip>
                    </span>
                  </template>
                  <el-input-number 
                    v-model="formData.height_cm" 
                    :precision="1" 
                    style="width: 100%" 
                    @blur="validateRange('height_cm', 120, 230, '身高', '请重新测量')"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="weight_kg">
                  <template #label>
                    <span>
                      体重(kg)
                      <el-tooltip content="合法区间：30 - 200 kg (需满足 BMI < 50)" placement="top">
                        <el-icon><QuestionFilled /></el-icon>
                      </el-tooltip>
                    </span>
                  </template>
                  <el-input-number 
                    v-model="formData.weight_kg" 
                    :precision="1" 
                    style="width: 100%" 
                    @blur="validateWeight"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item prop="waist_cm">
                  <template #label>
                    <span>
                      腰围(cm)
                      <el-tooltip content="合法区间：45 - 200 cm (必须 < 臀围)" placement="top">
                        <el-icon><QuestionFilled /></el-icon>
                      </el-tooltip>
                    </span>
                  </template>
                  <el-input-number 
                    v-model="formData.waist_cm" 
                    :precision="1" 
                    style="width: 100%" 
                    @blur="validateWaist"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="hip_cm">
                  <template #label>
                    <span>
                      臀围(cm)
                      <el-tooltip content="合法区间：50 - 250 cm (必须 > 腰围)" placement="top">
                        <el-icon><QuestionFilled /></el-icon>
                      </el-tooltip>
                    </span>
                  </template>
                  <el-input-number 
                    v-model="formData.hip_cm" 
                    :precision="1" 
                    style="width: 100%" 
                    @blur="validateHip"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item prop="body_fat_percent" label="体脂率(%)">
                  <el-input-number v-model="formData.body_fat_percent" :min="3" :max="60" :precision="1" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <div v-if="calculatedData" class="indicators-preview">
              <div class="form-section-title">当前指标预览</div>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="BMI">{{ calculatedData.bmi }}</el-descriptions-item>
                <el-descriptions-item label="BMR">{{ calculatedData.bmr }} kcal</el-descriptions-item>
                <el-descriptions-item label="体型评价">{{ calculatedData.weight_category }}</el-descriptions-item>
                <el-descriptions-item label="体脂评价">{{ calculatedData.body_fat_category }}</el-descriptions-item>
                <el-descriptions-item label="腰臀比(WHR)">{{ calculatedData.whr }}</el-descriptions-item>
                <el-descriptions-item label="腰高比(WHtR)">{{ calculatedData.whtr }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </el-col>
        </el-row>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, QuestionFilled, Camera } from '@element-plus/icons-vue'
import { getProfile, createProfile, updateProfile } from '@/api/profile'

const formRef = ref(null)
const loading = ref(false)
const profile = ref(null)
const avatarUrl = ref('')
const calculatedData = ref(null)

const formData = reactive({
  real_name: '',
  gender: 'male',
  birthday: '',
  age: 25,
  height_cm: 170,
  weight_kg: 65,
  waist_cm: 80,
  hip_cm: 95,
  body_fat_percent: 20
})

const rules = {
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
  height_cm: [{ required: true, message: '请输入身高', trigger: 'blur' }],
  weight_kg: [{ required: true, message: '请输入体重', trigger: 'blur' }],
}

// 校验并修正数值范围
const validateRange = (field, min, max, label, errorMsg) => {
  const value = formData[field]
  if (value === null || value === undefined) return

  if (value < min) {
    ElMessage.warning(`${label}不能小于 ${min}，${errorMsg}`)
    formData[field] = min
  } else if (value > max) {
    ElMessage.warning(`${label}不能大于 ${max}，${errorMsg}`)
    formData[field] = max
  }
}

// 校验体重 (BMI < 50)
const validateWeight = () => {
  const weight = formData.weight_kg
  const height = formData.height_cm
  
  if (!weight) return
  
  // 基础范围校验
  if (weight < 30) {
    ElMessage.warning('体重不能小于 30kg')
    formData.weight_kg = 30
    return
  } else if (weight > 200) {
    ElMessage.warning('体重不能大于 200kg')
    formData.weight_kg = 200
    return
  }

  // BMI 联合校验
  if (height) {
    const heightM = height / 100
    const bmi = weight / (heightM * heightM)
    if (bmi >= 50) {
      ElMessage.warning('BMI数值异常(≥50)，请检查身高体重数据')
      // 自动调整体重使 BMI < 50 (取 49.9)
      const maxWeight = 49.9 * heightM * heightM
      formData.weight_kg = parseFloat(maxWeight.toFixed(1))
    }
  }
}

// 校验腰围 (< 臀围)
const validateWaist = () => {
  const waist = formData.waist_cm
  const hip = formData.hip_cm
  
  if (!waist) return
  
  if (waist < 45) {
    ElMessage.warning('腰围不能小于 45cm，必须 < 臀围')
    formData.waist_cm = 45
    return
  } else if (waist > 200) {
    ElMessage.warning('腰围不能大于 200cm')
    formData.waist_cm = 200
    return
  }

  if (hip && waist >= hip) {
    ElMessage.warning('腰围必须小于臀围')
    formData.waist_cm = hip - 1
  }
}

// 校验臀围 (> 腰围)
const validateHip = () => {
  const hip = formData.hip_cm
  const waist = formData.waist_cm
  
  if (!hip) return
  
  if (hip < 50) {
    ElMessage.warning('臀围不能小于 50cm，必须 > 腰围')
    formData.hip_cm = 50
    return
  } else if (hip > 250) {
    ElMessage.warning('臀围不能大于 250cm')
    formData.hip_cm = 250
    return
  }

  if (waist && hip <= waist) {
    ElMessage.warning('臀围必须大于腰围')
    formData.hip_cm = waist + 1
  }
}

const handleBirthdayChange = (val) => {
  // 年龄计算由 watcher 处理，此处可扩展其他逻辑
}

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return {
    Authorization: `Bearer ${token}`
  }
})

const handleAvatarSuccess = (response, uploadFile) => {
  if (response.code === 200) {
    avatarUrl.value = response.data.url
    ElMessage.success('头像上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

const beforeAvatarUpload = (rawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
    ElMessage.error('头像必须是 JPG 或 PNG 格式!')
    return false
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }
  return true
}

const loadProfile = async () => {
  try {
    const response = await getProfile()
    if (response.data && response.data.data) {
      profile.value = response.data.data
      if (response.data.data.avatar) {
        avatarUrl.value = response.data.data.avatar
      }
      Object.assign(formData, {
        real_name: response.data.data.real_name || '',
        gender: response.data.data.gender,
        birthday: response.data.data.birthday,
        age: response.data.data.age,
        height_cm: response.data.data.height_cm,
        weight_kg: response.data.data.weight_kg,
        waist_cm: response.data.data.waist_cm,
        hip_cm: response.data.data.hip_cm,
        body_fat_percent: response.data.data.body_fat_percent
      })
      calculatedData.value = response.data.data
    } else {
      profile.value = null
    }
  } catch (error) {
    if (error.response?.data?.message !== '档案不存在，请先创建') {
      ElMessage.error('加载档案失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (profile.value) {
          await updateProfile(formData)
          ElMessage.success('档案更新成功')
        } else {
          await createProfile(formData)
          ElMessage.success('档案创建成功')
        }
        await loadProfile()
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      } finally {
        loading.value = false
      }
    }
  })
}

// Auto-calculate age from birthday
watch(() => formData.birthday, (newVal) => {
  if (newVal) {
    const birthDate = new Date(newVal)
    const today = new Date()
    let age = today.getFullYear() - birthDate.getFullYear()
    const m = today.getMonth() - birthDate.getMonth()
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age--
    }
    if (age >= 0) {
      formData.age = age
    }
  }
})

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-form {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatar-column {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 20px;
  border-right: 1px solid #f0f0f0;
}

.avatar-wrapper {
  text-align: center;
}

.avatar-uploader .el-upload {
  border: 2px dashed #409EFF; /* Colored border as requested */
  border-radius: 50%; /* Circular avatar */
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
  width: 180px;
  height: 180px;
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 180px;
  height: 180px;
  text-align: center;
  line-height: 180px;
}

.avatar-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.avatar {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

.avatar-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-container:hover .avatar-mask {
  opacity: 1;
}

.avatar-tip {
  margin-top: 10px;
  color: #909399;
  font-size: 12px;
}

.form-section-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 20px;
  padding-left: 10px;
  border-left: 4px solid #409EFF;
}

.indicators-preview {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px dashed #ebeef5;
}
</style>

