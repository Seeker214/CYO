<template>
  <div class="feature-card glass-card" @click="handleClick">
    <div class="card-border"></div>
    <div class="feature-icon">
      <el-icon :size="48">
        <component :is="icon" />
      </el-icon>
    </div>
    <div class="feature-content">
      <h3 class="feature-title">{{ title }}</h3>
      <p class="feature-desc">{{ description }}</p>
    </div>
    <div class="feature-arrow">
      <el-icon><ArrowRight /></el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue';

defineProps<{
  icon: any;
  title: string;
  description: string;
}>();

const emit = defineEmits<{
  (e: 'click'): void;
}>();

function handleClick() {
  emit('click');
}
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.feature-card {
  position: relative;
  padding: $spacing-xl;
  cursor: pointer;
  overflow: hidden;
  transition: all $transition-normal;
  
  .card-border {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, $secondary-color, $primary-color);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform $transition-normal;
  }
  
  &:hover {
    .card-border {
      transform: scaleX(1);
    }
    
    .feature-icon {
      transform: scale(1.1) rotate(5deg);
    }
    
    .feature-arrow {
      transform: translateX(4px);
      opacity: 1;
    }
  }
  
  .feature-icon {
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, rgba(0, 153, 255, 0.2), rgba(0, 212, 255, 0.2));
    border: 1px solid $border-color;
    border-radius: $radius-lg;
    color: $primary-color;
    margin-bottom: $spacing-lg;
    transition: all $transition-normal;
  }
  
  .feature-content {
    margin-bottom: $spacing-md;
    
    .feature-title {
      font-size: 20px;
      font-weight: 600;
      color: $text-primary;
      margin: 0 0 $spacing-sm 0;
    }
    
    .feature-desc {
      font-size: 14px;
      color: $text-secondary;
      margin: 0;
      line-height: 1.6;
    }
  }
  
  .feature-arrow {
    position: absolute;
    bottom: $spacing-lg;
    right: $spacing-lg;
    color: $primary-color;
    opacity: 0;
    transition: all $transition-normal;
  }
}
</style>
