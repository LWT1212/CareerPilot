<!-- 主布局 - 按照PRD页面设计 -->
<!-- 左侧：导航栏（项目可展开显示聊天和文档）| 中间：内容区 | 右侧：Project Context -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useProjectStore } from '../stores/project'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()
const projectStore = useProjectStore()

const rightPanelCollapsed = ref(false)
const projects = ref<any[]>([])
const showNewProjectDialog = ref(false)
const newProjectName = ref('')
const newProjectDesc = ref('')

// 当前展开的项目ID
const expandedProjectId = ref<string>('')
// 每个展开项目的详细数据 { projectId: { chats: [], docs: [] } }
const projectDetails = ref<Record<string, { chats: any[]; docs: any[] }>>({})

onMounted(async () => {
  await loadProjects()
  if (projectStore.currentProjectId) {
    await projectStore.loadProjectDetail()
  }
})

// 加载项目列表
const loadProjects = async () => {
  try {
    const response = await api.get('/projects')
    projects.value = response.data.items || []
    // 恢复上次展开的项目
    if (projectStore.currentProjectId) {
      expandedProjectId.value = projectStore.currentProjectId
      await toggleProject(projects.value.find(p => p.id === projectStore.currentProjectId), false)
    }
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

// 展开/折叠项目
const toggleProject = async (project: any, forceLoad: boolean = true) => {
  if (!project) return

  // 如果点击的是其他项目，先切换项目上下文
  if (project.id !== projectStore.currentProjectId) {
    await projectStore.setProject(project.id)
  }

  // 展开/折叠切换
  if (expandedProjectId.value === project.id) {
    expandedProjectId.value = ''
  } else {
    expandedProjectId.value = project.id
    if (!projectDetails.value[project.id] || forceLoad) {
      await loadProjectDetails(project.id)
    }
  }
}

// 加载展开项目的聊天和文档
const loadProjectDetails = async (projectId: string) => {
  try {
    const [chatsRes, docsRes] = await Promise.all([
      api.get(`/projects/${projectId}/chats`),
      api.get(`/projects/${projectId}/knowledge`),
    ])
    projectDetails.value[projectId] = {
      chats: chatsRes.data.items || chatsRes.data || [],
      docs: docsRes.data || [],
    }
  } catch (error) {
    console.error('加载项目详情失败', error)
  }
}

// 点击项目下的聊天
const selectChat = async (chat: any) => {
  if (projectStore.currentProjectId !== chat.project_id) {
    await projectStore.setProject(chat.project_id)
  }
  await projectStore.selectChat(chat)
  router.push('/')
}

// 点击"+ New Chat"（触发新聊天）
const handleNewChat = () => {
  projectStore.requestNewChat()
  router.push('/')
}

// 点击项目下的文档 → 进入知识库
const goToKnowledge = () => {
  navigateTo('/knowledge')
}

// 退出登录
const logout = () => {
  projectStore.clear()
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
        <button class="new-chat-btn" @click="handleNewChat">
          + New Chat
        </button>

        <!-- Projects（可展开） -->
        <div class="section">
          <div class="section-header">
            <span class="section-title">Projects</span>
            <button class="add-btn" @click="showNewProjectDialog = true" title="新建项目">+</button>
          </div>

          <!-- 项目列表 -->
          <div
            v-for="project in projects"
            :key="project.id"
            class="project-tree"
          >
            <!-- 项目行（点击展开/折叠） -->
            <div
              class="project-row"
              :class="{ expanded: expandedProjectId === project.id, active: projectStore.currentProjectId === project.id }"
              @click="toggleProject(project)"
            >
              <span class="arrow">{{ expandedProjectId === project.id ? '▼' : '▶' }}</span>
              <span class="project-icon">📁</span>
              <span class="project-name">{{ project.name }}</span>
            </div>

            <!-- 展开的内容：聊天 + 文档 -->
            <div v-if="expandedProjectId === project.id" class="project-details">
              <!-- 该项目的聊天 -->
              <div class="detail-label">💬 聊天</div>
              <div
                v-for="chat in projectDetails[project.id]?.chats || []"
                :key="chat.id"
                class="detail-item"
                :class="{ active: projectStore.currentChat?.id === chat.id }"
                @click="selectChat(chat)"
              >
                {{ chat.title || '新聊天' }}
              </div>
              <div
                v-if="(projectDetails[project.id]?.chats || []).length === 0"
                class="detail-empty"
              >暂无聊天</div>

              <!-- 该项目的文档 -->
              <div class="detail-label">📄 文档</div>
              <div
                v-for="doc in projectDetails[project.id]?.docs || []"
                :key="doc.id"
                class="detail-item"
                @click="goToKnowledge"
              >
                {{ doc.filename }}
              </div>
              <div
                v-if="(projectDetails[project.id]?.docs || []).length === 0"
                class="detail-empty"
              >暂无文档，点击上方知识库上传</div>
            </div>
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
  width: 280px;
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

/* 项目树 */
.project-tree {
  margin-bottom: 4px;
}

.project-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.project-row:hover {
  background: #f0f0f0;
}

.project-row.active {
  background: #e8e8e8;
}

.arrow {
  font-size: 10px;
  color: #999;
  width: 12px;
}

.project-icon {
  font-size: 16px;
}

.project-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 展开的详情 */
.project-details {
  padding-left: 24px;
  margin-bottom: 8px;
}

.detail-label {
  font-size: 11px;
  color: #999;
  padding: 8px 0 4px 8px;
  text-transform: uppercase;
}

.detail-item {
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #555;
}

.detail-item:hover {
  background: #f0f0f0;
}

.detail-item.active {
  background: #e8e8e8;
  color: #333;
}

.detail-empty {
  padding: 6px 12px;
  font-size: 12px;
  color: #bbb;
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
