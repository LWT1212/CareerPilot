<!-- 面试模块页面 - 开发顺序：Step 10 -->
<!-- 功能：查看面试列表，添加面试，查看统计 -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getInterviews, createInterview, deleteInterview, getInterviewStats } from '../api/interview'
import { ElMessage } from 'element-plus'

const route = useRoute()
const projectId = route.params.id as string

const interviews = ref<any[]>([])
const stats = ref<any>(null)
const loading = ref(false)
const showCreateDialog = ref(false)
const newInterview = ref({
  company: '',
  position: '',
  interview_date: '',
  result: '',
  overall_feedback: ''
})

const results = [
  { value: 'offer', label: 'Offer' },
  { value: 'rejected', label: '被拒' },
  { value: 'pending', label: '待定' },
  { value: 'ghosted', label: '无回复' }
]

onMounted(async () => {
  await loadInterviews()
  await loadStats()
})

// 加载面试列表
const loadInterviews = async () => {
  loading.value = true
  try {
    const response = await getInterviews(projectId)
    interviews.value = response.data
  } catch (error) {
    console.error('加载面试失败', error)
  } finally {
    loading.value = false
  }
}

// 加载统计
const loadStats = async () => {
  try {
    const response = await getInterviewStats(projectId)
    stats.value = response.data
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

// 创建面试
const handleCreate = async () => {
  try {
    await createInterview(projectId, newInterview.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    newInterview.value = { company: '', position: '', interview_date: '', result: '', overall_feedback: '' }
    await loadInterviews()
    await loadStats()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

// 删除面试
const handleDelete = async (id: string) => {
  try {
    await deleteInterview(projectId, id)
    ElMessage.success('删除成功')
    await loadInterviews()
    await loadStats()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}
</script>

<template>
  <div class="interview-page">
    <!-- 统计卡片 -->
    <div class="stats-section" v-if="stats">
      <div class="stat-card">
        <h4>面试总数</h4>
        <p>{{ stats.total_interviews }}</p>
      </div>
      <div class="stat-card">
        <h4>问题总数</h4>
        <p>{{ stats.total_questions }}</p>
      </div>
      <div class="stat-card">
        <h4>薄弱领域</h4>
        <p>{{ stats.weak_areas.length }}</p>
      </div>
    </div>

    <!-- 头部 -->
    <div class="header">
      <h3>面试记录</h3>
      <el-button type="primary" @click="showCreateDialog = true">添加面试</el-button>
    </div>

    <!-- 面试列表 -->
    <div class="interview-list" v-loading="loading">
      <div v-if="interviews.length === 0" class="empty">
        <p>还没有面试记录</p>
      </div>
      <div v-for="item in interviews" :key="item.id" class="interview-item">
        <div class="item-header">
          <h4>{{ item.company }} - {{ item.position }}</h4>
          <el-button type="danger" size="small" @click="handleDelete(item.id)">删除</el-button>
        </div>
        <div class="item-meta">
          <span v-if="item.interview_date">📅 {{ item.interview_date }}</span>
          <el-tag v-if="item.result" :type="item.result === 'offer' ? 'success' : 'danger'">
            {{ item.result }}
          </el-tag>
        </div>
        <p v-if="item.overall_feedback" class="feedback">{{ item.overall_feedback }}</p>
      </div>
    </div>

    <!-- 薄弱领域 -->
    <div class="weak-section" v-if="stats && stats.weak_areas.length > 0">
      <h3>薄弱领域</h3>
      <div class="weak-list">
        <div v-for="weak in stats.weak_areas" :key="weak.category" class="weak-item">
          <span>{{ weak.category }}</span>
          <el-tag type="danger">{{ weak.count }} 个问题</el-tag>
        </div>
      </div>
    </div>

    <!-- 创建对话框 -->
    <el-dialog v-model="showCreateDialog" title="添加面试记录">
      <el-form :model="newInterview">
        <el-form-item label="公司">
          <el-input v-model="newInterview.company" placeholder="公司名称" />
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="newInterview.position" placeholder="应聘职位" />
        </el-form-item>
        <el-form-item label="面试日期">
          <el-date-picker v-model="newInterview.interview_date" type="date" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="结果">
          <el-select v-model="newInterview.result" placeholder="选择结果">
            <el-option v-for="r in results" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="反馈">
          <el-input v-model="newInterview.overall_feedback" type="textarea" placeholder="面试反馈" />
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
.interview-page {
  padding: 20px;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
}

.stat-card h4 {
  color: #666;
  margin-bottom: 10px;
}

.stat-card p {
  font-size: 24px;
  color: #667eea;
  font-weight: bold;
  margin: 0;
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

.interview-list {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
}

.interview-item {
  padding: 20px 0;
  border-bottom: 1px solid #eee;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.item-meta {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 10px;
  color: #666;
  font-size: 14px;
}

.feedback {
  color: #666;
  font-style: italic;
}

.weak-section {
  background: white;
  border-radius: 10px;
  padding: 20px;
}

.weak-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
}

.weak-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background: #fef0f0;
  border-radius: 6px;
}

.empty {
  text-align: center;
  color: #999;
  padding: 40px;
}
</style>
