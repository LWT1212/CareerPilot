// 面试模块相关API - 开发顺序：Step 10

import api from './index'

// 创建面试记录
export const createInterview = (projectId: string, data: any) => {
  return api.post(`/projects/${projectId}/interviews`, data)
}

// 获取面试列表
export const getInterviews = (projectId: string) => {
  return api.get(`/projects/${projectId}/interviews`)
}

// 获取面试统计
export const getInterviewStats = (projectId: string) => {
  return api.get(`/projects/${projectId}/interviews/stats`)
}

// 删除面试记录
export const deleteInterview = (projectId: string, interviewId: string) => {
  return api.delete(`/projects/${projectId}/interviews/${interviewId}`)
}

// 添加面试问题
export const addQuestion = (interviewId: string, data: any) => {
  return api.post(`/interviews/${interviewId}/questions`, data)
}
