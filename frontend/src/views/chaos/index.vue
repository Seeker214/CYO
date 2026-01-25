
<template>
  <div>
    <div class="page-header">混沌特性展示</div>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card header="参数设置">
          <!-- 混沌系统参数控制（如 μ 值）占位 -->
        </el-card>
      </el-col>
      <el-col :span="18">
        <el-card header="可视化区域">
          <div style="height: 400px;"><!-- 分岔图/相图可视化占位 --></div>
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
</style>
