<template>
  <div class="dashboard">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          混沌图像加密系统
        </h1>
        <p class="hero-subtitle">
          基于混沌理论的图像加密与目标检测平台。<br/>
          安全、高效、可靠的图像处理解决方案。
        </p>
        <div class="hero-actions">
          <button class="primary-button" @click="navigateTo('/encryption')">
            开始加密
            <el-icon class="button-icon"><Right /></el-icon>
          </button>
          <button class="secondary-button" @click="navigateTo('/detection')">
            目标识别
          </button>
        </div>
      </div>
      
      <!-- Stats inline -->
      <div class="hero-stats">
        <div class="stat-item">
          <div class="stat-value">2<sup>256</sup></div>
          <div class="stat-label">密钥空间</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <div class="stat-value">99.9%</div>
          <div class="stat-label">信息熵</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <div class="stat-value">&lt;0.01</div>
          <div class="stat-label">像素相关性</div>
        </div>
      </div>
    </div>
    
    <!-- Features Section -->
    <div class="features-section">
      <div class="section-header">
        <span class="section-badge">核心功能</span>
        <h2 class="section-title">强大的图像处理能力</h2>
      </div>
      
      <div class="features-grid">
        <div
          v-for="feature in features"
          :key="feature.title"
          class="feature-item"
          @click="navigateTo(feature.route)"
        >
          <div class="feature-icon-wrapper">
            <el-icon class="feature-icon" :size="24">
              <component :is="feature.icon" />
            </el-icon>
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-description">{{ feature.description }}</p>
          <div class="feature-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>
    
    <!-- System Status - Minimal -->
    <div class="status-section">
      <div class="status-content">
        <div class="status-left">
          <div class="status-badge">
            <span class="status-dot"></span>
            <span>系统运行正常</span>
          </div>
          <div class="status-info">
            <span class="info-item">已处理 <strong>1,247</strong> 张图像</span>
            <span class="info-divider">·</span>
            <span class="info-item">运行 <strong>72h</strong></span>
            <span class="info-divider">·</span>
            <span class="info-item">CPU <strong>45%</strong></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { 
  Right,
  Aim, 
  DataAnalysis, 
  Lock, 
  Unlock, 
  TrendCharts,
  ArrowRight
} from '@element-plus/icons-vue';

const router = useRouter();

const features = [
  {
    title: '目标识别',
    description: '基于 YOLOv9 的高精度目标检测与识别系统',
    icon: Aim,
    route: '/detection'
  },
  {
    title: '图像分析',
    description: '3D可视化分析，深入理解图像数据特征',
    icon: DataAnalysis,
    route: '/analysis'
  },
  {
    title: '图像加密',
    description: '混沌加密算法保护图像隐私与安全',
    icon: Lock,
    route: '/encryption'
  },
  {
    title: '图像解密',
    description: '快速解密并恢复加密图像原貌',
    icon: Unlock,
    route: '/decryption'
  },
  {
    title: '系统动力学',
    description: '分析混沌系统的动力学特性与轨迹',
    icon: TrendCharts,
    route: '/dynamics'
  }
];

function navigateTo(route: string) {
  router.push(route);
}
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
  
  // Hero Section - Linear Style
  .hero-section {
    padding: 80px 0 100px;
    text-align: center;
    
    .hero-content {
      margin-bottom: 60px;
    }
    
    .hero-title {
      font-size: 64px;
      font-weight: 600;
      line-height: 1.1;
      letter-spacing: -0.02em;
      margin: 0 0 24px;
      background: linear-gradient(135deg, $text-primary 0%, rgba(255, 255, 255, 0.7) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      animation: fadeInUp 0.6s ease-out;
    }
    
    .hero-subtitle {
      font-size: 20px;
      line-height: 1.6;
      color: $text-secondary;
      margin: 0 auto 40px;
      max-width: 600px;
      animation: fadeInUp 0.7s ease-out;
    }
    
    .hero-actions {
      display: flex;
      gap: 16px;
      justify-content: center;
      animation: fadeInUp 0.8s ease-out;
      
      button {
        padding: 14px 28px;
        font-size: 16px;
        font-weight: 500;
        border-radius: 10px;
        border: none;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 8px;
        
        &.primary-button {
          background: linear-gradient(135deg, $secondary-color, $primary-color);
          color: $text-primary;
          
          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 40px rgba(0, 212, 255, 0.3);
          }
          
          .button-icon {
            transition: transform 0.2s ease;
          }
          
          &:hover .button-icon {
            transform: translateX(4px);
          }
        }
        
        &.secondary-button {
          background: rgba(255, 255, 255, 0.05);
          color: $text-primary;
          border: 1px solid rgba(255, 255, 255, 0.1);
          
          &:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.2);
          }
        }
      }
    }
    
    .hero-stats {
      display: flex;
      justify-content: center;
      gap: 60px;
      padding: 32px 0;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      animation: fadeInUp 0.9s ease-out;
      
      .stat-item {
        text-align: center;
        
        .stat-value {
          font-size: 32px;
          font-weight: 600;
          color: $text-primary;
          margin-bottom: 8px;
          font-family: 'SF Mono', 'Monaco', monospace;
          
          sup {
            font-size: 18px;
            margin-left: 2px;
          }
        }
        
        .stat-label {
          font-size: 14px;
          color: $text-secondary;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          font-weight: 500;
        }
      }
      
      .stat-divider {
        width: 1px;
        background: rgba(255, 255, 255, 0.06);
      }
    }
  }
  
  // Features Section - Linear Style
  .features-section {
    padding: 100px 0;
    
    .section-header {
      text-align: center;
      margin-bottom: 60px;
      
      .section-badge {
        display: inline-block;
        padding: 6px 14px;
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 20px;
        font-size: 13px;
        color: $primary-color;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 16px;
      }
      
      .section-title {
        font-size: 40px;
        font-weight: 600;
        color: $text-primary;
        margin: 0;
        letter-spacing: -0.01em;
      }
    }
    
    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 24px;
      
      .feature-item {
        padding: 32px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        
        &:hover {
          background: rgba(255, 255, 255, 0.04);
          border-color: rgba(0, 212, 255, 0.3);
          transform: translateY(-4px);
          
          .feature-icon-wrapper {
            background: rgba(0, 212, 255, 0.15);
            border-color: rgba(0, 212, 255, 0.4);
          }
          
          .feature-arrow {
            opacity: 1;
            transform: translateX(4px);
          }
        }
        
        .feature-icon-wrapper {
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(0, 212, 255, 0.08);
          border: 1px solid rgba(0, 212, 255, 0.2);
          border-radius: 12px;
          margin-bottom: 20px;
          transition: all 0.3s ease;
          
          .feature-icon {
            color: $primary-color;
          }
        }
        
        .feature-title {
          font-size: 20px;
          font-weight: 600;
          color: $text-primary;
          margin: 0 0 12px;
        }
        
        .feature-description {
          font-size: 15px;
          line-height: 1.6;
          color: $text-secondary;
          margin: 0;
        }
        
        .feature-arrow {
          position: absolute;
          top: 32px;
          right: 32px;
          opacity: 0;
          transition: all 0.3s ease;
          color: $primary-color;
        }
      }
    }
  }
  
  // Status Section - Minimal
  .status-section {
    padding: 40px 0 80px;
    
    .status-content {
      padding: 24px 32px;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      
      .status-left {
        display: flex;
        align-items: center;
        gap: 32px;
        
        .status-badge {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 14px;
          font-weight: 500;
          color: $accent-color;
          
          .status-dot {
            width: 8px;
            height: 8px;
            background: $accent-color;
            border-radius: 50%;
            animation: pulse-dot 2s infinite;
          }
        }
        
        .status-info {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 14px;
          color: $text-secondary;
          
          .info-item {
            strong {
              color: $text-primary;
              font-weight: 600;
            }
          }
          
          .info-divider {
            opacity: 0.3;
          }
        }
      }
    }
  }
}

// Animations
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse-dot {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 0 0 rgba(0, 255, 170, 0.7);
  }
  50% {
    opacity: 0.8;
    box-shadow: 0 0 0 8px rgba(0, 255, 170, 0);
  }
}

// Responsive
@media (max-width: 768px) {
  .dashboard {
    .hero-section {
      padding: 60px 20px 80px;
      
      .hero-title {
        font-size: 40px;
      }
      
      .hero-subtitle {
        font-size: 18px;
      }
      
      .hero-stats {
        flex-direction: column;
        gap: 32px;
        
        .stat-divider {
          display: none;
        }
      }
    }
    
    .features-section {
      padding: 60px 20px;
      
      .section-title {
        font-size: 32px;
      }
      
      .features-grid {
        grid-template-columns: 1fr;
      }
    }
    
    .status-section {
      padding: 40px 20px;
      
      .status-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 20px;
        
        .status-left {
          flex-direction: column;
          align-items: flex-start;
          gap: 16px;
        }
      }
    }
  }
}
</style>
