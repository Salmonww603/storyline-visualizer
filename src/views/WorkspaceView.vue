<template>
  <div class="workspace">
    <div class="page-head">
      <div>
        <h1>我的工作台</h1>
        <p class="subtitle">管理你的故事线，添加事件，生成时间轴</p>
      </div>
      <button class="logout" @click="handleLogout">退出登录</button>
    </div>

    <div class="layout">
      <!-- 左栏：故事线管理 -->
      <aside class="sidebar">
        <StorylineManager />
      </aside>

      <!-- 右栏：上方时间轴展示，下方事件编辑 -->
      <main class="content">
        <div v-if="store.loading.value" class="state">加载中…</div>
        <template v-else-if="currentStoryline">
          <Timeline :storyline="currentStoryline" />
          <EventEditor :storyline="currentStoryline" />
        </template>
        <div v-else class="state">
          <p>← 先在左边创建或选择一条故事线</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StorylineManager from '../components/StorylineManager.vue'
import Timeline from '../components/Timeline.vue'
import EventEditor from '../components/EventEditor.vue'
import { useStorylines } from '../composables/useStorylines.js'
import { useAuth } from '../stores/auth.js'

const router = useRouter()
const auth = useAuth()
const store = useStorylines()

const currentStoryline = computed(() => store.current())

// 进入工作台时从后端加载数据
onMounted(() => {
  store.load()
})

function handleLogout() {
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.workspace {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
  font-family: system-ui, sans-serif;
  color: #333;
}
.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
}
h1 { font-size: 24px; font-weight: 500; margin-bottom: 6px; }
.subtitle { color: #888; font-size: 14px; margin: 0; }
.logout {
  border: 1px solid #ddd;
  background: white;
  color: #777;
  border-radius: 6px;
  padding: 7px 14px;
  font-size: 13px;
  cursor: pointer;
}
.logout:hover { border-color: #7c5cbf; color: #7c5cbf; }
.layout {
  display: grid;
  grid-template-columns: minmax(280px, 340px) minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}
.sidebar {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  min-width: 0;
}
.content { min-height: 300px; min-width: 0; }
.state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #bbb;
  font-size: 14px;
  background: #fafafa;
  border-radius: 8px;
}
@media (max-width: 800px) {
  .layout { grid-template-columns: 1fr; }
}
</style>
