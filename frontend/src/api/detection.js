import request from '../utils/request'
import { API_BASE, authHeaders } from '../config/api'

/**
 * 构建检测上传表单。
 * 必须传浏览器 File/Blob 对象，字段名 file；不能传路径字符串。
 */
export function buildDetectionFormData(file, modelName = 'pest-v1') {
  const formData = new FormData()
  const name = file?.name || 'upload.jpg'
  formData.append('file', file, name)
  formData.append('model_name', modelName)
  return formData
}

export const detectSingleImage = (file, modelName) => {
  const data = file instanceof FormData ? file : buildDetectionFormData(file, modelName)
  return request({
    url: '/detection/single',
    method: 'post',
    data,
  })
}

export const getDetectionHistory = (params) => {
  return request({
    url: '/detection/history',
    method: 'get',
    params,
  })
}

export const getDetectionDetail = (id) => {
  return request({
    url: `/detection/detail/${id}`,
    method: 'get',
  })
}

export const deleteDetection = (id) => {
  return request({
    url: `/detection/${id}`,
    method: 'delete',
  })
}

/** 通过后端 attachment 响应触发浏览器下载 */
export async function downloadDetectionImage(id, filename) {
  const res = await fetch(`${API_BASE}/detection/download/${id}`, {
    headers: authHeaders(),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || '下载失败')
  }
  const blob = await res.blob()
  const blobUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = blobUrl
  link.download = filename || `detection_${id}.jpg`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(blobUrl)
}

export const getTargetList = () => {
  return request({
    url: '/detection/targets/list',
    method: 'get',
  })
}

/** 实时检测等不走 axios 的场景 */
export const DETECTION_SINGLE_URL = `${API_BASE}/detection/single`
