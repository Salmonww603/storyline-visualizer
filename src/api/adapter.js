/**
 * 数据适配器：前后端字段格式互转。
 *
 * 为什么需要：V1 前端组件用 camelCase（personA/date/imageUrl），
 * 后端 API 用 snake_case（person_a/event_date/image_url），
 * 而且 people 前端是数组 ['A','B']、后端是字符串 'AB'。
 *
 * 在这里集中转换，组件层完全不用改——这就是"适配器模式"：
 * 让不兼容的两方通过一层转换协作，而不是改动其中一方。
 */

/** 后端故事线 → 前端格式（含事件列表） */
export function storylineFromApi(s) {
  return {
    id: s.id,
    title: s.title,
    description: s.description || '',
    personA: s.person_a || '',
    personB: s.person_b || '',
    isPublic: !!s.is_public,
    ownerId: s.owner_id,
    events: (s.events || []).map(eventFromApi),
  }
}

/** 后端发现页的精简故事线 → 前端格式（没有 events） */
export function summaryFromApi(s) {
  return {
    id: s.id,
    title: s.title,
    description: s.description || '',
    personA: s.person_a || '',
    personB: s.person_b || '',
    ownerId: s.owner_id,
    eventCount: s.event_count || 0,
  }
}

/** 前端故事线数据 → 后端格式（创建/更新时用） */
export function storylineToApi(data) {
  const result = {}
  // 只把传进来的字段转成后端命名，没传的不动（配合后端的局部更新）
  if ('title' in data) result.title = data.title
  if ('description' in data) result.description = data.description
  if ('personA' in data) result.person_a = data.personA
  if ('personB' in data) result.person_b = data.personB
  if ('isPublic' in data) result.is_public = data.isPublic
  return result
}

/** 后端事件 → 前端格式 */
export function eventFromApi(e) {
  return {
    id: e.id,
    date: e.event_date || '',
    title: e.title,
    description: e.description || '',
    // 后端 'AB' → 前端 ['A','B']；空字符串 → []
    people: peopleFromApi(e.people),
    tags: e.tags || [],
    imageUrl: e.image_url || '',
  }
}

/** 前端事件数据 → 后端格式 */
export function eventToApi(data) {
  const result = {}
  if ('date' in data) result.event_date = data.date
  if ('title' in data) result.title = data.title
  if ('description' in data) result.description = data.description
  if ('people' in data) result.people = peopleToApi(data.people)
  if ('tags' in data) result.tags = data.tags
  if ('imageUrl' in data) result.image_url = data.imageUrl
  return result
}

/** 后端参与者字符串 'AB' → 前端数组 ['A','B'] */
function peopleFromApi(str) {
  if (!str) return []
  return str.split('').filter(c => c === 'A' || c === 'B')
}

/** 前端参与者数组 ['A','B'] → 后端字符串 'AB' */
function peopleToApi(arr) {
  if (!Array.isArray(arr)) return 'A'
  // 保证顺序稳定：A 在前 B 在后
  const hasA = arr.includes('A')
  const hasB = arr.includes('B')
  if (hasA && hasB) return 'AB'
  if (hasA) return 'A'
  if (hasB) return 'B'
  return 'A'
}
