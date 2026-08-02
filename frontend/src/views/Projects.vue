<!-- 项目列表页面 -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Layout from '../components/Layout.vue'
import api from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const projects = ref<any[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const newProject = ref({ name: '', description: '' })

onMounted(async () => {
  await loadProjects()
})

const loadProjects = async () => {
  loading.value = true
  try {
    const response = await api.get('/projects')
    projects.value = response.data.items || []
  } catch (error) {
    console.error('加载项目失败', error)
  } finally {
    loading.value = false
  }
}

const createProject = async () => {
  if (!newProject.value.name.trim()) return
  try {
    await api.post('/projects', newProject.value)
    ElMessage.success('项目创建成功')
    showCreateDialog.value = false
    newProject.value = { name: '', description: '' }
    await loadProjects()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const openProject = (id: string) => {
  localStorage.setItem('current_project_id', id)
  router.push('/')
}
</script>

<template>
  <Layout>
    <div class="projects-page">
      <div class="page-header">
        <h1>📁 项目列表</h1>
        <p>管理你的长期项目</p>
        <button class="add-btn" @click="showCreateDialog = true">+ 新建项目</button>
      </div>

      <div class="project-grid" v-loading="loading">
        <div v-if="projects.length === 0 && !loading" class="empty">
          <p>还没有项目，点击"新建项目"开始！</p>
        </div>
        <div v-for="project in projects" :key="project.id" class="project-card" @click="openProject(project.id)">
          <h3>{{ project.icon }} {{ project.name }}</h3>
          <p>{{ project.description || '暂无描述' }}</p>
        </div>
      </div>

      <!-- 新建项目对话框 -->
      <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
        <div class="dialog">
          <h3>新建项目</h3>
          <input v-model="newProject.name" placeholder="项目名称" />
          <textarea v-model="newProject.description" placeholder="项目描述（可选）" rows="3"></textarea>
          <div class="dialog-actions">
            <button class="cancel-btn" @click="showCreateDialog = false">取消</button>
            <button class="confirm-btn" @click="createProject">创建</button>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<style scoped>
.projects-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 24px;
  margin-bottom: 8px;
  color: #333;
}

.page-header p {
  color: #999;
  margin-bottom: 20px;
}

.add-btn {
  padding: 10px 24px;
  background: #000;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.project-card {
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 25px;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
}

.project-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.project-card h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.project-card p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.empty {
  grid-column: 1 / -1;
  text-align: center;
  color: #999;
  padding: 60px;
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
