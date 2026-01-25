<template>
  <el-container class="main-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon class="logo-icon"><House /></el-icon>
        <span class="logo-text">CYO 系统</span>
      </div>
      <el-menu
        :default-active="route.path"
        class="menu"
        router
        background-color="#001529"
        text-color="#fff"
        active-text-color="#fff"
        :unique-opened="true"
        :collapse="false"
        :style="{ '--el-menu-active-bg-color': '#1890ff' }"
      >
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/messages">
          <el-icon><Bell /></el-icon>
          <span>消息中心</span>
        </el-menu-item>
        <el-menu-item index="/detection">
          <el-icon><Aim /></el-icon>
          <span>目标识别</span>
        </el-menu-item>
        <el-menu-item index="/analysis">
          <el-icon><DataAnalysis /></el-icon>
          <span>图像分析</span>
        </el-menu-item>
        <el-menu-item index="/encryption">
          <el-icon><Lock /></el-icon>
          <span>图像加密</span>
        </el-menu-item>
        <el-menu-item index="/decryption">
          <el-icon><Unlock /></el-icon>
          <span>图像解密</span>
        </el-menu-item>
        <el-menu-item index="/dynamics">
          <el-icon><TrendCharts /></el-icon>
          <span>系统动力学</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item v-for="(item, idx) in breadcrumbs" :key="idx">
            <span v-if="idx === breadcrumbs.length - 1">{{ item.meta.title }}</span>
            <router-link v-else :to="item.path">{{ item.meta.title }}</router-link>
          </el-breadcrumb-item>
        </el-breadcrumb>
      </el-header>
      <el-main class="main">
        <transition name="fade" mode="out-in">
          <router-view />
        </transition>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import { ElIcon } from 'element-plus'
import { House, Bell, Aim, DataAnalysis, Lock, Unlock, TrendCharts, Setting } from '@element-plus/icons-vue'

const route = useRoute()

const breadcrumbs = computed(() => {
  return route.matched.filter(item => item.meta && item.meta.title)
})
</script>

<style scoped>
.main-layout {
  height: 100vh;
}
.sidebar {
  background: #001529;
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 0;
  height: 100vh;
}
.logo {
  display: flex;
  align-items: center;
  height: 60px;
  padding-left: 24px;
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  margin-bottom: 8px;
}
.logo-icon {
  font-size: 26px;
  margin-right: 10px;
}
.menu {
  border-right: none;
  background: #001529;
  flex: 1;
}
.el-menu-item {
  font-size: 16px;
}
.header {
  height: 60px;
  background: #fff;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px #f0f1f2;
  border-bottom: 1px solid #ebeef5;
  padding-left: 24px;
}
.main {
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
  padding: 24px;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>

<style>
body {
  margin: 0;
}
</style>
