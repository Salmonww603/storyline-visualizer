import { ref } from 'vue'
import { storylineApi, eventApi } from '../api/client.js'
import {
  storylineFromApi, storylineToApi, eventToApi,
} from '../api/adapter.js'

/**
 * 故事线数据仓库（V2 版）：数据从后端 API 读写，不再存浏览器本地。
 *
 * 对外暴露的方法和 V1 完全一样（load/create/update/remove/addEvent...），
 * 所以 StorylineManager、EventEditor 这些组件几乎不用改。
 * 区别只是每个方法内部从"操作 localStorage"变成"发 HTTP 请求"——
 * 这就是把数据层单独抽出来的价值。
 *
 * 注意：所有方法都是 async（因为网络请求是异步的）。
 */

const storylines = ref([])      // 我的故事线列表（含 events）
const currentId = ref(null)     // 当前选中的故事线 id
const loading = ref(false)
const error = ref('')

/** 从后端加载"我的故事线"，每条再单独拉详情（含事件） */
async function load() {
  loading.value = true
  error.value = ''
  try {
    const summaries = await storylineApi.mine()
    // 列表接口是精简版（不含事件），逐条拉详情拿完整事件
    // 并发请求：Promise.all 比 for 循环逐个 await 快得多
    const detailed = await Promise.all(
      summaries.map(s => storylineApi.detail(s.id))
    )
    storylines.value = detailed.map(storylineFromApi)
    if (storylines.value.length > 0) {
      // 尽量保持原来的选中项；没有就选第一条
      const stillExists = storylines.value.some(s => s.id === currentId.value)
      currentId.value = stillExists ? currentId.value : storylines.value[0].id
    } else {
      currentId.value = null
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

/** 创建故事线 */
async function create(title, description = '', personA = '', personB = '') {
  error.value = ''
  try {
    const data = storylineToApi({ title, description, personA, personB, isPublic: false })
    const created = await storylineApi.create(data)
    const item = storylineFromApi(created)
    storylines.value.push(item)
    currentId.value = item.id
    return item
  } catch (e) {
    error.value = e.message
    throw e
  }
}

/** 根据 id 查找（本地缓存里找） */
function getById(id) {
  return storylines.value.find(s => s.id === id)
}

/** 当前选中的故事线 */
function current() {
  return getById(currentId.value)
}

/** 切换选中的故事线 */
function select(id) {
  currentId.value = id
}

/** 更新故事线（标题/简介/A B 名字/公开状态） */
async function update(id, fields) {
  error.value = ''
  try {
    const data = storylineToApi(fields)
    const updated = await storylineApi.update(id, data)
    const index = storylines.value.findIndex(s => s.id === id)
    if (index !== -1) {
      storylines.value[index] = storylineFromApi(updated)
    }
  } catch (e) {
    error.value = e.message
    throw e
  }
}

/** 删除故事线 */
async function remove(id) {
  error.value = ''
  try {
    await storylineApi.remove(id)
    storylines.value = storylines.value.filter(s => s.id !== id)
    if (currentId.value === id) {
      currentId.value = storylines.value.length > 0 ? storylines.value[0].id : null
    }
  } catch (e) {
    error.value = e.message
    throw e
  }
}

// ===== 事件相关操作 =====

/** 添加事件：后端返回新事件，本地拿到后补一个临时 id 的占位，再整体刷新这条故事线 */
async function addEvent(storylineId, eventData) {
  error.value = ''
  try {
    const data = eventToApi(eventData)
    await eventApi.create(storylineId, data)
    // 重新拉这条故事线的详情，拿到带正确 id 和排序的事件列表
    const fresh = await storylineApi.detail(storylineId)
    const index = storylines.value.findIndex(s => s.id === storylineId)
    if (index !== -1) {
      storylines.value[index] = storylineFromApi(fresh)
    }
  } catch (e) {
    error.value = e.message
    throw e
  }
}

/** 更新事件 */
async function updateEvent(storylineId, eventId, eventData) {
  error.value = ''
  try {
    const data = eventToApi(eventData)
    await eventApi.update(eventId, data)
    const fresh = await storylineApi.detail(storylineId)
    const index = storylines.value.findIndex(s => s.id === storylineId)
    if (index !== -1) {
      storylines.value[index] = storylineFromApi(fresh)
    }
  } catch (e) {
    error.value = e.message
    throw e
  }
}

/** 删除事件 */
async function removeEvent(storylineId, eventId) {
  error.value = ''
  try {
    await eventApi.remove(eventId)
    const fresh = await storylineApi.detail(storylineId)
    const index = storylines.value.findIndex(s => s.id === storylineId)
    if (index !== -1) {
      storylines.value[index] = storylineFromApi(fresh)
    }
  } catch (e) {
    error.value = e.message
    throw e
  }
}

export function useStorylines() {
  return {
    storylines,
    currentId,
    loading,
    error,
    current,
    load,
    create,
    getById,
    select,
    update,
    remove,
    addEvent,
    updateEvent,
    removeEvent,
  }
}
