/**
 * 全局登录状态：一个精简的 store。
 * 用 reactive 包一个对象，所有组件 import 后读到的是同一份数据。
 * 这样登录后在导航栏显示用户名、路由守卫判断登录态，都从这里读。
 */
import { reactive, computed } from 'vue'
import { authApi, getToken, setToken, clearToken } from '../api/client.js'

// 全局唯一的状态对象
const state = reactive({
  token: getToken(),   // 页面刷新后从本地恢复 token
  user: null,          // 当前用户信息 {id, username, email}
  loading: false,
})

/** 是否已登录（计算属性，token 变了自动更新） */
const isLoggedIn = computed(() => !!state.token)

/** 当前用户名 */
const username = computed(() => state.user?.username || '')

/**
 * 登录：调接口拿 token，存起来，顺便获取用户信息。
 * @returns {Promise<boolean>} 是否成功
 */
async function login(username, password) {
  state.loading = true
  try {
    const res = await authApi.login({ username, password })
    setToken(res.access_token)
    state.token = res.access_token
    // 拿到 token 后再请求一次用户信息，存到 state.user
    await fetchMe()
    return true
  } finally {
    state.loading = false
  }
}

/**
 * 注册：注册成功后自动登录（体验更顺，不用注册完再输一遍密码）
 */
async function register(username, email, password) {
  state.loading = true
  try {
    await authApi.register({ username, email, password })
    return await login(username, password)
  } finally {
    state.loading = false
  }
}

/** 获取当前用户信息（失败也不影响，比如 token 过期时） */
async function fetchMe() {
  try {
    state.user = await authApi.me()
  } catch {
    state.user = null
  }
}

/** 退出登录：清 token、清用户信息 */
function logout() {
  clearToken()
  state.token = ''
  state.user = null
}

// 如果页面刷新时本地有 token，自动拉一次用户信息（这样导航栏能显示用户名）
if (state.token) {
  fetchMe()
}

export function useAuth() {
  return {
    state,
    isLoggedIn,
    username,
    login,
    register,
    logout,
    fetchMe,
  }
}
