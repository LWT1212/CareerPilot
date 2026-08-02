<!-- 设置页面 -->

<script setup lang="ts">
import { ref } from 'vue'
import Layout from '../components/Layout.vue'

const settings = ref({
  llm_provider: 'openai',
  llm_model: 'gpt-4',
  theme: 'light',
  language: 'zh',
})

const providers = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'ollama', label: 'Ollama (本地)' },
]

const models = ['gpt-4', 'gpt-3.5-turbo', 'qwen', 'llama3']

const saveSettings = () => {
  localStorage.setItem('llm_settings', JSON.stringify(settings.value))
  alert('设置已保存')
}
</script>

<template>
  <Layout>
    <div class="settings-page">
      <div class="page-header">
        <h1>⚙️ 设置</h1>
        <p>个性化配置你的CareerPilot AI</p>
      </div>

      <div class="settings-section">
        <h2>LLM 配置</h2>
        <div class="setting-item">
          <label>LLM 提供商</label>
          <select v-model="settings.llm_provider">
            <option v-for="p in providers" :key="p.value" :value="p.value">
              {{ p.label }}
            </option>
          </select>
        </div>
        <div class="setting-item">
          <label>模型</label>
          <select v-model="settings.llm_model">
            <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
      </div>

      <div class="settings-section">
        <h2>界面设置</h2>
        <div class="setting-item">
          <label>主题</label>
          <select v-model="settings.theme">
            <option value="light">浅色</option>
            <option value="dark">深色</option>
          </select>
        </div>
        <div class="setting-item">
          <label>语言</label>
          <select v-model="settings.language">
            <option value="zh">中文</option>
            <option value="en">English</option>
          </select>
        </div>
      </div>

      <div class="settings-actions">
        <button class="save-btn" @click="saveSettings">保存设置</button>
      </div>
    </div>
  </Layout>
</template>

<style scoped>
.settings-page {
  max-width: 700px;
  margin: 0 auto;
  padding: 40px 20px;
}

.page-header {
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 24px;
  margin-bottom: 8px;
  color: #333;
}

.page-header p {
  color: #999;
}

.settings-section {
  background: #fff;
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 20px;
  border: 1px solid #e5e5e5;
}

.settings-section h2 {
  font-size: 16px;
  margin-bottom: 20px;
  color: #333;
}

.setting-item {
  margin-bottom: 20px;
}

.setting-item label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.setting-item select,
.setting-item input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}

.setting-item select:focus,
.setting-item input:focus {
  border-color: #000;
}

.settings-actions {
  display: flex;
  justify-content: flex-end;
}

.save-btn {
  padding: 12px 32px;
  background: #000;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
}

.save-btn:hover {
  opacity: 0.8;
}
</style>
