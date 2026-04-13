# 管理端核心前端 UI 界面代码导出

导出时间：2026-04-10

导出范围：管理端路由入口与 `frontend/src/views/admin` 下的核心页面源码（不含测试文件）。

## 文件目录
- `frontend\src\router\index.js`
- `frontend\src\views\admin\AdminLayout.vue`
- `frontend\src\views\admin\AdminLogin.vue`
- `frontend\src\views\admin\AdminDashboard.vue`
- `frontend\src\views\admin\AdminPolicies.vue`
- `frontend\src\views\admin\AdminPolicyReview.vue`
- `frontend\src\views\admin\AdminPolicyNew.vue`
- `frontend\src\views\admin\AdminPolicyEdit.vue`
- `frontend\src\views\admin\AdminPolicyImport.vue`
- `frontend\src\views\admin\AdminTasks.vue`
- `frontend\src\views\admin\AdminAutoCrawler.vue`

## frontend\src\router\index.js

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

## frontend\src\views\admin\AdminLayout.vue

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

## frontend\src\views\admin\AdminLogin.vue

```vue
<template>
  <div class="admin-login-page">
    <div class="admin-login-orb admin-login-orb--one" />
    <div class="admin-login-orb admin-login-orb--two" />

    <div class="admin-login-shell">
      <section class="admin-login-copy">
        <img class="admin-brand-logo" :src="brandLogoWordmarkLight" alt="AgriPolicy AI" />
        <p class="admin-login-kicker">ADMIN CONSOLE</p>
        <h1 class="admin-login-display">杩涘叆鍐滅瓥寰厜鍚庡彴鎺у埗鍙般€?/h1>
        <p class="admin-login-text">
          鍚庡彴璐熻矗缁熶竴绠＄悊鏀跨瓥搴撱€佸鏍镐换鍔°€佽嚜鍔ㄦ姄鍙栧拰椋庡悜鏍囩敓鎴愶紝瑙嗚涓婁笌鍓嶅彴淇濇寔鍚屼竴濂楁斂鍔￠珮绾х豢浣撶郴銆?
        </p>
      </section>

      <section class="login-card">
        <p class="login-card-kicker">SIGN IN</p>
        <h2 class="login-title">绠＄悊鍛樼櫥褰?/h2>
        <p class="login-subtitle">璇蜂娇鐢ㄧ鐞嗗憳璐﹀彿鐧诲綍</p>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="0"
          class="login-form"
          @submit.prevent="handleSubmit"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="鐢ㄦ埛鍚?
              size="large"
              :prefix-icon="User"
              clearable
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="瀵嗙爜"
              size="large"
              :prefix-icon="Lock"
              show-password
              clearable
              @keyup.enter="handleSubmit"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="handleSubmit">
              鐧诲綍
            </el-button>
          </el-form-item>
        </el-form>
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import brandLogoWordmarkLight from '../../assets/brand-logo-wordmark-light.png'

import { loginAdminSession } from '../../services/authSession'

const router = useRouter()
const route = useRoute()
const formRef = ref(null)
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '璇疯緭鍏ョ敤鎴峰悕', trigger: 'blur' }],
  password: [{ required: true, message: '璇疯緭鍏ュ瘑鐮?, trigger: 'blur' }],
}

async function handleSubmit() {
  errorMsg.value = ''
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await loginAdminSession({ username: form.username, password: form.password })
    ElMessage.success(`娆㈣繋锛?{res.username}`)
    await router.replace(route.query.redirect || '/admin')
  } catch (error) {
    errorMsg.value = error.response?.data?.detail || '鐧诲綍澶辫触锛岃妫€鏌ョ敤鎴峰悕鍜屽瘑鐮?
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  display: grid;
  place-items: center;
  padding: 1.2rem;
  background:
    radial-gradient(circle at 16% 16%, rgba(29, 91, 61, 0.14), transparent 24%),
    radial-gradient(circle at 84% 10%, rgba(185, 150, 82, 0.16), transparent 18%),
    linear-gradient(180deg, #edf2eb 0%, #e5ebe3 100%);
}

.admin-login-orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(22px);
  pointer-events: none;
}

.admin-login-orb--one {
  left: -4%;
  top: 8%;
  width: 320px;
  height: 320px;
  background: radial-gradient(circle, rgba(29, 91, 61, 0.16), transparent 66%);
}

.admin-login-orb--two {
  right: -6%;
  bottom: 10%;
  width: 260px;
  height: 260px;
  background: radial-gradient(circle, rgba(185, 150, 82, 0.16), transparent 66%);
}

.admin-login-shell {
  position: relative;
  z-index: 1;
  width: min(980px, 100%);
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(340px, 400px);
  gap: 1rem;
}

.admin-login-copy,
.login-card {
  border-radius: 30px;
  border: 1px solid rgba(18, 39, 27, 0.1);
  box-shadow: var(--nc-shadow-lg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.admin-login-copy {
  padding: 2.4rem 2.2rem;
  background:
    radial-gradient(circle at top right, rgba(185, 150, 82, 0.12), transparent 28%),
    linear-gradient(145deg, rgba(11, 33, 24, 0.95), rgba(29, 91, 61, 0.86));
  color: var(--nc-text-inverse);
}

.admin-login-kicker,
.login-card-kicker {
  margin: 0;
  font-size: 0.74rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  font-weight: 700;
}

.admin-brand-logo {
  display: block;
  height: 34px;
  width: auto;
  max-width: 100%;
  object-fit: contain;
  margin-bottom: 1rem;
}

.admin-login-kicker {
  color: rgba(247, 240, 228, 0.72);
}

.admin-login-display {
  margin: 1rem 0 0;
  font-family: var(--nc-font-serif);
  font-size: clamp(2.2rem, 4vw, 3.6rem);
  line-height: 1.06;
  letter-spacing: -0.04em;
}

.admin-login-text {
  margin: 1rem 0 0;
  max-width: 30rem;
  color: rgba(247, 240, 228, 0.76);
  line-height: 1.85;
}

.login-card {
  padding: 2rem;
  background: rgba(255, 253, 247, 0.9);
}

.login-card-kicker {
  color: var(--nc-accent-gold);
}

.login-title {
  margin: 0.7rem 0 0;
  font-family: var(--nc-font-serif);
  font-size: 2rem;
  color: var(--nc-text-strong);
}

.login-subtitle {
  margin: 0.6rem 0 1.5rem;
  color: var(--nc-text-secondary);
  text-align: left;
}

.submit-btn {
  width: 100%;
}

.error-msg {
  font-size: 0.8125rem;
  color: var(--nc-danger);
  margin: 0.5rem 0 0;
  text-align: center;
}

@media (max-width: 860px) {
  .admin-login-shell {
    grid-template-columns: 1fr;
  }
}
</style>
```

## frontend\src\views\admin\AdminDashboard.vue

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

## frontend\src\views\admin\AdminPolicies.vue

```vue
<template>
  <div class="page-shell admin-policies">
    <section class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">鏀跨瓥搴撶淮鎶?/h3>
        <p class="page-subtitle">
          鏌ョ湅缁撴瀯鍖栨斂绛栥€佹墦寮€璇︽儏銆佹壒閲忓垹闄わ紝骞舵妸琛ユ憳瑕佹敼鎴愬悗鍙颁綔涓氥€?        </p>
      </div>
      <div class="page-actions">
        <el-button type="warning" plain :loading="fillSummaryLoading" @click="handleBatchFillSummary">鎵归噺琛ユ憳瑕?/el-button>
        <el-button
          type="danger"
          plain
          :disabled="selectedRows.length === 0"
          :loading="batchDeleting"
          @click="handleBatchDelete"
        >
          鎵归噺鍒犻櫎锛坽{ selectedRows.length }}锛?        </el-button>
        <el-button type="primary" @click="router.push('/admin/policies/new')">鏂板鏀跨瓥</el-button>
      </div>
    </section>

    <section class="page-panel">
      <div class="table-meta">
        <span class="meta-chip">褰撳墠鎬婚噺 {{ total }}</span>
        <span class="meta-chip">鏈〉 {{ list.length }} 鏉?/span>
        <span class="meta-chip">宸查€?{{ selectedRows.length }} 鏉?/span>
      </div>

      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="list"
        stripe
        class="surface-table"
        @selection-change="onSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="policy_id" label="ID" width="80" />
        <el-table-column prop="title" label="鏍囬" min-width="240" show-overflow-tooltip />
        <el-table-column prop="source" label="鏉ユ簮" width="160" show-overflow-tooltip />
        <el-table-column prop="summary" label="鎽樿" min-width="240" show-overflow-tooltip />
        <el-table-column label="鍘熸枃" width="120" fixed="right">
          <template #default="{ row }">
            <el-link v-if="isUrl(row.raw_text_ref)" type="primary" :href="row.raw_text_ref" target="_blank" rel="noopener">
              鎵撳紑鍘熸枃
            </el-link>
            <span v-else class="muted-text">鏃犻摼鎺?/span>
          </template>
        </el-table-column>
        <el-table-column label="鎿嶄綔" width="170" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openDetail(row)">璇︽儏</el-button>
            <el-button type="primary" link size="small" @click="router.push(`/admin/policies/${row.policy_id}/edit`)">缂栬緫</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">鍒犻櫎</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        class="surface-pagination"
        @current-change="loadList"
        @size-change="loadList"
      />
    </section>

    <el-dialog v-model="detailVisible" title="鏀跨瓥璇︽儏" width="720px" destroy-on-close>
      <div v-if="detailLoading" class="detail-loading">鍔犺浇涓?..</div>
      <div v-else-if="detail" class="detail-shell">
        <div class="detail-block">
          <span class="detail-label">鏍囬</span>
          <strong>{{ detail.title }}</strong>
        </div>
        <div class="detail-grid">
          <div class="detail-block">
            <span class="detail-label">鏉ユ簮</span>
            <strong>{{ detail.source || '鏈～鍐? }}</strong>
          </div>
          <div class="detail-block">
            <span class="detail-label">鍘熸枃閾炬帴</span>
            <el-link v-if="isUrl(detail.raw_text_ref)" type="primary" :href="detail.raw_text_ref" target="_blank" rel="noopener">
              鎵撳紑鍘熸枃
            </el-link>
            <span v-else class="muted-text">鏈厤缃?/span>
          </div>
        </div>
        <div class="detail-block">
          <span class="detail-label">鎽樿</span>
          <p class="detail-paragraph">{{ detail.summary || '鏆傛棤鎽樿' }}</p>
        </div>
        <el-collapse>
          <el-collapse-item title="鏉′欢鏍戠粨鏋? name="tree">
            <pre class="tree-json">{{ formatTree(detail.root_condition) }}</pre>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { batchFillSummary, deletePolicy, getPolicies, getPolicy } from '../../api/client'

const router = useRouter()

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const detailVisible = ref(false)
const detailLoading = ref(false)
const detail = ref(null)
const tableRef = ref(null)
const selectedRows = ref([])
const batchDeleting = ref(false)
const fillSummaryLoading = ref(false)

function isUrl(value) {
  return typeof value === 'string' && (value.startsWith('http://') || value.startsWith('https://'))
}

function formatTree(node) {
  return node ? JSON.stringify(node, null, 2) : '鏆傛棤鏁版嵁'
}

async function openDetail(row) {
  detailVisible.value = true
  detail.value = null
  detailLoading.value = true
  try {
    detail.value = await getPolicy(Number(row.policy_id))
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '鍔犺浇璇︽儏澶辫触')
  } finally {
    detailLoading.value = false
  }
}

function onSelectionChange(rows) {
  selectedRows.value = rows || []
}

async function loadList() {
  loading.value = true
  try {
    const response = await getPolicies({
      offset: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
    })
    list.value = response.items || []
    total.value = response.total ?? 0
    if (list.value.length === 0 && page.value > 1) {
      page.value = 1
      await loadList()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '鍔犺浇鏀跨瓥鍒楄〃澶辫触')
  } finally {
    loading.value = false
  }
}

async function handleBatchFillSummary() {
  try {
    await ElMessageBox.confirm(
      '灏嗗鎽樿涓虹┖鐨勬斂绛栧垱寤哄悗鍙拌ˉ鎽樿浣滀笟锛屾湰娆℃渶澶氬鐞?50 鏉°€傛槸鍚︾户缁紵',
      '鎵归噺琛ユ憳瑕?,
      { confirmButtonText: '寮€濮?, cancelButtonText: '鍙栨秷', type: 'info' },
    )
  } catch {
    return
  }

  fillSummaryLoading.value = true
  try {
    const run = await batchFillSummary({ limit: 50 })
    ElMessage.success('鍚庡彴琛ユ憳瑕佷换鍔″凡鍒涘缓')
    router.push(`/admin/tasks?run_id=${run.run_id}`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '鍒涘缓鎵归噺琛ユ憳瑕佷换鍔″け璐?)
  } finally {
    fillSummaryLoading.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`纭畾鍒犻櫎鈥?{row.title}鈥濆悧锛焋, '纭鍒犻櫎', {
      confirmButtonText: '鍒犻櫎',
      cancelButtonText: '鍙栨秷',
      type: 'warning',
    })
  } catch {
    return
  }

  try {
    await deletePolicy(Number(row.policy_id))
    ElMessage.success('鏀跨瓥宸插垹闄?)
    await loadList()
    await nextTick()
    tableRef.value?.clearSelection?.()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '鍒犻櫎澶辫触')
  }
}

async function handleBatchDelete() {
  if (selectedRows.value.length === 0) return
  try {
    await ElMessageBox.confirm(
      `纭畾鍒犻櫎閫変腑鐨?${selectedRows.value.length} 鏉℃斂绛栧悧锛熸鎿嶄綔涓嶅彲鎭㈠銆俙,
      '鎵归噺鍒犻櫎',
      { confirmButtonText: '鍒犻櫎', cancelButtonText: '鍙栨秷', type: 'warning' },
    )
  } catch {
    return
  }

  batchDeleting.value = true
  let success = 0
  let failed = 0
  for (const row of selectedRows.value) {
    try {
      await deletePolicy(Number(row.policy_id))
      success += 1
    } catch {
      failed += 1
    }
  }
  batchDeleting.value = false

  if (success > 0) {
    ElMessage.success(`宸插垹闄?${success} 鏉℃斂绛?{failed > 0 ? `锛?{failed} 鏉″け璐 : ''}`)
    await loadList()
    await nextTick()
    tableRef.value?.clearSelection?.()
  } else if (failed > 0) {
    ElMessage.error('鎵归噺鍒犻櫎澶辫触')
  }
}

onMounted(loadList)
</script>

<style scoped>
.table-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-bottom: 0.9rem;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  background: rgba(26, 95, 58, 0.08);
  color: #1a5f3a;
  font-size: 0.82rem;
}

.muted-text {
  color: #7d877c;
}

.detail-loading {
  padding: 1rem 0;
  text-align: center;
  color: #6d796c;
}

.detail-shell {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.detail-block {
  padding: 0.95rem 1rem;
  border-radius: 18px;
  background: rgba(248, 245, 236, 0.85);
  border: 1px solid rgba(20, 52, 35, 0.08);
}

.detail-label {
  display: block;
  margin-bottom: 0.4rem;
  font-size: 0.78rem;
  color: #7d877c;
}

.detail-paragraph {
  margin: 0;
  color: #4f5f50;
  line-height: 1.75;
}

.tree-json {
  margin: 0;
  max-height: 320px;
  overflow: auto;
  padding: 0.9rem;
  border-radius: 16px;
  background: rgba(17, 43, 30, 0.06);
  color: #304033;
}

@media (max-width: 780px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
```

## frontend\src\views\admin\AdminPolicyReview.vue

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

## frontend\src\views\admin\AdminPolicyNew.vue

```vue
<template>
  <div class="page-shell">
    <section class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">鏂板缓缁撴瀯鍖栨斂绛?/h3>
        <p class="page-subtitle">
          灏嗗師濮嬫斂绛栨枃鏈彁浜ゅ埌瀹℃牳闃熷垪銆傜郴缁熶細鍦ㄥ悗鍙扮敓鎴愯鍒欒崏绋垮拰 AI 瀹℃牳寤鸿銆?        </p>
      </div>
      <div class="page-actions">
        <el-button @click="router.push('/admin/policies')">杩斿洖鏀跨瓥鍒楄〃</el-button>
      </div>
    </section>

    <section class="page-grid two-column">
      <div class="page-panel">
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="editor-form">
          <el-form-item label="鏀跨瓥鏍囬" prop="title" required>
            <el-input v-model="form.title" placeholder="渚嬪锛?026 骞磋鏂藉啘涓氳ˉ璐寸敵鎶ユ寚寮? clearable />
          </el-form-item>

          <el-form-item label="鏉ユ簮鏈烘瀯" prop="source">
            <el-input v-model="form.source" placeholder="渚嬪锛氭箹鍖楃渷鍐滀笟鍐滄潙鍘? clearable />
          </el-form-item>

          <el-form-item label="鍘熷鏀跨瓥鏂囨湰" prop="raw_text" required>
            <el-input
              v-model="form.raw_text"
              type="textarea"
              :rows="16"
              placeholder="绮樿创鏀跨瓥鍘熸枃鎴栧叧閿潯娆撅紝绯荤粺浼氬湪鍚庡彴鍒涘缓瀹℃牳浣滀笟銆?
            />
          </el-form-item>

          <div class="page-actions">
            <el-button type="primary" :loading="loading" @click="handleSubmit">鍒涘缓鍚庡彴浣滀笟</el-button>
            <el-button @click="router.push('/admin/policies')">鍙栨秷</el-button>
          </div>
        </el-form>
        <p v-if="errorMsg" class="form-feedback error">{{ errorMsg }}</p>
      </div>

      <aside class="page-panel tips-panel">
        <h3 class="panel-title">濉啓寤鸿</h3>
        <ul class="soft-list">
          <li>浼樺厛鎻愪氦鍘熸枃瀹屾暣銆佹潯娆炬竻鏅扮殑鏀跨瓥鏂囨湰锛屽悗鍙扮紪璇戠ǔ瀹氭€ф洿楂樸€?/li>
          <li>鏉ユ簮鏈烘瀯寤鸿淇濈暀锛屼究浜庡悗缁湪瀹℃牳鍙般€佽亰澶╅〉鍜屾礊瀵熼〉灞曠ず銆?/li>
          <li>濡傛灉瑙勫垯鐢熸垚澶辫触锛屽厛妫€鏌ュ師鏂囨槸鍚﹁繃鐭紝鎴栨槸鍚︾己灏戦€傜敤瀵硅薄涓庣敵鎶ユ潯浠躲€?/li>
        </ul>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createPolicyReviewTask } from '../../api/client'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({
  title: '',
  source: '',
  raw_text: '',
})

const rules = {
  title: [{ required: true, message: '璇疯緭鍏ユ斂绛栨爣棰?, trigger: 'blur' }],
  raw_text: [{ required: true, message: '璇疯緭鍏ュ師濮嬫斂绛栨枃鏈?, trigger: 'blur' }],
}

async function handleSubmit() {
  errorMsg.value = ''
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const run = await createPolicyReviewTask({
      source_type: 'manual',
      title: form.title.trim(),
      source: form.source.trim() || undefined,
      raw_text: form.raw_text.trim(),
    })
    ElMessage.success('鍚庡彴浣滀笟宸插垱寤?)
    router.push(`/admin/tasks?run_id=${run.run_id}`)
  } catch (error) {
    errorMsg.value = error.response?.data?.detail || '鍒涘缓瀹℃牳浠诲姟澶辫触锛岃妫€鏌ュ師鏂囧悗閲嶈瘯'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.editor-form {
  display: flex;
  flex-direction: column;
}

.tips-panel {
  align-self: start;
}

.form-feedback {
  margin: 0.9rem 0 0;
  font-size: 0.9rem;
}

.form-feedback.error {
  color: #ba4343;
}
</style>
```

## frontend\src\views\admin\AdminPolicyEdit.vue

```vue
<template>
  <div class="page-shell">
    <section class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">缂栬緫缁撴瀯鍖栨斂绛?/h3>
        <p class="page-subtitle">
          褰撳墠椤甸潰浠呰皟鏁存爣棰樸€佹潵婧愩€佹憳瑕佸拰鍘熸枃寮曠敤淇℃伅銆傛潯浠舵爲淇濇寔鍙灞曠ず锛岄伩鍏嶈鏀圭粨鏋勫寲瑙勫垯缁撴灉銆?        </p>
      </div>
      <div class="page-actions">
        <el-button @click="$router.push('/admin/policies')">杩斿洖鏀跨瓥鍒楄〃</el-button>
      </div>
    </section>

    <div v-if="loadError" class="page-panel">
      <p class="form-feedback error">{{ loadError }}</p>
    </div>

    <section v-else class="page-grid two-column">
      <div class="page-panel">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="editor-form"
        >
          <el-form-item label="鏀跨瓥鏍囬" prop="title" required>
            <el-input v-model="form.title" placeholder="鏀跨瓥鏍囬" clearable />
          </el-form-item>

          <el-form-item label="鏉ユ簮鏈烘瀯" prop="source">
            <el-input v-model="form.source" placeholder="渚嬪锛氭箹鍖楃渷鍐滀笟鍐滄潙鍘? clearable />
          </el-form-item>

          <el-form-item label="鎽樿" prop="summary">
            <el-input v-model="form.summary" type="textarea" :rows="4" placeholder="鏀跨瓥鎽樿" />
          </el-form-item>

          <el-form-item label="鍘熸枃閾炬帴" prop="raw_text_ref">
            <el-input v-model="form.raw_text_ref" placeholder="鍘熺綉椤垫垨鏂囦欢閾炬帴" clearable />
          </el-form-item>

          <div class="page-actions">
            <el-button type="primary" :loading="saving" @click="handleSubmit">淇濆瓨淇敼</el-button>
            <el-button @click="$router.push('/admin/policies')">鍙栨秷</el-button>
          </div>
        </el-form>
        <p v-if="submitError" class="form-feedback error">{{ submitError }}</p>
      </div>

      <aside class="page-panel">
        <h3 class="panel-title">鏉′欢鏍戝彧璇婚瑙?/h3>
        <p class="panel-subtitle">濡傞渶璋冩暣瑙勫垯缁撴灉锛岃鍥炲埌鏂板/缂栬瘧閾捐矾閲嶆柊鐢熸垚锛屼笉鍦ㄦ椤电洿鎺ユ敼鍔ㄦ爲缁撴瀯銆?/p>
        <pre class="tree-json">{{ formatTree(policy?.root_condition) }}</pre>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPolicy, updatePolicy } from '../../api/client'

const route = useRoute()
const router = useRouter()
const policyId = computed(() => Number(route.params.id))
const policy = ref(null)
const loadError = ref('')
const formRef = ref(null)
const saving = ref(false)
const submitError = ref('')

const form = reactive({
  title: '',
  source: '',
  summary: '',
  raw_text_ref: '',
})

const rules = {
  title: [{ required: true, message: '璇疯緭鍏ユ斂绛栨爣棰?, trigger: 'blur' }],
}

function formatTree(node) {
  if (!node) return '鏆傛棤鏁版嵁'
  return JSON.stringify(node, null, 2)
}

async function loadPolicy() {
  loadError.value = ''
  try {
    policy.value = await getPolicy(policyId.value)
    form.title = policy.value.title || ''
    form.source = policy.value.source || ''
    form.summary = policy.value.summary || ''
    form.raw_text_ref = policy.value.raw_text_ref || ''
  } catch (error) {
    loadError.value = error.response?.data?.detail || '鍔犺浇鏀跨瓥澶辫触'
  }
}

async function handleSubmit() {
  submitError.value = ''
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid || !policy.value) return

  saving.value = true
  try {
    await updatePolicy(policyId.value, {
      ...policy.value,
      title: form.title.trim(),
      source: form.source.trim() || undefined,
      summary: form.summary.trim() || undefined,
      raw_text_ref: form.raw_text_ref.trim() || undefined,
    })
    ElMessage.success('鏀跨瓥宸蹭繚瀛?)
    router.push('/admin/policies')
  } catch (error) {
    submitError.value = error.response?.data?.detail || '淇濆瓨澶辫触'
  } finally {
    saving.value = false
  }
}

onMounted(loadPolicy)
</script>

<style scoped>
.editor-form {
  display: flex;
  flex-direction: column;
}

.tree-json {
  margin: 0.9rem 0 0;
  max-height: 420px;
  overflow: auto;
  padding: 0.95rem;
  border-radius: 18px;
  background: rgba(17, 43, 30, 0.06);
  color: #304033;
}

.form-feedback {
  margin: 0.9rem 0 0;
  font-size: 0.9rem;
}

.form-feedback.error {
  color: #ba4343;
}
</style>
```

## frontend\src\views\admin\AdminPolicyImport.vue

```vue
<template>
  <div class="page-shell">
    <section class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">瀵煎叆涓庣埇铏?/h3>
        <p class="page-subtitle">
          灏忔枃浠朵繚鎸佸悓姝ラ瑙堬紱瓒呴檺鏂囦欢鍙浆鍚庡彴瑙ｆ瀽锛屾姄鍙栫粨鏋滃拰瑙ｆ瀽缁撴灉閮借兘鍦ㄤ换鍔′腑蹇冩仮澶嶅苟缁х画瀵煎叆銆?        </p>
      </div>
      <div class="page-actions">
        <el-button plain @click="router.push('/admin/tasks')">鎵撳紑浠诲姟涓績</el-button>
        <el-button @click="router.push('/admin/policies')">杩斿洖鏀跨瓥鍒楄〃</el-button>
      </div>
    </section>

    <section class="page-panel">
      <div class="meta-strip">
        <span class="meta-chip">褰撳墠婧?{{ sourceLabel }}</span>
        <span class="meta-chip">榛樿鎶撳彇椤垫暟 {{ crawlMaxPages }}</span>
        <span class="meta-chip">灏忔枃浠跺悓姝ラ瑙堬紝瓒呴檺鏂囦欢杞悗鍙拌В鏋?/span>
      </div>

      <div v-if="restoredRunId" class="restore-banner">
        <div>
          <strong>宸叉仮澶嶅悗鍙颁换鍔?{{ restoredRunId }}</strong>
          <p class="admin-note">
            褰撳墠椤甸潰灞曠ず鐨勬槸{{ restoredRunLabel }}缁撴灉锛屽彲缁х画鍕鹃€夊悗鍙戣捣鎵归噺瀵煎叆銆?          </p>
        </div>
        <el-button plain @click="router.push(`/admin/tasks?run_id=${restoredRunId}`)">鏌ョ湅浠诲姟璇︽儏</el-button>
      </div>

      <div v-if="uploadFallback.visible" class="restore-banner warning">
        <div>
          <strong>璇ユ枃浠朵笉閫傚悎鍚屾瑙ｆ瀽</strong>
          <p class="admin-note">{{ uploadFallback.message }}</p>
        </div>
        <el-button type="primary" :loading="jobLoading" @click="createParseJob">杞悗鍙拌В鏋?/el-button>
      </div>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="鎵嬪姩鎶撳彇" name="crawl">
          <div class="tab-shell">
            <div class="action-row">
              <el-input-number v-model="crawlMaxPages" :min="1" :max="50" />
              <el-button type="primary" :loading="crawlLoading" @click="runCrawl">鍒涘缓鎶撳彇浠诲姟</el-button>
            </div>
            <p class="admin-note">
              鎵嬪姩鎶撳彇浼氱珛鍗宠繑鍥炲苟鍦ㄤ换鍔′腑蹇冩墽琛屻€傛姄鍙栧畬鎴愬悗锛屽彲浠庝换鍔′腑蹇冭鎯呮垨鏈〉缁х画閫夋嫨缁撴灉骞跺彂璧峰鍏ャ€?            </p>

            <el-table
              v-if="crawlResult.length > 0"
              :data="crawlResult"
              stripe
              class="surface-table"
              max-height="460"
              @selection-change="onCrawlSelectionChange"
            >
              <el-table-column type="selection" width="50" />
              <el-table-column prop="title" label="鏍囬" min-width="260" show-overflow-tooltip />
              <el-table-column prop="source" label="鏉ユ簮" width="180" show-overflow-tooltip />
              <el-table-column label="鍘熸枃" width="110">
                <template #default="{ row }">
                  <el-link v-if="row.url" type="primary" :href="row.url" target="_blank" rel="noopener">鎵撳紑鍘熸枃</el-link>
                  <span v-else class="muted-text">鏃犻摼鎺?/span>
                </template>
              </el-table-column>
              <el-table-column label="鎿嶄綔" width="160">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="batchImport([row])">鍗曠嫭瀵煎叆</el-button>
                  <el-button
                    v-if="restoredRunId"
                    type="primary"
                    link
                    size="small"
                    @click="router.push(`/admin/tasks?run_id=${restoredRunId}`)"
                  >
                    鏌ョ湅浠诲姟
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <div v-if="crawlResult.length > 0" class="page-actions">
              <el-button
                type="primary"
                :loading="importLoading"
                :disabled="crawlSelected.length === 0"
                @click="batchImport(crawlSelected)"
              >
                鎵归噺瀵煎叆閫変腑椤癸紙{{ crawlSelected.length }}锛?              </el-button>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="鏂囦欢涓婁紶" name="upload">
          <div class="tab-shell">
            <div class="action-row wrap">
              <el-upload
                ref="uploadRef"
                :auto-upload="false"
                :limit="1"
                accept=".docx,.pdf"
                :on-change="onFileChange"
              >
                <el-button type="primary" :loading="uploadLoading || jobLoading">閫夋嫨 Word 鎴?PDF</el-button>
              </el-upload>
              <el-input v-model="uploadSource" placeholder="鏉ユ簮鏈烘瀯锛堝彲閫夛級" class="source-input" clearable />
            </div>
            <p class="admin-note">
              灏忔枃浠朵細鐩存帴瑙ｆ瀽骞堕瑙堬紱瓒呴檺鏂囦欢浼氭彁绀鸿浆鍏ュ悗鍙拌В鏋愩€傝В鏋愬畬鎴愬悗锛岄兘鍙互缁х画鍒涘缓鎵归噺瀵煎叆浣滀笟銆?            </p>

            <el-table
              v-if="uploadItems.length > 0"
              :data="uploadItems"
              stripe
              class="surface-table"
              max-height="460"
              @selection-change="onUploadSelectionChange"
            >
              <el-table-column type="selection" width="50" />
              <el-table-column prop="title" label="鏍囬" min-width="280" show-overflow-tooltip />
              <el-table-column prop="source" label="鏉ユ簮" width="180" show-overflow-tooltip />
              <el-table-column label="鍘熸枃闀垮害" width="120">
                <template #default="{ row }">{{ (row.raw_text || '').length }} 瀛?/template>
              </el-table-column>
            </el-table>

            <div v-if="uploadItems.length > 0" class="page-actions">
              <el-button
                type="primary"
                :loading="importLoading"
                :disabled="uploadSelected.length === 0"
                @click="batchImport(uploadSelected)"
              >
                鎵归噺瀵煎叆閫変腑椤癸紙{{ uploadSelected.length }}锛?              </el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  batchImportPolicies,
  createParsePolicyFileJob,
  crawlPolicies,
  getAdminOperationRun,
  getAdminOperationRunItems,
  getCrawlSources,
  parsePolicyFile,
} from '../../api/client'

const router = useRouter()
const route = useRoute()

const activeTab = ref('crawl')
const crawlSources = ref([])
const crawlSourceId = ref('hubei_gov_open')
const crawlMaxPages = ref(20)
const uploadSource = ref('婀栧寳鐪佸啘涓氬啘鏉戝巺')
const uploadLoading = ref(false)
const crawlLoading = ref(false)
const importLoading = ref(false)
const jobLoading = ref(false)
const crawlResult = ref([])
const crawlSelected = ref([])
const uploadRef = ref(null)
const uploadItems = ref([])
const uploadSelected = ref([])
const restoredRunId = ref(null)
const restoredRunType = ref('')
const uploadFallback = ref({
  visible: false,
  message: '',
  file: null,
})

const sourceLabel = computed(() => {
  const primary = crawlSources.value.find((item) => item.id === crawlSourceId.value) || crawlSources.value[0]
  return primary?.source_label || primary?.name || '婀栧寳鐪佸啘涓氬啘鏉戝巺'
})

const restoredRunLabel = computed(() =>
  restoredRunType.value === 'policy_file_parse' ? '鏂囦欢瑙ｆ瀽' : '鎶撳彇',
)

function onCrawlSelectionChange(rows) {
  crawlSelected.value = rows || []
}

function onUploadSelectionChange(rows) {
  uploadSelected.value = rows || []
}

function clearUploadFallback() {
  uploadFallback.value = {
    visible: false,
    message: '',
    file: null,
  }
}

function normalizeImportableItems(items = []) {
  return items
    .map((item) => item.result_json || {})
    .filter((item) => item.title && item.raw_text)
    .map((item) => ({
      title: item.title,
      source: item.source || '婀栧寳鐪佸啘涓氬啘鏉戝巺',
      raw_text: item.raw_text || '',
      url: item.url || undefined,
    }))
}

async function restoreOperationRun(runId) {
  if (!runId) {
    restoredRunId.value = null
    restoredRunType.value = ''
    return
  }
  try {
    const [detail, itemResponse] = await Promise.all([
      getAdminOperationRun(runId),
      getAdminOperationRunItems(runId, { offset: 0, limit: 500 }),
    ])
    const nextItems = normalizeImportableItems(itemResponse.items || [])
    restoredRunId.value = runId
    restoredRunType.value = detail.operation_type || ''

    if (detail.operation_type === 'policy_file_parse') {
      activeTab.value = 'upload'
      uploadItems.value = nextItems
      uploadSelected.value = []
    } else {
      activeTab.value = 'crawl'
      crawlResult.value = nextItems
      crawlSelected.value = []
    }

    if (nextItems.length === 0) {
      ElMessage.warning('璇ュ悗鍙颁换鍔℃殏鏃舵病鏈夊彲鎭㈠鐨勫鍏ョ粨鏋?)
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '鎭㈠鍚庡彴浠诲姟缁撴灉澶辫触')
  }
}

async function runCrawl() {
  crawlLoading.value = true
  try {
    const run = await crawlPolicies({
      source_id: crawlSourceId.value,
      max_pages: crawlMaxPages.value,
    })
    ElMessage.success('鎶撳彇鍚庡彴浣滀笟宸插垱寤?)
    router.push(`/admin/tasks?run_id=${run.run_id}`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '鍒涘缓鎶撳彇浠诲姟澶辫触')
  } finally {
    crawlLoading.value = false
  }
}

async function batchImport(items) {
  if (!items || items.length === 0) return
  importLoading.value = true
  try {
    const run = await batchImportPolicies({
      items: items.map((item) => ({
        title: item.title || '鏈懡鍚嶆斂绛?,
        source: item.source || '婀栧寳鐪佸啘涓氬啘鏉戝巺',
        raw_text: item.raw_text || '',
        url: item.url || undefined,
      })),
    })
    ElMessage.success('鎵归噺瀵煎叆鍚庡彴浣滀笟宸插垱寤?)
    router.push(`/admin/tasks?run_id=${run.run_id}`)
  } catch (error) {
    const detail = error.response?.data?.detail
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg || item.loc?.join('.')).join('锛?)
      : (detail || error.message || '鍒涘缓鎵归噺瀵煎叆浠诲姟澶辫触')
    ElMessage.error(message)
  } finally {
    importLoading.value = false
  }
}

async function createParseJob() {
  if (!uploadFallback.value.file) return
  jobLoading.value = true
  try {
    const run = await createParsePolicyFileJob(uploadFallback.value.file, uploadSource.value || '婀栧寳鐪佸啘涓氬啘鏉戝巺')
    clearUploadFallback()
    ElMessage.success('鏂囦欢瑙ｆ瀽鍚庡彴浣滀笟宸插垱寤?)
    router.push(`/admin/tasks?run_id=${run.run_id}`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '鍒涘缓鏂囦欢瑙ｆ瀽浠诲姟澶辫触')
  } finally {
    jobLoading.value = false
  }
}

function canFallbackToAsync(error) {
  const detail = error?.response?.data?.detail || ''
  return [408, 413].includes(error?.response?.status) && typeof detail === 'string' && detail.includes('鍚庡彴瑙ｆ瀽')
}

async function onFileChange(file) {
  if (!file?.raw) return
  clearUploadFallback()
  const name = (file.name || '').toLowerCase()
  if (!name.endsWith('.docx') && !name.endsWith('.pdf')) {
    ElMessage.warning('浠呮敮鎸?.docx 鎴?.pdf 鏂囦欢')
    return
  }
  uploadLoading.value = true
  try {
    const list = await parsePolicyFile(file.raw, uploadSource.value || '婀栧寳鐪佸啘涓氬啘鏉戝巺')
    uploadItems.value = list || []
    uploadSelected.value = []
    restoredRunId.value = null
    restoredRunType.value = ''
    if (uploadItems.value.length === 0) {
      ElMessage.warning('鏈兘浠庢枃浠朵腑鎻愬彇鍒版湁鏁堟鏂?)
    } else {
      ElMessage.success('鏂囦欢瑙ｆ瀽瀹屾垚锛屽彲缁х画鍒涘缓瀵煎叆浠诲姟')
    }
  } catch (error) {
    if (canFallbackToAsync(error)) {
      uploadFallback.value = {
        visible: true,
        message: error.response?.data?.detail || '璇ユ枃浠惰秴鍑哄悓姝ヨВ鏋愰檺鍒讹紝璇锋敼鐢ㄥ悗鍙拌В鏋愩€?,
        file: file.raw,
      }
      uploadItems.value = []
      uploadSelected.value = []
      ElMessage.warning('璇ユ枃浠跺凡瓒呭嚭鍚屾瑙ｆ瀽闄愬埗锛屽彲杞悗鍙拌В鏋?)
      return
    }
    ElMessage.error(error.response?.data?.detail || error.message || '瑙ｆ瀽鏂囦欢澶辫触')
  } finally {
    uploadLoading.value = false
  }
}

watch(
  () => route.query.run_id || route.query.crawl_run_id,
  async (value) => {
    const runId = value ? Number(value) : null
    if (runId) {
      await restoreOperationRun(runId)
    }
  },
)

onMounted(async () => {
  try {
    crawlSources.value = await getCrawlSources()
    if (crawlSources.value.length > 0) {
      crawlSourceId.value = crawlSources.value[0].id
      if (!uploadSource.value) {
        uploadSource.value = crawlSources.value[0].source_label || '婀栧寳鐪佸啘涓氬啘鏉戝巺'
      }
    }
  } catch {
    crawlSources.value = [
      {
        id: 'hubei_gov_open',
        name: '婀栧寳鐪佸啘涓氬啘鏉戝巺 - 鏀垮簻淇℃伅鍏紑',
        source_label: '婀栧寳鐪佸啘涓氬啘鏉戝巺',
      },
    ]
    crawlSourceId.value = 'hubei_gov_open'
  }

  const routeRunId = route.query.run_id || route.query.crawl_run_id
  if (routeRunId) {
    await restoreOperationRun(Number(routeRunId))
  }
})
</script>

<style scoped>
.meta-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-bottom: 1rem;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.42rem 0.76rem;
  border-radius: 999px;
  background: rgba(26, 95, 58, 0.08);
  color: #1a5f3a;
  font-size: 0.82rem;
}

.restore-banner {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.95rem 1rem;
  margin-bottom: 1rem;
  border-radius: 18px;
  background: rgba(241, 248, 237, 0.9);
  border: 1px solid rgba(26, 95, 58, 0.12);
}

.restore-banner.warning {
  background: rgba(255, 247, 232, 0.92);
  border-color: rgba(185, 150, 82, 0.18);
}

.tab-shell {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.action-row.wrap {
  flex-wrap: wrap;
}

.source-input {
  max-width: 260px;
}

.muted-text {
  color: #7d877c;
}
</style>
```

## frontend\src\views\admin\AdminTasks.vue

```vue
<template>
  <div class="page-shell admin-tasks">
    <section class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">浠诲姟涓績</h3>
        <p class="page-subtitle">缁熶竴鏌ョ湅浠诲姟鑰楁椂銆佸け璐ュ師鍥犮€侀噸璇曠粨鏋滃拰 OCR 鎴愭湰浠ｇ悊鎸囨爣銆?/p>
      </div>
      <div class="page-actions">
        <el-button plain @click="refreshAll">鍒锋柊</el-button>
      </div>
    </section>

    <section class="page-panel">
      <div class="task-filters">
        <el-select v-model="filters.operation_type" clearable placeholder="浠诲姟绫诲瀷" class="filter-item" @change="handleFilter">
          <el-option v-for="item in operationOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="filters.status" clearable placeholder="鐘舵€? class="filter-item" @change="handleFilter">
          <el-option label="寰呮墽琛? value="pending" />
          <el-option label="鎵ц涓? value="running" />
          <el-option label="鎴愬姛" value="success" />
          <el-option label="閮ㄥ垎澶辫触" value="partial" />
          <el-option label="澶辫触" value="failed" />
        </el-select>
        <el-select v-model="filters.trigger_source" clearable placeholder="瑙﹀彂鏉ユ簮" class="filter-item" @change="handleFilter">
          <el-option label="鎵嬪姩" value="manual" />
          <el-option label="璋冨害鍣? value="scheduler" />
        </el-select>
        <el-select v-model="filters.window_days" class="filter-item" @change="handleFilter">
          <el-option label="鏈€杩?1 澶? :value="1" />
          <el-option label="鏈€杩?7 澶? :value="7" />
          <el-option label="鏈€杩?30 澶? :value="30" />
          <el-option label="鏈€杩?90 澶? :value="90" />
        </el-select>
        <el-input
          v-model="filters.requested_by"
          clearable
          class="filter-item keyword"
          placeholder="鍙戣捣浜?
          @keyup.enter="handleFilter"
        />
        <el-button type="primary" @click="handleFilter">搴旂敤绛涢€?/el-button>
      </div>

      <div v-loading="summaryLoading" class="summary-grid">
        <article class="metric-card" data-testid="metric-total-runs">
          <span class="metric-label">浠诲姟鎬绘暟</span>
          <strong class="metric-value">{{ summary.total_runs ?? 0 }}</strong>
        </article>
        <article class="metric-card" data-testid="metric-avg-duration">
          <span class="metric-label">骞冲潎鑰楁椂</span>
          <strong class="metric-value">{{ formatDuration(summary.avg_duration_ms) }}</strong>
        </article>
        <article class="metric-card" data-testid="metric-failure-rate">
          <span class="metric-label">澶辫触鐜?/span>
          <strong class="metric-value">{{ formatPercent(summary.failure_rate) }}</strong>
        </article>
        <article class="metric-card" data-testid="metric-retry-success">
          <span class="metric-label">閲嶈瘯鎴愬姛鐜?/span>
          <strong class="metric-value">{{ retrySuccessRate }}</strong>
        </article>
        <article class="metric-card" data-testid="metric-ocr-pages">
          <span class="metric-label">OCR 椤垫暟</span>
          <strong class="metric-value">{{ summary.ocr_cost?.ocr_pages ?? 0 }}</strong>
        </article>
        <article class="metric-card" data-testid="metric-ocr-invocations">
          <span class="metric-label">OCR 璋冪敤娆℃暟</span>
          <strong class="metric-value">{{ summary.ocr_cost?.ocr_invocations ?? 0 }}</strong>
        </article>
      </div>

      <div class="summary-chart-grid">
        <div class="chart-card">
          <div class="chart-head">
            <h4>澶辫触鍘熷洜鍒嗗竷</h4>
            <p>鎸夊師鍥犵爜鑱氬悎鐨勫墠 5 椤?/p>
          </div>
          <div ref="failureChartEl" class="chart-canvas" data-testid="failure-chart"></div>
        </div>
        <div class="chart-card">
          <div class="chart-head">
            <h4>浠诲姟绫诲瀷鑰楁椂</h4>
            <p>褰撳墠鏃堕棿绐楀彛鍐呯殑骞冲潎鑰楁椂</p>
          </div>
          <div ref="durationChartEl" class="chart-canvas" data-testid="duration-chart"></div>
        </div>
      </div>
    </section>

    <section class="page-panel">
      <el-table
        v-loading="listLoading"
        :data="runs"
        row-key="run_id"
        class="surface-table"
        height="420"
        highlight-current-row
        :current-row-key="selectedRunId"
        @current-change="handleSelectRun"
      >
        <el-table-column prop="run_id" label="浠诲姟 ID" width="96" />
        <el-table-column label="浠诲姟绫诲瀷" min-width="180">
          <template #default="{ row }">{{ operationText(row.operation_type) }}</template>
        </el-table-column>
        <el-table-column label="鐘舵€? width="110">
          <template #default="{ row }">
            <el-tag size="small" :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="鏉ユ簮" width="110">
          <template #default="{ row }">{{ triggerSourceText(row.trigger_source) }}</template>
        </el-table-column>
        <el-table-column prop="requested_by" label="鍙戣捣浜? width="120" />
        <el-table-column label="杩涘害" width="170">
          <template #default="{ row }">{{ progressText(row) }}</template>
        </el-table-column>
        <el-table-column label="鍒涘缓鏃堕棿" min-width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        class="surface-pagination"
        @current-change="loadRuns"
        @size-change="loadRuns"
      />
    </section>

    <section class="page-grid two-column">
      <div class="page-panel">
        <div v-if="detailLoading" class="empty-hint">姝ｅ湪鍔犺浇浠诲姟璇︽儏...</div>
        <div v-else-if="!detail" class="empty-hint">璇峰厛浠庡垪琛ㄤ腑閫夋嫨涓€涓换鍔°€?/div>
        <template v-else>
          <div class="panel-head">
            <div>
              <h3 class="panel-title">浠诲姟璇︽儏</h3>
              <p class="panel-subtitle">鏌ョ湅鎵ц鎽樿銆乼elemetry 鎸囨爣鍜屼簨浠舵椂闂寸嚎銆?/p>
            </div>
            <div class="page-actions">
              <el-button
                v-if="detail.retryable"
                type="warning"
                plain
                :loading="retryLoading"
                @click="handleRetry"
              >
                閲嶈瘯浠诲姟
              </el-button>
              <el-button
                v-if="canUseImportableResult"
                type="primary"
                plain
                @click="router.push(`/admin/policies/import?run_id=${detail.run_id}`)"
              >
                瀵煎叆褰撳墠缁撴灉
              </el-button>
            </div>
          </div>

          <div class="detail-grid">
            <div class="detail-block">
              <span class="detail-label">浠诲姟绫诲瀷</span>
              <strong>{{ operationText(detail.operation_type) }}</strong>
            </div>
            <div class="detail-block">
              <span class="detail-label">鐘舵€?/span>
              <el-tag :type="statusType(detail.status)" effect="light">{{ statusText(detail.status) }}</el-tag>
            </div>
            <div class="detail-block">
              <span class="detail-label">瑙﹀彂鏉ユ簮</span>
              <strong>{{ triggerSourceText(detail.trigger_source) }}</strong>
            </div>
            <div class="detail-block">
              <span class="detail-label">鍙戣捣浜?/span>
              <strong>{{ detail.requested_by || '绯荤粺' }}</strong>
            </div>
            <div class="detail-block">
              <span class="detail-label">鍒涘缓鏃堕棿</span>
              <strong>{{ formatTime(detail.created_at) }}</strong>
            </div>
            <div class="detail-block">
              <span class="detail-label">寮€濮嬫椂闂?/span>
              <strong>{{ formatTime(detail.started_at) }}</strong>
            </div>
            <div class="detail-block">
              <span class="detail-label">缁撴潫鏃堕棿</span>
              <strong>{{ formatTime(detail.finished_at) }}</strong>
            </div>
            <div class="detail-block">
              <span class="detail-label">杩涘害</span>
              <strong>{{ progressText(detail) }}</strong>
            </div>
          </div>

          <div class="telemetry-grid" data-testid="telemetry-summary">
            <article class="detail-block">
              <span class="detail-label">鎵ц鑰楁椂</span>
              <strong>{{ formatDuration(telemetry.duration_ms) }}</strong>
            </article>
            <article class="detail-block">
              <span class="detail-label">Telemetry 浜嬩欢鏁?/span>
              <strong>{{ telemetry.event_count ?? 0 }}</strong>
            </article>
            <article class="detail-block">
              <span class="detail-label">OCR 椤垫暟</span>
              <strong>{{ telemetry.ocr_pages ?? 0 }}</strong>
            </article>
            <article class="detail-block">
              <span class="detail-label">OCR 璋冪敤娆℃暟</span>
              <strong>{{ telemetry.ocr_invocations ?? 0 }}</strong>
            </article>
            <article class="detail-block">
              <span class="detail-label">閲嶈瘯鏉ユ簮浠诲姟</span>
              <strong>{{ telemetry.retry_of_run_id ? `#${telemetry.retry_of_run_id}` : '鏃? }}</strong>
            </article>
            <article class="detail-block">
              <span class="detail-label">鏈€杩戜竴娆￠噸璇曠姸鎬?/span>
              <strong>{{ telemetry.latest_retry_status ? statusText(telemetry.latest_retry_status) : '鏃? }}</strong>
            </article>
          </div>

          <div class="detail-block detail-stack">
            <span class="detail-label">鎵ц鎽樿</span>
            <p class="detail-paragraph">{{ detail.summary_message || '鏆傛棤鎵ц鎽樿銆? }}</p>
          </div>

          <div v-if="detail.error_summary" class="detail-block detail-stack error-block">
            <span class="detail-label">閿欒鎽樿</span>
            <pre class="summary-box">{{ detail.error_summary }}</pre>
          </div>

          <div class="detail-block detail-stack">
            <span class="detail-label">澶辫触鍘熷洜</span>
            <div v-if="telemetry.failure_reasons?.length" class="reason-list">
              <span v-for="reason in telemetry.failure_reasons" :key="reason.reason_code" class="reason-chip">
                {{ reason.reason_label }} x {{ reason.count }}
              </span>
            </div>
            <p v-else class="detail-paragraph">褰撳墠浠诲姟鏆傛棤鑱氬悎澶辫触鍘熷洜銆?/p>
          </div>

          <div class="detail-block detail-stack">
            <span class="detail-label">Telemetry 鏃堕棿绾?/span>
            <div v-if="telemetry.events?.length" class="event-list" data-testid="telemetry-events">
              <article v-for="event in telemetry.events" :key="event.id" class="event-card">
                <div class="event-head">
                  <strong>{{ event.event_name }}</strong>
                  <el-tag size="small" :type="eventStatusType(event.status)" effect="light">{{ event.status }}</el-tag>
                </div>
                <p class="event-meta">
                  {{ formatTime(event.occurred_at) }}
                  <span v-if="event.duration_ms != null"> | {{ formatDuration(event.duration_ms) }}</span>
                  <span v-if="event.reason_label"> | {{ event.reason_label }}</span>
                </p>
                <p v-if="event.reason_message" class="event-message">{{ event.reason_message }}</p>
                <pre v-if="hasRenderableItemJson(event.metadata_json)" class="item-json">{{ formatJson(event.metadata_json) }}</pre>
              </article>
            </div>
            <p v-else class="detail-paragraph">褰撳墠浠诲姟鏆傛棤 telemetry 浜嬩欢銆?/p>
          </div>

          <div class="detail-block detail-stack">
            <span class="detail-label">缁撴灉 JSON</span>
            <pre class="summary-box">{{ formatJson(detail.result_json) }}</pre>
          </div>
        </template>
      </div>

      <div class="page-panel">
        <div class="panel-head">
          <div>
              <h3 class="panel-title">浠诲姟鏄庣粏</h3>
              <p class="panel-subtitle">鏌ョ湅閫愰」缁撴灉鍜屽鍏ヨ浇鑽枫€?/p>
          </div>
        </div>

        <div v-if="itemLoading" class="empty-hint">姝ｅ湪鍔犺浇浠诲姟鏄庣粏...</div>
        <div v-else-if="!items.length" class="empty-hint">褰撳墠浠诲姟鏆傛棤鏄庣粏銆?/div>
        <div v-else class="item-list">
          <article v-for="item in items" :key="item.id" class="item-card">
            <div class="item-head">
              <strong>{{ item.title || `鏄庣粏 ${item.item_index + 1}` }}</strong>
              <el-tag size="small" :type="item.status === 'success' ? 'success' : 'danger'" effect="light">
                {{ item.status === 'success' ? '鎴愬姛' : '澶辫触' }}
              </el-tag>
            </div>
            <p class="item-meta">搴忓彿 {{ item.item_index + 1 }}</p>
            <p v-if="item.error_message" class="item-error">{{ item.error_message }}</p>
            <pre v-if="hasRenderableItemJson(item.result_json)" class="item-json">{{ formatJson(item.result_json) }}</pre>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import {
  getAdminOperationRun,
  getAdminOperationRunItems,
  getAdminOperationRunTelemetry,
  getAdminOperationRuns,
  getAdminOperationSummary,
  retryAdminOperationRun,
} from '../../api/client'

const router = useRouter()
const route = useRoute()
const POLL_INTERVAL_MS = 5000

const operationOptions = [
  { value: 'policy_review_create', label: '鍒涘缓瀹℃牳浠诲姟' },
  { value: 'policy_review_ai_refresh', label: '閲嶈窇 AI 瀹℃牳' },
  { value: 'policy_batch_import', label: '鎵归噺瀵煎叆瀹℃牳闃熷垪' },
  { value: 'policy_batch_fill_summary', label: '鎵归噺琛ユ憳瑕? },
  { value: 'policy_crawl_manual', label: '鎵嬪姩鎶撳彇鏀跨瓥' },
  { value: 'policy_file_parse', label: '鏂囦欢瑙ｆ瀽' },
  { value: 'compass_generate', label: '鐢熸垚椋庡悜鏍? },
  { value: 'auto_crawler_run', label: '鑷姩鐖櫕' },
]

const emptyTelemetry = () => ({
  event_count: 0,
  duration_ms: null,
  ocr_pages: 0,
  ocr_invocations: 0,
  failure_reasons: [],
  retry_of_run_id: null,
  retried_run_ids: [],
  latest_retry_status: null,
  events: [],
})

const emptySummary = () => ({
  total_runs: 0,
  success_count: 0,
  partial_count: 0,
  failed_count: 0,
  running_count: 0,
  pending_count: 0,
  success_rate: 0,
  failure_rate: 0,
  avg_duration_ms: null,
  p95_duration_ms: null,
  retry_results: { total_retries: 0, succeeded: 0, partial: 0, failed: 0, running: 0, pending: 0 },
  ocr_cost: { ocr_pages: 0, ocr_invocations: 0 },
  failure_reasons: [],
  operation_durations: [],
})

const filters = reactive({
  operation_type: '',
  status: '',
  trigger_source: '',
  requested_by: '',
  window_days: 7,
})

const runs = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const listLoading = ref(false)
const summaryLoading = ref(false)
const detailLoading = ref(false)
const itemLoading = ref(false)
const retryLoading = ref(false)
const selectedRunId = ref(null)
const detail = ref(null)
const items = ref([])
const telemetry = ref(emptyTelemetry())
const summary = ref(emptySummary())
const pollTimer = ref(null)
const failureChartEl = ref(null)
const durationChartEl = ref(null)

let failureChart = null
let durationChart = null

const canUseImportableResult = computed(
  () =>
    ['policy_crawl_manual', 'policy_file_parse'].includes(detail.value?.operation_type) &&
    ['success', 'partial'].includes(detail.value?.status),
)

const retrySuccessRate = computed(() => {
  const retryResults = summary.value?.retry_results || {}
  const totalRetries = Number(retryResults.total_retries || 0)
  if (!totalRetries) return '0%'
  return `${Math.round((Number(retryResults.succeeded || 0) / totalRetries) * 100)}%`
})

function isActiveStatus(status) {
  return status === 'pending' || status === 'running'
}

function operationText(operationType) {
  return operationOptions.find((item) => item.value === operationType)?.label || operationType || '-'
}

function statusText(status) {
  if (status === 'pending') return '寰呮墽琛?
  if (status === 'running') return '鎵ц涓?
  if (status === 'success') return '鎴愬姛'
  if (status === 'partial') return '閮ㄥ垎澶辫触'
  if (status === 'failed') return '澶辫触'
  return '鏈煡'
}

function statusType(status) {
  if (status === 'success') return 'success'
  if (status === 'partial') return 'warning'
  if (status === 'failed') return 'danger'
  if (status === 'running') return 'primary'
  return 'info'
}

function eventStatusType(status) {
  if (status === 'success') return 'success'
  if (status === 'error' || status === 'failed') return 'danger'
  if (status === 'info') return 'primary'
  return 'info'
}

function triggerSourceText(triggerSource) {
  if (triggerSource === 'manual') return '鎵嬪姩'
  if (triggerSource === 'scheduler') return '璋冨害鍣?
  return '-'
}

function progressText(run) {
  const totalValue = Number(run?.progress_total || 0)
  const completedValue = Number(run?.progress_completed || 0)
  const failedValue = Number(run?.progress_failed || 0)
  return `${completedValue}/${totalValue}锛屽け璐?${failedValue}`
}

function formatTime(value) {
  if (!value) return '鏆傛棤'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

function formatJson(value) {
  return JSON.stringify(value || {}, null, 2)
}

function formatPercent(value) {
  return `${Number(value || 0).toFixed(2)}%`
}

function formatDuration(value) {
  if (value == null) return '鏆傛棤'
  const totalMs = Number(value)
  if (!Number.isFinite(totalMs)) return '鏆傛棤'
  if (totalMs < 1000) return `${totalMs} ms`
  if (totalMs < 60000) return `${(totalMs / 1000).toFixed(1)} s`
  return `${(totalMs / 60000).toFixed(1)} min`
}

function hasRenderableItemJson(value) {
  return Boolean(value && Object.keys(value).length > 0)
}

function currentParams() {
  return {
    operation_type: filters.operation_type || undefined,
    status: filters.status || undefined,
    trigger_source: filters.trigger_source || undefined,
    requested_by: filters.requested_by || undefined,
    window_days: filters.window_days,
  }
}

function stopPolling() {
  if (pollTimer.value) {
    window.clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

function disposeCharts() {
  failureChart?.dispose()
  durationChart?.dispose()
  failureChart = null
  durationChart = null
}

function renderFailureChart() {
  if (!failureChartEl.value) return
  if (!failureChart) failureChart = echarts.init(failureChartEl.value)
  const reasons = summary.value.failure_reasons || []
  failureChart.setOption({
    tooltip: { trigger: 'item' },
    series: [
      {
        type: 'pie',
        radius: ['42%', '72%'],
        label: { formatter: '{b}: {c}' },
        data: reasons.map((item) => ({ name: item.reason_label, value: item.count })),
      },
    ],
    graphic: reasons.length
      ? undefined
      : [
          {
            type: 'text',
            left: 'center',
            top: 'middle',
            style: { text: '鏆傛棤澶辫触鏁版嵁', fill: '#70806f', fontSize: 14 },
          },
        ],
  })
}

function renderDurationChart() {
  if (!durationChartEl.value) return
  if (!durationChart) durationChart = echarts.init(durationChartEl.value)
  const durations = summary.value.operation_durations || []
  durationChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      axisLabel: { interval: 0, rotate: 18 },
      data: durations.map((item) => operationText(item.operation_type)),
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter(value) {
          return `${Math.round(value / 1000)}s`
        },
      },
    },
    series: [
      {
        type: 'bar',
        barWidth: 28,
        data: durations.map((item) => item.avg_duration_ms || 0),
      },
    ],
    graphic: durations.length
      ? undefined
      : [
          {
            type: 'text',
            left: 'center',
            top: 'middle',
            style: { text: '鏆傛棤鑰楁椂鏁版嵁', fill: '#70806f', fontSize: 14 },
          },
        ],
  })
}

async function syncCharts() {
  await nextTick()
  renderFailureChart()
  renderDurationChart()
}

async function loadSummary() {
  summaryLoading.value = true
  try {
    summary.value = {
      ...emptySummary(),
      ...(await getAdminOperationSummary(currentParams())),
    }
    await syncCharts()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '鍔犺浇浠诲姟姒傝澶辫触')
  } finally {
    summaryLoading.value = false
  }
}

async function loadRuns() {
  listLoading.value = true
  try {
    const response = await getAdminOperationRuns({
      offset: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      ...currentParams(),
    })
    runs.value = response.items || []
    total.value = response.total || 0

    if (!selectedRunId.value && route.query.run_id) {
      selectedRunId.value = Number(route.query.run_id)
    }

    const hasSelected = runs.value.some((item) => item.run_id === selectedRunId.value)
    if (!hasSelected) {
      selectedRunId.value = runs.value[0]?.run_id ?? null
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '鍔犺浇浠诲姟鍒楄〃澶辫触')
  } finally {
    listLoading.value = false
  }
}

async function loadDetail(runId) {
  if (!runId) {
    detail.value = null
    items.value = []
    telemetry.value = emptyTelemetry()
    stopPolling()
    return
  }

  detailLoading.value = true
  itemLoading.value = true
  try {
    const [detailResponse, itemResponse, telemetryResponse] = await Promise.all([
      getAdminOperationRun(runId),
      getAdminOperationRunItems(runId, { offset: 0, limit: 200 }),
      getAdminOperationRunTelemetry(runId),
    ])
    detail.value = detailResponse
    items.value = itemResponse.items || []
    telemetry.value = {
      ...emptyTelemetry(),
      ...telemetryResponse,
      events: telemetryResponse?.events || [],
      failure_reasons: telemetryResponse?.failure_reasons || [],
      retried_run_ids: telemetryResponse?.retried_run_ids || [],
    }

    if (isActiveStatus(detailResponse.status)) {
      startPolling(runId)
    } else {
      stopPolling()
    }
  } catch (error) {
    stopPolling()
    ElMessage.error(error.response?.data?.detail || '鍔犺浇浠诲姟璇︽儏澶辫触')
  } finally {
    detailLoading.value = false
    itemLoading.value = false
  }
}

function startPolling(runId) {
  stopPolling()
  pollTimer.value = window.setInterval(async () => {
    try {
      await Promise.all([loadSummary(), loadRuns(), loadDetail(runId)])
    } catch {
      stopPolling()
    }
  }, POLL_INTERVAL_MS)
}

function handleSelectRun(row) {
  if (!row?.run_id) return
  selectedRunId.value = row.run_id
  router.replace({ query: { ...route.query, run_id: String(row.run_id) } })
}

async function handleFilter() {
  page.value = 1
  await Promise.all([loadSummary(), loadRuns()])
  await loadDetail(selectedRunId.value)
}

async function refreshAll() {
  await Promise.all([loadSummary(), loadRuns()])
  await loadDetail(selectedRunId.value)
}

async function handleRetry() {
  if (!detail.value?.run_id) return
  retryLoading.value = true
  try {
    const nextRun = await retryAdminOperationRun(detail.value.run_id)
    ElMessage.success('宸插垱寤洪噸璇曚换鍔?)
    selectedRunId.value = nextRun.run_id
    router.replace({ query: { ...route.query, run_id: String(nextRun.run_id) } })
    await Promise.all([loadSummary(), loadRuns()])
    await loadDetail(nextRun.run_id)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '閲嶈瘯浠诲姟鍒涘缓澶辫触')
  } finally {
    retryLoading.value = false
  }
}

watch(
  () => route.query.run_id,
  async (value) => {
    const runId = value ? Number(value) : null
    if (runId && runId !== selectedRunId.value) {
      selectedRunId.value = runId
    }
    await loadDetail(selectedRunId.value)
  },
)

watch(
  summary,
  async () => {
    await syncCharts()
  },
  { deep: true },
)

onMounted(async () => {
  if (route.query.run_id) {
    selectedRunId.value = Number(route.query.run_id)
  }
  await Promise.all([loadSummary(), loadRuns()])
  await loadDetail(selectedRunId.value)
  window.addEventListener('resize', syncCharts)
})

onBeforeUnmount(() => {
  stopPolling()
  disposeCharts()
  window.removeEventListener('resize', syncCharts)
})
</script>

<style scoped>
.task-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.filter-item {
  min-width: 180px;
}

.filter-item.keyword {
  min-width: 220px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0.9rem;
  margin-bottom: 1rem;
}

.metric-card {
  padding: 1rem;
  border-radius: 20px;
  background: linear-gradient(145deg, rgba(248, 245, 236, 0.92), rgba(239, 245, 232, 0.92));
  border: 1px solid rgba(20, 52, 35, 0.08);
}

.metric-label {
  display: block;
  margin-bottom: 0.4rem;
  font-size: 0.8rem;
  color: #70806f;
}

.metric-value {
  font-size: 1.3rem;
  color: #213528;
}

.summary-chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.chart-card {
  padding: 1rem;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(20, 52, 35, 0.08);
}

.chart-head h4,
.chart-head p {
  margin: 0;
}

.chart-head p {
  margin-top: 0.35rem;
  color: #70806f;
  font-size: 0.85rem;
}

.chart-canvas {
  height: 260px;
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.detail-grid,
.telemetry-grid {
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

.detail-stack {
  margin-top: 1rem;
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

.summary-box,
.item-json {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  color: #304033;
  line-height: 1.7;
}

.reason-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.reason-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  background: rgba(20, 52, 35, 0.08);
  color: #304033;
  font-size: 0.82rem;
}

.event-list {
  display: grid;
  gap: 0.75rem;
}

.event-card {
  padding: 0.85rem 0.95rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(20, 52, 35, 0.08);
}

.event-head,
.item-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.event-meta,
.item-meta {
  margin: 0.45rem 0 0;
  color: #7d877c;
}

.event-message,
.item-error {
  margin: 0.55rem 0 0;
  color: #b64242;
  line-height: 1.7;
  white-space: pre-wrap;
}

.error-block {
  background: rgba(255, 245, 245, 0.88);
  border-color: rgba(182, 66, 66, 0.14);
}

.item-list {
  display: grid;
  gap: 0.8rem;
}

.item-card {
  padding: 0.95rem 1rem;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(20, 52, 35, 0.08);
}

.empty-hint {
  color: #70806f;
  padding: 2rem 0;
  text-align: center;
}

@media (max-width: 1200px) {
  .summary-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .summary-grid,
  .summary-chart-grid,
  .detail-grid,
  .telemetry-grid {
    grid-template-columns: 1fr;
  }
}
</style>
```

## frontend\src\views\admin\AdminAutoCrawler.vue

```vue
<template>
  <div class="page-shell">
    <section class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">鑷姩鐖櫕涓庡鏍稿叆闃熼摼璺?/h3>
        <p class="page-subtitle">
          缁熶竴绠＄悊鐪熷疄鏁版嵁婧?<code>hubei_gov_open</code> 鐨勫悓姝ャ€丄I 绛涢€変笌瀹℃牳鍏ラ槦銆傜珛鍗虫墽琛岀幇鍦ㄦ敼涓哄紓姝ヤ换鍔★紝椤甸潰浼氭寔缁睍绀哄綋鍓嶄换鍔＄姸鎬併€?        </p>
      </div>
      <div class="page-actions">
        <el-button plain @click="$router.push('/admin/policies')">鏌ョ湅鏀跨瓥鍒楄〃</el-button>
        <el-button type="primary" :loading="runLoading" @click="runNow">绔嬪嵆鎵ц涓€娆?/el-button>
      </div>
    </section>

    <section class="page-panel">
      <div class="stat-grid">
        <div class="stat-card">
          <span class="stat-label">鍚敤鐘舵€?/span>
          <strong class="stat-value">{{ config.enabled ? '宸插惎鐢? : '鏈惎鐢? }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">缁熶竴鏁版嵁婧?/span>
          <strong class="stat-value source-text">{{ sourceLabel }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">鎵ц闂撮殧</span>
          <strong class="stat-value">{{ config.interval_hours }}h</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">鍗曟鎶撳彇椤垫暟</span>
          <strong class="stat-value">{{ config.max_pages_per_source }}</strong>
        </div>
      </div>
    </section>

    <section class="page-grid two-column">
      <div class="page-panel">
        <div class="panel-head">
          <h3 class="panel-title">鑷姩鎵ц閰嶇疆</h3>
          <p class="panel-subtitle">褰撳墠鍚庡彴鍙繚鐣欎竴涓湡瀹炴簮銆傚巻鍙?source_id 浼氬湪鍚庣鑷姩褰掍竴鍒拌婧愩€?/p>
        </div>

        <el-form label-position="top" class="config-form">
          <el-form-item label="鍚敤鑷姩鐖櫕">
            <el-switch v-model="config.enabled" />
          </el-form-item>

          <el-form-item label="褰撳墠鏁版嵁婧?>
            <div class="source-pill-list">
              <div
                v-for="source in sources"
                :key="source.id"
                class="source-pill"
                :class="{ active: config.source_ids.includes(source.id) }"
              >
                <strong>{{ source.name }}</strong>
                <span>{{ source.id }}</span>
              </div>
            </div>
            <p class="admin-note">
              鍘嗗彶閰嶇疆涓殑 <code>hubei_nyt</code>銆?code>moa</code> 绛夋棫鍊间細鑷姩鏀跺彛鍒板綋鍓嶇湡瀹炴簮銆?            </p>
          </el-form-item>

          <div class="form-split">
            <el-form-item label="鎵ц闂撮殧锛堝皬鏃讹級">
              <el-input-number v-model="config.interval_hours" :min="1" :max="168" />
            </el-form-item>
            <el-form-item label="鍗曟鏈€澶ф姄鍙栭〉鏁?>
              <el-input-number v-model="config.max_pages_per_source" :min="1" :max="50" />
            </el-form-item>
          </div>

          <div class="page-actions">
            <el-button type="primary" :loading="saveLoading" @click="saveConfig">淇濆瓨閰嶇疆</el-button>
          </div>
        </el-form>
      </div>

      <div class="page-grid">
        <section class="page-panel">
          <div class="panel-head">
            <h3 class="panel-title">{{ hasActiveRun ? '褰撳墠浠诲姟' : '鏈€杩戜竴娆″畬鎴愪换鍔? }}</h3>
            <p class="panel-subtitle">
              {{ hasActiveRun ? '寮傛浠诲姟宸插叆闃熸垨姝ｅ湪鎵ц锛岄〉闈細鑷姩鍒锋柊鐘舵€併€? : '鏄剧ず鏈€杩戜竴娆″凡瀹屾垚鐨勮嚜鍔ㄧ埇铏粨鏋溿€? }}
            </p>
          </div>
          <div class="status-box">
            <el-tag :type="statusType(displayRun.status)" effect="light">{{ statusText(displayRun.status) }}</el-tag>
            <p class="admin-note">璇锋眰鏃堕棿锛歿{ formatTime(displayRun.run_at) }}</p>
            <p class="admin-note">寮€濮嬫椂闂达細{{ formatTime(displayRun.started_at) }}</p>
            <p class="admin-note">瀹屾垚鏃堕棿锛歿{ formatTime(displayRun.finished_at) }}</p>
            <p class="admin-note">瑙﹀彂鏉ユ簮锛歿{ triggerSourceText(displayRun.trigger_source) }}</p>
            <p class="admin-note">璇锋眰浜猴細{{ displayRun.requested_by || '绯荤粺' }}</p>
            <ul class="soft-list">
              <li>寰呭鐞嗗師鏂?{{ displayRun.crawled_count || 0 }} 鏉?/li>
              <li>绛涢€夐€氳繃 {{ displayRun.filtered_count || 0 }} 鏉?/li>
              <li>杩涘叆瀹℃牳闃熷垪 {{ displayRun.queued_count || 0 }} 鏉?/li>
              <li>澶辫触 {{ displayRun.failed_count || 0 }} 鏉?/li>
            </ul>
          </div>
        </section>

        <section class="page-panel">
          <div class="panel-head">
            <h3 class="panel-title">婕旂ず楠岃瘉璺緞</h3>
            <p class="panel-subtitle">鐢ㄤ簬璇存槑杩欐潯閾捐矾涓嶆槸鍋囨暟鎹紝鑰屾槸鍙互鍓嶅悗鍙拌仈鍔ㄩ獙璇佺殑鐪熷疄娴佺▼銆?/p>
          </div>
          <ul class="soft-list">
            <li>鍒涘缓浠诲姟鍚庡厛鍦ㄦ湰椤电‘璁ょ姸鎬佷粠鈥滅瓑寰呮墽琛屸€濊繘鍏モ€滄墽琛屼腑鈥濆啀杩涘叆缁堟€併€?/li>
            <li>鍐嶅埌瑙勫垯璐ㄩ噺瀹℃牳鍙扮‘璁ゆ湁鏂颁换鍔¤繘鍏ラ槦鍒楋紝涓?AI 寤鸿宸茬粡鐢熸垚銆?/li>
            <li>瀹℃牳閫氳繃鍚庯紝鍐嶅埌鏀跨瓥鍒楄〃鍜岃亰澶╅〉纭鍓嶅彴鍙互娑堣垂鏂版暟鎹€?/li>
          </ul>
          <pre v-if="displayRun.error_summary" class="summary-box">{{ displayRun.error_summary }}</pre>
        </section>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getActiveAutoCrawlerRun,
  getAutoCrawlerConfig,
  getAutoCrawlerLastRun,
  getAutoCrawlerRun,
  getCrawlSources,
  runAutoCrawlerNow,
  updateAutoCrawlerConfig,
} from '../../api/client'

const POLL_INTERVAL_MS = 5000

const sources = ref([])
const saveLoading = ref(false)
const runLoading = ref(false)
const pollingTimer = ref(null)
const config = reactive({
  enabled: false,
  source_ids: ['hubei_gov_open'],
  interval_hours: 24,
  max_pages_per_source: 20,
})

function createEmptyRun() {
  return {
    run_id: null,
    run_at: null,
    started_at: null,
    finished_at: null,
    status: null,
    trigger_source: null,
    requested_by: null,
    crawled_count: 0,
    filtered_count: 0,
    queued_count: 0,
    failed_count: 0,
    error_summary: '',
  }
}

const activeRun = reactive(createEmptyRun())
const lastRun = reactive(createEmptyRun())

const sourceLabel = computed(() => {
  const primary = sources.value[0]
  return primary?.source_label || primary?.name || '婀栧寳鐪佸啘涓氬啘鏉戝巺'
})

const hasActiveRun = computed(() => Boolean(activeRun.run_id))
const displayRun = computed(() => (hasActiveRun.value ? activeRun : lastRun))

function syncRun(target, data) {
  const next = data || createEmptyRun()
  target.run_id = next.run_id ?? null
  target.run_at = next.run_at ?? null
  target.started_at = next.started_at ?? null
  target.finished_at = next.finished_at ?? null
  target.status = next.status ?? null
  target.trigger_source = next.trigger_source ?? null
  target.requested_by = next.requested_by ?? null
  target.crawled_count = next.crawled_count || 0
  target.filtered_count = next.filtered_count || 0
  target.queued_count = next.queued_count || 0
  target.failed_count = next.failed_count || 0
  target.error_summary = next.error_summary || ''
}

function isActiveStatus(status) {
  return status === 'pending' || status === 'running'
}

function stopPolling() {
  if (pollingTimer.value) {
    window.clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

async function refreshRun(runId) {
  const data = await getAutoCrawlerRun(runId)
  syncRun(activeRun, data)
  if (!isActiveStatus(data?.status)) {
    stopPolling()
    await loadLastRun()
    syncRun(activeRun, null)
  }
}

function startPolling(runId) {
  stopPolling()
  pollingTimer.value = window.setInterval(async () => {
    try {
      await refreshRun(runId)
    } catch (error) {
      stopPolling()
      ElMessage.error(error.response?.data?.detail || '鍒锋柊鑷姩鐖櫕浠诲姟鐘舵€佸け璐?)
    }
  }, POLL_INTERVAL_MS)
}

async function loadSources() {
  try {
    sources.value = await getCrawlSources()
  } catch {
    sources.value = [
      {
        id: 'hubei_gov_open',
        name: '婀栧寳鐪佸啘涓氬啘鏉戝巺 路 鏀垮簻淇℃伅鍏紑',
        source_label: '婀栧寳鐪佸啘涓氬啘鏉戝巺',
      },
    ]
  }
  if (!config.source_ids.length && sources.value.length > 0) {
    config.source_ids = [sources.value[0].id]
  }
}

async function loadConfig() {
  const data = await getAutoCrawlerConfig()
  config.enabled = !!data.enabled
  config.source_ids = Array.isArray(data.source_ids) && data.source_ids.length ? data.source_ids : ['hubei_gov_open']
  config.interval_hours = data.interval_hours || 24
  config.max_pages_per_source = data.max_pages_per_source || 20
}

async function loadLastRun() {
  const data = await getAutoCrawlerLastRun()
  syncRun(lastRun, data)
}

async function restoreRunState() {
  const active = await getActiveAutoCrawlerRun()
  if (active) {
    syncRun(activeRun, active)
    startPolling(active.run_id)
    return
  }
  syncRun(activeRun, null)
  await loadLastRun()
}

async function saveConfig() {
  saveLoading.value = true
  try {
    await updateAutoCrawlerConfig({
      enabled: config.enabled,
      source_ids: config.source_ids,
      interval_hours: config.interval_hours,
      max_pages_per_source: config.max_pages_per_source,
    })
    ElMessage.success('鑷姩鐖櫕閰嶇疆宸蹭繚瀛?)
    await loadConfig()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '淇濆瓨閰嶇疆澶辫触')
  } finally {
    saveLoading.value = false
  }
}

async function runNow() {
  runLoading.value = true
  try {
    const previousRunId = activeRun.run_id
    const data = await runAutoCrawlerNow()
    syncRun(activeRun, data)
    if (data?.run_id) {
      startPolling(data.run_id)
    }
    if (previousRunId && previousRunId === data?.run_id) {
      ElMessage.success('宸叉湁鑷姩鐖櫕浠诲姟鍦ㄦ墽琛岋紝宸叉帴绠″綋鍓嶄换鍔＄姸鎬?)
    } else {
      ElMessage.success(isActiveStatus(data?.status) ? '鑷姩鐖櫕浠诲姟宸插垱寤? : '鑷姩鐖櫕浠诲姟鐘舵€佸凡鍒锋柊')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '鍒涘缓鑷姩鐖櫕浠诲姟澶辫触')
  } finally {
    runLoading.value = false
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
  if (status === 'running') return 'primary'
  if (status === 'pending') return 'info'
  return 'info'
}

function statusText(status) {
  if (status === 'success') return '杩愯鎴愬姛'
  if (status === 'partial') return '閮ㄥ垎鎴愬姛'
  if (status === 'failed') return '杩愯澶辫触'
  if (status === 'running') return '鎵ц涓?
  if (status === 'pending') return '绛夊緟鎵ц'
  return '鏆傛棤璁板綍'
}

function triggerSourceText(triggerSource) {
  if (triggerSource === 'manual') return '绠＄悊鍛樻墜鍔ㄨЕ鍙?
  if (triggerSource === 'scheduler') return '璋冨害鍣ㄨ嚜鍔ㄨЕ鍙?
  return '鏆傛棤璁板綍'
}

onMounted(async () => {
  await Promise.all([loadSources(), loadConfig()])
  await restoreRunState()
})

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<style scoped>
.source-text {
  font-size: 1.05rem;
}

.panel-head {
  margin-bottom: 1rem;
}

.config-form {
  display: flex;
  flex-direction: column;
}

.source-pill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.source-pill {
  min-width: 240px;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.95rem 1rem;
  border-radius: 18px;
  border: 1px solid rgba(20, 52, 35, 0.08);
  background: rgba(255, 255, 255, 0.76);
}

.source-pill.active {
  border-color: rgba(26, 95, 58, 0.2);
  background: rgba(241, 248, 237, 0.9);
}

.source-pill span {
  font-size: 0.82rem;
  color: #74836d;
}

.form-split {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.status-box {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding: 1rem;
  border-radius: 18px;
  border: 1px solid rgba(20, 52, 35, 0.08);
  background: rgba(255, 255, 255, 0.76);
}

.summary-box {
  margin: 0.9rem 0 0;
  padding: 0.9rem;
  border-radius: 16px;
  background: rgba(17, 43, 30, 0.06);
  color: #48574a;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.7;
}

@media (max-width: 780px) {
  .form-split {
    grid-template-columns: 1fr;
  }
}
</style>
```
