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
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
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

