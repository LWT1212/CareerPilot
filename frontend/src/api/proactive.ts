// 主动成长相关API - 学习计划/提醒/Agent执行记录

import api from './index'

// 获取学习计划（面试薄弱点自动生成）
export const getLearningPlans = (projectId: string) => {
  return api.get(`/projects/${projectId}/learning-plans`)
}

// 获取提醒
export const getNotifications = (projectId: string, unreadOnly: boolean = false) => {
  return api.get(`/projects/${projectId}/notifications`, {
    params: { unread_only: unreadOnly },
  })
}

// 标记提醒已读
export const markNotificationRead = (projectId: string, notifId: string) => {
  return api.post(`/projects/${projectId}/notifications/${notifId}/read`)
}

// 获取Agent执行记录
export const getAgentExecutions = (limit: number = 10) => {
  return api.get('/agents/executions', { params: { limit } })
}

// 获取项目记忆
export const getProjectMemories = (projectId: string) => {
  return api.get(`/projects/${projectId}/memories`)
}
