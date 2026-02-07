<template>
  <div class="analysis-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-wrapper">
          <h1 class="page-title">图像安全性分析</h1>
          <p class="page-subtitle">对加密图像进行多维度安全性评估与可视化分析</p>
        </div>
      </div>
    </div>

    <!-- Upload Section -->
    <div class="upload-section">
      <div class="section-card">
        <div class="upload-grid">
          <!-- Left: Controls -->
          <div class="controls-area">
            <div class="control-group">
              <label class="control-label">图像类型</label>
              <div class="switch-wrapper">
                <el-switch
                  v-model="isEncrypted"
                  size="large"
                  inline-prompt
                  active-text="加密后"
                  inactive-text="原始图像"
                  active-color="#00ffaa"
                  inactive-color="#00d4ff"
                />
              </div>
            </div>

            <div class="upload-zone">
              <el-upload
                class="upload-area"
                drag
                action=""
                :http-request="handleUpload"
                :show-file-list="false"
                accept="image/*"
                :disabled="loading"
              >
                <div class="upload-content">
                  <el-icon class="upload-icon"><upload-filled /></el-icon>
                  <div class="upload-text">
                    <p class="main-text">拖拽图片到此处或点击上传</p>
                    <p class="sub-text">支持 JPG、PNG 格式</p>
                  </div>
                </div>
              </el-upload>
            </div>
          </div>
          
          <!-- Right: Preview -->
          <div class="preview-area">
            <div v-if="previewUrl" class="preview-wrapper">
              <div class="preview-header">
                <span class="preview-label">图像预览</span>
                <span :class="['mode-badge', isEncrypted ? 'encrypted' : 'original']">
                  {{ isEncrypted ? '加密模式' : '原始模式' }}
                </span>
              </div>
              <div class="preview-image-container">
                <el-image 
                  :src="previewUrl" 
                  fit="contain" 
                  class="preview-image"
                  :preview-src-list="[previewUrl]"
                />
              </div>
            </div>
            <div v-else class="preview-empty">
              <el-icon class="empty-icon"><Picture /></el-icon>
              <p class="empty-text">未上传图像</p>
              <p class="empty-hint">请选择图像类型并上传以开始分析</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div v-loading="loading" element-loading-text="正在进行数学特征计算..." class="charts-section">
      <div class="charts-grid">
        <!-- Histogram -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>直方图分析</h3>
          </div>
          <div ref="histChartRef" class="chart-container"></div>
        </div>
        
        <!-- Correlation -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>相邻像素相关性</h3>
            <el-radio-group v-model="correlationDirection" size="small" @change="updateCorrelationChart">
              <el-radio-button label="Horizontal">水平</el-radio-button>
              <el-radio-button label="Vertical">垂直</el-radio-button>
              <el-radio-button label="Diagonal">对角</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="corrChartRef" class="chart-container"></div>
        </div>
      </div>
      
      <div class="charts-grid">
        <!-- Entropy -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>信息熵分析</h3>
          </div>
          <div ref="entropyChartRef" class="chart-container entropy-chart"></div>
        </div>
        
        <!-- Differential Analysis -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>差分攻击分析</h3>
          </div>
          <div class="differential-container">
            <div v-if="differentialData" class="diff-metrics">
              <div class="metric-card">
                <div class="metric-header">NPCR</div>
                <div class="metric-desc">像素变化率</div>
                <div class="metric-value" :class="getNpcrClass(differentialData.npcr)">
                  {{ differentialData.npcr }}%
                </div>
                <div class="metric-ideal">理想值: {{ differentialData.npcr_ideal }}%</div>
                <div class="metric-badge" :class="getNpcrClass(differentialData.npcr)">
                  {{ getNpcrStatus(differentialData.npcr) }}
                </div>
              </div>
              
              <div class="metric-divider"></div>
              
              <div class="metric-card">
                <div class="metric-header">UACI</div>
                <div class="metric-desc">平均变化强度</div>
                <div class="metric-value" :class="getUaciClass(differentialData.uaci)">
                  {{ differentialData.uaci }}%
                </div>
                <div class="metric-ideal">理想值: {{ differentialData.uaci_ideal }}%</div>
                <div class="metric-badge" :class="getUaciClass(differentialData.uaci)">
                  {{ getUaciStatus(differentialData.uaci) }}
                </div>
              </div>
            </div>
            <div v-else class="diff-empty">
              <el-icon class="empty-icon"><InfoFilled /></el-icon>
              <p class="empty-text">仅在上传原始图像时进行差分攻击分析</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { UploadFilled, Picture, InfoFilled } from '@element-plus/icons-vue'; 
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import request from '@/utils/request'; 

// --- 状态定义 ---
const loading = ref(false);
const previewUrl = ref('');
const uploadedFileName = ref('');
const fullAnalysisData = ref<any>(null);
const correlationDirection = ref('Horizontal');
const currentCorrelationValue = ref<number | null>(null);
const differentialData = ref<any>(null);

// [新增] 定义是否加密的布尔变量，默认为 false (原始图像)
const isEncrypted = ref(false);

// Charts Refs
const histChartRef = ref<HTMLElement | null>(null);
const corrChartRef = ref<HTMLElement | null>(null);
const entropyChartRef = ref<HTMLElement | null>(null);

let histChart: echarts.ECharts | null = null;
let corrChart: echarts.ECharts | null = null;
let entropyChart: echarts.ECharts | null = null;

// --- 生命周期 ---
onMounted(() => {
  initCharts();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  histChart?.dispose();
  corrChart?.dispose();
  entropyChart?.dispose();
});

const handleResize = () => {
  histChart?.resize();
  corrChart?.resize();
  entropyChart?.resize();
};

const initCharts = () => {
  if (histChartRef.value) histChart = echarts.init(histChartRef.value);
  if (corrChartRef.value) corrChart = echarts.init(corrChartRef.value);
  if (entropyChartRef.value) entropyChart = echarts.init(entropyChartRef.value);
};

// --- 核心业务逻辑 ---

const handleUpload = async (options: any) => {
  const { file } = options;
  
  previewUrl.value = URL.createObjectURL(file);
  uploadedFileName.value = file.name;
  
  const formData = new FormData();
  formData.append('file', file);
  
  // [新增] 将 bool 值传入后端
  // 注意：FormData 传输时会将 true 变为字符串 "true"
  // FastAPI 可以自动识别 "true"/"false" 为 bool 类型
  formData.append('is_encrypted', String(isEncrypted.value));

  loading.value = true;

  try {
    const res = await request.post('/api/analyze_image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    const responseData = res.data || res; 

    if (responseData) {
      fullAnalysisData.value = responseData;
      
      // 如果后端根据 is_encrypted 做了特殊处理（例如期望的熵值范围不同），
      // 这里前端展示逻辑不需要变，只负责渲染数据
      renderHistogram(responseData.histogram);
      renderEntropy(responseData.entropy);
      correlationDirection.value = 'Horizontal';
      updateCorrelationChart();
      differentialData.value = responseData.differential || null;
      
      ElMessage.success(`分析完成 (${isEncrypted.value ? '加密模式' : '原始模式'})`);
    }
  } catch (error) {
    console.error(error);
    ElMessage.error('分析失败');
  } finally {
    loading.value = false;
  }
};

// --- 图表渲染逻辑 (保持之前的代码不变) ---
/**
 * 渲染直方图 (修改为柱状图/矩形样式)
 */
const renderHistogram = (histData: Record<string, number[]>) => {
  if (!histChart) return;

  const series = [];
  const colors: Record<string, string> = { 
    'Red': '#ff4d4f', 
    'Green': '#52c41a', 
    'Blue': '#1890ff', 
    'Gray': '#666' 
  };

  for (const [key, data] of Object.entries(histData)) {
    series.push({
      name: key,
      type: 'bar', // 核心修改：改为柱状图
      barCategoryGap: '0%', // 核心修改：让柱子之间没有间隙，形成连续的直方图
      barGap: '-100%', // 如果是多通道，让它们重叠显示而不是并排显示（避免柱子变得极细）
      itemStyle: { 
        color: colors[key] || '#000',
        opacity: 0.6 // 设置透明度，这样红绿蓝重叠时能看到混合色，而不是互相覆盖
      },
      data: data,
      // 优化渲染性能
      large: true 
    });
  }

  histChart.setOption({
    tooltip: { 
      trigger: 'axis',
      axisPointer: { type: 'shadow' } // 鼠标悬停时显示阴影指示器
    },
    legend: { data: Object.keys(histData), top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '30px', containLabel: true },
    xAxis: { 
      type: 'category', 
      data: Array.from({ length: 256 }, (_, i) => i),
      name: '像素值',
      nameLocation: 'middle',
      nameGap: 25,
      axisTick: { alignWithLabel: true }
    },
    yAxis: { 
      type: 'value',
      name: '频数'
    },
    series: series
  }, true); // true 表示不合并旧数据，彻底重绘
};

const updateCorrelationChart = () => {
  if (!corrChart || !fullAnalysisData.value) return;
  const direction = correlationDirection.value;
  const dataObj = fullAnalysisData.value.correlation[direction];
  currentCorrelationValue.value = dataObj.correlation_coefficient;
  const scatterData = dataObj.plot_data.x.map((val: number, index: number) => [val, dataObj.plot_data.y[index]]);
  corrChart.setOption({
    tooltip: { trigger: 'item', formatter: (p: any) => `(${p.value[0]}, ${p.value[1]})` },
    grid: { left: '5%', right: '10%', bottom: '10%', top: '15%', containLabel: true },
    xAxis: { type: 'value', name: 'Pixel(x,y)', min: 0, max: 255, splitLine: { show: false } },
    yAxis: { type: 'value', name: 'Neighbor', min: 0, max: 255, splitLine: { show: false } },
    series: [{ symbolSize: 2, data: scatterData, type: 'scatter', itemStyle: { color: 'rgba(64, 158, 255, 0.5)' } }]
  }, true);
};

const renderEntropy = (entropyVal: number) => {
  if (!entropyChart) return;
  entropyChart.setOption({
    series: [{
      type: 'gauge', min: 0, max: 8,
      axisLine: { lineStyle: { width: 12, color: [[0.3, '#ff4d4f'], [0.7, '#faad14'], [1, '#52c41a']] } },
      pointer: { length: '60%' }, detail: { formatter: '{value}', fontSize: 24, offsetCenter: [0, '70%'] },
      data: [{ value: entropyVal, name: 'Entropy' }]
    }]
  });
};

// 差分攻击状态判断函数
const getNpcrStatus = (npcr: number) => {
  if (npcr >= 99.5) return '优秀';
  if (npcr >= 99.0) return '良好';
  return '待改进';
};

const getUaciStatus = (uaci: number) => {
  if (uaci >= 32.0 && uaci <= 35.0) return '优秀';
  if (uaci >= 30.0 && uaci <= 37.0) return '良好';
  return '待改进';
};

const getNpcrClass = (npcr: number) => {
  if (npcr >= 99.5) return 'status-excellent';
  if (npcr >= 99.0) return 'status-good';
  return 'status-poor';
};

const getUaciClass = (uaci: number) => {
  if (uaci >= 32.0 && uaci <= 35.0) return 'status-excellent';
  if (uaci >= 30.0 && uaci <= 37.0) return 'status-good';
  return 'status-poor';
};
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.analysis-page {
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
  
  // Upload Section
  .upload-section {
    margin-bottom: 48px;
    
    .section-card {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 16px;
      padding: 32px;
    }
    
    .upload-grid {
      display: grid;
      grid-template-columns: 400px 1fr;
      gap: 32px;
    }
    
    .controls-area {
      .control-group {
        margin-bottom: 24px;
        
        .control-label {
          display: block;
          font-size: 14px;
          font-weight: 500;
          color: $text-primary;
          margin-bottom: 12px;
        }
        
        .switch-wrapper {
          :deep(.el-switch) {
            height: 40px;
          }
        }
      }
      
      .upload-zone {
        :deep(.el-upload) {
          width: 100%;
        }
        
        :deep(.el-upload-dragger) {
          width: 100%;
          padding: 48px 24px;
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
          .upload-icon {
            font-size: 48px;
            color: $text-secondary;
            margin-bottom: 16px;
            transition: all 0.3s ease;
          }
          
          .upload-text {
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
    }
    
    .preview-area {
      display: flex;
      flex-direction: column;
      
      .preview-wrapper {
        .preview-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
          
          .preview-label {
            font-size: 14px;
            font-weight: 500;
            color: $text-primary;
          }
          
          .mode-badge {
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            
            &.encrypted {
              background: rgba(0, 255, 170, 0.1);
              border: 1px solid rgba(0, 255, 170, 0.2);
              color: $accent-color;
            }
            
            &.original {
              background: rgba(0, 212, 255, 0.1);
              border: 1px solid rgba(0, 212, 255, 0.2);
              color: $primary-color;
            }
          }
        }
        
        .preview-image-container {
          background: rgba(0, 0, 0, 0.2);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 12px;
          padding: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          height: 350px;
          overflow: hidden;
          
          :deep(.el-image) {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            
            img {
              max-width: 100%;
              max-height: 100%;
              width: auto;
              height: auto;
              object-fit: contain;
              border-radius: 8px;
            }
          }
        }
      }
      
      .preview-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 48px 24px;
        text-align: center;
        min-height: 300px;
        
        .empty-icon {
          font-size: 64px;
          color: rgba(255, 255, 255, 0.08);
          margin-bottom: 16px;
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
    }
  }
  
  // Charts Section
  .charts-section {
    .charts-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 24px;
      margin-bottom: 24px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    .chart-card {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 16px;
      padding: 24px;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: rgba(0, 212, 255, 0.2);
      }
      
      .chart-header {
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
        
        :deep(.el-radio-group) {
          .el-radio-button__inner {
            background: rgba(255, 255, 255, 0.02);
            border-color: rgba(255, 255, 255, 0.1);
            color: $text-secondary;
            padding: 6px 12px;
            font-size: 13px;
          }
          
          .el-radio-button__original-radio:checked + .el-radio-button__inner {
            background: rgba(0, 212, 255, 0.15);
            border-color: rgba(0, 212, 255, 0.4);
            color: $primary-color;
          }
        }
      }
      
      .chart-container {
        height: 350px;
        
        &.entropy-chart {
          height: 300px;
        }
      }
      
      // Differential Analysis
      .differential-container {
        height: 350px;
        display: flex;
        align-items: center;
        justify-content: center;
        
        .diff-metrics {
          display: flex;
          align-items: stretch;
          justify-content: space-around;
          width: 100%;
          gap: 32px;
          
          .metric-card {
            flex: 1;
            text-align: center;
            padding: 24px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            
            .metric-header {
              font-size: 14px;
              font-weight: 600;
              color: $text-primary;
              text-transform: uppercase;
              letter-spacing: 0.05em;
              margin-bottom: 4px;
            }
            
            .metric-desc {
              font-size: 13px;
              color: $text-secondary;
              margin-bottom: 20px;
            }
            
            .metric-value {
              font-size: 36px;
              font-weight: 700;
              margin-bottom: 12px;
              font-family: 'SF Mono', 'Monaco', monospace;
              
              &.status-excellent {
                color: $accent-color;
              }
              
              &.status-good {
                color: #E6A23C;
              }
              
              &.status-poor {
                color: #F56C6C;
              }
            }
            
            .metric-ideal {
              font-size: 12px;
              color: rgba(255, 255, 255, 0.4);
              margin-bottom: 16px;
            }
            
            .metric-badge {
              display: inline-block;
              padding: 6px 14px;
              border-radius: 6px;
              font-size: 13px;
              font-weight: 500;
              
              &.status-excellent {
                background: rgba(0, 255, 170, 0.1);
                border: 1px solid rgba(0, 255, 170, 0.2);
                color: $accent-color;
              }
              
              &.status-good {
                background: rgba(230, 162, 60, 0.1);
                border: 1px solid rgba(230, 162, 60, 0.2);
                color: #E6A23C;
              }
              
              &.status-poor {
                background: rgba(245, 108, 108, 0.1);
                border: 1px solid rgba(245, 108, 108, 0.2);
                color: #F56C6C;
              }
            }
          }
          
          .metric-divider {
            width: 1px;
            background: rgba(255, 255, 255, 0.06);
          }
        }
        
        .diff-empty {
          text-align: center;
          
          .empty-icon {
            font-size: 48px;
            color: rgba(255, 255, 255, 0.1);
            margin-bottom: 16px;
          }
          
          .empty-text {
            font-size: 14px;
            color: $text-secondary;
            margin: 0;
          }
        }
      }
    }
  }
}

// Responsive
@media (max-width: 1024px) {
  .analysis-page {
    .upload-section .upload-grid {
      grid-template-columns: 1fr;
    }
    
    .charts-section .charts-grid {
      grid-template-columns: 1fr;
    }
  }
}

@media (max-width: 768px) {
  .analysis-page {
    padding: 0 20px;
    
    .page-header {
      padding: 32px 0 36px;
      margin-bottom: 32px;
      
      .title-wrapper .page-title {
        font-size: 32px;
      }
    }
    
    .upload-section .section-card,
    .charts-section .chart-card {
      padding: 20px;
    }
  }
}
</style>