<template>
  <div class="stat-card">
    <div class="stat-icon" :style="{ background: iconBg }">
      <el-icon :size="32">
        <component :is="icon" />
      </el-icon>
    </div>
    <div class="stat-content">
      <div class="stat-value">{{ value }}</div>
      <div class="stat-label">{{ label }}</div>
      <div class="stat-trend" v-if="trend">
        <el-icon :size="12" :class="trend > 0 ? 'up' : 'down'">
          <component :is="trend > 0 ? 'ArrowUp' : 'ArrowDown'" />
        </el-icon>
        <span>{{ Math.abs(trend) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon: any;
  value: string | number;
  label: string;
  iconBg?: string;
  trend?: number;
}>();
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.stat-card {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
  padding: $spacing-lg;
  background: $card-bg;
  backdrop-filter: blur(10px);
  border: 1px solid $border-color;
  border-radius: $radius-lg;
  transition: all $transition-normal;
  
  &:hover {
    border-color: $primary-color;
    box-shadow: $shadow-glow;
    transform: translateY(-2px);
  }
  
  .stat-icon {
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, rgba(0, 153, 255, 0.2), rgba(0, 212, 255, 0.2));
    border-radius: $radius-lg;
    color: $primary-color;
  }
  
  .stat-content {
    flex: 1;
    
    .stat-value {
      font-size: 28px;
      font-weight: 700;
      color: $text-primary;
      margin-bottom: 4px;
      
      sup {
        font-size: 14px;
        margin-left: 2px;
      }
    }
    
    .stat-label {
      font-size: 13px;
      color: $text-secondary;
      margin-bottom: 4px;
    }
    
    .stat-trend {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
      
      &.up {
        color: $accent-color;
      }
      
      &.down {
        color: #ff4d4f;
      }
    }
  }
}
</style>
