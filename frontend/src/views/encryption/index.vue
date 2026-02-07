<template>
  <div class="encryption-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-wrapper">
          <h1 class="page-title">图像加密</h1>
          <p class="page-subtitle">基于混沌理论的高强度图像加密系统</p>
        </div>
      </div>
    </div>

    <!-- Parameters Section -->
    <div class="params-section">
      <div class="section-card">
        <div class="card-header">
          <h3>参数配置</h3>
          <span class="badge">必填</span>
        </div>
        
        <div class="params-form">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">图像类别</label>
              <el-select 
                v-model="imageCategory" 
                placeholder="选择类别" 
                size="large"
                class="form-select"
              >
                <el-option label="舰船识别" value="warship" />
                <el-option label="人脸识别" value="face" />
                <el-option label="车牌识别" value="car" />
              </el-select>
            </div>
            
            <div class="form-group">
              <label class="form-label">加密密钥</label>
              <el-input 
                v-model="secretKey" 
                placeholder="输入密钥" 
                type="password" 
                show-password
                size="large"
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">选择图片</label>
              <el-upload
                class="upload-wrapper"
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleFileChange"
                accept="image/*"
              >
                <button class="upload-btn">
                  <el-icon><Folder /></el-icon>
                  <span>{{ selectedFile ? selectedFile.name : '选择文件' }}</span>
                </button>
              </el-upload>
            </div>
          </div>
          
          <button 
            class="encrypt-btn"
            @click="handleEncrypt" 
            :disabled="loading"
          >
            <el-icon v-if="!loading"><Lock /></el-icon>
            <el-icon v-else class="loading-icon"><Loading /></el-icon>
            <span>{{ loading ? '加密处理中...' : '开始加密' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Image Comparison -->
    <div class="comparison-section">
      <div class="comparison-grid">
        <!-- Original Image -->
        <div class="image-card">
          <div class="card-header">
            <h3>原始图像</h3>
            <span v-if="originalImageUrl" class="status-badge original">
              未加密
            </span>
          </div>
          <div class="image-container">
            <div v-if="!originalImageUrl" class="empty-state">
              <el-icon class="empty-icon"><Picture /></el-icon>
              <p class="empty-text">未选择图片</p>
            </div>
            <img v-else :src="originalImageUrl" alt="原始图像" class="preview-img" />
          </div>
        </div>

        <!-- Encrypted Image -->
        <div class="image-card">
          <div class="card-header">
            <h3>加密后图像</h3>
            <span v-if="encryptedImageUrl" class="status-badge encrypted">
              <span class="status-dot"></span>
              已加密
            </span>
          </div>
          <div class="image-container">
            <div v-if="loading" class="loading-state">
              <el-icon class="loading-icon"><Loading /></el-icon>
              <p class="loading-text">加密处理中...</p>
            </div>
            <div v-else-if="!encryptedImageUrl" class="empty-state">
              <el-icon class="empty-icon"><Lock /></el-icon>
              <p class="empty-text">等待加密</p>
            </div>
            <img v-else :src="encryptedImageUrl" alt="加密后图像" class="preview-img" />
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
import { Lock, Folder, Picture, Loading } from '@element-plus/icons-vue';


// --- 响应式数据 ---
const imageCategory = ref('warship'); // 默认类别
const secretKey = ref('');            // 密钥
const selectedFile = ref<File | null>(null); // 存储选中的文件对象
const originalImageUrl = ref('');     // 本地预览地址
const encryptedImageUrl = ref('');    // 后端返回的加密图地址
const loading = ref(false);           // 加载状态

// --- 1. 处理文件选择与预览 ---
const handleFileChange = (uploadFile: any) => {
  const rawFile = uploadFile.raw;
  
  // 校验图片
  if (!rawFile.type.startsWith('image/')) {
    ElMessage.error('只能上传图片文件');
    return;
  }

  // 保存文件对象供后续上传
  selectedFile.value = rawFile;

  // 生成本地预览 URL (不需要上传到后端就能看)
  originalImageUrl.value = URL.createObjectURL(rawFile);
  
  // 清空之前的加密结果
  encryptedImageUrl.value = '';
};

// --- 2. 处理加密请求 ---
const handleEncrypt = async () => {
  // 校验逻辑
  if (!selectedFile.value) {
    ElMessage.warning('请先选择一张图片');
    return;
  }
  if (!secretKey.value) {
    ElMessage.warning('请输入加密密钥');
    return;
  }

  loading.value = true;

  // 构建 FormData
  const formData = new FormData();
  formData.append('file', selectedFile.value);
  formData.append('image_category', imageCategory.value);
  formData.append('key', secretKey.value); // 传递密钥

  try {
    
    const data = await request.post(`/api/encrypt`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }) as any;
    console.log('后端返回数据:', data);

    if (data.url) {
      encryptedImageUrl.value = data.url;
      ElMessage.success('加密成功');
    } else {
      ElMessage.error('加密失败：未返回图像地址');
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

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.encryption-page {
  max-width: 1400px;
  margin: 0 auto;
  
  // Page Header
  .page-header {
    padding: 40px 0 48px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    margin-bottom: 48px;
    
    .header-content {
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
    }
  }
  
  // Parameters Section
  .params-section {
    margin-bottom: 48px;
    
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
      }
      
      .params-form {
        .form-row {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 20px;
          margin-bottom: 24px;
        }
        
        .form-group {
          .form-label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: $text-primary;
            margin-bottom: 12px;
          }
          
          .form-select,
          .form-input {
            width: 100%;
            
            :deep(.el-input__wrapper) {
              background: rgba(255, 255, 255, 0.02);
              border: 1px solid rgba(255, 255, 255, 0.1);
              box-shadow: none;
              
              &:hover {
                border-color: rgba(0, 212, 255, 0.3);
              }
              
              &.is-focus {
                border-color: rgba(0, 212, 255, 0.5);
              }
            }
          }
          
          .upload-wrapper {
            :deep(.el-upload) {
              width: 100%;
            }
            
            .upload-btn {
              width: 100%;
              height: 40px;
              display: flex;
              align-items: center;
              justify-content: center;
              gap: 8px;
              background: rgba(255, 255, 255, 0.02);
              border: 1px solid rgba(255, 255, 255, 0.1);
              border-radius: 8px;
              color: $text-primary;
              font-size: 14px;
              cursor: pointer;
              transition: all 0.2s ease;
              
              &:hover {
                background: rgba(255, 255, 255, 0.04);
                border-color: rgba(0, 212, 255, 0.3);
              }
              
              .el-icon {
                font-size: 16px;
              }
              
              span {
                max-width: 200px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
              }
            }
          }
        }
        
        .encrypt-btn {
          width: 100%;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          background: linear-gradient(135deg, $secondary-color, $primary-color);
          border: none;
          border-radius: 10px;
          color: $text-primary;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
          
          &:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 40px rgba(0, 212, 255, 0.3);
          }
          
          &:disabled {
            opacity: 0.6;
            cursor: not-allowed;
          }
          
          .el-icon {
            font-size: 18px;
          }
          
          .loading-icon {
            animation: rotate 1s linear infinite;
          }
        }
      }
    }
  }
  
  // Comparison Section
  .comparison-section {
    .comparison-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 24px;
    }
    
    .image-card {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 16px;
      padding: 24px;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: rgba(0, 212, 255, 0.2);
      }
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        
        h3 {
          font-size: 18px;
          font-weight: 600;
          color: $text-primary;
          margin: 0;
        }
        
        .status-badge {
          padding: 6px 12px;
          border-radius: 6px;
          font-size: 13px;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 8px;
          
          &.original {
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.2);
            color: $primary-color;
          }
          
          &.encrypted {
            background: rgba(0, 255, 170, 0.1);
            border: 1px solid rgba(0, 255, 170, 0.2);
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
      
      .image-container {
        height: 500px;
        display: flex;
        justify-content: center;
        align-items: center;
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        overflow: hidden;
        
        .preview-img {
          max-width: 100%;
          max-height: 100%;
          width: auto;
          height: auto;
          object-fit: contain;
          border-radius: 8px;
        }
        
        .empty-state,
        .loading-state {
          text-align: center;
          
          .empty-icon,
          .loading-icon {
            font-size: 64px;
            color: rgba(255, 255, 255, 0.08);
            margin-bottom: 16px;
          }
          
          .loading-icon {
            animation: rotate 1.5s linear infinite;
          }
          
          .empty-text,
          .loading-text {
            font-size: 14px;
            color: $text-secondary;
            margin: 0;
          }
        }
      }
    }
  }
}

// Animations
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

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
  .encryption-page {
    .params-section .section-card .params-form .form-row {
      grid-template-columns: 1fr;
    }
    
    .comparison-section .comparison-grid {
      grid-template-columns: 1fr;
    }
  }
}

@media (max-width: 768px) {
  .encryption-page {
    padding: 0 20px;
    
    .page-header {
      padding: 32px 0 36px;
      margin-bottom: 32px;
      
      .title-wrapper .page-title {
        font-size: 32px;
      }
    }
    
    .params-section .section-card,
    .comparison-section .image-card {
      padding: 20px;
    }
  }
}
</style>