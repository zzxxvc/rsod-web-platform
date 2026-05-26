/** 后端根地址（无 /api 后缀），用于 /static、/register、/token */
export const API_ORIGIN = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
).replace(/\/api\/?$/, '')

/** 业务 API 前缀，用于 /api/detection/... */
export const API_BASE = `${API_ORIGIN}/api`

/** 静态资源完整 URL，relative 形如 /static/uploads/xxx.jpg */
export function staticUrl(relativePath) {
  if (!relativePath) return ''
  if (/^https?:\/\//.test(relativePath)) return relativePath
  return `${API_ORIGIN}${relativePath.startsWith('/') ? '' : '/'}${relativePath}`
}
