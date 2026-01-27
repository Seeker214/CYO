<template>
  <div>
    <div class="page-header">敏感信息识别</div>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card header="上传与配置">
          <el-form @submit.prevent>
            <el-form-item label="选择类别">
              <el-select v-model="imageCategory" placeholder="请选择类别" style="width: 100%">
                <el-option label="warship" value="warship" />
                <el-option label="face" value="face" />
                <el-option label="car" value="car" />
              </el-select>
            </el-form-item>
            <el-form-item label="上传图片">
              <el-upload
                class="upload-demo"
                action=""
                :show-file-list="false"
                :before-upload="handleBeforeUpload"
                :http-request="handleUpload"
                accept="image/*"
              >
                <el-button type="primary">选择图片</el-button>
              </el-upload>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card header="检测结果">
          <div id="detection-canvas" style="height: 300px; margin-bottom: 16px;">
            <img v-if="resultImageUrl" :src="resultImageUrl" alt="检测结果" style="max-width:100%;max-height:300px;" />
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

const imageCategory = ref('warship');
const resultImageUrl = ref('');

function handleBeforeUpload(file: File) {
  const isImage = file.type.startsWith('image/');
  if (!isImage) {
    ElMessage.error('只能上传图片文件');
  }
  return isImage;
}

async function handleUpload({ file }: { file: File }) {
  if (!imageCategory.value) return;

  const formData = new FormData();
  formData.append('file', file);
  formData.append('image_category', imageCategory.value);

  try {
    // 【修改点】：直接写相对路径，axios 会自动拼接 VITE_API_BASE_URL
    // 即：http://127.0.0.1:8000 + /api/predict
    const data = await request.post('/api/predict', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    // 因为我们在拦截器里直接返回了 response.data，这里直接用 data
    if (data.url) {
      resultImageUrl.value = data.url;
      ElMessage.success('检测完成');
    } else {
      ElMessage.error('未获取到结果');
    }
  } catch (err) {
    // 错误已经在拦截器里弹窗了，这里可以不写，或者处理特定的 loading 状态
  }
}
</script>

<style scoped>
.page-header {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 24px;
}
</style>
