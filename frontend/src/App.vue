<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: var(--user-font-family, 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif);
  font-size: var(--user-font-size, 14px);
  color: var(--user-font-color, #303133);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 全局应用字体设置 */
body {
  font-family: var(--user-font-family, 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif) !important;
  font-size: var(--user-font-size, 14px) !important;
  color: var(--user-font-color, #303133) !important;
}

/* 确保所有文本元素应用字体设置 */
p, span, div, h1, h2, h3, h4, h5, h6, li, td, th, label, 
.el-card, .el-card__body, .el-card__header, .el-form-item__label, 
.el-button, .el-input__inner, .el-textarea__inner, .el-select .el-input__inner,
.el-menu-item, .el-sub-menu__title, .el-tag, .el-link {
  font-family: var(--user-font-family, inherit) !important;
  font-size: var(--user-font-size, 14px) !important;
  color: var(--user-font-color, #303133) !important;
}

/* 侧边栏背景色 - 强制应用到所有相关元素 */
.el-aside,
.el-aside.sidebar,
.el-aside .el-menu,
.el-aside .sidebar-menu {
  background-color: var(--user-sidebar-color, #fff) !important;
}

/* 导航栏背景色 - 强制应用到所有相关元素 */
.el-header,
.el-header.header {
  background-color: var(--user-header-color, #304156) !important;
}

/* 打印样式 */
@media print {
  /* 隐藏不需要打印的元素 */
  .header, 
  .sidebar, 
  .el-header, 
  .el-aside,
  .el-button:not(.print-visible),
  .export-controls,
  .action-area {
    display: none !important;
  }

  /* 调整主要内容区域 */
  .el-main,
  .main-content {
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    background-color: #fff !important;
  }

  /* 强制打印背景色和颜色 */
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  /* 移除阴影和边框，更适合打印 */
  .el-card {
    box-shadow: none !important;
    border: 1px solid #eee !important;
  }
}
</style>

