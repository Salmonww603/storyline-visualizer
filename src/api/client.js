/**
 * HTTP 请求封装：所有后端调用都经过这里。
 * 做三件事：① 拼基础地址 ② 自动带 JWT token ③ 统一处理错误
 */

// 后端地址。开发期前端 5173、后端 8000，是两个服务，所以要写全地址。
// 部署时把这里改成后端域名即可（一个常量，方便切换）。
export const API_BASE = 'http://127.0.0.1:8000'

/**
 * 从浏览器本地存储读取 token。
 * token 是登录后服务器发的"身份凭条"，存起来以后每次请求带上。
 */
export function getToken() {
  return localStorage.getItem('storyline_token') || ''
}

/** 保存 token（登录成功后调用） */
export function setToken(token) {
  localStorage.setItem('storyline_token', token)
}

/** 清除 token（退出登录时调用） */
export function clearToken() {
  localStorage.removeItem('storyline_token')
}

/**
 * 通用请求函数。
 * @param {string} path   接口路径，如 '/api/auth/login'
 * @param {object} options { method, body, auth }
 *   - method: HTTP 方法，默认 GET
 *   - body: 请求体对象，会自动 JSON 序列化
 *   - auth: 是否需要带 token（需要登录的接口传 true）
 */
export async function request(path, options = {}) {
  const { method = 'GET', body, auth = false } = options

  // 组装请求头
  const headers = {}
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }
  if (auth) {
    const token = getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  let response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch (e) {
    // fetch 抛错 = 真正的网络层失败：后端没启动、地址写错、跨域被拒
    // 注意：后端返回 500 不会走到这里（那是 response.ok=false 的分支），
    // 所以这句只表示"连不上"，不是"服务器内部报错"
    console.error('网络请求失败：', e)
    throw new Error('无法连接服务器：请确认后端已启动（端口 8000）')
  }

  // 204 表示删除成功、没有返回内容
  if (response.status === 204) {
    return null
  }

  // 解析响应。后端可能返回 JSON 或纯文本，做个兜底
  let data
  try {
    data = await response.json()
  } catch {
    data = null
  }

  if (!response.ok) {
    // 401 = 没登录或 token 过期，清掉 token 让界面回到未登录状态
    if (response.status === 401) {
      clearToken()
    }
    // 后端 FastAPI 的错误信息在 detail 字段里
    // 注意：500 是服务器内部错误（如数据库字段太短、代码 bug），
    // 必须和"连不上"区分开，否则排查方向完全错误
    const message = data?.detail || `请求失败（${response.status}）`
    if (response.status === 500) {
      throw new Error(`服务器处理失败（500）：${message}。若含图片，可能是图片过大。`)
    }
    throw new Error(typeof message === 'string' ? message : '请求参数有误')
  }

  return data
}

// ===== 认证接口 =====
export const authApi = {
  register: (data) => request('/api/auth/register', { method: 'POST', body: data }),
  login: (data) => request('/api/auth/login', { method: 'POST', body: data }),
  me: () => request('/api/auth/me', { auth: true }),
}

// ===== 故事线接口 =====
export const storylineApi = {
  mine: () => request('/api/storylines/mine', { auth: true }),
  discover: () => request('/api/storylines/discover'),
  detail: (id) => request(`/api/storylines/${id}`),
  create: (data) => request('/api/storylines', { method: 'POST', body: data, auth: true }),
  update: (id, data) => request(`/api/storylines/${id}`, { method: 'PUT', body: data, auth: true }),
  remove: (id) => request(`/api/storylines/${id}`, { method: 'DELETE', auth: true }),
}

// ===== 事件接口 =====
export const eventApi = {
  create: (storylineId, data) =>
    request(`/api/events?storyline_id=${storylineId}`, { method: 'POST', body: data, auth: true }),
  update: (eventId, data) =>
    request(`/api/events/${eventId}`, { method: 'PUT', body: data, auth: true }),
  remove: (eventId) =>
    request(`/api/events/${eventId}`, { method: 'DELETE', auth: true }),
}
