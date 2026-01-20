import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { getSettings, saveSettings as saveSettingsAPI } from '@/api/settings'

// 默认设置
const defaultSettings = {
  fontSize: 14, // 字体大小（px）
  fontFamily: 'Arial, sans-serif', // 字体样式
  fontColor: '#303133', // 字体颜色
  headerColor: '#304156', // 上方导航栏背景色（单色模式）
  headerUseGradient: false, // 是否使用渐变
  headerGradientType: 'linear', // 渐变类型：linear（线性）或 radial（径向）
  headerGradientColor1: '#304156', // 渐变颜色1
  headerGradientColor2: '#409EFF', // 渐变颜色2
  headerGradientDirection: 'to right', // 渐变方向（线性渐变）：to right, to left, to bottom, to top, to bottom right 等
  sidebarColor: '#fff', // 左侧侧边栏背景色（单色模式）
  sidebarUseGradient: false, // 侧边栏是否使用渐变
  sidebarGradientType: 'linear', // 侧边栏渐变类型：linear（线性）或 radial（径向）
  sidebarGradientColor1: '#fff', // 侧边栏渐变颜色1
  sidebarGradientColor2: '#f0f2f5', // 侧边栏渐变颜色2
  sidebarGradientDirection: 'to bottom', // 侧边栏渐变方向
  contentBackgroundColor: '#f0f2f5', // 中间内容区域背景色
  customFontName: null, // 自定义字体名称
  customFontUrl: null, // 自定义字体文件URL
  logoSize: 40, // Logo 大小（px）
  backgroundImageUrl: null, // 背景图片 URL
  backgroundImageOpacity: 1.0 // 背景图片不透明度（0-1）
}

export const useSettingsStore = defineStore('settings', () => {
  // 先定义所有 ref 变量（必须在函数调用之前定义）
  const fontSize = ref(defaultSettings.fontSize)
  const fontFamily = ref(defaultSettings.fontFamily)
  const fontColor = ref(defaultSettings.fontColor)
  const headerColor = ref(defaultSettings.headerColor)
  const headerUseGradient = ref(defaultSettings.headerUseGradient)
  const headerGradientType = ref(defaultSettings.headerGradientType)
  const headerGradientColor1 = ref(defaultSettings.headerGradientColor1)
  const headerGradientColor2 = ref(defaultSettings.headerGradientColor2)
  const headerGradientDirection = ref(defaultSettings.headerGradientDirection)
  const sidebarColor = ref(defaultSettings.sidebarColor)
  const sidebarUseGradient = ref(defaultSettings.sidebarUseGradient)
  const sidebarGradientType = ref(defaultSettings.sidebarGradientType)
  const sidebarGradientColor1 = ref(defaultSettings.sidebarGradientColor1)
  const sidebarGradientColor2 = ref(defaultSettings.sidebarGradientColor2)
  const sidebarGradientDirection = ref(defaultSettings.sidebarGradientDirection)
  const contentBackgroundColor = ref(defaultSettings.contentBackgroundColor)
  const customFontName = ref(defaultSettings.customFontName)
  const customFontUrl = ref(defaultSettings.customFontUrl)
  const logoSize = ref(defaultSettings.logoSize)
  const backgroundImageUrl = ref(defaultSettings.backgroundImageUrl)
  const backgroundImageOpacity = ref(defaultSettings.backgroundImageOpacity)

  // 生成导航栏背景样式
  const getHeaderBackground = () => {
    if (headerUseGradient.value) {
      if (headerGradientType.value === 'linear') {
        return `linear-gradient(${headerGradientDirection.value}, ${headerGradientColor1.value}, ${headerGradientColor2.value})`
      } else {
        return `radial-gradient(circle, ${headerGradientColor1.value}, ${headerGradientColor2.value})`
      }
    }
    return headerColor.value
  }

  // 加载自定义字体
  const loadCustomFont = (fontName, fontUrl) => {
    // 检查是否已经加载过这个字体
    const existingStyle = document.getElementById(`custom-font-${fontName}`)
    if (existingStyle) {
      return
    }

    // 创建 @font-face 样式
    const style = document.createElement('style')
    style.id = `custom-font-${fontName}`
    style.textContent = `
      @font-face {
        font-family: "${fontName}";
        src: url("${fontUrl}") format("truetype");
      }
    `
    document.head.appendChild(style)
  }

  // 应用设置到页面
  const applySettings = () => {
    const root = document.documentElement
    
    // 设置字体大小
    root.style.setProperty('--user-font-size', `${fontSize.value}px`)
    
    // 设置字体样式
    let finalFontFamily = fontFamily.value
    if (customFontName.value && customFontUrl.value) {
      // 如果有自定义字体，使用自定义字体
      finalFontFamily = `"${customFontName.value}", Arial, sans-serif`
      
      // 动态加载自定义字体
      loadCustomFont(customFontName.value, customFontUrl.value)
    }
    root.style.setProperty('--user-font-family', finalFontFamily)
    
    // 设置字体颜色
    root.style.setProperty('--user-font-color', fontColor.value)
    
    // 设置上方导航栏颜色
    const headerBackground = getHeaderBackground()
    root.style.setProperty('--user-header-color', headerColor.value)
    root.style.setProperty('--user-header-background', headerBackground)
    
    // 应用到导航栏元素
    setTimeout(() => {
      const header = document.querySelector('.header')
      const elHeader = document.querySelector('.el-header')
      
      if (headerUseGradient.value) {
        // 渐变模式
        if (header) {
          header.style.setProperty('background', headerBackground, 'important')
          header.style.setProperty('background-color', 'transparent', 'important')
        }
        if (elHeader) {
          elHeader.style.setProperty('background', headerBackground, 'important')
          elHeader.style.setProperty('background-color', 'transparent', 'important')
        }
      } else {
        // 单色模式
        if (header) {
          header.style.setProperty('background-color', headerColor.value, 'important')
          header.style.setProperty('background', headerColor.value, 'important')
        }
        if (elHeader) {
          elHeader.style.setProperty('background-color', headerColor.value, 'important')
          elHeader.style.setProperty('background', headerColor.value, 'important')
        }
      }
    }, 0)
    
    // 设置左侧侧边栏颜色（单色或渐变）
    if (sidebarUseGradient.value) {
      if (sidebarGradientType.value === 'linear') {
        const sidebarBg = `linear-gradient(${sidebarGradientDirection.value}, ${sidebarGradientColor1.value}, ${sidebarGradientColor2.value})`
        root.style.setProperty('--user-sidebar-background', sidebarBg)
      } else {
        const sidebarBg = `radial-gradient(circle, ${sidebarGradientColor1.value}, ${sidebarGradientColor2.value})`
        root.style.setProperty('--user-sidebar-background', sidebarBg)
      }
    } else {
      root.style.setProperty('--user-sidebar-background', sidebarColor.value)
    }
    root.style.setProperty('--user-sidebar-color', sidebarColor.value)
    
    // 设置中间内容区域背景色
    root.style.setProperty('--user-content-bg-color', contentBackgroundColor.value)
    
    // 设置 Logo 大小
    root.style.setProperty('--user-logo-size', `${logoSize.value}px`)
    
    // 设置背景图片
    if (backgroundImageUrl.value) {
      const opacity = backgroundImageOpacity.value || 1.0
      root.style.setProperty('--user-background-image', `url(${backgroundImageUrl.value})`)
      root.style.setProperty('--user-background-opacity', opacity.toString())
      // 使用伪元素实现不透明度
      const bgStyle = document.getElementById('background-image-style')
      if (bgStyle) {
        bgStyle.remove()
      }
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
          background-image: url(${backgroundImageUrl.value});
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
    } else {
      root.style.setProperty('--user-background-image', 'none')
      const bgStyle = document.getElementById('background-image-style')
      if (bgStyle) {
        bgStyle.remove()
      }
      document.body.style.setProperty('background-image', 'none', 'important')
    }
    
    // 强制应用到所有元素
    document.body.style.fontFamily = finalFontFamily
    document.body.style.fontSize = `${fontSize.value}px`
    document.body.style.color = fontColor.value
    
    // 应用到导航栏（强制覆盖所有相关元素）
    const header = document.querySelector('.header')
    if (header) {
      if (headerUseGradient.value) {
        header.style.setProperty('background', headerBackground, 'important')
        header.style.setProperty('background-color', 'transparent', 'important')
      } else {
        header.style.setProperty('background-color', headerColor.value, 'important')
        header.style.setProperty('background', 'none', 'important')
      }
    }
    // 也应用到 el-header
    const elHeader = document.querySelector('.el-header')
    if (elHeader) {
      if (headerUseGradient.value) {
        elHeader.style.setProperty('background', headerBackground, 'important')
        elHeader.style.setProperty('background-color', 'transparent', 'important')
      } else {
        elHeader.style.setProperty('background-color', headerColor.value, 'important')
        elHeader.style.setProperty('background', 'none', 'important')
      }
    }
    
      // 应用到侧边栏（强制覆盖所有相关元素）
      setTimeout(() => {
        let sidebarBg = sidebarColor.value
        if (sidebarUseGradient.value) {
          if (sidebarGradientType.value === 'linear') {
            sidebarBg = `linear-gradient(${sidebarGradientDirection.value}, ${sidebarGradientColor1.value}, ${sidebarGradientColor2.value})`
          } else {
            sidebarBg = `radial-gradient(circle, ${sidebarGradientColor1.value}, ${sidebarGradientColor2.value})`
          }
        }
        
        const sidebar = document.querySelector('.sidebar')
        if (sidebar) {
          if (sidebarUseGradient.value) {
            sidebar.style.setProperty('background', sidebarBg, 'important')
            sidebar.style.setProperty('background-color', 'transparent', 'important')
          } else {
            sidebar.style.setProperty('background-color', sidebarColor.value, 'important')
            sidebar.style.setProperty('background', sidebarColor.value, 'important')
          }
        }
        // 也应用到 el-aside
        const elAside = document.querySelector('.el-aside')
        if (elAside) {
          if (sidebarUseGradient.value) {
            elAside.style.setProperty('background', sidebarBg, 'important')
            elAside.style.setProperty('background-color', 'transparent', 'important')
          } else {
            elAside.style.setProperty('background-color', sidebarColor.value, 'important')
            elAside.style.setProperty('background', sidebarColor.value, 'important')
          }
        }
        // 应用到侧边栏菜单
        const sidebarMenu = document.querySelector('.sidebar-menu')
        if (sidebarMenu) {
          if (sidebarUseGradient.value) {
            sidebarMenu.style.setProperty('background', sidebarBg, 'important')
            sidebarMenu.style.setProperty('background-color', 'transparent', 'important')
          } else {
            sidebarMenu.style.setProperty('background-color', sidebarColor.value, 'important')
            sidebarMenu.style.setProperty('background', sidebarColor.value, 'important')
          }
        }
        // 应用到 el-menu（查找所有可能的菜单元素）
        const elMenus = document.querySelectorAll('.el-aside .el-menu')
        elMenus.forEach(menu => {
          if (sidebarUseGradient.value) {
            menu.style.setProperty('background', sidebarBg, 'important')
            menu.style.setProperty('background-color', 'transparent', 'important')
          } else {
            menu.style.setProperty('background-color', sidebarColor.value, 'important')
            menu.style.setProperty('background', sidebarColor.value, 'important')
          }
        })
        // 也直接设置 background 属性
        const allSidebarElements = document.querySelectorAll('.el-aside, .sidebar, .sidebar-menu, .el-aside .el-menu')
        allSidebarElements.forEach(el => {
          if (sidebarUseGradient.value) {
            el.style.setProperty('background', sidebarBg, 'important')
            el.style.setProperty('background-color', 'transparent', 'important')
          } else {
            el.style.setProperty('background-color', sidebarColor.value, 'important')
            el.style.setProperty('background', sidebarColor.value, 'important')
          }
        })
      
      // 应用到中间内容区域
      const mainContent = document.querySelector('.main-content')
      if (mainContent) {
        mainContent.style.setProperty('background-color', contentBackgroundColor.value, 'important')
      }
      const elMain = document.querySelector('.el-main')
      if (elMain) {
        elMain.style.setProperty('background-color', contentBackgroundColor.value, 'important')
      }
    }, 0)
  }

  // 从 localStorage 加载设置（备用方案）
  const loadSettingsFromLocal = () => {
    const saved = localStorage.getItem('userSettings')
    if (saved) {
      try {
        const localSettings = JSON.parse(saved)
        fontSize.value = localSettings.fontSize || defaultSettings.fontSize
        fontFamily.value = localSettings.fontFamily || defaultSettings.fontFamily
        fontColor.value = localSettings.fontColor || defaultSettings.fontColor
        customFontName.value = localSettings.customFontName || defaultSettings.customFontName
        customFontUrl.value = localSettings.customFontUrl || defaultSettings.customFontUrl
        headerColor.value = localSettings.headerColor || defaultSettings.headerColor
        headerUseGradient.value = localSettings.headerUseGradient !== undefined ? localSettings.headerUseGradient : defaultSettings.headerUseGradient
        headerGradientType.value = localSettings.headerGradientType || defaultSettings.headerGradientType
        headerGradientColor1.value = localSettings.headerGradientColor1 || defaultSettings.headerGradientColor1
        headerGradientColor2.value = localSettings.headerGradientColor2 || defaultSettings.headerGradientColor2
        headerGradientDirection.value = localSettings.headerGradientDirection || defaultSettings.headerGradientDirection
        sidebarColor.value = localSettings.sidebarColor || defaultSettings.sidebarColor
        sidebarUseGradient.value = localSettings.sidebarUseGradient !== undefined ? localSettings.sidebarUseGradient : defaultSettings.sidebarUseGradient
        sidebarGradientType.value = localSettings.sidebarGradientType || defaultSettings.sidebarGradientType
        sidebarGradientColor1.value = localSettings.sidebarGradientColor1 || defaultSettings.sidebarGradientColor1
        sidebarGradientColor2.value = localSettings.sidebarGradientColor2 || defaultSettings.sidebarGradientColor2
        sidebarGradientDirection.value = localSettings.sidebarGradientDirection || defaultSettings.sidebarGradientDirection
        contentBackgroundColor.value = localSettings.contentBackgroundColor || defaultSettings.contentBackgroundColor
        backgroundImageUrl.value = localSettings.backgroundImageUrl || defaultSettings.backgroundImageUrl
        backgroundImageOpacity.value = localSettings.backgroundImageOpacity !== undefined ? localSettings.backgroundImageOpacity : defaultSettings.backgroundImageOpacity
        logoSize.value = localSettings.logoSize || defaultSettings.logoSize
        applySettings()
        return true
      } catch (e) {
        console.error('加载设置失败:', e)
      }
    }
    // 使用默认设置
    fontSize.value = defaultSettings.fontSize
    fontFamily.value = defaultSettings.fontFamily
    fontColor.value = defaultSettings.fontColor
    customFontName.value = defaultSettings.customFontName
    customFontUrl.value = defaultSettings.customFontUrl
    headerColor.value = defaultSettings.headerColor
    headerUseGradient.value = defaultSettings.headerUseGradient
    headerGradientType.value = defaultSettings.headerGradientType
    headerGradientColor1.value = defaultSettings.headerGradientColor1
    headerGradientColor2.value = defaultSettings.headerGradientColor2
    headerGradientDirection.value = defaultSettings.headerGradientDirection
    sidebarColor.value = defaultSettings.sidebarColor
    sidebarUseGradient.value = defaultSettings.sidebarUseGradient
    sidebarGradientType.value = defaultSettings.sidebarGradientType
    sidebarGradientColor1.value = defaultSettings.sidebarGradientColor1
    sidebarGradientColor2.value = defaultSettings.sidebarGradientColor2
    sidebarGradientDirection.value = defaultSettings.sidebarGradientDirection
    contentBackgroundColor.value = defaultSettings.contentBackgroundColor
    backgroundImageUrl.value = defaultSettings.backgroundImageUrl
    backgroundImageOpacity.value = defaultSettings.backgroundImageOpacity
    logoSize.value = defaultSettings.logoSize
    applySettings()
    return false
  }

  // 从后端加载设置
  const loadSettingsFromServer = async () => {
    try {
      const res = await getSettings()
      if (res && res.data && res.data.code === 200 && res.data.data) {
        const serverSettings = res.data.data
        // 更新所有ref值
        fontSize.value = serverSettings.fontSize || defaultSettings.fontSize
        fontFamily.value = serverSettings.fontFamily || defaultSettings.fontFamily
        fontColor.value = serverSettings.fontColor || defaultSettings.fontColor
        customFontName.value = serverSettings.customFontName || defaultSettings.customFontName
        customFontUrl.value = serverSettings.customFontUrl || defaultSettings.customFontUrl
        headerColor.value = serverSettings.headerColor || defaultSettings.headerColor
        headerUseGradient.value = serverSettings.headerUseGradient !== undefined ? serverSettings.headerUseGradient : defaultSettings.headerUseGradient
        headerGradientType.value = serverSettings.headerGradientType || defaultSettings.headerGradientType
        headerGradientColor1.value = serverSettings.headerGradientColor1 || defaultSettings.headerGradientColor1
        headerGradientColor2.value = serverSettings.headerGradientColor2 || defaultSettings.headerGradientColor2
        headerGradientDirection.value = serverSettings.headerGradientDirection || defaultSettings.headerGradientDirection
        sidebarColor.value = serverSettings.sidebarColor || defaultSettings.sidebarColor
        sidebarUseGradient.value = serverSettings.sidebarUseGradient !== undefined ? serverSettings.sidebarUseGradient : defaultSettings.sidebarUseGradient
        sidebarGradientType.value = serverSettings.sidebarGradientType || defaultSettings.sidebarGradientType
        sidebarGradientColor1.value = serverSettings.sidebarGradientColor1 || defaultSettings.sidebarGradientColor1
        sidebarGradientColor2.value = serverSettings.sidebarGradientColor2 || defaultSettings.sidebarGradientColor2
        sidebarGradientDirection.value = serverSettings.sidebarGradientDirection || defaultSettings.sidebarGradientDirection
        contentBackgroundColor.value = serverSettings.contentBackgroundColor || defaultSettings.contentBackgroundColor
        backgroundImageUrl.value = serverSettings.backgroundImageUrl || defaultSettings.backgroundImageUrl
        backgroundImageOpacity.value = serverSettings.backgroundImageOpacity !== undefined ? serverSettings.backgroundImageOpacity : defaultSettings.backgroundImageOpacity
        logoSize.value = serverSettings.logoSize || defaultSettings.logoSize
        // 应用设置
        applySettings()
        return true
      }
    } catch (error) {
      console.error('从服务器加载设置失败:', error)
      // 如果失败，尝试从 localStorage 加载
      return loadSettingsFromLocal()
    }
    return false
  }

  // 初始化时从服务器加载设置（只在有token时加载）
  // 如果没有token，会静默失败并使用默认设置
  // 注意：这个调用是异步的，不会阻塞应用启动
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      const token = window.localStorage.getItem('token')
      // 只有在有有效token时才尝试从服务器加载设置
      // 注意：这里不验证token是否有效，因为验证会在请求时进行
      // 如果token无效，loadSettingsFromServer会失败并fallback到本地设置
      if (token && token.trim() !== '') {
      // 有token时，异步加载服务器设置（不阻塞）
      Promise.resolve().then(() => {
          loadSettingsFromServer().catch((error) => {
            // 如果是401错误（未授权），说明token无效，清除token
            if (error?.response?.status === 401) {
              window.localStorage.removeItem('token')
            }
          // 静默失败，使用本地设置
          loadSettingsFromLocal()
        })
      })
    } else {
      // 没有token时，直接使用默认设置
        loadSettingsFromLocal()
      }
    } else {
      // 没有localStorage时，使用默认设置
      loadSettingsFromLocal()
    }
  } catch (e) {
    // 如果出错，使用默认设置
    loadSettingsFromLocal()
  }

  // 保存设置到服务器和 localStorage
  const saveSettings = async () => {
    const settings = {
      fontSize: fontSize.value,
      fontFamily: fontFamily.value,
      fontColor: fontColor.value,
      headerColor: headerColor.value,
      headerUseGradient: headerUseGradient.value,
      headerGradientType: headerGradientType.value,
      headerGradientColor1: headerGradientColor1.value,
      headerGradientColor2: headerGradientColor2.value,
      headerGradientDirection: headerGradientDirection.value,
      sidebarColor: sidebarColor.value,
      sidebarUseGradient: sidebarUseGradient.value,
      sidebarGradientType: sidebarGradientType.value,
      sidebarGradientColor1: sidebarGradientColor1.value,
      sidebarGradientColor2: sidebarGradientColor2.value,
      sidebarGradientDirection: sidebarGradientDirection.value,
      contentBackgroundColor: contentBackgroundColor.value,
      customFontName: customFontName.value,
      customFontUrl: customFontUrl.value,
      logoSize: logoSize.value,
      backgroundImageUrl: backgroundImageUrl.value,
      backgroundImageOpacity: backgroundImageOpacity.value
    }
    
    // 同时保存到 localStorage（作为备用）
    localStorage.setItem('userSettings', JSON.stringify(settings))
    
    // 保存到服务器
    try {
      await saveSettingsAPI(settings)
    } catch (error) {
      console.error('保存设置到服务器失败:', error)
      // 如果服务器保存失败，至少本地已保存
    }
    
    applySettings()
  }

  // 重置为默认设置
  const resetSettings = () => {
    fontSize.value = defaultSettings.fontSize
    fontFamily.value = defaultSettings.fontFamily
    fontColor.value = defaultSettings.fontColor
    headerColor.value = defaultSettings.headerColor
    headerUseGradient.value = defaultSettings.headerUseGradient
    headerGradientType.value = defaultSettings.headerGradientType
    headerGradientColor1.value = defaultSettings.headerGradientColor1
    headerGradientColor2.value = defaultSettings.headerGradientColor2
    headerGradientDirection.value = defaultSettings.headerGradientDirection
    sidebarColor.value = defaultSettings.sidebarColor
    sidebarUseGradient.value = defaultSettings.sidebarUseGradient
    sidebarGradientType.value = defaultSettings.sidebarGradientType
    sidebarGradientColor1.value = defaultSettings.sidebarGradientColor1
    sidebarGradientColor2.value = defaultSettings.sidebarGradientColor2
    sidebarGradientDirection.value = defaultSettings.sidebarGradientDirection
    contentBackgroundColor.value = defaultSettings.contentBackgroundColor
    customFontName.value = defaultSettings.customFontName
    customFontUrl.value = defaultSettings.customFontUrl
    logoSize.value = defaultSettings.logoSize
    backgroundImageUrl.value = defaultSettings.backgroundImageUrl
    backgroundImageOpacity.value = defaultSettings.backgroundImageOpacity
    saveSettings()
  }

  // 初始化时应用设置（延迟执行，等待从服务器加载完成）
  setTimeout(() => {
    applySettings()
  }, 100)

  return {
    loadSettingsFromServer,
    loadSettingsFromLocal,
    fontSize,
    fontFamily,
    fontColor,
    headerColor,
    headerUseGradient,
    headerGradientType,
    headerGradientColor1,
    headerGradientColor2,
    headerGradientDirection,
    sidebarColor,
    sidebarUseGradient,
    sidebarGradientType,
    sidebarGradientColor1,
    sidebarGradientColor2,
    sidebarGradientDirection,
    contentBackgroundColor,
    customFontName,
    customFontUrl,
    logoSize,
    backgroundImageUrl,
    backgroundImageOpacity,
    saveSettings,
    resetSettings,
    applySettings,
    loadCustomFont,
    getHeaderBackground
  }
})
