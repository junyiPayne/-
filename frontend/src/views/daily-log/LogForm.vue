<template>
  <div class="log-form">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>每日记录</span>
          <div class="header-controls">
            <el-button 
              v-if="authStore.user?.role_code === 'student'"
              type="primary" 
              @click="handleSubmitReport"
              style="margin-right: 15px"
            >
              提交报告
            </el-button>
            <el-button 
              link
              @click="isFormCollapsed = !isFormCollapsed"
              style="margin-right: 15px"
            >
              {{ isFormCollapsed ? '展开记录' : '收起记录' }}
            </el-button>
            <el-date-picker
              v-model="selectedDate"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </div>
        </div>
      </template>
      
      <div v-show="!isFormCollapsed">
        <el-tabs v-model="activeTab">
          <!-- 饮食记录 -->
          <el-tab-pane label="饮食记录" name="diet">
          <el-form :model="dietForm" label-width="120px">
            <el-form-item label="摄入热量(kcal)">
              <el-input-number v-model="dietForm.calorie_intake" :min="0" :precision="0" />
              <div v-if="recommendedValues.intake" style="margin-left: 10px; display: inline-block; color: #67C23A; font-size: 12px;">
                <el-tooltip content="基于TDEE和您的体重目标(BMI推断)计算得出" placement="top">
                  <span style="cursor: help; display: flex; align-items: center;">
                    <el-icon style="margin-right: 4px"><InfoFilled /></el-icon> 
                    推荐摄入: {{ recommendedValues.intake }} kcal
                  </span>
                </el-tooltip>
              </div>
            </el-form-item>
            <el-row :gutter="20">
              <el-col :span="16">
                <el-form-item label="碳水(%)">
                  <el-input-number v-model="dietForm.carb_percent" :min="0" :max="100" :precision="1" />
                </el-form-item>
                <el-form-item label="蛋白质(%)">
                  <el-input-number v-model="dietForm.protein_percent" :min="0" :max="100" :precision="1" />
                </el-form-item>
                <el-form-item label="脂肪(%)">
                  <el-input-number v-model="dietForm.fat_percent" :min="0" :max="100" :precision="1" />
                </el-form-item>
              </el-col>
              <el-col :span="8" style="display: flex; align-items: center; justify-content: center;">
                <div ref="pieChartRef" style="width: 100%; height: 160px;"></div>
              </el-col>
            </el-row>
            <el-form-item label="膳食纤维(克)">
              <el-input-number v-model="dietForm.fiber_grams" :min="0" :precision="1" />
            </el-form-item>
            <el-form-item label="酒精(克)">
              <el-input-number v-model="dietForm.alcohol_grams" :min="0" :precision="1" />
            </el-form-item>

            <el-divider content-position="left">食物录入</el-divider>
            
            <el-form-item label="录入方式">
              <el-radio-group v-model="dietInputMode" size="small">
                <el-radio-button label="search">🔍 搜索库</el-radio-button>
                <el-radio-button label="photo">📷 拍照识别</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <!-- Search Mode -->
            <div v-if="dietInputMode === 'search'" style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #eee;">
              <el-form-item label="搜索食物" label-width="80px" style="margin-bottom: 15px;">
                <el-autocomplete
                  v-model="foodSearchQuery"
                  :fetch-suggestions="querySearchFood"
                  placeholder="请输入食物名称 (如: 米饭)"
                  @select="handleFoodSelect"
                  style="width: 100%"
                  :trigger-on-focus="true"
                  clearable
                >
                  <template #default="{ item }">
                    <div style="display: flex; justify-content: space-between;">
                      <span>{{ item.name }}</span>
                      <span style="color: #999; font-size: 12px;">{{ item.calories }} kcal/{{ item.unit }}</span>
                    </div>
                  </template>
                </el-autocomplete>
                <div v-if="foodSearchQuery && !selectedFood" style="margin-top: 5px; color: #E6A23C; font-size: 12px; display: flex; align-items: center;">
                  <el-icon style="margin-right: 4px"><Warning /></el-icon> 
                  未找到该食物数据，请手动输入热量后添加
                </div>
              </el-form-item>
              <el-form-item label="份量(克)" label-width="80px">
                <el-slider v-model="foodWeight" :min="10" :max="1000" :step="10" show-input input-size="small" />
              </el-form-item>
              
              <el-form-item label="单项热量" label-width="80px">
                <div style="display: flex; align-items: center; width: 100%;">
                  <el-input-number v-model="currentItemCalories" :min="0" :disabled="!!selectedFood" style="width: 120px; margin-right: 10px;" />
                  <span style="margin-right: auto;">kcal</span>
                  <el-button type="primary" @click="addFoodItem" :disabled="!foodSearchQuery">
                    <el-icon style="margin-right: 5px"><Plus /></el-icon> 添加到今日列表
                  </el-button>
                </div>
              </el-form-item>

              <!-- Added Food List -->
              <div v-if="addedFoods.length > 0" style="margin-top: 15px; border-top: 1px dashed #ddd; padding-top: 10px;">
                <div style="font-size: 13px; color: #606266; margin-bottom: 10px;">今日已添加:</div>
                <div v-for="(food, index) in addedFoods" :key="index" style="display: flex; justify-content: space-between; align-items: center; background: #fff; padding: 8px; margin-bottom: 5px; border-radius: 4px; border: 1px solid #ebeef5;">
                  <div>
                    <span style="font-weight: bold;">{{ food.name }}</span>
                    <span style="color: #909399; font-size: 12px; margin-left: 8px;">{{ food.weight }}g</span>
                  </div>
                  <div style="display: flex; align-items: center;">
                    <span style="color: #E6A23C; font-weight: bold; margin-right: 10px;">{{ food.calories }} kcal</span>
                    <el-button type="danger" link size="small" @click="removeFoodItem(index)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
                <div style="text-align: right; margin-top: 10px; font-weight: bold; color: #409EFF;">
                  总计: {{ addedFoods.reduce((sum, item) => sum + item.calories, 0) }} kcal
                </div>
              </div>
            </div>

            <!-- Photo Mode -->
            <div v-if="dietInputMode === 'photo'" style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #eee;">
              <el-form-item label="上传图片" label-width="80px">
                <el-upload
                  v-model:file-list="fileList"
                  action="/api/daily-log/upload"
                  list-type="picture-card"
                  :on-success="handleUploadSuccess"
                  :on-remove="handleRemove"
                  :on-preview="handlePictureCardPreview"
                  :headers="uploadHeaders"
                  :before-upload="beforeUpload"
                  :limit="1"
                >
                  <el-icon><Plus /></el-icon>
                </el-upload>
              </el-form-item>
              <div style="margin-left: 80px;">
                <el-button type="success" plain size="small" disabled>
                  <el-icon style="margin-right: 5px"><Camera /></el-icon>
                  调用通义千问视觉API识别 (开发中)
                </el-button>
              </div>
            </div>

            <el-form-item label="食物描述">
              <el-input v-model="dietForm.food_description" type="textarea" :rows="2" placeholder="自动生成或手动输入" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 运动记录 -->
        <el-tab-pane label="运动记录" name="exercise">
          <el-form :model="exerciseForm" label-width="120px">
            <el-form-item label="运动目标">
              <el-select v-model="exerciseForm.exercise_goal" placeholder="请选择目标">
                <el-option label="保持体重" value="maintain" />
                <el-option label="减脂/减重" value="lose" />
                <el-option label="增肌/增重" value="gain" />
              </el-select>
            </el-form-item>
            <el-form-item label="运动类型">
              <el-select v-model="exerciseForm.exercise_type" placeholder="请选择" filterable>
                <el-option
                  v-for="item in MET_TABLE"
                  :key="item.name"
                  :label="item.name + (item.met > 0 ? ` (MET: ${item.met})` : '')"
                  :value="item.name"
                />
              </el-select>
            </el-form-item>
            <el-form-item v-if="exerciseForm.exercise_type === '自定义'" label="自定义MET值">
              <el-input-number v-model="exerciseForm.custom_met" :min="0" :precision="1" :step="0.1" />
              <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                MET值参考: 休息=1, 走路=3, 慢跑=8, 冲刺=15
              </span>
            </el-form-item>
            <el-form-item label="运动时长(分钟)">
              <el-input-number v-model="exerciseForm.exercise_duration" :min="0" />
            </el-form-item>
            <el-form-item label="运动强度">
              <el-select v-model="exerciseForm.exercise_intensity" placeholder="请选择">
                <el-option label="低强度" value="低强度" />
                <el-option label="中强度" value="中强度" />
                <el-option label="高强度" value="高强度" />
              </el-select>
            </el-form-item>
            <el-form-item label="运动频率(次/周)">
              <el-input-number v-model="exerciseForm.exercise_frequency" :min="0" />
            </el-form-item>
            <el-form-item label="消耗热量(kcal)">
              <el-input-number v-model="exerciseForm.calorie_expenditure" :min="0" :precision="0" />
              <div v-if="recommendedValues.expenditure" style="margin-left: 10px; display: inline-block; color: #E6A23C; font-size: 12px;">
                <el-tooltip content="基于TDEE和运动目标计算的推荐每日总消耗" placement="top">
                  <span style="cursor: help; display: flex; align-items: center;">
                    <el-icon style="margin-right: 4px"><InfoFilled /></el-icon> 
                    推荐总消耗: {{ targetExpenditure }} kcal
                  </span>
                </el-tooltip>
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 身体指标 -->
        <el-tab-pane label="身体指标" name="body">
          <el-form :model="bodyForm" label-width="120px">
            <el-form-item label="体重(kg)">
              <el-input-number v-model="bodyForm.daily_weight" :min="20" :max="300" :precision="1" />
            </el-form-item>
            <el-form-item label="腰围(cm)">
              <el-input-number v-model="bodyForm.daily_waist" :min="40" :max="200" :precision="1" />
            </el-form-item>
            <el-form-item label="臀围(cm)">
              <el-input-number v-model="bodyForm.daily_hip" :min="50" :max="200" :precision="1" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <el-form-item style="margin-top: 20px">
        <el-button type="primary" @click="handleSave" :loading="loading">保存记录</el-button>
      </el-form-item>
      </div>
      
      <!-- Chart Section -->
      <div class="chart-section" style="margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
          <h3 style="color: #606266; margin: 0;">热量趋势分析</h3>
          <el-date-picker
            v-model="chartMonth"
            type="month"
            placeholder="选择月份"
            format="YYYY-MM"
            value-format="YYYY-MM"
            @change="initChart"
            :clearable="false"
          />
        </div>
        <div ref="chartRef" style="width: 100%; height: 400px;"></div>
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible">
      <img w-full :src="dialogImageUrl" alt="Preview Image" style="width: 100%" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, InfoFilled, Camera, Warning, Delete } from '@element-plus/icons-vue'
import { getDailyLog, createOrUpdateLog, getDailyLogs, getStatistics } from '@/api/dailyLog'
import { getProfile } from '@/api/profile'
import { useAuthStore } from '@/stores/auth'
import * as echarts from 'echarts'
// 使用原生Date格式化日期

const route = useRoute()
const authStore = useAuthStore()
const loading = ref(false)
const activeTab = ref('diet')
const chartRef = ref(null)
const pieChartRef = ref(null)
const isFormCollapsed = ref(false)
let chartInstance = null
let pieChartInstance = null

const userWeight = ref(60) // Default weight fallback
const dietInputMode = ref('search') // 'search' or 'photo'

// Mock Food Database (China Food Composition 2022 subset)
const FOOD_DATABASE = [
  // Grains
  { name: '米饭 (蒸)', calories: 116, unit: '100g' },
  { name: '馒头', calories: 223, unit: '100g' },
  { name: '面条 (煮)', calories: 110, unit: '100g' },
  { name: '粥 (白米)', calories: 46, unit: '100g' },
  { name: '全麦面包', calories: 246, unit: '100g' },
  { name: '油条', calories: 388, unit: '100g' },
  { name: '玉米 (煮)', calories: 112, unit: '100g' },
  { name: '红薯 (蒸)', calories: 102, unit: '100g' },
  
  // Proteins
  { name: '鸡蛋 (煮)', calories: 144, unit: '100g' },
  { name: '鸡蛋 (煎)', calories: 209, unit: '100g' },
  { name: '牛奶', calories: 54, unit: '100ml' },
  { name: '酸奶', calories: 72, unit: '100g' },
  { name: '豆浆', calories: 31, unit: '100ml' },
  { name: '鸡胸肉 (生)', calories: 118, unit: '100g' },
  { name: '鸡腿 (烤)', calories: 181, unit: '100g' },
  { name: '猪肉 (瘦)', calories: 143, unit: '100g' },
  { name: '猪肉 (五花)', calories: 349, unit: '100g' },
  { name: '牛肉 (瘦)', calories: 106, unit: '100g' },
  { name: '牛排', calories: 200, unit: '100g' },
  { name: '羊肉', calories: 203, unit: '100g' },
  { name: '虾仁', calories: 85, unit: '100g' },
  { name: '三文鱼', calories: 139, unit: '100g' },
  { name: '豆腐', calories: 84, unit: '100g' },
  
  // Vegetables
  { name: '青菜 (炒)', calories: 40, unit: '100g' },
  { name: '菠菜 (炒)', calories: 45, unit: '100g' },
  { name: '西兰花 (煮)', calories: 33, unit: '100g' },
  { name: '西红柿', calories: 18, unit: '100g' },
  { name: '黄瓜', calories: 16, unit: '100g' },
  { name: '胡萝卜', calories: 39, unit: '100g' },
  { name: '土豆 (炒)', calories: 120, unit: '100g' },
  
  // Fruits
  { name: '苹果', calories: 53, unit: '100g' },
  { name: '香蕉', calories: 93, unit: '100g' },
  { name: '橙子', calories: 47, unit: '100g' },
  { name: '葡萄', calories: 45, unit: '100g' },
  { name: '西瓜', calories: 31, unit: '100g' },
  { name: '草莓', calories: 32, unit: '100g' },
  
  // Dishes
  { name: '西红柿炒鸡蛋', calories: 85, unit: '100g' },
  { name: '宫保鸡丁', calories: 130, unit: '100g' },
  { name: '鱼香肉丝', calories: 140, unit: '100g' },
  { name: '红烧肉', calories: 400, unit: '100g' },
  { name: '麻婆豆腐', calories: 110, unit: '100g' },
  { name: '饺子 (猪肉白菜)', calories: 220, unit: '100g' },
  { name: '汉堡包', calories: 250, unit: '100g' },
  { name: '薯条', calories: 312, unit: '100g' },
  { name: '可乐', calories: 43, unit: '100ml' },
  { name: '奶茶', calories: 150, unit: '100ml' }
]

const foodSearchQuery = ref('')
const selectedFood = ref(null)
const foodWeight = ref(100)
const addedFoods = ref([])
const currentItemCalories = ref(0)

const querySearchFood = (queryString, cb) => {
  const results = queryString
    ? FOOD_DATABASE.filter(createFilter(queryString))
    : FOOD_DATABASE
  // call callback function to return suggestions
  cb(results.map(item => ({ value: item.name, ...item })))
}

const createFilter = (queryString) => {
  return (restaurant) => {
    return (restaurant.name.toLowerCase().indexOf(queryString.toLowerCase()) > -1)
  }
}

const handleFoodSelect = (item) => {
  selectedFood.value = item
  calculateCurrentItemCalories()
}

const calculateCurrentItemCalories = () => {
  if (selectedFood.value && foodWeight.value > 0) {
    // Simple calculation: (Calories / 100) * Weight
    const cal = (selectedFood.value.calories / 100) * foodWeight.value
    currentItemCalories.value = Math.round(cal)
  } else {
    currentItemCalories.value = 0
  }
}

const addFoodItem = () => {
  const name = selectedFood.value ? selectedFood.value.name : foodSearchQuery.value
  if (!name) return

  // If manual input (no selectedFood), use the manually entered calories if > 0, else 0
  // But we don't have a manual calorie input for the *current item* yet in the UI.
  // For now, if selectedFood exists, use calculated. If not, use 0 (user can edit total later) or prompt?
  // Let's assume for now we only add if we have calories or just add name.
  
  // Actually, let's allow adding even if 0 calories, user can edit total.
  // But better: if selectedFood is null, we don't know calories per 100g.
  // Let's rely on currentItemCalories.
  
  addedFoods.value.push({
    name: name,
    weight: foodWeight.value,
    calories: currentItemCalories.value
  })
  
  updateDietFormFromList()
  
  // Reset inputs
  selectedFood.value = null
  foodSearchQuery.value = ''
  foodWeight.value = 100
  currentItemCalories.value = 0
}

const removeFoodItem = (index) => {
  addedFoods.value.splice(index, 1)
  updateDietFormFromList()
}

const updateDietFormFromList = () => {
  if (addedFoods.value.length > 0) {
    const totalCalories = addedFoods.value.reduce((sum, item) => sum + item.calories, 0)
    dietForm.calorie_intake = totalCalories
    
    const description = addedFoods.value.map(item => `${item.name} ${item.weight}g`).join('; ')
    dietForm.food_description = description
  } else {
    dietForm.calorie_intake = 0
    dietForm.food_description = ''
  }
}

watch(foodWeight, () => {
  calculateCurrentItemCalories()
})

// Watch for manual typing in search box
watch(foodSearchQuery, (newVal) => {
  if (!newVal) {
    selectedFood.value = null
    currentItemCalories.value = 0
    return
  }
  // If user types something that doesn't match selected food, reset selection
  if (selectedFood.value && newVal !== selectedFood.value.name) {
    selectedFood.value = null
    currentItemCalories.value = 0
  }
})

// MET Table (Sorted by MET High to Low)
const MET_TABLE = [
  { name: '跑步 (16 km/h)', met: 16.0 },
  { name: '跑步 (14 km/h)', met: 14.0 },
  { name: '跳绳 (快)', met: 12.0 },
  { name: '游泳 (蝶泳)', met: 11.0 },
  { name: '跑步 (10 km/h)', met: 10.0 },
  { name: '跳绳 (中等)', met: 10.0 },
  { name: '足球 (竞技)', met: 10.0 },
  { name: '篮球 (比赛)', met: 8.0 },
  { name: '游泳 (自由泳)', met: 8.0 },
  { name: 'HIIT (高强度间歇)', met: 8.0 },
  { name: '网球 (单打)', met: 8.0 },
  { name: '登山 (负重)', met: 7.5 },
  { name: '有氧舞蹈', met: 7.0 },
  { name: '羽毛球 (竞技)', met: 7.0 },
  { name: '骑行 (20 km/h)', met: 8.0 },
  { name: '慢跑 (8 km/h)', met: 8.0 },
  { name: '力量训练 (高强度)', met: 6.0 },
  { name: '游泳 (蛙泳)', met: 5.5 },
  { name: '快走 (6 km/h)', met: 5.0 },
  { name: '羽毛球 (休闲)', met: 4.5 },
  { name: '乒乓球', met: 4.0 },
  { name: '太极拳', met: 4.0 },
  { name: '力量训练 (轻度)', met: 3.5 },
  { name: '散步 (4 km/h)', met: 3.0 },
  { name: '瑜伽', met: 2.5 },
  { name: '普拉提', met: 3.0 },
  { name: '家务劳动', met: 2.5 },
  { name: '站立工作', met: 1.8 },
  { name: '坐姿工作', met: 1.3 },
  { name: '睡眠', met: 0.9 },
  { name: '自定义', met: 0 }
]

const dialogImageUrl = ref('')
const dialogVisible = ref(false)

// 监听路由变化，自动切换标签
watch(() => route.path, (newPath) => {
  if (newPath.includes('exercise')) {
    activeTab.value = 'exercise'
  } else {
    activeTab.value = 'diet'
  }
}, { immediate: true })

const getToday = () => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
const getCurrentMonth = () => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
}

const selectedDate = ref(getToday())
const chartMonth = ref(getCurrentMonth())

// 监听日期变化，自动加载数据
watch(selectedDate, (newDate) => {
  if (newDate) {
    loadLog()
    // 刷新图表以更新高亮
    initChart()
  }
})

const dietForm = reactive({
  calorie_intake: null,
  carb_percent: null,
  protein_percent: null,
  fat_percent: null,
  fiber_grams: null,
  alcohol_grams: null,
  food_description: '',
  food_images: []
})

const exerciseForm = reactive({
  exercise_goal: 'maintain',
  exercise_type: '',
  exercise_duration: null,
  exercise_intensity: '',
  exercise_frequency: null,
  calorie_expenditure: null,
  custom_met: 0
})

// Watchers for auto-calculation
watch(() => [exerciseForm.exercise_type, exerciseForm.exercise_duration, exerciseForm.custom_met, exerciseForm.exercise_intensity], () => {
  calculateCalories()
})

const calculateCalories = () => {
  const selectedExercise = MET_TABLE.find(e => e.name === exerciseForm.exercise_type)
  let met = 0
  
  if (selectedExercise) {
    if (selectedExercise.name === '自定义') {
      met = parseFloat(exerciseForm.custom_met) || 0
    } else {
      met = selectedExercise.met
    }
  }

  if (met > 0 && exerciseForm.exercise_duration > 0 && userWeight.value > 0) {
    // Intensity Multiplier
    const intensityMultipliers = {
      '低强度': 0.8,
      '中强度': 1.0,
      '高强度': 1.2
    }
    const multiplier = intensityMultipliers[exerciseForm.exercise_intensity] || 1.0

    // Formula: Calories = MET * Weight(kg) * Time(hours) * Intensity
    const hours = exerciseForm.exercise_duration / 60
    exerciseForm.calorie_expenditure = Math.round(met * userWeight.value * hours * multiplier)
  }
}

const bodyForm = reactive({
  daily_weight: null,
  daily_waist: null,
  daily_hip: null
})

const recommendedValues = reactive({
  intake: null,
  expenditure: null
})

const targetExpenditure = computed(() => {
  const base = recommendedValues.expenditure || 2000
  const goal = exerciseForm.exercise_goal
  if (goal === 'lose') return Math.round(base + 300)
  if (goal === 'gain') return Math.round(base)
  return base
})

const fileList = ref([])

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return {
    Authorization: `Bearer ${token}`
  }
})

const handleUploadSuccess = (response, uploadFile) => {
  if (response.code === 200) {
    ElMessage.success('上传成功')
    // 后端返回的是相对路径 /static/uploads/xxx
    // 在开发环境中，我们需要通过代理访问，或者拼接完整的后端地址
    // 这里假设 vue.config.js 配置了 /static 的代理，或者我们手动处理
    // 暂时直接使用返回的 url，但在显示时可能需要处理
    uploadFile.url = response.data.url
  } else {
    ElMessage.error(response.message || '上传失败')
    const index = fileList.value.indexOf(uploadFile)
    if (index !== -1) fileList.value.splice(index, 1)
  }
}

const handleRemove = (uploadFile, uploadFiles) => {
  console.log(uploadFile, uploadFiles)
}

const handlePictureCardPreview = (uploadFile) => {
  dialogImageUrl.value = uploadFile.url
  dialogVisible.value = true
}

const beforeUpload = (rawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png' && rawFile.type !== 'image/gif') {
    ElMessage.error('图片格式必须是 JPG/PNG/GIF!')
    return false
  } else if (rawFile.size / 1024 / 1024 > 5) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

// Watch diet form changes to update pie chart
watch(() => [dietForm.carb_percent, dietForm.protein_percent, dietForm.fat_percent], () => {
  updatePieChart()
})

const initPieChart = () => {
  if (!pieChartRef.value) return
  if (!pieChartInstance) {
    pieChartInstance = echarts.init(pieChartRef.value)
  }
  updatePieChart()
}

const updatePieChart = () => {
  if (!pieChartInstance) return
  
  const data = [
    { value: dietForm.carb_percent || 0, name: '碳水' },
    { value: dietForm.protein_percent || 0, name: '蛋白质' },
    { value: dietForm.fat_percent || 0, name: '脂肪' }
  ]
  
  const total = data.reduce((sum, item) => sum + item.value, 0)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}%'
    },
    series: [
      {
        name: '饮食结构',
        type: 'pie',
        radius: ['40%', '90%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 5,
          borderColor: '#fff',
          borderWidth: 1
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '12',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: total > 0 ? data : [{value: 1, name: '无数据', itemStyle: {color: '#eee'}}]
      }
    ],
    color: ['#409EFF', '#67C23A', '#E6A23C']
  }
  
  pieChartInstance.setOption(option)
}

const loadLog = async () => {
  if (!selectedDate.value) return
  
  try {
    const response = await getDailyLog(selectedDate.value)
    if (response.data && response.data.data) {
      const log = response.data.data
      Object.assign(dietForm, {
        calorie_intake: log.calorie_intake,
        carb_percent: log.carb_percent,
        protein_percent: log.protein_percent,
        fat_percent: log.fat_percent,
        fiber_grams: log.fiber_grams,
        alcohol_grams: log.alcohol_grams,
        food_description: log.food_description,
        food_images: log.food_images ? JSON.parse(log.food_images) : []
      })
      
      // 初始化图片列表
      if (dietForm.food_images && dietForm.food_images.length > 0) {
        fileList.value = dietForm.food_images.map((url, index) => ({
          name: `Image ${index + 1}`,
          url: url
        }))
      } else {
        fileList.value = []
      }

      Object.assign(exerciseForm, {
        exercise_type: log.exercise_type,
        exercise_duration: log.exercise_duration,
        exercise_intensity: log.exercise_intensity,
        exercise_frequency: log.exercise_frequency,
        calorie_expenditure: log.calorie_expenditure
      })
      Object.assign(bodyForm, {
        daily_weight: log.daily_weight,
        daily_waist: log.daily_waist,
        daily_hip: log.daily_hip
      })
      
      recommendedValues.intake = log.recommended_intake
      recommendedValues.expenditure = log.recommended_expenditure
      
      // Update pie chart
      updatePieChart()
    } else {
      // 清空表单
      Object.assign(dietForm, {
        calorie_intake: null,
        carb_percent: null,
        protein_percent: null,
        fat_percent: null,
        fiber_grams: null,
        alcohol_grams: null,
        food_description: '',
        food_images: []
      })
      fileList.value = []
      Object.assign(exerciseForm, {
        exercise_type: '',
        exercise_duration: null,
        exercise_intensity: '',
        exercise_frequency: null,
        calorie_expenditure: null
      })
      Object.assign(bodyForm, {
        daily_weight: null,
        daily_waist: null,
        daily_hip: null
      })
      recommendedValues.intake = null
      recommendedValues.expenditure = null
      
      updatePieChart()
    }
  } catch (error) {
    console.error('加载日志失败:', error)
  }
}

const handleSave = async () => {
  loading.value = true
  try {
    // 更新 food_images
    dietForm.food_images = fileList.value.map(file => {
      if (file.response && file.response.data && file.response.data.url) {
        return file.response.data.url
      }
      return file.url
    })

    const data = {
      log_date: selectedDate.value,
      ...dietForm,
      ...exerciseForm,
      ...bodyForm
    }
    await createOrUpdateLog(data)
    ElMessage.success('保存成功')
    // 保存成功后刷新图表
    initChart()
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    loading.value = false
  }
}

const initChart = async () => {
  if (!chartRef.value) return
  
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
    chartInstance.on('click', (params) => {
      if (params.name) {
        const day = params.name
        const [year, month] = chartMonth.value.split('-')
        const newDate = `${year}-${month}-${day}`
        selectedDate.value = newDate
        // 如果表单被收起，自动展开
        if (isFormCollapsed.value) {
          isFormCollapsed.value = false
        }
      }
    })
  }
  
  try {
    const res = await getStatistics({
      month: chartMonth.value
    })
    
    if (res.data && res.data.data && res.data.data.logs) {
      const logs = res.data.data.logs
      
      // 生成当月所有日期
      const [year, month] = chartMonth.value.split('-').map(Number)
      const daysInMonth = new Date(year, month, 0).getDate()
      
      const dates = []
      const intakes = []
      const expenditures = []
      const weights = []
      const waists = []
      const hips = []
      const recIntakes = []
      const recExpenditures = []
      const logDetails = []
      
      // 创建日志映射
      const logMap = {}
      logs.forEach(l => {
        logMap[l.log_date] = l
      })
      
      for (let i = 1; i <= daysInMonth; i++) {
        const dayStr = String(i).padStart(2, '0')
        const dateStr = `${year}-${String(month).padStart(2, '0')}-${dayStr}`
        dates.push(dayStr)
        
        const log = logMap[dateStr]
        intakes.push(log ? (log.calorie_intake || 0) : 0)
        expenditures.push(log ? (log.calorie_expenditure || 0) : 0)
        weights.push(log ? (log.daily_weight || null) : null)
        waists.push(log ? (log.daily_waist || null) : null)
        hips.push(log ? (log.daily_hip || null) : null)
        
        // 推荐值
        recIntakes.push(log ? (log.recommended_intake || null) : null)
        recExpenditures.push(log ? (log.recommended_expenditure || null) : null)
        
        logDetails.push(log || null)
      }
      
      const option = {
        title: {
          text: `${year}年${month}月 热量收支与身体指标`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: function (params) {
            const index = params[0].dataIndex
            const log = logDetails[index]
            const date = params[0].axisValue
            const fullDate = `${year}-${String(month).padStart(2, '0')}-${date}`
            
            let html = `<div style="font-weight:bold;margin-bottom:5px;">${fullDate}</div>`
            
            params.forEach(param => {
               let unit = 'kcal'
               if (param.seriesName === '体重') unit = 'kg'
               else if (param.seriesName === '腰围' || param.seriesName === '臀围') unit = 'cm'
               
               if (param.value != null) {
                 html += `${param.marker} ${param.seriesName}: ${param.value} ${unit}<br/>`
               }
            })

            if (log) {
              html += `<div style="margin-top:10px;border-top:1px solid #eee;padding-top:5px;">`
              
              // Diet
              html += `<strong>饮食:</strong><br/>`
              if (log.food_description) {
                  html += `<span style="font-size:12px;color:#ddd">${log.food_description}</span><br/>`
              } else {
                  html += `<span style="font-size:12px;color:#999">无详细描述</span><br/>`
              }
              
              // Exercise
              html += `<div style="margin-top:5px;"><strong>运动:</strong></div>`
              if (log.exercise_type) {
                  html += `<span style="font-size:12px;color:#ddd">${log.exercise_type} (${log.exercise_duration || 0}分钟)</span>`
              } else {
                  html += `<span style="font-size:12px;color:#999">无运动记录</span>`
              }
              
              // AI Analysis
              if (log.ai_risk_assessment || log.ai_suggestions) {
                  html += `<div style="margin-top:5px;border-top:1px dashed #eee;padding-top:5px;"><strong>AI 分析:</strong></div>`
                  
                  if (log.ai_risk_assessment) {
                      html += `<div style="font-size:12px;color:#F56C6C;margin-bottom:2px;">⚠️ ${log.ai_risk_assessment}</div>`
                  }
                  
                  if (log.ai_suggestions) {
                      try {
                          let suggestions = log.ai_suggestions
                          if (typeof suggestions === 'string') {
                              suggestions = JSON.parse(suggestions)
                          }
                          if (Array.isArray(suggestions)) {
                              suggestions.forEach(s => {
                                  html += `<div style="font-size:12px;color:#67C23A;">💡 ${s}</div>`
                              })
                          }
                      } catch (e) {}
                  }
              }
              
              html += `</div>`
            } else {
               html += `<div style="margin-top:10px;color:#999;font-size:12px;">无详细记录</div>`
            }
            
            return html
          }
        },
        legend: {
          data: ['摄入热量', '消耗热量', '推荐摄入', '推荐消耗', '体重', '腰围', '臀围'],
          bottom: 0
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisTick: { alignWithLabel: true },
          name: '日期',
          axisLabel: {
            color: (value) => {
              const [year, month] = chartMonth.value.split('-')
              const currentFullDate = `${year}-${month}-${value}`
              return currentFullDate === selectedDate.value ? '#409EFF' : '#606266'
            },
            fontWeight: (value) => {
              const [year, month] = chartMonth.value.split('-')
              const currentFullDate = `${year}-${month}-${value}`
              return currentFullDate === selectedDate.value ? 'bold' : 'normal'
            }
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '热量 (kcal)',
            position: 'left'
          },
          {
            type: 'value',
            name: '指标 (kg/cm)',
            position: 'right',
            splitLine: { show: false }
          }
        ],
        series: [
          {
            name: '摄入热量',
            type: 'bar',
            data: intakes,
            itemStyle: { color: '#E6A23C' },
            label: { show: false }
          },
          {
            name: '消耗热量',
            type: 'bar',
            data: expenditures,
            itemStyle: { color: '#67C23A' },
            label: { show: false }
          },
          {
            name: '推荐摄入',
            type: 'line',
            data: recIntakes,
            itemStyle: { color: '#E6A23C' },
            lineStyle: { type: 'dashed', width: 2 },
            symbol: 'none',
            connectNulls: true
          },
          {
            name: '推荐消耗',
            type: 'line',
            data: recExpenditures,
            itemStyle: { color: '#67C23A' },
            lineStyle: { type: 'dashed', width: 2 },
            symbol: 'none',
            connectNulls: true
          },
          {
            name: '体重',
            type: 'line',
            yAxisIndex: 1,
            data: weights,
            connectNulls: true,
            itemStyle: { color: '#409EFF' },
            symbol: 'circle',
            symbolSize: 6
          },
          {
            name: '腰围',
            type: 'line',
            yAxisIndex: 1,
            data: waists,
            connectNulls: true,
            itemStyle: { color: '#F56C6C' },
            lineStyle: { type: 'dashed' },
            symbol: 'none'
          },
          {
            name: '臀围',
            type: 'line',
            yAxisIndex: 1,
            data: hips,
            connectNulls: true,
            itemStyle: { color: '#909399' },
            lineStyle: { type: 'dotted' },
            symbol: 'none'
          }
        ]
      }
      
      chartInstance.setOption(option)
    }
  } catch (e) {
    console.error('Failed to load chart data', e)
  }
}

const handleSubmitReport = () => {
  ElMessageBox.confirm('确定要提交当前的健康报告吗？', '提交报告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info',
  }).then(() => {
    ElMessage.success('报告提交成功')
  }).catch(() => {})
}

onMounted(async () => {
  try {
    // Fetch user profile for weight
    const profileRes = await getProfile()
    if (profileRes.data && profileRes.data.weight_kg) {
      userWeight.value = profileRes.data.weight_kg
    }
  } catch (error) {
    console.error('Failed to load profile weight', error)
  }

  loadLog()
  initChart()
  initPieChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
  }
  if (pieChartInstance) {
    pieChartInstance.dispose()
  }
})

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
  if (pieChartInstance) {
    pieChartInstance.resize()
  }
}
</script>

<style scoped>
.log-form {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-controls {
  display: flex;
  align-items: center;
}
</style>

