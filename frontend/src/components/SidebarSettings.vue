<template>
  <el-drawer
    v-model="visible"
    title="个性化设置"
    direction="rtl"
    size="400px"
    :before-close="handleClose"
  >
    <div class="settings-content">
      <el-form :model="form" label-width="120px" label-position="left">
        <!-- 字体大小 -->
        <el-form-item label="字体大小">
          <div style="display: flex; align-items: center; width: 100%;">
            <el-slider
              v-model="form.fontSize"
              :min="12"
              :max="20"
              :step="1"
              style="flex: 1; margin-right: 15px;"
              show-input
              :show-input-controls="false"
            />
            <span style="min-width: 50px; text-align: right;">{{ form.fontSize }}px</span>
          </div>
          <div style="margin-top: 10px; padding: 8px; background: #f5f7fa; border-radius: 4px;">
            <span :style="{ fontSize: form.fontSize + 'px' }">预览：这是字体大小预览效果</span>
          </div>
        </el-form-item>

        <el-divider />

        <!-- 字体样式 -->
        <el-form-item label="字体样式">
          <el-select v-model="form.fontFamily" style="width: 100%;" @change="handleFontFamilyChange">
            <el-option label="Arial" value="Arial, sans-serif" />
            <el-option label="微软雅黑" value="Microsoft YaHei, sans-serif" />
            <el-option label="宋体" value="SimSun, serif" />
            <el-option label="黑体" value="SimHei, sans-serif" />
            <el-option label="Times New Roman" value="Times New Roman, serif" />
            <el-option label="Courier New" value="Courier New, monospace" />
            <el-option label="Georgia" value="Georgia, serif" />
            <el-option label="Verdana" value="Verdana, sans-serif" />
            <el-option label="自定义字体" value="custom" />
          </el-select>
          <div style="margin-top: 10px; padding: 8px; background: #f5f7fa; border-radius: 4px;">
            <span :style="{ fontFamily: getDisplayFontFamily() }">预览：这是字体样式预览效果</span>
          </div>
        </el-form-item>

        <!-- 自定义字体上传 -->
        <el-form-item v-if="form.fontFamily === 'custom'" label="上传字体文件">
          <el-upload
            ref="fontUploadRef"
            :auto-upload="false"
            :on-change="handleFontFileChange"
            :file-list="fontFileList"
            accept=".ttf,.otf,.woff,.woff2"
            :limit="1"
          >
            <template #trigger>
              <el-button type="primary" size="small">选择字体文件</el-button>
            </template>
            <template #tip>
              <div style="color: #909399; font-size: 12px; margin-top: 5px;">
                支持格式：.ttf, .otf, .woff, .woff2
              </div>
            </template>
          </el-upload>
          <div v-if="form.customFontName" style="margin-top: 10px;">
            <el-input
              v-model="form.customFontName"
              placeholder="请输入字体名称"
              size="small"
              style="margin-bottom: 8px;"
            />
            <div style="padding: 8px; background: #f5f7fa; border-radius: 4px;">
              <span :style="{ fontFamily: getCustomFontPreview() }">
                预览：这是自定义字体预览效果
              </span>
            </div>
          </div>
        </el-form-item>

        <el-divider />

        <!-- 字体颜色 -->
        <el-form-item label="字体颜色">
          <div style="display: flex; align-items: center; gap: 15px;">
            <el-color-picker v-model="form.fontColor" size="small" />
            <el-input v-model="form.fontColor" size="small" style="width: 120px;" />
            <span :style="{ color: form.fontColor }">预览文字</span>
          </div>
        </el-form-item>

        <el-divider />

        <!-- Logo 大小 -->
        <el-form-item label="Logo 大小">
          <div style="display: flex; align-items: center; width: 100%;">
            <el-slider
              v-model="form.logoSize"
              :min="20"
              :max="80"
              :step="5"
              style="flex: 1; margin-right: 15px;"
              show-input
              :show-input-controls="false"
              @input="handleLogoSizeChange"
            />
            <span style="min-width: 50px; text-align: right;">{{ form.logoSize }}px</span>
          </div>
          <div style="margin-top: 10px; padding: 8px; background: #f5f7fa; border-radius: 4px; display: flex; align-items: center; gap: 8px;">
            <div style="width: 30px; height: 30px; border: 1px solid #dcdfe6; border-radius: 4px; display: flex; align-items: center; justify-content: center; background: #fff;">
              <span style="font-size: 15px;">📷</span>
            </div>
            <div :style="{ width: form.logoSize + 'px', height: form.logoSize + 'px', border: '1px solid #dcdfe6', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fff', transition: 'all 0.3s' }">
              <span :style="{ fontSize: (form.logoSize * 0.5) + 'px' }">📷</span>
            </div>
            <span style="color: #909399; font-size: 12px;">预览</span>
          </div>
        </el-form-item>

        <el-divider />

        <!-- 侧边栏颜色 -->
        <el-form-item label="侧边栏背景色">
          <div style="display: flex; align-items: center; gap: 15px;">
            <el-color-picker v-model="form.sidebarColor" size="small" />
            <el-input v-model="form.sidebarColor" size="small" style="width: 120px;" />
            <div
              :style="{
                width: '80px',
                height: '30px',
                backgroundColor: form.sidebarColor,
                border: '1px solid #dcdfe6',
                borderRadius: '4px'
              }"
            ></div>
          </div>
        </el-form-item>

        <el-divider />

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleSave" style="width: 100%;">保存设置</el-button>
          <el-button @click="handleReset" style="width: 100%; margin-top: 10px;">重置为默认</el-button>
        </el-form-item>
      </el-form>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const settingsStore = useSettingsStore()
const fontUploadRef = ref(null)
const fontFileList = ref([])

const visible = ref(props.modelValue)

watch(() => props.modelValue, (val) => {
  visible.value = val
})

watch(visible, (val) => {
  emit('update:modelValue', val)
  if (val) {
    // 打开时加载当前设置
    loadCurrentSettings()
  }
})

// 初始化字体样式
const getInitialFontFamily = () => {
  if (settingsStore.customFontName && settingsStore.customFontUrl) {
    return 'custom'
  }
  return settingsStore.fontFamily
}

// 表单数据
const form = reactive({
  fontSize: 14,
  fontFamily: 'Arial, sans-serif',
  fontColor: '#303133',
  sidebarColor: '#fff',
  logoSize: 40,
  customFontName: null,
  customFontUrl: null
})

// 加载当前设置
const loadCurrentSettings = () => {
  form.fontSize = settingsStore.fontSize
  form.fontFamily = getInitialFontFamily()
  form.fontColor = settingsStore.fontColor
  form.sidebarColor = settingsStore.sidebarColor
  form.logoSize = settingsStore.logoSize || 40
  form.customFontName = settingsStore.customFontName
  form.customFontUrl = settingsStore.customFontUrl
}

// 获取显示的字体样式
const getDisplayFontFamily = () => {
  if (form.fontFamily === 'custom' && form.customFontName) {
    return getCustomFontPreview()
  }
  return form.fontFamily
}

// 获取自定义字体预览样式
const getCustomFontPreview = () => {
  if (form.customFontName) {
    return `"${form.customFontName}", Arial, sans-serif`
  }
  return 'Arial, sans-serif'
}

// 处理字体文件上传
const handleFontFileChange = (file) => {
  if (!file || !file.raw) {
    ElMessage.error('文件读取失败')
    return
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const blob = new Blob([e.target.result], { type: file.raw.type || 'font/ttf' })
      const url = URL.createObjectURL(blob)
      
      form.customFontUrl = url
      
      if (!form.customFontName) {
        const fileName = file.name || file.raw.name || 'font'
        form.customFontName = fileName.substring(0, fileName.lastIndexOf('.')) || 'CustomFont'
      }
      
      settingsStore.customFontName = form.customFontName
      settingsStore.customFontUrl = form.customFontUrl
      settingsStore.loadCustomFont(form.customFontName, form.customFontUrl)
      
      ElMessage.success('字体文件加载成功')
    } catch (error) {
      console.error('字体文件处理失败:', error)
      ElMessage.error('字体文件处理失败，请重试')
    }
  }
  
  reader.onerror = () => {
    ElMessage.error('文件读取失败')
  }
  
  reader.readAsArrayBuffer(file.raw)
}

// 处理字体样式变化
const handleFontFamilyChange = (value) => {
  if (value !== 'custom') {
    form.customFontName = null
    form.customFontUrl = null
  }
}

// 处理 Logo 大小变化（实时更新）
const handleLogoSizeChange = (value) => {
  // 实时更新 store，让左上角 Logo 实时变化
  settingsStore.logoSize = value
  const root = document.documentElement
  root.style.setProperty('--user-logo-size', `${value}px`)
}

// 保存设置
const handleSave = () => {
  settingsStore.fontSize = form.fontSize
  settingsStore.fontColor = form.fontColor
  settingsStore.sidebarColor = form.sidebarColor
  settingsStore.logoSize = form.logoSize
  
  if (form.fontFamily === 'custom') {
    if (!form.customFontName || !form.customFontUrl) {
      ElMessage.warning('请先上传自定义字体文件')
      return
    }
    settingsStore.customFontName = form.customFontName
    settingsStore.customFontUrl = form.customFontUrl
    settingsStore.fontFamily = `"${form.customFontName}", Arial, sans-serif`
    settingsStore.loadCustomFont(form.customFontName, form.customFontUrl)
  } else {
    settingsStore.fontFamily = form.fontFamily
    settingsStore.customFontName = null
    settingsStore.customFontUrl = null
  }
  
  settingsStore.saveSettings()
  ElMessage.success('设置已保存并应用')
}

// 重置设置
const handleReset = () => {
  settingsStore.resetSettings()
  loadCurrentSettings()
  fontFileList.value = []
  ElMessage.success('已重置为默认设置')
}

// 关闭抽屉
const handleClose = () => {
  visible.value = false
}

// 初始化加载设置
loadCurrentSettings()
</script>

<style scoped>
.settings-content {
  padding: 10px 0;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  font-size: 14px;
}
</style>
