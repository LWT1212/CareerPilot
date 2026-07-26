// 认证状态管理

import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

interface User {
  id: string
  username: string
  email: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  // 登录
  async function login(email: string, password: string) {
    const response = await api.post('/auth/login', { email, password })
    token.value = response.data.access_token
    user.value = response.data.user
    localStorage.setItem('token', token.value)
    return response.data
  }

  // 注册
  async function register(username: string, email: string, password: string) {
    const response = await api.post('/auth/register', { username, email, password })
    return response.data
  }

  // 登出
  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, token, login, register, logout }
})
