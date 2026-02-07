<template>
  <div class="main-layout">
    <TechBackground />
    
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-icon">
          <el-icon :size="32"><Aim /></el-icon>
        </div>
        <div class="logo-text">
          <span class="logo-title">CYO</span>
          <span class="logo-subtitle">混沌图像系统</span>
        </div>
      </div>
      
      <nav class="nav-menu">
        <div
          v-for="item in menuItems"
          :key="item.path"
          class="menu-item"
          :class="{ active: isActive(item.path) }"
          @click="navigateTo(item.path)"
        >
          <div class="menu-item-content">
            <el-icon class="menu-icon" :size="20">
              <component :is="item.icon" />
            </el-icon>
            <span class="menu-text">{{ item.title }}</span>
          </div>
          <div class="menu-indicator"></div>
        </div>
      </nav>
      
      <div class="sidebar-footer">
        <div class="system-info">
          <div class="info-item">
            <span class="info-label">版本</span>
            <span class="info-value">v1.0.0</span>
          </div>
        </div>
      </div>
    </aside>
    
    <!-- 主内容区 -->
    <div class="main-container">
      <header class="header">
        <div class="breadcrumb">
          <el-icon class="breadcrumb-icon"><HomeFilled /></el-icon>
          <span v-for="(item, idx) in breadcrumbs" :key="idx" class="breadcrumb-item">
            <span class="separator">/</span>
            <span :class="{ active: idx === breadcrumbs.length - 1 }">
              {{ item.meta?.title }}
            </span>
          </span>
        </div>
        
        <div class="header-actions">
          <div class="time-display">
            {{ currentTime }}
          </div>
        </div>
      </header>
      
      <main class="main-content">
        <transition name="page-fade" mode="out-in">
          <router-view />
        </transition>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { computed, ref, onMounted, onUnmounted } from 'vue';
import TechBackground from '@/components/TechBackground.vue';
import { 
  Aim, 
  DataAnalysis, 
  Lock, 
  Unlock, 
  TrendCharts,
  HomeFilled,
  Monitor
} from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();

const menuItems = [
  { path: '/dashboard', title: '首页', icon: Monitor },
  { path: '/detection', title: '目标识别', icon: Aim },
  { path: '/analysis', title: '图像分析', icon: DataAnalysis },
  { path: '/encryption', title: '图像加密', icon: Lock },
  { path: '/decryption', title: '图像解密', icon: Unlock },
  { path: '/dynamics', title: '系统动力学', icon: TrendCharts },
];

const breadcrumbs = computed(() => {
  return route.matched.filter(item => item.meta && item.meta.title);
});

const currentTime = ref('');

function updateTime() {
  const now = new Date();
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

let timer: number;
onMounted(() => {
  updateTime();
  timer = window.setInterval(updateTime, 1000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});

function isActive(path: string) {
  return route.path === path;
}

function navigateTo(path: string) {
  router.push(path);
}
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

// 侧边栏
.sidebar {
  width: 260px;
  background: $sidebar-bg;
  backdrop-filter: blur(20px);
  border-right: 1px solid $border-color;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 10;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 1px;
    height: 100%;
    background: linear-gradient(180deg, 
      transparent,
      $primary-color 50%,
      transparent
    );
    animation: slide-vertical 3s infinite;
  }
}

@keyframes slide-vertical {
  0%, 100% { transform: translateY(-100%); }
  50% { transform: translateY(100%); }
}

.logo {
  display: flex;
  align-items: center;
  padding: $spacing-lg $spacing-xl;
  gap: $spacing-md;
  border-bottom: 1px solid $border-color;
  
  .logo-icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, $secondary-color, $primary-color);
    border-radius: $radius-lg;
    color: $text-primary;
    box-shadow: $shadow-glow;
    animation: pulse-glow 2s infinite;
  }
  
  .logo-text {
    display: flex;
    flex-direction: column;
    
    .logo-title {
      font-size: 24px;
      font-weight: 700;
      background: linear-gradient(135deg, $text-primary, $primary-color);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .logo-subtitle {
      font-size: 12px;
      color: $text-secondary;
      margin-top: 2px;
    }
  }
}

.nav-menu {
  flex: 1;
  padding: $spacing-lg $spacing-md;
  overflow-y: auto;
}

.menu-item {
  position: relative;
  margin-bottom: $spacing-sm;
  cursor: pointer;
  border-radius: $radius-md;
  overflow: hidden;
  transition: all $transition-normal;
  
  .menu-item-content {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    padding: $spacing-md $spacing-lg;
    color: $text-secondary;
    transition: all $transition-normal;
  }
  
  .menu-icon {
    transition: all $transition-normal;
  }
  
  .menu-text {
    font-size: 15px;
    font-weight: 500;
  }
  
  .menu-indicator {
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 0;
    background: linear-gradient(180deg, $secondary-color, $primary-color);
    border-radius: 0 2px 2px 0;
    transition: all $transition-normal;
  }
  
  &:hover {
    background: rgba(0, 212, 255, 0.08);
    
    .menu-item-content {
      color: $primary-color;
      transform: translateX(4px);
    }
  }
  
  &.active {
    background: rgba(0, 212, 255, 0.15);
    
    .menu-item-content {
      color: $primary-color;
    }
    
    .menu-icon {
      transform: scale(1.1);
    }
    
    .menu-indicator {
      height: 24px;
    }
  }
}

.sidebar-footer {
  padding: $spacing-lg;
  border-top: 1px solid $border-color;
  
  .system-info {
    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $spacing-sm 0;
      
      .info-label {
        color: $text-secondary;
        font-size: 12px;
      }
      
      .info-value {
        color: $primary-color;
        font-size: 12px;
        font-weight: 600;
      }
    }
  }
}

// 主内容区
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 64px;
  background: rgba(10, 14, 39, 0.6);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid $border-color;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $spacing-xl;
  position: relative;
  z-index: 5;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, 
      transparent,
      $primary-color 50%,
      transparent
    );
  }
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  color: $text-secondary;
  
  .breadcrumb-icon {
    color: $primary-color;
  }
  
  .breadcrumb-item {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    
    .separator {
      color: $text-secondary;
      opacity: 0.5;
    }
    
    span {
      font-size: 14px;
      transition: color $transition-fast;
      
      &.active {
        color: $primary-color;
        font-weight: 600;
      }
    }
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
}

.time-display {
  font-size: 13px;
  color: $text-secondary;
  font-family: 'Courier New', monospace;
  padding: $spacing-sm $spacing-md;
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid $border-color;
  border-radius: $radius-md;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: $spacing-xl;
}

// 页面切换动画
.page-fade-enter-active,
.page-fade-leave-active {
  transition: all $transition-normal;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
