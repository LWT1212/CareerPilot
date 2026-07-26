<!-- 登录页面 - ChatGPT风格 -->

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const isLogin = ref(true)
const form = ref({
  username: '',
  email: '',
  password: '',
})

const handleSubmit = async () => {
  try {
    if (isLogin.value) {
      await authStore.login(form.value.email, form.value.password)
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      await authStore.register(form.value.username, form.value.email, form.value.password)
      ElMessage.success('注册成功，请登录')
      isLogin.value = true
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="logo">
        <span class="logo-icon">🤖</span>
        <h1>CareerPilot AI</h1>
        <p>基于Multi-Agent的长期项目成长助手</p>
      </div>

      <form @submit.prevent="handleSubmit">
        <input
          v-if="!isLogin"
          v-model="form.username"
          type="text"
          placeholder="用户名"
        />
        <input
          v-model="form.email"
          type="email"
          placeholder="邮箱地址"
        />
        <input
          v-model="form.password"
          type="password"
          placeholder="密码"
        />
        <button type="submit" class="submit-btn">
          {{ isLogin ? '登录' : '注册' }}
        </button>
      </form>

      <p class="toggle">
        {{ isLogin ? '没有账号？' : '已有账号？' }}
        <a @click="isLogin = !isLogin">
          {{ isLogin ? '立即注册' : '立即登录' }}
        </a>
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #212121;
}

.login-card {
  width: 400px;
  padding: 40px;
}

.logo {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 15px;
}

.logo h1 {
  font-size: 24px;
  margin-bottom: 8px;
}

.logo p {
  color: #8e8ea0;
  font-size: 14px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

input {
  background: #40414f;
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 14px 16px;
  color: #fff;
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s;
}

input:focus {
  border-color: #fff;
}

input::placeholder {
  color: #8e8ea0;
}

.submit-btn {
  background: #fff;
  color: #000;
  border: none;
  border-radius: 8px;
  padding: 14px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: opacity 0.2s;
  margin-top: 10px;
}

.submit-btn:hover {
  opacity: 0.9;
}

.toggle {
  text-align: center;
  color: #8e8ea0;
  margin-top: 25px;
  font-size: 14px;
}

.toggle a {
  color: #fff;
  cursor: pointer;
}

.toggle a:hover {
  text-decoration: underline;
}
</style>
