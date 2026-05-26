import axios from 'axios'
import { ElMessage } from 'element-plus'
import { API_BASE } from '../config/api'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || API_BASE,
  timeout: 120000,
})

service.interceptors.request.use(
  (config) => {
    // FormData 必须由浏览器自动带 boundary，不能手写 Content-Type
    if (config.data instanceof FormData) {
      if (config.headers) {
        delete config.headers['Content-Type']
      }
    }
    return config
  },
  (error) => Promise.reject(error),
)

service.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const detail = error.response?.data?.detail
    const msg =
      (typeof detail === 'string' && detail) ||
      error.response?.data?.message ||
      '服务器错误'
    ElMessage.error('请求失败：' + msg)
    return Promise.reject(error)
  },
)

export default service
