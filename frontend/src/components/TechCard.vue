<template>
  <div class="tech-card glass-card" :class="{ clickable: clickable }" @click="handleClick">
    <div class="card-glow"></div>
    <div class="card-content">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  clickable?: boolean;
}>();

const emit = defineEmits<{
  (e: 'click'): void;
}>();

function handleClick() {
  if (props.clickable) {
    emit('click');
  }
}
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.tech-card {
  position: relative;
  padding: $spacing-lg;
  overflow: hidden;
  
  &.clickable {
    cursor: pointer;
  }
  
  .card-glow {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
    opacity: 0;
    transition: opacity $transition-normal;
    pointer-events: none;
  }
  
  &:hover .card-glow {
    opacity: 1;
  }
  
  .card-content {
    position: relative;
    z-index: 1;
  }
}
</style>
