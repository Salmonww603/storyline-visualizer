<template>
  <div class="manager">
    <h2>我的故事线</h2>

    <div v-if="!editingId" class="create-form">
      <input v-model="newTitle" type="text" placeholder="故事线标题，例如：主线 CP" @keyup.enter="handleCreate" />
      <div class="people-row">
        <input v-model="newPersonA" type="text" placeholder="主角 A 的名字" />
        <span class="x">×</span>
        <input v-model="newPersonB" type="text" placeholder="主角 B 的名字" />
      </div>
      <input v-model="newDescription" type="text" placeholder="简介（可选）" @keyup.enter="handleCreate" />
      <button @click="handleCreate">+ 新建</button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>

    <ul class="list">
      <li
        v-for="item in store.storylines.value"
        :key="item.id"
        :class="{ active: item.id === store.currentId.value }"
        @click="store.select(item.id)"
      >
        <template v-if="editingId === item.id">
          <div class="edit-form">
            <input v-model="editTitle" placeholder="标题" @keyup.enter="handleUpdate(item.id)" @keyup.esc="cancelEdit" />
            <div class="people-row">
              <input v-model="editPersonA" placeholder="主角 A" />
              <span class="x">×</span>
              <input v-model="editPersonB" placeholder="主角 B" />
            </div>
            <input v-model="editDescription" placeholder="简介" @keyup.enter="handleUpdate(item.id)" @keyup.esc="cancelEdit" />
            <label class="public-toggle">
              <input type="checkbox" v-model="editPublic" /> 公开（别人可在首页看到）
            </label>
            <div class="edit-actions">
              <button @click.stop="handleUpdate(item.id)">保存</button>
              <button class="ghost" @click.stop="cancelEdit">取消</button>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="item-info">
            <span class="title">{{ item.title }}</span>
            <span class="people" v-if="item.personA || item.personB">{{ item.personA || 'A' }} × {{ item.personB || 'B' }}</span>
            <span class="count">
              {{ item.events.length }} 个事件
              <span v-if="item.isPublic" class="public-badge">公开</span>
            </span>
          </div>
          <div class="actions">
            <button @click.stop="startEdit(item)">改</button>
            <button class="danger" @click.stop="handleRemove(item.id)">删</button>
          </div>
        </template>
      </li>
    </ul>

    <p v-if="store.storylines.value.length === 0" class="empty">还没有故事线，在上方填写并创建第一条吧。</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useStorylines } from '../composables/useStorylines.js'

const store = useStorylines()

const newTitle = ref('')
const newDescription = ref('')
const newPersonA = ref('')
const newPersonB = ref('')
const error = ref('')
const editingId = ref(null)
const editTitle = ref('')
const editDescription = ref('')
const editPersonA = ref('')
const editPersonB = ref('')
const editPublic = ref(false)

async function handleCreate() {
  if (!newTitle.value.trim()) {
    error.value = '标题不能为空'
    return
  }
  try {
    await store.create(newTitle.value.trim(), newDescription.value.trim(), newPersonA.value.trim(), newPersonB.value.trim())
    newTitle.value = ''
    newDescription.value = ''
    newPersonA.value = ''
    newPersonB.value = ''
    error.value = ''
  } catch (e) {
    error.value = e.message
  }
}

function startEdit(item) {
  editingId.value = item.id
  editTitle.value = item.title
  editDescription.value = item.description
  editPersonA.value = item.personA || ''
  editPersonB.value = item.personB || ''
  editPublic.value = !!item.isPublic
}

async function handleUpdate(id) {
  if (!editTitle.value.trim()) return
  try {
    // V2：update 传对象，包含公开状态（字段适配由 API 层负责）
    await store.update(id, {
      title: editTitle.value.trim(),
      description: editDescription.value.trim(),
      personA: editPersonA.value.trim(),
      personB: editPersonB.value.trim(),
      isPublic: editPublic.value,
    })
    editingId.value = null
  } catch (e) {
    error.value = e.message
  }
}

async function handleRemove(id) {
  if (!confirm('确定删除这条故事线吗？它的所有事件也会一起删除。')) return
  try {
    await store.remove(id)
  } catch (e) {
    error.value = e.message
  }
}

function cancelEdit() {
  editingId.value = null
}
</script>

<style scoped>
.manager {
  min-width: 0;
}
h2 {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 12px;
}
.create-form, .edit-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 8px;
}
.people-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.people-row input {
  min-width: 0;
  flex: 1;
}
.x {
  color: #999;
  font-size: 14px;
}
input {
  padding: 8px 10px;
  border: 1px solid #d0d0d0;
  border-radius: 6px;
  font-size: 14px;
  min-width: 0;
  box-sizing: border-box;
  width: 100%;
}
button {
  padding: 8px 14px;
  border: 1px solid #409eff;
  background: #409eff;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  white-space: nowrap;
}
button.ghost {
  background: white;
  color: #666;
  border-color: #d0d0d0;
}
button.danger {
  background: #f56c6c;
  border-color: #f56c6c;
}
.error {
  color: #f56c6c;
  font-size: 13px;
  margin: 6px 0;
}
.list {
  list-style: none;
  padding: 0;
  margin-top: 12px;
}
.list li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  min-width: 0;
}
.list li.active {
  border-color: #409eff;
  background: #f0f7ff;
}
.item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.title {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.people {
  font-size: 12px;
  color: #409eff;
}
.count {
  color: #aaa;
  font-size: 12px;
}
.actions, .edit-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}
.empty {
  color: #999;
  font-size: 13px;
}
.public-badge {
  display: inline-block;
  font-size: 10px;
  color: #7c5cbf;
  background: #f0eafb;
  border-radius: 4px;
  padding: 1px 5px;
  margin-left: 4px;
}
.public-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
}
.public-toggle input { width: auto; }
</style>
