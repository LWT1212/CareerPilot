// 经验管理相关API - 开发顺序：Step 9

import api from './index'

// 创建经验
export const createExperience = (projectId: string, data: any) => {
  return api.post(`/projects/${projectId}/experiences`, data)
}

// 获取经验列表
export const getExperiences = (projectId: string, type?: string) => {
  const params = type ? { type } : {}
  return api.get(`/projects/${projectId}/experiences`, { params })
}

// 获取单个经验
export const getExperience = (projectId: string, expId: string) => {
  return api.get(`/projects/${projectId}/experiences/${expId}`)
}

// 更新经验
export const updateExperience = (projectId: string, expId: string, data: any) => {
  return api.put(`/projects/${projectId}/experiences/${expId}`, data)
}

// 删除经验
export const deleteExperience = (projectId: string, expId: string) => {
  return api.delete(`/projects/${projectId}/experiences/${expId}`)
}
