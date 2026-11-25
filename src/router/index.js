/**
 * 路由配置：定义"网址 → 页面"的映射，以及访问权限。
 * V2 从单页面变成四个页面：
 *   /            首页/发现页（看别人的公开故事线）
 *   /login       登录注册
 *   /workspace   我的工作台（V1 的功能搬过来，需要登录）
 *   /detail/:id  别人的故事线只读详情
 */
import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '../api/client.js'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import WorkspaceView from '../views/WorkspaceView.vue'
import DetailView from '../views/DetailView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/login', name: 'login', component: LoginView },
  {
    path: '/workspace',
    name: 'workspace',
    component: WorkspaceView,
    meta: { requiresAuth: true },  // 需要登录才能进
  },
  { path: '/detail/:id', name: 'detail', component: DetailView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

/**
 * 路由守卫：每次跳转前检查。
 * 如果目标页面要求登录、但本地没 token，就拦下来跳到登录页，
 * 并把原本想去的地址记在 query 里，登录完可以跳回去。
 */
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !getToken()) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
