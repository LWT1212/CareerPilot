<!-- 项目详情页 - 开发顺序：Step 6 -->
<!-- 功能：项目入口，跳转到各个子模块 -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id as string

const project = ref<any>(null)

onMounted(async () => {
  await loadProject()
})

const loadProject = async () => {
  try {
    const response = await api.get(`/projects/${projectId}`)
    project.value = response.data
  } catch (error) {
    console.error('加载项目失败', error)
  }
}

// 导航到子模块
const navigateTo = (path: string) => {
  router.push(path)
}
</script>

<template>
  <div class="project-page" v-if="project">
    <header>
      <button @click="router.push('/')">← 返回</button>
      <h1>{{ project.icon }} {{ project.name }}</h1>
      <p>{{ project.description }}</p>
    </header>

    <main>
      <div class="module-grid">
        <!-- 聊天模块 -->
        <div class="module-card" @click="navigateTo(`/projects/${projectId}/chat`)">
          <div class="module-icon">💬</div>
          <h3>聊天</h3>
          <p>与AI助手对话，获取帮助</p>
        </div>

        <!-- 知识库模块 -->
        <div class="module-card" @click="navigateTo(`/projects/${projectId}/knowledge`)">
          <div class="module-icon">📚</div>
          <h3>知识库</h3>
          <p>管理项目文档和知识</p>
        </div>

        <!-- 经验模块 -->
        <div class="module-card" @click="navigateTo(`/projects/${projectId}/experience`)">
          <div class="module-icon">💡</div>
          <h3>经验</h3>
          <p>记录开发经验和问题</p>
        </div>

        <!-- 面试模块 -->
        <div class="module-card" @click="navigateTo(`/projects/${projectId}/interview`)">
          <div class="module-icon">🎯</div>
          <h3>面试</h3>
          <p>管理面试记录和成长</p>
        </div>

        <!-- 文档模块 -->
        <div class="module-card" @click="navigateTo(`/projects/${projectId}/documents`)">
          <div class="module-icon">📄</div>
          <h3>文档</h3>
          <p>AI自动生成项目文档</p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.project-page {
  min-height: 100vh;
  background: #f5f7fa;
}

header {
  background: white;
  padding: 30px 40px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

header button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #667eea;
  margin-bottom: 10px;
}

header h1 {
  margin: 0 0 10px 0;
  color: #333;
}

header p {
  margin: 0;
  color: #666;
}

main {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.module-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  text-align: center;
}

.module-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.module-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.module-card h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.module-card p {
  margin: 0;
  color: #666;
  font-size: 14px;
}
</style>
