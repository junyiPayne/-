<template>
  <div class="statistics">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>预测报告</span>
          <el-select v-model="selectedWeeks" @change="loadStatistics" style="width: 150px">
            <el-option label="4周" :value="4" />
            <el-option label="8周" :value="8" />
            <el-option label="12周" :value="12" />
          </el-select>
        </div>
      </template>
      
      <el-row :gutter="20" v-if="statistics">
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-label">记录天数</div>
              <div class="stat-value">{{ statistics.total_logs || 0 }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-label">平均日摄入</div>
              <div class="stat-value">{{ Math.round(statistics.avg_daily_intake || 0) }} kcal</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-label">平均日消耗</div>
              <div class="stat-value">{{ Math.round(statistics.avg_daily_expenditure || 0) }} kcal</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-label">预测体重变化</div>
              <div class="stat-value" :style="getWeightChangeStyle(statistics.predicted_weight_change_kg)">
                {{ statistics.predicted_weight_change_kg || 0 }} kg
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-divider />
      
      <!-- 报告预览部分 -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>健康报告预览</span>
            <div>
              <el-button type="primary" @click="handlePreviewReport" :loading="previewLoading">
                预览报告
              </el-button>
              <el-button type="success" @click="handleSubmitReport" :loading="submitLoading">
                提交报告
              </el-button>
            </div>
          </div>
        </template>
        
        <div v-if="pdfUrl" style="width: 100%; height: 800px;">
          <iframe 
            :src="pdfUrl" 
            style="width: 100%; height: 100%; border: none;"
            frameborder="0"
          ></iframe>
        </div>
        <el-empty v-else description="点击预览报告按钮查看报告" />
      </el-card>
      
      <el-divider />
      
      <!-- AI分析 -->
      <el-card v-if="aiAssessment">
        <template #header>
          <span>AI健康分析</span>
        </template>
        <el-alert v-if="aiAssessment.risks && aiAssessment.risks.length > 0" type="warning" :closable="false">
          <template #title>
            <strong>健康风险：</strong>
            <ul>
              <li v-for="(risk, index) in aiAssessment.risks" :key="index">{{ risk }}</li>
            </ul>
          </template>
        </el-alert>
        <el-alert v-if="aiAssessment.suggestions && aiAssessment.suggestions.length > 0" type="success" :closable="false" style="margin-top: 10px">
          <template #title>
            <strong>建议：</strong>
            <ul>
              <li v-for="(suggestion, index) in aiAssessment.suggestions" :key="index">{{ suggestion }}</li>
            </ul>
          </template>
        </el-alert>
        <div style="margin-top: 10px">
          <el-button type="primary" @click="getAIAssessment" :loading="aiLoading">刷新AI分析</el-button>
        </div>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getStatistics } from '@/api/dailyLog'
import { getHealthAssessment } from '@/api/ai'
import { previewReport, submitReport } from '@/api/report'

const selectedWeeks = ref(4)
const statistics = ref(null)
const aiAssessment = ref(null)
const aiLoading = ref(false)
const previewLoading = ref(false)
const submitLoading = ref(false)
const pdfUrl = ref(null)

const loadStatistics = async () => {
  try {
    const response = await getStatistics({ weeks: selectedWeeks.value })
    statistics.value = response.data.data
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  }
}

const getAIAssessment = async () => {
  if (!statistics.value) {
    ElMessage.warning('请先加载统计数据')
    return
  }
  
  aiLoading.value = true
  try {
    const response = await getHealthAssessment({
      weeks: selectedWeeks.value,
      predicted_weight_change: statistics.value.predicted_weight_change_kg
    })
    aiAssessment.value = response.data.data
    ElMessage.success('AI分析完成')
  } catch (error) {
    ElMessage.error('AI分析失败')
  } finally {
    aiLoading.value = false
  }
}

const getWeightChangeStyle = (value) => {
  if (!value) return {}
  if (value > 0) {
    return { color: '#f56c6c' } // 红色表示增加
  } else {
    return { color: '#67c23a' } // 绿色表示减少
  }
}

// 预览报告
const handlePreviewReport = async () => {
  previewLoading.value = true
  try {
    const response = await previewReport()
    // 创建blob URL用于iframe显示
    const blob = new Blob([response.data], { type: 'application/pdf' })
    // 如果之前有URL，先释放
    if (pdfUrl.value) {
      URL.revokeObjectURL(pdfUrl.value)
    }
    pdfUrl.value = URL.createObjectURL(blob)
    ElMessage.success('报告预览加载成功')
  } catch (error) {
    ElMessage.error('预览报告失败')
    pdfUrl.value = null
  } finally {
    previewLoading.value = false
  }
}

// 提交报告
const handleSubmitReport = async () => {
  submitLoading.value = true
  try {
    await submitReport()
    ElMessage.success('报告提交成功')
    // 提交成功后刷新预览
    await handlePreviewReport()
  } catch (error) {
    // Error handled by interceptor
  } finally {
    submitLoading.value = false
  }
}

// 组件卸载时清理URL
onUnmounted(() => {
  if (pdfUrl.value) {
    URL.revokeObjectURL(pdfUrl.value)
  }
})

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.statistics {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}
</style>

