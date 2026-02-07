<template>
  <div class="chaos-page">
    <PageHeader 
      title="系统动力学"
      subtitle="混沌特性多维展示与分岔分析"
      :icon="TrendCharts"
    />
    
    <el-row :gutter="24">
      <el-col :span="6">
        <div class="control-panel glass-card">
          <div class="panel-header">
            <el-icon class="header-icon"><Setting /></el-icon>
            <h3>参数设置</h3>
            <el-tag size="small">{{ modeLabel }}模式</el-tag>
          </div>
          
          <el-form :model="form" label-position="top">
            <el-form-item label="分析模式">
              <el-radio-group v-model="form.mode" @change="handleModeChange" class="mode-group">
                <el-radio-button label="k">K 变化</el-radio-button>
                <el-radio-button label="a">A 变化</el-radio-button>
              </el-radio-group>
            </el-form-item>
            
            <el-divider>扫描范围</el-divider>
            
            <el-row :gutter="12">
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
            
            <el-form-item label="扫描步长">
              <el-input-number v-model="form.step" :step="0.001" :precision="4" style="width: 100%" />
            </el-form-item>
            
            <el-divider>系统常量</el-divider>
            
            <el-form-item :label="labels.fixed">
              <el-input-number v-model="form.fixed_val" :step="0.1" :precision="3" style="width: 100%" />
            </el-form-item>
            
            <el-button 
              type="primary" 
              @click="startAnalysis" 
              :loading="loading"
              size="large"
              style="width: 100%"
            >
              {{ loading ? '计算中...' : '开始仿真分析' }}
            </el-button>
          </el-form>
          
          <div class="info-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>计算量较大，高精度步长可能需要几秒钟。</span>
          </div>
        </div>
      </el-col>
      
      <el-col :span="18">
        <div v-loading="loading" element-loading-text="正在计算...">
          <div class="chart-card glass-card">
            <div class="chart-header">
              <el-icon><TrendCharts /></el-icon>
              <h3>分岔图 (Bifurcation Diagram)</h3>
            </div>
            <div ref="bifChartRef" class="chart-container large"></div>
          </div>
          
          <el-row :gutter="24" class="mt-24">
            <el-col :span="12">
              <div class="chart-card glass-card">
                <div class="chart-header">
                  <el-icon><DataLine /></el-icon>
                  <h3>Lyapunov 指数谱</h3>
                </div>
                <div ref="leChartRef" class="chart-container"></div>
              </div>
            </el-col>
            
            <el-col :span="12">
              <div class="chart-card glass-card">
                <div class="chart-header">
                  <el-icon><ScaleToOriginal /></el-icon>
                  <h3>末态相图 (Phase Portrait)</h3>
                </div>
                <div ref="phaseChartRef" class="chart-container"></div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import PageHeader from '@/components/PageHeader.vue';
import request from '@/utils/request';
import { 
  TrendCharts, 
  Setting, 
  InfoFilled,
  DataLine,
  ScaleToOriginal
} from '@element-plus/icons-vue';

const form = ref({
  mode: 'k',
  start: 0.1,
  end: 4.0,
  step: 0.01,
  fixed_val: 3.5
});

const loading = ref(false);

const labels = computed(() => {
  if (form.value.mode === 'k') {
    return { start: 'K 起始', end: 'K 终止', fixed: '固定 A 值' };
  } else {
    return { start: 'A 起始', end: 'A 终止', fixed: '固定 K 值' };
  }
});

const modeLabel = computed(() => {
  return form.value.mode === 'k' ? 'K变化' : 'A变化';
});

const bifChartRef = ref<HTMLElement>();
const leChartRef = ref<HTMLElement>();
const phaseChartRef = ref<HTMLElement>();

let bifChart: echarts.ECharts;
let leChart: echarts.ECharts;
let phaseChart: echarts.ECharts;

onMounted(() => {
  if (bifChartRef.value) bifChart = echarts.init(bifChartRef.value);
  if (leChartRef.value) leChart = echarts.init(leChartRef.value);
  if (phaseChartRef.value) phaseChart = echarts.init(phaseChartRef.value);
});

function handleModeChange() {
  // 模式切换逻辑
}

async function startAnalysis() {
  loading.value = true;
  
  try {
    const data = await request.post('/api/chaos/analyze', form.value);
    updateCharts(data);
    ElMessage.success('分析完成');
  } catch (error) {
    ElMessage.error('分析失败');
  } finally {
    loading.value = false;
  }
}

function updateCharts(data: any) {
  // 更新图表逻辑
  if (bifChart && data.bifurcation) {
    bifChart.setOption({
      backgroundColor: 'transparent',
      grid: { left: '10%', right: '10%', top: '10%', bottom: '10%' },
      xAxis: { type: 'value' },
      yAxis: { type: 'value' },
      series: [{
        type: 'scatter',
        data: data.bifurcation,
        symbolSize: 1
      }]
    });
  }
}
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.chaos-page {
  .control-panel {
    padding: $spacing-xl;
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
      flex: 1;
      font-size: 18px;
      font-weight: 600;
      color: $text-primary;
      margin: 0;
    }
  }
  
  .mode-group {
    width: 100%;
    
    :deep(.el-radio-button) {
      flex: 1;
    }
  }
  
  .info-tip {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    padding: $spacing-md;
    margin-top: $spacing-lg;
    background: rgba(0, 212, 255, 0.08);
    border: 1px solid $border-color;
    border-radius: $radius-md;
    color: $text-secondary;
    font-size: 12px;
    
    .el-icon {
      color: $primary-color;
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
      font-size: 16px;
      font-weight: 600;
      color: $text-primary;
      margin: 0;
    }
  }
  
  .chart-container {
    height: 300px;
    
    &.large {
      height: 400px;
    }
  }
  
  .mt-24 {
    margin-top: $spacing-xl;
  }
}
</style>
