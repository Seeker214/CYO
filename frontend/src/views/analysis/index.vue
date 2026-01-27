<template>
  <div class="analysis-container">
    <div class="page-header">
      <span>加密图像安全性分析</span>
    </div>

    <el-card shadow="hover" class="mb-20">
      <div class="upload-section">
        <el-row :gutter="20" align="top">
          <el-col :span="8">
            
            <div class="control-panel mb-15">
              <span class="label-text">图像类型：</span>
              <el-switch
                v-model="isEncrypted"
                size="large"
                inline-prompt
                active-text="加密后文件"
                inactive-text="原始图像"
                active-color="#13ce66"
                inactive-color="#409eff"
              />
            </div>

            <el-upload
              class="upload-demo"
              drag
              action=""
              :http-request="handleUpload"
              :show-file-list="false"
              accept="image/*"
              :disabled="loading"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽图片到此处 或 <em>点击上传</em>
              </div>
            </el-upload>
          </el-col>
          
          <el-col :span="16">
            <div v-if="previewUrl" class="preview-container">
              <div class="preview-info">
                <span class="label">当前预览：</span>
                <el-tag :type="isEncrypted ? 'success' : 'primary'" size="small">
                  {{ isEncrypted ? '加密模式' : '原始模式' }}
                </el-tag>
              </div>
              <el-image 
                :src="previewUrl" 
                fit="contain" 
                class="preview-image"
                :preview-src-list="[previewUrl]"
              />
            </div>
            <div v-else class="empty-tip">
              请选择图像类型并上传以开始分析
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <div v-loading="loading" element-loading-text="正在进行数学特征计算..." class="charts-area">
       <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover">
             <template #header><span>直方图分析</span></template>
             <div ref="histChartRef" style="height: 350px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header-tabs">
                <span>相邻像素相关性</span>
                <el-radio-group v-model="correlationDirection" size="small" @change="updateCorrelationChart">
                  <el-radio-button label="Horizontal">水平</el-radio-button>
                  <el-radio-button label="Vertical">垂直</el-radio-button>
                  <el-radio-button label="Diagonal">对角</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div ref="corrChartRef" style="height: 350px;"></div>
          </el-card>
        </el-col>
      </el-row>
      <el-row :gutter="20" class="mt-20">
         <el-col :span="12">
            <el-card shadow="hover">
               <template #header><span>信息熵分析</span></template>
               <div ref="entropyChartRef" style="height: 300px;"></div>
            </el-card>
         </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { UploadFilled } from '@element-plus/icons-vue'; 
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
</script>

<style scoped>
.analysis-container { padding: 20px; }
.page-header { font-size: 24px; font-weight: 600; margin-bottom: 20px; color: #303133; }
.mb-20 { margin-bottom: 20px; }
.mb-15 { margin-bottom: 15px; }
.mr-10 { margin-right: 10px; }
.mt-20 { margin-top: 20px; }

/* 控件面板样式 */
.control-panel {
  display: flex;
  align-items: center;
}
.label-text {
  font-size: 14px;
  font-weight: bold;
  color: #606266;
  margin-right: 12px;
}

/* 预览区域样式调整 */
.preview-container {
  display: flex;
  flex-direction: column; 
  gap: 10px;
  height: 180px;
}
.preview-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.preview-image {
  max-height: 140px; 
  max-width: 100%;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  padding: 4px;
  align-self: flex-start;
}
.empty-tip {
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  background: #f5f7fa;
  border-radius: 4px;
}
.card-header-tabs { display: flex; justify-content: space-between; align-items: center; }
.correlation-score { text-align: center; margin-top: 10px; font-size: 14px; color: #606266; }
</style>