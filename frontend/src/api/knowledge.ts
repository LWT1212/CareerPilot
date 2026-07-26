// 知识库相关API - 开发顺序：Step 8

import api from './index'

// 上传文档
export const uploadDocument = (projectId: string, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/projects/${projectId}/knowledge`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 获取文档列表
export const getDocuments = (projectId: string) => {
  return api.get(`/projects/${projectId}/knowledge`)
}

// 删除文档
export const deleteDocument = (projectId: string, docId: string) => {
  return api.delete(`/projects/${projectId}/knowledge/${docId}`)
}

// 知识检索
export const searchKnowledge = (projectId: string, query: string) => {
  return api.post(`/projects/${projectId}/knowledge/search`, { query, top_k: 5 })
}
