import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'detection',
        name: 'Detection',
        component: () => import('@/views/detection/index.vue'),
        meta: { title: '目标识别' }
      },
      {
        path: 'analysis',
        name: 'Analysis',
        component: () => import('@/views/analysis/index.vue'),
        meta: { title: '图像分析' }
      },
      {
        path: 'encryption',
        name: 'Encryption',
        component: () => import('@/views/encryption/index.vue'),
        meta: { title: '图像加密' }
      },
      {
        path: 'decryption',
        name: 'Decryption',
        component: () => import('@/views/decryption/index.vue'),
        meta: { title: '图像解密' }
      },
      {
        path: 'dynamics',
        name: 'Dynamics',
        component: () => import('@/views/chaos/index.vue'),
        meta: { title: '系统动力学' }
      },
    //   {
    //     path: 'settings',
    //     name: 'Settings',
    //     component: () => import('@/views/settings/index.vue'),
    //     meta: { title: '设置' }
    //   }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
