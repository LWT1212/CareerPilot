<!-- 知识库页面 - 开发顺序：Step 8 -->
<!-- 功能：上传文档，查看文档列表，删除文档，知识检索 -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getDocuments, uploadDocument, deleteDocument, searchKnowledge } from '../api/knowledge'
import { ElMessage } from 'element-plus'

const route = useRoute()
const projectId = route.params.id as string

const documents = ref<any[]>([])
const loading = ref(false)
const searchQuery = ref('')
const searchResults = ref<any[]>([])

onMounted(async () => {
  await loadDocuments()
})

// 加载文档列表
const loadDocuments = async () => {
  loading.value = true
  try {
    const response = await getDocuments(projectId)
    documents.value = response.data
  } catch (error) {
    console.error('加载文档失败', error)
  } finally {
    loading.value = false
  }
}

// 上传文档
const handleUpload = async (file: File) => {
  try {
    await uploadDocument(projectId, file)
    ElMessage.success('上传成功')
    await loadDocuments()
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

// 删除文档
const handleDelete = async (docId: string) => {
  try {
    await deleteDocument(projectId, docId)
    ElMessage.success('删除成功')
    await loadDocuments()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 知识检索
const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  try {
    const response = await searchKnowledge(projectId, searchQuery.value)
    searchResults.value = response.data.results
  } catch (error) {
    console.error('检索失败', error)
  }
}
</script>

<template>
  <div class="knowledge-page">
    <!-- 上传区域 -->
    <div class="upload-section">
      <h3>知识库管理</h3>
      <el-upload
        :before-upload="handleUpload"
        :show-file-list="false"
        accept=".pdf,.docx,.md,.txt"
      >
        <el-button type="primary">上传文档</el-button>
      </el-upload>
    </div>

    <!-- 文档列表 -->
    <div class="document-list" v-loading="loading">
      <div v-if="documents.length === 0" class="empty">
        <p>还没有文档，点击上方按钮上传</p>
      </div>
      <div v-for="doc in documents" :key="doc.id" class="document-item">
        <div class="doc-info">
          <strong>{{ doc.filename }}</strong>
          <span class="doc-type">{{ doc.file_type }}</span>
          <el-tag size="small" :type="doc.embedding_status === 'completed' ? 'success' : 'warning'">
            {{ doc.embedding_status }}
          </el-tag>
        </div>
        <el-button type="danger" size="small" @click="handleDelete(doc.id)">删除</el-button>
      </div>
    </div>

    <!-- 知识检索 -->
    <div class="search-section">
      <h3>知识检索</h3>
      <div class="search-box">
        <el-input v-model="searchQuery" placeholder="输入关键词搜索..." @keyup.enter="handleSearch" />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>
      <div v-if="searchResults.length > 0" class="search-results">
        <div v-for="(result, index) in searchResults" :key="index" class="result-item">
          <strong>{{ result.filename }}</strong>
          <p>{{ result.content }}</p>
          <span class="score">相似度: {{ (result.score * 100).toFixed(0) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.knowledge-page {
  padding: 20px;
}

.upload-section, .search-section {
  background: white;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.upload-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.document-list {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
}

.document-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.doc-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.doc-type {
  color: #999;
  font-size: 12px;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-results {
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.result-item {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 10px;
}

.score {
  color: #667eea;
  font-size: 12px;
}

.empty {
  text-align: center;
  color: #999;
  padding: 40px;
}
</style>
