<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id as string

const project = ref<any>(null)
const activeTab = ref('chat')

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
</script>

<template>
  <div class="project-page" v-if="project">
    <header>
      <button @click="router.push('/')">← 返回</button>
      <h1>{{ project.icon }} {{ project.name }}</h1>
    </header>

    <main>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="聊天" name="chat">
          <div class="chat-placeholder">
            <p>聊天功能开发中...</p>
          </div>
        </el-tab-pane>
        <el-tab-pane label="知识库" name="knowledge">
          <div class="placeholder">
            <p>知识库功能开发中...</p>
          </div>
        </el-tab-pane>
        <el-tab-pane label="经验" name="experience">
          <div class="placeholder">
            <p>经验管理功能开发中...</p>
          </div>
        </el-tab-pane>
        <el-tab-pane label="面试" name="interview">
          <div class="placeholder">
            <p>面试模块功能开发中...</p>
          </div>
        </el-tab-pane>
        <el-tab-pane label="文档" name="documents">
          <div class="placeholder">
            <p>文档管理功能开发中...</p>
          </div>
        </el-tab-pane>
      </el-tabs>
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
  padding: 20px 40px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

header button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #667eea;
}

header h1 {
  margin: 0;
  color: #333;
}

main {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.chat-placeholder, .placeholder {
  background: white;
  padding: 60px;
  text-align: center;
  border-radius: 10px;
  color: #999;
}
</style>
