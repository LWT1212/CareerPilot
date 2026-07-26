<!-- 聊天页面 - 开发顺序：Step 7 -->
<!-- 功能：实时聊天，发送消息，查看历史消息 -->

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getMessages, sendMessage, createChat } from '../api/chat'

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
    const response = await getMessages(projectId) // 这里应该是getChats
    chats.value = response.data
    if (chats.value.length > 0) {
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
    messages.value = response.data.items || []
    scrollToBottom()
  } catch (error) {
    console.error('加载消息失败', error)
  }
}

// 发送消息
const handleSend = async () => {
  if (!inputMessage.value.trim() || !currentChat.value) return

  const content = inputMessage.value
  inputMessage.value = ''
  loading.value = true

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
  <div class="chat-page">
    <!-- 左侧聊天列表 -->
    <aside class="chat-sidebar">
      <div class="sidebar-header">
        <h3>聊天列表</h3>
        <el-button type="primary" size="small" @click="handleNewChat">新建</el-button>
      </div>
      <div class="chat-list">
        <div
          v-for="chat in chats"
          :key="chat.id"
          class="chat-item"
          :class="{ active: currentChat?.id === chat.id }"
          @click="selectChat(chat)"
        >
          {{ chat.title || '新聊天' }}
        </div>
      </div>
    </aside>

    <!-- 右侧消息区 -->
    <main class="chat-main">
      <div class="messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty">
          <p>开始对话吧！</p>
        </div>
        <div v-for="msg in messages" :key="msg.id" class="message" :class="msg.role">
          <div class="message-content">
            {{ msg.content }}
          </div>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="input-area">
        <el-input
          v-model="inputMessage"
          placeholder="输入消息..."
          @keyup.enter="handleSend"
          :disabled="loading"
        />
        <el-button type="primary" @click="handleSend" :loading="loading">发送</el-button>
      </div>
    </main>
  </div>
</template>

<style scoped>
.chat-page {
  display: flex;
  height: calc(100vh - 140px);
}

.chat-sidebar {
  width: 250px;
  background: white;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.chat-item {
  padding: 12px 15px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 5px;
  transition: background 0.2s;
}

.chat-item:hover {
  background: #f5f7fa;
}

.chat-item.active {
  background: #667eea;
  color: white;
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

.message {
  margin-bottom: 15px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
}

.message.user .message-content {
  background: #667eea;
  color: white;
}

.message.assistant .message-content {
  background: #f0f0f0;
  color: #333;
}

.input-area {
  padding: 15px;
  background: white;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
}

.empty {
  text-align: center;
  color: #999;
  padding: 60px;
}
</style>
