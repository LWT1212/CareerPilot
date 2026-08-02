<!-- 文档管理页面 - ChatGPT风格 -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Layout from '../components/Layout.vue'
import { useProjectStore } from '../stores/project'
import { getDocuments, getDocument, updateDocument, generateDocument } from '../api/document'
import { ElMessage } from 'element-plus'

const projectStore = useProjectStore()
const projectId = ref(projectStore.currentProjectId)

const documents = ref<any[]>([])
const currentDoc = ref<any>(null)
const loading = ref(false)
const editing = ref(false)
const editContent = ref('')
const generating = ref(false)

const docTypes = [
  { value: 'readme', label: 'README', icon: '📄' },
  { value: 'prd', label: 'PRD', icon: '📋' },
  { value: 'star', label: 'STAR', icon: '⭐' },
  { value: 'resume', label: '简历', icon: '📝' },
]

onMounted(async () => {
  await loadDocuments()
})

const loadDocuments = async () => {
  loading.value = true
  try {
    const response = await getDocuments(projectId.value)
    documents.value = response.data
  } catch (error) {
    console.error('加载文档失败', error)
  } finally {
    loading.value = false
  }
}

const viewDocument = async (docType: string) => {
  try {
    const response = await getDocument(projectId.value, docType)
    currentDoc.value = response.data
    editContent.value = response.data.content || ''
    editing.value = false
  } catch (error) {
    currentDoc.value = { doc_type: docType, content: '文档不存在，点击"AI生成"创建', version: 0 }
    editContent.value = ''
  }
}

const startEdit = () => { editing.value = true }

const saveDocument = async () => {
  try {
    await updateDocument(projectId.value, currentDoc.value.doc_type, editContent.value)
    ElMessage.success('保存成功')
    editing.value = false
    await viewDocument(currentDoc.value.doc_type)
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleGenerate = async (docType: string) => {
  generating.value = true
  try {
    await generateDocument(projectId.value, docType)
    ElMessage.success('生成成功')
    await viewDocument(docType)
  } catch (error) {
    ElMessage.error('生成失败')
  } finally {
    generating.value = false
  }
}
</script>

<template>
  <Layout>
    <div class="documents-page">
      <div class="page-header">
        <h1>📄 文档管理</h1>
        <p>AI自动生成项目文档</p>
      </div>

      <div class="doc-grid">
        <!-- 文档类型列表 -->
        <div class="doc-sidebar">
          <div
            v-for="doc in docTypes"
            :key="doc.value"
            class="doc-type-item"
            :class="{ active: currentDoc?.doc_type === doc.value }"
            @click="viewDocument(doc.value)"
          >
            <span class="doc-icon">{{ doc.icon }}</span>
            <span>{{ doc.label }}</span>
          </div>
        </div>

        <!-- 文档内容 -->
        <div class="doc-content" v-if="currentDoc">
          <div class="doc-header">
            <h2>{{ currentDoc.doc_type?.toUpperCase() }}</h2>
            <div class="doc-actions">
              <span class="version" v-if="currentDoc.version">v{{ currentDoc.version }}</span>
              <button v-if="!editing" class="edit-btn" @click="startEdit">编辑</button>
              <button v-if="editing" class="save-btn" @click="saveDocument">保存</button>
              <button class="generate-btn" :disabled="generating" @click="handleGenerate(currentDoc.doc_type)">
                {{ generating ? '生成中...' : 'AI生成' }}
              </button>
            </div>
          </div>
          <div class="doc-body">
            <textarea v-if="editing" v-model="editContent" class="edit-area"></textarea>
            <div v-else class="doc-text">{{ currentDoc.content }}</div>
          </div>
        </div>

        <div v-else class="doc-empty">
          <p>选择左侧文档类型查看</p>
        </div>
      </div>
    </div>
  </Layout>
</template>

<style scoped>
.documents-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 { font-size: 28px; margin-bottom: 10px; }
.page-header p { color: #8e8ea0; }

.doc-grid {
  display: flex;
  gap: 20px;
  min-height: 500px;
}

.doc-sidebar {
  width: 180px;
  background: #171717;
  border-radius: 12px;
  padding: 15px;
}

.doc-type-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 5px;
  transition: background 0.2s;
}

.doc-type-item:hover { background: #2a2a2a; }
.doc-type-item.active { background: #343541; }

.doc-content {
  flex: 1;
  background: #171717;
  border-radius: 12px;
  padding: 25px;
}

.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #2a2a2a;
}

.doc-header h2 { margin: 0; }

.doc-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.version {
  color: #8e8ea0;
  font-size: 12px;
}

.edit-btn, .save-btn, .generate-btn {
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 13px;
}

.edit-btn { background: #40414f; color: #fff; }
.save-btn { background: #10b981; color: #fff; }
.generate-btn { background: #fff; color: #000; font-weight: bold; }
.generate-btn:disabled { opacity: 0.5; }

.doc-body { min-height: 400px; }

.edit-area {
  width: 100%;
  min-height: 400px;
  background: #40414f;
  border: none;
  border-radius: 8px;
  padding: 15px;
  color: #fff;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
  outline: none;
}

.doc-text {
  white-space: pre-wrap;
  line-height: 1.7;
  color: #ccc;
}

.doc-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #171717;
  border-radius: 12px;
  color: #8e8ea0;
}
</style>
