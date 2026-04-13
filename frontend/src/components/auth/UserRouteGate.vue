<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ensureUserSession, userSessionError, userSessionStatus } from '../../services/authSession'

const router = useRouter()
const route = useRoute()
const retryingSession = ref(false)

const isAuthenticated = computed(() => userSessionStatus.value === 'authenticated')
const isForbidden = computed(() => userSessionStatus.value === 'forbidden')
const isUnavailable = computed(() => userSessionStatus.value === 'error')
const gateTitle = computed(() =>
  isForbidden.value ? '当前账号无权访问对话工作台' : '会话恢复失败，请重试'
)
const gateDescription = computed(() =>
  isForbidden.value
    ? '当前账号缺少进入用户对话工作台的权限。你可切换到正确入口，或重新登录其他账号后再试。'
    : userSessionError.value?.message || '网络异常或服务暂时不可用。请稍后重试。'
)

function redirectToLogin() {
  router.replace({ path: '/login', query: { redirect: route.fullPath } })
}

watch(
  () => userSessionStatus.value,
  (status) => {
    if (status === 'anonymous') {
      redirectToLogin()
    }
  }
)

async function retrySessionRecovery() {
  retryingSession.value = true
  try {
    const result = await ensureUserSession({ force: true })
    if (result.status === 'anonymous') {
      redirectToLogin()
    }
  } finally {
    retryingSession.value = false
  }
}

onMounted(async () => {
  await ensureUserSession({ force: true })
})
</script>

<template>
  <slot v-if="isAuthenticated" />
  <div v-else-if="isUnavailable || isForbidden" class="user-route-gate">
    <div class="user-route-gate__orb user-route-gate__orb--one" />
    <div class="user-route-gate__orb user-route-gate__orb--two" />

    <div class="user-route-gate__panel">
      <div class="user-route-gate__copy">
        <p class="user-route-gate__eyebrow">SESSION RECOVERY</p>
        <h1>{{ gateTitle }}</h1>
        <p class="user-route-gate__text">{{ gateDescription }}</p>
      </div>

      <div class="user-route-gate__aside">
        <div class="user-route-gate__note">
          <span class="user-route-gate__note-label">当前处理</span>
          <strong>{{ isForbidden ? '切换到正确入口或账号' : '保留本地会话状态，等待恢复' }}</strong>
        </div>
        <div class="user-route-gate__actions">
          <el-button type="primary" size="large" :loading="retryingSession" @click="retrySessionRecovery">
            重试恢复
          </el-button>
          <el-button size="large" @click="router.push('/login')">前往登录页</el-button>
        </div>
        <button type="button" class="user-route-gate__link" @click="router.push('/')">返回首页</button>
      </div>
    </div>
  </div>
  <div v-else class="user-route-gate user-route-gate--loading">
    <div class="user-route-gate__loading">正在恢复登录状态…</div>
  </div>
</template>

<style scoped>
.user-route-gate {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  display: grid;
  place-items: center;
  padding: 1.2rem;
  background:
    radial-gradient(circle at 18% 18%, rgba(29, 91, 61, 0.14), transparent 24%),
    radial-gradient(circle at 80% 10%, rgba(185, 150, 82, 0.18), transparent 18%),
    linear-gradient(180deg, #edf2eb 0%, #e4ebe2 100%);
}

.user-route-gate--loading {
  background: linear-gradient(180deg, #edf2eb 0%, #e7ede6 100%);
}

.user-route-gate__loading {
  position: relative;
  z-index: 1;
  padding: 1rem 1.25rem;
  border-radius: 999px;
  background: rgba(255, 253, 247, 0.86);
  border: 1px solid rgba(18, 39, 27, 0.08);
  color: #4d534f;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);
}

.user-route-gate__orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(22px);
  pointer-events: none;
}

.user-route-gate__orb--one {
  left: -4%;
  top: 12%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(29, 91, 61, 0.14), transparent 66%);
}

.user-route-gate__orb--two {
  right: -5%;
  bottom: 12%;
  width: 260px;
  height: 260px;
  background: radial-gradient(circle, rgba(185, 150, 82, 0.16), transparent 66%);
}

.user-route-gate__panel {
  position: relative;
  z-index: 1;
  width: min(1040px, 100%);
  padding: 1rem;
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
  gap: 1rem;
  border-radius: 30px;
  border: 1px solid rgba(18, 39, 27, 0.1);
  background: rgba(255, 253, 247, 0.66);
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

.user-route-gate__copy,
.user-route-gate__aside {
  border-radius: 24px;
}

.user-route-gate__copy {
  padding: 2.2rem 2rem;
  background:
    radial-gradient(circle at top right, rgba(185, 150, 82, 0.12), transparent 28%),
    linear-gradient(145deg, rgba(11, 33, 24, 0.96), rgba(29, 91, 61, 0.84));
  color: #f7f0e4;
}

.user-route-gate__eyebrow {
  margin: 0;
  font-size: 0.74rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(247, 240, 228, 0.7);
}

.user-route-gate h1 {
  margin: 1rem 0 0;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(2.2rem, 4vw, 3.7rem);
  line-height: 1.04;
  letter-spacing: -0.04em;
}

.user-route-gate__text {
  margin: 1rem 0 0;
  max-width: 32rem;
  font-size: 1rem;
  line-height: 1.85;
  color: rgba(247, 240, 228, 0.76);
}

.user-route-gate__aside {
  padding: 1.6rem;
  background: rgba(255, 253, 247, 0.84);
  border: 1px solid rgba(18, 39, 27, 0.08);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.user-route-gate__note {
  padding: 1rem 1.05rem;
  border-radius: 18px;
  background: rgba(29, 91, 61, 0.06);
  border: 1px solid rgba(29, 91, 61, 0.08);
}

.user-route-gate__note-label {
  display: block;
  font-size: 0.72rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #6b7280;
}

.user-route-gate__note strong {
  display: block;
  margin-top: 0.4rem;
  color: #111412;
  line-height: 1.55;
}

.user-route-gate__actions {
  display: grid;
  gap: 0.8rem;
  margin-top: 1.5rem;
}

.user-route-gate__link {
  margin-top: 1rem;
  padding: 0;
  border: 0;
  background: transparent;
  color: #4d534f;
  text-decoration: underline;
  cursor: pointer;
}

@media (max-width: 860px) {
  .user-route-gate__panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .user-route-gate {
    padding: 1rem;
  }

  .user-route-gate__copy,
  .user-route-gate__aside {
    padding: 1.4rem 1.2rem;
  }
}
</style>
