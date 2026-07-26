<!-- 文档管理页面 - 开发顺序：Step 11 -->
<!-- 功能：查看文档，编辑文档，AI生成文档 -->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getDocuments, getDocument, updateDocument, generateDocument } from '../api/document'
import { ElMessage } from 'element-plus'

const route = useRoute()
const projectId = route.params.id as string

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
  { value: 'project_intro', label: '项目介绍', icon: '介绍' }
]

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

// 查看文档
const viewDocument = async (docType: string) => {
  try {
    const response = await getDocument(projectId, docType)
    currentDoc.value = response.data
    editContent.value = response.data.content || ''
    editing.value = false
  } catch (error) {
    ElMessage.error('文档不存在')
  }
}

// 开始编辑
const startEdit = () => {
  editing.value = true
}

// 保存文档
const saveDocument = async () => {
  try {
    await updateDocument(projectId, currentDoc.value.doc_type, editContent.value)
    ElMessage.success('保存成功')
    editing.value = false
    await viewDocument(currentDoc.value.doc_type)
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// AI生成文档
const handleGenerate = async (docType: string) => {
  generating.value = true
  try {
    await generateDocument(projectId, docType, '根据项目信息自动生成')
    ElMessage.success('生成成功')
    await loadDocuments()
    await viewDocument(docType)
  } catch (error) {
    ElMessage.error('生成失败')
  } finally {
    generating.value = false
  }
}
</script>

<template>
  <div class="documents-page">
    <!-- 文档类型列表 -->
    <div class="doc-types">
      <h3>项目文档</h3>
      <div class="type-list">
        <div
          v-for="doc in docTypes"
          :key="doc.value"
          class="type-item"
          :class="{ active: currentDoc?.doc_type === doc.value }"
          @click="viewDocument(doc.value)"
        >
          <span class="icon">{{ doc.icon }}</span>
          <span>{{ doc.label }}</span>
        </div>
      </div>
    </div>

    <!-- 文档内容 -->
    <div class="doc-content" v-if="currentDoc">
      <div class="doc-header">
        <h3>{{ currentDoc.doc_type.toUpperCase() }}</h3>
        <div class="doc-actions">
          <el-tag v-if="currentDoc.is_auto_generated" type="success">AI生成</el-tag>
          <span class="version">v{{ currentDoc.version }}</span>
          <el-button v-if="!editing" type="primary" size="small" @click="startEdit">编辑</el-button>
          <el-button v-if="editing" type="success" size="small" @click="saveDocument">保存</el-button>
          <el-button
            type="warning"
            size="small"
            :loading="generating"
            @click="handleGenerate(currentDoc.doc_type)"
          >
            AI重新生成
          </el-button>
        </div>
      </div>
      <div class="doc-body">
        <textarea v-if="editing" v-model="editContent" class="edit-area"></textarea>
        <div v-else class="markdown-content">{{ currentDoc.content }}</div>
      </div>
    </div>

    <div v-else class="empty">
      <p>选择左侧文档类型查看内容</p>
    </div>
  </div>
</template>

<style scoped>
.documents-page {
  display: flex;
  height: calc(100vh - 140px);
}

.doc-types {
  width: 200px;
  background: white;
  border-right: 1px solid #eee;
  padding: 20px;
}

.doc-types h3 {
  margin-bottom: 20px;
  color: #333;
}

.type-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.type-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.type-item:hover {
  background: #f5f7fa;
}

.type-item.active {
  background: #667eea;
  color: white;
}

.doc-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.doc-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.version {
  color: #999;
  font-size: 12px;
}

.doc-body {
  background: white;
  border-radius: 10px;
  padding: 20px;
  min-height: 400px;
}

.edit-area {
  width: 100%;
  min-height: 400px;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 15px;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
}

.markdown-content {
  white-space: pre-wrap;
  line-height: 1.6;
}

.empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}
</style>
