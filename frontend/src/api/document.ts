// 文档管理相关API - 开发顺序：Step 11

import api from './index'

// 获取文档列表
export const getDocuments = (projectId: string) => {
  return api.get(`/projects/${projectId}/documents`)
}

// 获取单个文档
export const getDocument = (projectId: string, docType: string) => {
  return api.get(`/projects/${projectId}/documents/${docType}`)
}

// 更新文档
export const updateDocument = (projectId: string, docType: string, content: string) => {
  return api.put(`/projects/${projectId}/documents/${docType}`, { content })
}

// AI生成文档
export const generateDocument = (projectId: string, docType: string, instruction?: string) => {
  return api.post(`/projects/${projectId}/documents/${docType}/generate`, { instruction })
}
