<template>
  <div class="event-editor">
    <div class="header">
      <h2>事件 · {{ storyline.title }}</h2>
      <span class="count">{{ storyline.events.length }} 个事件</span>
    </div>

    <!-- 已有事件列表 -->
    <div class="event-list">
      <div v-for="event in storyline.events" :key="event.id" class="event-item">
        <img v-if="event.imageUrl" :src="event.imageUrl" class="thumb" alt="事件配图" />
        <div class="event-info" @click="startEdit(event)">
          <div class="event-date">{{ event.date || '未设日期' }}</div>
          <div class="event-title">{{ event.title }}</div>
          <div class="event-meta">
            <span class="people-tag" v-for="p in event.people" :key="p">{{ personName(p) }}</span>
            <span class="tag" v-for="t in event.tags" :key="t">#{{ t }}</span>
          </div>
        </div>
        <div class="actions">
          <button @click="startEdit(event)">改</button>
          <button class="danger" @click="handleRemove(event.id)">删</button>
        </div>
      </div>
      <p v-if="storyline.events.length === 0" class="empty">还没有事件，在下方添加第一条吧。</p>
    </div>

    <!-- 添加 / 编辑表单 -->
    <div class="form">
      <h3>{{ editingId ? '编辑事件' : '添加新事件' }}</h3>
      <div class="row">
        <input v-model="form.date" type="date" placeholder="日期" />
        <input v-model="form.title" type="text" placeholder="事件标题 *" />
      </div>
      <textarea v-model="form.description" placeholder="描述详情：发生了什么、为什么重要..." rows="3"></textarea>

      <!-- 参与者：显示真实姓名 -->
      <div class="field">
        <label>参与者：</label>
        <label class="radio"><input type="radio" value="A" v-model="peopleMode" /> 只有 {{ storyline.personA || 'A' }}</label>
        <label class="radio"><input type="radio" value="B" v-model="peopleMode" /> 只有 {{ storyline.personB || 'B' }}</label>
        <label class="radio"><input type="radio" value="AB" v-model="peopleMode" /> 两人互动</label>
      </div>

      <!-- 标签 -->
      <div class="field">
        <label>标签（用逗号分隔）：</label>
        <input v-model="tagsInput" type="text" placeholder="开端, 转折, 名场面" />
      </div>

      <!-- 配图 -->
      <div class="field">
        <label>配图：</label>
        <input type="file" accept="image/*" @change="handleImage" />
        <input v-model="form.imageUrl" type="text" placeholder="或粘贴图片 URL" />
        <img v-if="form.imageUrl" :src="form.imageUrl" class="preview" alt="预览" />
        <p v-if="imageHint" class="hint">{{ imageHint }}</p>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <div class="form-actions">
        <button @click="handleSave">保存事件</button>
        <button v-if="editingId" @click="cancelEdit">取消编辑</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useStorylines } from '../composables/useStorylines.js'

// 接收当前选中的故事线作为参数（从父组件传进来）
const props = defineProps({
  storyline: {
    type: Object,
    required: true,
  },
})

const store = useStorylines()

const editingId = ref(null)
const error = ref('')
const imageHint = ref('')
const peopleMode = ref('AB')       // 默认两人互动
const tagsInput = ref('')

// 表单数据
const form = reactive({
  date: '',
  title: '',
  description: '',
  imageUrl: '',
})

// 把 'A'/'B' 显示成真实名字（存的时候仍是 'A'/'B'，保证筛选逻辑稳定）
function personName(code) {
  if (code === 'A') return props.storyline.personA || 'A'
  if (code === 'B') return props.storyline.personB || 'B'
  return code
}

// 把 peopleMode 转成数组：'A'→['A'], 'B'→['B'], 'AB'→['A','B']
function peopleToArray(mode) {
  if (mode === 'AB') return ['A', 'B']
  return [mode]
}

// 把数组转回单选模式（编辑时用）
function arrayToPeople(people) {
  if (people.includes('A') && people.includes('B')) return 'AB'
  if (people.includes('A')) return 'A'
  if (people.includes('B')) return 'B'
  return 'AB'
}

// 本地图片转 base64（存进浏览器本地存储，不需要后端）
function handleImage(event) {
  const file = event.target.files[0]
  if (!file) return
  // 限制 2MB，因为本地存储空间有限
  if (file.size > 2 * 1024 * 1024) {
    imageHint.value = '图片太大（超过 2MB），请换一张小图或用图片 URL'
    return
  }
  const reader = new FileReader()
  reader.onload = (e) => {
    form.imageUrl = e.target.result
    imageHint.value = '图片已加载（会存到服务器，换设备也能看到）'
  }
  reader.readAsDataURL(file)
}

// 进入编辑模式：把事件数据填进表单
function startEdit(event) {
  editingId.value = event.id
  form.date = event.date
  form.title = event.title
  form.description = event.description
  form.imageUrl = event.imageUrl
  peopleMode.value = arrayToPeople(event.people)
  tagsInput.value = event.tags.join(', ')
  error.value = ''
}

// 保存（新建或更新）
async function handleSave() {
  if (!form.title.trim()) {
    error.value = '事件标题不能为空'
    return
  }
  const data = {
    date: form.date,
    title: form.title.trim(),
    description: form.description.trim(),
    people: peopleToArray(peopleMode.value),
    tags: tagsInput.value.split(/[,，]/).map(t => t.trim()).filter(Boolean),
    imageUrl: form.imageUrl,
  }
  try {
    if (editingId.value) {
      await store.updateEvent(props.storyline.id, editingId.value, data)
    } else {
      await store.addEvent(props.storyline.id, data)
    }
    resetForm()
  } catch (e) {
    error.value = e.message
  }
}

// 删除事件
async function handleRemove(eventId) {
  if (confirm('确定删除这个事件吗？')) {
    try {
      await store.removeEvent(props.storyline.id, eventId)
    } catch (e) {
      error.value = e.message
    }
  }
}

// 取消编辑 / 重置表单
function cancelEdit() {
  resetForm()
}

function resetForm() {
  editingId.value = null
  form.date = ''
  form.title = ''
  form.description = ''
  form.imageUrl = ''
  peopleMode.value = 'AB'
  tagsInput.value = ''
  error.value = ''
  imageHint.value = ''
}
</script>

<style scoped>
.event-editor {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
}
.header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 14px;
}
h2 {
  font-size: 17px;
  font-weight: 500;
  margin: 0;
}
h3 {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 10px;
}
.count {
  font-size: 12px;
  color: #999;
}
.event-list {
  margin-bottom: 20px;
}
.event-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  margin-bottom: 8px;
}
.thumb {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 4px;
}
.event-info {
  flex: 1;
  cursor: pointer;
}
.event-date {
  font-size: 12px;
  color: #999;
}
.event-title {
  font-size: 14px;
  font-weight: 500;
}
.event-meta {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}
.people-tag {
  font-size: 11px;
  padding: 1px 6px;
  background: #e8f4ff;
  color: #409eff;
  border-radius: 10px;
}
.tag {
  font-size: 11px;
  color: #999;
}
.actions {
  display: flex;
  gap: 6px;
}
button {
  padding: 6px 12px;
  border: 1px solid #409eff;
  background: #409eff;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  font-size: 13px;
}
button.danger {
  background: #f56c6c;
  border-color: #f56c6c;
}
.form {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
}
.row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
input, textarea {
  padding: 8px 10px;
  border: 1px solid #d0d0d0;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}
.row input:first-child {
  width: 160px;
}
.row input:last-child {
  flex: 1;
}
textarea {
  width: 100%;
  box-sizing: border-box;
  margin-bottom: 8px;
  resize: vertical;
}
.field {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 13px;
}
.radio {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}
.preview {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
}
.hint, .error {
  font-size: 12px;
  color: #e6a23c;
  margin: 4px 0;
}
.error {
  color: #f56c6c;
}
.form-actions {
  margin-top: 12px;
}
.empty {
  font-size: 13px;
  color: #999;
}
</style>
