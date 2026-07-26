<!-- ChatGPT风格布局 - 修复按钮点击 -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const projects = ref<any[]>([])
const showNewProjectDialog = ref(false)
const newProjectName = ref('')

onMounted(async () => {
  await loadProjects()
})

const loadProjects = async () => {
  try {
    const response = await api.get('/projects')
    projects.value = response.data.items || []
  } catch (error) {
    console.error('加载项目失败', error)
  }
}

const createProject = async () => {
  if (!newProjectName.value.trim()) return
  try {
    await api.post('/projects', { name: newProjectName.value })
    newProjectName.value = ''
    showNewProjectDialog.value = false
    await loadProjects()
  } catch (error) {
    console.error('创建项目失败', error)
  }
}

const navigateTo = (path: string) => {
  router.push(path)
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <!-- 头部 -->
      <div class="sidebar-header">
        <div class="app-title">CareerPilot AI</div>
        <div class="header-actions">
          <div class="user-avatar" @click="logout">👤</div>
        </div>
      </div>

      <!-- 内容区 -->
      <div class="sidebar-content">
        <!-- 新建聊天 -->
        <button class="new-chat-btn" @click="navigateTo('/')">
          + New Chat
        </button>

        <!-- 最近聊天 -->
        <div class="section">
          <div class="section-title">Recent Chats</div>
          <div class="nav-item" @click="navigateTo('/')">Redis是什么</div>
          <div class="nav-item" @click="navigateTo('/')">LangGraph</div>
          <div class="nav-item" @click="navigateTo('/')">MCP</div>
        </div>

        <!-- 项目 -->
        <div class="section">
          <div class="section-header">
            <span class="section-title">Projects</span>
            <button class="add-btn" @click="showNewProjectDialog = true">+</button>
          </div>
          <div class="project-list">
            <div
              v-for="project in projects"
              :key="project.id"
              class="nav-item project-item"
            >
              <span class="nav-icon">📁</span>
              <span>{{ project.name }}</span>
            </div>
            <div v-if="projects.length === 0" class="empty-text">暂无项目</div>
          </div>
        </div>

        <!-- 知识库 -->
        <div class="section">
          <div class="section-title">Knowledge Base</div>
          <div class="nav-item" @click="navigateTo('/knowledge')">📚 知识库</div>
        </div>
      </div>

      <!-- 底部设置 -->
      <div class="sidebar-footer">
        <div class="nav-item" @click="navigateTo('/experience')">💡 经验</div>
        <div class="nav-item" @click="navigateTo('/interview')">🎯 面试</div>
        <div class="nav-item" @click="navigateTo('/documents')">📄 文档</div>
        <div class="nav-item" @click="navigateTo('/settings')">⚙️ Settings</div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <slot />
    </main>

    <!-- 右侧面板 -->
    <aside class="context-panel">
      <div class="panel-header">Context Panel</div>
      <slot name="context" />
    </aside>

    <!-- 新建项目对话框 -->
    <div v-if="showNewProjectDialog" class="dialog-overlay" @click.self="showNewProjectDialog = false">
      <div class="dialog">
        <h3>新建项目</h3>
        <input v-model="newProjectName" placeholder="项目名称" @keyup.enter="createProject" />
        <div class="dialog-actions">
          <button class="cancel-btn" @click="showNewProjectDialog = false">取消</button>
          <button class="confirm-btn" @click="createProject">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
}

.sidebar {
  width: 260px;
  background: #fff;
  border-right: 1px solid #e5e5e5;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e5e5;
}

.app-title {
  font-weight: 600;
  font-size: 16px;
  color: #333;
}

.user-avatar {
  font-size: 20px;
  cursor: pointer;
  padding: 5px;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.new-chat-btn {
  width: 100%;
  padding: 12px;
  background: transparent;
  border: 1px dashed #d0d0d0;
  border-radius: 8px;
  color: #666;
  cursor: pointer;
  font-size: 14px;
  text-align: left;
  margin-bottom: 20px;
}

.new-chat-btn:hover {
  background: #f5f5f5;
}

.section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.add-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 18px;
  cursor: pointer;
  padding: 0 5px;
}

.add-btn:hover {
  color: #000;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.nav-item:hover {
  background: #f0f0f0;
}

.project-list {
  display: flex;
  flex-direction: column;
}

.project-item {
  font-size: 13px;
}

.empty-text {
  color: #999;
  font-size: 13px;
  padding: 10px 8px;
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid #e5e5e5;
}

.sidebar-footer .nav-item {
  padding: 8px;
  margin-bottom: 4px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.context-panel {
  width: 280px;
  background: #fff;
  border-left: 1px solid #e5e5e5;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px 20px;
  font-weight: 600;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #e5e5e5;
}

/* Dialog */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  width: 400px;
}

.dialog h3 {
  margin-bottom: 16px;
  color: #333;
}

.dialog input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  margin-bottom: 16px;
}

.dialog input:focus {
  border-color: #000;
}

.dialog-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.cancel-btn {
  padding: 8px 16px;
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.confirm-btn {
  padding: 8px 16px;
  background: #000;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>
