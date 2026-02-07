<template>
  <div class="detection-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-wrapper">
          <h1 class="page-title">目标识别</h1>
          <p class="page-subtitle">基于 YOLOv9 的高精度图像目标检测与识别</p>
        </div>
        
        <div class="header-meta">
          <span class="meta-badge">
            <el-icon><Aim /></el-icon>
            YOLOv9
          </span>
        </div>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="detection-container">
      <!-- Left: Controls -->
      <div class="controls-section">
        <div class="section-card">
          <div class="card-header">
            <h3>检测配置</h3>
            <span class="badge">必填</span>
          </div>
          
          <!-- Category Selection -->
          <div class="form-group">
            <label class="form-label">识别类别</label>
            <div class="category-options">
              <div 
                v-for="cat in categories" 
                :key="cat.value"
                :class="['category-card', { active: imageCategory === cat.value }]"
                @click="imageCategory = cat.value"
              >
                <el-icon class="category-icon">
                  <component :is="cat.icon" />
                </el-icon>
                <div class="category-info">
                  <div class="category-name">{{ cat.label }}</div>
                  <div class="category-desc">{{ cat.dataset }}</div>
                </div>
                <el-icon v-if="imageCategory === cat.value" class="check-icon">
                  <Select />
                </el-icon>
              </div>
            </div>
          </div>
          
          <!-- Upload Area -->
          <div class="form-group">
            <label class="form-label">上传图片</label>
            <el-upload
              class="upload-zone"
              drag
              action=""
              :show-file-list="false"
              :before-upload="handleBeforeUpload"
              :http-request="handleUpload"
              accept="image/*"
            >
              <div class="upload-content">
                <el-icon class="upload-icon"><UploadFilled /></el-icon>
                <div class="upload-text">
                  <p class="main-text">拖拽图片到此处或点击上传</p>
                  <p class="sub-text">支持 JPG、PNG 格式，文件不超过 10MB</p>
                </div>
              </div>
            </el-upload>
          </div>
          
          <!-- Info Notice -->
          <div class="notice-box">
            <el-icon class="notice-icon"><InfoFilled /></el-icon>
            <span>检测完成后结果将自动显示在右侧区域</span>
          </div>
        </div>
      </div>
      
      <!-- Right: Results -->
      <div class="results-section">
        <div class="section-card result-card">
          <div class="card-header">
            <h3>检测结果</h3>
            <span v-if="resultImageUrl" class="status-badge success">
              <span class="status-dot"></span>
              已完成
            </span>
            <span v-else class="status-badge">
              等待检测
            </span>
          </div>
          
          <div class="result-area">
            <!-- Empty State -->
            <div v-if="!resultImageUrl" class="empty-result">
              <el-icon class="empty-icon"><Picture /></el-icon>
              <p class="empty-text">未检测到图像</p>
              <p class="empty-hint">请先上传图片并选择识别类别</p>
            </div>
            
            <!-- Result Display -->
            <div v-else class="result-display">
              <img :src="resultImageUrl" alt="检测结果" class="result-img" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';
import { 
  Aim, 
  UploadFilled, 
  Picture, 
  InfoFilled,
  Ship,
  User,
  Van,
  Select
} from '@element-plus/icons-vue';

const imageCategory = ref('warship');
const resultImageUrl = ref('');

const categories = [
  {
    value: 'warship',
    label: '舰船识别',
    dataset: 'HRSC2016',
    icon: Ship
  },
  {
    value: 'face',
    label: '人脸识别',
    dataset: 'CelebA',
    icon: User
  },
  {
    value: 'car',
    label: '车牌识别',
    dataset: 'CCPD',
    icon: Van
  }
];

function handleBeforeUpload(file: File) {
  const isImage = file.type.startsWith('image/');
  if (!isImage) {
    ElMessage.error('只能上传图片文件');
    return false;
  }
  
  const isLt10M = file.size / 1024 / 1024 < 10;
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB');
    return false;
  }
  
  return true;
}

async function handleUpload({ file }: { file: File }) {
  if (!imageCategory.value) {
    ElMessage.warning('请先选择识别类别');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);
  formData.append('image_category', imageCategory.value);

  const loading = ElMessage({
    message: '正在检测中...',
    duration: 0,
    type: 'info'
  });

  try {
    const data = await request.post('/api/predict', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }) as any;

    loading.close();

    if (data.url) {
      resultImageUrl.value = data.url;
      ElMessage.success('检测完成');
    } else {
      ElMessage.error('未获取到结果');
    }
  } catch (err) {
    loading.close();
    ElMessage.error('检测失败，请重试');
  }
}
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.detection-page {
  max-width: 1400px;
  margin: 0 auto;
  
  // Page Header
  .page-header {
    padding: 40px 0 48px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    margin-bottom: 48px;
    
    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }
    
    .title-wrapper {
      .page-title {
        font-size: 40px;
        font-weight: 600;
        color: $text-primary;
        margin: 0 0 12px;
        letter-spacing: -0.01em;
      }
      
      .page-subtitle {
        font-size: 16px;
        color: $text-secondary;
        margin: 0;
        line-height: 1.6;
      }
    }
    
    .header-meta {
      .meta-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 8px;
        font-size: 14px;
        color: $primary-color;
        font-weight: 500;
        
        .el-icon {
          font-size: 16px;
        }
      }
    }
  }
  
  // Main Container
  .detection-container {
    display: grid;
    grid-template-columns: 400px 1fr;
    gap: 32px;
    align-items: start;
  }
  
  // Section Card
  .section-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 32px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 32px;
      
      h3 {
        font-size: 18px;
        font-weight: 600;
        color: $text-primary;
        margin: 0;
      }
      
      .badge {
        padding: 4px 10px;
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 6px;
        font-size: 12px;
        color: $primary-color;
        font-weight: 500;
      }
      
      .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        font-size: 13px;
        color: $text-secondary;
        font-weight: 500;
        
        &.success {
          background: rgba(0, 255, 170, 0.1);
          border-color: rgba(0, 255, 170, 0.2);
          color: $accent-color;
          
          .status-dot {
            width: 6px;
            height: 6px;
            background: $accent-color;
            border-radius: 50%;
            animation: pulse-dot 2s infinite;
          }
        }
      }
    }
  }
  
  // Form Group
  .form-group {
    margin-bottom: 28px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .form-label {
      display: block;
      font-size: 14px;
      font-weight: 500;
      color: $text-primary;
      margin-bottom: 12px;
    }
  }
  
  // Category Options
  .category-options {
    display: flex;
    flex-direction: column;
    gap: 12px;
    
    .category-card {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 16px;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
      position: relative;
      
      &:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(0, 212, 255, 0.3);
      }
      
      &.active {
        background: rgba(0, 212, 255, 0.08);
        border-color: rgba(0, 212, 255, 0.4);
        
        .category-icon {
          color: $primary-color;
        }
        
        .category-name {
          color: $primary-color;
        }
      }
      
      .category-icon {
        font-size: 24px;
        color: $text-secondary;
        transition: color 0.2s ease;
      }
      
      .category-info {
        flex: 1;
        
        .category-name {
          font-size: 15px;
          font-weight: 500;
          color: $text-primary;
          margin-bottom: 4px;
          transition: color 0.2s ease;
        }
        
        .category-desc {
          font-size: 13px;
          color: $text-secondary;
        }
      }
      
      .check-icon {
        color: $primary-color;
        font-size: 20px;
      }
    }
  }
  
  // Upload Zone
  .upload-zone {
    :deep(.el-upload) {
      width: 100%;
      display: block;
    }
    
    :deep(.el-upload-dragger) {
      width: 100%;
      padding: 40px 20px;
      background: rgba(255, 255, 255, 0.02);
      border: 2px dashed rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(0, 212, 255, 0.05);
        border-color: rgba(0, 212, 255, 0.4);
        
        .upload-icon {
          transform: translateY(-4px);
          color: $primary-color;
        }
      }
    }
    
    .upload-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      
      .upload-icon {
        font-size: 48px;
        color: $text-secondary;
        margin-bottom: 16px;
        transition: all 0.3s ease;
      }
      
      .upload-text {
        text-align: center;
        
        .main-text {
          font-size: 15px;
          color: $text-primary;
          margin: 0 0 8px;
          font-weight: 500;
        }
        
        .sub-text {
          font-size: 13px;
          color: $text-secondary;
          margin: 0;
        }
      }
    }
  }
  
  // Notice Box
  .notice-box {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 16px;
    background: rgba(0, 212, 255, 0.05);
    border: 1px solid rgba(0, 212, 255, 0.15);
    border-radius: 10px;
    font-size: 13px;
    color: $text-secondary;
    line-height: 1.6;
    margin-top: 28px;
    
    .notice-icon {
      color: $primary-color;
      font-size: 16px;
      flex-shrink: 0;
      margin-top: 2px;
    }
  }
  
  // Results Section
  .results-section {
    .result-card {
      min-height: 600px;
      display: flex;
      flex-direction: column;
    }
    
    .result-area {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(0, 0, 0, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 12px;
      padding: 32px;
      height: 500px;
      overflow: hidden;
    }
    
    .empty-result {
      text-align: center;
      
      .empty-icon {
        font-size: 64px;
        color: rgba(255, 255, 255, 0.08);
        margin-bottom: 20px;
      }
      
      .empty-text {
        font-size: 16px;
        font-weight: 500;
        color: $text-secondary;
        margin: 0 0 8px;
      }
      
      .empty-hint {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.3);
        margin: 0;
      }
    }
    
    .result-display {
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
      
      .result-img {
        max-width: 100%;
        max-height: 100%;
        width: auto;
        height: auto;
        object-fit: contain;
        border-radius: 10px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
      }
    }
  }
}

// Animations
@keyframes pulse-dot {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 0 0 rgba(0, 255, 170, 0.7);
  }
  50% {
    opacity: 0.8;
    box-shadow: 0 0 0 6px rgba(0, 255, 170, 0);
  }
}

// Responsive
@media (max-width: 1024px) {
  .detection-page {
    .detection-container {
      grid-template-columns: 1fr;
    }
  }
}

@media (max-width: 768px) {
  .detection-page {
    padding: 0 20px;
    
    .page-header {
      padding: 32px 0 36px;
      margin-bottom: 32px;
      
      .header-content {
        flex-direction: column;
        gap: 20px;
      }
      
      .title-wrapper .page-title {
        font-size: 32px;
      }
    }
    
    .section-card {
      padding: 24px;
    }
  }
}
</style>
