<template>
  <div class="chaos-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-wrapper">
          <h1 class="page-title">系统动力学</h1>
          <p class="page-subtitle">基于混沌理论的系统动力学特性分析与可视化</p>
        </div>
        
        <div class="header-meta">
          <span class="mode-badge">
            {{ modeLabel }}模式
          </span>
        </div>
      </div>
    </div>

    <div class="chaos-container">
      <!-- Left: Parameters -->
      <div class="params-section">
        <div class="section-card">
          <div class="card-header">
            <h3>参数配置</h3>
          </div>
          
          <div class="params-form">
            <!-- Mode Selection -->
            <div class="form-group">
              <label class="form-label">分析模式</label>
              <div class="mode-selector">
                <button 
                  :class="['mode-btn', { active: form.mode === 'k' }]"
                  @click="handleModeChange('k')"
                >
                  <span class="mode-title">K 变化</span>
                  <span class="mode-desc">固定 A 参数</span>
                </button>
                <button 
                  :class="['mode-btn', { active: form.mode === 'a' }]"
                  @click="handleModeChange('a')"
                >
                  <span class="mode-title">A 变化</span>
                  <span class="mode-desc">固定 K 参数</span>
                </button>
              </div>
            </div>
            
            <!-- Range Settings -->
            <div class="form-group">
              <label class="form-label">扫描范围</label>
              <div class="range-inputs">
                <div class="input-wrapper">
                  <span class="input-label">{{ labels.start }}</span>
                  <el-input-number 
                    v-model="form.start" 
                    :step="0.1" 
                    :precision="3" 
                    size="large"
                    controls-position="right"
                  />
                </div>
                <div class="input-wrapper">
                  <span class="input-label">{{ labels.end }}</span>
                  <el-input-number 
                    v-model="form.end" 
                    :step="0.1" 
                    :precision="3" 
                    size="large"
                    controls-position="right"
                  />
                </div>
              </div>
            </div>
            
            <div class="form-group">
              <label class="form-label">扫描步长</label>
              <el-input-number 
                v-model="form.step" 
                :step="0.001" 
                :precision="4" 
                size="large"
                controls-position="right"
                style="width: 100%"
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">{{ labels.fixed }}</label>
              <el-input-number 
                v-model="form.fixed_val" 
                :step="0.1" 
                :precision="3" 
                size="large"
                controls-position="right"
                style="width: 100%"
              />
            </div>
            
            <button 
              class="analyze-btn"
              @click="startAnalysis" 
              :disabled="loading"
            >
              <el-icon v-if="!loading"><TrendCharts /></el-icon>
              <el-icon v-else class="loading-icon"><Loading /></el-icon>
              <span>{{ loading ? '计算拓扑结构中...' : '开始仿真分析' }}</span>
            </button>
            
            <div class="info-notice">
              <el-icon><InfoFilled /></el-icon>
              <span>高精度步长可能需要较长计算时间</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Visualizations -->
      <div class="viz-section">
        <div v-loading="loading" element-loading-text="正在进行数值迭代与矩阵分解..." class="charts-wrapper">
          <!-- Main Chart -->
          <div class="chart-card main-chart">
            <div class="chart-header">
              <h3>分岔图</h3>
              <span class="chart-subtitle">Bifurcation Diagram</span>
            </div>
            <div ref="bifChartRef" class="chart-canvas large"></div>
          </div>

          <!-- Sub Charts -->
          <div class="sub-charts-grid">
            <div class="chart-card">
              <div class="chart-header">
                <h3>Lyapunov 指数谱</h3>
              </div>
              <div ref="leChartRef" class="chart-canvas normal"></div>
            </div>
            
            <div class="chart-card">
              <div class="chart-header">
                <h3>末态相图</h3>
                <span class="chart-subtitle">Phase Portrait</span>
              </div>
              <div ref="phaseChartRef" class="chart-canvas normal"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import { ElMessage } from 'element-plus';
import { TrendCharts, Loading, InfoFilled } from '@element-plus/icons-vue';
import request from '@/utils/request';

// --- 状态管理 ---
const loading = ref(false);

const form = reactive({
  mode: 'k',       // 'k' 或 'a'
  start: 0.6,
  end: 1.4,
  step: 0.005,
  fixed_val: 0.6,
  iterations: 3000 // 默认迭代次数，前端不暴露但传给后端
});

// --- 计算属性：动态标签 ---
const labels = computed(() => {
  return form.mode === 'k' 
    ? { start: 'K 起始值', end: 'K 终止值', fixed: '固定参数 A' }
    : { start: 'A 起始值', end: 'A 终止值', fixed: '固定参数 K' };
});

const modeLabel = computed(() => form.mode === 'k' ? '变 K' : '变 A');

// --- ECharts 实例引用 ---
const bifChartRef = ref<HTMLElement | null>(null);
const leChartRef = ref<HTMLElement | null>(null);
const phaseChartRef = ref<HTMLElement | null>(null);

let bifChart: echarts.ECharts | null = null;
let leChart: echarts.ECharts | null = null;
let phaseChart: echarts.ECharts | null = null;

// --- 核心逻辑 ---

const handleModeChange = (val: string) => {
  // 更新模式
  form.mode = val;
  
  // 切换模式时重置为典型参数，提升体验
  if (val === 'k') {
    form.start = 0.6; form.end = 1.4; form.fixed_val = 0.6;
  } else {
    form.start = 0.5; form.end = 2.5; form.fixed_val = 0.8;
  }
};

const startAnalysis = async () => {
  loading.value = true;
  try {
    const res = await request.post('/api/chaos_analysis', form);
    // 兼容后端直接返回数据或包裹在 data 中
    const data = res.data.data || res.data || res; 
    console.log('后端返回数据:', data);

    // 渲染三个图表
    renderBifurcation(data.bifurcation);
    renderLyapunov(data.lyapunov);
    renderPhase(data.phase);

    ElMessage.success('混沌分析完成');
  } catch (error) {
    console.error(error);
    ElMessage.error('分析失败，请检查后端服务');
  } finally {
    loading.value = false;
  }
};

// --- 图表渲染函数 ---

// 1. 分岔图
const renderBifurcation = (data: any) => {
  if (!bifChart) return;
  const xAxisName = form.mode.toUpperCase();
  
  bifChart.setOption({
    tooltip: { trigger: 'axis', show: false },
    grid: { left: '5%', right: '5%', bottom: '15%', top: '10%', containLabel: true },
    dataZoom: [
      { type: 'inside' }, 
      { 
        type: 'slider',
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        dataBackground: {
          lineStyle: { color: 'rgba(0, 212, 255, 0.5)' },
          areaStyle: { color: 'rgba(0, 212, 255, 0.2)' }
        },
        fillerColor: 'rgba(0, 212, 255, 0.2)',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        handleStyle: { color: '#00d4ff' },
        moveHandleStyle: { color: '#00d4ff' },
        textStyle: { color: '#ccc' }
      }
    ],
    xAxis: { 
      name: xAxisName, 
      type: 'value', 
      scale: true,
      nameLocation: 'middle',
      nameGap: 25,
      nameTextStyle: { color: '#ccc', fontSize: 13 },
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      axisLabel: { color: '#999' },
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.05)' } }
    },
    yAxis: { 
      name: 'x(n)', 
      scale: true,
      nameTextStyle: { color: '#ccc', fontSize: 13 },
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      axisLabel: { color: '#999' },
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.05)' } }
    },
    series: [{
      type: 'scatter',
      symbolSize: 1.5,
      itemStyle: { color: '#00d4ff', opacity: 0.4 },
      large: true,
      largeThreshold: 2000,
      data: data.x
    }]
  }, true);
};

// 2. Lyapunov 指数谱
const renderLyapunov = (data: any) => {
  if (!leChart) return;
  const xAxisName = form.mode.toUpperCase();

  leChart.setOption({
    tooltip: { 
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'rgba(0, 212, 255, 0.5)',
      textStyle: { color: '#fff' }
    },
    legend: { 
      top: 0,
      textStyle: { color: '#ccc' },
      inactiveColor: 'rgba(255, 255, 255, 0.3)'
    },
    grid: { left: '10%', right: '5%', bottom: '15%', top: '15%', containLabel: true },
    xAxis: { 
      name: xAxisName, 
      type: 'value', 
      scale: true,
      nameTextStyle: { color: '#ccc', fontSize: 13 },
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      axisLabel: { color: '#999' },
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.05)' } }
    },
    yAxis: { 
      name: 'LEs',
      nameTextStyle: { color: '#ccc', fontSize: 13 },
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      axisLabel: { color: '#999' },
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.05)' } }
    },
    series: [
      { 
        name: 'LE1', 
        type: 'line', 
        showSymbol: false, 
        smooth: true,
        lineStyle: { width: 2.5 }, 
        color: '#00d4ff',
        data: data.le1,
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: 'rgba(255, 255, 255, 0.2)', type: 'dashed', width: 1 },
          data: [{ yAxis: 0 }],
          label: { show: false }
        }
      },
      { 
        name: 'LE2', 
        type: 'line', 
        showSymbol: false, 
        smooth: true,
        lineStyle: { width: 2.5 }, 
        color: '#ff6b9d',
        data: data.le2
      }
    ]
  }, true);
};

// 3. 相图
const renderPhase = (data: any) => {
  if (!phaseChart) return;
  
  const scatterData = data.x.map((val: number, i: number) => [val, data.y[i]]);

  phaseChart.setOption({
    tooltip: { 
      trigger: 'item',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'rgba(0, 212, 255, 0.5)',
      textStyle: { color: '#fff' }
    },
    grid: { left: '10%', right: '10%', bottom: '15%', top: '10%', containLabel: true },
    xAxis: { 
      name: 'x(n)', 
      scale: true, 
      splitLine: { show: false },
      nameTextStyle: { color: '#ccc', fontSize: 13 },
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      axisLabel: { color: '#999' }
    },
    yAxis: { 
      name: 'y(n)', 
      scale: true, 
      splitLine: { show: false },
      nameTextStyle: { color: '#ccc', fontSize: 13 },
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      axisLabel: { color: '#999' }
    },
    series: [{
      type: 'scatter',
      symbolSize: 2.5,
      itemStyle: { color: 'rgba(0, 255, 170, 0.6)' },
      data: scatterData
    }]
  }, true);
};

// --- 生命周期与自适应 ---

const initCharts = () => {
  if (bifChartRef.value) bifChart = echarts.init(bifChartRef.value);
  if (leChartRef.value) leChart = echarts.init(leChartRef.value);
  if (phaseChartRef.value) phaseChart = echarts.init(phaseChartRef.value);
};

const handleResize = () => {
  bifChart?.resize();
  leChart?.resize();
  phaseChart?.resize();
};

onMounted(() => {
  nextTick(() => {
    initCharts();
    window.addEventListener('resize', handleResize);
  });
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  bifChart?.dispose();
  leChart?.dispose();
  phaseChart?.dispose();
});
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.chaos-page {
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
        .mode-badge {
          padding: 8px 16px;
          background: rgba(0, 212, 255, 0.1);
          border: 1px solid rgba(0, 212, 255, 0.2);
          border-radius: 8px;
          font-size: 14px;
          color: $primary-color;
          font-weight: 500;
        }
      }
    }
  }
  
  // Main Container
  .chaos-container {
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 32px;
    align-items: start;
  }
  
  // Parameters Section
  .params-section {
    .section-card {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 16px;
      padding: 32px;
      
      .card-header {
        margin-bottom: 32px;
        
        h3 {
          font-size: 18px;
          font-weight: 600;
          color: $text-primary;
          margin: 0;
        }
      }
      
      .params-form {
        .form-group {
          margin-bottom: 28px;
          
          .form-label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: $text-primary;
            margin-bottom: 12px;
          }
        }
        
        // Mode Selector
        .mode-selector {
          display: flex;
          flex-direction: column;
          gap: 12px;
          
          .mode-btn {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            padding: 16px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            
            &:hover {
              background: rgba(255, 255, 255, 0.04);
              border-color: rgba(0, 212, 255, 0.3);
            }
            
            &.active {
              background: rgba(0, 212, 255, 0.08);
              border-color: rgba(0, 212, 255, 0.4);
              
              .mode-title {
                color: $primary-color;
              }
            }
            
            .mode-title {
              font-size: 15px;
              font-weight: 500;
              color: $text-primary;
              margin-bottom: 4px;
              transition: color 0.2s ease;
            }
            
            .mode-desc {
              font-size: 13px;
              color: $text-secondary;
            }
          }
        }
        
        // Range Inputs
        .range-inputs {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
          
          .input-wrapper {
            .input-label {
              display: block;
              font-size: 13px;
              color: $text-secondary;
              margin-bottom: 8px;
            }
            
            :deep(.el-input-number) {
              width: 100%;
              
              .el-input__wrapper {
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
          }
        }
        
        // Input Number Global Style
        :deep(.el-input-number) {
          .el-input__wrapper {
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
        
        // Analyze Button
        .analyze-btn {
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
          margin-top: 12px;
          
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
        
        // Info Notice
        .info-notice {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 12px;
          background: rgba(0, 212, 255, 0.05);
          border: 1px solid rgba(0, 212, 255, 0.15);
          border-radius: 8px;
          margin-top: 20px;
          
          .el-icon {
            color: $primary-color;
            font-size: 16px;
            flex-shrink: 0;
          }
          
          span {
            font-size: 13px;
            color: $text-secondary;
            line-height: 1.5;
          }
        }
      }
    }
  }
  
  // Visualization Section
  .viz-section {
    .charts-wrapper {
      display: flex;
      flex-direction: column;
      gap: 24px;
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
        
        .chart-subtitle {
          font-size: 13px;
          color: $text-secondary;
          font-weight: 400;
        }
      }
      
      .chart-canvas {
        width: 100%;
        
        &.large {
          height: 400px;
        }
        
        &.normal {
          height: 320px;
        }
      }
    }
    
    .sub-charts-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 24px;
    }
  }
}

// Animations
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// Responsive
@media (max-width: 1024px) {
  .chaos-page {
    .chaos-container {
      grid-template-columns: 1fr;
    }
    
    .viz-section .sub-charts-grid {
      grid-template-columns: 1fr;
    }
  }
}

@media (max-width: 768px) {
  .chaos-page {
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
    
    .params-section .section-card,
    .viz-section .chart-card {
      padding: 20px;
    }
    
    .params-section .params-form .range-inputs {
      grid-template-columns: 1fr;
    }
  }
}
</style>