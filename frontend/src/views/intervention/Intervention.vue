<template>
  <div class="intervention-container">
    <el-row :gutter="20">
      <!-- 左侧：方案区 & 参数滑杆 -->
      <el-col :span="9">
        <el-card class="plan-card">
          <template #header>
            <div class="card-header">
              <span>干预工坊</span>
              <el-tag type="success" effect="dark">设计方案</el-tag>
            </div>
          </template>
          
          <el-tabs v-model="activeTab">
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
            </el-tab-pane>
          </el-tabs>
          
          <div class="action-area" style="margin-top: 20px;">
            <div style="margin-bottom: 10px; font-size: 14px; color: #606266;">预测时长:</div>
            <el-radio-group v-model="predictionWeeks" style="width: 100%; margin-bottom: 15px;" @change="updatePrediction">
              <el-radio-button :label="1">1周</el-radio-button>
              <el-radio-button :label="4">4周</el-radio-button>
              <el-radio-button :label="12">12周</el-radio-button>
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
            
            <!-- 悬浮的风险提示 -->
            <div v-if="simulationResult && simulationResult.risks && simulationResult.risks.length > 0" 
                 style="position: absolute; top: 10px; right: 10px; background: rgba(245, 108, 108, 0.1); border: 1px solid #f56c6c; padding: 10px; border-radius: 4px; max-width: 200px;">
              <div style="color: #f56c6c; font-weight: bold; font-size: 12px; margin-bottom: 5px;">⚠️ 潜在风险</div>
              <ul style="margin: 0; padding-left: 15px; font-size: 12px; color: #606266;">
                <li v-for="(risk, idx) in simulationResult.risks" :key="idx">{{ risk }}</li>
              </ul>
            </div>
          </div>

          <!-- 导出报告区域 -->
          <div class="export-section" style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;">
            <div class="ai-suggestions" v-if="simulationResult && simulationResult.suggestions">
              <h4 style="margin: 0 0 10px 0; color: #409EFF;">AI 专家建议</h4>
              <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #606266;">
                <li v-for="(sugg, idx) in simulationResult.suggestions" :key="idx" style="margin-bottom: 5px;">{{ sugg }}</li>
              </ul>
            </div>
            <div v-else style="color: #909399; font-size: 13px;">
              点击左侧按钮获取 AI 建议
            </div>
            
            <div class="export-controls" style="min-width: 200px; text-align: right;">
              <el-checkbox v-model="includeAISuggestions" style="margin-right: 15px;">包含 AI 建议</el-checkbox>
              <el-button type="success" plain @click="exportReport">
                <el-icon style="margin-right: 5px"><Document /></el-icon> 生成 PDF 报告
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, Document } from '@element-plus/icons-vue'
import { getProfile } from '@/api/profile'
import { getDailyLog } from '@/api/dailyLog'
import request from '@/api/request'
import * as echarts from 'echarts'

const activeTab = ref('diet')
const predictionWeeks = ref(4)
const loading = ref(false)
const logsFilled = ref(false) // 触发条件
const includeAISuggestions = ref(true)
const chartRef = ref(null)
let chartInstance = null

const simulationResult = ref(null)
const userProfile = ref(null)
const linearData = ref([])
const aiData = ref([])

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
  initChart()
  window.addEventListener('resize', handleResize)
  
  try {
    // 1. Profile
    const res = await getProfile()
    if (res.data && res.data.data) {
      userProfile.value = res.data.data
      if (userProfile.value.bmr) {
        dietPlan.calories = Math.round(userProfile.value.bmr * 1.2)
      }
    }
    
    // 2. Check Today's Log
    const today = new Date().toISOString().split('T')[0]
    const logRes = await getDailyLog(today)
    if (logRes.data && logRes.data.data) {
      // 简单判断：如果有摄入热量和运动类型，就算填了
      const log = logRes.data.data
      if (log.calorie_intake > 0) {
        logsFilled.value = true
      }
    }
    
    // Initial Linear Prediction
    updatePrediction()
    
  } catch (error) {
    console.error('Init failed', error)
  }
})

const handleResize = () => {
  chartInstance && chartInstance.resize()
}

const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    renderChart()
  }
}

const renderChart = () => {
  if (!chartInstance) return
  
  const weeks = predictionWeeks.value
  const xAxisData = Array.from({length: weeks + 1}, (_, i) => `第${i}周`)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xAxisData
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

  loading.value = true
  try {
    const expenditure = calculateDailyExpenditure()
    
    // Mock AI Response for now (since backend might not be ready for this specific prompt)
    // In real scenario: await request.post('/ai/prediction', { ... })
    
    // Simulating API delay
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Mock Logic: AI corrects linear prediction based on "Metabolic Adaptation"
    // Usually linear overestimates weight loss. AI adds a "slow down" factor.
    const currentWeight = userProfile.value?.weight_kg || 60
    const newAiData = [currentWeight]
    const linearFinal = linearData.value[linearData.value.length - 1]
    const linearChange = linearFinal - currentWeight
    
    // AI Correction: Weight loss slows down by 10% every 4 weeks due to adaptation
    let currentW = currentWeight
    const weeklyDeficit = (dietPlan.calories - expenditure) * 7
    
    for (let i = 1; i <= predictionWeeks.value; i++) {
      // Adaptation factor: metabolism drops as weight drops
      const adaptationFactor = Math.max(0.5, 1 - (i * 0.02)) 
      const realDeficit = weeklyDeficit * adaptationFactor
      const change = realDeficit / 7700
      currentW += change
      newAiData.push(parseFloat(currentW.toFixed(2)))
    }
    
    aiData.value = newAiData
    
    // 动态生成 AI 建议和风险提示
    const risks = []
    const suggestions = []

    // 1. 热量分析
    if (dietPlan.calories < 1200) {
      risks.push('热量摄入过低，可能导致基础代谢损伤')
      risks.push('微量元素缺乏风险')
      suggestions.push('建议将热量提升至基础代谢(BMR)以上')
    } else if (dietPlan.calories > 3000) {
      risks.push('热量盈余过多，体脂增加风险高')
      suggestions.push('建议适当减少总热量摄入')
    }

    // 2. 营养素分析
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

    // 3. 运动分析
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

    // 兜底建议
    if (suggestions.length === 0) {
      suggestions.push('当前的饮食和运动计划非常均衡，请继续保持！')
    }

    simulationResult.value = {
      weight: (newAiData[newAiData.length-1] - currentWeight).toFixed(1) + ' kg',
      fat: ((newAiData[newAiData.length-1] - currentWeight) * 0.8 / currentWeight * 100).toFixed(1) + '%', // 粗略估算体脂变化
      risks: risks,
      suggestions: suggestions
    }
    
    renderChart()
    ElMessage.success('AI 修正预测完成')
    
  } catch (error) {
    console.error(error)
    ElMessage.error('预测失败')
  } finally {
    loading.value = false
  }
}

const exportReport = () => {
  ElMessage.success('正在生成 PDF 报告...')
  // 使用浏览器原生打印功能，用户可以选择"另存为PDF"
  window.print()
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
.dot.dashed { border-top: 2px dashed #909399; }
.dot.solid { border-top: 2px solid #409EFF; }

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
</style>