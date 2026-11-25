<template>
  <div class="migrate-page">
    <div class="migrate-card">
      <router-link to="/" class="back">← 返回首页</router-link>
      <h1>V1 数据迁移</h1>
      <p class="lead">把早期存在浏览器本地的故事线，导入到服务器数据库（MySQL）。一次性操作，导入后可在本机备份里找回原数据。</p>

      <!-- 读取本地数据 -->
      <div v-if="loadingLocal" class="state">正在读取浏览器本地数据…</div>

      <template v-else>
        <!-- 没读到数据 -->
        <div v-if="localData === null" class="state error">
          <p>没有找到 V1 本地数据（localStorage 里的 <code>storylines</code>）。</p>
          <p class="hint">可能原因：① 你从没在 V1 版本创建过故事线；② 之前换过浏览器/设备；③ 浏览器数据被清理过。</p>
        </div>

        <!-- 读到数据但为空 -->
        <div v-else-if="localData.length === 0" class="state">
          找到了本地数据，但是空的（0 条故事线），无需迁移。
        </div>

        <!-- 有数据：预览 + 操作 -->
        <template v-else>
          <div class="preview">
            <div class="preview-head">
              <span class="preview-title">发现 {{ localData.length }} 条故事线，共 {{ totalEvents }} 个事件</span>
              <span v-if="migrated" class="badge done">✓ 已迁移</span>
              <span v-else class="badge">待迁移</span>
            </div>
            <div v-for="s in localData" :key="s.id" class="preview-item">
              <div class="preview-line-title">{{ s.title || '（无标题）' }}</div>
              <div class="preview-line-meta">
                {{ s.personA || 'A' }} × {{ s.personB || 'B' }} · {{ (s.events || []).length }} 个事件
              </div>
            </div>
          </div>

          <!-- 登录状态 -->
          <div v-if="!loggedIn" class="login-box">
            <p>请先登录要导入到的账号：</p>
            <div class="form-row">
              <input v-model="username" placeholder="用户名" />
              <input v-model="password" type="password" placeholder="密码" @keyup.enter="doLogin" />
              <button :disabled="logging" @click="doLogin">{{ logging ? '登录中…' : '登录' }}</button>
            </div>
          </div>
          <div v-else class="login-ok">
            ✓ 将以 <strong>{{ auth.username.value || username }}</strong> 的身份导入
          </div>

          <p v-if="actionError" class="action-error">{{ actionError }}</p>

          <div class="actions">
            <button class="btn-primary" :disabled="!loggedIn || migrating" @click="startMigrate">
              {{ migrating ? '迁移中…' : '开始迁移到 MySQL' }}
            </button>
            <button class="btn-ghost" :disabled="migrating" @click="downloadBackup">导出本地数据备份 (.json)</button>
          </div>

          <!-- 迁移结果 -->
          <div v-if="result" class="result">
            <h3>迁移完成</h3>
            <p>成功导入 {{ result.ok }} 条故事线、{{ result.events }} 个事件。</p>
            <p v-if="result.failed.length" class="action-error">
              {{ result.failed.length }} 条失败：{{ result.failed.join('、') }}
            </p>
            <p class="hint">原数据已在浏览器里改名为 <code>storylines_v1_backup</code> 保留，不会丢失。你可以去工作台查看，确认无误后再决定是否清理备份。</p>
            <router-link to="/workspace" class="go-workspace">去工作台查看 →</router-link>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storylineApi, eventApi } from '../api/client.js'
import { storylineToApi, eventToApi } from '../api/adapter.js'
import { useAuth } from '../stores/auth.js'

const auth = useAuth()
const localData = ref(null)     // null = 没找到；[] = 空；数组 = 有数据
const loadingLocal = ref(true)
const migrated = ref(false)
const username = ref('')
const password = ref('')
const logging = ref(false)
const migrating = ref(false)
const actionError = ref('')
const result = ref(null)

const loggedIn = computed(() => auth.isLoggedIn.value)
const totalEvents = computed(() =>
  (localData.value || []).reduce((sum, s) => sum + (s.events || []).length, 0)
)

onMounted(() => {
  try {
    const raw = localStorage.getItem('storylines')
    if (raw === null) {
      localData.value = null
    } else {
      const parsed = JSON.parse(raw)
      localData.value = Array.isArray(parsed) ? parsed : null
    }
    migrated.value = localStorage.getItem('storylines_v1_backup') !== null
  } catch (e) {
    actionError.value = '读取本地数据失败：' + e.message
    localData.value = null
  } finally {
    loadingLocal.value = false
  }
})

async function doLogin() {
  actionError.value = ''
  if (!username.value || !password.value) {
    actionError.value = '请输入用户名和密码'
    return
  }
  logging.value = true
  try {
    const ok = await auth.login(username.value, password.value)
    if (!ok) actionError.value = '登录失败，请检查用户名密码'
  } catch (e) {
    actionError.value = '登录失败：' + e.message
  } finally {
    logging.value = false
  }
}

/**
 * 迁移主逻辑：逐条故事线创建，再逐条事件创建。
 * 用串行 await（不用 Promise.all）：一是后端接口简单，二是失败时能准确知道停在哪条，
 * 三是 artificially 限制并发，避免一次性灌太多数据把后端打满。
 */
async function startMigrate() {
  if (!loggedIn.value || !localData.value) return
  migrating.value = true
  actionError.value = ''
  result.value = null
  let ok = 0
  let events = 0
  const failed = []

  for (const s of localData.value) {
    try {
      // 创建故事线：V1 数据默认不公开，迁过来后在后台手动公开
      const created = await storylineApi.create(
        storylineToApi({
          title: s.title || '（未命名故事线）',
          description: s.description || '',
          personA: s.personA || '',
          personB: s.personB || '',
          isPublic: false,
        })
      )
      // 再逐个创建事件
      for (const e of (s.events || [])) {
        try {
          await eventApi.create(created.id, eventToApi({
            date: e.date || '',
            title: e.title || '（未命名事件）',
            description: e.description || '',
            people: e.people || ['A'],
            tags: e.tags || [],
            imageUrl: e.imageUrl || '',
          }))
          events++
        } catch (ee) {
          failed.push(`${s.title}/事件「${e.title}」: ${ee.message}`)
        }
      }
      ok++
    } catch (se) {
      failed.push(`${s.title}: ${se.message}`)
    }
  }

  // 备份原数据：改名而不是删除，可回退
  try {
    const raw = localStorage.getItem('storylines')
    if (raw !== null && localStorage.getItem('storylines_v1_backup') === null) {
      localStorage.setItem('storylines_v1_backup', raw)
      migrated.value = true
    }
  } catch (e) {
    actionError.value = '数据已导入，但备份到本地失败：' + e.message
  }

  result.value = { ok, events, failed }
  migrating.value = false
}

/** 导出备份：把 localStorage 原始数据下载成 json 文件 */
function downloadBackup() {
  const raw = localStorage.getItem('storylines') || '[]'
  const blob = new Blob([raw], { type: 'application/json;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'storylines_v1_backup.json'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.migrate-page {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 60px 20px;
  background: #f7f7f9;
  font-family: system-ui, -apple-system, sans-serif;
  color: #333;
}
.migrate-card {
  background: #fff;
  border: 1px solid #eaeaea;
  border-radius: 12px;
  padding: 32px;
  width: min(100%, 640px);
}
.back { color: #7c5cbf; text-decoration: none; font-size: 13px; }
.back:hover { text-decoration: underline; }
h1 { font-size: 22px; font-weight: 500; margin: 20px 0 8px; }
.lead { font-size: 13px; color: #888; line-height: 1.7; margin: 0 0 24px; }
.state { text-align: center; padding: 30px 10px; color: #888; font-size: 14px; line-height: 1.8; }
.state.error { color: #c0392b; }
.hint { font-size: 12px; color: #999; line-height: 1.7; }
code { background: #f2f2f5; padding: 1px 5px; border-radius: 4px; font-size: 12px; }

.preview { border: 1px solid #eaeaea; border-radius: 8px; margin-bottom: 20px; }
.preview-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 16px; background: #faf9fd; border-bottom: 1px solid #eaeaea;
}
.preview-title { font-size: 14px; font-weight: 500; }
.badge { font-size: 12px; color: #a06fd0; background: #f3eafb; padding: 3px 10px; border-radius: 12px; }
.badge.done { color: #2e8b57; background: #eaf7ef; }
.preview-item { padding: 12px 16px; border-bottom: 1px solid #f2f2f2; }
.preview-item:last-child { border-bottom: none; }
.preview-line-title { font-size: 14px; }
.preview-line-meta { font-size: 12px; color: #999; margin-top: 4px; }

.login-box { background: #faf9fd; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
.login-box p { font-size: 13px; margin: 0 0 12px; }
.form-row { display: flex; gap: 8px; }
.form-row input {
  flex: 1; min-width: 0; padding: 9px 12px; border: 1px solid #ddd;
  border-radius: 6px; font-size: 13px; box-sizing: border-box;
}
.form-row button {
  padding: 9px 16px; border: none; border-radius: 6px; background: #7c5cbf;
  color: #fff; font-size: 13px; cursor: pointer; white-space: nowrap;
}
.form-row button:disabled { background: #c9c0dd; cursor: not-allowed; }
.login-ok { font-size: 13px; color: #2e8b57; padding: 12px 0; }
.action-error { font-size: 13px; color: #c0392b; line-height: 1.6; }

.actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 8px; }
.btn-primary, .btn-ghost {
  padding: 11px 20px; border-radius: 8px; font-size: 14px; cursor: pointer;
}
.btn-primary { border: none; background: #7c5cbf; color: #fff; }
.btn-primary:disabled { background: #c9c0dd; cursor: not-allowed; }
.btn-ghost { border: 1px solid #ddd; background: #fff; color: #666; }
.btn-ghost:disabled { opacity: .5; cursor: not-allowed; }

.result { margin-top: 24px; padding: 20px; background: #eaf7ef; border-radius: 8px; }
.result h3 { font-size: 16px; margin: 0 0 10px; color: #2e8b57; }
.result p { font-size: 13px; line-height: 1.7; margin: 6px 0; }
.go-workspace { display: inline-block; margin-top: 12px; color: #7c5cbf; font-size: 14px; text-decoration: none; }
</style>
