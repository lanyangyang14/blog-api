import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router/index.js'

const request = axios.create({
  baseURL: '/api/v1', // 走 vite 的代理
  timeout: 10000,
})

// 请求拦截器：自动带 Token
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  response => response.data,
  error => {
    const status = error.response?.status
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('token')
      router.push('/login')
    } else {
      const msg = error.response?.data?.message || error.message
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)

export default request
