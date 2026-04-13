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
          {{ isForbidden ? '切换到用户端入口' : '前往管理员登录' }}
        </el-button>
        <el-button plain size="large" @click="router.push('/')">返回首页</el-button>
      </div>
    </div>
  </div>
  <div v-else class="admin-access admin-access--loading">
    <div class="admin-access__loading">正在恢复管理端会话…</div>
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
  Monitor,
  Opportunity,
} from '@element-plus/icons-vue'
import brandLogoMark from '../../assets/logo_icon.png'
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
  {
    key: 'policies',
    label: '政策管理',
    to: '/admin/policies',
    icon: Document,
    names: ['AdminPolicies', 'AdminPolicyEdit'],
  },
  { key: 'review', label: '规则审核', to: '/admin/policies/review', icon: Opportunity, names: ['AdminPolicyReview'] },
  { key: 'new', label: '新增政策', to: '/admin/policies/new', icon: EditPen, names: ['AdminPolicyNew'] },
  { key: 'import', label: '导入与爬取', to: '/admin/policies/import', icon: FolderOpened, names: ['AdminPolicyImport'] },
  { key: 'tasks', label: '任务中心', to: '/admin/tasks', icon: Files, names: ['AdminTasks'] },
  {
    key: 'crawler',
    label: '全自动爬取',
    to: '/admin/policies/auto-crawler',
    icon: Cpu,
    names: ['AdminAutoCrawler'],
  },
  { key: 'sessions', label: '会话管理', to: '/admin/sessions', icon: Monitor, names: ['AdminSessions'] },
]

const currentTitle = computed(() => route.meta?.title || '管理端')
const currentDescription = computed(
  () => route.meta?.description || '统一管理政策库、原文导入、后台作业和自动任务。',
)
const currentSection = computed(() => route.meta?.section || 'ADMIN')
const isAuthenticated = computed(() => adminSessionStatus.value === 'authenticated')
const isForbidden = computed(() => adminSessionStatus.value === 'forbidden')
const accessTitle = computed(() =>
  isForbidden.value ? '当前账号无权访问管理端' : '管理端会话恢复失败',
)
const accessDescription = computed(() =>
  isForbidden.value
    ? '当前账号缺少进入管理端的权限。你可以切换到普通用户入口，或重新登录其他管理员账号后再试。'
    : adminSessionError.value?.message || '网络异常或服务暂时不可用，当前不会自动把你当作已退出。请稍后重试。',
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
  --nc-shadow-lg: 0 18px 50px rgba(41, 55, 43, 0.12), 0 8px 24px rgba(0, 0, 0, 0.06);
  --nc-font-serif: ui-serif, 'Songti SC', 'Noto Serif SC', 'Source Han Serif SC', serif;
  --nc-text-secondary: #6d796c;
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
  transition:
    background 160ms ease,
    transform 160ms ease,
    color 160ms ease;
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
