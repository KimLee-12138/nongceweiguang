# 政策洞察大屏前端UI代码导出

## 导出范围

- 路由入口：`frontend/src/router/index.js`
- 首页入口：`frontend/src/views/HomePage.vue`
- 管理端入口：`frontend/src/views/admin/AdminLayout.vue`
- 政策洞察大屏主页面：`frontend/src/views/Dashboard/BusinessInsightView.vue`
- 全局主题样式：`frontend/src/styles/theme.css`

## 代码目录

- 路由入口：`frontend/src/router/index.js`
- 首页入口：`frontend/src/views/HomePage.vue`
- 管理端入口：`frontend/src/views/admin/AdminLayout.vue`
- 政策洞察大屏主页面：`frontend/src/views/Dashboard/BusinessInsightView.vue`
- 全局主题样式：`frontend/src/styles/theme.css`

## 路由入口

路径：`frontend/src/router/index.js`

```js
import { createRouter, createWebHistory } from 'vue-router'

import { ensureAdminSession, ensureUserSession } from '../services/authSession'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/HomePage.vue'),
      meta: { title: '农策微光' },
    },
    {
      path: '/home',
      redirect: '/',
    },
    {
      path: '/insights',
      name: 'BusinessInsight',
      component: () => import('../views/Dashboard/BusinessInsightView.vue'),
      meta: { title: '辅助洞察大屏' },
    },
    {
      path: '/compass',
      name: 'PolicyCompass',
      component: () => import('../views/Dashboard/PolicyCompassView.vue'),
      meta: { title: '政策风向标' },
    },
    {
      path: '/chat',
      name: 'Chat',
      component: () => import('../views/ChatRouteView.vue'),
      meta: { title: '政策对话工作台', requiresUser: true },
    },
    {
      path: '/login',
      name: 'UserLogin',
      component: () => import('../views/UserLogin.vue'),
      meta: { title: '用户登录', public: true },
    },
    {
      path: '/register',
      name: 'UserRegister',
      component: () => import('../views/UserRegister.vue'),
      meta: { title: '用户注册', public: true },
    },
    {
      path: '/privacy',
      name: 'PrivacyPolicy',
      component: () => import('../views/LegalDocumentPage.vue'),
      meta: { title: '隐私政策', public: true, legalDocument: 'privacy' },
    },
    {
      path: '/terms',
      name: 'TermsOfService',
      component: () => import('../views/LegalDocumentPage.vue'),
      meta: { title: '用户协议', public: true, legalDocument: 'terms' },
    },
    {
      path: '/admin/login',
      name: 'AdminLogin',
      component: () => import('../views/admin/AdminLogin.vue'),
      meta: { title: '管理端登录', public: true },
    },
    {
      path: '/admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      meta: { title: '管理端', requiresAdmin: true },
      children: [
        {
          path: '',
          name: 'AdminDashboard',
          component: () => import('../views/admin/AdminDashboard.vue'),
          meta: {
            title: '运营工作台',
            description: '查看政策库概况、最近自动任务状态和后台快捷入口。',
            section: 'WORKSPACE',
          },
        },
        {
          path: 'policies',
          name: 'AdminPolicies',
          component: () => import('../views/admin/AdminPolicies.vue'),
          meta: {
            title: '政策管理',
            description: '集中维护结构化政策库，处理摘要补全、详情查看和批量删除。',
            section: 'POLICY LIBRARY',
          },
        },
        {
          path: 'policies/review',
          name: 'AdminPolicyReview',
          component: () => import('../views/admin/AdminPolicyReview.vue'),
          meta: {
            title: '规则质量审核台',
            description: '统一处理待审核政策，查看 AI 建议、编辑规则草稿并决定是否入正式政策库。',
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
            description: '统一查看管理端后台作业的状态、失败明细和重试入口。',
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
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const title = to.matched[to.matched.length - 1]?.meta?.title
  if (title) document.title = `${title} | 农业政策智能匹配`

  if (to.meta?.requiresUser) {
    const userProbe = await ensureUserSession()
    if (userProbe.status === 'anonymous') {
      return { path: '/login', query: { redirect: to.fullPath } }
    }
  }

  if (to.meta?.requiresAdmin) {
    const adminProbe = await ensureAdminSession()
    if (adminProbe.status === 'anonymous') {
      return { path: '/admin/login', query: { redirect: to.fullPath } }
    }
  }

  if (to.path === '/login' || to.path === '/register') {
    const userProbe = await ensureUserSession()
    if (userProbe.status === 'authenticated') return { path: '/chat' }
  }

  if (to.path === '/admin/login') {
    const adminProbe = await ensureAdminSession()
    if (adminProbe.status === 'authenticated') return { path: '/admin' }
  }
})

export default router
```

## 首页入口

路径：`frontend/src/views/HomePage.vue`

```vue
<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'
import heroImage from '../assets/hero.png'
import brandLogoMark from '../assets/brand-logo-mark.png'
import {
  ensureAdminSession,
  ensureUserSession,
  hasAdminSession,
  hasUserSession,
  logoutAdminSessionState,
  logoutUserSessionState,
} from '../services/authSession'

const router = useRouter()
const rootRef = ref(null)
const isScrolled = ref(false)
let observer = null

const hasAccessToken = computed(() => hasUserSession.value)
const hasAdminToken = computed(() => hasAdminSession.value)
const chatEntryLabel = computed(() => (hasAccessToken.value ? '进入工作台' : '开始专属匹配'))
const adminEntryPath = computed(() => (hasAdminToken.value ? '/admin' : '/admin/login'))

const featureSections = [
  {
    eyebrow: '精准定帧',
    title: '你的农场，\n你的专属引擎。',
    desc: '一次性挂载经营面积、主体认证与生产条件，让系统以你的真实画像为锚点过滤无关政策，而不是把用户丢进原文海洋里自行对照。',
    variant: 'image',
  },
  {
    eyebrow: '化繁为简',
    title: '八股公文，\n一秒说人话。',
    desc: '把晦涩条款拆成适用对象、核心门槛和申报路径。你看到的不再是公文格式，而是可直接理解的判断结果。',
    variant: 'abstract',
  },
  {
    eyebrow: '谋定后动',
    title: '知道怎么做，\n比知道能报什么更重要。',
    desc: '系统继续输出条件缺口与行动路径，让“能不能报”顺势延伸到“下一步该补什么、先做什么”。',
    variant: 'steps',
  },
]

function go(to = '/chat') {
  router.push(to)
}

async function syncAuthState(options = {}) {
  const { force = false } = options
  await Promise.all([ensureUserSession({ force }), ensureAdminSession({ force })])
}

async function logoutUser() {
  await logoutUserSessionState()
  router.push('/')
}

async function logoutAdmin() {
  await logoutAdminSessionState()
  router.push('/')
}

function initReveal() {
  const root = rootRef.value
  if (!root) return

  const elements = root.querySelectorAll('.cinematic-reveal')
  elements.forEach((el) => {
    el.classList.remove('is-revealed')
  })

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return
        entry.target.classList.add('is-revealed')
        observer?.unobserve(entry.target)
      })
    },
    { threshold: 0.1, rootMargin: '0px 0px -10% 0px' }
  )

  elements.forEach((el) => observer?.observe(el))
}

function handleScroll() {
  isScrolled.value = window.scrollY > 48
}

async function handleWindowFocus() {
  await syncAuthState({ force: true })
}

onMounted(async () => {
  await syncAuthState()
  handleScroll()
  window.addEventListener('focus', handleWindowFocus)
  window.addEventListener('scroll', handleScroll, { passive: true })
  requestAnimationFrame(() => {
    rootRef.value?.classList.add('is-mounted')
    initReveal()
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('focus', handleWindowFocus)
  window.removeEventListener('scroll', handleScroll)
  observer?.disconnect()
  observer = null
})
</script>

<template>
  <div ref="rootRef" class="premium-home">
    <nav class="nav-bar" :class="{ 'nav-scrolled': isScrolled }">
      <div class="nav-container">
        <div class="nav-brand" @click="go('/')">
          <img class="brand-seal" :src="brandLogoMark" alt="AgriPolicy AI" />
          <span class="brand-name">农策微光</span>
        </div>

        <div class="nav-menu">
          <button class="nav-link" @click="go('/insights')">洞察</button>
          <button class="nav-link" @click="go(adminEntryPath)">控制台</button>
          <div class="nav-divider"></div>
          <template v-if="!hasAccessToken">
            <button class="nav-link" @click="go('/login')">登录</button>
            <button class="nav-link" @click="go('/register')">注册</button>
          </template>
          <template v-else>
            <button class="nav-link" @click="logoutUser">退出</button>
          </template>
          <button v-if="hasAdminToken" class="nav-link" @click="logoutAdmin">退出管理端</button>
        </div>
      </div>
    </nav>

    <main>
      <section class="section-hero">
        <div class="hero-bg-glow"></div>
        <div class="hero-content cinematic-reveal delay-1">
          <h1 class="hero-title">
            政策，
            <br />
            不该像天书。
          </h1>
          <p class="hero-subtitle cinematic-reveal delay-2">
            构建专属农户画像，将冗长繁杂的农业公文，
            <br />
            化作极其清晰的下一步行动。
          </p>
          <div class="hero-actions cinematic-reveal delay-3">
            <button class="btn-primary-dark" @click="go('/chat')">{{ chatEntryLabel }}</button>
            <button class="btn-text-dark" @click="go('/insights')">
              探索大盘洞察
              <el-icon><ArrowRight /></el-icon>
            </button>
          </div>
        </div>
      </section>

      <section class="section-manifesto">
        <div class="manifesto-container cinematic-reveal">
          <h2 class="manifesto-text">
            不要去海里捞针。
            <br />
            <span>让对的政策，来找你。</span>
          </h2>
        </div>
      </section>

      <section
        v-for="(feature, index) in featureSections"
        :key="feature.title"
        class="section-feature"
        :class="{
          'feature-right bg-alt': index === 1,
          'feature-left': index !== 1,
        }"
      >
        <div class="feature-container">
          <div class="feature-text cinematic-reveal" :class="{ 'delay-2': index === 1 }">
            <span class="feature-eyebrow">{{ feature.eyebrow }}</span>
            <h2 class="feature-title">{{ feature.title }}</h2>
            <p class="feature-desc">{{ feature.desc }}</p>
          </div>

          <div class="feature-visual cinematic-reveal" :class="{ 'delay-2': index !== 1 }">
            <div v-if="feature.variant === 'image'" class="visual-artbox artbox-1">
              <img :src="heroImage" class="art-image" alt="农业政策匹配引擎视觉" />
              <div class="art-overlay"></div>
            </div>

            <div v-else-if="feature.variant === 'abstract'" class="visual-artbox artbox-2">
              <div class="abstract-card">
                <div class="line line-short"></div>
                <div class="line line-long"></div>
                <div class="line line-medium"></div>
                <div class="highlight-box">适用对象：家庭农场 / 合作社</div>
              </div>
            </div>

            <div v-else class="visual-artbox artbox-3">
              <div class="action-steps">
                <div class="step-item"><span class="step-dot"></span> 补齐高标准农田认证</div>
                <div class="step-item"><span class="step-dot"></span> 准备近三年财务流水</div>
                <div class="step-item active"><span class="step-dot"></span> 发起项目入库申报</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="section-end-cta">
        <div class="cta-container cinematic-reveal">
          <h2 class="cta-title">
            一切就绪。
            <br />
            开始你的专属匹配。
          </h2>
          <div class="cta-actions">
            <button class="btn-primary-dark large" @click="go('/chat')">进入智能工作台</button>
            <button v-if="!hasAccessToken" class="btn-outline-dark large" @click="go('/register')">
              免费创建账号
            </button>
          </div>
        </div>
      </section>
    </main>

    <footer class="premium-footer">
      <div class="footer-container">
        <div class="footer-left">
          <p>© 2026 农策微光 (Agricultural Policy Intelligence). All rights reserved.</p>
        </div>
        <div class="footer-right">
          <RouterLink to="/privacy">隐私政策</RouterLink>
          <RouterLink to="/terms">用户协议</RouterLink>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.premium-home {
  font-family: var(--nc-font-sans);
  background: #fff;
  color: #111;
  overflow-x: hidden;
}

.cinematic-reveal {
  opacity: 0;
  transform: translateY(40px);
  transition:
    opacity 1.2s cubic-bezier(0.16, 1, 0.3, 1),
    transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: opacity, transform;
}

.cinematic-reveal.is-revealed,
.is-mounted .cinematic-reveal.is-revealed {
  opacity: 1;
  transform: translateY(0);
}

.delay-1 { transition-delay: 0.1s; }
.delay-2 { transition-delay: 0.24s; }
.delay-3 { transition-delay: 0.38s; }

.nav-bar {
  position: fixed;
  inset: 0 0 auto;
  height: 60px;
  z-index: 100;
  transition:
    background-color 0.4s ease,
    backdrop-filter 0.4s ease,
    border-color 0.4s ease;
}

.nav-scrolled {
  background: rgba(255, 255, 255, 0.86);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
}

.nav-container {
  width: min(1200px, calc(100% - 48px));
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  cursor: pointer;
}

.brand-seal {
  display: block;
  height: 26px;
  width: auto;
  max-width: 100%;
  object-fit: contain;
}

.brand-name {
  color: #fff;
  font-family: var(--nc-font-serif);
  font-size: 15px;
  font-weight: 600;
  transition: color 0.3s ease;
}

.nav-scrolled .brand-name {
  color: #111;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 24px;
}

.nav-link {
  border: 0;
  background: transparent;
  padding: 0;
  font: inherit;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: color 0.3s ease, opacity 0.3s ease;
}

.nav-scrolled .nav-link {
  color: rgba(17, 17, 17, 0.64);
}

.nav-link:hover {
  color: #fff;
}

.nav-scrolled .nav-link:hover {
  color: #111;
}

.nav-divider {
  width: 1px;
  height: 12px;
  background: rgba(255, 255, 255, 0.2);
}

.nav-scrolled .nav-divider {
  background: rgba(0, 0, 0, 0.1);
}

.section-hero {
  position: relative;
  min-height: 100vh;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  background:
    radial-gradient(circle at 50% 42%, rgba(29, 91, 61, 0.22), transparent 28%),
    linear-gradient(180deg, #050b08 0%, #06110c 100%);
  overflow: hidden;
}

.hero-bg-glow {
  position: absolute;
  top: 40%;
  left: 50%;
  width: 60vw;
  height: 60vw;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(29, 91, 61, 0.22) 0%, rgba(0, 0, 0, 0) 70%);
  filter: blur(60px);
  pointer-events: none;
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 900px;
}

.hero-title {
  margin: 0 0 32px;
  color: #fbfbfd;
  font-family: var(--nc-font-serif);
  font-size: clamp(3.5rem, 8vw, 7rem);
  font-weight: 700;
  line-height: 1.05;
  letter-spacing: -0.04em;
}

.hero-subtitle {
  margin: 0 auto 48px;
  max-width: 680px;
  color: #86868b;
  font-size: clamp(1.15rem, 2vw, 1.6rem);
  font-weight: 400;
  line-height: 1.6;
  letter-spacing: 0.01em;
}

.hero-actions,
.cta-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
}

.btn-primary-dark,
.btn-text-dark,
.btn-outline-dark {
  appearance: none;
  font: inherit;
  cursor: pointer;
  border: 0;
  background: transparent;
  transition:
    transform 0.3s cubic-bezier(0.16, 1, 0.3, 1),
    opacity 0.3s ease,
    background 0.3s ease,
    border-color 0.3s ease;
}

.btn-primary-dark {
  height: 52px;
  padding: 0 28px;
  border-radius: 999px;
  background: #f5f5f7;
  color: #111;
  font-size: 16px;
  font-weight: 600;
}

.btn-primary-dark:hover {
  background: #fff;
  transform: scale(1.03);
}

.btn-text-dark {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #f5f5f7;
  font-size: 16px;
  font-weight: 500;
}

.btn-text-dark:hover {
  opacity: 0.74;
}

.btn-text-dark :deep(.el-icon) {
  font-size: 14px;
  transition: transform 0.3s ease;
}

.btn-text-dark:hover :deep(.el-icon) {
  transform: translateX(4px);
}

.btn-outline-dark {
  height: 52px;
  padding: 0 28px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 999px;
  color: #f5f5f7;
  font-size: 16px;
  font-weight: 500;
}

.btn-outline-dark:hover {
  border-color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.section-manifesto {
  padding: 160px 24px;
  text-align: center;
  background: #fff;
}

.manifesto-container {
  max-width: 1000px;
  margin: 0 auto;
}

.manifesto-text {
  margin: 0;
  color: #111;
  font-family: var(--nc-font-serif);
  font-size: clamp(2.5rem, 5vw, 4.5rem);
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.03em;
}

.manifesto-text span {
  color: #86868b;
}

.section-feature {
  padding: 140px 24px;
  background: #fff;
}

.section-feature.bg-alt {
  background: #fbfbfd;
}

.feature-container {
  width: min(1200px, 100%);
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: min(10vw, 96px);
}

.feature-right .feature-container {
  flex-direction: row-reverse;
}

.feature-text {
  flex: 1;
  max-width: 500px;
  white-space: pre-line;
}

.feature-eyebrow {
  display: block;
  margin-bottom: 16px;
  color: #728a7c;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.1em;
}

.feature-title {
  margin: 0 0 24px;
  color: #111;
  font-family: var(--nc-font-serif);
  font-size: clamp(2.5rem, 4vw, 3.5rem);
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.03em;
}

.feature-desc {
  margin: 0;
  color: #86868b;
  font-size: 1.2rem;
  line-height: 1.65;
}

.feature-visual {
  flex: 1.2;
  display: flex;
  justify-content: center;
}

.visual-artbox {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 32px;
  background: #f5f5f7;
}

.artbox-1 {
  background: linear-gradient(180deg, #eef1ec 0%, #dfe6df 100%);
}

.art-image {
  position: relative;
  z-index: 1;
  width: 80%;
  height: auto;
  object-fit: cover;
  filter: contrast(1.1) brightness(0.95) saturate(0.8);
  transform: translateY(20px);
}

.art-overlay {
  position: absolute;
  inset: auto 0 0;
  height: 44%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0), rgba(10, 20, 15, 0.08));
}

.abstract-card {
  width: 60%;
  padding: 40px 32px;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.04);
}

.line {
  height: 8px;
  margin-bottom: 16px;
  border-radius: 4px;
  background: #e8e8ed;
}

.line-short { width: 40%; }
.line-long { width: 100%; }
.line-medium {
  width: 70%;
  margin-bottom: 32px;
}

.highlight-box {
  padding: 12px 16px;
  border-radius: 8px;
  background: rgba(29, 91, 61, 0.08);
  color: #1d5b3d;
  font-size: 14px;
  font-weight: 600;
}

.action-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 70%;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
  color: #86868b;
  font-size: 16px;
  font-weight: 500;
  transition: transform 0.3s ease, box-shadow 0.3s ease, color 0.3s ease;
}

.step-item.active {
  color: #111;
  transform: scale(1.05);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.06);
}

.step-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #e8e8ed;
}

.step-item.active .step-dot {
  background: #1d5b3d;
  box-shadow: 0 0 0 4px rgba(29, 91, 61, 0.15);
}

.section-end-cta {
  padding: 160px 24px;
  text-align: center;
  background: linear-gradient(180deg, #050b08 0%, #08110d 100%);
}

.cta-container {
  max-width: 800px;
  margin: 0 auto;
}

.cta-title {
  margin: 0 0 48px;
  color: #fbfbfd;
  font-family: var(--nc-font-serif);
  font-size: clamp(3rem, 6vw, 4.5rem);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.btn-primary-dark.large,
.btn-outline-dark.large {
  height: 56px;
  padding: 0 36px;
  font-size: 18px;
}

.premium-footer {
  padding: 32px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: #050b08;
}

.footer-container {
  width: min(1200px, 100%);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.footer-left p {
  margin: 0;
  color: rgba(255, 255, 255, 0.42);
  font-size: 12px;
}

.footer-right {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.footer-right a {
  color: rgba(255, 255, 255, 0.62);
  font-size: 12px;
  transition: color 0.2s ease;
}

.footer-right a:hover {
  color: #fff;
}

@media (max-width: 900px) {
  .feature-container,
  .feature-right .feature-container {
    flex-direction: column;
    gap: 40px;
  }

  .feature-text {
    max-width: 100%;
    text-align: center;
  }

  .feature-visual {
    width: 100%;
  }
}

@media (max-width: 760px) {
  .nav-container {
    width: min(100%, calc(100% - 28px));
  }

  .nav-menu {
    gap: 14px;
    flex-wrap: wrap;
    justify-content: flex-end;
  }

  .nav-divider {
    display: none;
  }

  .nav-link {
    font-size: 12px;
  }

  .section-hero {
    min-height: 90svh;
  }

  .hero-title {
    font-size: clamp(3rem, 13vw, 4.5rem);
  }

  .hero-actions,
  .cta-actions {
    flex-direction: column;
    width: 100%;
  }

  .btn-primary-dark,
  .btn-outline-dark {
    width: 100%;
  }

  .abstract-card,
  .action-steps {
    width: 82%;
  }
}

@media (max-width: 560px) {
  .nav-menu .nav-link:nth-child(1),
  .nav-menu .nav-link:nth-child(2) {
    display: none;
  }

  .section-manifesto,
  .section-feature,
  .section-end-cta {
    padding: 112px 20px;
  }

  .feature-title {
    font-size: 2.2rem;
  }

  .feature-desc {
    font-size: 1.06rem;
  }

  .abstract-card,
  .action-steps {
    width: 100%;
  }

  .footer-container {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
```

## 管理端入口

路径：`frontend/src/views/admin/AdminLayout.vue`

```vue
<template>
  <div v-if="sessionReady && isAuthenticated" class="admin-layout">
    <aside class="admin-sidebar">
      <div class="sidebar-brand">
        <img class="brand-mark" :src="brandLogoMark" alt="AgriPolicy AI" />
        <div>
          <p class="brand-kicker">ADMIN CONSOLE</p>
          <h1 class="brand-title">农策微光</h1>
        </div>
      </div>

      <nav class="sidebar-nav">
        <button
          v-for="item in navItems"
          :key="item.key"
          type="button"
          class="nav-item"
          :class="{ active: isItemActive(item) }"
          @click="handleNavigate(item.to)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <div class="user-card">
          <span class="user-meta">当前账号</span>
          <strong>{{ adminUsername || '管理员' }}</strong>
        </div>
        <el-button type="danger" plain class="logout-btn" @click="handleLogout">退出登录</el-button>
      </div>
    </aside>

    <el-drawer
      v-model="drawerVisible"
      direction="ltr"
      size="288px"
      class="admin-drawer"
      :show-close="false"
    >
      <template #header>
        <div class="drawer-head">
          <img class="brand-mark" :src="brandLogoMark" alt="AgriPolicy AI" />
          <div>
            <p class="brand-kicker">ADMIN CONSOLE</p>
            <strong class="drawer-title">农策微光</strong>
          </div>
        </div>
      </template>

      <div class="drawer-nav">
        <button
          v-for="item in navItems"
          :key="`${item.key}-drawer`"
          type="button"
          class="nav-item"
          :class="{ active: isItemActive(item) }"
          @click="handleDrawerNavigate(item.to)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </button>
      </div>

      <div class="drawer-footer">
        <div class="user-card">
          <span class="user-meta">当前账号</span>
          <strong>{{ adminUsername || '管理员' }}</strong>
        </div>
        <el-button type="danger" plain class="logout-btn" @click="handleLogout">退出登录</el-button>
      </div>
    </el-drawer>

    <div class="admin-stage">
      <header class="stage-header">
        <div class="stage-heading">
          <button type="button" class="menu-toggle" @click="drawerVisible = true">
            <el-icon><Menu /></el-icon>
          </button>
          <div class="heading-copy">
            <p class="heading-kicker">{{ currentSection }}</p>
            <h2 class="heading-title">{{ currentTitle }}</h2>
            <p class="heading-desc">{{ currentDescription }}</p>
          </div>
        </div>

        <div class="stage-actions">
          <el-button plain @click="router.push('/')">返回首页</el-button>
          <el-button plain @click="router.push('/insights')">政策洞察</el-button>
          <el-button type="primary" @click="router.push('/chat')">进入聊天</el-button>
        </div>
      </header>

      <main class="stage-main">
        <router-view />
      </main>
    </div>
  </div>
  <div v-else-if="sessionReady" class="admin-access">
    <div class="admin-access__panel">
      <div class="admin-access__copy">
        <p class="admin-access__eyebrow">ADMIN ACCESS</p>
        <h1>{{ accessTitle }}</h1>
        <p class="admin-access__text">{{ accessDescription }}</p>
      </div>

      <div class="admin-access__actions">
        <el-button type="primary" size="large" :loading="retryingSession" @click="retrySessionRecovery">重试恢复</el-button>
        <el-button size="large" @click="router.push(isForbidden ? '/login' : '/admin/login')">
          {{ isForbidden ? '切换到用户端入口' : '前往管理端登录' }}
        </el-button>
        <el-button plain size="large" @click="router.push('/')">返回首页</el-button>
      </div>
    </div>
  </div>
  <div v-else class="admin-access admin-access--loading">
    <div class="admin-access__loading">正在恢复管理端会话...</div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Cpu,
  Document,
  EditPen,
  Files,
  FolderOpened,
  Histogram,
  Menu,
  Opportunity,
} from '@element-plus/icons-vue'
import brandLogoMark from '../../assets/brand-logo-mark.png'
import {
  adminSessionError,
  adminSessionStatus,
  ensureAdminSession,
  logoutAdminSessionState,
} from '../../services/authSession'

const router = useRouter()
const route = useRoute()
const drawerVisible = ref(false)
const adminUsername = ref('')
const sessionReady = ref(false)
const retryingSession = ref(false)

const navItems = [
  { key: 'dashboard', label: '工作台', to: '/admin', icon: Histogram, names: ['AdminDashboard'] },
  { key: 'policies', label: '政策管理', to: '/admin/policies', icon: Document, names: ['AdminPolicies', 'AdminPolicyEdit'] },
  { key: 'review', label: '规则审核', to: '/admin/policies/review', icon: Opportunity, names: ['AdminPolicyReview'] },
  { key: 'new', label: '新增政策', to: '/admin/policies/new', icon: EditPen, names: ['AdminPolicyNew'] },
  { key: 'import', label: '导入与爬虫', to: '/admin/policies/import', icon: FolderOpened, names: ['AdminPolicyImport'] },
  { key: 'tasks', label: '任务中心', to: '/admin/tasks', icon: Files, names: ['AdminTasks'] },
  { key: 'crawler', label: '全自动爬虫', to: '/admin/policies/auto-crawler', icon: Cpu, names: ['AdminAutoCrawler'] },
]

const currentTitle = computed(() => route.meta?.title || '管理端')
const currentDescription = computed(
  () => route.meta?.description || '统一管理政策库、原文导入、后台作业和自动任务。',
)
const currentSection = computed(() => route.meta?.section || 'ADMIN')
const isAuthenticated = computed(() => adminSessionStatus.value === 'authenticated')
const isForbidden = computed(() => adminSessionStatus.value === 'forbidden')
const accessTitle = computed(() => (isForbidden.value ? '当前账号无权访问管理端' : '管理端会话恢复失败'))
const accessDescription = computed(() =>
  isForbidden.value
    ? '当前账号缺少进入管理端的权限。你可以切换到普通用户入口，或重新登录其他管理员账号后再试。'
    : adminSessionError.value?.message || '网络异常或服务暂时不可用，当前不会自动把你当作已退出。请稍后重试。'
)

function isItemActive(item) {
  return item.names.includes(route.name)
}

function handleNavigate(path) {
  if (route.path !== path) router.push(path)
}

function handleDrawerNavigate(path) {
  drawerVisible.value = false
  if (route.path !== path) router.push(path)
}

onMounted(async () => {
  const result = await ensureAdminSession({ force: true })
  if (result.status === 'authenticated' && result.principal) {
    adminUsername.value = result.principal.username
  }
  sessionReady.value = true
})

async function retrySessionRecovery() {
  retryingSession.value = true
  try {
    const result = await ensureAdminSession({ force: true })
    if (result.status === 'authenticated' && result.principal) {
      adminUsername.value = result.principal.username
    }
    sessionReady.value = true
  } finally {
    retryingSession.value = false
  }
}

async function handleLogout() {
  await logoutAdminSessionState()
  router.replace('/admin/login')
}
</script>

<style scoped>
.admin-layout {
  --adm-sidebar-bg: #112f21;
  --adm-sidebar-bg-strong: #0c2318;
  --adm-sidebar-border: rgba(255, 255, 255, 0.08);
  --adm-sidebar-text: rgba(245, 243, 234, 0.72);
  --adm-sidebar-text-strong: #f6f2e8;
  --adm-sidebar-active: rgba(185, 150, 82, 0.18);
  --adm-stage-bg: linear-gradient(180deg, #edf2eb 0%, #e7ece5 100%);
  --adm-panel-bg: rgba(255, 253, 248, 0.94);
  --adm-panel-border: rgba(25, 69, 48, 0.1);
  --adm-muted: #70806f;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 264px minmax(0, 1fr);
  background: var(--adm-stage-bg);
}

.admin-sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 1.4rem 1rem 1rem;
  background:
    radial-gradient(circle at top, rgba(185, 150, 82, 0.16), transparent 28%),
    linear-gradient(180deg, var(--adm-sidebar-bg), var(--adm-sidebar-bg-strong));
  border-right: 1px solid var(--adm-sidebar-border);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 0.4rem 0.4rem 1.2rem;
}

.brand-mark {
  display: block;
  width: 38px;
  height: 38px;
  flex: 0 0 auto;
  object-fit: contain;
}

.brand-kicker {
  margin: 0;
  font-size: 0.7rem;
  letter-spacing: 0.2em;
  color: rgba(246, 242, 232, 0.54);
}

.brand-title,
.drawer-title {
  margin: 0.2rem 0 0;
  color: var(--adm-sidebar-text-strong);
  font-size: 1.08rem;
}

.sidebar-nav,
.drawer-nav {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.nav-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.86rem 0.9rem;
  border: 0;
  border-radius: 16px;
  background: transparent;
  color: var(--adm-sidebar-text);
  font: inherit;
  cursor: pointer;
  text-align: left;
  transition: background 160ms ease, transform 160ms ease, color 160ms ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--adm-sidebar-text-strong);
}

.nav-item.active {
  background: linear-gradient(135deg, var(--adm-sidebar-active), rgba(255, 255, 255, 0.06));
  color: var(--adm-sidebar-text-strong);
  box-shadow: inset 0 0 0 1px rgba(214, 183, 119, 0.18);
}

.nav-item :deep(.el-icon) {
  font-size: 1rem;
}

.sidebar-footer,
.drawer-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-card {
  padding: 0.95rem 1rem;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--adm-sidebar-text-strong);
}

.user-meta {
  display: block;
  margin-bottom: 0.35rem;
  font-size: 0.76rem;
  color: rgba(246, 242, 232, 0.6);
}

.logout-btn {
  width: 100%;
}

.admin-stage {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.stage-header {
  position: sticky;
  top: 0;
  z-index: 5;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.2rem 1.6rem 1rem;
  background: rgba(237, 242, 235, 0.9);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(25, 69, 48, 0.08);
}

.stage-heading {
  display: flex;
  align-items: flex-start;
  gap: 0.9rem;
  min-width: 0;
}

.menu-toggle {
  display: none;
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 14px;
  background: rgba(29, 91, 61, 0.08);
  color: #173726;
  cursor: pointer;
}

.heading-copy {
  min-width: 0;
}

.heading-kicker {
  margin: 0;
  font-size: 0.75rem;
  letter-spacing: 0.16em;
  color: #74836d;
}

.heading-title {
  margin: 0.3rem 0 0;
  font-size: 1.65rem;
  line-height: 1.15;
  color: #143423;
}

.heading-desc {
  margin: 0.45rem 0 0;
  max-width: 720px;
  color: var(--adm-muted);
  line-height: 1.7;
}

.stage-actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.stage-main {
  flex: 1;
  padding: 1.4rem 1.6rem 1.8rem;
  overflow: auto;
}

.drawer-head {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

:deep(.admin-drawer .el-drawer__header) {
  margin-bottom: 0;
  padding-bottom: 0;
}

:deep(.admin-drawer .el-drawer__body) {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 1rem;
}

:deep(.page-shell) {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

:deep(.page-head) {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

:deep(.page-title-group) {
  min-width: 0;
}

:deep(.page-title) {
  margin: 0;
  font-size: 1.28rem;
  line-height: 1.2;
  color: #173726;
}

:deep(.page-subtitle) {
  margin: 0.45rem 0 0;
  color: var(--adm-muted);
  line-height: 1.7;
}

:deep(.page-actions) {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

:deep(.page-grid) {
  display: grid;
  gap: 1rem;
}

:deep(.page-grid.two-column) {
  grid-template-columns: minmax(0, 1.3fr) minmax(280px, 0.9fr);
}

:deep(.page-panel) {
  padding: 1.2rem 1.25rem;
  border-radius: 26px;
  border: 1px solid var(--adm-panel-border);
  background: var(--adm-panel-bg);
  box-shadow: 0 18px 50px rgba(41, 55, 43, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

:deep(.panel-title) {
  margin: 0;
  font-size: 1rem;
  color: #173726;
}

:deep(.panel-subtitle) {
  margin: 0.3rem 0 0;
  color: var(--adm-muted);
  line-height: 1.65;
}

:deep(.stat-grid) {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.85rem;
}

:deep(.stat-card) {
  padding: 1rem 1.05rem;
  border-radius: 20px;
  border: 1px solid rgba(21, 63, 44, 0.09);
  background: rgba(255, 255, 255, 0.88);
}

:deep(.stat-label) {
  display: block;
  font-size: 0.78rem;
  color: #7a8778;
}

:deep(.stat-value) {
  display: block;
  margin-top: 0.35rem;
  font-size: 1.55rem;
  font-weight: 700;
  color: #173726;
}

:deep(.admin-note) {
  margin: 0;
  color: var(--adm-muted);
  line-height: 1.7;
}

:deep(.soft-list) {
  margin: 0;
  padding-left: 1.15rem;
  color: var(--adm-muted);
  line-height: 1.8;
}

:deep(.surface-table) {
  border-radius: 20px;
  overflow: hidden;
}

:deep(.surface-pagination) {
  margin-top: 1rem;
}

:deep(.admin-layout .el-card) {
  border-radius: 22px;
  border: 1px solid var(--adm-panel-border);
  box-shadow: none;
  background: rgba(255, 253, 248, 0.94);
}

:deep(.admin-layout .el-table) {
  --el-table-border-color: rgba(20, 52, 35, 0.08);
  --el-table-header-bg-color: rgba(18, 58, 40, 0.05);
  --el-table-row-hover-bg-color: rgba(26, 95, 58, 0.05);
  border-radius: 18px;
}

:deep(.admin-layout .el-table th.el-table__cell) {
  color: #56705e;
  font-weight: 600;
}

:deep(.admin-layout .el-dialog),
:deep(.admin-layout .el-message-box) {
  border-radius: 24px;
}

:deep(.admin-layout .el-form-item__label) {
  color: #566754;
  font-weight: 600;
}

:deep(.admin-layout .el-tabs__item.is-active),
:deep(.admin-layout .el-tabs__item:hover) {
  color: #1a5f3a;
}

:deep(.admin-layout .el-tabs__active-bar) {
  background-color: #1a5f3a;
}

.admin-access {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1.25rem;
  background:
    radial-gradient(circle at top, rgba(185, 150, 82, 0.18), transparent 26%),
    linear-gradient(180deg, #edf2eb 0%, #e6ece4 100%);
}

.admin-access--loading {
  background: linear-gradient(180deg, #edf2eb 0%, #e7ece5 100%);
}

.admin-access__panel {
  width: min(720px, 100%);
  padding: 1.25rem;
  border-radius: 28px;
  border: 1px solid rgba(25, 69, 48, 0.1);
  background: rgba(255, 253, 248, 0.84);
  box-shadow: var(--nc-shadow-lg);
}

.admin-access__copy {
  padding: 2rem;
  border-radius: 22px;
  background:
    radial-gradient(circle at top right, rgba(185, 150, 82, 0.12), transparent 28%),
    linear-gradient(145deg, rgba(11, 33, 24, 0.96), rgba(29, 91, 61, 0.84));
  color: #f6f2e8;
}

.admin-access__eyebrow {
  margin: 0;
  font-size: 0.74rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(246, 242, 232, 0.68);
}

.admin-access__copy h1 {
  margin: 1rem 0 0;
  font-family: var(--nc-font-serif);
  font-size: clamp(2rem, 4vw, 3.1rem);
  line-height: 1.05;
}

.admin-access__text {
  margin: 1rem 0 0;
  font-size: 1rem;
  line-height: 1.8;
  color: rgba(246, 242, 232, 0.78);
}

.admin-access__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  padding: 1.3rem 0.5rem 0;
}

.admin-access__loading {
  padding: 1rem 1.25rem;
  border-radius: 999px;
  background: rgba(255, 253, 247, 0.86);
  border: 1px solid rgba(18, 39, 27, 0.08);
  color: var(--nc-text-secondary);
  box-shadow: var(--nc-shadow-lg);
}

@media (max-width: 1180px) {
  .admin-layout {
    grid-template-columns: 1fr;
  }

  .admin-sidebar {
    display: none;
  }

  .menu-toggle {
    display: grid;
    place-items: center;
  }
}

@media (max-width: 900px) {
  .stage-header,
  .stage-main {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  :deep(.page-grid.two-column),
  :deep(.stat-grid) {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stage-header {
    flex-direction: column;
  }

  .admin-access__copy {
    padding: 1.4rem 1.2rem;
  }

  .stage-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .heading-title {
    font-size: 1.35rem;
  }
}
</style>
```

## 政策洞察大屏主页面

路径：`frontend/src/views/Dashboard/BusinessInsightView.vue`

```vue
<template>
  <div ref="screenRef" class="insight-screen" :class="{ 'is-ready': isReady }">
    <div class="screen-orb screen-orb--one" />
    <div class="screen-orb screen-orb--two" />
    <div class="screen-grid" />

    <header class="topbar reveal-section">
      <div class="brand-block">
        <div class="eyebrow">REAL POLICY INTELLIGENCE</div>
        <div class="title-row">
          <h1>湖北农业政策真实洞察大屏</h1>
          <span class="freshness">{{ freshnessLabel }}</span>
        </div>
        <p>
          基于真实 <code>hubei_policies_raw</code> 与 <code>policies</code>
          数据聚合，直接观察政策发布趋势、发布机构分布与适用主体覆盖情况。
        </p>
      </div>

      <div class="top-actions">
        <button class="ghost-btn" @click="navigate('/')">返回首页</button>
        <button class="primary-btn" @click="navigate('/chat')">进入智能匹配</button>
      </div>
    </header>

    <section class="hero-strip reveal-section">
      <article v-for="card in kpiCards" :key="card.label" class="metric-tile">
        <div class="metric-label">{{ card.label }}</div>
        <div class="metric-value">{{ card.value }}</div>
        <div class="metric-hint">{{ card.hint }}</div>
      </article>
    </section>

    <section class="main-stage reveal-section">
      <div class="panel-shell trend-panel">
        <div class="panel-head">
          <div>
            <div class="panel-kicker">TREND</div>
            <h2>政策发布时间趋势</h2>
            <p>按{{ trendGranularityLabel }}聚合真实政策发布时间，观察近阶段政策供给节奏。</p>
          </div>
          <button class="panel-link" @click="navigate('/chat')">去对话追问</button>
        </div>
        <div ref="trendChartEl" class="chart chart--hero" />
      </div>

      <div class="side-stack">
        <div class="panel-shell side-panel">
          <div class="panel-head">
            <div>
              <div class="panel-kicker">SOURCE</div>
              <h2>发布机构分布</h2>
              <p>按发布机构或回退来源聚合，展示当前政策供给的主要来源。</p>
            </div>
          </div>
          <div ref="sourceChartEl" class="chart chart--side" />
        </div>

        <div class="panel-shell side-panel">
          <div class="panel-head">
            <div>
              <div class="panel-kicker">SUBJECT</div>
              <h2>适用主体分布</h2>
              <p>从结构化条件树提取主体标签，观察政策主要面向哪些经营主体。</p>
            </div>
          </div>
          <div ref="subjectChartEl" class="chart chart--side" />
        </div>
      </div>
    </section>

    <section class="intel-strip reveal-section">
      <div class="intel-module">
        <div class="intel-kicker">热点栏目</div>
        <div class="intel-list">
          <div v-for="item in topColumns" :key="item.name" class="intel-row">
            <span>{{ item.name }}</span>
            <strong>{{ item.value }}</strong>
          </div>
          <div v-if="!topColumns.length" class="intel-empty">暂无栏目统计</div>
        </div>
      </div>

      <div class="intel-module">
        <div class="intel-kicker">主要主题</div>
        <div class="intel-list">
          <div v-for="item in topTopics" :key="item.name" class="intel-row">
            <span>{{ item.name }}</span>
            <strong>{{ item.value }}</strong>
          </div>
          <div v-if="!topTopics.length" class="intel-empty">暂无主题统计</div>
        </div>
      </div>

      <div class="intel-module">
        <div class="intel-kicker">解读提示</div>
        <div class="insight-copy">
          <p>{{ insightNotes[0] }}</p>
          <p>{{ insightNotes[1] }}</p>
          <p>{{ insightNotes[2] }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import client from '../../api/client'

const router = useRouter()
const screenRef = ref(null)
const trendChartEl = ref(null)
const sourceChartEl = ref(null)
const subjectChartEl = ref(null)

const isReady = ref(false)

const dashboard = reactive({
  kpi: null,
  trend: { granularity: 'month', points: [] },
  source: { items: [], total: 0 },
  audience: { items: [], total: 0, covered_policy_count: 0 },
})

let trendChart = null
let sourceChart = null
let subjectChart = null
let revealObserver = null

const topColumns = computed(() => dashboard.kpi?.top_columns || [])
const topTopics = computed(() => dashboard.kpi?.top_topics || [])

const trendGranularityLabel = computed(() =>
  dashboard.trend?.granularity === 'quarter' ? '季度' : '月份',
)

const freshnessLabel = computed(() => {
  const latest = dashboard.kpi?.latest_publish_date
  if (!latest) return '等待数据'
  return `最近更新 ${latest}`
})

const kpiCards = computed(() => [
  {
    label: '累计原始政策',
    value: formatNumber(dashboard.kpi?.total_raw_policies),
    hint: '原始政策库已收录的政策正文总量',
  },
  {
    label: '近 12 个月新增',
    value: formatNumber(dashboard.kpi?.recent_12_month_policies),
    hint: '用真实发布日期计算近一年政策活跃度',
  },
  {
    label: '已结构化政策',
    value: formatNumber(dashboard.kpi?.structured_policy_count),
    hint: '已完成规则化编译、可用于画像匹配的政策数',
  },
  {
    label: '覆盖主体类别',
    value: formatNumber(dashboard.kpi?.subject_category_count),
    hint: '条件树中可识别出的适用主体类别总数',
  },
])

const insightNotes = computed(() => {
  const structured = Number(dashboard.kpi?.structured_policy_count || 0)
  const total = Number(dashboard.kpi?.total_raw_policies || 0)
  const covered = Number(dashboard.kpi?.subject_coverage_policy_count || 0)
  const ratio = total > 0 ? `${Math.round((structured / total) * 100)}%` : '0%'

  return [
    `规则化覆盖率目前约为 ${ratio}，大屏可以直接揭示“原始政策库”和“可匹配政策库”的真实差距。`,
    `已有 ${covered} 条结构化政策被识别出明确适用主体，可继续作为画像匹配与申报辅导的重点样本。`,
    '点击趋势点、发布机构或主体类型后，会直接跳入聊天页，转成具体政策问答与白话解读。',
  ]
})

function formatNumber(value) {
  return Number(value || 0).toLocaleString('zh-CN')
}

function navigate(path) {
  router.push(path)
}

function pushFilter(filterType, filterValue) {
  if (!filterValue) return
  router.push({
    path: '/chat',
    query: {
      filter_type: filterType,
      filter_value: String(filterValue),
    },
  })
}

function getEmptyGraphic(text) {
  return {
    type: 'text',
    left: 'center',
    top: 'middle',
    style: {
      text,
      fill: 'rgba(243, 239, 226, 0.78)',
      fontSize: 14,
      fontFamily: 'var(--nc-font-sans)',
    },
  }
}

function initTrendChart() {
  if (!trendChartEl.value) return
  if (!trendChart) trendChart = echarts.init(trendChartEl.value)

  const points = dashboard.trend?.points || []
  const labels = points.map((item) => item.label)
  const values = points.map((item) => Number(item.policy_count || 0))

  trendChart.setOption(
    {
      backgroundColor: 'transparent',
      animationDuration: 800,
      grid: { left: 18, right: 18, top: 42, bottom: 20, containLabel: true },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(14, 34, 23, 0.96)',
        borderColor: 'rgba(185, 150, 82, 0.22)',
        textStyle: { color: '#f7f3e7' },
      },
      xAxis: {
        type: 'category',
        data: labels,
        boundaryGap: false,
        axisLine: { lineStyle: { color: 'rgba(212, 224, 205, 0.18)' } },
        axisLabel: { color: 'rgba(237, 239, 228, 0.78)' },
      },
      yAxis: {
        type: 'value',
        minInterval: 1,
        axisLabel: { color: 'rgba(237, 239, 228, 0.78)' },
        splitLine: { lineStyle: { color: 'rgba(212, 224, 205, 0.1)' } },
      },
      series: [
        {
          name: '政策数量',
          type: 'line',
          smooth: true,
          data: values,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: {
            width: 3,
            color: '#89a97d',
            shadowBlur: 16,
            shadowColor: 'rgba(137, 169, 125, 0.34)',
          },
          itemStyle: {
            color: '#d7be8a',
            borderWidth: 2,
            borderColor: '#183122',
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(137, 169, 125, 0.34)' },
                { offset: 1, color: 'rgba(137, 169, 125, 0.02)' },
              ],
            },
          },
        },
      ],
      graphic: points.length ? [] : [getEmptyGraphic('暂无可用发布时间数据')],
    },
    true,
  )

  trendChart.off('click')
  trendChart.on('click', (params) => {
    const point = points?.[params?.dataIndex ?? -1]
    if (point?.period) pushFilter('trend_period', point.period)
  })
}

function initSourceChart() {
  if (!sourceChartEl.value) return
  if (!sourceChart) sourceChart = echarts.init(sourceChartEl.value)

  const items = dashboard.source?.items || []
  const labels = items.map((item) => item.name).reverse()
  const values = items.map((item) => Number(item.value || 0)).reverse()

  sourceChart.setOption(
    {
      backgroundColor: 'transparent',
      animationDuration: 800,
      grid: { left: 18, right: 18, top: 20, bottom: 12, containLabel: true },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: 'rgba(14, 34, 23, 0.96)',
        borderColor: 'rgba(185, 150, 82, 0.24)',
        textStyle: { color: '#f8f2df' },
      },
      xAxis: {
        type: 'value',
        minInterval: 1,
        axisLabel: { color: 'rgba(241, 235, 220, 0.72)' },
        splitLine: { lineStyle: { color: 'rgba(185, 150, 82, 0.12)' } },
      },
      yAxis: {
        type: 'category',
        data: labels,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: 'rgba(241, 235, 220, 0.82)', width: 100, overflow: 'truncate' },
      },
      series: [
        {
          name: '政策数量',
          type: 'bar',
          data: values,
          barWidth: 16,
          itemStyle: {
            borderRadius: [10, 10, 10, 10],
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [
                { offset: 0, color: '#b99652' },
                { offset: 1, color: '#e1cf9d' },
              ],
            },
            shadowBlur: 18,
            shadowColor: 'rgba(185, 150, 82, 0.24)',
          },
        },
      ],
      graphic: items.length ? [] : [getEmptyGraphic('暂无可用来源数据')],
    },
    true,
  )

  sourceChart.off('click')
  sourceChart.on('click', (params) => {
    const name = params?.name
    if (name) pushFilter('issuer', name)
  })
}

function initSubjectChart() {
  if (!subjectChartEl.value) return
  if (!subjectChart) subjectChart = echarts.init(subjectChartEl.value)

  const items = dashboard.audience?.items || []
  const total = Number(dashboard.audience?.total || 0)

  subjectChart.setOption(
    {
      backgroundColor: 'transparent',
      animationDuration: 800,
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(14, 34, 23, 0.96)',
        borderColor: 'rgba(137, 169, 125, 0.24)',
        textStyle: { color: '#f2f7ee' },
      },
      legend: {
        bottom: 0,
        icon: 'circle',
        textStyle: { color: 'rgba(239, 239, 228, 0.74)' },
      },
      series: [
        {
          name: '适用主体',
          type: 'pie',
          radius: ['54%', '76%'],
          center: ['50%', '44%'],
          avoidLabelOverlap: true,
          label: {
            color: 'rgba(247, 243, 231, 0.88)',
            formatter: ({ name, percent }) => `${name}\n${percent}%`,
          },
          labelLine: {
            lineStyle: { color: 'rgba(209, 219, 189, 0.28)' },
          },
          itemStyle: {
            borderColor: 'rgba(8, 25, 17, 0.9)',
            borderWidth: 4,
          },
          data: items.map((item, index) => ({
            ...item,
            itemStyle: {
              color: ['#89a97d', '#b99652', '#d4c497', '#6f8a63', '#4c6a53', '#c7b26d'][index % 6],
            },
          })),
        },
      ],
      graphic: items.length
        ? [
            {
              type: 'text',
              left: 'center',
              top: '36%',
              style: {
                text: `${formatNumber(total)}\n主体命中`,
                textAlign: 'center',
                fill: '#f6f3e9',
                fontSize: 20,
                fontWeight: 700,
                lineHeight: 28,
              },
            },
          ]
        : [getEmptyGraphic('暂无可识别主体')],
    },
    true,
  )

  subjectChart.off('click')
  subjectChart.on('click', (params) => {
    const name = params?.name
    if (name) pushFilter('subject', name)
  })
}

function initRevealObserver() {
  if (!screenRef.value) return
  const nodes = screenRef.value.querySelectorAll('.reveal-section')
  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add('is-visible')
      })
    },
    { threshold: 0.18 },
  )

  nodes.forEach((node) => revealObserver.observe(node))
}

function resizeCharts() {
  trendChart?.resize()
  sourceChart?.resize()
  subjectChart?.resize()
}

async function fetchDashboard() {
  try {
    const [kpiRes, trendRes, sourceRes, audienceRes] = await Promise.all([
      client.get('/insights/kpi-summary'),
      client.get('/insights/trend-analysis'),
      client.get('/insights/source-distribution'),
      client.get('/insights/target-audience'),
    ])

    dashboard.kpi = kpiRes?.data || {}
    dashboard.trend = trendRes?.data || { granularity: 'month', points: [] }
    dashboard.source = sourceRes?.data || { items: [], total: 0 }
    dashboard.audience = audienceRes?.data || { items: [], total: 0, covered_policy_count: 0 }
  } catch (error) {
    console.error('Failed to load insights dashboard data', error)
    ElMessage.error('政策洞察数据加载失败')
  }

  await nextTick()
  initTrendChart()
  initSourceChart()
  initSubjectChart()
  isReady.value = true
}

onMounted(async () => {
  window.addEventListener('resize', resizeCharts)
  initRevealObserver()
  await fetchDashboard()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  revealObserver?.disconnect()
  trendChart?.dispose()
  sourceChart?.dispose()
  subjectChart?.dispose()
  trendChart = null
  sourceChart = null
  subjectChart = null
})
</script>

<style scoped>
.insight-screen {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  padding: 30px 30px 36px;
  color: #f6f3e9;
  background:
    radial-gradient(circle at top left, rgba(78, 126, 91, 0.22), transparent 28%),
    radial-gradient(circle at 84% 10%, rgba(185, 150, 82, 0.16), transparent 24%),
    linear-gradient(145deg, #0d1f17 0%, #14281d 46%, #0b1812 100%);
}

.screen-orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(18px);
  pointer-events: none;
  opacity: 0.42;
  animation: drift 12s ease-in-out infinite;
}

.screen-orb--one {
  top: 86px;
  right: 14%;
  width: 280px;
  height: 280px;
  background: radial-gradient(circle, rgba(137, 169, 125, 0.28), transparent 68%);
}

.screen-orb--two {
  bottom: 120px;
  left: 6%;
  width: 240px;
  height: 240px;
  background: radial-gradient(circle, rgba(185, 150, 82, 0.18), transparent 68%);
  animation-delay: -4s;
}

.screen-grid {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(204, 214, 193, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(204, 214, 193, 0.05) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.9), transparent 92%);
}

.topbar,
.hero-strip,
.main-stage,
.intel-strip {
  position: relative;
  z-index: 1;
}

.topbar {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
  margin-bottom: 26px;
}

.brand-block {
  max-width: 780px;
}

.eyebrow,
.panel-kicker,
.intel-kicker {
  color: rgba(214, 192, 139, 0.84);
  letter-spacing: 0.22em;
  font-size: 11px;
  text-transform: uppercase;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin: 10px 0 10px;
}

.title-row h1 {
  margin: 0;
  font-size: clamp(32px, 4vw, 54px);
  line-height: 1.02;
  font-weight: 700;
  letter-spacing: 0.03em;
}

.brand-block p {
  max-width: 700px;
  margin: 0;
  color: rgba(239, 239, 228, 0.72);
  font-size: 15px;
}

.brand-block code {
  color: #f5e8c3;
  background: rgba(185, 150, 82, 0.12);
  padding: 1px 6px;
  border-radius: 999px;
}

.freshness {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(185, 150, 82, 0.18);
  color: #f5f0de;
  background: rgba(16, 35, 24, 0.76);
  box-shadow: inset 0 0 0 1px rgba(185, 150, 82, 0.05);
  font-size: 12px;
}

.top-actions {
  display: flex;
  gap: 12px;
}

.primary-btn,
.ghost-btn,
.panel-link {
  border: 0;
  cursor: pointer;
  transition:
    transform 180ms ease,
    box-shadow 180ms ease,
    border-color 180ms ease,
    background 180ms ease;
}

.primary-btn,
.ghost-btn {
  min-height: 44px;
  padding: 0 18px;
  border-radius: 999px;
  font-size: 14px;
}

.primary-btn {
  color: #102117;
  background: linear-gradient(135deg, #d2bb87 0%, #f3e2b7 100%);
  box-shadow: 0 16px 34px rgba(185, 150, 82, 0.2);
}

.ghost-btn {
  color: #f2f3e8;
  background: rgba(16, 35, 24, 0.58);
  border: 1px solid rgba(197, 205, 183, 0.16);
}

.panel-link {
  min-height: 36px;
  padding: 0 14px;
  border-radius: 999px;
  color: #f3f4e8;
  background: rgba(15, 35, 24, 0.66);
  border: 1px solid rgba(197, 205, 183, 0.16);
}

.primary-btn:hover,
.ghost-btn:hover,
.panel-link:hover {
  transform: translateY(-1px);
}

.hero-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 22px;
}

.metric-tile,
.panel-shell,
.intel-module {
  position: relative;
  border: 1px solid rgba(197, 205, 183, 0.12);
  background: linear-gradient(180deg, rgba(16, 35, 24, 0.88), rgba(11, 25, 18, 0.94));
  box-shadow:
    inset 0 1px 0 rgba(255, 248, 232, 0.05),
    0 20px 60px rgba(0, 0, 0, 0.24);
  backdrop-filter: blur(10px);
}

.metric-tile {
  padding: 18px 18px 16px;
  border-radius: 22px;
}

.metric-tile::after,
.panel-shell::after,
.intel-module::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(135deg, rgba(185, 150, 82, 0.28), transparent 32%, transparent 68%, rgba(137, 169, 125, 0.16));
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.metric-label {
  color: rgba(228, 231, 218, 0.66);
  font-size: 13px;
}

.metric-value {
  margin-top: 10px;
  color: #f8f3e7;
  font-size: clamp(28px, 2.8vw, 40px);
  font-weight: 700;
  letter-spacing: 0.03em;
}

.metric-hint {
  margin-top: 10px;
  color: rgba(228, 231, 218, 0.58);
  font-size: 12px;
}

.main-stage {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(340px, 0.9fr);
  gap: 18px;
  align-items: stretch;
}

.trend-panel,
.side-panel {
  border-radius: 30px;
  padding: 20px;
}

.side-stack {
  display: grid;
  grid-template-rows: 1fr 1fr;
  gap: 18px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 14px;
}

.panel-head h2 {
  margin: 8px 0 8px;
  font-size: 22px;
  font-weight: 600;
  color: #f8f3e7;
}

.panel-head p {
  margin: 0;
  max-width: 520px;
  color: rgba(228, 231, 218, 0.66);
  font-size: 13px;
}

.chart {
  width: 100%;
}

.chart--hero {
  height: 430px;
}

.chart--side {
  height: 292px;
}

.intel-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-top: 18px;
}

.intel-module {
  min-height: 228px;
  padding: 18px;
  border-radius: 24px;
}

.intel-list {
  margin-top: 16px;
}

.intel-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(197, 205, 183, 0.12);
  color: rgba(240, 241, 231, 0.84);
}

.intel-row strong {
  color: #dcc386;
  font-size: 18px;
  font-weight: 600;
}

.intel-empty {
  margin-top: 24px;
  color: rgba(224, 228, 216, 0.54);
  font-size: 13px;
}

.insight-copy {
  margin-top: 16px;
  display: grid;
  gap: 14px;
}

.insight-copy p {
  margin: 0;
  color: rgba(233, 236, 224, 0.74);
  font-size: 14px;
  line-height: 1.75;
}

.reveal-section {
  opacity: 0;
  transform: translateY(28px);
  transition:
    opacity 520ms ease,
    transform 520ms ease;
}

.reveal-section.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.is-ready .topbar {
  animation: rise-in 720ms ease both;
}

.is-ready .hero-strip {
  animation: rise-in 820ms ease both;
}

@keyframes drift {
  0%,
  100% {
    transform: translate3d(0, 0, 0);
  }
  50% {
    transform: translate3d(12px, -14px, 0);
  }
}

@keyframes rise-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1280px) {
  .hero-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .main-stage {
    grid-template-columns: 1fr;
  }

  .side-stack {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-template-rows: none;
  }
}

@media (max-width: 860px) {
  .insight-screen {
    padding: 22px 18px 26px;
  }

  .topbar {
    flex-direction: column;
  }

  .top-actions {
    width: 100%;
    justify-content: stretch;
  }

  .top-actions button {
    flex: 1;
  }

  .hero-strip,
  .intel-strip,
  .side-stack {
    grid-template-columns: 1fr;
  }

  .chart--hero {
    height: 340px;
  }

  .chart--side {
    height: 280px;
  }
}
</style>
```

## 全局主题样式

路径：`frontend/src/styles/theme.css`

```css
/**
 * 农策微光 · 全站视觉系统
 * 方向：政务高级绿
 */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap');

:root {
  --nc-font-serif: 'Noto Serif SC', serif;
  --nc-font-sans: 'Noto Sans SC', sans-serif;

  --nc-bg: #eef2eb;
  --nc-bg-alt: #e6ede5;
  --nc-home-bg: #f4f6f1;
  --nc-home-surface: rgba(255, 253, 247, 0.78);
  --nc-home-surface-strong: rgba(255, 253, 247, 0.92);
  --nc-home-muted: rgba(18, 39, 27, 0.68);
  --nc-home-dark: #112419;
  --nc-surface: rgba(255, 253, 247, 0.9);
  --nc-surface-strong: rgba(255, 253, 247, 0.98);
  --nc-surface-muted: rgba(246, 248, 242, 0.82);
  --nc-surface-dark: rgba(10, 32, 22, 0.88);
  --nc-overlay: rgba(9, 24, 17, 0.58);

  --nc-text: #20362a;
  --nc-text-strong: #12271b;
  --nc-text-secondary: #536757;
  --nc-text-muted: #7a8a7e;
  --nc-text-inverse: #f5f3ea;

  --nc-primary: #1d5b3d;
  --nc-primary-hover: #174b32;
  --nc-primary-soft: #dce9de;
  --nc-primary-soft-strong: #bdd4c1;
  --nc-ink-deep: #12271b;
  --nc-secondary: #6f8a63;
  --nc-accent-gold: #b99652;
  --nc-accent-gold-soft: rgba(185, 150, 82, 0.14);
  --nc-glass-soft: rgba(255, 253, 247, 0.7);
  --nc-success: #2d6a47;
  --nc-warning: #b67f28;
  --nc-danger: #bb564b;
  --nc-info: #5c7e6c;

  --nc-border: rgba(28, 63, 44, 0.12);
  --nc-border-strong: rgba(28, 63, 44, 0.2);
  --nc-line: rgba(28, 63, 44, 0.08);

  --nc-shadow-xs: 0 4px 10px rgba(18, 41, 29, 0.04);
  --nc-shadow-sm: 0 10px 24px rgba(18, 41, 29, 0.06);
  --nc-shadow: 0 18px 42px rgba(18, 41, 29, 0.08);
  --nc-shadow-lg: 0 28px 64px rgba(18, 41, 29, 0.12);
  --nc-shadow-inset: inset 0 1px 0 rgba(255, 255, 255, 0.78);

  --nc-radius-xs: 10px;
  --nc-radius: 16px;
  --nc-radius-lg: 24px;
  --nc-radius-xl: 32px;
  --nc-pill: 999px;

  --nc-space-1: 4px;
  --nc-space-2: 8px;
  --nc-space-3: 12px;
  --nc-space-4: 16px;
  --nc-space-5: 20px;
  --nc-space-6: 24px;
  --nc-space-7: 32px;
  --nc-space-8: 40px;
  --nc-space-9: 56px;

  --nc-motion-fast: 180ms;
  --nc-motion-base: 280ms;
  --nc-motion-slow: 520ms;
  --nc-ease: cubic-bezier(0.22, 1, 0.36, 1);

  --nc-chart-1: #1d5b3d;
  --nc-chart-2: #4f7b57;
  --nc-chart-3: #87aa7a;
  --nc-chart-4: #b99652;
  --nc-chart-5: #d6bd83;
  --nc-chart-6: #304c3b;

  --el-color-primary: var(--nc-primary);
  --el-color-primary-dark-2: #15452e;
  --el-color-primary-light-3: #4d7f61;
  --el-color-primary-light-5: #7ca48a;
  --el-color-primary-light-7: #a9c4af;
  --el-color-primary-light-8: #c0d4c5;
  --el-color-primary-light-9: #dce9de;
  --el-color-success: var(--nc-success);
  --el-color-warning: var(--nc-warning);
  --el-color-danger: var(--nc-danger);
  --el-border-radius-base: var(--nc-radius);
  --el-border-radius-small: var(--nc-radius-xs);
  --el-border-radius-round: var(--nc-pill);
  --el-box-shadow-light: var(--nc-shadow-sm);
  --el-mask-color: rgba(11, 24, 18, 0.45);
  --el-fill-color-light: rgba(29, 91, 61, 0.05);
  --el-fill-color-blank: rgba(255, 253, 247, 0.98);
  --el-bg-color-page: transparent;
  --el-bg-color-overlay: rgba(255, 253, 247, 0.98);
  --el-border-color: var(--nc-border);
  --el-border-color-light: var(--nc-line);
  --el-text-color-primary: var(--nc-text);
  --el-text-color-regular: var(--nc-text-secondary);
  --el-text-color-secondary: var(--nc-text-muted);
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

body {
  margin: 0;
  min-width: 320px;
  font-family: var(--nc-font-sans);
  color: var(--nc-text);
  line-height: 1.6;
  background:
    radial-gradient(circle at top left, rgba(29, 91, 61, 0.08), transparent 24%),
    radial-gradient(circle at 90% 10%, rgba(185, 150, 82, 0.12), transparent 16%),
    linear-gradient(180deg, #f1f4ef 0%, #e9eee7 100%);
}

body::selection {
  background: rgba(29, 91, 61, 0.16);
}

a {
  color: inherit;
  text-decoration: none;
}

button,
input,
textarea,
select {
  font: inherit;
}

img {
  display: block;
  max-width: 100%;
}

#app {
  min-height: 100vh;
}

.nc-page-shell {
  width: min(1280px, calc(100% - 32px));
  margin: 0 auto;
}

.nc-surface-card {
  border-radius: var(--nc-radius-lg);
  border: 1px solid var(--nc-border);
  background: var(--nc-surface);
  box-shadow: var(--nc-shadow), var(--nc-shadow-inset);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.nc-surface-card--strong {
  background: var(--nc-surface-strong);
}

.nc-surface-card--dark {
  color: var(--nc-text-inverse);
  background: linear-gradient(180deg, rgba(12, 35, 24, 0.95), rgba(17, 49, 34, 0.88));
  border-color: rgba(255, 248, 232, 0.08);
}

.nc-kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  font-weight: 700;
  color: var(--nc-accent-gold);
}

.nc-title {
  margin: 0;
  font-family: var(--nc-font-serif);
  color: var(--nc-text-strong);
  letter-spacing: -0.03em;
}

.nc-copy {
  margin: 0;
  color: var(--nc-text-secondary);
}

.nc-chip {
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  padding: 0 14px;
  border-radius: var(--nc-pill);
  border: 1px solid var(--nc-border);
  background: rgba(255, 253, 247, 0.78);
  color: var(--nc-text-secondary);
  box-shadow: var(--nc-shadow-xs);
}

.nc-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--nc-border-strong), transparent);
}

.nc-reveal {
  opacity: 0;
  transform: translateY(24px);
  transition:
    opacity var(--nc-motion-slow) var(--nc-ease),
    transform var(--nc-motion-slow) var(--nc-ease);
}

.nc-reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.el-button {
  min-height: 44px;
  border-radius: var(--nc-pill);
  font-weight: 600;
  transition:
    transform var(--nc-motion-fast) ease,
    box-shadow var(--nc-motion-fast) ease,
    background var(--nc-motion-fast) ease,
    border-color var(--nc-motion-fast) ease,
    color var(--nc-motion-fast) ease;
}

.el-button:hover {
  transform: translateY(-1px);
}

.el-button--primary {
  --el-button-bg-color: var(--nc-primary);
  --el-button-border-color: var(--nc-primary);
  --el-button-hover-bg-color: var(--nc-primary-hover);
  --el-button-hover-border-color: var(--nc-primary-hover);
  --el-button-active-bg-color: #123c28;
  --el-button-active-border-color: #123c28;
  --el-button-text-color: #f8f5eb;
  box-shadow: 0 14px 28px rgba(29, 91, 61, 0.18);
}

.el-button.is-plain,
.el-button--default {
  --el-button-border-color: var(--nc-border);
  --el-button-hover-border-color: var(--nc-primary);
  --el-button-hover-text-color: var(--nc-primary);
  --el-button-hover-bg-color: rgba(29, 91, 61, 0.05);
  --el-button-active-bg-color: rgba(29, 91, 61, 0.08);
  background: rgba(255, 253, 247, 0.82);
  color: var(--nc-text);
}

.el-input__wrapper,
.el-textarea__inner,
.el-select .el-select__wrapper,
.el-date-editor.el-input,
.el-date-editor.el-input__wrapper {
  border-radius: var(--nc-radius);
}

.el-input__wrapper,
.el-select .el-select__wrapper,
.el-textarea__inner {
  background: rgba(255, 253, 247, 0.92);
  box-shadow:
    0 0 0 1px var(--nc-border) inset,
    0 8px 18px rgba(18, 41, 29, 0.03);
}

.el-input__wrapper:hover,
.el-select .el-select__wrapper:hover,
.el-textarea__inner:hover {
  box-shadow:
    0 0 0 1px var(--nc-border-strong) inset,
    0 10px 20px rgba(18, 41, 29, 0.05);
}

.el-input__wrapper.is-focus,
.el-select .el-select__wrapper.is-focused,
.el-textarea__inner:focus {
  box-shadow:
    0 0 0 4px rgba(29, 91, 61, 0.1),
    0 0 0 1px var(--nc-primary) inset,
    0 16px 24px rgba(18, 41, 29, 0.06);
}

.el-card,
.el-dialog,
.el-message-box {
  border-radius: var(--nc-radius-lg);
  border-color: var(--nc-border);
  box-shadow: var(--nc-shadow-lg);
}

.el-table {
  --el-table-border-color: var(--nc-line);
  --el-table-header-bg-color: rgba(29, 91, 61, 0.05);
  --el-table-row-hover-bg-color: rgba(29, 91, 61, 0.05);
  border-radius: 20px;
  overflow: hidden;
}

.el-table th.el-table__cell {
  color: var(--nc-text-secondary);
  font-weight: 600;
}

.el-drawer__body,
.el-dialog__body,
.el-message-box__content {
  color: var(--nc-text-secondary);
}

.el-form-item__label,
.el-descriptions__label {
  color: var(--nc-text-secondary);
  font-weight: 600;
}

.el-tag {
  min-height: 28px;
  border-radius: var(--nc-pill);
}

.el-tabs__item {
  min-height: 40px;
}

.el-tabs__item.is-active,
.el-tabs__item:hover {
  color: var(--nc-primary);
}

.el-tabs__active-bar {
  background-color: var(--nc-primary);
}

.el-message {
  border-radius: var(--nc-radius);
  border-color: var(--nc-border);
  box-shadow: var(--nc-shadow);
}

::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-thumb {
  background: rgba(29, 91, 61, 0.22);
  border-radius: 999px;
  border: 2px solid rgba(255, 255, 255, 0);
  background-clip: padding-box;
}

::-webkit-scrollbar-track {
  background: transparent;
}

@media (max-width: 768px) {
  .nc-page-shell {
    width: min(100%, calc(100% - 20px));
  }
}
```

