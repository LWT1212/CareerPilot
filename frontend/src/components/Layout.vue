<!-- ChatGPT风格布局 - 主布局组件 -->

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const sidebarCollapsed = ref(false)
const activeMenu = ref('chat')

// 菜单项
const menuItems = [
  { id: 'chat', icon: '💬', label: '聊天', path: '/chat' },
  { id: 'knowledge', icon: '📚', label: '知识库', path: '/knowledge' },
  { id: 'experience', icon: '💡', label: '经验', path: '/experience' },
  { id: 'interview', icon: '🎯', label: '面试', path: '/interview' },
  { id: 'documents', icon: '📄', label: '文档', path: '/documents' },
]

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 导航
const navigate = (path: string) => {
  activeMenu.value = path.substring(1)
  router.push(path)
}

// 退出登录
const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <button class="toggle-btn" @click="toggleSidebar">
          {{ sidebarCollapsed ? '☰' : '✕' }}
        </button>
        <span v-if="!sidebarCollapsed" class="logo">CareerPilot AI</span>
      </div>

      <nav class="sidebar-nav" v-if="!sidebarCollapsed">
        <div
          v-for="item in menuItems"
          :key="item.id"
          class="nav-item"
          :class="{ active: activeMenu === item.id }"
          @click="navigate(item.path)"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </div>
      </nav>

      <div class="sidebar-footer" v-if="!sidebarCollapsed">
        <div class="user-info">
          <span>{{ authStore.user?.username || '用户' }}</span>
        </div>
        <button class="logout-btn" @click="logout">退出</button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 260px;
  background: #171717;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #2a2a2a;
}

.toggle-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  padding: 5px;
}

.logo {
  font-size: 16px;
  font-weight: bold;
  color: #fff;
}

.sidebar-nav {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 5px;
}

.nav-item:hover {
  background: #2a2a2a;
}

.nav-item.active {
  background: #343541;
}

.nav-icon {
  font-size: 18px;
}

.nav-label {
  font-size: 14px;
}

.sidebar-footer {
  padding: 15px;
  border-top: 1px solid #2a2a2a;
}

.user-info {
  font-size: 14px;
  color: #999;
  margin-bottom: 10px;
}

.logout-btn {
  width: 100%;
  padding: 8px;
  background: #2a2a2a;
  border: none;
  border-radius: 6px;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
}

.logout-btn:hover {
  background: #3a3a3a;
}

.main-content {
  flex: 1;
  background: #212121;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
