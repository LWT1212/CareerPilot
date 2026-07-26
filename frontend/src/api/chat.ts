// 聊天相关API - 开发顺序：Step 7

import api from './index'

// 创建聊天
export const createChat = (projectId: string, data: { title?: string; model?: string }) => {
  return api.post(`/projects/${projectId}/chats`, data)
}

// 获取聊天列表
export const getChats = (projectId: string) => {
  return api.get(`/projects/${projectId}/chats`)
}

// 获取单个聊天
export const getChat = (projectId: string, chatId: string) => {
  return api.get(`/projects/${projectId}/chats/${chatId}`)
}

// 删除聊天
export const deleteChat = (projectId: string, chatId: string) => {
  return api.delete(`/projects/${projectId}/chats/${chatId}`)
}

// 发送消息
export const sendMessage = (chatId: string, content: string) => {
  return api.post(`/chats/${chatId}/messages`, { content })
}

// 获取消息列表
export const getMessages = (chatId: string) => {
  return api.get(`/chats/${chatId}/messages`)
}
