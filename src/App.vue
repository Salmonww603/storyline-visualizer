<template>
  <div class="app-shell" :class="{ 'no-topbar': isImmersive }">
    <!-- 顶部导航：所有页面共用（沉浸式分享页隐藏） -->
    <header v-if="!isImmersive" class="topbar">
      <div class="topbar-inner">
        <router-link to="/" class="brand">
          <span class="brand-mark">◈</span> 故事线
        </router-link>
        <nav class="nav">
          <router-link to="/">发现</router-link>
          <router-link v-if="auth.isLoggedIn.value" to="/workspace">我的工作台</router-link>
        </nav>
        <div class="account">
          <template v-if="auth.isLoggedIn.value">
            <span class="username">{{ auth.username.value || '我' }}</span>
            <button class="logout-mini" @click="handleLogout">退出</button>
          </template>
          <router-link v-else to="/login" class="login-link">登录 / 注册</router-link>
        </div>
      </div>
    </header>

    <!-- 页面内容：由路由决定显示哪个页面 -->
    <router-view />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from './stores/auth.js'

const router = useRouter()
const route = useRoute()
const auth = useAuth()

// 沉浸式页面（如分享页）隐藏顶部导航，让展示全屏无干扰
const isImmersive = computed(() => !!route.meta.immersive)

function handleLogout() {
  auth.logout()
  // 如果当前在需要登录的页面，退出后回首页
  if (router.currentRoute.value.meta.requiresAuth) {
    router.push('/')
  }
}
</script>

<style>
/* 全局样式（不加 scoped，作用于所有页面） */
* { box-sizing: border-box; }
body {
  margin: 0;
  background: #f7f7f9;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  color: #333;
}
a { color: inherit; }
</style>

<style scoped>
.app-shell { min-height: 100vh; }
.topbar {
  background: white;
  border-bottom: 1px solid #eaeaea;
  position: sticky;
  top: 0;
  z-index: 50;
}
.topbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 58px;
  display: flex;
  align-items: center;
  gap: 28px;
}
.brand {
  font-size: 17px;
  font-weight: 500;
  color: #5b468f;
  text-decoration: none;
  white-space: nowrap;
}
.brand-mark { color: #7c5cbf; margin-right: 2px; }
.nav { display: flex; gap: 20px; flex: 1; }
.nav a {
  font-size: 14px;
  color: #666;
  text-decoration: none;
  padding: 6px 0;
}
.nav a:hover, .nav a.router-link-active { color: #7c5cbf; }
.account { display: flex; align-items: center; gap: 10px; }
.username { font-size: 13px; color: #666; }
.logout-mini {
  border: 1px solid #ddd;
  background: white;
  color: #888;
  border-radius: 6px;
  padding: 5px 10px;
  font-size: 12px;
  cursor: pointer;
}
.logout-mini:hover { border-color: #7c5cbf; color: #7c5cbf; }
.login-link {
  font-size: 13px;
  color: #7c5cbf;
  text-decoration: none;
  border: 1px solid #d9c9f0;
  border-radius: 6px;
  padding: 6px 12px;
}
</style>
