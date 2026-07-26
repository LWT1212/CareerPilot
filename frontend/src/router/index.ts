// 路由配置 - 前端开发顺序：Step 2

import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
    },
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/Home.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/projects/:id',
      name: 'Project',
      component: () => import('../views/Project.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/projects/:id/chat',
      name: 'Chat',
      component: () => import('../views/Chat.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/projects/:id/knowledge',
      name: 'Knowledge',
      component: () => import('../views/Knowledge.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/projects/:id/experience',
      name: 'Experience',
      component: () => import('../views/Experience.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/projects/:id/interview',
      name: 'Interview',
      component: () => import('../views/Interview.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/projects/:id/documents',
      name: 'Documents',
      component: () => import('../views/Documents.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
