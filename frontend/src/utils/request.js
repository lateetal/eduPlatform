import axios from 'axios'
// 创建 Axios 实例
const instance = axios.create();

// 添加请求拦截器
instance.interceptors.request.use(config => {
  const token = localStorage.getItem('token'); // 从本地存储获取令牌
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default instance;