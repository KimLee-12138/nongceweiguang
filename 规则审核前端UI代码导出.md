# 规则审核前端 UI 代码导出

导出时间：2026-04-12

导出范围：规则审核功能直接相关的前端 UI 代码，包括管理端路由入口、侧边导航/页面框架、工作台快捷入口和规则审核主页面源码。

## 文件目录
- `frontend/src/router/index.js`
- `frontend/src/views/admin/AdminLayout.vue`
- `frontend/src/views/admin/AdminDashboard.vue`
- `frontend/src/views/admin/AdminPolicyReview.vue`

## frontend/src/router/index.js

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
      meta: { title: '鍐滅瓥寰厜' },
    },
    {
      path: '/home',
      redirect: '/',
    },
    {
      path: '/insights',
      name: 'BusinessInsight',
      component: () => import('../views/Dashboard/BusinessInsightView.vue'),
      meta: { title: '杈呭姪娲炲療澶у睆' },
    },
    {
      path: '/compass',
      name: 'PolicyCompass',
      component: () => import('../views/Dashboard/PolicyCompassView.vue'),
      meta: { title: '鏀跨瓥椋庡悜鏍? },
    },
    {
      path: '/chat',
      name: 'Chat',
      component: () => import('../views/ChatRouteView.vue'),
      meta: { title: '鏀跨瓥瀵硅瘽宸ヤ綔鍙?, requiresUser: true },
    },
    {
      path: '/login',
      name: 'UserLogin',
      component: () => import('../views/UserLogin.vue'),
      meta: { title: '鐢ㄦ埛鐧诲綍', public: true },
    },
    {
      path: '/register',
      name: 'UserRegister',
      component: () => import('../views/UserRegister.vue'),
      meta: { title: '鐢ㄦ埛娉ㄥ唽', public: true },
    },
    {
      path: '/privacy',
      name: 'PrivacyPolicy',
      component: () => import('../views/LegalDocumentPage.vue'),
      meta: { title: '闅愮鏀跨瓥', public: true, legalDocument: 'privacy' },
    },
    {
      path: '/terms',
      name: 'TermsOfService',
      component: () => import('../views/LegalDocumentPage.vue'),
      meta: { title: '鐢ㄦ埛鍗忚', public: true, legalDocument: 'terms' },
    },
    {
      path: '/admin/login',
      name: 'AdminLogin',
      component: () => import('../views/admin/AdminLogin.vue'),
      meta: { title: '绠＄悊绔櫥褰?, public: true },
    },
    {
      path: '/admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      meta: { title: '绠＄悊绔?, requiresAdmin: true },
      children: [
        {
          path: '',
          name: 'AdminDashboard',
          component: () => import('../views/admin/AdminDashboard.vue'),
          meta: {
            title: '杩愯惀宸ヤ綔鍙?,
            description: '鏌ョ湅鏀跨瓥搴撴鍐点€佹渶杩戣嚜鍔ㄤ换鍔＄姸鎬佸拰鍚庡彴蹇嵎鍏ュ彛銆?,
            section: 'WORKSPACE',
          },
        },
        {
          path: 'policies',
          name: 'AdminPolicies',
          component: () => import('../views/admin/AdminPolicies.vue'),
          meta: {
            title: '鏀跨瓥绠＄悊',
            description: '闆嗕腑缁存姢缁撴瀯鍖栨斂绛栧簱锛屽鐞嗘憳瑕佽ˉ鍏ㄣ€佽鎯呮煡鐪嬪拰鎵归噺鍒犻櫎銆?,
            section: 'POLICY LIBRARY',
          },
        },
        {
          path: 'policies/review',
          name: 'AdminPolicyReview',
          component: () => import('../views/admin/AdminPolicyReview.vue'),
          meta: {
            title: '瑙勫垯璐ㄩ噺瀹℃牳鍙?,
            description: '缁熶竴澶勭悊寰呭鏍告斂绛栵紝鏌ョ湅 AI 寤鸿銆佺紪杈戣鍒欒崏绋垮苟鍐冲畾鏄惁鍏ユ寮忔斂绛栧簱銆?,
            section: 'POLICY LIBRARY',
          },
        },
        {
          path: 'policies/new',
          name: 'AdminPolicyNew',
          component: () => import('../views/admin/AdminPolicyNew.vue'),
          meta: {
            title: '鏂板鏀跨瓥',
            description: '褰曞叆鍘熸枃鍚庣紪璇戜负缁撴瀯鍖栨潯浠舵爲锛屽啓鍏ユ寮忔斂绛栧簱銆?,
            section: 'POLICY AUTHORING',
          },
        },
        {
          path: 'policies/:id/edit',
          name: 'AdminPolicyEdit',
          component: () => import('../views/admin/AdminPolicyEdit.vue'),
          meta: {
            title: '缂栬緫鏀跨瓥',
            description: '璋冩暣缁撴瀯鍖栨斂绛栫殑鏍囬銆佹潵婧愩€佹憳瑕佸拰鍘熸枃寮曠敤淇℃伅銆?,
            section: 'POLICY AUTHORING',
          },
        },
        {
          path: 'policies/import',
          name: 'AdminPolicyImport',
          component: () => import('../views/admin/AdminPolicyImport.vue'),
          meta: {
            title: '瀵煎叆涓庣埇铏?,
            description: '鎵ц鎵嬪姩鎶撳彇銆佹枃浠惰В鏋愬拰鎵归噺閫佸锛岃ˉ榻愬師鏂囬噰闆嗛摼璺€?,
            section: 'INGESTION',
          },
        },
        {
          path: 'tasks',
          name: 'AdminTasks',
          component: () => import('../views/admin/AdminTasks.vue'),
          meta: {
            title: '浠诲姟涓績',
            description: '缁熶竴鏌ョ湅绠＄悊绔悗鍙颁綔涓氱殑鐘舵€併€佸け璐ユ槑缁嗗拰閲嶈瘯鍏ュ彛銆?,
            section: 'OPERATIONS',
          },
        },
        {
          path: 'policies/auto-crawler',
          name: 'AdminAutoCrawler',
          component: () => import('../views/admin/AdminAutoCrawler.vue'),
          meta: {
            title: '鍏ㄨ嚜鍔ㄧ埇铏?,
            description: '缁熶竴绠＄悊鑷姩鍚屾銆丄I 绛涢€夊拰瀹℃牳鍏ラ槦鐨勬墽琛岄摼璺€?,
            section: 'AUTOMATION',
          },
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const title = to.matched[to.matched.length - 1]?.meta?.title
  if (title) document.title = `${title} | 鍐滀笟鏀跨瓥鏅鸿兘鍖归厤`

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

## frontend/src/views/admin/AdminLayout.vue

```vue
<template>
  <div v-if="sessionReady && isAuthenticated" class="admin-layout">
    <aside class="admin-sidebar">
      <div class="sidebar-brand">
        <img class="brand-mark" :src="brandLogoMark" alt="AgriPolicy AI" />
        <div>
          <p class="brand-kicker">ADMIN CONSOLE</p>
          <h1 class="brand-title">鍐滅瓥寰厜</h1>
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
          <span class="user-meta">褰撳墠璐﹀彿</span>
          <strong>{{ adminUsername || '绠＄悊鍛? }}</strong>
        </div>
        <el-button type="danger" plain class="logout-btn" @click="handleLogout">閫€鍑虹櫥褰?/el-button>
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
            <strong class="drawer-title">鍐滅瓥寰厜</strong>
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
          <span class="user-meta">褰撳墠璐﹀彿</span>
          <strong>{{ adminUsername || '绠＄悊鍛? }}</strong>
        </div>
        <el-button type="danger" plain class="logout-btn" @click="handleLogout">閫€鍑虹櫥褰?/el-button>
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
          <el-button plain @click="router.push('/')">杩斿洖棣栭〉</el-button>
          <el-button plain @click="router.push('/insights')">鏀跨瓥娲炲療</el-button>
          <el-button type="primary" @click="router.push('/chat')">杩涘叆鑱婂ぉ</el-button>
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
        <el-button type="primary" size="large" :loading="retryingSession" @click="retrySessionRecovery">閲嶈瘯鎭㈠</el-button>
        <el-button size="large" @click="router.push(isForbidden ? '/login' : '/admin/login')">
          {{ isForbidden ? '鍒囨崲鍒扮敤鎴风鍏ュ彛' : '鍓嶅線绠＄悊绔櫥褰? }}
        </el-button>
        <el-button plain size="large" @click="router.push('/')">杩斿洖棣栭〉</el-button>
      </div>
    </div>
  </div>
  <div v-else class="admin-access admin-access--loading">
    <div class="admin-access__loading">姝ｅ湪鎭㈠绠＄悊绔細璇?..</div>
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
  { key: 'dashboard', label: '宸ヤ綔鍙?, to: '/admin', icon: Histogram, names: ['AdminDashboard'] },
  { key: 'policies', label: '鏀跨瓥绠＄悊', to: '/admin/policies', icon: Document, names: ['AdminPolicies', 'AdminPolicyEdit'] },
  { key: 'review', label: '瑙勫垯瀹℃牳', to: '/admin/policies/review', icon: Opportunity, names: ['AdminPolicyReview'] },
  { key: 'new', label: '鏂板鏀跨瓥', to: '/admin/policies/new', icon: EditPen, names: ['AdminPolicyNew'] },
  { key: 'import', label: '瀵煎叆涓庣埇铏?, to: '/admin/policies/import', icon: FolderOpened, names: ['AdminPolicyImport'] },
  { key: 'tasks', label: '浠诲姟涓績', to: '/admin/tasks', icon: Files, names: ['AdminTasks'] },
  { key: 'crawler', label: '鍏ㄨ嚜鍔ㄧ埇铏?, to: '/admin/policies/auto-crawler', icon: Cpu, names: ['AdminAutoCrawler'] },
]

const currentTitle = computed(() => route.meta?.title || '绠＄悊绔?)
const currentDescription = computed(
  () => route.meta?.description || '缁熶竴绠＄悊鏀跨瓥搴撱€佸師鏂囧鍏ャ€佸悗鍙颁綔涓氬拰鑷姩浠诲姟銆?,
)
const currentSection = computed(() => route.meta?.section || 'ADMIN')
const isAuthenticated = computed(() => adminSessionStatus.value === 'authenticated')
const isForbidden = computed(() => adminSessionStatus.value === 'forbidden')
const accessTitle = computed(() => (isForbidden.value ? '褰撳墠璐﹀彿鏃犳潈璁块棶绠＄悊绔? : '绠＄悊绔細璇濇仮澶嶅け璐?))
const accessDescription = computed(() =>
  isForbidden.value
    ? '褰撳墠璐﹀彿缂哄皯杩涘叆绠＄悊绔殑鏉冮檺銆備綘鍙互鍒囨崲鍒版櫘閫氱敤鎴峰叆鍙ｏ紝鎴栭噸鏂扮櫥褰曞叾浠栫鐞嗗憳璐﹀彿鍚庡啀璇曘€?
    : adminSessionError.value?.message || '缃戠粶寮傚父鎴栨湇鍔℃殏鏃朵笉鍙敤锛屽綋鍓嶄笉浼氳嚜鍔ㄦ妸浣犲綋浣滃凡閫€鍑恒€傝绋嶅悗閲嶈瘯銆?
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

## frontend/src/views/admin/AdminDashboard.vue

```vue
<template>
  <div class="page-shell admin-dashboard">
    <section class="page-panel">
      <div class="page-head">
        <div class="page-title-group">
          <h3 class="page-title">浠婃棩姒傝</h3>
          <p class="page-subtitle">
            姹囨€绘斂绛栧簱瑙勬ā銆佸緟瀹℃牳浠诲姟銆佽嚜鍔ㄧ埇铏渶杩戠粨鏋滃拰缁熶竴浠诲姟涓績鍏ュ彛銆?          </p>
        </div>
        <div class="page-actions">
          <el-button plain @click="router.push('/admin/tasks')">浠诲姟涓績</el-button>
          <el-button plain @click="router.push('/admin/policies/import')">鎵嬪姩瀵煎叆</el-button>
          <el-button type="primary" @click="router.push('/admin/policies/new')">鏂板鏀跨瓥</el-button>
        </div>
      </div>

      <div class="stat-grid">
        <div class="stat-card">
          <span class="stat-label">缁撴瀯鍖栨斂绛栨€绘暟</span>
          <strong class="stat-value">{{ overview.totalPolicies }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">寰呭鏍镐换鍔?/span>
          <strong class="stat-value">{{ overview.pendingReview }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">鏈€杩戝叆闃熸暟</span>
          <strong class="stat-value">{{ overview.lastQueued }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">鏈€杩戣嚜鍔ㄤ换鍔＄姸鎬?/span>
          <strong class="stat-value">{{ statusText(lastRun.status) }}</strong>
        </div>
      </div>
    </section>

    <section class="page-grid two-column">
      <div class="page-panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">蹇嵎鎿嶄綔</h3>
            <p class="panel-subtitle">甯哥敤鍏ュ彛缁熶竴鏀剁撼鍒板伐浣滃彴锛岄伩鍏嶅湪澶氫釜椤甸潰闂撮绻佽烦杞€?/p>
          </div>
        </div>

        <div class="quick-grid">
          <button type="button" class="quick-card" @click="router.push('/admin/policies')">
            <span class="quick-kicker">LIST</span>
            <strong>杩涘叆鏀跨瓥绠＄悊</strong>
            <p>鏌ョ湅缁撴瀯鍖栨斂绛栥€佹墦寮€璇︽儏銆佺紪杈戝拰鎵归噺鍒犻櫎銆?/p>
          </button>
          <button type="button" class="quick-card" @click="router.push('/admin/policies/review')">
            <span class="quick-kicker">REVIEW</span>
            <strong>瑙勫垯璐ㄩ噺瀹℃牳鍙?/strong>
            <p>鏌ョ湅寰呭鏍告斂绛栥€佺紪杈戣崏绋垮苟鍐冲畾鏄惁鍏ユ寮忓簱銆?/p>
          </button>
          <button type="button" class="quick-card" @click="router.push('/admin/policies/import')">
            <span class="quick-kicker">INGEST</span>
            <strong>瀵煎叆涓庣埇铏?/strong>
            <p>鎵ц鏂囦欢瑙ｆ瀽銆佹仮澶嶆姄鍙栫粨鏋滐紝骞跺垱寤哄鍏ュ悗鍙颁綔涓氥€?/p>
          </button>
          <button type="button" class="quick-card" @click="router.push('/admin/tasks')">
            <span class="quick-kicker">TASKS</span>
            <strong>浠诲姟涓績</strong>
            <p>缁熶竴鏌ョ湅鍚庡彴浣滀笟杩涘害銆佸け璐ユ槑缁嗗拰鏁翠换鍔￠噸璇曘€?/p>
          </button>
          <button type="button" class="quick-card accent" @click="handleRegenerateCompass">
            <span class="quick-kicker">COMPASS</span>
            <strong>{{ compassGenerating ? '姝ｅ湪鍒涘缓浠诲姟' : '鐢熸垚鏈湡椋庡悜鏍? }}</strong>
            <p>鍒涘缓鍛ㄦ姤涓庢湳璇瘝鍏哥殑鍚庡彴浣滀笟锛屽畬鎴愬悗鍚屾鍒板墠鍙板睍绀恒€?/p>
          </button>
        </div>

        <p v-if="compassResult" class="feedback success">{{ compassResult }}</p>
        <p v-if="compassError" class="feedback error">{{ compassError }}</p>
      </div>

      <div class="page-grid">
        <section class="page-panel">
          <h3 class="panel-title">鏈€杩戣嚜鍔ㄤ换鍔?/h3>
          <p class="panel-subtitle">鐢ㄤ簬纭鑷姩鐖櫕涓庡鏍稿叆闃熼摼璺槸鍚﹀浜庡彲鐢ㄧ姸鎬併€?/p>
          <div class="status-card">
            <el-tag :type="statusType(lastRun.status)" effect="light">{{ statusText(lastRun.status) }}</el-tag>
            <p class="admin-note">鏈€杩戞墽琛屾椂闂达細<strong>{{ formatTime(lastRun.run_at) }}</strong></p>
            <ul class="soft-list">
              <li>寰呭鐞嗗師鏂?{{ lastRun.crawled_count || 0 }} 鏉?/li>
              <li>绛涢€夐€氳繃 {{ lastRun.filtered_count || 0 }} 鏉?/li>
              <li>杩涘叆瀹℃牳闃熷垪 {{ lastRun.queued_count || 0 }} 鏉?/li>
            </ul>
            <div class="page-actions">
              <el-button plain @click="router.push('/admin/policies/auto-crawler')">鏌ョ湅鑷姩鐖櫕</el-button>
              <el-button plain @click="router.push('/admin/tasks')">鏌ョ湅浠诲姟涓績</el-button>
            </div>
          </div>
        </section>

        <section class="page-panel">
          <h3 class="panel-title">鏈€杩戦鍚戞爣</h3>
          <p class="panel-subtitle">鏄剧ず鏈€鏂版姤鍛婃爣棰橈紝甯姪纭鍓嶅彴椋庡悜鏍囧唴瀹规槸鍚﹀凡鏇存柊銆?/p>
          <div class="status-card">
            <strong class="latest-title">{{ latestCompassTitle }}</strong>
            <p class="admin-note">鏈€杩戝埛鏂版椂闂达細{{ latestCompassTime }}</p>
            <div class="page-actions">
              <el-button plain @click="router.push('/compass')">鏌ョ湅椋庡悜鏍囧墠鍙?/el-button>
              <el-button plain @click="router.push('/chat')">鏌ョ湅鑱婂ぉ椤?/el-button>
            </div>
          </div>
        </section>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  getAutoCrawlerLastRun,
  getCompassReports,
  getPolicies,
  getPolicyReviewTasks,
  triggerCompassGenerate,
} from '../../api/client'

const router = useRouter()

const compassGenerating = ref(false)
const compassResult = ref('')
const compassError = ref('')
const latestCompassTitle = ref('鏆傛棤鍛ㄦ姤璁板綍')
const latestCompassTime = ref('鏆傛棤鏁版嵁')

const overview = reactive({
  totalPolicies: 0,
  pendingReview: 0,
  lastQueued: 0,
})

const lastRun = reactive({
  run_at: null,
  status: null,
  crawled_count: 0,
  filtered_count: 0,
  queued_count: 0,
  failed_count: 0,
})

async function loadOverview() {
  const [policyRes, runRes, reports, reviewRes] = await Promise.all([
    getPolicies({ offset: 0, limit: 1 }),
    getAutoCrawlerLastRun(),
    getCompassReports(1),
    getPolicyReviewTasks({ offset: 0, limit: 1, review_status: 'pending' }),
  ])

  overview.totalPolicies = policyRes?.total ?? 0
  overview.pendingReview = reviewRes?.stats?.pending ?? reviewRes?.total ?? 0
  overview.lastQueued = runRes?.queued_count || 0

  lastRun.run_at = runRes?.run_at || null
  lastRun.status = runRes?.status || null
  lastRun.crawled_count = runRes?.crawled_count || 0
  lastRun.filtered_count = runRes?.filtered_count || 0
  lastRun.queued_count = runRes?.queued_count || 0
  lastRun.failed_count = runRes?.failed_count || 0

  const latest = Array.isArray(reports) ? reports[0] : null
  latestCompassTitle.value = latest?.title || '鏆傛棤鍛ㄦ姤璁板綍'
  latestCompassTime.value = formatTime(latest?.published_at || latest?.created_at || null)
}

async function handleRegenerateCompass() {
  compassGenerating.value = true
  compassResult.value = ''
  compassError.value = ''
  try {
    const run = await triggerCompassGenerate()
    compassResult.value = '椋庡悜鏍囧悗鍙颁綔涓氬凡鍒涘缓锛屾鍦ㄨ烦杞换鍔′腑蹇冦€?
    ElMessage.success('椋庡悜鏍囩敓鎴愪换鍔″凡鍒涘缓')
    router.push(`/admin/tasks?run_id=${run.run_id}`)
  } catch (error) {
    compassError.value = error.response?.data?.detail || error.message || '鍒涘缓椋庡悜鏍囩敓鎴愪换鍔″け璐?
    ElMessage.error(compassError.value)
  } finally {
    compassGenerating.value = false
  }
}

function formatTime(value) {
  if (!value) return '鏆傛棤璁板綍'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

function statusType(status) {
  if (status === 'success') return 'success'
  if (status === 'partial') return 'warning'
  if (status === 'failed') return 'danger'
  return 'info'
}

function statusText(status) {
  if (status === 'success') return '杩愯鎴愬姛'
  if (status === 'partial') return '閮ㄥ垎鎴愬姛'
  if (status === 'failed') return '杩愯澶辫触'
  return '鏆傛棤璁板綍'
}

onMounted(async () => {
  try {
    await loadOverview()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '鍔犺浇宸ヤ綔鍙版暟鎹け璐?)
  }
})
</script>

<style scoped>
.panel-head {
  margin-bottom: 1rem;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.quick-card {
  padding: 1.05rem 1.05rem 1rem;
  border: 1px solid rgba(19, 59, 41, 0.1);
  border-radius: 22px;
  background: rgba(255, 253, 247, 0.8);
  text-align: left;
  cursor: pointer;
  transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
}

.quick-card:hover {
  transform: translateY(-2px);
  border-color: rgba(26, 95, 58, 0.25);
  box-shadow: 0 14px 28px rgba(43, 60, 48, 0.08);
}

.quick-card.accent {
  background: linear-gradient(135deg, rgba(241, 248, 237, 0.95), rgba(247, 241, 226, 0.95));
}

.quick-kicker {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.72rem;
  letter-spacing: 0.18em;
  color: #7a8778;
}

.quick-card strong {
  display: block;
  color: #173726;
  font-size: 1.02rem;
}

.quick-card p {
  margin: 0.45rem 0 0;
  color: #6d796c;
  line-height: 1.7;
}

.status-card {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding: 1rem 1.05rem;
  border-radius: 20px;
  background: rgba(255, 253, 247, 0.8);
  border: 1px solid rgba(19, 59, 41, 0.08);
}

.latest-title {
  color: #173726;
  line-height: 1.6;
}

.feedback {
  margin: 0.9rem 0 0;
  font-size: 0.92rem;
}

.feedback.success {
  color: #1a5f3a;
}

.feedback.error {
  color: #b64242;
}

@media (max-width: 780px) {
  .quick-grid {
    grid-template-columns: 1fr;
  }
}
</style>
```

## frontend/src/views/admin/AdminPolicyReview.vue

```vue
<template>
  <div class="page-shell admin-policy-review">
    <section class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">瑙勫垯璐ㄩ噺瀹℃牳鍙?/h3>
        <p class="page-subtitle">
          鎵€鏈夋柊鏀跨瓥鍏堣繘鍏ュ鏍搁槦鍒椼€備綘鍙互鏌ョ湅鍘熸枃銆佺紪杈戣鍒欒崏绋匡紝骞剁粨鍚?AI 瀹℃牳寤鸿鍋氭渶缁堝喅绛栥€?        </p>
      </div>
      <div class="page-actions">
        <el-button plain @click="loadList">鍒锋柊鍒楄〃</el-button>
        <el-button type="primary" @click="router.push('/admin/policies/new')">鏂板缓寰呭鏍镐换鍔?/el-button>
      </div>
    </section>

    <section class="page-panel">
      <div class="stat-grid review-stat-grid">
        <div class="stat-card">
          <span class="stat-label">寰呭鏍?/span>
          <strong class="stat-value">{{ stats.pending }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">宸查€氳繃</span>
          <strong class="stat-value">{{ stats.approved }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">宸查┏鍥?/span>
          <strong class="stat-value">{{ stats.rejected }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">AI 澶辫触</span>
          <strong class="stat-value">{{ stats.ai_failed }}</strong>
        </div>
      </div>

      <div class="review-filters">
        <el-select v-model="filters.review_status" clearable placeholder="瀹℃牳鐘舵€? class="filter-item">
          <el-option label="寰呭鏍? value="pending" />
          <el-option label="宸查€氳繃" value="approved" />
          <el-option label="宸查┏鍥? value="rejected" />
        </el-select>
        <el-select v-model="filters.source_type" clearable placeholder="鏉ユ簮绫诲瀷" class="filter-item">
          <el-option label="鑷姩鎶撳彇" value="crawler" />
          <el-option label="鏂囦欢涓婁紶" value="upload" />
          <el-option label="鎵嬪姩鏂板" value="manual" />
        </el-select>
        <el-select v-model="filters.category" clearable placeholder="鍒嗙被" class="filter-item">
          <el-option v-for="item in CATEGORY_OPTIONS" :key="item" :label="item" :value="item" />
        </el-select>
        <el-input
          v-model="filters.keyword"
          clearable
          placeholder="鎸夋爣棰樸€佹潵婧愩€佹憳瑕佹悳绱?
          class="filter-item keyword"
          @keyup.enter="handleFilter"
        />
        <el-button type="primary" @click="handleFilter">绛涢€?/el-button>
      </div>
    </section>

    <section class="review-layout">
      <div class="page-panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">瀹℃牳浠诲姟鍒楄〃</h3>
            <p class="panel-subtitle">閫夋嫨涓€鏉′换鍔℃煡鐪嬪師鏂囥€佽鍒欒崏绋垮拰 AI 寤鸿銆?/p>
          </div>
        </div>

        <el-table
          v-loading="listLoading"
          :data="tasks"
          row-key="id"
          class="surface-table"
          height="640"
          highlight-current-row
          :current-row-key="selectedTaskId"
          @current-change="handleSelectTask"
        >
          <el-table-column prop="title" label="鏍囬" min-width="220" show-overflow-tooltip />
          <el-table-column prop="source" label="鏉ユ簮" min-width="140" show-overflow-tooltip />
          <el-table-column label="绫诲瀷" width="110">
            <template #default="{ row }">{{ sourceTypeText(row.source_type) }}</template>
          </el-table-column>
          <el-table-column prop="ai_category" label="AI 鍒嗙被" width="130" show-overflow-tooltip />
          <el-table-column label="AI 寤鸿" width="110">
            <template #default="{ row }">
              <el-tag size="small" :type="recommendationType(row.ai_recommendation)" effect="light">
                {{ recommendationText(row.ai_recommendation) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="鐘舵€? width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="reviewStatusType(row.review_status)" effect="light">
                {{ reviewStatusText(row.review_status) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          class="surface-pagination"
          @current-change="loadList"
          @size-change="loadList"
        />
      </div>

      <div class="review-main">
        <section class="page-panel detail-panel">
          <div v-if="detailLoading" class="empty-hint">鍔犺浇璇︽儏涓?..</div>
          <div v-else-if="!detail" class="empty-hint">璇烽€夋嫨宸︿晶浠诲姟鏌ョ湅璇︽儏銆?/div>
          <template v-else>
            <div class="panel-head">
              <div>
                <h3 class="panel-title">鍘熸枃涓庤鍒欒崏绋?/h3>
                <p class="panel-subtitle">鍏堟牳瀵规斂绛栧師鏂囷紝鍐嶇‘璁よ鍒?JSON 鏄惁鍙俊銆?/p>
              </div>
              <div class="tag-row">
                <el-tag :type="reviewStatusType(detail.review_status)" effect="light">
                  {{ reviewStatusText(detail.review_status) }}
                </el-tag>
                <el-tag :type="aiStatusType(detail.ai_status)" effect="light">
                  AI {{ aiStatusText(detail.ai_status) }}
                </el-tag>
              </div>
            </div>

            <div class="detail-meta-grid">
              <div class="detail-block">
                <span class="detail-label">鍘熷鏍囬</span>
                <strong>{{ detail.title }}</strong>
              </div>
              <div class="detail-block">
                <span class="detail-label">鏉ユ簮绫诲瀷</span>
                <strong>{{ sourceTypeText(detail.source_type) }}</strong>
              </div>
              <div class="detail-block">
                <span class="detail-label">鏉ユ簮鏈烘瀯</span>
                <strong>{{ detail.source || '鏈彁渚? }}</strong>
              </div>
              <div class="detail-block">
                <span class="detail-label">鍘熸枃閾炬帴</span>
                <el-link
                  v-if="isUrl(detail.raw_text_ref || detail.source_ref)"
                  type="primary"
                  :href="detail.raw_text_ref || detail.source_ref"
                  target="_blank"
                  rel="noopener"
                >
                  鎵撳紑鍘熸枃
                </el-link>
                <span v-else class="muted-text">鏃犻摼鎺?/span>
              </div>
            </div>

            <div class="detail-block raw-text-block">
              <span class="detail-label">鏀跨瓥鍘熸枃</span>
              <pre class="raw-text">{{ detail.raw_text }}</pre>
            </div>

            <el-form label-position="top" class="draft-form">
              <div class="draft-grid">
                <el-form-item label="鑽夌鏍囬">
                  <el-input v-model="draft.title" />
                </el-form-item>
                <el-form-item label="鑽夌鏉ユ簮">
                  <el-input v-model="draft.source" clearable />
                </el-form-item>
              </div>
              <el-form-item label="鑽夌鎽樿">
                <el-input v-model="draft.summary" type="textarea" :rows="4" />
              </el-form-item>
              <el-form-item label="鍒嗙被">
                <el-select v-model="draft.category" class="full-width">
                  <el-option v-for="item in CATEGORY_OPTIONS" :key="item" :label="item" :value="item" />
                </el-select>
              </el-form-item>
              <el-form-item label="瑙勫垯 JSON 鑽夌">
                <el-input v-model="draft.conditionTreeJson" type="textarea" :rows="16" class="json-textarea" />
              </el-form-item>
            </el-form>

            <div class="page-actions">
              <el-button type="primary" :loading="saveLoading" @click="handleSaveDraft">淇濆瓨鑽夌</el-button>
              <el-button type="success" :loading="approveLoading" @click="handleApprove">缂栬緫鍚庨€氳繃</el-button>
              <el-button type="danger" plain :loading="rejectLoading" @click="handleReject">椹冲洖</el-button>
            </div>

            <div v-if="detail.events?.length" class="timeline-wrap">
              <h4 class="panel-title small">瀹℃牳鐣欑棔</h4>
              <el-timeline>
                <el-timeline-item
                  v-for="event in detail.events"
                  :key="event.id"
                  :timestamp="formatTime(event.created_at)"
                  placement="top"
                >
                  <div class="timeline-card">
                    <strong>{{ eventTypeText(event.event_type) }}</strong>
                    <p class="timeline-meta">鎿嶄綔浜猴細{{ event.operator || '绯荤粺' }}</p>
                    <p v-if="event.comment" class="timeline-comment">{{ event.comment }}</p>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </template>
        </section>

        <aside class="page-panel ai-panel">
          <div v-if="!detail" class="empty-hint">閫夋嫨浠诲姟鍚庢煡鐪?AI 瀹℃牳鍔╂墜銆?/div>
          <template v-else>
            <div class="panel-head">
              <div>
                <h3 class="panel-title">AI 瀹℃牳鍔╂墜</h3>
                <p class="panel-subtitle">AI 杈撳嚭鎽樿銆佸垎绫汇€佸鏍稿缓璁拰渚濇嵁鏉℃锛屼粎渚涗汉宸ュ鏍搞€?/p>
              </div>
              <el-button plain size="small" :loading="refreshAILoading" @click="handleRefreshAI">閲嶆柊鐢熸垚</el-button>
            </div>

            <div class="ai-disclaimer">
              AI 浠呬负杈呭姪鍒ゆ柇锛屼笉浠ｈ〃鏈€缁堝鏍哥粨璁猴紝璇蜂互鍘熸枃鍜岃鍒欒崏绋垮鏍镐负鍑嗐€?            </div>

            <div class="detail-block">
              <span class="detail-label">AI 鎽樿</span>
              <p class="detail-paragraph">{{ detail.ai_summary || detail.ai_error || '鏆傛棤 AI 杈撳嚭' }}</p>
            </div>

            <div class="detail-block">
              <span class="detail-label">AI 鍒嗙被</span>
              <strong>{{ detail.ai_category || '鏈垎绫? }}</strong>
            </div>

            <div class="detail-block">
              <span class="detail-label">瀹℃牳寤鸿</span>
              <p class="detail-paragraph">{{ detail.ai_suggestion || '鏆傛棤寤鸿' }}</p>
            </div>

            <div class="detail-block">
              <span class="detail-label">鏄惁寤鸿閫氳繃</span>
              <el-tag :type="recommendationType(detail.ai_recommendation)" effect="light">
                {{ recommendationText(detail.ai_recommendation) }}
              </el-tag>
            </div>

            <div class="detail-block">
              <span class="detail-label">涓昏椋庨櫓鐐?/span>
              <ul v-if="detail.ai_risk_points_json?.length" class="soft-list risk-list">
                <li v-for="(item, idx) in detail.ai_risk_points_json" :key="`${idx}-${item}`">{{ item }}</li>
              </ul>
              <p v-else class="detail-paragraph">鏆傛棤椋庨櫓鐐广€?/p>
            </div>

            <div class="detail-block">
              <span class="detail-label">渚濇嵁鏉℃</span>
              <div v-if="detail.ai_evidence_json?.length" class="evidence-list">
                <article
                  v-for="(item, idx) in detail.ai_evidence_json"
                  :key="`${idx}-${item.source_type}-${item.locator}`"
                  class="evidence-item"
                >
                  <div class="evidence-head">
                    <strong>{{ item.locator }}</strong>
                    <el-tag size="small" effect="light">{{ evidenceSourceText(item.source_type) }}</el-tag>
                  </div>
                  <p class="evidence-excerpt">{{ item.excerpt }}</p>
                  <p class="evidence-relevance">{{ item.relevance }}</p>
                </article>
              </div>
              <p v-else class="detail-paragraph">鏈 AI 鏈畾浣嶅埌绋冲畾渚濇嵁锛岃浜哄伐閲嶇偣澶嶆牳鍘熸枃銆?/p>
            </div>

            <div v-if="detail.rejection_reason" class="detail-block">
              <span class="detail-label">鏈€杩戦┏鍥炲師鍥?/span>
              <p class="detail-paragraph">{{ detail.rejection_reason }}</p>
            </div>
          </template>
        </aside>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  approvePolicyReviewTask,
  getPolicyReviewTask,
  getPolicyReviewTasks,
  refreshPolicyReviewAI,
  rejectPolicyReviewTask,
  updatePolicyReviewDraft,
} from '../../api/client'

const router = useRouter()

const CATEGORY_OPTIONS = [
  '楂樻爣鍑嗗啘鐢?,
  '缁胯壊绉嶅吇',
  '鍐滄満瑁呭',
  '鏁板瓧鍐滀笟',
  '鍐烽摼鐗╂祦',
  '璁炬柦鍐滀笟',
  '鍐滀骇鍝佸姞宸?,
  '閲戣瀺淇濋櫓',
  '鍏朵粬',
]

const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const listLoading = ref(false)
const detailLoading = ref(false)
const saveLoading = ref(false)
const approveLoading = ref(false)
const rejectLoading = ref(false)
const refreshAILoading = ref(false)
const tasks = ref([])
const selectedTaskId = ref(null)
const detail = ref(null)

const stats = reactive({
  pending: 0,
  approved: 0,
  rejected: 0,
  ai_failed: 0,
})

const filters = reactive({
  review_status: 'pending',
  source_type: '',
  category: '',
  keyword: '',
})

const draft = reactive({
  title: '',
  source: '',
  summary: '',
  category: '鍏朵粬',
  conditionTreeJson: '{}',
})

function isUrl(value) {
  return typeof value === 'string' && (value.startsWith('http://') || value.startsWith('https://'))
}

function formatTime(value) {
  if (!value) return '鏆傛棤璁板綍'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

function sourceTypeText(value) {
  if (value === 'crawler') return '鑷姩鎶撳彇'
  if (value === 'upload') return '鏂囦欢涓婁紶'
  if (value === 'manual') return '鎵嬪姩鏂板'
  return '鏈煡'
}

function reviewStatusText(value) {
  if (value === 'approved') return '宸查€氳繃'
  if (value === 'rejected') return '宸查┏鍥?
  return '寰呭鏍?
}

function reviewStatusType(value) {
  if (value === 'approved') return 'success'
  if (value === 'rejected') return 'danger'
  return 'warning'
}

function aiStatusText(value) {
  if (value === 'success') return '鎴愬姛'
  if (value === 'failed') return '澶辫触'
  return '澶勭悊涓?
}

function aiStatusType(value) {
  if (value === 'success') return 'success'
  if (value === 'failed') return 'danger'
  return 'info'
}

function recommendationText(value) {
  if (value === 'approve') return '寤鸿閫氳繃'
  if (value === 'reject') return '寤鸿椹冲洖'
  return '寤鸿澶嶆牳'
}

function recommendationType(value) {
  if (value === 'approve') return 'success'
  if (value === 'reject') return 'danger'
  return 'warning'
}

function evidenceSourceText(value) {
  return value === 'draft_tree' ? '瑙勫垯鑽夌' : '鍘熸枃鏉℃'
}

function eventTypeText(value) {
  if (value === 'created') return '浠诲姟鍒涘缓'
  if (value === 'draft_saved') return '鑽夌淇濆瓨'
  if (value === 'ai_refreshed') return 'AI 閲嶈窇'
  if (value === 'approved') return '瀹℃牳閫氳繃'
  if (value === 'rejected') return '瀹℃牳椹冲洖'
  return value
}

function fillDraftForm(task) {
  draft.title = task?.draft_title || task?.title || ''
  draft.source = task?.draft_source || task?.source || ''
  draft.summary = task?.draft_summary || ''
  draft.category = task?.draft_category || task?.ai_category || '鍏朵粬'
  draft.conditionTreeJson = JSON.stringify(task?.draft_condition_tree || {}, null, 2)
}

async function loadDetail(taskId) {
  if (!taskId) {
    detail.value = null
    return
  }
  detailLoading.value = true
  try {
    detail.value = await getPolicyReviewTask(taskId)
    fillDraftForm(detail.value)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '鍔犺浇瀹℃牳璇︽儏澶辫触')
  } finally {
    detailLoading.value = false
  }
}

async function loadList() {
  listLoading.value = true
  try {
    const response = await getPolicyReviewTasks({
      offset: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      review_status: filters.review_status || undefined,
      source_type: filters.source_type || undefined,
      category: filters.category || undefined,
      keyword: filters.keyword || undefined,
    })
    tasks.value = response.items || []
    total.value = response.total || 0
    stats.pending = response.stats?.pending || 0
    stats.approved = response.stats?.approved || 0
    stats.rejected = response.stats?.rejected || 0
    stats.ai_failed = response.stats?.ai_failed || 0

    const hasSelected = tasks.value.some((item) => item.id === selectedTaskId.value)
    if (!hasSelected) {
      selectedTaskId.value = tasks.value[0]?.id || null
    }
    if (selectedTaskId.value) {
      await loadDetail(selectedTaskId.value)
    } else {
      detail.value = null
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '鍔犺浇瀹℃牳浠诲姟澶辫触')
  } finally {
    listLoading.value = false
  }
}

function handleSelectTask(row) {
  selectedTaskId.value = row?.id || null
  if (selectedTaskId.value) {
    loadDetail(selectedTaskId.value)
  }
}

function handleFilter() {
  page.value = 1
  loadList()
}

function parseDraftTree() {
  try {
    return JSON.parse(draft.conditionTreeJson || '{}')
  } catch {
    throw new Error('瑙勫垯 JSON 涓嶆槸鍚堟硶鏍煎紡')
  }
}

async function saveDraftOnly(comment = '') {
  if (!selectedTaskId.value) return null
  const tree = parseDraftTree()
  return updatePolicyReviewDraft(selectedTaskId.value, {
    draft_title: draft.title,
    draft_source: draft.source || undefined,
    draft_summary: draft.summary || undefined,
    draft_category: draft.category,
    draft_condition_tree: tree,
    comment: comment || undefined,
  })
}

async function handleSaveDraft() {
  saveLoading.value = true
  try {
    await saveDraftOnly('浜哄伐淇濆瓨鑽夌')
    ElMessage.success('鑽夌宸蹭繚瀛?)
    await Promise.all([loadList(), loadDetail(selectedTaskId.value)])
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || error.message || '淇濆瓨鑽夌澶辫触')
  } finally {
    saveLoading.value = false
  }
}

async function handleApprove() {
  if (!selectedTaskId.value) return
  try {
    await ElMessageBox.confirm(
      'AI 浠呬负杈呭姪鍒ゆ柇锛屼笉浠ｈ〃鏈€缁堝鏍哥粨璁恒€傝纭浣犲凡浜哄伐鏍稿鍘熸枃銆佽鍒欒崏绋垮拰 AI 渚濇嵁鍚庡啀閫氳繃銆?,
      '纭瀹℃牳閫氳繃',
      {
        confirmButtonText: '纭閫氳繃',
        cancelButtonText: '鍙栨秷',
        type: 'warning',
      },
    )
  } catch (error) {
    if (error === 'cancel' || error?.action === 'cancel' || error?.action === 'close') return
    ElMessage.error(error.message || '纭瀹℃牳閫氳繃鏃跺彂鐢熷紓甯?)
    return
  }

  approveLoading.value = true
  try {
    await saveDraftOnly('浜哄伐淇敼鍚庢彁浜ら€氳繃')
    await approvePolicyReviewTask(selectedTaskId.value, { comment: '瀹℃牳閫氳繃骞跺啓鍏ユ寮忔斂绛栧簱' })
    ElMessage.success('瀹℃牳閫氳繃锛屽凡鍐欏叆姝ｅ紡鏀跨瓥搴?)
    await loadList()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || error.message || '瀹℃牳閫氳繃澶辫触')
  } finally {
    approveLoading.value = false
  }
}

async function handleReject() {
  if (!selectedTaskId.value) return
  try {
    const { value } = await ElMessageBox.prompt('璇疯緭鍏ラ┏鍥炲師鍥?, '椹冲洖瀹℃牳浠诲姟', {
      confirmButtonText: '纭椹冲洖',
      cancelButtonText: '鍙栨秷',
      inputPattern: /.+/,
      inputErrorMessage: '椹冲洖鍘熷洜涓嶈兘涓虹┖',
    })
    rejectLoading.value = true
    await rejectPolicyReviewTask(selectedTaskId.value, { reason: value })
    ElMessage.success('瀹℃牳浠诲姟宸查┏鍥?)
    await loadList()
  } catch (error) {
    if (error === 'cancel' || error?.action === 'cancel' || error?.action === 'close') return
    ElMessage.error(error.response?.data?.detail || error.message || '椹冲洖澶辫触')
  } finally {
    rejectLoading.value = false
  }
}

async function handleRefreshAI() {
  if (!selectedTaskId.value) return
  refreshAILoading.value = true
  try {
    const run = await refreshPolicyReviewAI(selectedTaskId.value)
    ElMessage.success('AI 閲嶈窇浠诲姟宸插垱寤?)
    router.push(`/admin/tasks?run_id=${run.run_id}`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || error.message || '鍒涘缓 AI 閲嶈窇浠诲姟澶辫触')
  } finally {
    refreshAILoading.value = false
  }
}

onMounted(loadList)
</script>

<style scoped>
.review-stat-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.review-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}

.filter-item {
  min-width: 180px;
}

.filter-item.keyword {
  min-width: 280px;
}

.review-layout {
  display: grid;
  grid-template-columns: minmax(320px, 0.95fr) minmax(0, 1.85fr);
  gap: 1rem;
}

.review-main {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.85fr);
  gap: 1rem;
}

.detail-panel,
.ai-panel {
  min-width: 0;
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.ai-disclaimer {
  margin-bottom: 1rem;
  padding: 0.85rem 0.95rem;
  border-radius: 16px;
  background: rgba(255, 245, 214, 0.72);
  border: 1px solid rgba(173, 123, 24, 0.18);
  color: #6a4d07;
  line-height: 1.7;
}

.detail-meta-grid,
.draft-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.detail-block {
  padding: 0.95rem 1rem;
  border-radius: 18px;
  background: rgba(248, 245, 236, 0.84);
  border: 1px solid rgba(20, 52, 35, 0.08);
}

.detail-label {
  display: block;
  margin-bottom: 0.45rem;
  font-size: 0.78rem;
  color: #7d877c;
}

.detail-paragraph {
  margin: 0;
  color: #475748;
  line-height: 1.75;
  white-space: pre-wrap;
}

.raw-text-block,
.timeline-wrap {
  margin-top: 1rem;
}

.raw-text {
  margin: 0;
  max-height: 280px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: #304033;
  line-height: 1.7;
}

.draft-form {
  margin-top: 1rem;
}

.full-width {
  width: 100%;
}

.json-textarea :deep(textarea) {
  font-family: Consolas, 'Courier New', monospace;
}

.timeline-card {
  padding: 0.85rem 0.95rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(20, 52, 35, 0.08);
}

.timeline-meta,
.timeline-comment {
  margin: 0.4rem 0 0;
  color: #677667;
  line-height: 1.7;
}

.small {
  font-size: 0.96rem;
}

.risk-list {
  margin: 0;
}

.evidence-list {
  display: grid;
  gap: 0.75rem;
}

.evidence-item {
  padding: 0.85rem 0.95rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(20, 52, 35, 0.08);
}

.evidence-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.evidence-excerpt,
.evidence-relevance {
  margin: 0.55rem 0 0;
  color: #475748;
  line-height: 1.7;
  white-space: pre-wrap;
}

.evidence-relevance {
  color: #667567;
}

.muted-text,
.empty-hint {
  color: #70806f;
}

.empty-hint {
  padding: 2rem 0;
  text-align: center;
}

@media (max-width: 1440px) {
  .review-layout,
  .review-main {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .review-stat-grid,
  .detail-meta-grid,
  .draft-grid {
    grid-template-columns: 1fr;
  }

  .evidence-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
```
