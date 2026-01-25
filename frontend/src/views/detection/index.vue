
<template>
  <div>
    <div class="page-header">敏感信息识别</div>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card header="上传与配置">
          <!-- 上传组件占位 -->
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card header="检测结果">
          <div id="detection-canvas" style="height: 300px; margin-bottom: 16px;"></div>
          <!-- 检测结果列表占位 -->
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
