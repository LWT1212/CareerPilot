<!-- 经验管理页面 - 开发顺序：Step 9 -->
<!-- 功能：查看经验列表，添加经验，按类型筛选 -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getExperiences, createExperience, deleteExperience } from '../api/experience'
import { ElMessage } from 'element-plus'

const route = useRoute()
const projectId = route.params.id as string

const experiences = ref<any[]>([])
const loading = ref(false)
const typeFilter = ref('')
const showCreateDialog = ref(false)
const newExperience = ref({
  title: '',
  type: 'bug',
  content: '',
  solution: '',
  tags: []
})

const types = [
  { value: 'bug', label: 'Bug' },
  { value: 'solution', label: '解决方案' },
  { value: 'architecture', label: '架构决策' },
  { value: 'lesson', label: '学习总结' },
  { value: 'note', label: '笔记' }
]

onMounted(async () => {
  await loadExperiences()
})

// 加载经验列表
const loadExperiences = async () => {
  loading.value = true
  try {
    const response = await getExperiences(projectId, typeFilter.value || undefined)
    experiences.value = response.data
  } catch (error) {
    console.error('加载经验失败', error)
  } finally {
    loading.value = false
  }
}

// 创建经验
const handleCreate = async () => {
  try {
    await createExperience(projectId, newExperience.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    newExperience.value = { title: '', type: 'bug', content: '', solution: '', tags: [] }
    await loadExperiences()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

// 删除经验
const handleDelete = async (expId: string) => {
  try {
    await deleteExperience(projectId, expId)
    ElMessage.success('删除成功')
    await loadExperiences()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 筛选类型
const handleFilter = () => {
  loadExperiences()
}
</script>

<template>
  <div class="experience-page">
    <!-- 头部 -->
    <div class="header">
      <h3>开发经验</h3>
      <div class="actions">
        <el-select v-model="typeFilter" placeholder="筛选类型" clearable @change="handleFilter">
          <el-option v-for="t in types" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
        <el-button type="primary" @click="showCreateDialog = true">添加经验</el-button>
      </div>
    </div>

    <!-- 经验列表 -->
    <div class="experience-list" v-loading="loading">
      <div v-if="experiences.length === 0" class="empty">
        <p>还没有经验记录</p>
      </div>
      <div v-for="exp in experiences" :key="exp.id" class="experience-item">
        <div class="exp-header">
          <h4>{{ exp.title }}</h4>
          <div class="exp-meta">
            <el-tag size="small">{{ exp.type }}</el-tag>
            <el-button type="danger" size="small" @click="handleDelete(exp.id)">删除</el-button>
          </div>
        </div>
        <p class="exp-content">{{ exp.content }}</p>
        <div v-if="exp.solution" class="exp-solution">
          <strong>解决方案：</strong>{{ exp.solution }}
        </div>
      </div>
    </div>

    <!-- 创建对话框 -->
    <el-dialog v-model="showCreateDialog" title="添加经验">
      <el-form :model="newExperience">
        <el-form-item label="标题">
          <el-input v-model="newExperience.title" placeholder="经验标题" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="newExperience.type">
            <el-option v-for="t in types" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="newExperience.content" type="textarea" :rows="4" placeholder="详细描述" />
        </el-form-item>
        <el-form-item label="解决方案">
          <el-input v-model="newExperience.solution" type="textarea" :rows="3" placeholder="解决方案（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.experience-page {
  padding: 20px;
}

.header {
  background: white;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  display: flex;
  gap: 10px;
}

.experience-list {
  background: white;
  border-radius: 10px;
  padding: 20px;
}

.experience-item {
  padding: 20px 0;
  border-bottom: 1px solid #eee;
}

.experience-item:last-child {
  border-bottom: none;
}

.exp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.exp-header h4 {
  margin: 0;
  color: #333;
}

.exp-meta {
  display: flex;
  gap: 10px;
  align-items: center;
}

.exp-content {
  color: #666;
  margin-bottom: 10px;
}

.exp-solution {
  background: #f0f9eb;
  padding: 10px 15px;
  border-radius: 6px;
  font-size: 14px;
}

.empty {
  text-align: center;
  color: #999;
  padding: 40px;
}
</style>
