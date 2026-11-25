<template>
  <div class="app">
    <header>
      <h1>故事线可视化平台</h1>
      <p class="subtitle">把散落的故事线索，变成一眼看清的时间轴</p>
    </header>

    <div class="layout">
      <!-- 左栏：故事线管理 -->
      <aside class="sidebar">
        <StorylineManager />
      </aside>

      <!-- 右栏：选中故事线的事件编辑 -->
      <main class="content">
        <template v-if="currentStoryline">
          <EventEditor :storyline="currentStoryline" />
        </template>
        <template v-else>
          <div class="placeholder">
            <p>← 先在左边创建或选择一条故事线</p>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import StorylineManager from './components/StorylineManager.vue'
import EventEditor from './components/EventEditor.vue'
import { useStorylines } from './composables/useStorylines.js'

const store = useStorylines()

// 当前选中的故事线（计算属性，切换时自动更新）
const currentStoryline = computed(() => store.current())

// 页面加载时从本地存储读数据
store.load()
</script>

<style scoped>
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
  font-family: system-ui, sans-serif;
  color: #333;
}
header {
  margin-bottom: 24px;
}
h1 {
  font-size: 24px;
  font-weight: 500;
  margin-bottom: 6px;
}
.subtitle {
  color: #888;
  font-size: 14px;
  margin: 0;
}
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
.content {
  min-height: 300px;
  min-width: 0;
}
.placeholder {
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
  .layout {
    grid-template-columns: 1fr;
  }
}
</style>
