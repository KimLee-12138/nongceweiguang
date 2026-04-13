<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { getAdminMe, getUserMe, adminLogoutAll, userLogoutAll } from './services/authSession'
import { authEvents } from './api/client'

const route = useRoute()
const router = useRouter()

const userMe = ref(null)
const adminMe = ref(null)

const isAdminRoute = computed(() => route.path.startsWith('/admin'))
const hideShellTopbar = computed(() => {
  const deepest = route.matched[route.matched.length - 1]
  if (deepest?.meta?.hideLayout) return true
  // 官网风页面自己承载导航与排版节奏，避免与全局 topbar 冲突
  const p = route.path
  return (
    p === '/' ||
    p === '/login' ||
    p === '/register' ||
    p === '/onboarding/profile' ||
    p === '/chat' ||
    p.startsWith('/admin')
  )
})

async function refreshMe() {
  try {
    userMe.value = await getUserMe()
  } catch {
    userMe.value = { authenticated: false }
  }
  try {
    adminMe.value = await getAdminMe()
  } catch {
    adminMe.value = { authenticated: false }
  }
}

async function logout() {
  try {
    if (isAdminRoute.value) {
      await adminLogoutAll()
      ElMessage.success('已退出管理员会话')
      await router.push('/admin/login')
    } else {
      await userLogoutAll()
      ElMessage.success('已退出登录')
      await router.push('/login')
    }
  } finally {
    await refreshMe()
  }
}

onMounted(refreshMe)

function onRefreshFailed(e) {
  const role = e?.detail?.role
  if (role === 'admin') {
    ElMessage.error('管理员登录已失效，请重新登录')
    router.push('/admin/login')
  } else {
    ElMessage.error('登录已失效，请重新登录')
    router.push('/login')
  }
  refreshMe()
}

onMounted(() => {
  authEvents.addEventListener('auth:refresh_failed', onRefreshFailed)
})

onBeforeUnmount(() => {
  authEvents.removeEventListener('auth:refresh_failed', onRefreshFailed)
})
</script>

<template>
  <div class="shell">
    <header v-if="!hideShellTopbar" class="topbar">
      <div class="brand" @click="$router.push('/')">农策微光</div>
      <nav class="nav">
        <a @click.prevent="$router.push('/')">首页</a>
        <a @click.prevent="$router.push('/chat')">聊天工作台</a>
        <a @click.prevent="$router.push('/insights')">洞察</a>
        <a @click.prevent="$router.push('/compass')">风向标</a>
        <a @click.prevent="$router.push('/admin')">管理端</a>
      </nav>
      <div class="session">
        <template v-if="isAdminRoute">
          <span class="muted">管理员：{{ adminMe?.authenticated ? '已登录' : '未登录' }}</span>
        </template>
        <template v-else>
          <span class="muted">用户：{{ userMe?.authenticated ? '已登录' : '未登录' }}</span>
        </template>
        <button class="btn" @click="refreshMe">刷新登录态</button>
        <button class="btn" @click="logout">退出</button>
      </div>
    </header>

    <main class="content" :class="{ 'content-fullbleed': hideShellTopbar }">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.shell {
  min-height: 100vh;
  background: #0b1220;
  color: #e5e7eb;
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  position: sticky;
  top: 0;
  background: rgba(11, 18, 32, 0.92);
  backdrop-filter: blur(8px);
  z-index: 10;
}
.brand {
  font-weight: 700;
  letter-spacing: 0.5px;
  cursor: pointer;
}
.nav {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.nav a {
  color: #cbd5e1;
  text-decoration: none;
  cursor: pointer;
  padding: 6px 8px;
  border-radius: 8px;
}
.nav a:hover {
  background: rgba(255, 255, 255, 0.06);
}
.session {
  display: flex;
  align-items: center;
  gap: 8px;
}
.muted {
  color: #94a3b8;
  font-size: 12px;
}
.btn {
  background: rgba(255, 255, 255, 0.06);
  color: #e5e7eb;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
}
.btn:hover {
  background: rgba(255, 255, 255, 0.1);
}
.content {
  padding: 16px;
  max-width: 1100px;
  margin: 0 auto;
}
.content.content-fullbleed {
  padding: 0;
  max-width: none;
  margin: 0;
}
</style>
