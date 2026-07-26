<!-- ChatGPT风格聊天页面 -->

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import Layout from '../components/Layout.vue'
import { getMessages, sendMessage, createChat, getChats } from '../api/chat'

const chats = ref<any[]>([])
const currentChat = ref<any>(null)
const messages = ref<any[]>([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

onMounted(async () => {
  await loadChats()
})

const loadChats = async () => {
  try {
    const response = await getChats('current')
    chats.value = response.data.items || response.data || []
    if (chats.value.length > 0 && !currentChat.value) {
      await selectChat(chats.value[0])
    }
  } catch (error) {
    console.error('加载聊天列表失败', error)
  }
}

const selectChat = async (chat: any) => {
  currentChat.value = chat
  await loadMessages(chat.id)
}

const loadMessages = async (chatId: string) => {
  try {
    const response = await getMessages(chatId)
    messages.value = response.data.items || response.data || []
    scrollToBottom()
  } catch (error) {
    console.error('加载消息失败', error)
  }
}

const handleSend = async () => {
  if (!inputMessage.value.trim()) return

  if (!currentChat.value) {
    try {
      const response = await createChat('current', { title: '新聊天' })
      currentChat.value = response.data
      await loadChats()
    } catch (error) {
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

const handleNewChat = async () => {
  try {
    const response = await createChat('current', { title: '新聊天' })
    await loadChats()
    await selectChat(response.data)
  } catch (error) {
    console.error('创建聊天失败', error)
  }
}

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
    <template #default>
      <div class="chat-container">
        <!-- 消息列表 -->
        <div class="messages" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-state">
            <h2>CareerPilot AI</h2>
            <p>有什么我可以帮助你的？</p>
          </div>

          <div v-for="msg in messages" :key="msg.id" class="message" :class="msg.role">
            <div class="message-avatar">
              {{ msg.role === 'user' ? '👤' : '🤖' }}
            </div>
            <div class="message-content">
              {{ msg.content }}
            </div>
          </div>

          <div v-if="loading" class="message assistant">
            <div class="message-avatar">🤖</div>
            <div class="message-content loading">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
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
            <button class="send-btn" @click="handleSend" :disabled="loading || !inputMessage.trim()">
              ➤
            </button>
          </div>
        </div>
      </div>
    </template>

    <template #context>
      <div class="context-content">
        <div class="context-section">
          <h4>当前项目</h4>
          <p>CareerPilot AI</p>
        </div>
        <div class="context-section">
          <h4>最近更新</h4>
          <p class="text-muted">暂无更新</p>
        </div>
        <div class="context-section">
          <h4>Agent状态</h4>
          <div class="agent-status">
            <span class="status-dot active"></span>
            <span>Coordinator</span>
          </div>
          <div class="agent-status">
            <span class="status-dot active"></span>
            <span>Knowledge</span>
          </div>
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
}

.empty-state h2 {
  font-size: 24px;
  margin-bottom: 10px;
  color: #333;
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
  transition: opacity 0.2s;
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
  padding: 20px;
}

.context-section {
  margin-bottom: 24px;
}

.context-section h4 {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
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
