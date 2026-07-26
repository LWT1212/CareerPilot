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
  <div class="login-container">
    <div class="login-card">
      <h1>CareerPilot AI</h1>
      <p>基于Multi-Agent的长期项目成长助手</p>

      <el-form :model="form" @submit.prevent="handleSubmit">
        <el-form-item v-if="!isLogin">
          <el-input v-model="form.username" placeholder="用户名" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.email" placeholder="邮箱" type="email" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" placeholder="密码" type="password" />
        </el-form-item>
        <el-button type="primary" native-type="submit" style="width: 100%">
          {{ isLogin ? '登录' : '注册' }}
        </el-button>
      </el-form>

      <p class="toggle" @click="isLogin = !isLogin">
        {{ isLogin ? '没有账号？立即注册' : '已有账号？立即登录' }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 400px;
}

h1 {
  text-align: center;
  margin-bottom: 10px;
  color: #333;
}

p {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.toggle {
  cursor: pointer;
  color: #667eea;
  margin-top: 20px;
}

.toggle:hover {
  text-decoration: underline;
}
</style>
