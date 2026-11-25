<template>
  <div class="login-page">
    <div class="card">
      <h1>故事线可视化平台</h1>
      <p class="subtitle">{{ isRegister ? '创建账号，开始记录你的故事' : '欢迎回来' }}</p>

      <!-- 登录/注册切换 -->
      <div class="tabs">
        <button :class="{ active: !isRegister }" @click="switchMode(false)">登录</button>
        <button :class="{ active: isRegister }" @click="switchMode(true)">注册</button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="field">
          <label>用户名</label>
          <input v-model="form.username" type="text" placeholder="你的用户名" autocomplete="username" required />
        </div>
        <div class="field" v-if="isRegister">
          <label>邮箱</label>
          <input v-model="form.email" type="email" placeholder="name@example.com" autocomplete="email" required />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="至少 6 位" autocomplete="current-password" required />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" class="submit" :disabled="loading">
          {{ loading ? '请稍候…' : (isRegister ? '注册并登录' : '登录') }}
        </button>
      </form>

      <p class="tip">测试账号：<code>testuser_wr</code> / <code>Test123456</code></p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../stores/auth.js'

const route = useRoute()
const router = useRouter()
const auth = useAuth()

const isRegister = ref(false)
const form = reactive({ username: '', email: '', password: '' })
const error = ref('')

function switchMode(register) {
  isRegister.value = register
  error.value = ''
}

async function handleSubmit() {
  error.value = ''
  // 前端先做简单校验，减轻后端压力、提示更快
  if (form.password.length < 6) {
    error.value = '密码至少 6 位'
    return
  }
  try {
    const ok = isRegister.value
      ? await auth.register(form.username, form.email, form.password)
      : await auth.login(form.username, form.password)

    if (ok) {
      // 登录成功后跳回原本想去的页面；没有就回工作台
      const redirect = route.query.redirect || '/workspace'
      router.push(redirect)
    }
  } catch (e) {
    error.value = e.message
  }
}
</script>

<style scoped>
.login-page {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}
.card {
  width: 100%;
  max-width: 400px;
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 14px;
  padding: 32px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
}
h1 { font-size: 21px; font-weight: 500; margin: 0 0 6px; text-align: center; }
.subtitle { font-size: 13px; color: #999; text-align: center; margin: 0 0 24px; }
.tabs {
  display: flex;
  background: #f5f5f5;
  border-radius: 8px;
  padding: 3px;
  margin-bottom: 22px;
}
.tabs button {
  flex: 1;
  border: none;
  background: transparent;
  padding: 9px;
  font-size: 14px;
  color: #777;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.tabs button.active {
  background: white;
  color: #7c5cbf;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 13px; color: #555; margin-bottom: 6px; }
.field input {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  border: 1px solid #d8d8d8;
  border-radius: 7px;
  font-size: 14px;
  font-family: inherit;
}
.field input:focus { outline: none; border-color: #7c5cbf; }
.error { color: #f56c6c; font-size: 13px; margin: 0 0 12px; }
.submit {
  width: 100%;
  padding: 11px;
  border: none;
  background: #7c5cbf;
  color: white;
  border-radius: 7px;
  font-size: 15px;
  cursor: pointer;
  margin-top: 4px;
}
.submit:hover { background: #6b4faa; }
.submit:disabled { opacity: 0.6; cursor: wait; }
.tip { font-size: 12px; color: #aaa; text-align: center; margin: 18px 0 0; }
code { background: #f5f5f5; padding: 1px 5px; border-radius: 4px; color: #666; }
</style>
