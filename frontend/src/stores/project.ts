// 项目上下文状态管理（全局共享）
// 支持两种聊天模式：
// 1. 全局聊天：不隶属任何项目（currentProjectId 为空）
// 2. 项目聊天：隶属当前项目

import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'
import {
  getChats as apiGetChats,
  getGlobalChats as apiGetGlobalChats,
  getMessages as apiGetMessages,
  createChat as apiCreateChat,
  createGlobalChat as apiCreateGlobalChat,
  sendMessage as apiSendMessage,
} from '../api/chat'

export const useProjectStore = defineStore('project', () => {
  // 当前项目ID（空字符串 = 全局模式）
  const currentProjectId = ref<string>(localStorage.getItem('current_project_id') || '')
  // 当前项目对象
  const currentProject = ref<any>(null)
  // 全局聊天列表
  const globalChats = ref<any[]>([])
  // 当前项目下的聊天列表
  const chats = ref<any[]>([])
  // 当前选中的聊天
  const currentChat = ref<any>(null)
  // 当前聊天消息
  const messages = ref<any[]>([])
  // 新聊天请求计数器（点击"+ New Chat"时+1，Chat页面监听执行创建）
  const newChatRequested = ref(0)

  // 设置当前项目（空字符串 = 全局模式）
  async function setProject(id: string) {
    currentProjectId.value = id
    if (id) {
      localStorage.setItem('current_project_id', id)
    } else {
      localStorage.removeItem('current_project_id')
    }
    currentChat.value = null
    messages.value = []
    if (id) {
      await Promise.all([loadProjectDetail(), loadChats()])
    }
  }

  // 加载项目详情
  async function loadProjectDetail() {
    if (!currentProjectId.value) {
      currentProject.value = null
      return
    }
    try {
      const response = await api.get(`/projects/${currentProjectId.value}`)
      currentProject.value = response.data
    } catch (error) {
      console.error('加载项目失败', error)
    }
  }

  // 加载全局聊天列表
  async function loadGlobalChats() {
    try {
      const response = await apiGetGlobalChats()
      globalChats.value = response.data || []
    } catch (error) {
      console.error('加载全局聊天失败', error)
    }
  }

  // 加载当前项目的聊天列表
  async function loadChats() {
    if (!currentProjectId.value) {
      chats.value = []
      return
    }
    try {
      const response = await apiGetChats(currentProjectId.value)
      chats.value = response.data || []
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

  // 创建新聊天（全局模式或项目模式）
  async function createNewChat() {
    try {
      let response
      if (currentProjectId.value) {
        response = await apiCreateChat(currentProjectId.value, { title: '新聊天' })
        await loadChats()
      } else {
        response = await apiCreateGlobalChat({ title: '新聊天' })
        await loadGlobalChats()
      }
      currentChat.value = response.data
      messages.value = []
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

  // 清空（退出登录时）
  function clear() {
    currentProjectId.value = ''
    currentProject.value = null
    chats.value = []
    globalChats.value = []
    currentChat.value = null
    messages.value = []
    localStorage.removeItem('current_project_id')
  }

  return {
    currentProjectId,
    currentProject,
    chats,
    globalChats,
    currentChat,
    messages,
    newChatRequested,
    setProject,
    loadProjectDetail,
    loadChats,
    loadGlobalChats,
    selectChat,
    loadMessages,
    createNewChat,
    sendMessageToChat,
    requestNewChat,
    clear,
  }
})
