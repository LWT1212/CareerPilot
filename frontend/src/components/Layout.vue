<!-- ChatGPT风格布局 - 按照设计图 -->

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const sidebarCollapsed = ref(false)
const searchQuery = ref('')

const navItems = [
  { id: 'chat', icon: '💬', label: '聊天', path: '/' },
]

const projectItems = [
  { id: 'career', icon: '📁', label: 'CareerPilot' },
  { id: 'resume', icon: '📁', label: 'Resume' },
  { id: 'vision', icon: '📁', label: 'Vision' },
]

const bottomItems = [
  { id: 'knowledge', icon: '📚', label: 'Knowledge Base' },
  { id: 'global-kb', icon: '🌐', label: 'Global KB' },
  { id: 'settings', icon: '⚙️', label: 'Settings', path: '/settings' },
]

const navigate = (path: string) => {
  if (path) router.push(path)
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
          <span class="search-icon">🔍</span>
          <div class="user-avatar" @click="logout">👤</div>
        </div>
      </div>

      <!-- 内容区 -->
      <div class="sidebar-content">
        <!-- 新建聊天 -->
        <div class="new-chat-section">
          <button class="new-chat-btn">+ New Chat</button>
        </div>

        <!-- 最近聊天 -->
        <div class="section">
          <div class="section-title">Recent Chats</div>
          <div class="section-items">
            <div class="nav-item">Redis是什么</div>
            <div class="nav-item">LangGraph</div>
            <div class="nav-item">MCP</div>
          </div>
        </div>

        <!-- 项目 -->
        <div class="section">
          <div class="section-title">Projects</div>
          <div class="section-items">
            <div
              v-for="item in projectItems"
              :key="item.id"
              class="nav-item project-item"
            >
              <span class="nav-icon">{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </div>
          </div>
        </div>

        <!-- 知识库 -->
        <div class="section">
          <div class="section-title">Knowledge Base</div>
          <div class="section-items">
            <div class="nav-item">Global KB</div>
          </div>
        </div>
      </div>

      <!-- 底部设置 -->
      <div class="sidebar-footer">
        <div class="nav-item" @click="navigate('/settings')">
          <span class="nav-icon">⚙️</span>
          <span>Settings</span>
        </div>
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-icon {
  font-size: 18px;
  cursor: pointer;
}

.user-avatar {
  font-size: 20px;
  cursor: pointer;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.new-chat-section {
  margin-bottom: 20px;
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
}

.new-chat-btn:hover {
  background: #f5f5f5;
}

.section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
  padding: 0 8px;
}

.section-items {
  display: flex;
  flex-direction: column;
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

.nav-icon {
  font-size: 16px;
}

.project-item {
  font-size: 13px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #e5e5e5;
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
</style>
