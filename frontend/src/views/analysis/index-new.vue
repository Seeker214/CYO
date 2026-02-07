<template>
  <div class="analysis-page">
    <PageHeader 
      title="图像分析"
      subtitle="3D可视化分析，深入理解图像数据特征"
      :icon="DataAnalysis"
    />
    
    <div class="control-section glass-card">
      <div class="panel-header">
        <el-icon class="header-icon"><Upload /></el-icon>
        <h3>上传分析</h3>
      </div>
      
      <el-row :gutter="24">
        <el-col :span="8">
          <div class="mode-selector">
            <span class="label-text">图像类型：</span>
            <el-switch
              v-model="isEncrypted"
              size="large"
              inline-prompt
              active-text="加密后"
              inactive-text="原始图像"
            />
          </div>
          
          <el-upload
            class="upload-area"
            drag
            action=""
            :http-request="handleUpload"
            :show-file-list="false"
            accept="image/*"
            :disabled="loading"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">
              <p class="primary-text">拖拽图片到此处</p>
              <p class="secondary-text">或点击上传</p>
            </div>
          </el-upload>
        </el-col>
        
        <el-col :span="16">
          <div v-if="previewUrl" class="preview-container">
            <div class="preview-header">
              <span>当前预览：</span>
              <el-tag :type="isEncrypted ? 'success' : 'primary'" size="small">
                {{ isEncrypted ? '加密模式' : '原始模式' }}
              </el-tag>
            </div>
            <img :src="previewUrl" class="preview-image" alt="预览" />
          </div>
          <div v-else class="empty-state">
            <el-icon class="empty-icon"><Picture /></el-icon>
            <p>请选择图像类型并上传以开始分析</p>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <div v-loading="loading" element-loading-text="正在分析..." class="charts-section">
      <el-row :gutter="24">
        <el-col :span="12">
          <div class="chart-card glass-card">
            <div class="chart-header">
              <el-icon><DataLine /></el-icon>
              <h3>直方图分析</h3>
            </div>
            <div ref="histChartRef" class="chart-container"></div>
          </div>
        </el-col>
        
        <el-col :span="12">
          <div class="chart-card glass-card">
            <div class="chart-header">
              <el-icon><ScaleToOriginal /></el-icon>
              <h3>相邻像素相关性</h3>
              <el-radio-group v-model="correlationDirection" size="small" @change="updateCorrelationChart">
                <el-radio-button label="Horizontal">水平</el-radio-button>
                <el-radio-button label="Vertical">垂直</el-radio-button>
                <el-radio-button label="Diagonal">对角</el-radio-button>
              </el-radio-group>
            </div>
            <div ref="corrChartRef" class="chart-container"></div>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="24" class="mt-24">
        <el-col :span="12">
          <div class="chart-card glass-card">
            <div class="chart-header">
              <el-icon><PieChart /></el-icon>
              <h3>信息熵分析</h3>
            </div>
            <div ref="entropyChartRef" class="chart-container"></div>
          </div>
        </el-col>
        
        <el-col :span="12">
          <div class="chart-card glass-card">
            <div class="chart-header">
              <el-icon><DataAnalysis /></el-icon>
              <h3>差分攻击分析</h3>
            </div>
            <div class="differential-metrics">
              <div class="metric-item">
                <span class="metric-label">NPCR (像素变化率)</span>
                <span class="metric-value">{{ differentialData?.npcr || '--' }}%</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">UACI (平均强度变化)</span>
                <span class="metric-value">{{ differentialData?.uaci || '--' }}%</span>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import PageHeader from '@/components/PageHeader.vue';
import request from '@/utils/request';
import { 
  DataAnalysis, 
  Upload, 
  UploadFilled, 
  Picture,
  DataLine,
  ScaleToOriginal,
  PieChart
} from '@element-plus/icons-vue';

const isEncrypted = ref(false);
const previewUrl = ref('');
const loading = ref(false);
const correlationDirection = ref('Horizontal');
const differentialData = ref<any>(null);

const histChartRef = ref<HTMLElement>();
const corrChartRef = ref<HTMLElement>();
const entropyChartRef = ref<HTMLElement>();

let histChart: echarts.ECharts;
let corrChart: echarts.ECharts;
let entropyChart: echarts.ECharts;

onMounted(() => {
  if (histChartRef.value) histChart = echarts.init(histChartRef.value);
  if (corrChartRef.value) corrChart = echarts.init(corrChartRef.value);
  if (entropyChartRef.value) entropyChart = echarts.init(entropyChartRef.value);
});

async function handleUpload({ file }: { file: File }) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('is_encrypted', isEncrypted.value ? 'true' : 'false');
  
  loading.value = true;
  previewUrl.value = URL.createObjectURL(file);
  
  try {
    const data = await request.post('/api/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    updateCharts(data);
    ElMessage.success('分析完成');
  } catch (error) {
    ElMessage.error('分析失败');
  } finally {
    loading.value = false;
  }
}

function updateCharts(data: any) {
  // 更新图表的逻辑
  if (histChart && data.histogram) {
    histChart.setOption({
      backgroundColor: 'transparent',
      grid: { left: '10%', right: '10%', top: '15%', bottom: '15%' },
      xAxis: { type: 'category', data: data.histogram.bins },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: data.histogram.values }]
    });
  }
}

function updateCorrelationChart() {
  // 更新相关性图表
}
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.analysis-page {
  .control-section {
    padding: $spacing-xl;
    margin-bottom: $spacing-xl;
  }
  
  .panel-header {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    margin-bottom: $spacing-lg;
    padding-bottom: $spacing-md;
    border-bottom: 1px solid $border-color;
    
    .header-icon {
      font-size: 24px;
      color: $primary-color;
    }
    
    h3 {
      font-size: 18px;
      font-weight: 600;
      color: $text-primary;
      margin: 0;
    }
  }
  
  .mode-selector {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    margin-bottom: $spacing-lg;
    
    .label-text {
      color: $text-secondary;
      font-size: 14px;
    }
  }
  
  .upload-area {
    :deep(.el-upload) {
      width: 100%;
    }
    
    :deep(.el-upload-dragger) {
      width: 100%;
      padding: $spacing-xl;
      background: rgba(0, 212, 255, 0.03);
      border: 2px dashed $border-color;
      border-radius: $radius-lg;
      
      &:hover {
        border-color: $primary-color;
      }
    }
    
    .upload-icon {
      font-size: 48px;
      color: $primary-color;
      margin-bottom: $spacing-md;
    }
  }
  
  .preview-container {
    height: 100%;
    padding: $spacing-lg;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid $border-color;
    border-radius: $radius-lg;
    
    .preview-header {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      margin-bottom: $spacing-md;
      color: $text-secondary;
    }
    
    .preview-image {
      max-width: 100%;
      max-height: 300px;
      border-radius: $radius-md;
    }
  }
  
  .empty-state {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: $text-secondary;
    
    .empty-icon {
      font-size: 64px;
      color: rgba(255, 255, 255, 0.1);
      margin-bottom: $spacing-md;
    }
  }
  
  .charts-section {
    .mt-24 {
      margin-top: $spacing-xl;
    }
  }
  
  .chart-card {
    padding: $spacing-xl;
    margin-bottom: $spacing-lg;
  }
  
  .chart-header {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    margin-bottom: $spacing-lg;
    
    .el-icon {
      font-size: 20px;
      color: $primary-color;
    }
    
    h3 {
      flex: 1;
      font-size: 16px;
      font-weight: 600;
      color: $text-primary;
      margin: 0;
    }
  }
  
  .chart-container {
    height: 350px;
  }
  
  .differential-metrics {
    display: flex;
    flex-direction: column;
    gap: $spacing-lg;
    padding: $spacing-xl;
    
    .metric-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $spacing-lg;
      background: rgba(0, 212, 255, 0.05);
      border: 1px solid $border-color;
      border-radius: $radius-md;
      
      .metric-label {
        color: $text-secondary;
        font-size: 14px;
      }
      
      .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: $primary-color;
      }
    }
  }
}
</style>
