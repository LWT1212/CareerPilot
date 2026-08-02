// 项目上下文状态管理（全局共享）
// 所有页面通过它读取当前项目，保证聊天/知识库/面试等数据都关联到当前项目

import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useProjectStore = defineStore('project', () => {
  // 当前项目ID（持久化到localStorage）
  const currentProjectId = ref<string>(localStorage.getItem('current_project_id') || '')
  // 当前项目对象
  const currentProject = ref<any>(null)
  // 新聊天请求计数器（点击"+ New Chat"时+1，Chat页面监听执行创建）
  const newChatRequested = ref(0)
  // 当前项目下的聊天列表
  const chats = ref<any[]>([])

  // 设置当前项目
  async function setProject(id: string) {
    currentProjectId.value = id
    localStorage.setItem('current_project_id', id)
    await loadProjectDetail()
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

  // 触发新聊天请求
  function requestNewChat() {
    newChatRequested.value++
  }

  // 清空当前项目（退出登录时）
  function clear() {
    currentProjectId.value = ''
    currentProject.value = null
    chats.value = []
    localStorage.removeItem('current_project_id')
  }

  return {
    currentProjectId,
    currentProject,
    newChatRequested,
    chats,
    setProject,
    loadProjectDetail,
    requestNewChat,
    clear,
  }
})
