// 知识库相关API - 支持全局知识库和项目知识库

import api from './index'

// === 全局知识库 ===

// 上传到全局知识库
export const uploadGlobalDocument = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/knowledge', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 获取全局知识库文档列表
export const getGlobalDocuments = () => {
  return api.get('/knowledge')
}

// === 项目知识库 ===

// 上传到项目
export const uploadDocument = (projectId: string, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/projects/${projectId}/knowledge`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 获取项目文档列表
export const getDocuments = (projectId: string) => {
  return api.get(`/projects/${projectId}/knowledge`)
}

// 删除文档（全局文档 projectId 传空字符串）
export const deleteDocument = (projectId: string, docId: string) => {
  const prefix = projectId ? `/projects/${projectId}` : ''
  return api.delete(`${prefix}/knowledge/${docId}`)
}

// 知识检索
export const searchKnowledge = (projectId: string, query: string) => {
  const prefix = projectId ? `/projects/${projectId}` : ''
  return api.post(`${prefix}/knowledge/search`, { query, top_k: 5 })
}
