<template>
  <div class="dashboard">
    <!-- 标题区 -->
    <div class="title-area">
      <div class="title">核心功能</div>
      <div class="title-underline"></div>
    </div>
    <!-- 功能区 -->
    <el-row :gutter="40" class="features-row">
      <el-col
        v-for="feature in features"
        :key="feature.title"
        :span="8"
        class="feature-col"
      >
        <div class="feature-card" @click="go(feature.route)">
          <div class="icon-wrap">
            <el-icon :size="32" class="feature-icon">
              <component :is="feature.icon" />
            </el-icon>
          </div>
          <div class="feature-info">
            <div class="feature-title">{{ feature.title }}</div>
            <div class="feature-desc">{{ feature.description }}</div>
          </div>
        </div>
      </el-col>
    </el-row>
    <!-- 底部数据横幅 -->
    <div class="banner">
      <div class="banner-item">
        <div class="banner-num">2<sup>256</sup></div>
        <div class="banner-label">密钥空间</div>
      </div>
      <div class="banner-item">
        <div class="banner-num">99.9%</div>
        <div class="banner-label">信息熵</div>
      </div>
      <div class="banner-item">
        <div class="banner-num">0.01</div>
        <div class="banner-label">像素相关性</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Aim, DataAnalysis, Lock, Unlock, TrendCharts, Setting } from '@element-plus/icons-vue'

const router = useRouter()
const features = [
  {
    title: '目标识别',
    description: '基于 YOLOv9 的图像目标检测与识别',
    icon: Aim,
    route: '/detection'
  },
  {
    title: '明文图像数据分析',
    description: '图像数据的 3D 可视化分析',
    icon: DataAnalysis,
    route: '/analysis'
  },
  {
    title: '加密',
    description: '图像加密与隐私保护',
    icon: Lock,
    route: '/encryption'
  },
  {
    title: '解密',
    description: '加密图像的解密与恢复',
    icon: Unlock,
    route: '/decryption'
  },
  {
    title: '系统动力学分析',
    description: '系统性能与动力学分析',
    icon: TrendCharts,
    route: '/dynamics'
  },
  {
    title: '设置',
    description: '个性化配置与系统参数设置',
    icon: Setting,
    route: '/settings'
  }
]

function go(route: string) {
  router.push(route)
}
</script>

<style scoped>
.dashboard {
  background: #fff;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}
.title-area {
  text-align: center;
  margin-top: 48px;
  margin-bottom: 32px;
}
.title {
  font-size: 28px;
  font-weight: bold;
  color: #222;
  letter-spacing: 2px;
}
.title-underline {
  width: 56px;
  height: 4px;
  background: #409eff;
  border-radius: 2px;
  margin: 12px auto 0 auto;
}
.features-row {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto 48px auto;
}
.feature-col {
  margin-bottom: 40px;
  display: flex;
  justify-content: center;
}
.feature-card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 12px 0 rgba(64,158,255,0.06);
  padding: 28px 24px;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
  width: 100%;
  min-width: 260px;
  max-width: 340px;
}
.feature-card:hover {
  box-shadow: 0 8px 24px 0 rgba(64,158,255,0.18);
  transform: translateY(-5px);
}
.icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(64,158,255,0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}
.feature-icon {
  color: #409eff;
}
.feature-info {
  flex: 1;
}
.feature-title {
  font-size: 18px;
  font-weight: 600;
  color: #222;
  margin-bottom: 6px;
}
.feature-desc {
  font-size: 14px;
  color: #888;
  line-height: 1.5;
}
.banner {
  width: 100vw;
  margin-left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #1890ff, #0050b3);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 36px 0 32px 0;
  margin-top: auto;
}
.banner-item {
  flex: 1 1 0;
  text-align: center;
}
.banner-num {
  font-size: 38px;
  font-family: 'Segoe UI', 'Arial', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-weight: bold;
  color: #fff;
  margin-bottom: 8px;
  line-height: 1.1;
}
.banner-label {
  font-size: 16px;
  color: #fff;
  opacity: 0.85;
  margin-top: 2px;
}
.banner-item:not(:last-child) {
  border-right: 1px solid rgba(255,255,255,0.18);
}
@media (max-width: 900px) {
  .features-row {
    max-width: 100%;
  }
  .feature-col {
    min-width: 100%;
    max-width: 100%;
  }
  .feature-card {
    min-width: 0;
    max-width: 100%;
  }
}
</style>
