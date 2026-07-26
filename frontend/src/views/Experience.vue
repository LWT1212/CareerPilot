<!-- 经验管理页面 - ChatGPT风格 -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Layout from '../components/Layout.vue'
import { getExperiences, createExperience, deleteExperience } from '../api/experience'
import { ElMessage } from 'element-plus'

const experiences = ref<any[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const newExperience = ref({ title: '', type: 'bug', content: '', solution: '' })

const types = [
  { value: 'bug', label: 'Bug' },
  { value: 'solution', label: '解决方案' },
  { value: 'architecture', label: '架构决策' },
  { value: 'lesson', label: '学习总结' },
]

onMounted(async () => {
  await loadExperiences()
})

const loadExperiences = async () => {
  loading.value = true
  try {
    const response = await getExperiences('current')
    experiences.value = response.data
  } catch (error) {
    console.error('加载经验失败', error)
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  try {
    await createExperience('current', newExperience.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    newExperience.value = { title: '', type: 'bug', content: '', solution: '' }
    await loadExperiences()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const handleDelete = async (id: string) => {
  try {
    await deleteExperience('current', id)
    ElMessage.success('删除成功')
    await loadExperiences()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}
</script>

<template>
  <Layout>
    <div class="experience-page">
      <div class="page-header">
        <h1>💡 开发经验</h1>
        <p>记录开发过程中的问题和解决方案</p>
        <button class="add-btn" @click="showCreateDialog = true">+ 添加经验</button>
      </div>

      <div class="experience-list" v-loading="loading">
        <div v-if="experiences.length === 0" class="empty">
          <p>还没有经验记录</p>
        </div>
        <div v-for="exp in experiences" :key="exp.id" class="experience-item">
          <div class="exp-header">
            <div>
              <span class="exp-type">{{ exp.type }}</span>
              <h3>{{ exp.title }}</h3>
            </div>
            <button class="delete-btn" @click="handleDelete(exp.id)">×</button>
          </div>
          <p class="exp-content">{{ exp.content }}</p>
          <div v-if="exp.solution" class="exp-solution">
            <strong>解决方案：</strong>{{ exp.solution }}
          </div>
        </div>
      </div>

      <!-- 创建对话框 -->
      <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
        <div class="dialog">
          <h2>添加经验</h2>
          <input v-model="newExperience.title" placeholder="标题" />
          <select v-model="newExperience.type">
            <option v-for="t in types" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select>
          <textarea v-model="newExperience.content" placeholder="详细描述" rows="4"></textarea>
          <textarea v-model="newExperience.solution" placeholder="解决方案（可选）" rows="3"></textarea>
          <div class="dialog-actions">
            <button class="cancel-btn" @click="showCreateDialog = false">取消</button>
            <button class="confirm-btn" @click="handleCreate">创建</button>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<style scoped>
.experience-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 { font-size: 28px; margin-bottom: 10px; }
.page-header p { color: #8e8ea0; margin-bottom: 20px; }

.add-btn {
  background: #fff;
  color: #000;
  border: none;
  border-radius: 8px;
  padding: 10px 24px;
  cursor: pointer;
  font-weight: bold;
}

.experience-item {
  background: #171717;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 15px;
}

.exp-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.exp-type {
  background: #343541;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: #8e8ea0;
}

.exp-header h3 { margin: 8px 0 0 0; }

.delete-btn {
  background: none;
  border: none;
  color: #8e8ea0;
  font-size: 20px;
  cursor: pointer;
}

.delete-btn:hover { color: #ef4444; }

.exp-content { color: #ccc; line-height: 1.6; }

.exp-solution {
  background: #2a2a2a;
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 12px;
  font-size: 14px;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: #171717;
  border-radius: 12px;
  padding: 30px;
  width: 500px;
}

.dialog h2 { margin-bottom: 20px; }

.dialog input, .dialog textarea, .dialog select {
  width: 100%;
  background: #40414f;
  border: none;
  border-radius: 8px;
  padding: 12px;
  color: #fff;
  margin-bottom: 15px;
  font-family: inherit;
  outline: none;
}

.dialog-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.cancel-btn {
  background: #2a2a2a;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  cursor: pointer;
}

.confirm-btn {
  background: #fff;
  color: #000;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  cursor: pointer;
  font-weight: bold;
}

.empty { text-align: center; color: #8e8ea0; padding: 60px; }
</style>
