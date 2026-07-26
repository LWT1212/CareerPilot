<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()

const projects = ref<any[]>([])
const loading = ref(false)
const showDialog = ref(false)
const newProject = ref({ name: '', description: '' })

onMounted(async () => {
  await loadProjects()
})

const loadProjects = async () => {
  loading.value = true
  try {
    const response = await api.get('/projects')
    projects.value = response.data.items
  } catch (error) {
    console.error('加载项目失败', error)
  } finally {
    loading.value = false
  }
}

const createProject = async () => {
  try {
    await api.post('/projects', newProject.value)
    showDialog.value = false
    newProject.value = { name: '', description: '' }
    await loadProjects()
  } catch (error) {
    console.error('创建项目失败', error)
  }
}

const openProject = (id: string) => {
  router.push(`/projects/${id}`)
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="home">
    <header>
      <h1>CareerPilot AI</h1>
      <button @click="logout">退出登录</button>
    </header>

    <main>
      <div class="projects-header">
        <h2>我的项目</h2>
        <el-button type="primary" @click="showDialog = true">新建项目</el-button>
      </div>

      <div class="projects-grid" v-loading="loading">
        <div v-for="project in projects" :key="project.id" class="project-card" @click="openProject(project.id)">
          <h3>{{ project.icon }} {{ project.name }}</h3>
          <p>{{ project.description || '暂无描述' }}</p>
          <span>{{ project.status }}</span>
        </div>

        <div v-if="projects.length === 0 && !loading" class="empty">
          <p>还没有项目，点击"新建项目"开始吧！</p>
        </div>
      </div>
    </main>

    <!-- 新建项目对话框 -->
    <el-dialog v-model="showDialog" title="新建项目">
      <el-form :model="newProject">
        <el-form-item label="项目名称">
          <el-input v-model="newProject.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="newProject.description" type="textarea" placeholder="请输入项目描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="createProject">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
  background: #f5f7fa;
}

header {
  background: white;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

.projects-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.project-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s;
}

.project-card:hover {
  transform: translateY(-5px);
}

.project-card h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.project-card p {
  color: #666;
  margin: 0 0 10px 0;
}

.project-card span {
  color: #409eff;
  font-size: 12px;
}

.empty {
  text-align: center;
  padding: 60px;
  color: #999;
}
</style>
