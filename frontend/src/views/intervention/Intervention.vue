<template>
  <div class="intervention-container">
    <el-row :gutter="20">
      <!-- 左侧：方案区 & 参数滑杆 -->
      <el-col :span="9">
        <el-card class="plan-card">
          <template #header>
            <div class="card-header">
              <span>AI体重助手</span>
              <el-tag type="success" effect="dark">个人方案模拟</el-tag>
            </div>
          </template>
          
          <el-tabs v-model="activeTab">
            <!-- 体重管理 -->
            <el-tab-pane label="体重管理（AI）" name="weight-gain">
              <div class="weight-gain-section">
                <div style="margin-bottom: 20px;">
                  <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 8px; color: #606266; font-weight: 500;">目标类型:</label>
                    <el-radio-group v-model="weightGainForm.goalType" style="margin-bottom: 15px;">
                      <el-radio-button label="gain">我想增重</el-radio-button>
                      <el-radio-button label="loss">我想减重</el-radio-button>
                    </el-radio-group>
                  </div>
                  <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 8px; color: #606266; font-weight: 500;">
                      {{ weightGainForm.goalType === 'gain' ? '我想增重' : '我想减重' }}:
                    </label>
                    <el-input-number 
                      v-model="weightGainForm.targetWeight" 
                      :min="1" 
                      :max="50" 
                      :step="1"
                      style="width: 200px;"
                    />
                    <span style="margin-left: 10px; color: #606266;">斤</span>
                  </div>
                  <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 8px; color: #606266; font-weight: 500;">计划周期:</label>
                    <el-radio-group v-model="weightGainForm.weeks" style="display: flex; flex-wrap: wrap; gap: 8px;">
                      <el-radio-button :label="4">4周</el-radio-button>
                      <el-radio-button :label="8">8周</el-radio-button>
                      <el-radio-button :label="12">12周</el-radio-button>
                      <el-radio-button :label="16">16周</el-radio-button>
                      <el-radio-button :label="20">20周</el-radio-button>
                      <el-radio-button :label="24">24周</el-radio-button>
                      <el-radio-button :label="26">26周（半年）</el-radio-button>
                    </el-radio-group>
                  </div>
                  <div>
                    <el-button 
                      type="primary" 
                      @click="handleGenerateDailyPlan"
                      :loading="dailyPlanLoading"
                      :disabled="!hasUserProfile || !weightGainForm.targetWeight || weightGainForm.targetWeight <= 0"
                      :class="{ 'is-disabled-custom': !hasUserProfile }"
                      style="width: 100%;"
                    >
                      <el-icon style="margin-right: 5px"><MagicStick /></el-icon>
                      <span v-if="!hasUserProfile">请先完成个人档案</span>
                      <span v-else-if="dailyPlanLoading">正在生成中...请不要走开哦😘</span>
                      <span v-else>生成每日体重管理计划（AI）</span>
                    </el-button>
                    <div v-if="!hasUserProfile" style="margin-top: 8px; font-size: 12px; color: #909399; text-align: center;">
                      <el-icon style="margin-right: 3px;"><InfoFilled /></el-icon>
                      请先前往"我的档案"页面完善个人档案信息
                    </div>
                  </div>
                </div>
                
                <!-- 每日计划展示 -->
                <div v-if="dailyPlan" style="margin-top: 20px;">
                  <el-divider />
                  <!-- AI模式标识 -->
                  <div v-if="dailyPlanMode" style="margin-bottom: 15px; padding: 10px; border-radius: 4px;" 
                       :style="dailyPlanMode === 'ai' ? 'background: #e1f3d8; border: 1px solid #67c23a;' : 'background: #fdf6ec; border: 1px solid #e6a23c;'">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                      <div>
                        <el-icon v-if="dailyPlanMode === 'ai'" style="color: #67c23a; margin-right: 5px;"><Check /></el-icon>
                        <el-icon v-else style="color: #e6a23c; margin-right: 5px;"><Warning /></el-icon>
                        <strong v-if="dailyPlanMode === 'ai'" style="color: #67c23a;">
                          🤖 使用真实AI生成（{{ dailyPlanProvider?.toUpperCase() || 'AI' }}）
                        </strong>
                        <strong v-else style="color: #e6a23c;">
                          📝 使用模拟模式生成（基于规则算法）
                        </strong>
                        <div v-if="dailyPlanGoalType" style="margin-top: 5px; font-size: 12px; color: #606266;">
                          目标类型：{{ dailyPlanGoalType === 'gain' ? '增重' : '减重' }} | 
                          目标{{ dailyPlanGoalType === 'gain' ? '增重' : '减重' }}：{{ weightGainForm.targetWeight }}斤 | 
                          计划周期：{{ weightGainForm.weeks }}周
                        </div>
                      </div>
                      <el-tag v-if="dailyPlanMode === 'ai'" type="success" size="small">AI生成</el-tag>
                      <el-tag v-else type="warning" size="small">模拟模式</el-tag>
                    </div>
                  </div>
                  <div class="daily-plan-display">
                    <!-- 每日饮食建议 -->
                    <el-card shadow="hover" style="margin-bottom: 15px;">
                      <template #header>
                        <div style="font-weight: bold; color: #409EFF;">
                          <el-icon style="margin-right: 5px"><Food /></el-icon>
                          每日饮食建议
                        </div>
                      </template>
                      <div v-if="dailyPlan.daily_diet">
                        <div style="margin-bottom: 10px;">
                          <strong>总热量:</strong> {{ dailyPlan.daily_diet.total_calories }} kcal
                        </div>
                        <div style="margin-bottom: 10px;">
                          <strong>碳水化合物:</strong> {{ dailyPlan.daily_diet.carbohydrates?.amount }} {{ dailyPlan.daily_diet.carbohydrates?.unit }}
                          <span v-if="dailyPlan.daily_diet.carbohydrates?.sources" style="color: #909399; font-size: 12px; margin-left: 10px;">
                            ({{ dailyPlan.daily_diet.carbohydrates.sources.join('、') }})
                          </span>
                        </div>
                        <div style="margin-bottom: 10px;">
                          <strong>蛋白质:</strong> {{ dailyPlan.daily_diet.protein?.amount }} {{ dailyPlan.daily_diet.protein?.unit }}
                          <span v-if="dailyPlan.daily_diet.protein?.sources" style="color: #909399; font-size: 12px; margin-left: 10px;">
                            ({{ dailyPlan.daily_diet.protein.sources.join('、') }})
                          </span>
                        </div>
                        <div style="margin-bottom: 10px;">
                          <strong>脂肪:</strong> {{ dailyPlan.daily_diet.fat?.amount }} {{ dailyPlan.daily_diet.fat?.unit }}
                          <span v-if="dailyPlan.daily_diet.fat?.sources" style="color: #909399; font-size: 12px; margin-left: 10px;">
                            ({{ dailyPlan.daily_diet.fat.sources.join('、') }})
                          </span>
                        </div>
                        <div style="margin-bottom: 10px;">
                          <strong>膳食纤维:</strong> {{ dailyPlan.daily_diet.fiber?.amount }} {{ dailyPlan.daily_diet.fiber?.unit }}
                        </div>
                        <div style="margin-bottom: 10px;">
                          <strong>饮水量:</strong> {{ dailyPlan.daily_diet.water?.amount }} {{ dailyPlan.daily_diet.water?.unit }}
                        </div>
                        <div v-if="dailyPlan.daily_diet.notes && dailyPlan.daily_diet.notes.length > 0" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee;">
                          <strong>注意事项:</strong>
                          <ul style="margin: 5px 0 0 20px; color: #606266;">
                            <li v-for="(note, idx) in dailyPlan.daily_diet.notes" :key="idx">{{ note }}</li>
                          </ul>
                        </div>
                      </div>
                    </el-card>
                    
                    <!-- 每日运动建议 -->
                    <el-card shadow="hover" style="margin-bottom: 15px;">
                      <template #header>
                        <div style="font-weight: bold; color: #67C23A;">
                          <el-icon style="margin-right: 5px"><Basketball /></el-icon>
                          每日运动建议
                        </div>
                      </template>
                      <div v-if="dailyPlan.daily_exercise">
                        <div v-if="dailyPlan.daily_exercise.aerobic" style="margin-bottom: 10px;">
                          <strong>有氧运动:</strong> {{ dailyPlan.daily_exercise.aerobic.type }}，{{ dailyPlan.daily_exercise.aerobic.duration }} {{ dailyPlan.daily_exercise.aerobic.unit }}，{{ dailyPlan.daily_exercise.aerobic.frequency }}
                          <span v-if="dailyPlan.daily_exercise.aerobic.intensity" style="color: #909399; font-size: 12px; margin-left: 10px;">
                            ({{ dailyPlan.daily_exercise.aerobic.intensity }})
                          </span>
                        </div>
                        <div v-if="dailyPlan.daily_exercise.strength" style="margin-bottom: 10px;">
                          <strong>力量训练:</strong> {{ dailyPlan.daily_exercise.strength.type }}，{{ dailyPlan.daily_exercise.strength.duration }} {{ dailyPlan.daily_exercise.strength.unit }}，{{ dailyPlan.daily_exercise.strength.frequency }}
                          <span v-if="dailyPlan.daily_exercise.strength.focus" style="color: #909399; font-size: 12px; margin-left: 10px;">
                            ({{ dailyPlan.daily_exercise.strength.focus }})
                          </span>
                        </div>
                        <div v-if="dailyPlan.daily_exercise.steps" style="margin-bottom: 10px;">
                          <strong>日常步数:</strong> {{ dailyPlan.daily_exercise.steps.target }} {{ dailyPlan.daily_exercise.steps.unit }}
                        </div>
                        <div v-if="dailyPlan.daily_exercise.rest" style="margin-bottom: 10px;">
                          <strong>休息建议:</strong> {{ dailyPlan.daily_exercise.rest }}
                        </div>
                      </div>
                    </el-card>
                    
                    <!-- 注意事项和风险 -->
                    <el-card shadow="hover" v-if="dailyPlan.notes || dailyPlan.risks">
                      <template #header>
                        <div style="font-weight: bold; color: #E6A23C;">
                          <el-icon style="margin-right: 5px"><Warning /></el-icon>
                          注意事项与风险提示
                        </div>
                      </template>
                      <div v-if="dailyPlan.notes && dailyPlan.notes.length > 0" style="margin-bottom: 15px;">
                        <strong>注意事项:</strong>
                        <ul style="margin: 5px 0 0 20px; color: #606266;">
                          <li v-for="(note, idx) in dailyPlan.notes" :key="idx">{{ note }}</li>
                        </ul>
                      </div>
                      <div v-if="dailyPlan.risks && dailyPlan.risks.length > 0">
                        <strong style="color: #F56C6C;">潜在风险:</strong>
                        <ul style="margin: 5px 0 0 20px; color: #F56C6C;">
                          <li v-for="(risk, idx) in dailyPlan.risks" :key="idx">{{ risk }}</li>
                        </ul>
                      </div>
                    </el-card>
                  </div>
                </div>
              </div>
            </el-tab-pane>
            
            <!-- 膳食干预 -->
            <el-tab-pane label="膳食干预" name="diet">
              <div class="slider-group">
                <div class="slider-item">
                  <span class="label">碳水化合物 (%) <span class="value">{{ dietPlan.carb }}%</span></span>
                  <el-slider v-model="dietPlan.carb" :min="0" :max="100" @input="updatePrediction" />
                </div>
                <div class="slider-item">
                  <span class="label">蛋白质 (%) <span class="value">{{ dietPlan.protein }}%</span></span>
                  <el-slider v-model="dietPlan.protein" :min="0" :max="100" @input="updatePrediction" />
                </div>
                <div class="slider-item">
                  <span class="label">脂肪 (%) <span class="value">{{ dietPlan.fat }}%</span></span>
                  <el-slider v-model="dietPlan.fat" :min="0" :max="100" @input="updatePrediction" />
                </div>
                <div class="slider-item">
                  <span class="label">酒精 (g) <span class="value">{{ dietPlan.alcohol }}g</span></span>
                  <el-slider v-model="dietPlan.alcohol" :min="0" :max="200" @input="updatePrediction" />
                </div>
                <div class="slider-item">
                  <span class="label">膳食纤维 (g) <span class="value">{{ dietPlan.fiber }}g</span></span>
                  <el-slider v-model="dietPlan.fiber" :min="0" :max="100" @input="updatePrediction" />
                </div>
                <el-divider />
                <div class="slider-item">
                  <span class="label">总热量调整 (kcal) <span class="value">{{ dietPlan.calories }}</span></span>
                  <el-slider v-model="dietPlan.calories" :min="1000" :max="4000" :step="50" @input="updatePrediction" />
                </div>
              </div>
              
              <!-- 预测时长和AI预测按钮 -->
              <div class="action-area" style="margin-top: 20px;">
                <div style="margin-bottom: 10px; font-size: 14px; color: #606266;">预测时长:</div>
                <el-radio-group v-model="predictionWeeks" style="width: 100%; margin-bottom: 15px; display: flex; flex-wrap: wrap; gap: 8px;" @change="updatePrediction">
                  <el-radio-button :label="1">1周</el-radio-button>
                  <el-radio-button :label="4">4周</el-radio-button>
                  <el-radio-button :label="8">8周</el-radio-button>
                  <el-radio-button :label="12">12周</el-radio-button>
                  <el-radio-button :label="16">16周</el-radio-button>
                  <el-radio-button :label="20">20周</el-radio-button>
                  <el-radio-button :label="24">24周</el-radio-button>
                  <el-radio-button :label="26">26周（半年）</el-radio-button>
                </el-radio-group>
                
                <el-button 
                  type="primary" 
                  class="w-100" 
                  @click="runSimulation" 
                  :loading="loading"
                  :disabled="!logsFilled"
                  :class="{ 'highlight-btn': logsFilled }"
                >
                  <el-icon style="margin-right: 5px"><MagicStick /></el-icon>
                  {{ logsFilled ? '几周后我会怎样（AI预测）' : '请先完成今日日志' }}
                </el-button>
              </div>
            </el-tab-pane>
            
            <!-- 运动干预 -->
            <el-tab-pane label="运动干预" name="exercise">
              <div class="slider-group">
                <div class="slider-item">
                  <span class="label">有氧运动频率 (次/周) <span class="value">{{ exercisePlan.aerobicFreq }}次</span></span>
                  <el-slider v-model="exercisePlan.aerobicFreq" :min="0" :max="7" @input="updatePrediction" />
                </div>
                <div class="slider-item">
                  <span class="label">有氧运动强度 (RPE 1-10) <span class="value">{{ exercisePlan.aerobicIntensity }}</span></span>
                  <el-slider v-model="exercisePlan.aerobicIntensity" :min="1" :max="10" @input="updatePrediction" />
                </div>
                <div class="slider-item">
                  <span class="label">有氧运动时长 (分钟/次) <span class="value">{{ exercisePlan.aerobicDuration }}min</span></span>
                  <el-slider v-model="exercisePlan.aerobicDuration" :min="0" :max="120" :step="10" @input="updatePrediction" />
                </div>
                <el-divider />
                <div class="slider-item">
                  <span class="label">抗阻训练 (部位 RM) <span class="value">{{ exercisePlan.resistance }}</span></span>
                  <el-slider v-model="exercisePlan.resistance" :min="0" :max="10" @input="updatePrediction" />
                </div>
                <div class="slider-item">
                  <span class="label">日常步数 (NEAT) <span class="value">{{ exercisePlan.steps }}步</span></span>
                  <el-slider v-model="exercisePlan.steps" :min="2000" :max="20000" :step="500" @input="updatePrediction" />
                </div>
              </div>
              
              <!-- 预测时长和AI预测按钮 -->
              <div class="action-area" style="margin-top: 20px;">
                <div style="margin-bottom: 10px; font-size: 14px; color: #606266;">预测时长:</div>
                <el-radio-group v-model="predictionWeeks" style="width: 100%; margin-bottom: 15px; display: flex; flex-wrap: wrap; gap: 8px;" @change="updatePrediction">
                  <el-radio-button :label="1">1周</el-radio-button>
                  <el-radio-button :label="4">4周</el-radio-button>
                  <el-radio-button :label="8">8周</el-radio-button>
                  <el-radio-button :label="12">12周</el-radio-button>
                  <el-radio-button :label="16">16周</el-radio-button>
                  <el-radio-button :label="20">20周</el-radio-button>
                  <el-radio-button :label="24">24周</el-radio-button>
                  <el-radio-button :label="26">26周（半年）</el-radio-button>
                </el-radio-group>
                
                <el-button 
                  type="primary" 
                  class="w-100" 
                  @click="runSimulation" 
                  :loading="loading"
                  :disabled="!logsFilled"
                  :class="{ 'highlight-btn': logsFilled }"
                >
                  <el-icon style="margin-right: 5px"><MagicStick /></el-icon>
                  {{ logsFilled ? '几周后我会怎样（AI预测）' : '请先完成今日日志' }}
                </el-button>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
      
      <!-- 右侧：曲线预览 & 报告 -->
      <el-col :span="15">
        <el-card class="preview-card">
          <template #header>
            <div class="card-header">
              <span>曲线预览</span>
              <div class="legend">
                <span class="dot dashed"></span> 线性预测 (能量平衡)
                <span class="dot solid" style="margin-left: 15px;"></span> AI 修正预测
              </div>
            </div>
          </template>
          
          <div class="chart-wrapper" style="position: relative;">
            <div ref="chartRef" style="width: 100%; height: 400px;"></div>
          </div>

          <!-- 导出报告区域 -->
          <div class="export-section" style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 20px;">
              <div class="ai-suggestions" style="flex: 1;">
                <!-- 潜在风险 -->
                <div v-if="simulationResult && simulationResult.risks && simulationResult.risks.length > 0" style="margin-bottom: 20px;">
                  <h4 style="margin: 0 0 10px 0; color: #F56C6C; display: flex; align-items: center;">
                    <el-icon style="margin-right: 5px;"><Warning /></el-icon>
                    潜在风险
                  </h4>
                  <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #F56C6C;">
                    <li v-for="(risk, idx) in simulationResult.risks" :key="idx" style="margin-bottom: 5px;">{{ risk }}</li>
                  </ul>
                </div>
                
                <!-- AI专家建议 -->
                <div v-if="simulationResult && simulationResult.suggestions && simulationResult.suggestions.length > 0">
                  <h4 style="margin: 0 0 10px 0; color: #409EFF; display: flex; align-items: center;">
                    <el-icon style="margin-right: 5px;"><MagicStick /></el-icon>
                    AI 专家建议
                  </h4>
                  <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #606266;">
                    <li v-for="(sugg, idx) in simulationResult.suggestions" :key="idx" style="margin-bottom: 5px;">{{ sugg }}</li>
                  </ul>
                </div>
                
                <!-- 空状态提示 -->
                <div v-if="!simulationResult || (!simulationResult.suggestions && !simulationResult.risks)" style="color: #909399; font-size: 13px;">
                  点击左侧按钮获取 AI 建议
                </div>
              </div>
              
              <div class="export-controls" style="min-width: 200px; text-align: right; flex-shrink: 0;">
                <el-checkbox v-model="includeAISuggestions" style="margin-right: 15px;">包含 AI 建议</el-checkbox>
                <el-button type="success" plain @click="exportReport">
                  <el-icon style="margin-right: 5px"><Document /></el-icon> 生成 PDF 报告
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onActivated, watch, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MagicStick, Document, Food, Basketball, Warning, Check, InfoFilled } from '@element-plus/icons-vue'
import { getProfile } from '@/api/profile'
import { getDailyLog } from '@/api/dailyLog'
import request from '@/api/request'
import * as echarts from 'echarts'

const route = useRoute()
const activeTab = ref('diet')
const predictionWeeks = ref(4)
const loading = ref(false)
const logsFilled = ref(false) // 触发条件
const includeAISuggestions = ref(true)
const chartRef = ref(null)
let chartInstance = null

const simulationResult = ref(null)
const userProfile = ref(null)

// 加载用户档案的函数（可复用）
const loadUserProfile = async () => {
  try {
    const res = await getProfile()
    if (res.data && res.data.data) {
      userProfile.value = res.data.data
      if (userProfile.value.bmr) {
        dietPlan.calories = Math.round(userProfile.value.bmr * 1.2)
      }
    } else {
      userProfile.value = null
    }
  } catch (error) {
    console.warn('⚠️ 获取用户档案失败，可能尚未创建:', error)
    userProfile.value = null
  }
}
const linearData = ref([])
const aiData = ref([])
const dailyPlan = ref(null)
const dailyPlanLoading = ref(false)
const dailyPlanMode = ref(null) // 'ai' 或 'simulation'
const dailyPlanProvider = ref(null) // 'deepseek' 或 'qwen'
const dailyPlanGoalType = ref(null) // 'gain' 或 'loss'

const weightGainForm = reactive({
  goalType: 'gain', // 'gain' 增重 或 'loss' 减重
  targetWeight: 5, // 默认5斤
  weeks: 4
})

// 检查用户档案是否完善（所有必填字段都有值）
const hasUserProfile = computed(() => {
  if (!userProfile.value) {
    return false
  }
  
  const profile = userProfile.value
  
  // 检查所有必填字段是否都有值
  // 必填字段：gender, age, height_cm, weight_kg（根据 ProfileForm.vue 的 rules）
  
  // 检查性别（必须是非空字符串）
  if (!profile.gender || profile.gender.trim() === '') {
    return false
  }
  
  // 检查年龄（必须是有效的正数）
  if (profile.age === null || profile.age === undefined || profile.age <= 0) {
    return false
  }
  
  // 检查身高（必须是有效的正数，单位：cm）
  if (profile.height_cm === null || profile.height_cm === undefined || profile.height_cm <= 0) {
    return false
  }
  
  // 检查体重（必须是有效的正数，单位：kg）
  if (profile.weight_kg === null || profile.weight_kg === undefined || profile.weight_kg <= 0) {
    return false
  }
  
  return true
})

const dietPlan = reactive({
  carb: 50,
  protein: 20,
  fat: 30,
  alcohol: 0,
  fiber: 25,
  calories: 2000
})

const exercisePlan = reactive({
  aerobicFreq: 3,
  aerobicIntensity: 5,
  aerobicDuration: 30,
  resistance: 5, 
  steps: 6000
})

// 获取用户档案和今日日志状态
onMounted(async () => {
  try {
    // 使用 nextTick 确保 DOM 完全渲染后再初始化图表
    await nextTick()
    setTimeout(() => {
      initChart()
    }, 100)
    window.addEventListener('resize', handleResize)
    
    // 1. Profile
    await loadUserProfile()
    
    // 2. Check Today's Log
    try {
      const today = new Date().toISOString().split('T')[0]
      const logRes = await getDailyLog(today)
      if (logRes.data && logRes.data.data) {
        // 简单判断：如果有摄入热量和运动类型，就算填了
        const log = logRes.data.data
        if (log.calorie_intake > 0) {
          logsFilled.value = true
        }
      }
    } catch (error) {
      console.warn('获取今日日志失败:', error)
    }
    
    // Initial Linear Prediction
    updatePrediction()
  } catch (error) {
    console.error('Init failed', error)
  }
})

// 页面激活时重新加载档案（当用户从"我的档案"页面返回时）
onActivated(() => {
  loadUserProfile()
})

// 监听路由变化，当从其他页面返回时重新加载档案
watch(() => route.path, (newPath, oldPath) => {
  // 如果从"我的档案"页面返回，重新加载档案
  if (oldPath === '/profile' && newPath === '/intervention') {
    loadUserProfile()
  }
})

const handleResize = () => {
  chartInstance && chartInstance.resize()
}

const initChart = () => {
  if (!chartRef.value) {
    console.warn('⚠️ chartRef 未准备好，延迟初始化')
    return
  }
  
  // 检查DOM尺寸
  const width = chartRef.value.clientWidth
  const height = chartRef.value.clientHeight
  
  if (width === 0 || height === 0) {
    console.warn(`⚠️ 图表容器尺寸为0: ${width}x${height}，延迟初始化`)
    setTimeout(() => initChart(), 200)
    return
  }
  
  try {
    if (chartInstance) {
      chartInstance.dispose() // 清理旧实例
    }
    chartInstance = echarts.init(chartRef.value)
    renderChart()
    console.log('✅ 图表初始化成功')
  } catch (error) {
    console.error('❌ 图表初始化失败:', error)
  }
}

const renderChart = () => {
  if (!chartInstance) {
    console.warn('⚠️ 图表实例不存在，尝试重新初始化')
    initChart()
    return
  }
  
  // 确保有数据
  if (!linearData.value || linearData.value.length === 0) {
    console.warn('⚠️ 图表数据为空，跳过渲染')
    return
  }
  
  const weeks = predictionWeeks.value
  // 根据周数生成x轴数据，如果周数较多则只显示部分标签
  const xAxisData = Array.from({length: weeks + 1}, (_, i) => {
    if (i === 0) return '当前'
    if (weeks <= 12) {
      return `第${i}周`
    } else if (weeks <= 20) {
      // 20周以内，每2周显示一次
      return i % 2 === 0 ? `第${i}周` : ''
    } else {
      // 20周以上，每4周显示一次
      return i % 4 === 0 ? `第${i}周` : ''
    }
  })
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        let result = params[0].name.replace('当前', '第0周') + '<br/>'
        params.forEach(item => {
          result += `${item.seriesName}: ${item.value} kg<br/>`
        })
        return result
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: weeks > 20 ? '8%' : '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xAxisData,
      axisLabel: {
        rotate: weeks > 20 ? 45 : 0, // 如果周数超过20，旋转标签45度
        interval: 0, // 显示所有标签（即使为空字符串）
        formatter: function(value) {
          return value || '' // 只显示非空标签
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '体重 (kg)',
      scale: true
    },
    series: [
      {
        name: '线性预测',
        type: 'line',
        data: linearData.value,
        lineStyle: {
          type: 'dashed',
          width: 2,
          color: '#409EFF'
        },
        itemStyle: {
          color: '#409EFF'
        },
        smooth: true
      },
      {
        name: 'AI 修正',
        type: 'line',
        data: aiData.value,
        lineStyle: {
          type: 'solid',
          width: 3,
          color: '#67C23A'
        },
        itemStyle: {
          color: '#67C23A'
        },
        smooth: true
      }
    ]
  }
  
  chartInstance.setOption(option)
}

// 计算每日总消耗 (估算)
const calculateDailyExpenditure = () => {
  if (!userProfile.value) return 2000 
  
  const bmr = userProfile.value.bmr || 1500
  const weight = userProfile.value.weight_kg || 60
  
  // 1. 有氧: METs * kg * h * freq / 7
  // Intensity 1-10 mapped to METs 3-12 approx
  const mets = 3 + exercisePlan.aerobicIntensity * 0.9
  const aerobicDaily = (mets * weight * (exercisePlan.aerobicDuration / 60) * exercisePlan.aerobicFreq) / 7
  
  // 2. 力量: Resistance 0-10 mapped to kcal
  const resistanceDaily = (exercisePlan.resistance * 300) / 7 // Max 300kcal per session approx
  
  // 3. NEAT
  const neatDaily = exercisePlan.steps * 0.04
  
  // TEF (食物热效应) 计算
  // 蛋白质 ~25%, 碳水 ~8%, 脂肪 ~2%, 酒精 ~20%
  const proteinCals = dietPlan.calories * (dietPlan.protein / 100)
  const carbCals = dietPlan.calories * (dietPlan.carb / 100)
  const fatCals = dietPlan.calories * (dietPlan.fat / 100)
  const alcoholCals = dietPlan.alcohol * 7
  
  const tef = (proteinCals * 0.25) + (carbCals * 0.08) + (fatCals * 0.02) + (alcoholCals * 0.20)
  
  // 总消耗 = BMR + TEF + NEAT + EAT
  return Math.round(bmr + tef + neatDaily + aerobicDaily + resistanceDaily)
}

// 模拟线性预测更新（拖动滑块时触发，延迟<300ms）
let debounceTimer = null
const updatePrediction = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    const expenditure = calculateDailyExpenditure()
    const intake = dietPlan.calories
    const balance = intake - expenditure
    
    // Generate Linear Data Points
    const currentWeight = userProfile.value?.weight_kg || 60
    const newData = [currentWeight]
    
    for (let i = 1; i <= predictionWeeks.value; i++) {
      // 7700kcal = 1kg
      const totalDeficit = balance * 7 * i
      const weightChange = totalDeficit / 7700
      newData.push(parseFloat((currentWeight + weightChange).toFixed(2)))
    }
    
    linearData.value = newData
    // Clear AI data when params change until re-run
    // aiData.value = [] 
    renderChart()
  }, 200)
}

const runSimulation = async () => {
  if (!logsFilled.value) {
    ElMessage.warning('请先完成今日的饮食和运动日志')
    return
  }

  console.log('🔵 开始AI预测，检查日志状态:', logsFilled.value)
  loading.value = true
  try {
    const expenditure = calculateDailyExpenditure()
    const currentWeight = userProfile.value?.weight_kg || 60
    
    // 先计算线性预测数据（用于图表显示）
    const newLinearData = [currentWeight]
    const balance = dietPlan.calories - expenditure
    
    for (let i = 1; i <= predictionWeeks.value; i++) {
      const totalDeficit = balance * 7 * i
      const weightChange = totalDeficit / 7700
      newLinearData.push(parseFloat((currentWeight + weightChange).toFixed(2)))
    }
    linearData.value = newLinearData
    
    // 调用后端AI服务获取专业预测和建议
    try {
      const aiRes = await request.post('/ai/prediction', {
        calorie_intake: dietPlan.calories,
        calorie_expenditure: expenditure,
        carb_percent: dietPlan.carb,
        protein_percent: dietPlan.protein,
        fat_percent: dietPlan.fat,
        fiber_grams: dietPlan.fiber,
        alcohol_grams: dietPlan.alcohol,
        exercise_duration: exercisePlan.aerobicDuration * exercisePlan.aerobicFreq / 7, // 日均运动时长
        aerobic_freq: exercisePlan.aerobicFreq,
        aerobic_intensity: exercisePlan.aerobicIntensity,
        steps: exercisePlan.steps,
        weeks: predictionWeeks.value
      })
      
      if (aiRes.data && aiRes.data.code === 200 && aiRes.data.data) {
        const assessment = aiRes.data.data.assessment || aiRes.data.data
        
        console.log('✅ AI API调用成功，返回数据:', {
          weight: assessment.weight,
          fat: assessment.fat,
          risksCount: assessment.risks?.length || 0,
          suggestionsCount: assessment.suggestions?.length || 0,
          suggestions: assessment.suggestions
        })
        
        // 检查建议数量和质量
        const suggestionCount = assessment.suggestions?.length || 0
        
        // 日志输出
        if (suggestionCount === 0) {
          console.warn('⚠️ AI返回的建议为空，可能使用了模拟模式')
        } else if (suggestionCount < 5) {
          console.warn(`⚠️ AI返回的建议较少（${suggestionCount}条），期望至少5条`)
          console.warn('⚠️ 建议内容:', assessment.suggestions)
          console.warn('⚠️ 这可能是模拟模式的输出，请检查后端日志确认是否调用了真实API')
        } else {
          console.log(`✅ AI返回了 ${suggestionCount} 条建议，符合预期`)
        }
        
        // 使用AI返回的预测结果
        // 如果AI返回了体重变化，计算AI修正后的曲线
        const weightChangeStr = assessment.weight || '0 kg'
        const weightChangeNum = parseFloat(weightChangeStr.replace(/[^0-9.-]/g, '')) || 0
        
        const newAiData = [currentWeight]
        // 将总变化量分配到每周（考虑代谢适应）
        for (let i = 1; i <= predictionWeeks.value; i++) {
          // 使用递减模型：前期变化快，后期变慢
          const progress = i / predictionWeeks.value
          const adaptationFactor = 1 - (progress * 0.3) // 后期减慢30%
          const weeklyChange = (weightChangeNum / predictionWeeks.value) * adaptationFactor
          newAiData.push(parseFloat((currentWeight + weeklyChange * i).toFixed(2)))
        }
        aiData.value = newAiData
        
        simulationResult.value = {
          weight: assessment.weight || weightChangeStr,
          fat: assessment.fat || '0%',
          risks: assessment.risks || [],
          suggestions: assessment.suggestions || []
        }
        
        renderChart()
        
        // 显示成功消息（使用上面声明的 suggestionCount）
        if (suggestionCount >= 5) {
          ElMessage.success(`AI 专业预测完成，提供 ${suggestionCount} 条详细建议`)
        } else {
          ElMessage.success('AI 预测完成')
        }
        return
      } else {
        console.warn('⚠️ AI API返回格式异常:', aiRes.data)
      }
    } catch (aiError) {
      console.error('❌ AI服务调用失败:', aiError)
      console.error('错误详情:', {
        message: aiError.message,
        response: aiError.response?.data,
        status: aiError.response?.status,
        statusText: aiError.response?.statusText,
        url: aiError.config?.url,
        method: aiError.config?.method
      })
      // 不显示错误提示，直接降级到本地模拟（避免干扰用户体验）
      console.warn('⚠️ 降级到本地模拟模式')
      // 如果AI调用失败，降级到本地模拟
    }
    
    // 降级方案：本地模拟逻辑（与之前相同，但保留作为后备）
    const newAiData = [currentWeight]
    const weeklyDeficit = (dietPlan.calories - expenditure) * 7
    
    for (let i = 1; i <= predictionWeeks.value; i++) {
      const adaptationFactor = Math.max(0.5, 1 - (i * 0.02))
      const realDeficit = weeklyDeficit * adaptationFactor
      const change = realDeficit / 7700
      newAiData.push(parseFloat((currentWeight + change * i).toFixed(2)))
    }
    
    aiData.value = newAiData
    
    // 本地模拟建议（作为后备）
    const risks = []
    const suggestions = []

    if (dietPlan.calories < 1200) {
      risks.push('热量摄入过低，可能导致基础代谢损伤')
      risks.push('微量元素缺乏风险')
      suggestions.push('建议将热量提升至基础代谢(BMR)以上')
    } else if (dietPlan.calories > 3000) {
      risks.push('热量盈余过多，体脂增加风险高')
      suggestions.push('建议适当减少总热量摄入')
    }

    if (dietPlan.protein < 15) {
      risks.push('蛋白质摄入不足，肌肉流失风险')
      suggestions.push('增加瘦肉、蛋奶或豆制品的摄入')
    } else if (dietPlan.protein > 35) {
      suggestions.push('高蛋白饮食需注意肾脏负担，多喝水')
    }

    if (dietPlan.carb < 40) {
      risks.push('低碳水可能导致运动表现下降')
      suggestions.push('运动前后适当补充碳水')
    }

    if (dietPlan.fiber < 25) {
      risks.push('膳食纤维不足，肠道健康风险')
      suggestions.push('增加蔬菜、全谷物摄入')
    }

    if (dietPlan.alcohol > 0) {
      risks.push('酒精摄入会抑制脂肪氧化')
      suggestions.push('建议减少或避免酒精摄入')
    }

    if (exercisePlan.aerobicFreq > 5 && exercisePlan.aerobicIntensity > 8) {
      risks.push('高频高强度有氧可能导致过度训练')
      suggestions.push('建议安排1-2天完全休息日')
    }

    if (exercisePlan.resistance < 3) {
      suggestions.push('建议增加抗阻训练频率以保留瘦体重')
    }

    if (exercisePlan.steps < 4000) {
      risks.push('日常活动量(NEAT)过低')
      suggestions.push('建议增加日常步行，减少久坐')
    }

    if (suggestions.length === 0) {
      suggestions.push('当前的饮食和运动计划非常均衡，请继续保持！')
    }

    simulationResult.value = {
      weight: (newAiData[newAiData.length-1] - currentWeight).toFixed(1) + ' kg',
      fat: ((newAiData[newAiData.length-1] - currentWeight) * 0.8 / currentWeight * 100).toFixed(1) + '%',
      risks: risks,
      suggestions: suggestions
    }
    
    renderChart()
    ElMessage.success('AI 修正预测完成（使用本地模拟）')
    
  } catch (error) {
    console.error(error)
    ElMessage.error('预测失败')
  } finally {
    loading.value = false
  }
}

const exportReport = async () => {
  if (!simulationResult.value) {
    ElMessage.warning('请先点击按钮获取 AI 预测结果')
    return
  }

  if (!linearData.value || linearData.value.length === 0) {
    ElMessage.warning('请先点击"几周后我会怎样"按钮生成预测数据')
    return
  }

  loading.value = true
  ElMessage.success('正在生成标准 PDF 报告...')
  
  try {
    console.log('发送数据:', {
      dietPlan,
      exercisePlan,
      simulationResult: simulationResult.value,
      linearData: linearData.value,
      aiData: aiData.value,
      weeks: predictionWeeks.value
    })
    
    const res = await request.post('/reports/intervention/export', {
      dietPlan: dietPlan,
      exercisePlan: exercisePlan,
      simulationResult: simulationResult.value,
      linearData: linearData.value,
      aiData: aiData.value,
      weeks: predictionWeeks.value
    }, { responseType: 'blob' })
    
    if (!res.data || res.data.size === 0) {
      ElMessage.error('生成的PDF为空，请检查后端日志')
      return
    }
    
    const blob = new Blob([res.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    window.open(url, '_blank')
    ElMessage.success('PDF报告生成成功！')
  } catch (error) {
    console.error('PDF生成错误:', error)
    if (error.response) {
      ElMessage.error(`报告生成失败: ${error.response.data?.message || error.message}`)
    } else {
      ElMessage.error('报告生成失败，请检查网络连接或后端服务')
    }
  } finally {
    loading.value = false
  }
}

// 处理生成每日计划（包装函数，用于调试）
const handleGenerateDailyPlan = (event) => {
  console.log('🔵 handleGenerateDailyPlan 被调用', event)
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  generateDailyPlan()
}

// 测试函数（用于调试）
const testGenerateDailyPlan = () => {
  console.log('🧪 测试函数被调用')
  console.log('🧪 weightGainForm:', weightGainForm)
  console.log('🧪 generateDailyPlan 函数类型:', typeof generateDailyPlan)
  if (typeof generateDailyPlan === 'function') {
    console.log('🧪 直接调用 generateDailyPlan')
    generateDailyPlan()
  } else {
    console.error('❌ generateDailyPlan 不是一个函数!')
  }
}

// 生成每日计划
const generateDailyPlan = async () => {
  console.log('🔵 generateDailyPlan 函数被调用')
  console.log('🔵 表单数据:', weightGainForm)
  console.log('🔵 targetWeight 值:', weightGainForm.targetWeight)
  console.log('🔵 targetWeight 类型:', typeof weightGainForm.targetWeight)
  
  // 检查是否有用户档案
  if (!hasUserProfile.value) {
    ElMessage.warning('请先完善个人档案')
    return
  }
  
  if (!weightGainForm.targetWeight || weightGainForm.targetWeight <= 0) {
    const goalText = weightGainForm.goalType === 'gain' ? '增重' : '减重'
    console.warn(`⚠️ 目标${goalText}量无效:`, weightGainForm.targetWeight)
    ElMessage.warning(`请输入有效的目标${goalText}量`)
    return
  }

  console.log('✅ 开始发送请求...')
  dailyPlanLoading.value = true
  
  try {
    const requestData = {
      goal_type: weightGainForm.goalType, // 'gain' 或 'loss'
      target_weight_change: weightGainForm.targetWeight, // 目标体重变化（斤）
      weeks: weightGainForm.weeks
    }
    
    console.log('📤 发送每日计划请求到 /ai/daily-plan:', requestData)
    console.log('📤 请求URL:', '/api/ai/daily-plan')
    console.log('📤 目标类型:', weightGainForm.goalType === 'gain' ? '增重' : '减重')
    
    const res = await request.post('/ai/daily-plan', requestData)
    
    console.log('📥 收到响应:', res)
    console.log('📥 响应数据:', res.data)
    console.log('📥 响应数据类型:', typeof res.data)
    console.log('📥 res.data.code:', res.data?.code)
    console.log('📥 res.data.data:', res.data?.data)
    console.log('📥 res.data.data.daily_plan:', res.data?.data?.daily_plan)
    
    // 检查响应结构
    if (!res || !res.data) {
      console.error('❌ 响应格式错误：res 或 res.data 不存在')
      ElMessage.error('响应格式错误，请检查后端日志')
      return
    }
    
    if (res.data.code !== 200) {
      console.error('❌ 响应code不是200:', res.data.code)
      ElMessage.error(res.data?.message || '生成计划失败')
      return
    }
    
    if (!res.data.data) {
      console.error('❌ res.data.data 不存在')
      ElMessage.error('响应数据为空，请检查后端日志')
      return
    }
    
    const dailyPlanData = res.data.data.daily_plan
    console.log('📦 准备设置的 dailyPlan 数据:', dailyPlanData)
    console.log('📦 dailyPlan 数据类型:', typeof dailyPlanData)
    console.log('📦 dailyPlan 是否为 null/undefined:', dailyPlanData == null)
    console.log('📦 dailyPlan 是否为对象:', typeof dailyPlanData === 'object' && dailyPlanData !== null)
    
    if (!dailyPlanData) {
      console.error('❌ daily_plan 数据为空！')
      console.error('❌ res.data.data 完整内容:', res.data.data)
      ElMessage.error('后端返回的计划数据为空，请检查后端日志')
      return
    }
    
    // 强制设置响应式数据（使用 Object.assign 确保响应式）
    try {
      dailyPlan.value = JSON.parse(JSON.stringify(dailyPlanData))  // 深拷贝确保响应式
      dailyPlanMode.value = res.data.data.is_ai_generated ? 'ai' : 'simulation'
      dailyPlanProvider.value = res.data.data.provider || null
      dailyPlanGoalType.value = res.data.data.goal_type || weightGainForm.goalType || 'gain'
      
      console.log('✅ dailyPlan.value 已设置:', dailyPlan.value)
      console.log('✅ dailyPlan.value 类型:', typeof dailyPlan.value)
      console.log('✅ dailyPlan.value 是否为 null:', dailyPlan.value === null)
      console.log('✅ dailyPlan.value 是否为 undefined:', dailyPlan.value === undefined)
      console.log('✅ dailyPlanMode.value:', dailyPlanMode.value)
      console.log('✅ dailyPlanProvider.value:', dailyPlanProvider.value)
      console.log('✅ dailyPlan.value.daily_diet:', dailyPlan.value?.daily_diet)
      console.log('✅ dailyPlan.value.daily_exercise:', dailyPlan.value?.daily_exercise)
      console.log('✅ dailyPlan.value 键列表:', Object.keys(dailyPlan.value || {}))
      
      // 强制触发 Vue 更新
      await nextTick()
      console.log('✅ nextTick 后 dailyPlan.value:', dailyPlan.value)
      console.log('✅ nextTick 后 dailyPlan.value 是否为 null:', dailyPlan.value === null)
      
      // 再次验证数据
      if (!dailyPlan.value) {
        console.error('❌ nextTick 后 dailyPlan.value 仍然是 null/undefined！')
        ElMessage.error('数据设置失败，请刷新页面重试')
        return
      }
      
      const goalText = dailyPlanGoalType.value === 'gain' ? '增重' : '减重'
      const message = res.data.data.is_ai_generated
        ? `每日${goalText}计划生成成功（AI生成，使用${res.data.data.provider?.toUpperCase() || 'AI'}）`
        : `每日${goalText}计划生成成功（模拟模式）`
      ElMessage.success(message)
      
      console.log('✅ 每日计划设置成功')
      console.log('📊 生成模式:', dailyPlanMode.value)
      console.log('📊 AI服务商:', dailyPlanProvider.value)
      console.log('📊 计划内容:', dailyPlan.value)
    } catch (e) {
      console.error('❌ 设置 dailyPlan 时出错:', e)
      ElMessage.error('数据设置失败: ' + e.message)
    }
  } catch (error) {
    console.error('❌ 生成每日计划失败:', error)
    console.error('❌ 错误类型:', error.constructor.name)
    console.error('❌ 错误详情:', {
      message: error.message,
      response: error.response,
      responseData: error.response?.data,
      status: error.response?.status,
      statusText: error.response?.statusText,
      config: error.config,
      code: error.code,
      request: error.request
    })
    
    // 检查是否是超时错误
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      console.error('❌ 请求超时（可能是AI生成时间过长）')
      ElMessage.warning('AI生成时间较长，请稍等片刻后重试，或检查后端日志确认是否已生成')
    } else if (error.response?.status === 404) {
      // 404错误，通常是用户档案未找到
      const errorMessage = error.response?.data?.message || '请先完善个人档案'
      console.error('❌ 资源未找到:', errorMessage)
      ElMessage.warning(errorMessage)
    } else if (!error.response) {
      // 检查是否是网络错误
      console.error('❌ 网络错误：请求未到达服务器')
      console.error('❌ error.request:', error.request)
      ElMessage.error('网络错误：无法连接到服务器，请检查后端服务是否运行')
    } else {
      const errorMessage = error.response?.data?.message || 
                          error.message || 
                          '生成计划失败，请检查网络连接或后端服务'
      ElMessage.error(errorMessage)
    }
  } finally {
    dailyPlanLoading.value = false
    console.log('🔵 请求完成，loading状态已重置')
  }
}
</script>

<style scoped>
.intervention-container {
  padding: 20px;
}
.slider-item {
  margin-bottom: 20px;
}
.label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  color: #606266;
}
.w-100 {
  width: 100%;
}
.chart-container {
  min-height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  border-radius: 4px;
}
.legend {
  font-size: 12px;
  color: #909399;
}
.dot {
  display: inline-block;
  width: 10px;
  height: 2px;
  vertical-align: middle;
  margin: 0 5px;
}
.dot.dashed { border-top: 2px dashed #409EFF; }
.dot.solid { border-top: 2px solid #67C23A; }

.result-panel {
  width: 100%;
  padding: 20px;
}
.prediction-summary {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}
.prediction-summary .item {
  text-align: center;
}
.prediction-summary .value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}
.text-danger {
  color: #F56C6C;
}

/* 禁用状态的按钮样式 */
.is-disabled-custom {
  opacity: 0.6;
  cursor: not-allowed !important;
}

/* AI体重助手专属打印优化 */
@media print {
  .intervention-container {
    padding: 0;
  }
  
  /* 让左右两栏在打印时垂直排列，并各占 100% 宽度 */
  .el-row {
    display: block !important;
  }
  
  .el-col-9, .el-col-15 {
    width: 100% !important;
    max-width: 100% !important;
    flex: none !important;
    margin-bottom: 20px;
  }

  /* 打印时展开所有 Tab 内容（可选，但目前 el-tabs 只能打印激活态） */
  
  /* 确保图表可见 */
  .chart-wrapper {
    page-break-inside: avoid;
  }
  
  .export-section {
    border-top: none !important;
  }
}
</style>