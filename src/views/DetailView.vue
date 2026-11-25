<template>
  <div class="detail-page">
    <router-link to="/" class="back">← 返回发现页</router-link>

    <div v-if="loading" class="state">加载中…</div>
    <div v-else-if="error" class="state error">{{ error }}</div>
    <template v-else-if="storyline">
      <div class="page-head">
        <h1>{{ storyline.title }}</h1>
        <p class="subtitle">
          {{ storyline.personA || 'A' }} <span class="x">×</span> {{ storyline.personB || 'B' }}
          <span class="dot">·</span> {{ storyline.events.length }} 个事件
        </p>
        <p v-if="storyline.description" class="desc">{{ storyline.description }}</p>
      </div>
      <!-- 复用时间轴组件，只读展示（带筛选、动画、导出图） -->
      <Timeline :storyline="storyline" />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Timeline from '../components/Timeline.vue'
import { storylineApi } from '../api/client.js'
import { storylineFromApi } from '../api/adapter.js'

const route = useRoute()
const storyline = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const data = await storylineApi.detail(route.params.id)
    storyline.value = storylineFromApi(data)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px 20px 60px;
  font-family: system-ui, sans-serif;
  color: #333;
}
.back {
  display: inline-block;
  color: #7c5cbf;
  text-decoration: none;
  font-size: 13px;
  margin-bottom: 24px;
}
.back:hover { text-decoration: underline; }
.page-head { margin-bottom: 28px; }
h1 { font-size: 26px; font-weight: 500; margin: 0 0 10px; }
.subtitle { font-size: 14px; color: #7c5cbf; margin: 0 0 8px; }
.x, .dot { color: #bbb; margin: 0 6px; }
.desc { font-size: 14px; color: #666; line-height: 1.7; margin: 0; }
.state {
  text-align: center;
  color: #999;
  font-size: 14px;
  padding: 60px 0;
}
.error { color: #f56c6c; }
</style>
