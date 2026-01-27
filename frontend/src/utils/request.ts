import axios from 'axios';
import { ElMessage } from 'element-plus';

// 1. 创建 axios 实例
const service = axios.create({
  // 自动使用 .env 文件中的变量
  baseURL: import.meta.env.VITE_API_BASE_URL, 
//   timeout: 5000 // 请求超时时间
});

// 2. 请求拦截器 (可以在这里统一加 Token)
service.interceptors.request.use(
  (config) => {
    // 例如：config.headers['Authorization'] = 'Bearer ' + getToken()
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 3. 响应拦截器 (可以在这里统一处理错误)
service.interceptors.response.use(
  (response) => {
    const res = response.data;
    // 这里可以根据后端返回的状态码做统一判断
    return res;
  },
  (error) => {
    console.log('err' + error);
    ElMessage.error(error.message || '请求失败');
    return Promise.reject(error);
  }
);

export default service;