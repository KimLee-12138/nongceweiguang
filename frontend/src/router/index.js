import { createRouter, createWebHistory } from 'vue-router'

import { ensureAdminSession, ensureUserSession } from '../services/authSession'
import { safeInternalRedirectPath } from '../utils/safeRedirect'

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: () => import('../views/HomePage.vue') },
    {
      path: '/onboarding/profile',
      component: () => import('../views/ProfileOnboardingPage.vue'),
      meta: { requiresUser: true, title: '画像问卷', hideLayout: true },
    },
    {
      path: '/chat',
      component: () => import('../views/ChatRouteView.vue'),
      meta: { requiresUser: true, title: '政策对话工作台' },
    },
    { path: '/insights', component: () => import('../views/InsightsPage.vue'), meta: { title: '政策洞察' } },
    { path: '/compass', component: () => import('../views/CompassPage.vue'), meta: { title: '政策风向标' } },
    { path: '/policy-compass', component: () => import('../views/CompassPage.vue'), meta: { title: '政策风向大屏' } },
    { path: '/login', component: () => import('../views/LoginPage.vue'), meta: { title: '用户登录' } },
    { path: '/register', component: () => import('../views/RegisterPage.vue'), meta: { title: '用户注册' } },
    { path: '/sessions', component: () => import('../views/SessionsPage.vue'), meta: { requiresUser: true, title: '会话管理' } },
    {
      path: '/admin/login',
      name: 'AdminLogin',
      component: () => import('../views/admin/AdminLogin.vue'),
      meta: { title: '管理员登录', public: true },
    },
    {
      path: '/admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      meta: { requiresAdmin: true, title: '管理中枢' },
      children: [
        {
          path: '',
          name: 'AdminDashboard',
          component: () => import('../views/admin/AdminDashboard.vue'),
          meta: {
            title: '运营工作台',
            description: '查看政策库概况、近期任务状态与快捷操作入口。',
            section: 'WORKSPACE',
          },
        },
        {
          path: 'policies',
          name: 'AdminPolicies',
          component: () => import('../views/admin/AdminPolicies.vue'),
          meta: {
            title: '政策管理',
            description: '集中维护结构化政策库，处理摘要补全、详情查看与批量操作。',
            section: 'POLICY LIBRARY',
          },
        },
        {
          path: 'policies/review',
          name: 'AdminPolicyReview',
          component: () => import('../views/admin/AdminPolicyReview.vue'),
          meta: {
            title: '规则质量审核',
            description: '统一处理待审核政策，查看 AI 建议、编辑规则草稿并决定是否入库。',
            section: 'POLICY LIBRARY',
          },
        },
        {
          path: 'policies/new',
          name: 'AdminPolicyNew',
          component: () => import('../views/admin/AdminPolicyNew.vue'),
          meta: {
            title: '新增政策',
            description: '录入原文后编译为结构化条件树，写入正式政策库。',
            section: 'POLICY AUTHORING',
          },
        },
        {
          path: 'policies/:id/edit',
          name: 'AdminPolicyEdit',
          component: () => import('../views/admin/AdminPolicyEdit.vue'),
          meta: {
            title: '编辑政策',
            description: '调整结构化政策的标题、来源、摘要和原文引用信息。',
            section: 'POLICY AUTHORING',
          },
        },
        {
          path: 'policies/import',
          name: 'AdminPolicyImport',
          component: () => import('../views/admin/AdminPolicyImport.vue'),
          meta: {
            title: '导入与爬虫',
            description: '执行手动抓取、文件解析和批量送审，补齐原文采集链路。',
            section: 'INGESTION',
          },
        },
        {
          path: 'tasks',
          name: 'AdminTasks',
          component: () => import('../views/admin/AdminTasks.vue'),
          meta: {
            title: '任务中心',
            description: '统一查看管理端后台作业的状态、失败详情和重试入口。',
            section: 'OPERATIONS',
          },
        },
        {
          path: 'policies/auto-crawler',
          name: 'AdminAutoCrawler',
          component: () => import('../views/admin/AdminAutoCrawler.vue'),
          meta: {
            title: '全自动爬虫',
            description: '统一管理自动同步、AI 筛选和审核入队的执行链路。',
            section: 'AUTOMATION',
          },
        },
        {
          path: 'sessions',
          name: 'AdminSessions',
          component: () => import('../views/admin/AdminSessions.vue'),
          meta: {
            title: '会话管理',
            description: '查看与撤销管理员登录会话。',
            section: 'OPERATIONS',
          },
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const deepest = to.matched[to.matched.length - 1]
  const title = deepest?.meta?.title
  if (title) document.title = `${title} | 农策微光`

  const needsUser = to.matched.some((record) => record.meta.requiresUser)
  if (needsUser) {
    const probe = await ensureUserSession()
    if (probe.status === 'anonymous') {
      return { path: '/login', query: { redirect: to.fullPath } }
    }
  }

  const needsAdmin = to.matched.some((record) => record.meta.requiresAdmin)
  if (needsAdmin) {
    const probe = await ensureAdminSession()
    if (probe.status === 'anonymous') {
      return { path: '/admin/login', query: { redirect: to.fullPath } }
    }
  }

  if (to.path === '/login' || to.path === '/register') {
    const probe = await ensureUserSession()
    if (probe.status === 'authenticated') {
      const destination = safeInternalRedirectPath(to.query.redirect, '/chat')
      return { path: destination, replace: true }
    }
  }

  if (to.path === '/admin/login') {
    const probe = await ensureAdminSession()
    if (probe.status === 'authenticated') {
      const destination = safeInternalRedirectPath(to.query.redirect, '/admin')
      return { path: destination, replace: true }
    }
  }
})
