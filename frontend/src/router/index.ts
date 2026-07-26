// 路由配置

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
      name: 'Chat',
      component: () => import('../views/Chat.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/knowledge',
      name: 'Knowledge',
      component: () => import('../views/Knowledge.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/experience',
      name: 'Experience',
      component: () => import('../views/Experience.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/interview',
      name: 'Interview',
      component: () => import('../views/Interview.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/documents',
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
