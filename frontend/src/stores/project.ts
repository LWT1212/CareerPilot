// 项目上下文状态管理（全局共享）
// 所有页面通过它读取当前项目，保证聊天/知识库/面试等数据都关联到当前项目

import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'
import { getChats as apiGetChats, getMessages as apiGetMessages, createChat as apiCreateChat, sendMessage as apiSendMessage } from '../api/chat'

export const useProjectStore = defineStore('project', () => {
  // 当前项目ID（持久化到localStorage）
  const currentProjectId = ref<string>(localStorage.getItem('current_project_id') || '')
  // 当前项目对象
  const currentProject = ref<any>(null)
  // 当前项目下的聊天列表
  const chats = ref<any[]>([])
  // 当前选中的聊天
  const currentChat = ref<any>(null)
  // 当前聊天消息
  const messages = ref<any[]>([])
  // 新聊天请求计数器（点击"+ New Chat"时+1，Chat页面监听执行创建）
  const newChatRequested = ref(0)

  // 设置当前项目
  async function setProject(id: string) {
    currentProjectId.value = id
    localStorage.setItem('current_project_id', id)
    currentChat.value = null
    messages.value = []
    await Promise.all([loadProjectDetail(), loadChats()])
  }

  // 加载项目详情
  async function loadProjectDetail() {
    if (!currentProjectId.value) return
    try {
      const response = await api.get(`/projects/${currentProjectId.value}`)
      currentProject.value = response.data
    } catch (error) {
      console.error('加载项目失败', error)
    }
  }

  // 加载聊天列表
  async function loadChats() {
    if (!currentProjectId.value) {
      chats.value = []
      return
    }
    try {
      const response = await apiGetChats(currentProjectId.value)
      chats.value = response.data.items || response.data || []
    } catch (error) {
      console.error('加载聊天列表失败', error)
    }
  }

  // 选择聊天
  async function selectChat(chat: any) {
    currentChat.value = chat
    await loadMessages(chat.id)
  }

  // 加载消息
  async function loadMessages(chatId: string) {
    try {
      const response = await apiGetMessages(chatId)
      messages.value = response.data.items || response.data || []
    } catch (error) {
      console.error('加载消息失败', error)
    }
  }

  // 创建新聊天
  async function createNewChat() {
    if (!currentProjectId.value) return null
    try {
      const response = await apiCreateChat(currentProjectId.value, { title: '新聊天' })
      currentChat.value = response.data
      messages.value = []
      await loadChats()
      return response.data
    } catch (error) {
      console.error('创建聊天失败', error)
      return null
    }
  }

  // 发送消息
  async function sendMessageToChat(chatId: string, content: string) {
    return await apiSendMessage(chatId, content)
  }

  // 触发新聊天请求
  function requestNewChat() {
    newChatRequested.value++
  }

  // 清空当前项目（退出登录时）
  function clear() {
    currentProjectId.value = ''
    currentProject.value = null
    chats.value = []
    currentChat.value = null
    messages.value = []
    localStorage.removeItem('current_project_id')
  }

  return {
    currentProjectId,
    currentProject,
    chats,
    currentChat,
    messages,
    newChatRequested,
    setProject,
    loadProjectDetail,
    loadChats,
    selectChat,
    loadMessages,
    createNewChat,
    sendMessageToChat,
    requestNewChat,
    clear,
  }
})
