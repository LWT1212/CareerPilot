<!-- 聊天页面 - 使用全局项目状态 -->
<!-- 支持：普通聊天 / RAG知识检索 / 多Agent协作 -->

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import Layout from '../components/Layout.vue'
import { useProjectStore } from '../stores/project'
import { getMessages, sendMessage, createChat, getChats } from '../api/chat'

const projectStore = useProjectStore()

const chats = ref<any[]>([])
const currentChat = ref<any>(null)
const messages = ref<any[]>([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

const projectId = ref(projectStore.currentProjectId)

// 监听项目切换（点击侧边栏项目时触发）
watch(
  () => projectStore.currentProjectId,
  (newId) => {
    projectId.value = newId
    currentChat.value = null
    messages.value = []
    chats.value = []
    loadChats()
  }
)

// 监听"+ New Chat"请求（点击侧边栏New Chat时触发）
watch(
  () => projectStore.newChatRequested,
  () => {
    handleNewChat()
  }
)

onMounted(async () => {
  await loadChats()
})

// 加载聊天列表
const loadChats = async () => {
  try {
    if (!projectId.value) {
      chats.value = []
      return
    }
    const response = await getChats(projectId.value)
    chats.value = response.data.items || response.data || []
    if (chats.value.length > 0 && !currentChat.value) {
      await selectChat(chats.value[0])
    }
  } catch (error) {
    console.error('加载聊天列表失败', error)
  }
}

// 选择聊天
const selectChat = async (chat: any) => {
  currentChat.value = chat
  await loadMessages(chat.id)
}

// 加载消息
const loadMessages = async (chatId: string) => {
  try {
    const response = await getMessages(chatId)
    messages.value = response.data.items || response.data || []
    scrollToBottom()
  } catch (error) {
    console.error('加载消息失败', error)
  }
}

// 发送消息
const handleSend = async () => {
  if (!inputMessage.value.trim()) return

  if (!projectId.value) {
    alert('请先在左侧选择一个项目')
    return
  }

  if (!currentChat.value) {
    try {
      const response = await createChat(projectId.value, { title: '新聊天' })
      currentChat.value = response.data
      await loadChats()
    } catch (error) {
      console.error('创建聊天失败', error)
      return
    }
  }

  const content = inputMessage.value
  inputMessage.value = ''
  loading.value = true

  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: content
  })
  scrollToBottom()

  try {
    await sendMessage(currentChat.value.id, content)
    await loadMessages(currentChat.value.id)
  } catch (error) {
    console.error('发送消息失败', error)
  } finally {
    loading.value = false
  }
}

// 新建聊天
const handleNewChat = async () => {
  if (!projectId.value) {
    alert('请先在左侧选择一个项目')
    return
  }
  try {
    const response = await createChat(projectId.value, { title: '新聊天' })
    currentChat.value = response.data
    messages.value = []
    await loadChats()
  } catch (error) {
    console.error('创建聊天失败', error)
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}
</script>

<template>
  <Layout>
    <!-- 中间聊天窗口 -->
    <template #default>
      <div class="chat-container">
        <!-- 消息列表 -->
        <div class="messages" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-state">
            <h2>CareerPilot AI</h2>
            <p>有什么我可以帮助你的？</p>
            <p class="hint">支持：普通聊天 / RAG知识检索 / 多Agent协作</p>
          </div>

          <div v-for="msg in messages" :key="msg.id" class="message" :class="msg.role">
            <div class="message-avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
            <div class="message-content">{{ msg.content }}</div>
          </div>

          <div v-if="loading" class="message assistant">
            <div class="message-avatar">🤖</div>
            <div class="message-content loading">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <div class="input-wrapper">
            <textarea
              v-model="inputMessage"
              placeholder="发送消息..."
              @keydown.enter.exact="handleSend"
              :disabled="loading"
              rows="1"
            ></textarea>
            <button class="send-btn" @click="handleSend" :disabled="loading || !inputMessage.trim()">➤</button>
          </div>
        </div>
      </div>
    </template>

    <!-- 右侧：Project Context -->
    <template #context>
      <div class="context-content">
        <div class="context-section">
          <h4>当前项目</h4>
          <p>{{ projectStore.currentProject?.name || '未选择' }}</p>
        </div>
        <div class="context-section">
          <h4>最近更新</h4>
          <p class="text-muted">暂无更新</p>
        </div>
        <div class="context-section">
          <h4>AI建议</h4>
          <p class="text-muted">暂无建议</p>
        </div>
        <div class="context-section">
          <h4>Agent执行</h4>
          <div class="agent-status"><span class="status-dot active"></span> Coordinator</div>
          <div class="agent-status"><span class="status-dot active"></span> Knowledge</div>
          <div class="agent-status"><span class="status-dot"></span> Experience</div>
          <div class="agent-status"><span class="status-dot"></span> Interview</div>
          <div class="agent-status"><span class="status-dot"></span> Document</div>
        </div>
        <div class="context-section">
          <h4>知识库</h4>
          <p class="text-muted">上传文档后显示</p>
        </div>
        <div class="context-section">
          <h4>最近面试</h4>
          <p class="text-muted">暂无记录</p>
        </div>
        <div class="context-section">
          <h4>项目统计</h4>
          <p class="text-muted">聊天 0 · 经验 0 · 面试 0</p>
        </div>
      </div>
    </template>
  </Layout>
</template>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  text-align: center;
}

.empty-state h2 {
  font-size: 24px;
  margin-bottom: 10px;
  color: #333;
}

.hint {
  font-size: 12px;
  margin-top: 10px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.message.user {
  flex-direction: row-reverse;
}

.message-content {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.message.user .message-content {
  background: #000;
  color: #fff;
}

.message.assistant .message-content {
  background: #f0f0f0;
  color: #333;
}

.loading .dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  margin: 0 3px;
  animation: bounce 1.4s infinite ease-in-out;
}

.loading .dot:nth-child(1) { animation-delay: -0.32s; }
.loading .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.input-area {
  padding: 20px;
  background: #fff;
  border-top: 1px solid #e5e5e5;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 12px 16px;
  max-width: 800px;
  margin: 0 auto;
}

.input-wrapper textarea {
  flex: 1;
  background: transparent;
  border: none;
  color: #333;
  font-size: 15px;
  resize: none;
  outline: none;
  font-family: inherit;
  max-height: 150px;
}

.input-wrapper textarea::placeholder {
  color: #999;
}

.send-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #000;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.send-btn:not(:disabled):hover {
  opacity: 0.8;
}

/* Context Panel */
.context-content {
  padding: 0;
}

.context-section {
  margin-bottom: 20px;
}

.context-section h4 {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.context-section p {
  font-size: 14px;
  color: #333;
  margin: 0;
}

.text-muted {
  color: #999 !important;
  font-size: 13px !important;
}

.agent-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #333;
  margin-bottom: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
}

.status-dot.active {
  background: #10b981;
}
</style>
