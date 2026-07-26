<!-- ChatGPT风格聊天页面 -->

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import Layout from '../components/Layout.vue'
import { getMessages, sendMessage, createChat, getChats } from '../api/chat'

const route = useRoute()
const projectId = route.params.id as string

const chats = ref<any[]>([])
const currentChat = ref<any>(null)
const messages = ref<any[]>([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)

onMounted(async () => {
  await loadChats()
})

// 加载聊天列表
const loadChats = async () => {
  try {
    const response = await getChats(projectId)
    chats.value = response.data.items || response.data
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

  // 如果没有当前聊天，先创建
  if (!currentChat.value) {
    try {
      const response = await createChat(projectId, { title: '新聊天' })
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

  // 先显示用户消息
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

// 创建新聊天
const handleNewChat = async () => {
  try {
    const response = await createChat(projectId, { title: '新聊天' })
    await loadChats()
    await selectChat(response.data)
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
    <div class="chat-container">
      <!-- 聊天历史侧栏 -->
      <div class="chat-sidebar">
        <button class="new-chat-btn" @click="handleNewChat">
          <span>+</span> 新聊天
        </button>
        <div class="chat-history">
          <div
            v-for="chat in chats"
            :key="chat.id"
            class="chat-history-item"
            :class="{ active: currentChat?.id === chat.id }"
            @click="selectChat(chat)"
          >
            {{ chat.title || '新聊天' }}
          </div>
        </div>
      </div>

      <!-- 聊天主区域 -->
      <div class="chat-main">
        <!-- 消息列表 -->
        <div class="messages" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-state">
            <h2>CareerPilot AI</h2>
            <p>基于Multi-Agent的长期项目成长助手</p>
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
              placeholder="输入消息..."
              @keydown.enter.exact="handleSend"
              :disabled="loading"
              rows="1"
            ></textarea>
            <button class="send-btn" @click="handleSend" :disabled="loading || !inputMessage.trim()">
              ↑
            </button>
          </div>
          <p class="input-hint">按 Enter 发送</p>
        </div>
      </div>
    </div>
  </Layout>
</template>

<style scoped>
.chat-container {
  display: flex;
  height: 100%;
}

.chat-sidebar {
  width: 260px;
  background: #171717;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #2a2a2a;
}

.new-chat-btn {
  margin: 10px;
  padding: 12px;
  background: transparent;
  border: 1px solid #4a4a4a;
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
}

.new-chat-btn:hover {
  background: #2a2a2a;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px;
}

.chat-history-item {
  padding: 12px 15px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 5px;
  font-size: 14px;
  color: #ccc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: background 0.2s;
}

.chat-history-item:hover {
  background: #2a2a2a;
}

.chat-history-item.active {
  background: #343541;
  color: #fff;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
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
  font-size: 28px;
  margin-bottom: 10px;
  color: #fff;
}

.message {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.message-avatar {
  font-size: 24px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message.user {
  flex-direction: row-reverse;
}

.message.user .message-content {
  background: #343541;
}

.message-content {
  padding: 12px 18px;
  border-radius: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.message.user .message-content {
  background: #343541;
}

.message.assistant .message-content {
  background: transparent;
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
  background: #212121;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: #40414f;
  border-radius: 12px;
  padding: 10px 15px;
  max-width: 800px;
  margin: 0 auto;
}

.input-wrapper textarea {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 16px;
  resize: none;
  outline: none;
  font-family: inherit;
  max-height: 150px;
}

.input-wrapper textarea::placeholder {
  color: #8e8ea0;
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #fff;
  border: none;
  cursor: pointer;
  font-size: 18px;
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

.input-hint {
  text-align: center;
  color: #8e8ea0;
  font-size: 12px;
  margin-top: 10px;
}
</style>
