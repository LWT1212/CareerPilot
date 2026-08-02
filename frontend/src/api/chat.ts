// 聊天相关API - 支持全局聊天和项目聊天

import api from './index'

// === 全局聊天（不隶属任何项目）===

// 创建全局聊天
export const createGlobalChat = (data: { title?: string; model?: string }) => {
  return api.post('/chats', data)
}

// 获取全局聊天列表
export const getGlobalChats = () => {
  return api.get('/chats')
}

// === 项目聊天 ===

// 创建项目聊天
export const createChat = (projectId: string, data: { title?: string; model?: string }) => {
  return api.post(`/projects/${projectId}/chats`, data)
}

// 获取项目聊天列表
export const getChats = (projectId: string) => {
  return api.get(`/projects/${projectId}/chats`)
}

// === 公共 ===

// 获取单个聊天
export const getChat = (chatId: string) => {
  return api.get(`/chats/${chatId}`)
}

// 删除聊天
export const deleteChat = (chatId: string) => {
  return api.delete(`/chats/${chatId}`)
}

// 发送消息
export const sendMessage = (chatId: string, content: string) => {
  return api.post(`/chats/${chatId}/messages`, { content })
}

// 获取消息列表
export const getMessages = (chatId: string) => {
  return api.get(`/chats/${chatId}/messages`)
}
