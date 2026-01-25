
<template>
  <div>
    <div class="page-header">图像加解密</div>
    <el-card header="参数设置" class="mb-20">
      <!-- 密钥输入框和加密/解密按钮占位 -->
    </el-card>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card header="原始/加密图像">
          <!-- 原始或加密图像展示占位 -->
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="解密/还原图像">
          <!-- 解密或还原图像展示占位 -->
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
.mb-20 {
  margin-bottom: 20px;
}
</style>
