import { ref } from 'vue'

// 故事线数据仓库：集中管理所有故事线的增删改查
// 用 ref 包裹数组，这样 Vue 能监听变化并自动更新页面

const storylines = ref([])
const currentId = ref(null) // 当前选中的故事线 id
let nextId = 1              // 自增 id 生成器

// 加载：从 localStorage 读取数据（第5步会用到，这里先留好接口）
function load() {
  const saved = localStorage.getItem('storylines')
  if (saved) {
    storylines.value = JSON.parse(saved)
    // 兼容老数据：早期创建的故事线没有 personA/personB，补空字符串
    storylines.value.forEach(s => {
      if (s.personA === undefined) s.personA = ''
      if (s.personB === undefined) s.personB = ''
    })
    // 恢复时 nextId 要跳过已用过的最大值，避免 id 重复
    nextId = Math.max(0, ...storylines.value.map(s => s.id)) + 1
    if (storylines.value.length > 0) {
      currentId.value = storylines.value[0].id
    }
  }
}

// 保存：把当前数据写回 localStorage
function save() {
  localStorage.setItem('storylines', JSON.stringify(storylines.value))
}

// 创建一条新故事线（含 A、B 两位主角的名字）
function create(title, description = '', personA = '', personB = '') {
  const item = {
    id: nextId++,
    title,
    description,
    personA,   // 主角 A 的名字
    personB,   // 主角 B 的名字
    events: [],
  }
  storylines.value.push(item)
  currentId.value = item.id
  save()
  return item
}

// 根据 id 查找故事线
function getById(id) {
  return storylines.value.find(s => s.id === id)
}

// 当前选中的故事线
function current() {
  return getById(currentId.value)
}

// 切换到某条故事线
function select(id) {
  currentId.value = id
}

// 更新故事线（标题、简介、A/B 名字）
function update(id, title, description, personA, personB) {
  const item = getById(id)
  if (item) {
    item.title = title
    item.description = description
    item.personA = personA
    item.personB = personB
    save()
  }
}

// 删除故事线（同时处理：删的是当前选中的怎么办）
function remove(id) {
  storylines.value = storylines.value.filter(s => s.id !== id)
  if (currentId.value === id) {
    // 如果删的是当前选中的，自动切到第一条；没有就置空
    currentId.value = storylines.value.length > 0 ? storylines.value[0].id : null
  }
  save()
}

// ===== 事件相关操作 =====

// 生成事件 id：用时间戳，避免和故事线的自增 id 冲突
function makeEventId() {
  return Date.now() + Math.floor(Math.random() * 1000)
}

// 给某条故事线添加事件
function addEvent(storylineId, eventData) {
  const item = getById(storylineId)
  if (!item) return
  const event = {
    id: makeEventId(),
    date: eventData.date || '',
    title: eventData.title,
    description: eventData.description || '',
    people: eventData.people || [],   // ['A'] / ['B'] / ['A','B']
    tags: eventData.tags || [],
    imageUrl: eventData.imageUrl || '',
  }
  item.events.push(event)
  // 按日期排序，保证时间轴顺序正确
  item.events.sort((a, b) => a.date.localeCompare(b.date))
  save()
  return event
}

// 更新某条故事线里的某个事件
function updateEvent(storylineId, eventId, eventData) {
  const item = getById(storylineId)
  if (!item) return
  const event = item.events.find(e => e.id === eventId)
  if (!event) return
  Object.assign(event, eventData)      // 把新数据合并进旧事件
  item.events.sort((a, b) => a.date.localeCompare(b.date))
  save()
}

// 删除某条故事线里的某个事件
function removeEvent(storylineId, eventId) {
  const item = getById(storylineId)
  if (!item) return
  item.events = item.events.filter(e => e.id !== eventId)
  save()
}

// 把这个仓库里的东西暴露出去，给组件用
export function useStorylines() {
  return {
    storylines,
    currentId,
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
