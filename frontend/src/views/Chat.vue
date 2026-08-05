<!-- 聊天页面 - 直接使用Store状态，保证数据隔离和响应式 -->

<script setup lang="ts">
import { onMounted, watch, nextTick, ref } from 'vue'
import Layout from '../components/Layout.vue'
import { useProjectStore } from '../stores/project'
import { streamMessage } from '../api/chat'
import {
  getLearningPlans,
  getNotifications,
  markNotificationRead,
  getAgentExecutions,
  getProjectMemories,
} from '../api/proactive'

const projectStore = useProjectStore()

const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

// === 右侧面板数据（T13-T16成果展示）===
const learningPlans = ref<any[]>([])
const notifications = ref<any[]>([])
const agentExecutions = ref<any[]>([])
const projectMemories = ref<any[]>([])

// 加载右侧面板数据
const loadContextData = async () => {
  const pid = projectStore.currentProjectId
  if (!pid) return

  try {
    const [plans, notifs, memories] = await Promise.all([
      getLearningPlans(pid),
      getNotifications(pid),
      getProjectMemories(pid),
    ])
    learningPlans.value = plans.data || []
    notifications.value = notifs.data || []
    projectMemories.value = memories.data?.memories || []
  } catch (error) {
    console.error('加载面板数据失败', error)
  }
}

// 标记提醒已读
const handleMarkRead = async (notifId: string) => {
  try {
    await markNotificationRead(projectStore.currentProjectId, notifId)
    await loadContextData()
  } catch (error) {
    console.error('标记已读失败', error)
  }
}

// Agent执行记录标签
const agentTypeLabel = (type: string) => {
  if (type.includes('tool:')) {
    const [agent, tool] = type.split('(tool:')
    return `${agent} ⚙️${tool?.replace(')', '') || ''}`
  }
  return type
}

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
  // 加载右侧面板数据（学习计划/提醒/记忆）
  await loadContextData()
  // 加载Agent执行记录
  try {
    const execs = await getAgentExecutions(10)
    agentExecutions.value = execs.data || []
  } catch (error) {
    console.error('加载执行记录失败', error)
  }
})

// 监听当前项目变化 → 清空消息 + 加载面板数据
watch(
  () => projectStore.currentProjectId,
  () => {
    scrollToBottom()
    loadContextData()
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

// 发送消息（使用SSE流式）
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

  // 添加一个空的AI消息，流式填充
  const aiMsgId = Date.now() + 1
  projectStore.messages.push({
    id: aiMsgId,
    role: 'assistant',
    content: ''
  })
  scrollToBottom()

  try {
    // 流式接收AI回复
    let fullContent = ''
    await streamMessage(projectStore.currentChat.id, content, (chunk) => {
      fullContent += chunk
      // 更新AI消息内容（实时显示）
      const msg = projectStore.messages.find(m => m.id === aiMsgId)
      if (msg) msg.content = fullContent
      scrollToBottom()
    })
  } catch (error) {
    console.error('发送消息失败', error)
    const msg = projectStore.messages.find(m => m.id === aiMsgId)
    if (msg) msg.content = '（消息发送失败，请重试）'
  } finally {
    loading.value = false
    // 刷新消息列表（从数据库拉取最新）
    await projectStore.loadMessages(projectStore.currentChat.id)
    scrollToBottom()
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

        <!-- 🔔 AI提醒（T16主动成长） -->
        <div class="context-section" v-if="notifications.length > 0">
          <h4>🔔 AI提醒</h4>
          <div v-for="n in notifications" :key="n.id" class="notif-item" :class="{ unread: !n.is_read }">
            <div class="notif-title">{{ n.title }}</div>
            <div class="notif-content">{{ n.content }}</div>
            <button v-if="!n.is_read" class="notif-read-btn" @click="handleMarkRead(n.id)">标记已读</button>
          </div>
        </div>

        <!-- 📚 学习计划（T16薄弱点） -->
        <div class="context-section" v-if="learningPlans.length > 0">
          <h4>📚 学习计划</h4>
          <div v-for="plan in learningPlans" :key="plan.id" class="plan-item">
            <div class="plan-title">{{ plan.title }}</div>
            <div class="plan-meta">薄弱{{ plan.weak_count }}次</div>
            <div class="plan-content">{{ plan.content }}</div>
          </div>
        </div>

        <!-- 🧠 项目记忆（T15长期记忆） -->
        <div class="context-section" v-if="projectMemories.length > 0">
          <h4>🧠 项目记忆</h4>
          <div v-for="m in projectMemories" :key="m.id" class="memory-item">
            <span class="memory-type">{{ m.memory_type }}</span>
            {{ m.content }}
          </div>
        </div>

        <!-- ⚙️ Agent执行（T13执行记录） -->
        <div class="context-section">
          <h4>⚙️ Agent执行</h4>
          <div v-if="agentExecutions.length === 0" class="text-muted">暂无执行记录</div>
          <div v-for="exec in agentExecutions" :key="exec.id" class="exec-item">
            <span class="exec-agent">{{ agentTypeLabel(exec.agent_type) }}</span>
            <span class="exec-status" :class="exec.status">{{ exec.status }}</span>
            <span class="exec-time">{{ exec.duration_ms }}ms</span>
          </div>
        </div>

        <div class="context-section">
          <h4>项目统计</h4>
          <p class="text-muted">聊天 {{ projectStore.chats.length }} · 学习计划 {{ learningPlans.length }}</p>
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

/* === 右侧面板：提醒/学习计划/记忆/执行记录 === */
.notif-item {
  padding: 10px;
  border-radius: 8px;
  background: #fff8e6;
  margin-bottom: 8px;
  border: 1px solid #f0e0b0;
}

.notif-item.unread {
  background: #fff3cc;
  border-color: #e8c860;
}

.notif-title {
  font-weight: 600;
  font-size: 13px;
  color: #8a6d00;
  margin-bottom: 4px;
}

.notif-content {
  font-size: 12px;
  color: #666;
}

.notif-read-btn {
  margin-top: 6px;
  font-size: 11px;
  background: none;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 2px 8px;
  cursor: pointer;
  color: #888;
}

.plan-item {
  padding: 10px;
  border-radius: 8px;
  background: #f0f7ff;
  margin-bottom: 8px;
  border: 1px solid #c8dff0;
}

.plan-title {
  font-weight: 600;
  font-size: 13px;
  color: #1a5a8a;
}

.plan-meta {
  font-size: 11px;
  color: #e67e22;
  margin: 2px 0;
}

.plan-content {
  font-size: 12px;
  color: #555;
  white-space: pre-wrap;
  max-height: 100px;
  overflow-y: auto;
}

.memory-item {
  font-size: 12px;
  color: #555;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
}

.memory-type {
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 3px;
  padding: 1px 6px;
  font-size: 11px;
  margin-right: 6px;
}

.exec-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #555;
  padding: 5px 0;
}

.exec-agent {
  font-weight: 500;
  color: #333;
}

.exec-status {
  font-size: 11px;
  border-radius: 3px;
  padding: 1px 6px;
}

.exec-status.success {
  background: #e8f5e9;
  color: #2e7d32;
}

.exec-status.failed {
  background: #fdecea;
  color: #c62828;
}

.exec-time {
  color: #aaa;
  font-size: 11px;
  margin-left: auto;
}
