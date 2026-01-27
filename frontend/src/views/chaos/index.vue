<template>
  <div class="chaos-analysis-page">
    <div class="page-header">混沌特性多维展示</div>
    
    <el-row :gutter="20">
      
      <el-col :span="6">
        <el-card class="control-card">
          <template #header>
            <div class="card-header">
              <span>参数设置</span>
              <el-tag size="small" effect="plain">{{ modeLabel }}模式</el-tag>
            </div>
          </template>

          <el-form :model="form" label-position="top" size="default">
            
            <el-form-item label="分析模式 (控制变量)">
              <el-radio-group v-model="form.mode" @change="handleModeChange" class="mode-group">
                <el-radio-button label="k">K 变化 (固定 A)</el-radio-button>
                <el-radio-button label="a">A 变化 (固定 K)</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <el-divider content-position="center">扫描范围</el-divider>

            <el-row :gutter="10">
              <el-col :span="12">
                <el-form-item :label="labels.start">
                  <el-input-number v-model="form.start" :step="0.1" :precision="3" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item :label="labels.end">
                  <el-input-number v-model="form.end" :step="0.1" :precision="3" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="扫描步长 (Step)">
              <el-input-number v-model="form.step" :step="0.001" :precision="4" style="width: 100%" />
            </el-form-item>

            <el-divider content-position="center">系统常量</el-divider>

            <el-form-item :label="labels.fixed">
              <el-input-number v-model="form.fixed_val" :step="0.1" :precision="3" style="width: 100%" />
            </el-form-item>

            <el-form-item class="mt-20">
              <el-button 
                type="primary" 
                @click="startAnalysis" 
                :loading="loading" 
                class="full-width-btn"
                size="large"
              >
                {{ loading ? '正在计算拓扑结构...' : '开始仿真分析' }}
              </el-button>
            </el-form-item>

          </el-form>
        </el-card>
        
        <div class="info-tip">
          <small>* 计算量较大，高精度步长可能需要几秒钟。</small>
        </div>
      </el-col>

      <el-col :span="18">
        <el-card header="可视化区域" class="viz-card" body-style="padding: 10px;">
          
          <div v-loading="loading" element-loading-text="正在进行数值迭代与矩阵分解...">
            
            <div class="chart-container main-chart">
              <div class="chart-title">分岔图 (Bifurcation Diagram)</div>
              <div ref="bifChartRef" class="echart-box large"></div>
            </div>

            <el-row :gutter="10" class="mt-10">
              <el-col :span="12">
                <div class="chart-container sub-chart">
                  <div class="chart-title">Lyapunov 指数谱</div>
                  <div ref="leChartRef" class="echart-box normal"></div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="chart-container sub-chart">
                  <div class="chart-title">末态相图 (Phase Portrait)</div>
                  <div ref="phaseChartRef" class="echart-box normal"></div>
                </div>
              </el-col>
            </el-row>

          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import { ElMessage } from 'element-plus';
import request from '@/utils/request'; // 确保路径正确

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
    tooltip: { trigger: 'axis', show: false }, // 数据量大时关闭 tooltip 提升性能
    grid: { left: '5%', right: '5%', bottom: '15%', top: '10%' },
    dataZoom: [{ type: 'inside' }, { type: 'slider' }], // 支持缩放查看细节
    xAxis: { 
      name: xAxisName, 
      type: 'value', 
      scale: true,
      nameLocation: 'middle',
      nameGap: 25 
    },
    yAxis: { name: 'x(n)', scale: true },
    series: [{
      type: 'scatter',
      symbolSize: 1.5,
      itemStyle: { color: '#000', opacity: 0.6 },
      large: true, // 开启大数据量优化
      largeThreshold: 2000,
      data: data.x // 后端已组装好 [[x, y], [x, y]] 格式
    }]
  }, true);
};

// 2. Lyapunov 指数谱
const renderLyapunov = (data: any) => {
  if (!leChart) return;
  const xAxisName = form.mode.toUpperCase();

  leChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { top: 0 },
    grid: { left: '10%', right: '5%', bottom: '15%', top: '15%' },
    xAxis: { name: xAxisName, type: 'value', scale: true },
    yAxis: { name: 'LEs' },
    // 添加 y=0 参考线
    markLine: {
      data: [{ yAxis: 0 }],
      symbol: 'none',
      lineStyle: { color: '#999', type: 'dashed' }
    },
    series: [
      { 
        name: 'LE1', type: 'line', showSymbol: false, smooth: true,
        lineStyle: { width: 1.5 }, color: '#409EFF',
        data: data.le1 
      },
      { 
        name: 'LE2', type: 'line', showSymbol: false, smooth: true,
        lineStyle: { width: 1.5 }, color: '#F56C6C',
        data: data.le2 
      }
    ]
  }, true);
};

// 3. 相图
const renderPhase = (data: any) => {
  if (!phaseChart) return;
  
  // 转换数据格式：x:[], y:[] -> [[x,y], ...]
  const scatterData = data.x.map((val: number, i: number) => [val, data.y[i]]);

  phaseChart.setOption({
    tooltip: { trigger: 'item' },
    grid: { left: '10%', right: '10%', bottom: '15%', top: '15%' },
    xAxis: { name: 'x(n)', scale: true, splitLine: { show: false } },
    yAxis: { name: 'y(n)', scale: true, splitLine: { show: false } },
    series: [{
      type: 'scatter',
      symbolSize: 2,
      itemStyle: { color: 'rgba(64, 158, 255, 0.6)' },
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

<style scoped>
.chaos-analysis-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.page-header {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  border-left: 5px solid #409EFF;
  padding-left: 10px;
}
.control-card {
  height: 100%;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.mode-group {
  width: 100%;
  display: flex;
}
.mode-group :deep(.el-radio-button) {
  flex: 1;
}
.mode-group :deep(.el-radio-button__inner) {
  width: 100%;
}

.full-width-btn {
  width: 100%;
  font-weight: bold;
}
.mt-20 { margin-top: 20px; }
.mt-10 { margin-top: 10px; }

.info-tip {
  margin-top: 10px;
  color: #909399;
  text-align: center;
}

/* 图表容器样式 */
.chart-container {
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  padding: 10px;
  position: relative;
}
.chart-title {
  font-size: 14px;
  font-weight: bold;
  color: #606266;
  margin-bottom: 10px;
  text-align: center;
}
.echart-box {
  width: 100%;
}
.echart-box.large {
  height: 350px; /* 分岔图高度 */
}
.echart-box.normal {
  height: 280px; /* 下方两个图的高度 */
}
</style>