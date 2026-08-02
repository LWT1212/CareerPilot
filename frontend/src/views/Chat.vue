<!-- 聊天页面 - 直接使用Store状态，保证数据隔离和响应式 -->

<script setup lang="ts">
import { onMounted, watch, nextTick, ref } from 'vue'
import Layout from '../components/Layout.vue'
import { useProjectStore } from '../stores/project'

const projectStore = useProjectStore()

const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

// 页面挂载时恢复当前状态（支持全局模式和项目模式）
onMounted(async () => {
  if (projectStore.currentProjectId) {
    // 项目模式：加载项目聊天
    if (projectStore.chats.length === 0) {
      await projectStore.loadChats()
    }
    if (!projectStore.currentChat && projectStore.chats.length > 0) {
      await projectStore.selectChat(projectStore.chats[0])
    }
  } else {
    // 全局模式：加载全局聊天
    if (projectStore.globalChats.length === 0) {
      await projectStore.loadGlobalChats()
    }
    if (!projectStore.currentChat && projectStore.globalChats.length > 0) {
      await projectStore.selectChat(projectStore.globalChats[0])
    }
  }
  scrollToBottom()
})

// 监听当前项目变化 → 清空消息
watch(
  () => projectStore.currentProjectId,
  () => {
    scrollToBottom()
  }
)

// 监听当前聊天变化 → 滚动到底部
watch(
  () => projectStore.currentChat?.id,
  () => {
    scrollToBottom()
  }
)

// 监听消息数量变化 → 滚动到底部
watch(
  () => projectStore.messages.length,
  () => {
    scrollToBottom()
  }
)

// 监听"+ New Chat"请求
watch(
  () => projectStore.newChatRequested,
  async () => {
    await handleNewChat()
  }
)

// 发送消息
const handleSend = async () => {
  if (!inputMessage.value.trim()) return

  // 如果没有当前聊天，先创建（自动判断全局/项目模式）
  if (!projectStore.currentChat) {
    const chat = await projectStore.createNewChat()
    if (!chat) return
  }

  const content = inputMessage.value
  inputMessage.value = ''
  loading.value = true

  // 先显示用户消息
  projectStore.messages.push({
    id: Date.now(),
    role: 'user',
    content: content
  })
  scrollToBottom()

  try {
    await projectStore.sendMessageToChat(projectStore.currentChat.id, content)
    await projectStore.loadMessages(projectStore.currentChat.id)
    scrollToBottom()
  } catch (error) {
    console.error('发送消息失败', error)
  } finally {
    loading.value = false
  }
}

// 新建聊天（全局或项目模式）
const handleNewChat = async () => {
  await projectStore.createNewChat()
  scrollToBottom()
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
        <!-- 消息列表：直接使用store状态 -->
        <div class="messages" ref="messagesContainer">
          <div v-if="projectStore.messages.length === 0" class="empty-state">
            <h2>CareerPilot AI</h2>
            <p>有什么我可以帮助你的？</p>
            <p class="hint">支持：普通聊天 / RAG知识检索 / 多Agent协作</p>
          </div>

          <div v-for="msg in projectStore.messages" :key="msg.id" class="message" :class="msg.role">
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
          <h4>当前聊天</h4>
          <p>{{ projectStore.currentChat?.title || '未选择' }}</p>
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
          <p class="text-muted">聊天 {{ projectStore.chats.length }} · 经验 0 · 面试 0</p>
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
