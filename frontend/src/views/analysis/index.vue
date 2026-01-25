
<template>
  <div>
    <div class="page-header">加密安全性分析</div>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card header="直方图分析">
          <div style="height: 300px;"><!-- ECharts 直方图占位 --></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="相邻像素相关性">
          <div style="height: 300px;"><!-- ECharts 相关性占位 --></div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card header="信息熵分析">
          <div style="height: 300px;"><!-- ECharts 信息熵占位 --></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="密钥敏感性">
          <div style="height: 300px;"><!-- ECharts 密钥敏感性占位 --></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
// 暂无复杂逻辑
</script>

<style scoped>
.page-header {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 24px;
}
.mt-20 {
  margin-top: 20px;
}
</style>
