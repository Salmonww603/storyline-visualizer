<template>
  <div class="share-page">
    <!-- 背景装饰：星点和光晕，纯 CSS，不依赖图片 -->
    <div class="bg-stars" aria-hidden="true"></div>
    <div class="bg-glow glow-a" aria-hidden="true"></div>
    <div class="bg-glow glow-b" aria-hidden="true"></div>

    <!-- 返回首页：沉浸式页面没有全局导航，这里单独放一个固定入口，滚动时始终可见 -->
    <router-link to="/" class="back-home">← 返回首页</router-link>

    <!-- 加载 / 错误态 -->
    <div v-if="loading" class="state">正在展开这段故事…</div>
    <div v-else-if="error" class="state error">
      <div class="error-symbol">◈</div>
      <p>{{ error }}</p>
      <router-link to="/" class="error-link">返回首页</router-link>
    </div>

    <template v-else-if="storyline">
      <!-- 顶部：标题 + 主角 + 简介，居中，带入场动画 -->
      <header class="share-head">
        <div class="head-badge">故事线 · STORYLINE</div>
        <h1 class="share-title">{{ storyline.title }}</h1>
        <div class="share-couple">
          <span class="person person-a">{{ storyline.personA || 'A' }}</span>
          <span class="cross">×</span>
          <span class="person person-b">{{ storyline.personB || 'B' }}</span>
        </div>
        <p v-if="storyline.description" class="share-desc">{{ storyline.description }}</p>
        <div class="share-meta">{{ storyline.events.length }} 个瞬间 · 按时间展开</div>
      </header>

      <!-- 筛选：胶囊 segmented，浅色玻璃质感 -->
      <div v-if="storyline.events.length > 0" class="filter-bar">
        <button
          v-for="opt in filterOptions"
          :key="opt.value"
          class="filter-btn"
          :class="{ active: filter === opt.value }"
          @click="switchFilter(opt.value)"
        >{{ opt.label }}</button>
      </div>

      <!-- 空态 -->
      <div v-if="storyline.events.length === 0" class="state">这段故事还没有记录下瞬间。</div>
      <div v-else-if="filteredEvents.length === 0" class="state">这个视角下还没有事件。</div>

      <!-- 时间轴：左右交替卡片 -->
      <div v-else class="timeline" :key="filter">
        <div class="center-line"><span class="line-fill"></span></div>
        <div
          v-for="(event, index) in filteredEvents"
          :key="event.id"
          class="moment"
          :class="index % 2 === 0 ? 'left' : 'right'"
          :style="{ animationDelay: (0.3 + index * 0.15) + 's' }"
          @click="openDetail(event)"
        >
          <div class="moment-dot" :class="dotClass(event)"></div>
          <div class="moment-card">
            <div class="moment-date">{{ event.date || '未设日期' }}</div>
            <h3 class="moment-title">{{ event.title }}</h3>
            <div class="moment-people">
              <span v-for="p in event.people" :key="p" class="chip" :class="'chip-' + p">{{ personName(p) }}</span>
              <span v-for="t in event.tags" :key="t" class="tag">#{{ t }}</span>
            </div>
            <img v-if="event.imageUrl" :src="event.imageUrl" class="moment-img" alt="事件配图" />
            <p v-if="event.description" class="moment-desc">{{ event.description }}</p>
          </div>
        </div>
        <div class="timeline-end">— 故事未完，待续 —</div>
      </div>

      <!-- 底部操作区 -->
      <footer class="share-footer">
        <button class="copy-btn" @click="copyLink">
          {{ copied ? '✓ 链接已复制' : '⬗ 复制分享链接' }}
        </button>
        <p class="footer-hint">把这个链接发给朋友，一起重温这段故事</p>
        <router-link to="/" class="footer-brand">◈ 故事线 · 记录你的每一段故事</router-link>
      </footer>

      <!-- 详情弹窗 -->
      <div v-if="detail" class="modal-mask" @click.self="closeDetail">
        <div class="modal">
          <button class="modal-close" @click="closeDetail">×</button>
          <div class="modal-date">{{ detail.date || '未设日期' }}</div>
          <h3 class="modal-title">{{ detail.title }}</h3>
          <div class="modal-people">
            <span v-for="p in detail.people" :key="p" class="chip" :class="'chip-' + p">{{ personName(p) }}</span>
          </div>
          <img v-if="detail.imageUrl" :src="detail.imageUrl" class="modal-img" alt="事件配图" />
          <p class="modal-desc">{{ detail.description || '（无描述）' }}</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { storylineApi } from '../api/client.js'
import { storylineFromApi } from '../api/adapter.js'

const route = useRoute()
const storyline = ref(null)
const loading = ref(true)
const error = ref('')
const filter = ref('all')
const detail = ref(null)
const copied = ref(false)

onMounted(async () => {
  try {
    // 用详情接口读数据。服务端已强制校验权限：
    // 公开内容谁都能读；私密的会直接返回 403（后端 detail 接口拦住）。
    // 这里保留 is_public 判断作为双保险——即使将来后端改动，也不会误展示私密内容。
    const data = await storylineApi.detail(route.params.id)
    if (!data.is_public) {
      error.value = '这条故事线未公开，无法分享。'
      return
    }
    storyline.value = storylineFromApi(data)
  } catch (e) {
    // 403 = 未公开且不是本人；404 = 链接失效。后端错误信息已足够友好，直接展示。
    error.value = e.message || '加载失败，链接可能已失效。'
  } finally {
    loading.value = false
  }
})

// 筛选按钮：显示真名
const filterOptions = computed(() => [
  { value: 'all', label: '全部' },
  { value: 'A', label: `只看${personName('A')}` },
  { value: 'B', label: `只看${personName('B')}` },
])

// 只看某人时，含此人的事件都显示（两人互动两边都在）
const filteredEvents = computed(() => {
  if (!storyline.value) return []
  if (filter.value === 'all') return storyline.value.events
  return storyline.value.events.filter(e => e.people.includes(filter.value))
})

function switchFilter(value) {
  filter.value = value
  detail.value = null
}

function personName(code) {
  if (!storyline.value) return code
  if (code === 'A') return storyline.value.personA || 'A'
  if (code === 'B') return storyline.value.personB || 'B'
  return code
}

// 节点颜色：两人=金紫，A=蓝，B=粉
function dotClass(event) {
  if (event.people.includes('A') && event.people.includes('B')) return 'dot-both'
  if (event.people.includes('A')) return 'dot-a'
  if (event.people.includes('B')) return 'dot-b'
  return 'dot-both'
}

function openDetail(event) { detail.value = event }
function closeDetail() { detail.value = null }

// 复制当前分享链接。优先用现代剪贴板 API，失败则降级到传统选中复制。
async function copyLink() {
  const url = window.location.href
  try {
    await navigator.clipboard.writeText(url)
  } catch {
    const input = document.createElement('textarea')
    input.value = url
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
  }
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>

<style scoped>
.share-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: linear-gradient(160deg, #1a1533 0%, #241a44 40%, #2d1b47 100%);
  color: #f0ecf8;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  padding: 0 20px 80px;
}

/* 返回首页：左上角固定，玻璃质感，在深色背景上清晰可见 */
.back-home {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 100;
  font-size: 13px;
  color: #d9c7f5;
  text-decoration: none;
  padding: 8px 16px;
  border: 1px solid rgba(217,199,245,.35);
  border-radius: 20px;
  background: rgba(30,22,55,.55);
  backdrop-filter: blur(8px);
  transition: all .25s;
}
.back-home:hover {
  color: #fff;
  border-color: rgba(217,199,245,.7);
  background: rgba(60,45,100,.75);
}

/* 背景：星点用径向渐变平铺，光晕用模糊圆 */
.bg-stars {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(1.5px 1.5px at 20% 15%, rgba(255,255,255,.7) 50%, transparent 50%),
    radial-gradient(1.5px 1.5px at 75% 25%, rgba(255,255,255,.6) 50%, transparent 50%),
    radial-gradient(2px 2px at 45% 60%, rgba(255,255,255,.5) 50%, transparent 50%),
    radial-gradient(1.5px 1.5px at 85% 70%, rgba(255,255,255,.6) 50%, transparent 50%),
    radial-gradient(1.5px 1.5px at 10% 85%, rgba(255,255,255,.5) 50%, transparent 50%),
    radial-gradient(2px 2px at 60% 90%, rgba(255,255,255,.4) 50%, transparent 50%);
  background-size: 320px 320px;
  opacity: .6;
  pointer-events: none;
}
.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  opacity: .35;
  pointer-events: none;
}
.glow-a { width: 380px; height: 380px; background: #7c5cbf; top: -120px; left: -80px; }
.glow-b { width: 320px; height: 320px; background: #d06a9c; top: 30%; right: -120px; }

.state {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 120px 20px;
  color: #c9bfe0;
  font-size: 15px;
}
.error-symbol { font-size: 40px; color: #a98fd6; margin-bottom: 12px; }
.error-link { color: #c9a8f0; display: inline-block; margin-top: 16px; }

/* 顶部标题区 */
.share-head {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 720px;
  margin: 0 auto;
  padding: 90px 0 40px;
  animation: headIn .8s ease-out both;
}
@keyframes headIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.head-badge {
  display: inline-block;
  font-size: 11px;
  letter-spacing: 3px;
  color: #b9a3e0;
  border: 1px solid rgba(185,163,224,.4);
  border-radius: 20px;
  padding: 5px 16px;
  margin-bottom: 22px;
}
.share-title {
  font-size: clamp(28px, 5vw, 44px);
  font-weight: 600;
  margin: 0 0 20px;
  background: linear-gradient(90deg, #fff, #d9c7f5, #fff);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.share-couple {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  font-size: clamp(18px, 3.5vw, 26px);
  margin-bottom: 18px;
}
.person { font-weight: 500; }
.person-a { color: #7fc4ff; text-shadow: 0 0 18px rgba(127,196,255,.5); }
.person-b { color: #ffa8cf; text-shadow: 0 0 18px rgba(255,168,207,.5); }
.cross { color: #a98fd6; font-size: 20px; }
.share-desc {
  font-size: 14px;
  color: #c4b8dd;
  line-height: 1.7;
  max-width: 560px;
  margin: 0 auto 14px;
}
.share-meta { font-size: 12px; color: #8d80ab; letter-spacing: 1px; }

/* 筛选 */
.filter-bar {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: center;
  gap: 4px;
  margin: 0 auto 50px;
  background: rgba(255,255,255,.06);
  border: 1px solid rgba(255,255,255,.1);
  border-radius: 24px;
  padding: 4px;
  width: fit-content;
  backdrop-filter: blur(8px);
}
.filter-btn {
  border: none;
  background: transparent;
  color: #b6a9cf;
  border-radius: 20px;
  padding: 8px 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all .25s;
}
.filter-btn:hover { color: #fff; }
.filter-btn.active {
  background: linear-gradient(135deg, #7c5cbf, #a06fd0);
  color: #fff;
  box-shadow: 0 2px 12px rgba(124,92,191,.5);
}

/* 时间轴：居中轴线 + 左右交替卡片 */
.timeline {
  position: relative;
  z-index: 1;
  max-width: 900px;
  margin: 0 auto;
  padding: 10px 0 40px;
}
.center-line {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  transform: translateX(-50%);
  background: rgba(255,255,255,.1);
}
.line-fill {
  display: block;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, #7fc4ff, #b98fe0, #ffa8cf);
  transform-origin: top;
  animation: growLine 1.6s ease-out .2s both;
}
@keyframes growLine {
  from { transform: scaleY(0); }
  to { transform: scaleY(1); }
}

.moment {
  position: relative;
  width: 50%;
  padding: 0 42px 36px 0;
  opacity: 0;
}
.moment.right {
  margin-left: 50%;
  padding: 0 0 36px 42px;
}
.moment.left { animation: slideLeft .6s ease-out both; }
.moment.right { animation: slideRight .6s ease-out both; }
@keyframes slideLeft {
  from { opacity: 0; transform: translateX(-30px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes slideRight {
  from { opacity: 0; transform: translateX(30px); }
  to { opacity: 1; transform: translateX(0); }
}
.moment-dot {
  position: absolute;
  top: 18px;
  right: -8px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #b98fe0;
  border: 3px solid #241a44;
  box-shadow: 0 0 0 3px rgba(185,143,224,.35), 0 0 16px rgba(185,143,224,.8);
  z-index: 2;
}
.moment.right .moment-dot {
  right: auto;
  left: -8px;
}
.dot-both { background: #c9a8f0; box-shadow: 0 0 0 3px rgba(201,168,240,.35), 0 0 16px rgba(201,168,240,.8); }
.dot-a { background: #7fc4ff; box-shadow: 0 0 0 3px rgba(127,196,255,.35), 0 0 16px rgba(127,196,255,.8); }
.dot-b { background: #ffa8cf; box-shadow: 0 0 0 3px rgba(255,168,207,.35), 0 0 16px rgba(255,168,207,.8); }

.moment-card {
  background: rgba(255,255,255,.07);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 14px;
  padding: 18px 20px;
  cursor: pointer;
  backdrop-filter: blur(10px);
  transition: transform .25s, border-color .25s, background .25s;
}
.moment-card:hover {
  transform: translateY(-4px);
  border-color: rgba(201,168,240,.6);
  background: rgba(255,255,255,.11);
}
.moment-date { font-size: 12px; color: #a99cc7; margin-bottom: 6px; }
.moment-title { font-size: 17px; font-weight: 500; margin: 0 0 10px; color: #fff; }
.moment-people { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.chip { font-size: 11px; padding: 2px 9px; border-radius: 10px; }
.chip-A { background: rgba(127,196,255,.2); color: #9fd4ff; }
.chip-B { background: rgba(255,168,207,.2); color: #ffb9d9; }
.tag { font-size: 11px; color: #a99cc7; }
.moment-img {
  width: 100%;
  max-height: 220px;
  object-fit: cover;
  border-radius: 10px;
  margin-top: 10px;
}
.moment-desc {
  font-size: 13px;
  line-height: 1.7;
  color: #cfc4e2;
  margin: 10px 0 0;
  white-space: pre-wrap;
}
.timeline-end {
  text-align: center;
  color: #7d6f9c;
  font-size: 12px;
  letter-spacing: 2px;
  padding-top: 10px;
}

/* 底部 */
.share-footer {
  position: relative;
  z-index: 1;
  text-align: center;
  margin-top: 60px;
}
.copy-btn {
  border: none;
  background: linear-gradient(135deg, #7c5cbf, #a06fd0);
  color: #fff;
  border-radius: 24px;
  padding: 12px 28px;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(124,92,191,.5);
  transition: transform .2s, box-shadow .2s;
}
.copy-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(124,92,191,.7); }
.footer-hint { font-size: 12px; color: #8d80ab; margin: 14px 0 30px; }
.footer-brand { font-size: 12px; color: #6f638c; text-decoration: none; }
.footer-brand:hover { color: #b9a3e0; }

/* 弹窗 */
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(10,8,20,.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn .2s ease-out;
  backdrop-filter: blur(4px);
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.modal {
  position: relative;
  background: linear-gradient(160deg, #2b2150, #241a44);
  border: 1px solid rgba(255,255,255,.15);
  border-radius: 16px;
  padding: 28px;
  width: min(92vw, 480px);
  max-height: 85vh;
  overflow-y: auto;
  animation: modalIn .3s cubic-bezier(.2,.9,.3,1.2);
}
@keyframes modalIn {
  from { opacity: 0; transform: scale(.92) translateY(12px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
.modal-close {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 30px;
  height: 30px;
  border: none;
  background: rgba(255,255,255,.1);
  color: #ddd;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  line-height: 1;
}
.modal-date { font-size: 12px; color: #a99cc7; }
.modal-title { font-size: 22px; font-weight: 500; margin: 8px 0 12px; color: #fff; }
.modal-people { display: flex; gap: 6px; flex-wrap: wrap; }
.modal-img { width: 100%; border-radius: 10px; margin-top: 16px; }
.modal-desc { font-size: 14px; line-height: 1.8; color: #cfc4e2; margin-top: 16px; white-space: pre-wrap; }

/* 手机适配：单列，轴线靠左 */
@media (max-width: 640px) {
  .share-head { padding: 60px 0 30px; }
  .timeline { padding-left: 8px; }
  .center-line { left: 8px; }
  .moment, .moment.right {
    width: 100%;
    margin-left: 0;
    padding: 0 0 28px 34px;
  }
  .moment-dot, .moment.right .moment-dot { left: 0; right: auto; }
}
</style>
