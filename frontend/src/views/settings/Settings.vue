<template>
  <div class="settings-container">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h2 style="margin: 0;">
            <el-icon style="margin-right: 8px;"><Setting /></el-icon>
            个性化设置
          </h2>
          <el-button size="small" @click="handleReset">重置为默认</el-button>
        </div>
      </template>

      <el-form :model="form" label-width="150px" label-position="left">
        <!-- 字体设置组 -->
        <el-card shadow="never" style="margin-bottom: 20px;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
              <span style="font-weight: 600; flex-shrink: 0;">字体设置</span>
              <div style="display: flex; gap: 10px; align-items: center; flex-shrink: 0;">
                <el-button type="primary" size="small" @click="saveFontSettings">保存</el-button>
                <el-button size="small" @click="resetFontSettings">重置</el-button>
              </div>
            </div>
          </template>
          
          <!-- 字体大小 -->
          <el-form-item label="字体大小">
            <div style="display: flex; align-items: center; width: 100%;">
              <el-slider
                v-model="form.fontSize"
                :min="12"
                :max="20"
                :step="1"
                style="flex: 1; margin-right: 20px;"
                show-input
                :show-input-controls="false"
                @input="applyPreview"
              />
              <span style="min-width: 60px; text-align: right;">{{ form.fontSize }}px</span>
            </div>
            <div style="margin-top: 10px; padding: 10px; background: #f5f7fa; border-radius: 4px;">
              <span :style="{ fontSize: form.fontSize + 'px' }">预览文字：这是字体大小预览效果</span>
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
            <div style="margin-top: 10px; padding: 10px; background: #f5f7fa; border-radius: 4px;">
              <span :style="{ fontFamily: getDisplayFontFamily() }">预览文字：这是字体样式预览效果</span>
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
                <el-button type="primary">选择字体文件</el-button>
              </template>
              <template #tip>
                <div style="color: #909399; font-size: 12px; margin-top: 8px;">
                  支持格式：.ttf, .otf, .woff, .woff2
                </div>
              </template>
            </el-upload>
            <div v-if="form.customFontName" style="margin-top: 10px;">
              <el-input
                v-model="form.customFontName"
                placeholder="请输入字体名称（如：MyCustomFont）"
                style="margin-bottom: 10px;"
                @input="applyPreview"
              />
              <div style="padding: 10px; background: #f5f7fa; border-radius: 4px;">
                <span :style="{ fontFamily: getCustomFontPreview() }">
                  预览文字：这是自定义字体预览效果
                </span>
              </div>
            </div>
          </el-form-item>

          <el-divider />

          <!-- 字体颜色 -->
          <el-form-item label="字体颜色">
            <div class="color-picker-row">
              <el-color-picker v-model="form.fontColor" @change="applyPreview" />
              <el-input v-model="form.fontColor" class="color-input" @input="applyPreview" />
              <span class="color-preview" :style="{ color: form.fontColor }">预览文字颜色</span>
            </div>
          </el-form-item>
        </el-card>

        <!-- 导航栏设置组 -->
        <el-card shadow="never" style="margin-bottom: 20px;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
              <span style="font-weight: 600; flex-shrink: 0;">导航栏设置</span>
              <div style="display: flex; gap: 10px; align-items: center; flex-shrink: 0;">
                <el-button type="primary" size="small" @click="saveHeaderSettings">保存</el-button>
                <el-button size="small" @click="resetHeaderSettings">重置</el-button>
              </div>
            </div>
          </template>
          
          <!-- 上方导航栏颜色 -->
          <el-form-item label="上方导航栏背景">
          <!-- 单色/渐变切换 -->
          <div style="margin-bottom: 15px;">
            <el-radio-group v-model="form.headerUseGradient" @change="applyPreview">
              <el-radio-button :label="false">单色</el-radio-button>
              <el-radio-button :label="true">渐变</el-radio-button>
            </el-radio-group>
          </div>

          <!-- 单色模式 -->
          <div v-if="!form.headerUseGradient" class="color-picker-row">
            <el-color-picker v-model="form.headerColor" @change="applyPreview" />
            <el-input v-model="form.headerColor" class="color-input" @input="applyPreview" />
            <div class="color-preview-box" :style="{ backgroundColor: form.headerColor }"></div>
          </div>

          <!-- 渐变模式 -->
          <div v-else>
            <!-- 渐变类型 -->
            <div style="margin-bottom: 15px;">
              <el-radio-group v-model="form.headerGradientType" @change="applyPreview">
                <el-radio-button label="linear">线性渐变</el-radio-button>
                <el-radio-button label="radial">径向渐变</el-radio-button>
              </el-radio-group>
            </div>

            <!-- 渐变颜色 -->
            <div class="gradient-colors-row">
              <div class="gradient-color-item">
                <span class="gradient-color-label">颜色1：</span>
                <el-color-picker v-model="form.headerGradientColor1" @change="applyPreview" />
                <el-input v-model="form.headerGradientColor1" class="color-input-small" @input="applyPreview" />
              </div>
              <div class="gradient-color-item">
                <span class="gradient-color-label">颜色2：</span>
                <el-color-picker v-model="form.headerGradientColor2" @change="applyPreview" />
                <el-input v-model="form.headerGradientColor2" class="color-input-small" @input="applyPreview" />
              </div>
            </div>

            <!-- 渐变方向（仅线性渐变） -->
            <div v-if="form.headerGradientType === 'linear'" class="gradient-direction-row">
              <span class="gradient-direction-label">渐变方向：</span>
              <el-select v-model="form.headerGradientDirection" @change="applyPreview" class="gradient-direction-select">
                <el-option label="向右" value="to right" />
                <el-option label="向左" value="to left" />
                <el-option label="向下" value="to bottom" />
                <el-option label="向上" value="to top" />
                <el-option label="向右下" value="to bottom right" />
                <el-option label="向右上" value="to top right" />
                <el-option label="向左下" value="to bottom left" />
                <el-option label="向左上" value="to top left" />
              </el-select>
            </div>

            <!-- 预览 -->
            <div style="margin-top: 15px;">
              <div
                :style="{
                  width: '100%',
                  height: '60px',
                  background: getGradientPreview(),
                  border: '1px solid #dcdfe6',
                  borderRadius: '4px'
                }"
              ></div>
            </div>
          </div>
          </el-form-item>
        </el-card>

        <el-divider />

        <!-- 侧边栏设置组 -->
        <el-card shadow="never" style="margin-bottom: 20px;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: 600;">侧边栏设置</span>
              <div style="display: flex; gap: 10px; align-items: center;">
                <el-button type="primary" size="small" @click="saveSidebarSettings">保存</el-button>
                <el-button size="small" @click="resetSidebarSettings">重置</el-button>
              </div>
            </div>
          </template>
          
          <!-- 左侧侧边栏背景 -->
          <el-form-item label="左侧侧边栏背景">
            <!-- 单色/渐变切换 -->
            <div style="margin-bottom: 15px;">
              <el-radio-group v-model="form.sidebarUseGradient" @change="applyPreview">
                <el-radio-button :label="false">单色</el-radio-button>
                <el-radio-button :label="true">渐变</el-radio-button>
              </el-radio-group>
            </div>

            <!-- 单色模式 -->
            <div v-if="!form.sidebarUseGradient" class="color-picker-row">
              <el-color-picker v-model="form.sidebarColor" @change="applyPreview" />
              <el-input v-model="form.sidebarColor" class="color-input" @input="applyPreview" />
              <div class="color-preview-box" :style="{ backgroundColor: form.sidebarColor }"></div>
            </div>

            <!-- 渐变模式 -->
            <div v-else>
              <!-- 渐变类型 -->
              <div style="margin-bottom: 15px;">
                <el-radio-group v-model="form.sidebarGradientType" @change="applyPreview">
                  <el-radio-button label="linear">线性渐变</el-radio-button>
                  <el-radio-button label="radial">径向渐变</el-radio-button>
                </el-radio-group>
              </div>

              <!-- 渐变颜色 -->
              <div class="gradient-colors-row">
                <div class="gradient-color-item">
                  <span class="gradient-color-label">颜色1：</span>
                  <el-color-picker v-model="form.sidebarGradientColor1" @change="applyPreview" />
                  <el-input v-model="form.sidebarGradientColor1" class="color-input-small" @input="applyPreview" />
                </div>
                <div class="gradient-color-item">
                  <span class="gradient-color-label">颜色2：</span>
                  <el-color-picker v-model="form.sidebarGradientColor2" @change="applyPreview" />
                  <el-input v-model="form.sidebarGradientColor2" class="color-input-small" @input="applyPreview" />
                </div>
              </div>

              <!-- 渐变方向（仅线性渐变） -->
              <div v-if="form.sidebarGradientType === 'linear'" class="gradient-direction-row">
                <span class="gradient-direction-label">渐变方向：</span>
                <el-select v-model="form.sidebarGradientDirection" @change="applyPreview" class="gradient-direction-select">
                  <el-option label="向下" value="to bottom" />
                  <el-option label="向上" value="to top" />
                  <el-option label="向右" value="to right" />
                  <el-option label="向左" value="to left" />
                  <el-option label="向右下" value="to bottom right" />
                  <el-option label="向右上" value="to top right" />
                  <el-option label="向左下" value="to bottom left" />
                  <el-option label="向左上" value="to top left" />
                </el-select>
              </div>

              <!-- 预览 -->
              <div style="margin-top: 15px;">
                <div
                  :style="{
                    width: '100%',
                    height: '60px',
                    background: getSidebarGradientPreview(),
                    border: '1px solid #dcdfe6',
                    borderRadius: '4px'
                  }"
                ></div>
              </div>
            </div>
          </el-form-item>
        </el-card>

        <el-divider />

        <!-- 内容区域设置组 -->
        <el-card shadow="never" style="margin-bottom: 20px;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
              <span style="font-weight: 600; flex-shrink: 0;">内容区域设置</span>
              <div style="display: flex; gap: 10px; align-items: center; flex-shrink: 0;">
                <el-button type="primary" size="small" @click="saveContentSettings">保存</el-button>
                <el-button size="small" @click="resetContentSettings">重置</el-button>
              </div>
            </div>
          </template>
          
          <!-- 中间内容区域背景色 -->
          <el-form-item label="中间内容区域背景色">
            <div class="color-picker-row">
              <el-color-picker v-model="form.contentBackgroundColor" @change="applyPreview" />
              <el-input v-model="form.contentBackgroundColor" class="color-input" @input="applyPreview" />
              <div class="color-preview-box" :style="{ backgroundColor: form.contentBackgroundColor }"></div>
            </div>
          </el-form-item>

          <el-divider />

          <!-- 背景图片 -->
          <el-form-item label="页面背景图片">
          <div style="margin-bottom: 15px;">
            <el-upload
              ref="backgroundUploadRef"
              :auto-upload="false"
              :on-change="handleBackgroundImageChange"
              :file-list="backgroundImageFileList"
              accept="image/*"
              :limit="1"
            >
              <template #trigger>
                <el-button type="primary">选择背景图片</el-button>
              </template>
              <template #tip>
                <div style="color: #909399; font-size: 12px; margin-top: 8px;">
                  支持格式：jpg, png, webp 等。背景图片将覆盖整个页面（导航栏除外）
                </div>
              </template>
            </el-upload>
          </div>
          
          <!-- 当前背景图片预览 -->
          <div v-if="form.backgroundImageUrl" style="margin-top: 15px;">
            <div style="margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
              <span>当前背景图片：</span>
              <el-button size="small" type="danger" @click="handleRemoveBackgroundImage">删除背景图片</el-button>
            </div>
            
            <!-- 背景图片不透明度调整 -->
            <el-form-item label="背景不透明度" class="opacity-form-item">
              <div class="opacity-control-row">
                <el-input-number
                  v-model="form.backgroundImageOpacity"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  :precision="1"
                  class="opacity-input"
                  @change="applyPreview"
                />
                <span class="opacity-hint">范围：0.0 - 1.0（0% - 100%）</span>
              </div>
            </el-form-item>
            
            <div
              :style="{
                width: '100%',
                height: '200px',
                backgroundImage: `url(${form.backgroundImageUrl})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                backgroundRepeat: 'no-repeat',
                border: '1px solid #dcdfe6',
                borderRadius: '4px',
                opacity: form.backgroundImageOpacity,
                position: 'relative'
              }"
            >
              <div style="position: absolute; bottom: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px;">
                不透明度: {{ (form.backgroundImageOpacity * 100).toFixed(0) }}%
              </div>
            </div>
          </div>
          
          <!-- 上传预览 -->
          <div v-if="backgroundImagePreview" style="margin-top: 15px;">
            <div style="margin-bottom: 10px;">
              <span>预览：</span>
            </div>
            
            <!-- 预览时不透明度调整 -->
            <el-form-item label="背景不透明度" class="opacity-form-item">
              <div class="opacity-control-row">
                <el-input-number
                  v-model="form.backgroundImageOpacity"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  :precision="1"
                  class="opacity-input"
                  @change="applyPreview"
                />
                <span class="opacity-hint">范围：0.0 - 1.0（0% - 100%）</span>
              </div>
            </el-form-item>
            
            <div
              :style="{
                width: '100%',
                height: '200px',
                backgroundImage: `url(${backgroundImagePreview})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                backgroundRepeat: 'no-repeat',
                border: '1px solid #dcdfe6',
                borderRadius: '4px',
                opacity: form.backgroundImageOpacity,
                position: 'relative'
              }"
            >
              <div style="position: absolute; bottom: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px;">
                不透明度: {{ (form.backgroundImageOpacity * 100).toFixed(0) }}%
              </div>
            </div>
            <div style="margin-top: 15px; display: flex; gap: 10px;">
              <el-button type="primary" @click="handleUploadBackgroundImage" :loading="backgroundImageUploading">上传并应用</el-button>
              <el-button @click="handleCancelBackgroundImage">取消</el-button>
            </div>
          </div>
          </el-form-item>
        </el-card>

        <el-divider />

        <!-- Logo 设置组 -->
        <el-card shadow="never" style="margin-bottom: 20px;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
              <span style="font-weight: 600; flex-shrink: 0;">Logo 设置</span>
              <div style="display: flex; gap: 10px; align-items: center; flex-shrink: 0;">
                <el-button type="primary" size="small" @click="saveLogoSettings">保存</el-button>
                <el-button size="small" @click="resetLogoSettings">重置</el-button>
              </div>
            </div>
          </template>
          
          <!-- Logo 大小 -->
          <el-form-item label="Logo 大小">
          <div style="display: flex; align-items: center; width: 100%;">
            <el-slider
              v-model="form.logoSize"
              :min="20"
              :max="80"
              :step="5"
              style="flex: 1; margin-right: 20px;"
              show-input
              :show-input-controls="false"
              @input="applyPreview"
            />
            <span style="min-width: 60px; text-align: right;">{{ form.logoSize }}px</span>
          </div>
          <div style="margin-top: 10px; padding: 10px; background: #f5f7fa; border-radius: 4px; display: flex; align-items: center; gap: 10px;">
            <div style="width: 40px; height: 40px; border: 1px solid #dcdfe6; border-radius: 4px; display: flex; align-items: center; justify-content: center; background: #fff;">
              <span style="font-size: 20px;">📷</span>
            </div>
            <div style="width: var(--user-logo-size, 40px); height: var(--user-logo-size, 40px); border: 1px solid #dcdfe6; border-radius: 4px; display: flex; align-items: center; justify-content: center; background: #fff; transition: all 0.3s;">
              <span :style="{ fontSize: (form.logoSize * 0.5) + 'px' }">📷</span>
            </div>
            <span style="color: #909399; font-size: 12px;">预览：Logo 大小效果</span>
          </div>
          </el-form-item>
        </el-card>

        <el-divider />

        <!-- 整体操作按钮 -->
        <el-form-item>
          <div style="display: flex; justify-content: center; gap: 15px; padding: 30px 0;">
            <el-button type="primary" size="large" @click="handleSaveAll">保存所有设置</el-button>
            <el-button size="large" @click="handleReset">重置为默认</el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { ElMessage } from 'element-plus'
import { Setting } from '@element-plus/icons-vue'
import { uploadBackgroundImage, getBackgroundImageUrl } from '@/api/settings'

const settingsStore = useSettingsStore()

// 默认设置（与 store 中的保持一致）
const defaultSettings = {
  fontSize: 14,
  fontFamily: 'Arial, sans-serif',
  fontColor: '#303133',
  headerColor: '#304156',
  headerUseGradient: false,
  headerGradientType: 'linear',
  headerGradientColor1: '#304156',
  headerGradientColor2: '#409EFF',
  headerGradientDirection: 'to right',
  sidebarColor: '#fff',
  contentBackgroundColor: '#f0f2f5',
  logoSize: 40,
  backgroundImageUrl: null,
  backgroundImageOpacity: 1.0
}
const fontUploadRef = ref(null)
const fontFileList = ref([])
const backgroundUploadRef = ref(null)
const backgroundImageFileList = ref([])
const backgroundImagePreview = ref(null)
const backgroundImageUploading = ref(false)
const pendingBackgroundFile = ref(null)

// 初始化字体样式
const getInitialFontFamily = () => {
  if (settingsStore.customFontName && settingsStore.customFontUrl) {
    return 'custom'
  }
  return settingsStore.fontFamily
}

// 表单数据
const form = reactive({
  fontSize: settingsStore.fontSize,
  fontFamily: getInitialFontFamily(),
  fontColor: settingsStore.fontColor,
  headerColor: settingsStore.headerColor,
  headerUseGradient: settingsStore.headerUseGradient || false,
  headerGradientType: settingsStore.headerGradientType || 'linear',
  headerGradientColor1: settingsStore.headerGradientColor1 || '#304156',
  headerGradientColor2: settingsStore.headerGradientColor2 || '#409EFF',
  headerGradientDirection: settingsStore.headerGradientDirection || 'to right',
  sidebarColor: settingsStore.sidebarColor,
  sidebarUseGradient: settingsStore.sidebarUseGradient || false,
  sidebarGradientType: settingsStore.sidebarGradientType || 'linear',
  sidebarGradientColor1: settingsStore.sidebarGradientColor1 || '#fff',
  sidebarGradientColor2: settingsStore.sidebarGradientColor2 || '#f0f2f5',
  sidebarGradientDirection: settingsStore.sidebarGradientDirection || 'to bottom',
  contentBackgroundColor: settingsStore.contentBackgroundColor,
  customFontName: settingsStore.customFontName,
  customFontUrl: settingsStore.customFontUrl,
  logoSize: settingsStore.logoSize || 40,
  backgroundImageUrl: settingsStore.backgroundImageUrl || null,
  backgroundImageOpacity: settingsStore.backgroundImageOpacity !== undefined ? settingsStore.backgroundImageOpacity : 1.0
})

// 获取导航栏渐变预览样式
const getGradientPreview = () => {
  if (form.headerGradientType === 'linear') {
    return `linear-gradient(${form.headerGradientDirection}, ${form.headerGradientColor1}, ${form.headerGradientColor2})`
  } else {
    return `radial-gradient(circle, ${form.headerGradientColor1}, ${form.headerGradientColor2})`
  }
}

// 获取侧边栏渐变预览样式
const getSidebarGradientPreview = () => {
  if (form.sidebarGradientType === 'linear') {
    return `linear-gradient(${form.sidebarGradientDirection}, ${form.sidebarGradientColor1}, ${form.sidebarGradientColor2})`
  } else {
    return `radial-gradient(circle, ${form.sidebarGradientColor1}, ${form.sidebarGradientColor2})`
  }
}

// 处理背景图片选择
const handleBackgroundImageChange = (file) => {
  if (!file || !file.raw) {
    ElMessage.error('文件读取失败')
    return
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    backgroundImagePreview.value = e.target.result
    pendingBackgroundFile.value = file.raw
  }
  reader.onerror = () => {
    ElMessage.error('文件读取失败')
  }
  reader.readAsDataURL(file.raw)
}

// 上传背景图片
const handleUploadBackgroundImage = async () => {
  if (!pendingBackgroundFile.value) {
    ElMessage.warning('请先选择背景图片')
    return
  }
  
  // 检查文件大小（限制为 10MB）
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (pendingBackgroundFile.value.size > maxSize) {
    ElMessage.error('图片文件大小不能超过 10MB')
    return
  }
  
  // 检查文件类型
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif']
  if (!allowedTypes.includes(pendingBackgroundFile.value.type)) {
    ElMessage.error('不支持的图片格式，请选择 jpg、png、webp 或 gif 格式')
    return
  }
  
  backgroundImageUploading.value = true
  try {
    const res = await uploadBackgroundImage(pendingBackgroundFile.value)
    // 检查响应结构 - 响应拦截器已经处理了非200的情况
    if (res && res.data && res.data.code === 200) {
      const data = res.data.data
      if (data && data.url) {
        // 更新表单和store
        form.backgroundImageUrl = data.url
        settingsStore.backgroundImageUrl = data.url
        settingsStore.backgroundImageOpacity = form.backgroundImageOpacity !== undefined ? form.backgroundImageOpacity : 1.0
        settingsStore.saveSettings()
        
        // 清除预览和待上传文件
        backgroundImagePreview.value = null
        pendingBackgroundFile.value = null
        backgroundImageFileList.value = []
        
        // 清除上传组件的文件列表
        if (backgroundUploadRef.value) {
          backgroundUploadRef.value.clearFiles()
        }
        
        ElMessage.success('背景图片上传成功')
        // 延迟一下再应用预览，确保文件已完全保存
        setTimeout(() => {
          applyPreview()
        }, 500)
      } else {
        ElMessage.error('上传成功但未返回图片URL')
      }
    }
  } catch (error) {
    // 错误已经被响应拦截器处理，这里只记录日志
    console.error('背景图片上传失败:', error)
    console.error('错误详情:', {
      message: error.message,
      response: error.response,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      config: error.config
    })
    // 如果响应拦截器没有处理（比如网络错误），显示通用错误
    if (!error.response) {
      ElMessage.error('网络错误，请检查网络连接')
    } else if (error.response.status === 404) {
      // 404错误说明路由不存在，可能是：
      // 1. 后端服务未启动
      // 2. 路由未正确注册
      // 3. 权限问题（但应该是403）
      console.error('404错误 - 可能的原因:', {
        url: error.config?.url,
        method: error.config?.method,
        baseURL: error.config?.baseURL
      })
    }
  } finally {
    backgroundImageUploading.value = false
  }
}

// 取消背景图片上传
const handleCancelBackgroundImage = () => {
  backgroundImagePreview.value = null
  pendingBackgroundFile.value = null
  backgroundImageFileList.value = []
  if (backgroundUploadRef.value) {
    backgroundUploadRef.value.clearFiles()
  }
}

// 删除背景图片
const handleRemoveBackgroundImage = () => {
  form.backgroundImageUrl = null
  form.backgroundImageOpacity = 1.0
  settingsStore.backgroundImageUrl = null
  settingsStore.backgroundImageOpacity = 1.0
  settingsStore.saveSettings()
  ElMessage.success('背景图片已删除')
  applyPreview()
}

// 加载背景图片（从用户设置中加载）
const loadBackgroundImage = async () => {
  try {
    const res = await getBackgroundImageUrl()
    // 如果返回成功但没有 url，说明没有设置背景图片，这是正常的，不应该报错
    if (res.data && res.data.code === 200 && res.data.data) {
      const settings = res.data.data
      if (settings.backgroundImageUrl) {
        form.backgroundImageUrl = settings.backgroundImageUrl
        form.backgroundImageOpacity = settings.backgroundImageOpacity !== undefined ? settings.backgroundImageOpacity : 1.0
        settingsStore.backgroundImageUrl = settings.backgroundImageUrl
        settingsStore.backgroundImageOpacity = settings.backgroundImageOpacity
      } else {
        // 没有背景图片是正常情况，不设置即可
        form.backgroundImageUrl = null
      }
    }
  } catch (error) {
    // 只在真正的错误时记录，404 或其他错误不应该影响页面
    if (error.response && error.response.status !== 404) {
      console.error('加载背景图片失败:', error)
      // 不显示错误消息，因为可能是正常的（没有设置背景图片）
    }
  }
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

// 实时预览（不保存到store，只应用到页面）
const applyPreview = () => {
  const root = document.documentElement
  
  // 应用字体大小
  root.style.setProperty('--user-font-size', `${form.fontSize}px`)
  
  // 应用字体样式
  let finalFontFamily = form.fontFamily
  if (form.fontFamily === 'custom' && form.customFontName && form.customFontUrl) {
    finalFontFamily = `"${form.customFontName}", Arial, sans-serif`
    // 加载自定义字体
    if (!document.getElementById(`custom-font-${form.customFontName}`)) {
      const style = document.createElement('style')
      style.id = `custom-font-${form.customFontName}`
      style.textContent = `
        @font-face {
          font-family: "${form.customFontName}";
          src: url("${form.customFontUrl}") format("truetype");
        }
      `
      document.head.appendChild(style)
    }
  }
  root.style.setProperty('--user-font-family', finalFontFamily)
  
  // 应用字体颜色
  root.style.setProperty('--user-font-color', form.fontColor)
  
  // 应用上方导航栏颜色（强制覆盖）
  root.style.setProperty('--user-header-color', form.headerColor)
  
  // 应用导航栏背景（单色或渐变）
  if (form.headerUseGradient) {
    const gradientBg = getGradientPreview()
    root.style.setProperty('--user-header-background', gradientBg)
    root.style.setProperty('--user-header-color', form.headerColor) // 保持颜色值更新
    const header = document.querySelector('.header')
    if (header) {
      header.style.setProperty('background', gradientBg, 'important')
      header.style.setProperty('background-color', 'transparent', 'important')
      header.style.removeProperty('background-image')
    }
    const elHeader = document.querySelector('.el-header')
    if (elHeader) {
      elHeader.style.setProperty('background', gradientBg, 'important')
      elHeader.style.setProperty('background-color', 'transparent', 'important')
      elHeader.style.removeProperty('background-image')
    }
  } else {
    // 单色模式：清除渐变背景，使用纯色
    root.style.setProperty('--user-header-background', form.headerColor)
    root.style.setProperty('--user-header-color', form.headerColor)
    const header = document.querySelector('.header')
    if (header) {
      header.style.setProperty('background-color', form.headerColor, 'important')
      header.style.setProperty('background', form.headerColor, 'important')
      header.style.removeProperty('background-image')
    }
    const elHeader = document.querySelector('.el-header')
    if (elHeader) {
      elHeader.style.setProperty('background-color', form.headerColor, 'important')
      elHeader.style.setProperty('background', form.headerColor, 'important')
      elHeader.style.removeProperty('background-image')
    }
  }
  
  // 应用左侧侧边栏颜色（单色或渐变）
  if (form.sidebarUseGradient) {
    const sidebarBg = getSidebarGradientPreview()
    root.style.setProperty('--user-sidebar-background', sidebarBg)
    root.style.setProperty('--user-sidebar-color', form.sidebarColor)
    
    setTimeout(() => {
      const allSidebarElements = document.querySelectorAll('.el-aside, .sidebar, .sidebar-menu, .el-aside .el-menu')
      allSidebarElements.forEach(el => {
        el.style.setProperty('background', sidebarBg, 'important')
        el.style.setProperty('background-color', 'transparent', 'important')
      })
    }, 0)
  } else {
    root.style.setProperty('--user-sidebar-background', form.sidebarColor)
    root.style.setProperty('--user-sidebar-color', form.sidebarColor)
    
    setTimeout(() => {
      const allSidebarElements = document.querySelectorAll('.el-aside, .sidebar, .sidebar-menu, .el-aside .el-menu')
      allSidebarElements.forEach(el => {
        el.style.setProperty('background-color', form.sidebarColor, 'important')
        el.style.setProperty('background', form.sidebarColor, 'important')
      })
    }, 0)
  }
  
  // 应用中间内容区域背景色
  root.style.setProperty('--user-content-bg-color', form.contentBackgroundColor)
  
  // 应用 Logo 大小（实时预览，让左上角 Logo 实时变化）
  root.style.setProperty('--user-logo-size', `${form.logoSize}px`)
  // 实时更新 store 中的 logoSize 以便 MainLayout 中的 computed 能响应
  settingsStore.logoSize = form.logoSize
  
  // 应用背景图片和不透明度
  const bgStyle = document.getElementById('background-image-style')
  if (bgStyle) {
    bgStyle.remove()
  }
  
  if (form.backgroundImageUrl) {
    const opacity = form.backgroundImageOpacity !== undefined ? form.backgroundImageOpacity : 1.0
    root.style.setProperty('--user-background-image', `url(${form.backgroundImageUrl})`)
    root.style.setProperty('--user-background-opacity', opacity.toString())
    
    // 使用伪元素实现不透明度
    const style = document.createElement('style')
    style.id = 'background-image-style'
    style.textContent = `
      body::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url(${form.backgroundImageUrl});
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        opacity: ${opacity};
        z-index: -1;
        pointer-events: none;
      }
    `
    document.head.appendChild(style)
    settingsStore.backgroundImageOpacity = opacity
  } else {
    root.style.setProperty('--user-background-image', 'none')
    document.body.style.setProperty('background-image', 'none', 'important')
  }
  
  // 使用 setTimeout 确保 DOM 已渲染
  setTimeout(() => {
    const allSidebarElements = document.querySelectorAll('.el-aside, .sidebar, .sidebar-menu, .el-aside .el-menu')
    allSidebarElements.forEach(el => {
      el.style.setProperty('background-color', form.sidebarColor, 'important')
    })
    
    // 应用到中间内容区域
    const mainContent = document.querySelector('.main-content')
    if (mainContent) {
      mainContent.style.setProperty('background-color', form.contentBackgroundColor, 'important')
    }
    const elMain = document.querySelector('.el-main')
    if (elMain) {
      elMain.style.setProperty('background-color', form.contentBackgroundColor, 'important')
    }
  }, 0)
}

// 监听表单变化，实时预览
watch(() => form.fontFamily, () => {
  applyPreview()
})

watch(() => form.fontColor, () => {
  applyPreview()
})

watch(() => form.headerColor, () => {
  applyPreview()
})

watch(() => form.headerUseGradient, () => {
  applyPreview()
})

watch(() => form.headerGradientType, () => {
  applyPreview()
})

watch(() => form.headerGradientColor1, () => {
  applyPreview()
})

watch(() => form.headerGradientColor2, () => {
  applyPreview()
})

watch(() => form.headerGradientDirection, () => {
  applyPreview()
})

watch(() => form.sidebarColor, () => {
  applyPreview()
})

watch(() => form.sidebarUseGradient, () => {
  applyPreview()
})

watch(() => form.sidebarGradientType, () => {
  applyPreview()
})

watch(() => form.sidebarGradientColor1, () => {
  applyPreview()
})

watch(() => form.sidebarGradientColor2, () => {
  applyPreview()
})

watch(() => form.sidebarGradientDirection, () => {
  applyPreview()
})

watch(() => form.contentBackgroundColor, () => {
  applyPreview()
})

watch(() => form.logoSize, () => {
  applyPreview()
})

watch(() => form.backgroundImageUrl, () => {
  applyPreview()
})

watch(() => form.backgroundImageOpacity, () => {
  applyPreview()
})

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
      
      applyPreview()
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
  applyPreview()
}

// 保存字体设置
const saveFontSettings = () => {
  settingsStore.fontSize = form.fontSize
  settingsStore.fontColor = form.fontColor
  
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
  ElMessage.success('字体设置已保存')
}

// 保存导航栏设置
const saveHeaderSettings = () => {
  settingsStore.headerColor = form.headerColor
  settingsStore.headerUseGradient = form.headerUseGradient
  settingsStore.headerGradientType = form.headerGradientType
  settingsStore.headerGradientColor1 = form.headerGradientColor1
  settingsStore.headerGradientColor2 = form.headerGradientColor2
  settingsStore.headerGradientDirection = form.headerGradientDirection
  settingsStore.saveSettings()
  // 确保立即应用设置
  applyPreview()
  ElMessage.success('导航栏设置已保存')
}

// 保存侧边栏设置
const saveSidebarSettings = () => {
  settingsStore.sidebarColor = form.sidebarColor
  settingsStore.sidebarUseGradient = form.sidebarUseGradient
  settingsStore.sidebarGradientType = form.sidebarGradientType
  settingsStore.sidebarGradientColor1 = form.sidebarGradientColor1
  settingsStore.sidebarGradientColor2 = form.sidebarGradientColor2
  settingsStore.sidebarGradientDirection = form.sidebarGradientDirection
  settingsStore.saveSettings()
  ElMessage.success('侧边栏设置已保存')
}

// 保存内容区域设置
const saveContentSettings = () => {
  settingsStore.contentBackgroundColor = form.contentBackgroundColor
  settingsStore.backgroundImageUrl = form.backgroundImageUrl
  settingsStore.backgroundImageOpacity = form.backgroundImageOpacity
  settingsStore.saveSettings()
  ElMessage.success('内容区域设置已保存')
}

// 保存 Logo 设置
const saveLogoSettings = () => {
  settingsStore.logoSize = form.logoSize
  settingsStore.saveSettings()
  ElMessage.success('Logo 设置已保存')
}

// 重置字体设置
const resetFontSettings = () => {
  form.fontSize = defaultSettings.fontSize
  form.fontFamily = defaultSettings.fontFamily
  form.fontColor = defaultSettings.fontColor
  form.customFontName = null
  form.customFontUrl = null
  fontFileList.value = []
  applyPreview()
  ElMessage.success('字体设置已重置')
}

// 重置导航栏设置
const resetHeaderSettings = () => {
  form.headerColor = defaultSettings.headerColor
  form.headerUseGradient = defaultSettings.headerUseGradient
  form.headerGradientType = defaultSettings.headerGradientType
  form.headerGradientColor1 = defaultSettings.headerGradientColor1
  form.headerGradientColor2 = defaultSettings.headerGradientColor2
  form.headerGradientDirection = defaultSettings.headerGradientDirection
  applyPreview()
  ElMessage.success('导航栏设置已重置')
}

// 重置侧边栏设置
const resetSidebarSettings = () => {
  form.sidebarColor = defaultSettings.sidebarColor
  form.sidebarUseGradient = defaultSettings.sidebarUseGradient
  form.sidebarGradientType = defaultSettings.sidebarGradientType
  form.sidebarGradientColor1 = defaultSettings.sidebarGradientColor1
  form.sidebarGradientColor2 = defaultSettings.sidebarGradientColor2
  form.sidebarGradientDirection = defaultSettings.sidebarGradientDirection
  applyPreview()
  ElMessage.success('侧边栏设置已重置')
}

// 重置内容区域设置
const resetContentSettings = () => {
  form.contentBackgroundColor = defaultSettings.contentBackgroundColor
  form.backgroundImageUrl = defaultSettings.backgroundImageUrl
  form.backgroundImageOpacity = defaultSettings.backgroundImageOpacity
  backgroundImageFileList.value = []
  backgroundImagePreview.value = null
  pendingBackgroundFile.value = null
  applyPreview()
  ElMessage.success('内容区域设置已重置')
}

// 重置 Logo 设置
const resetLogoSettings = () => {
  form.logoSize = defaultSettings.logoSize
  applyPreview()
  ElMessage.success('Logo 设置已重置')
}

// 保存所有设置
const handleSaveAll = () => {
  settingsStore.fontSize = form.fontSize
  settingsStore.fontColor = form.fontColor
  settingsStore.headerColor = form.headerColor
  settingsStore.headerUseGradient = form.headerUseGradient
  settingsStore.headerGradientType = form.headerGradientType
  settingsStore.headerGradientColor1 = form.headerGradientColor1
  settingsStore.headerGradientColor2 = form.headerGradientColor2
  settingsStore.headerGradientDirection = form.headerGradientDirection
  settingsStore.sidebarColor = form.sidebarColor
  settingsStore.sidebarUseGradient = form.sidebarUseGradient
  settingsStore.sidebarGradientType = form.sidebarGradientType
  settingsStore.sidebarGradientColor1 = form.sidebarGradientColor1
  settingsStore.sidebarGradientColor2 = form.sidebarGradientColor2
  settingsStore.sidebarGradientDirection = form.sidebarGradientDirection
  settingsStore.contentBackgroundColor = form.contentBackgroundColor
  settingsStore.logoSize = form.logoSize
  settingsStore.backgroundImageUrl = form.backgroundImageUrl
  settingsStore.backgroundImageOpacity = form.backgroundImageOpacity
  
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
  ElMessage.success('所有设置已保存')
}

// 重置设置
const handleReset = () => {
  settingsStore.resetSettings()
  form.fontSize = settingsStore.fontSize
  form.fontFamily = getInitialFontFamily()
  form.fontColor = settingsStore.fontColor
  form.headerColor = settingsStore.headerColor
  form.headerUseGradient = settingsStore.headerUseGradient || false
  form.headerGradientType = settingsStore.headerGradientType || 'linear'
  form.headerGradientColor1 = settingsStore.headerGradientColor1 || '#304156'
  form.headerGradientColor2 = settingsStore.headerGradientColor2 || '#409EFF'
  form.headerGradientDirection = settingsStore.headerGradientDirection || 'to right'
  form.sidebarColor = settingsStore.sidebarColor
  form.contentBackgroundColor = settingsStore.contentBackgroundColor
  form.logoSize = defaultSettings.logoSize
  form.backgroundImageUrl = defaultSettings.backgroundImageUrl
  form.backgroundImageOpacity = defaultSettings.backgroundImageOpacity
  form.customFontName = defaultSettings.customFontName
  form.customFontUrl = defaultSettings.customFontUrl
  fontFileList.value = []
  backgroundImageFileList.value = []
  backgroundImagePreview.value = null
  pendingBackgroundFile.value = null
  applyPreview()
  ElMessage.success('已重置为默认设置')
}

onMounted(async () => {
  // 从服务器加载用户设置
  await settingsStore.loadSettingsFromServer()
  // 加载背景图片
  await loadBackgroundImage()
  // 初始化时应用当前设置
  applyPreview()
})
</script>

<style scoped>
.settings-container {
  max-width: 900px;
  margin: 0 auto;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  width: 150px !important;
  text-align: right;
  padding-right: 20px;
}

/* 颜色选择器行 - 统一对齐 */
.color-picker-row {
  display: flex;
  align-items: center;
  gap: 15px;
}

.color-picker-row .el-color-picker {
  flex-shrink: 0;
}

.color-input {
  width: 150px !important;
  flex-shrink: 0;
}

.color-preview {
  flex: 1;
  min-width: 0;
}

.color-preview-box {
  width: 100px;
  height: 40px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  flex-shrink: 0;
}

/* 渐变颜色行 - 统一对齐 */
.gradient-colors-row {
  display: flex;
  align-items: center;
  gap: 30px;
  margin-bottom: 15px;
}

.gradient-color-item {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.gradient-color-label {
  min-width: 60px;
  text-align: right;
  flex-shrink: 0;
}

.color-input-small {
  width: 120px !important;
  flex-shrink: 0;
}

/* 渐变方向行 - 统一对齐 */
.gradient-direction-row {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.gradient-direction-label {
  min-width: 80px;
  text-align: right;
  flex-shrink: 0;
}

.gradient-direction-select {
  width: 200px;
  flex-shrink: 0;
}

/* 不透明度控制行 - 统一对齐 */
.opacity-form-item {
  margin-bottom: 15px;
}

.opacity-control-row {
  display: flex;
  align-items: center;
  gap: 15px;
}

.opacity-input {
  width: 150px !important;
  flex-shrink: 0;
}

.opacity-hint {
  color: #909399;
  font-size: 12px;
  flex: 1;
  min-width: 0;
}
</style>
