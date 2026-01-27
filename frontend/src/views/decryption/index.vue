<template>
  <div>
    <div class="page-header">图像解密工具</div>

    <el-card header="参数配置与上传" class="mb-20">
      <el-form :inline="true" class="demo-form-inline">

        <el-form-item label="解密密钥">
          <el-input 
            v-model="secretKey" 
            placeholder="请输入密钥" 
            type="password" 
            show-password
            style="width: 200px" 
          />
        </el-form-item>

        <el-form-item>
          <el-upload
            class="upload-inline"
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFileChange"
            accept="image/*"
          >
            <el-button>选择图片</el-button>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleEncrypt" :loading="loading">
            开始解密
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card header="待解密图像">
          <div class="image-container">
            <div v-if="!originalImageUrl" class="placeholder-text">请先选择图片</div>
            <img v-else :src="originalImageUrl" alt="待解密图像" class="preview-img" />
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card header="解密后图像 (结果)">
          <div class="image-container">
            <div v-if="loading" class="placeholder-text">解密处理中...</div>
            <div v-else-if="!encryptedImageUrl" class="placeholder-text">等待处理结果</div>
            <img v-else :src="encryptedImageUrl" alt="解密后图像" class="preview-img" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';


// --- 响应式数据 ---
const imageCategory = ref('warship'); // 默认类别
const secretKey = ref('');            // 密钥
const selectedFile = ref<File | null>(null); // 存储选中的文件对象
const originalImageUrl = ref('');     // 本地预览地址
const encryptedImageUrl = ref('');    // 后端返回的图地址
const loading = ref(false);           // 加载状态

// --- 1. 处理文件选择与预览 ---
const handleFileChange = (uploadFile: any) => {
  const rawFile = uploadFile.raw;
  
  if (!rawFile.type.startsWith('image/')) {
    ElMessage.error('只能上传图片文件');
    return;
  }

  selectedFile.value = rawFile;

  originalImageUrl.value = URL.createObjectURL(rawFile);
  
  encryptedImageUrl.value = '';
};

const handleEncrypt = async () => {
  // 校验逻辑
  if (!selectedFile.value) {
    ElMessage.warning('请先选择待解密图片');
    return;
  }
  if (!secretKey.value) {
    ElMessage.warning('请输入解密密钥');
    return;
  }

  loading.value = true;

  const formData = new FormData();
  formData.append('file', selectedFile.value);
  formData.append('key', secretKey.value); // 传递密钥

  try {
    const res = await request.post(`/api/decrypt`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    console.log('后端返回数据:', res);

    if (res.url) {
      encryptedImageUrl.value = res.url;
      ElMessage.success('解密成功');
    } else {
      ElMessage.error('解密失败：未返回图像地址');
    }

  } catch (error: any) {
    console.error(error);
    const msg = error.response?.data?.detail || error.message || '请求失败';
    ElMessage.error(msg);
  } finally {
    loading.value = false;
  }
};
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

/* 简单的图像容器样式 */
.image-container {
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.placeholder-text {
  color: #909399;
  font-size: 14px;
}

/* 让上传组件表现为行内元素 */
.upload-inline {
  display: inline-block;
  margin-right: 10px;
}
</style>