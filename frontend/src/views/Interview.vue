<!-- 面试模块页面 - ChatGPT风格 -->

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import Layout from '../components/Layout.vue'
import { useProjectStore } from '../stores/project'
import { getInterviews, getInterview, createInterview, deleteInterview, getInterviewStats, addQuestion } from '../api/interview'
import { ElMessage } from 'element-plus'

const projectStore = useProjectStore()
const projectId = ref(projectStore.currentProjectId)

const interviews = ref<any[]>([])
const stats = ref<any>(null)
const loading = ref(false)
const showCreateDialog = ref(false)
const newInterview = ref({ company: '', position: '', interview_date: '', result: '', overall_feedback: '' })

// 面试问题相关状态
const expandedInterview = ref<string>('')        // 当前展开的面试ID
const interviewDetail = ref<any>(null)           // 面试详情（含问题）
const showQuestionDialog = ref(false)            // 添加问题弹窗
const currentInterviewId = ref('')               // 当前添加问题的面试
const newQuestion = ref({
  question: '',
  user_answer: '',
  category: '',
  difficulty: 'medium',
  rating: 3,
  interviewer_feedback: '',
})

// 展开/收起面试，加载问题列表
const toggleExpand = async (interviewId: string) => {
  if (expandedInterview.value === interviewId) {
    expandedInterview.value = ''
    return
  }
  expandedInterview.value = interviewId
  try {
    const res = await getInterview(projectId.value, interviewId)
    interviewDetail.value = res.data
  } catch (error) {
    console.error('加载面试详情失败', error)
  }
}

// 打开添加问题弹窗
const openQuestionDialog = (interviewId: string) => {
  currentInterviewId.value = interviewId
  newQuestion.value = { question: '', user_answer: '', category: '', difficulty: 'medium', rating: 3, interviewer_feedback: '' }
  showQuestionDialog.value = true
}

// 添加问题（触发AI薄弱点分析）
const handleAddQuestion = async () => {
  try {
    await addQuestion(currentInterviewId.value, newQuestion.value)
    ElMessage.success('问题已添加，AI正在分析薄弱点...')
    showQuestionDialog.value = false
    // 刷新详情和统计
    const res = await getInterview(projectId.value, currentInterviewId.value)
    interviewDetail.value = res.data
    await loadStats()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

onMounted(async () => {
  await loadInterviews()
  await loadStats()
})

// 监听项目切换，自动刷新数据
watch(
  () => projectStore.currentProjectId,
  () => {
    projectId.value = projectStore.currentProjectId
    loadInterviews()
    loadStats()
  }
)

const loadInterviews = async () => {
  loading.value = true
  try {
    const response = await getInterviews(projectId.value)
    interviews.value = response.data
  } catch (error) {
    console.error('加载面试失败', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await getInterviewStats(projectId.value)
    stats.value = response.data
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

const handleCreate = async () => {
  try {
    await createInterview(projectId.value, newInterview.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    newInterview.value = { company: '', position: '', interview_date: '', result: '', overall_feedback: '' }
    await loadInterviews()
    await loadStats()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const handleDelete = async (id: string) => {
  try {
    await deleteInterview(projectId.value, id)
    ElMessage.success('删除成功')
    await loadInterviews()
    await loadStats()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}
</script>

<template>
  <Layout>
    <div class="interview-page">
      <div class="page-header">
        <h1>🎯 面试管理</h1>
        <p>记录面试经历，持续提升</p>
        <button class="add-btn" @click="showCreateDialog = true">+ 添加面试</button>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid" v-if="stats">
        <div class="stat-card">
          <span class="stat-value">{{ stats.total_interviews }}</span>
          <span class="stat-label">面试总数</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ stats.total_questions }}</span>
          <span class="stat-label">问题总数</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ stats.weak_areas.length }}</span>
          <span class="stat-label">薄弱领域</span>
        </div>
      </div>

      <!-- 面试列表 -->
      <div class="interview-list" v-loading="loading">
        <div v-if="interviews.length === 0" class="empty">
          <p>还没有面试记录</p>
        </div>
        <div v-for="item in interviews" :key="item.id" class="interview-item">
          <div class="item-header">
            <div>
              <h3>{{ item.company }}</h3>
              <p>{{ item.position }}</p>
            </div>
            <div class="item-actions">
              <button class="expand-btn" @click="toggleExpand(item.id)">
                {{ expandedInterview === item.id ? '收起 ▲' : '查看问题 ▼' }}
              </button>
              <button class="add-q-btn" @click="openQuestionDialog(item.id)">+ 添加问题</button>
              <button class="delete-btn" @click="handleDelete(item.id)">×</button>
            </div>
          </div>
          <div class="item-meta">
            <span v-if="item.interview_date">📅 {{ item.interview_date }}</span>
            <span v-if="item.result" class="result-badge" :class="item.result">{{ item.result }}</span>
          </div>
          <p v-if="item.overall_feedback" class="feedback">{{ item.overall_feedback }}</p>

          <!-- 展开的问题列表 -->
          <div v-if="expandedInterview === item.id" class="question-list">
            <div v-if="!interviewDetail || interviewDetail.questions.length === 0" class="question-empty">
              暂无问题，点击"+ 添加问题"记录面试题
            </div>
            <div v-for="q in interviewDetail?.questions || []" :key="q.id" class="question-item">
              <div class="q-header">
                <span class="q-category">{{ q.category || '未分类' }}</span>
                <span class="q-difficulty">{{ q.difficulty }}</span>
                <span class="q-rating" :class="q.rating <= 2 ? 'weak' : ''">评分 {{ q.rating }}/5</span>
              </div>
              <div class="q-text">{{ q.question }}</div>
              <div v-if="q.user_answer" class="q-answer">
                <strong>我的回答：</strong>{{ q.user_answer }}
              </div>
              <div v-if="q.interviewer_feedback" class="q-feedback">
                <strong>面试官反馈：</strong>{{ q.interviewer_feedback }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 薄弱领域 -->
      <div class="weak-section" v-if="stats && stats.weak_areas.length > 0">
        <h2>⚠️ 薄弱领域</h2>
        <div class="weak-list">
          <div v-for="weak in stats.weak_areas" :key="weak.category" class="weak-item">
            <span>{{ weak.category }}</span>
            <span class="weak-count">{{ weak.count }} 个问题</span>
          </div>
        </div>
      </div>

      <!-- 创建对话框 -->
      <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
        <div class="dialog">
          <h2>添加面试记录</h2>
          <input v-model="newInterview.company" placeholder="公司名称" />
          <input v-model="newInterview.position" placeholder="应聘职位" />
          <input v-model="newInterview.interview_date" type="date" />
          <select v-model="newInterview.result">
            <option value="">选择结果</option>
            <option value="offer">Offer</option>
            <option value="rejected">被拒</option>
            <option value="pending">待定</option>
          </select>
          <textarea v-model="newInterview.overall_feedback" placeholder="面试反馈" rows="3"></textarea>
          <div class="dialog-actions">
            <button class="cancel-btn" @click="showCreateDialog = false">取消</button>
            <button class="confirm-btn" @click="handleCreate">创建</button>
          </div>
        </div>
      </div>

      <!-- 添加问题弹窗 -->
      <div v-if="showQuestionDialog" class="dialog-overlay" @click.self="showQuestionDialog = false">
        <div class="dialog">
          <h2>添加面试问题</h2>
          <textarea v-model="newQuestion.question" placeholder="面试问题" rows="2"></textarea>
          <textarea v-model="newQuestion.user_answer" placeholder="我的回答（可选）" rows="2"></textarea>
          <input v-model="newQuestion.category" placeholder="分类（如 Redis、系统设计）" />
          <select v-model="newQuestion.difficulty">
            <option value="easy">简单</option>
            <option value="medium">中等</option>
            <option value="hard">困难</option>
          </select>
          <div class="rating-row">
            <label>回答评分：</label>
            <select v-model="newQuestion.rating">
              <option :value="1">1 - 很差</option>
              <option :value="2">2 - 较弱</option>
              <option :value="3">3 - 一般</option>
              <option :value="4">4 - 良好</option>
              <option :value="5">5 - 优秀</option>
            </select>
            <span class="rating-hint">评分≤2会被AI识别为薄弱点</span>
          </div>
          <textarea v-model="newQuestion.interviewer_feedback" placeholder="面试官反馈（可选）" rows="2"></textarea>
          <div class="dialog-actions">
            <button class="cancel-btn" @click="showQuestionDialog = false">取消</button>
            <button class="confirm-btn" @click="handleAddQuestion">添加</button>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<style scoped>
.interview-page {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: #171717;
  border-radius: 12px;
  padding: 25px;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 32px;
  font-weight: bold;
  color: #fff;
  margin-bottom: 5px;
}

.stat-label {
  color: #8e8ea0;
  font-size: 14px;
}

.interview-item {
  background: #171717;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 15px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.item-header h3 { margin: 0; }
.item-header p { color: #8e8ea0; margin: 5px 0 0 0; }

.delete-btn {
  background: none;
  border: none;
  color: #8e8ea0;
  font-size: 20px;
  cursor: pointer;
}

.delete-btn:hover { color: #ef4444; }

.item-meta {
  display: flex;
  gap: 15px;
  align-items: center;
  color: #8e8ea0;
  font-size: 14px;
  margin-bottom: 10px;
}

.result-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  text-transform: uppercase;
}

.result-badge.offer { background: #065f46; color: #10b981; }
.result-badge.rejected { background: #7f1d1d; color: #ef4444; }
.result-badge.pending { background: #78350f; color: #f59e0b; }

.feedback { color: #ccc; font-style: italic; }

.weak-section {
  background: #171717;
  border-radius: 12px;
  padding: 25px;
  margin-top: 30px;
}

.weak-section h2 { font-size: 18px; margin-bottom: 20px; }

.weak-list { display: flex; flex-wrap: wrap; gap: 10px; }

.weak-item {
  background: #7f1d1d;
  padding: 10px 16px;
  border-radius: 8px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.weak-count { color: #fca5a5; font-size: 12px; }

/* Dialog styles */
.dialog-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
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

.item-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.expand-btn, .add-q-btn {
  background: #2a2a2a;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 5px 12px;
  cursor: pointer;
  font-size: 12px;
}

.add-q-btn {
  background: #667eea;
}

.question-list {
  margin-top: 15px;
  border-top: 1px solid #2a2a2a;
  padding-top: 10px;
}

.question-empty {
  color: #8e8ea0;
  font-size: 13px;
  padding: 10px 0;
}

.question-item {
  background: #2a2a2a;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
}

.q-header {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 8px;
}

.q-category {
  background: #343541;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #8e8ea0;
}

.q-difficulty {
  font-size: 12px;
  color: #8e8ea0;
}

.q-rating {
  font-size: 12px;
  color: #10b981;
}

.q-rating.weak {
  color: #ef4444;
  font-weight: bold;
}

.q-text {
  color: #fff;
  margin-bottom: 6px;
}

.q-answer, .q-feedback {
  font-size: 13px;
  color: #ccc;
  margin-top: 4px;
}

.rating-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.rating-row label {
  color: #ccc;
}

.rating-hint {
  font-size: 11px;
  color: #ef4444;
}
