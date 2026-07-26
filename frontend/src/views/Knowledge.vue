<!-- 知识库页面 - ChatGPT风格 -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Layout from '../components/Layout.vue'
import { getDocuments, uploadDocument, deleteDocument, searchKnowledge } from '../api/knowledge'
import { ElMessage } from 'element-plus'

const documents = ref<any[]>([])
const loading = ref(false)
const searchQuery = ref('')
const searchResults = ref<any[]>([])

onMounted(async () => {
  await loadDocuments()
})

const loadDocuments = async () => {
  loading.value = true
  try {
    const response = await getDocuments('current')
    documents.value = response.data
  } catch (error) {
    console.error('加载文档失败', error)
  } finally {
    loading.value = false
  }
}

const handleUpload = async (file: File) => {
  try {
    await uploadDocument('current', file)
    ElMessage.success('上传成功')
    await loadDocuments()
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

const handleDelete = async (docId: string) => {
  try {
    await deleteDocument('current', docId)
    ElMessage.success('删除成功')
    await loadDocuments()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  try {
    const response = await searchKnowledge('current', searchQuery.value)
    searchResults.value = response.data.results
  } catch (error) {
    console.error('检索失败', error)
  }
}
</script>

<template>
  <Layout>
    <div class="knowledge-page">
      <div class="page-header">
        <h1>📚 知识库管理</h1>
        <p>上传文档，构建项目知识库</p>
      </div>

      <!-- 上传区域 -->
      <div class="upload-section">
        <el-upload
          :before-upload="handleUpload"
          :show-file-list="false"
          accept=".pdf,.docx,.md,.txt"
          drag
        >
          <div class="upload-content">
            <span class="upload-icon">📤</span>
            <p>拖拽文件到这里，或点击上传</p>
            <p class="upload-hint">支持 PDF、Word、Markdown、TXT</p>
          </div>
        </el-upload>
      </div>

      <!-- 文档列表 -->
      <div class="document-section">
        <h2>已上传文档</h2>
        <div class="document-list" v-loading="loading">
          <div v-if="documents.length === 0" class="empty">
            <p>还没有文档</p>
          </div>
          <div v-for="doc in documents" :key="doc.id" class="document-item">
            <div class="doc-info">
              <span class="doc-icon">📄</span>
              <div>
                <strong>{{ doc.filename }}</strong>
                <span class="doc-meta">{{ doc.file_type }} · {{ doc.embedding_status }}</span>
              </div>
            </div>
            <el-button type="danger" size="small" @click="handleDelete(doc.id)">删除</el-button>
          </div>
        </div>
      </div>

      <!-- 知识检索 -->
      <div class="search-section">
        <h2>知识检索</h2>
        <div class="search-box">
          <input
            v-model="searchQuery"
            placeholder="输入关键词搜索..."
            @keyup.enter="handleSearch"
          />
          <button @click="handleSearch">搜索</button>
        </div>
        <div v-if="searchResults.length > 0" class="search-results">
          <div v-for="(result, index) in searchResults" :key="index" class="result-item">
            <strong>{{ result.filename }}</strong>
            <p>{{ result.content }}</p>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<style scoped>
.knowledge-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 28px;
  margin-bottom: 10px;
}

.page-header p {
  color: #8e8ea0;
}

.upload-section {
  margin-bottom: 40px;
}

.upload-section :deep(.el-upload-dragger) {
  background: #171717;
  border: 2px dashed #4a4a4a;
  border-radius: 12px;
  padding: 40px;
}

.upload-content {
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 15px;
}

.upload-hint {
  color: #8e8ea0;
  font-size: 12px;
  margin-top: 10px;
}

.document-section, .search-section {
  background: #171717;
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 30px;
}

.document-section h2, .search-section h2 {
  font-size: 18px;
  margin-bottom: 20px;
}

.document-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #2a2a2a;
}

.document-item:last-child {
  border-bottom: none;
}

.doc-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.doc-icon {
  font-size: 24px;
}

.doc-meta {
  display: block;
  color: #8e8ea0;
  font-size: 12px;
  margin-top: 4px;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-box input {
  flex: 1;
  background: #40414f;
  border: none;
  border-radius: 8px;
  padding: 12px 16px;
  color: #fff;
  font-size: 14px;
  outline: none;
}

.search-box button {
  background: #fff;
  color: #000;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  cursor: pointer;
  font-weight: bold;
}

.result-item {
  background: #2a2a2a;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
}

.result-item p {
  color: #ccc;
  margin-top: 8px;
  font-size: 14px;
}

.empty {
  text-align: center;
  color: #8e8ea0;
  padding: 40px;
}
</style>
