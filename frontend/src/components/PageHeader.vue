<template>
  <div class="page-header">
    <div class="header-content">
      <div class="header-icon" v-if="icon">
        <el-icon :size="28">
          <component :is="icon" />
        </el-icon>
      </div>
      <div class="header-text">
        <h1 class="title">{{ title }}</h1>
        <p class="subtitle" v-if="subtitle">{{ subtitle }}</p>
      </div>
    </div>
    <div class="header-line"></div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  subtitle?: string;
  icon?: any;
}>();
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.page-header {
  margin-bottom: $spacing-xl;
  
  .header-content {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    margin-bottom: $spacing-md;
  }
  
  .header-icon {
    width: 56px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, rgba(0, 153, 255, 0.2), rgba(0, 212, 255, 0.2));
    border: 1px solid $border-color;
    border-radius: $radius-lg;
    color: $primary-color;
    animation: pulse-glow 2s infinite;
  }
  
  .header-text {
    flex: 1;
    
    .title {
      font-size: 28px;
      font-weight: 700;
      margin: 0;
      background: linear-gradient(135deg, $text-primary, $primary-color);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .subtitle {
      margin: 4px 0 0;
      color: $text-secondary;
      font-size: 14px;
    }
  }
  
  .header-line {
    height: 2px;
    background: linear-gradient(90deg, 
      transparent, 
      $primary-color 50%, 
      transparent
    );
    border-radius: 2px;
  }
}
</style>
