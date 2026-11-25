<template>
  <div class="home">
    <!-- 产品介绍区 -->
    <section class="hero">
      <h1>把散落的故事，变成一眼看清的时间轴</h1>
      <p class="lead">
        追剧、嗑 CP、读小说时，那些散落在笔记和截图里的线索——
        在这里按时间排成一条会动的轴，看清每个人物的来龙去脉。
      </p>
      <div class="hero-actions">
        <router-link to="/workspace" class="btn-primary">开始创作</router-link>
        <a href="#discover" class="btn-ghost">逛逛别人的故事</a>
      </div>
      <ul class="features">
        <li><span class="feature-title">按时间看</span><span class="feature-desc">事件自动排成时间轴，带动画</span></li>
        <li><span class="feature-title">按人物筛</span><span class="feature-desc">只看某一人的故事线</span></li>
        <li><span class="feature-title">分享出去</span><span class="feature-desc">公开作品，导出图片</span></li>
      </ul>
    </section>

    <!-- 发现页：公开故事线卡片墙 -->
    <section id="discover" class="discover">
      <div class="section-header">
        <h2>大家的故事</h2>
        <button class="refresh" @click="loadDiscover" :disabled="loading">刷新</button>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <div v-if="loading" class="state">加载中…</div>
      <div v-else-if="items.length === 0" class="state">
        还没有人公开故事线。成为第一个吧 —— <router-link to="/workspace">去创作</router-link>
      </div>
      <div v-else class="card-grid">
        <router-link
          v-for="item in items"
          :key="item.id"
          :to="`/detail/${item.id}`"
          class="card"
        >
          <div class="card-cover">
            <span class="avatars">{{ item.personA || 'A' }} <span class="x">×</span> {{ item.personB || 'B' }}</span>
          </div>
          <div class="card-body">
            <h3>{{ item.title }}</h3>
            <p class="card-desc">{{ item.description || '（暂无简介）' }}</p>
            <div class="card-meta">
              <span>{{ item.eventCount }} 个事件</span>
              <span class="view-hint">查看时间轴 →</span>
            </div>
          </div>
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { storylineApi } from '../api/client.js'
import { summaryFromApi } from '../api/adapter.js'

const items = ref([])
const loading = ref(false)
const error = ref('')

async function loadDiscover() {
  loading.value = true
  error.value = ''
  try {
    const data = await storylineApi.discover()
    items.value = data.map(summaryFromApi)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(loadDiscover)
</script>

<style scoped>
.home {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px 60px;
}
.hero {
  padding: 64px 0 48px;
  text-align: center;
}
h1 {
  font-size: 32px;
  font-weight: 500;
  margin: 0 0 16px;
  color: #222;
}
.lead {
  font-size: 15px;
  color: #666;
  line-height: 1.8;
  max-width: 620px;
  margin: 0 auto 24px;
}
.hero-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-bottom: 44px;
}
.btn-primary, .btn-ghost {
  padding: 11px 22px;
  border-radius: 8px;
  font-size: 14px;
  text-decoration: none;
  cursor: pointer;
}
.btn-primary {
  background: #7c5cbf;
  color: white;
}
.btn-primary:hover { background: #6b4faa; }
.btn-ghost {
  background: white;
  color: #555;
  border: 1px solid #ddd;
}
.btn-ghost:hover { border-color: #7c5cbf; color: #7c5cbf; }
.features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
.features li {
  background: #faf8fd;
  border: 1px solid #efe9f7;
  border-radius: 10px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.feature-title { font-size: 14px; font-weight: 500; color: #5b468f; }
.feature-desc { font-size: 12px; color: #888; }
.discover {
  padding-top: 24px;
}
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}
h2 {
  font-size: 20px;
  font-weight: 500;
  margin: 0;
}
.refresh {
  border: 1px solid #ddd;
  background: white;
  border-radius: 6px;
  padding: 5px 12px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
}
.state {
  text-align: center;
  color: #999;
  font-size: 14px;
  padding: 48px 0;
  background: #fafafa;
  border-radius: 10px;
}
.state a { color: #7c5cbf; }
.error { color: #f56c6c; font-size: 13px; }
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 18px;
}
.card {
  display: block;
  text-decoration: none;
  color: inherit;
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(124, 92, 191, 0.12);
}
.card-cover {
  height: 92px;
  background: linear-gradient(135deg, #e8ddf7, #d3e4f7);
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatars {
  font-size: 17px;
  color: #5b468f;
  font-weight: 500;
}
.x { color: #a892cf; margin: 0 4px; }
.card-body { padding: 16px; }
.card-body h3 { font-size: 15px; font-weight: 500; margin: 0 0 8px; }
.card-desc {
  font-size: 13px;
  color: #777;
  line-height: 1.6;
  margin: 0 0 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 42px;
}
.card-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}
.view-hint { color: #7c5cbf; }
@media (max-width: 680px) {
  h1 { font-size: 25px; }
  .features { grid-template-columns: 1fr; }
}
</style>
