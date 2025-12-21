<template>
  <div class="help-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>帮助中心</span>
        </div>
      </template>
      <div class="content">
        <el-collapse>
          <el-collapse-item title="如何使用饮食日志？" name="1">
            <div>在饮食日志页面，您可以记录每日的饮食摄入情况，包括热量、营养素比例等。</div>
          </el-collapse-item>
          <el-collapse-item title="如何查看预测报告？" name="2">
            <div>预测报告页面会根据您的历史数据和AI算法，预测未来的体重变化趋势。</div>
          </el-collapse-item>
          <el-collapse-item title="什么是AI体重虚拟实验？" name="3">
            <div>这是一个基于AI的模拟系统，可以根据您的生理参数模拟不同干预措施下的体重变化。</div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>
  </div>
</template>

<script setup>
</script>

<style scoped>
.help-container {
  padding: 20px;
}
</style>