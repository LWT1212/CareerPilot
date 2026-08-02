<!-- 主布局 - 按照PRD页面设计 -->
<!-- 左侧：导航栏 | 中间：内容区 | 右侧：Project Context（可折叠） -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()

const rightPanelCollapsed = ref(false)
const projects = ref<any[]>([])
const showNewProjectDialog = ref(false)
const newProjectName = ref('')
const newProjectDesc = ref('')

onMounted(async () => {
  await loadProjects()
})

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await api.get('/projects')
    projects.value = response.data.items || []
  } catch (error) {
    console.error('加载项目失败', error)
  }
}

// 创建项目
const createProject = async () => {
  if (!newProjectName.value.trim()) return
  try {
    await api.post('/projects', { name: newProjectName.value, description: newProjectDesc.value })
    newProjectName.value = ''
    newProjectDesc.value = ''
    showNewProjectDialog.value = false
    await loadProjects()
  } catch (error) {
    console.error('创建项目失败', error)
  }
}

// 导航
const navigateTo = (target: any) => {
  router.push(target)
}

// 选择项目（跳转到聊天）
const selectProject = (id: string) => {
  localStorage.setItem('current_project_id', id)
  router.push({ path: '/', query: { project: id } })
}

// 退出登录
const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="layout">
    <!-- 左侧边栏 -->
    <aside class="sidebar">
      <!-- 顶部：标题+头像 -->
      <div class="sidebar-header">
        <div class="app-title">CareerPilot AI</div>
        <div class="user-avatar" @click="logout" title="退出登录">👤</div>
      </div>

      <!-- 导航内容 -->
      <div class="sidebar-content">
        <!-- + New Chat -->
        <button class="new-chat-btn" @click="navigateTo({ path: '/', query: { action: 'new' } })">
          + New Chat
        </button>

        <!-- Recent Chats -->
        <div class="section">
          <div class="section-title">Recent Chats</div>
          <div class="nav-item" @click="navigateTo({ path: '/', query: { action: 'recent' } })">💬 最近聊天</div>
        </div>

        <!-- Projects -->
        <div class="section">
          <div class="section-header">
            <span class="section-title">Projects</span>
            <button class="add-btn" @click="showNewProjectDialog = true" title="新建项目">+</button>
          </div>
          <div
            v-for="project in projects"
            :key="project.id"
            class="nav-item project-item"
            @click="selectProject(project.id)"
          >
            📁 {{ project.name }}
          </div>
          <div v-if="projects.length === 0" class="empty-text">暂无项目，点击+新建</div>
        </div>

        <!-- Knowledge Base -->
        <div class="section">
          <div class="section-title">Knowledge Base</div>
          <div class="nav-item" @click="navigateTo('/knowledge')">📚 知识库</div>
        </div>

        <!-- Experience -->
        <div class="section">
          <div class="section-title">Experience</div>
          <div class="nav-item" @click="navigateTo('/experience')">💡 经验</div>
        </div>

        <!-- Interview -->
        <div class="section">
          <div class="section-title">Interview</div>
          <div class="nav-item" @click="navigateTo('/interview')">🎯 面试</div>
        </div>

        <!-- Documents -->
        <div class="section">
          <div class="section-title">Documents</div>
          <div class="nav-item" @click="navigateTo('/documents')">📄 文档</div>
        </div>
      </div>

      <!-- 底部：设置 -->
      <div class="sidebar-footer">
        <div class="nav-item" @click="navigateTo('/settings')">⚙️ Settings</div>
      </div>
    </aside>

    <!-- 中间内容区 -->
    <main class="main-content">
      <slot />
    </main>

    <!-- 右侧：Project Context（可折叠） -->
    <aside class="context-panel" :class="{ collapsed: rightPanelCollapsed }">
      <div class="panel-header">
        <span>Project Context</span>
        <button class="collapse-btn" @click="rightPanelCollapsed = !rightPanelCollapsed">
          {{ rightPanelCollapsed ? '«' : '»' }}
        </button>
      </div>
      <div v-if="!rightPanelCollapsed" class="panel-content">
        <slot name="context" />
      </div>
    </aside>

    <!-- 新建项目对话框 -->
    <div v-if="showNewProjectDialog" class="dialog-overlay" @click.self="showNewProjectDialog = false">
      <div class="dialog">
        <h3>新建项目</h3>
        <input v-model="newProjectName" placeholder="项目名称" @keyup.enter="createProject" />
        <textarea v-model="newProjectDesc" placeholder="项目描述（可选）" rows="2"></textarea>
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

/* 左侧边栏 */
.sidebar {
  width: 260px;
  background: #fff;
  border-right: 1px solid #e5e5e5;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
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
  padding: 4px 8px;
  border-radius: 6px;
}

.user-avatar:hover {
  background: #f0f0f0;
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
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 12px;
  color: #999;
  margin-bottom: 6px;
  text-transform: uppercase;
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

/* 中间内容 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 右侧面板 */
.context-panel {
  width: 280px;
  background: #fff;
  border-left: 1px solid #e5e5e5;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width 0.3s;
}

.context-panel.collapsed {
  width: 40px;
}

.panel-header {
  padding: 16px 20px;
  font-weight: 600;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.collapse-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 16px;
  padding: 0 4px;
}

.collapse-btn:hover {
  color: #000;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* 对话框 */
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

.dialog input,
.dialog textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  margin-bottom: 12px;
  font-family: inherit;
  resize: vertical;
}

.dialog input:focus,
.dialog textarea:focus {
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
