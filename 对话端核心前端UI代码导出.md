# 对话端核心前端 UI 代码导出

导出时间：2026-04-11

导出范围：对话端路由入口、页面壳、聊天主界面及其核心 UI 组件源码（不含测试文件、接口层与组合式逻辑文件）。

## 文件目录
- `frontend\src\router\index.js`
- `frontend\src\views\ChatRouteView.vue`
- `frontend\src\views\ChatPage.vue`
- `frontend\src\components\auth\UserRouteGate.vue`
- `frontend\src\components\ChatWindow.vue`
- `frontend\src\components\chat\ChatWorkbenchShell.vue`
- `frontend\src\components\chat\ChatMessagePane.vue`
- `frontend\src\components\chat\ChatComposer.vue`
- `frontend\src\components\chat\SidebarLeft.vue`
- `frontend\src\components\chat\SidebarRight.vue`
- `frontend\src\components\chat\PolicyHealthCard.vue`
- `frontend\src\components\chat\InterpretationCard.vue`
- `frontend\src\components\chat\PolicyRecommendationList.vue`
- `frontend\src\components\chat\ReportDrawer.vue`
- `frontend\src\components\chat\ProfileEditorDialog.vue`
- `frontend\src\components\chat\MatchHistoryDialog.vue`
- `frontend\src\components\common\SafeRichText.vue`

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

## frontend\src\views\ChatRouteView.vue

```vue
<script setup>
import UserRouteGate from '../components/auth/UserRouteGate.vue'
import ChatPage from './ChatPage.vue'
</script>

<template>
  <UserRouteGate>
    <ChatPage />
  </UserRouteGate>
</template>
```

## frontend\src\views\ChatPage.vue

```vue
<script setup>
import ChatWindow from '../components/ChatWindow.vue'
</script>

<template>
  <ChatWindow />
</template>
```

## frontend\src\components\auth\UserRouteGate.vue

```vue
<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ensureUserSession, userSessionError, userSessionStatus } from '../../services/authSession'

const router = useRouter()
const route = useRoute()
const retryingSession = ref(false)

const isAuthenticated = computed(() => userSessionStatus.value === 'authenticated')
const isForbidden = computed(() => userSessionStatus.value === 'forbidden')
const isUnavailable = computed(() => userSessionStatus.value === 'unavailable')
const gateTitle = computed(() =>
  isForbidden.value ? '褰撳墠璐﹀彿鏃犳潈璁块棶鑱婂ぉ宸ヤ綔鍙? : '浼氳瘽鎭㈠澶辫触锛岃閲嶈瘯',
)
const gateDescription = computed(() =>
  isForbidden.value
    ? '褰撳墠璐﹀彿缂哄皯杩涘叆鐢ㄦ埛鑱婂ぉ宸ヤ綔鍙扮殑鏉冮檺銆備綘鍙互鍒囨崲鍒版纭叆鍙ｏ紝鎴栭噸鏂扮櫥褰曞叾浠栬处鍙峰悗鍐嶈瘯銆?
    : userSessionError.value?.message || '缃戠粶寮傚父鎴栨湇鍔℃殏鏃朵笉鍙敤锛屽綋鍓嶄笉浼氳嚜鍔ㄦ妸浣犲綋浣滃凡閫€鍑恒€傝绋嶅悗閲嶈瘯銆?,
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
  },
  { immediate: true },
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
          <span class="user-route-gate__note-label">褰撳墠澶勭悊</span>
          <strong>{{ isForbidden ? '鍒囨崲鍒版纭叆鍙ｆ垨璐﹀彿' : '淇濈暀鏈湴浼氳瘽鎬侊紝绛夊緟鎭㈠' }}</strong>
        </div>
        <div class="user-route-gate__actions">
          <el-button type="primary" size="large" :loading="retryingSession" @click="retrySessionRecovery">
            閲嶈瘯鎭㈠
          </el-button>
          <el-button size="large" @click="router.push(isForbidden ? '/admin/login' : '/login')">
            {{ isForbidden ? '鍒囨崲鍒扮鐞嗙鍏ュ彛' : '鍓嶅線鐧诲綍椤? }}
          </el-button>
        </div>
        <button type="button" class="user-route-gate__link" @click="router.push('/')">杩斿洖棣栭〉</button>
      </div>
    </div>
  </div>
  <div v-else class="user-route-gate user-route-gate--loading">
    <div class="user-route-gate__loading">姝ｅ湪鎭㈠鐧诲綍鐘舵€?..</div>
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
  color: var(--nc-text-secondary);
  box-shadow: var(--nc-shadow-lg);
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
  box-shadow: var(--nc-shadow-lg);
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
  color: var(--nc-text-inverse);
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
  font-family: var(--nc-font-serif);
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
  color: var(--nc-text-muted);
}

.user-route-gate__note strong {
  display: block;
  margin-top: 0.4rem;
  color: var(--nc-text-strong);
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
  color: var(--nc-text-secondary);
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
```

## frontend\src\components\ChatWindow.vue

```vue
<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import {
  getSuggestedPolicies,
  matchProfile,
  getProfileWithHistory,
  getCompassReports,
  getCompassReport,
  getCompassGlossary,
  getCompassOverview,
  getCompassOpportunitySignals,
  getUserMe,
} from '../api/client'
import { useProfileEditor } from '../composables/useProfileEditor'
import { useChatSessions } from '../composables/useChatSessions'
import { usePersistentChatStream } from '../composables/usePersistentChatStream'
import ChatComposer from './chat/ChatComposer.vue'
import ChatMessagePane from './chat/ChatMessagePane.vue'
import ChatWorkbenchShell from './chat/ChatWorkbenchShell.vue'
import ProfileEditorDialog from './chat/ProfileEditorDialog.vue'
import MatchHistoryDialog from './chat/MatchHistoryDialog.vue'
import PolicyHealthCard from './chat/PolicyHealthCard.vue'
import InterpretationCard from './chat/InterpretationCard.vue'
import PolicyRecommendationList from './chat/PolicyRecommendationList.vue'
import ReportDrawer from './chat/ReportDrawer.vue'

const route = useRoute()
const router = useRouter()
const chatSessions = useChatSessions()

// ---------- 农户画像：真实数据（左侧列表与当前选中） ----------
const currentProfile = ref(null) // 当前选中的画像（historyProfiles 中的某一项或 null）

const messages = chatSessions.messages
const currentConversation = chatSessions.currentConversation
const recentConversations = chatSessions.conversations

const quickQuestions = ref([
  '我只有30亩地能报什么补贴？',
  '绿色认证补贴的流程是什么？',
  '滴灌设施改造有补贴吗？',
  '合作社资质怎么办理？',
])

// 政策风向标周报（右侧栏，来自 GET /compass/reports）
const compassReports = ref([])
const compassReportLoading = ref(false)
const reportDetailVisible = ref(false)
const selectedReport = ref(null) // { id, title, category, summary, content, published_at }
const reportDetailLoading = ref(false)
const compassOverview = ref({})
const compassSignals = ref({})

// 智库词典（与风向标同周期，来自 GET /compass/glossary，内容与报告呼应）
const glossary = ref([])

// ---------- 状态 ----------
const inputText = ref('')
const streaming = ref(false)
const streamingContent = ref('')
const reportStreaming = ref(false) // 申报规划报告打字机输出中
const chatMessagePaneRef = ref(null)
const leftPanelVisible = ref(false)
const rightPanelVisible = ref(false)
const isCompactLayout = ref(false)

const matchingPolicyId = ref(null) // 当前正在执行匹配的 policy_id，用于卡片 loading

// 聊天模式：match（政策体检/匹配）| interpret（政策白话解读）
const chatMode = ref('match')

// 大屏/图表点击 -> Chat 的冷启动自动提问：发送完成后清理 URL query 防重复触发
const autoAskClearUrl = ref(false)
const autoAskTriggered = ref(false)

const modeLabel = computed(() => {
  if (chatMode.value === 'match') return '🔍 政策智能匹配'
  if (chatMode.value === 'interpret') return '📖 政策白话解读'
  if (chatMode.value === 'llm') return '🌾 农业大模型（湖北政策限定）'
  return '模式'
})

// 当前“引用预览”政策：用于在输入框上方展示，并在发送时附带 policy_id
const citedPolicy = ref(null) // { id: number | null, title: string }

// “一键白话解读”按钮 loading，防止连点
const oneKeyInterpretLoading = ref(null)

// 匹配历史弹窗
const matchHistoryVisible = ref(false)
const matchHistoryLoading = ref(false)
const matchHistoryData = ref(null) // { profile, match_history }

const {
  historyProfiles,
  profileDialogVisible,
  editingProfileId,
  profileForm,
  profileFormLoading,
  profileSubmitLoading,
  fetchProfiles,
  openProfileDialog,
  submitProfileForm,
} = useProfileEditor({
  currentProfile,
  onProfilesLoaded: () => applyConversationProfile(currentConversation.value),
})

const currentProfileName = computed(() => currentProfile.value?.name ?? '未选择画像')
const currentConversationId = computed(() => currentConversation.value?.id ?? null)
const canClearConversation = computed(() => Boolean(currentConversationId.value) && !streaming.value && !reportStreaming.value && !stopping.value)
const currentModeTone = computed(() => {
  if (chatMode.value === 'match') return '围绕画像做政策适配、门槛体检与申报规划。'
  if (chatMode.value === 'interpret') return '聚焦政策白话解释、适用对象与申报流程。'
  if (chatMode.value === 'llm') return '使用湖北政策限定问答做更开放的追问与分析。'
  return '围绕当前农业政策问题提供辅助分析。'
})
const citedPolicyTitle = computed(() => citedPolicy.value?.title || '')

function getRouteConversationId() {
  const raw = Array.isArray(route.query.conversation_id) ? route.query.conversation_id[0] : route.query.conversation_id
  if (raw == null || raw === '') return null
  const value = Number(raw)
  return Number.isInteger(value) && value > 0 ? value : null
}

async function syncConversationRoute(conversationId = currentConversation.value?.id ?? null) {
  const nextQuery = {}
  if (conversationId != null) nextQuery.conversation_id = String(conversationId)
  try {
    await router.replace({ path: '/chat', query: nextQuery })
  } catch (_) {}
}

function applyConversationDraft(conversation = currentConversation.value) {
  const conversationId = conversation?.id ?? null
  const localDraft = chatSessions.readLocalDraft(conversationId)
  inputText.value = localDraft || conversation?.draftText || ''
}

async function persistCurrentDraft() {
  const text = inputText.value || ''
  chatSessions.writeLocalDraft(text)
  try {
    await chatSessions.flushDraftSync(text)
  } catch (_) {}
}

function applyConversationProfile(conversation = currentConversation.value) {
  const profileId = conversation?.lastProfileId ?? null
  if (profileId == null) return
  const matched = historyProfiles.value.find((item) => Number(item.id) === Number(profileId))
  if (matched) currentProfile.value = matched
}

function formatConversationTime(item) {
  const source = item?.lastMessageAt || item?.updatedAt || item?.createdAt
  if (!source) return ''
  const date = new Date(source)
  if (Number.isNaN(date.getTime())) return ''
  const now = new Date()
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  if (date.getFullYear() === now.getFullYear()) {
    return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' })
  }
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'numeric', day: 'numeric' })
}

async function openConversationById(conversationId, params = {}) {
  const detail = await chatSessions.openConversation(conversationId, { limit: 50, ...params })
  streaming.value = false
  streamingContent.value = ''
  reportStreaming.value = false
  if (Array.isArray(messages.value) && messages.value.some((item) => item.status === 'streaming')) {
    messages.value = messages.value.map((item) =>
      item.status === 'streaming'
        ? {
            ...item,
            status: 'cancelled',
            errorMessage: item.errorMessage || 'interrupted_after_reload',
          }
        : item,
    )
  }
  applyConversationProfile(detail?.conversation)
  applyConversationDraft(detail?.conversation)
  if (detail?.conversation?.lastMode) chatMode.value = detail.conversation.lastMode
  await syncConversationRoute(detail?.conversation?.id ?? conversationId)
  nextTick(scrollChatToBottom)
  return detail
}

async function initializeChatSessions() {
  try {
    const me = await getUserMe()
    chatSessions.setUserId(me?.id ?? null)
  } catch (_) {
    chatSessions.setUserId(null)
  }

  let loadError = null
  for (const delay of [0, 250, 800]) {
    try {
      if (delay > 0) {
        await new Promise((resolve) => window.setTimeout(resolve, delay))
      }
      await chatSessions.loadConversations({ offset: 0, limit: 20 })
      loadError = null
      break
    } catch (error) {
      loadError = error
      console.error('load conversations failed', error)
    }
  }

  if (loadError) {
    ElMessage.warning(loadError?.response?.data?.detail || '历史会话加载失败，请稍后刷新重试')
  }

  const targetConversationId = getRouteConversationId() ?? recentConversations.value[0]?.id ?? null
  if (targetConversationId != null) {
    try {
      await openConversationById(targetConversationId)
      return
    } catch (error) {
      console.error(error)
    }
  }

  currentConversation.value = null
  messages.value = []
  applyConversationDraft(null)
  await syncConversationRoute(null)
}

function isPolicyUrl(s) {
  return typeof s === 'string' && (s.startsWith('http://') || s.startsWith('https://'))
}

/** 根据后端画像对象生成展示用标签（面积、绿色认证、灌溉、类型） */
function profileDisplayTags(profile) {
  if (!profile) return []
  const tags = []
  if (profile.area != null && profile.area !== '') tags.push(`${profile.area}亩`)
  if (profile.green_cert === true) tags.push('绿色认证')
  else if (profile.green_cert === false) tags.push('无绿色认证')
  if (profile.irrigation) tags.push(profile.irrigation)
  if (profile.type) tags.push(profile.type)
  return tags
}

function policyHealthTitle(health) {
  if (!health || health.loading) return '正在生成体检结果'
  if (health.match_status === 'success') return '初步匹配成功'
  if (health.match_status === 'fail') return '未通过关键条件'
  return '潜在资格，仍需补齐条件'
}

function policyHealthEvidenceCount(health) {
  if (!health) return { matched: 0, failedMust: 0, failedShould: 0 }
  return {
    matched: Array.isArray(health.matched_nodes) ? health.matched_nodes.length : 0,
    failedMust: Array.isArray(health.failed_must_nodes) ? health.failed_must_nodes.length : 0,
    failedShould: Array.isArray(health.failed_should_nodes) ? health.failed_should_nodes.length : 0,
  }
}

const FIELD_LABEL_MAP = {
  region: '所在地区',
  type: '申请身份',
  area: '经营面积',
  green_cert: '绿色认证',
  irrigation: '灌溉方式',
  main_crop: '主要种植品种',
  crop_structure: '种植结构',
  land_type: '土地类型',
  facility_type: '设施类型',
  employee_count: '用工人数',
  operating_years: '经营年限',
  has_loan: '贷款情况',
  loan_amount: '贷款金额',
  insurance: '参保情况',
  annual_output: '年产值',
  annual_cost: '年经营成本',
}

const ENUM_VALUE_MAP = {
  hubei: '湖北省',
  farmer: '个人农户',
  agricultural_organization: '农业生产经营组织',
  cooperative: '农民合作社',
  coop: '农民合作社',
  family_farm: '家庭农场',
  enterprise: '农业企业',
  agricultural_enterprise: '农业企业',
  leading_enterprise: '龙头企业',
  service_org: '农业社会化服务组织',
  socialized_service_org: '农业社会化服务组织',
  true: '是',
  false: '否',
}

function friendlyFieldLabel(field, fallbackLabel) {
  if (field && FIELD_LABEL_MAP[field]) return FIELD_LABEL_MAP[field]
  return fallbackLabel || field || '该项条件'
}

function evidenceTitle(node) {
  if (!node) return '该项条件'
  const rawLabel = String(node.label || '').trim()
  if (!rawLabel) return friendlyFieldLabel(node.field)
  if (/^[a-z_]+$/i.test(rawLabel)) return friendlyFieldLabel(node.field, rawLabel)
  return rawLabel
}

function friendlyThresholdValue(field, threshold) {
  if (Array.isArray(threshold)) {
    return threshold.map((item) => friendlyThresholdValue(field, item)).join('、')
  }
  if (typeof threshold === 'boolean') {
    return threshold ? '是' : '否'
  }
  if (threshold == null || threshold === '') return ''
  const normalized = String(threshold).trim()
  if (ENUM_VALUE_MAP[normalized]) return ENUM_VALUE_MAP[normalized]
  return normalized
}

function friendlyRuleDetail(node) {
  if (!node) return ''
  const fieldLabel = friendlyFieldLabel(node.field, node.label)
  const operator = node.operator || ''
  const thresholdText = friendlyThresholdValue(node.field, node.threshold)

  if (!operator && !thresholdText) return fieldLabel

  if (operator === 'in') {
    if (node.field === 'region') return `${fieldLabel}在 ${thresholdText} 范围内即可`
    if (node.field === 'type') return `${fieldLabel}属于 ${thresholdText}`
    return `${fieldLabel}属于 ${thresholdText}`
  }
  if (operator === 'not_in') return `${fieldLabel}不能属于 ${thresholdText}`
  if (operator === '==') return `${fieldLabel}应为 ${thresholdText}`
  if (operator === '!=') return `${fieldLabel}不能为 ${thresholdText}`
  if (operator === '>=') return `${fieldLabel}不低于 ${thresholdText}`
  if (operator === '>') return `${fieldLabel}高于 ${thresholdText}`
  if (operator === '<=') return `${fieldLabel}不高于 ${thresholdText}`
  if (operator === '<') return `${fieldLabel}低于 ${thresholdText}`

  return `${fieldLabel}需满足 ${operator} ${thresholdText}`.trim()
}

function evidenceReason(node) {
  if (!node) return ''
  const fieldLabel = friendlyFieldLabel(node.field, node.label)
  const rawReason = String(node.reason || '').trim()
  if (node.passed) {
    return '根据你当前填写的信息，系统判断你符合这项要求'
  }
  if (!rawReason || rawReason === '字段缺失或值为空') {
    return `你还没有填写“${fieldLabel}”，系统暂时无法判断`
  }
  if (rawReason.includes('不满足条件')) {
    return `根据你当前填写的信息，系统判断你暂时还不符合这项要求`
  }
  return rawReason
}

function evidenceSource(node, health) {
  if (node?.source_label) return node.source_label
  if (health?.source_reference?.source) return `依据：${health.source_reference.source}`
  return '依据：政策原文整理出的结构化条件'
}

function evidenceSummaryText(health) {
  if (!health) return ''
  if (health.evidence_summary) return health.evidence_summary
  const counts = policyHealthEvidenceCount(health)
  const totalChecked = counts.matched + counts.failedMust + counts.failedShould
  if (!totalChecked) return '系统正在结合你的画像信息核验政策条件。'
  return `系统共核验了 ${totalChecked} 项条件，其中 ${counts.matched} 项已符合，${counts.failedMust} 项需要优先补充，${counts.failedShould} 项建议进一步完善。`
}

/** 解读模式卡片：只有当结构化字段有“可用信息”才展示 */
function isInterpretationUseful(h) {
  if (!h) return false
  if (h.loading) return true
  const emptyMarkers = ['无法确定', '无法解读', '暂无', '', '—', '——']
  const a = String(h['适用对象'] ?? '').trim()
  const b = String(h['核心标准'] ?? '').trim()
  const arr = Array.isArray(h['申报流程']) ? h['申报流程'] : []
  const cUseful = arr.some((x) => {
    const s = String(x ?? '').trim()
    return s && !emptyMarkers.includes(s)
  })
  const aUseful = a && !emptyMarkers.includes(a)
  const bUseful = b && !emptyMarkers.includes(b)
  return aUseful || bUseful || cUseful
}

function useQuickQuestion(text) {
  inputText.value = text
}

/** 输入框 Enter：Enter 发送，Shift+Enter 换行 */
function onInputEnter(e) {
  if (e.shiftKey) return
  e.preventDefault()
  sendChatMessage()
}

function setChatMode(cmd) {
  chatMode.value = cmd
}

function syncLayoutMode() {
  isCompactLayout.value = typeof window !== 'undefined' ? window.innerWidth <= 1180 : false
  if (!isCompactLayout.value) {
    leftPanelVisible.value = false
    rightPanelVisible.value = false
  }
}

function openLeftPanel() {
  leftPanelVisible.value = true
}

function openRightPanel() {
  rightPanelVisible.value = true
}

async function handleCreateConversation() {
  if (streaming.value || reportStreaming.value) return
  await persistCurrentDraft()
  currentConversation.value = null
  messages.value = []
  citedPolicy.value = null
  applyConversationDraft(null)
  await syncConversationRoute(null)
  leftPanelVisible.value = false
}

async function handleSwitchConversation(item) {
  if (streaming.value || reportStreaming.value) return
  const conversationId = Number(item?.id)
  if (!conversationId || conversationId === currentConversationId.value) {
    leftPanelVisible.value = false
    return
  }
  await persistCurrentDraft()
  await openConversationById(conversationId)
  leftPanelVisible.value = false
}

async function handleClearConversation() {
  if (!canClearConversation.value) return
  try {
    await ElMessageBox.confirm('清空后当前会话消息和草稿都会移除，但最近会话列表仍会保留该会话壳。是否继续？', '清空当前会话', {
      type: 'warning',
      confirmButtonText: '确认清空',
      cancelButtonText: '取消',
    })
  } catch (_) {
    return
  }

  try {
    await chatSessions.clearCurrentConversation()
    inputText.value = ''
    citedPolicy.value = null
    chatMode.value = currentConversation.value?.lastMode || 'match'
    await syncConversationRoute(currentConversation.value?.id ?? null)
    ElMessage.success('当前会话已清空')
  } catch (error) {
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '清空会话失败')
  }
}

const {
  sendPersistent: sendChatMessage,
  stopPersistent,
  stopping,
} = usePersistentChatStream({
  chatSessions,
  messages,
  currentConversation,
  inputText,
  currentProfile,
  citedPolicy,
  chatMode,
  streaming,
  streamingContent,
  oneKeyInterpretLoading,
  autoAskClearUrl,
  autoAskTriggered,
  scrollChatToBottom,
  syncConversationRoute,
  nextTick,
})

function switchProfile(p) {
  currentProfile.value = p
}

function handleSwitchProfile(p) {
  switchProfile(p)
  if (currentConversation.value?.id) {
    chatSessions.patchCurrentConversation({ last_profile_id: p?.id ?? null }).catch(() => {})
  }
  leftPanelVisible.value = false
}

function handleOpenProfileDialog(profile) {
  leftPanelVisible.value = false
  openProfileDialog(profile)
}

function handleOpenMatchHistory() {
  leftPanelVisible.value = false
  openMatchHistory()
}

async function fetchCompassReports() {
  compassReportLoading.value = true
  try {
    const [list, glossaryList, overview, signals] = await Promise.all([
      getCompassReports(4),
      getCompassGlossary(12),
      getCompassOverview(),
      getCompassOpportunitySignals(),
    ])
    compassReports.value = Array.isArray(list) ? list : []
    glossary.value = Array.isArray(glossaryList) ? glossaryList : []
    compassOverview.value = overview && typeof overview === 'object' ? overview : {}
    compassSignals.value = signals && typeof signals === 'object' ? signals : {}
  } catch (_) {
    compassReports.value = []
    glossary.value = []
    compassOverview.value = {}
    compassSignals.value = {}
  } finally {
    compassReportLoading.value = false
  }
}

function formatCompassDate(isoStr) {
  if (!isoStr) return ''
  try {
    const d = new Date(isoStr)
    return `${d.getMonth() + 1}月${d.getDate()}日`
  } catch (_) {
    return ''
  }
}

async function openReport(reportId) {
  reportDetailLoading.value = true
  reportDetailVisible.value = true
  selectedReport.value = null
  try {
    const report = await getCompassReport(reportId)
    selectedReport.value = report
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '加载报告失败')
  } finally {
    reportDetailLoading.value = false
  }
}

function handleOpenReport(reportId) {
  rightPanelVisible.value = false
  openReport(reportId)
}

function handleOpenCompassPage() {
  rightPanelVisible.value = false
  router.push('/compass')
}

onMounted(async () => {
  syncLayoutMode()
  window.addEventListener('resize', syncLayoutMode)
  await Promise.all([fetchProfiles(), fetchCompassReports()])
  await initializeChatSessions()
  applyConversationProfile(currentConversation.value)

  // 图表点击穿透冷启动：/chat?filter_type=...&filter_value=...
  const q = route?.query || {}
  const filterType = typeof q.filter_type === 'string' ? q.filter_type : null
  const filterValue = typeof q.filter_value === 'string' ? q.filter_value : null

  // 兼容旧参数（如之前的 intent_topic/time_range）
  const intentTopic = typeof q.intent_topic === 'string' ? q.intent_topic : null
  const timeRange = typeof q.time_range === 'string' ? q.time_range : null

  // 若不满足参数条件，直接退出
  let promptText = ''
  if (filterType === 'time_or_audience' && filterValue) {
    const v = filterValue.trim()
    const isQuarter = /^\\d{4}-Q[1-4]$/.test(v) || /Q[1-4]/.test(v)
    if (isQuarter) {
      promptText = `请为我总结 ${v} 关于湖北省农业政策的核心政策导向与重点规定。`
    } else {
      promptText = `请为我总结面向${v}的湖北省农业政策核心要点与申报门槛。`
    }
  } else if (filterType === 'trend_period' && filterValue) {
    const v = filterValue.trim()
    promptText = `请为我总结 ${v} 对应阶段湖北省农业政策的发布趋势、重点方向与值得关注的政策信号。`
  } else if (filterType === 'issuer' && filterValue) {
    const v = filterValue.trim()
    promptText = `请为我梳理由“${v}”发布的湖北农业政策重点，说明主要关注领域、适用对象与申报关注点。`
  } else if (filterType === 'subject' && filterValue) {
    const v = filterValue.trim()
    promptText = `请为我总结面向“${v}”的湖北省农业政策核心支持方向、申报门槛与常见注意事项。`
  } else if (filterType === 'theme' && filterValue) {
    const v = filterValue.trim()
    promptText = `请围绕“${v}”这个方向，为我总结湖北省当前最值得关注的农业政策趋势、适用主体、申报重点和提前准备建议。`
  } else if (filterType === 'prep_signal' && filterValue) {
    const v = filterValue.trim()
    promptText = `请围绕“${v}”这个申报准备事项，为我说明湖北省农业政策中为什么经常要求它、哪些主体最该提前准备、以及具体该准备什么材料。`
  } else if (intentTopic && timeRange) {
    promptText = `请为我总结 ${timeRange} 关于‘${intentTopic}’的核心政策导向与重点规定。`
  }

  if (!promptText) return
  if (autoAskTriggered.value) return
  if ((messages.value || []).length > 0) return
  if (streaming.value) return

  // 强制进入 llm 模式，并模拟“用户自己点发送”
  chatMode.value = 'llm'
  citedPolicy.value = null
  inputText.value = promptText
  autoAskClearUrl.value = true
  autoAskTriggered.value = true

  setTimeout(() => {
    // 防止用户在 300ms 内改动输入框
    if (inputText.value.trim() !== promptText) return
    if ((messages.value || []).length > 0) return
    sendChatMessage()
  }, 300)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', syncLayoutMode)
})

watch(inputText, (value) => {
  chatSessions.scheduleDraftSync(value)
})

watch(
  () => route.query.conversation_id,
  async () => {
    if (streaming.value || reportStreaming.value) return
    const targetConversationId = getRouteConversationId()
    if (targetConversationId == null) return
    if (targetConversationId === currentConversationId.value) return
    try {
      await persistCurrentDraft()
      await openConversationById(targetConversationId)
    } catch (error) {
      console.error(error)
      ElMessage.warning(error?.response?.data?.detail || '会话恢复失败，请稍后重试')
    }
  },
)

/** 换一批：对某条政策推荐消息请求下一批 4 条政策；没有更多时自动从第一批循环 */
async function replacePolicyBatch(msgIndex) {
  const profileId = currentProfile.value?.id
  if (profileId == null) return
  const msg = messages.value[msgIndex]
  const offset = msg.policyOffset ?? 0
  try {
    let list = await getSuggestedPolicies(profileId, { offset, limit: 4 })
    let nextOffset = offset + 4
    if ((list || []).length === 0) {
      // 没有更多了，从第一批重新开始（循环）
      list = await getSuggestedPolicies(profileId, { offset: 0, limit: 4 })
      nextOffset = (list || []).length > 0 ? 4 : 0
      if ((list || []).length > 0) ElMessage.info('已看完所有推荐，已为您重新展示第一批')
      else ElMessage.warning('当前暂无适合的推荐政策')
    }
    messages.value[msgIndex] = {
      ...msg,
      policyCards: list || [],
      policyOffset: nextOffset,
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '换一批失败')
  }
}

/** 对该政策提问：设置引用预览卡片（引用不填充输入框内容） */
function setCitedPolicy(policy) {
  const idRaw = policy?.policy_id ?? policy?.policyId ?? policy?.id ?? null
  const id = idRaw != null ? Number(idRaw) : null
  const rawIdRaw = policy?.raw_id ?? policy?.rawId ?? null
  const raw_id = rawIdRaw != null ? Number(rawIdRaw) : null
  const title = policy?.title || '该政策'
  citedPolicy.value = { id, raw_id, title }
  // 引用只做“提示”，不自动拼接输入框文字
  inputText.value = ''
}
function clearCitedPolicy() {
  citedPolicy.value = null
}

function oneKeyInterpretKey(p) {
  const key = p?.raw_id ?? p?.rawId ?? p?.policy_id ?? p?.policyId ?? p?.id ?? p?.title ?? null
  return key != null ? String(key) : null
}

function buildOneKeyInterpretPrompt(title) {
  const t = title || '该政策'
  return `请为我深度解读《${t}》。输出：适用对象、核心标准、申报流程。`
}

function oneKeyInterpretFromPolicy(p) {
  const key = oneKeyInterpretKey(p)
  if (!key) return
  if (oneKeyInterpretLoading.value != null) return

  oneKeyInterpretLoading.value = key

  // 复用现有引用机制：只写入 citedPolicy（raw_id/policy_id 定位），并静默触发发送
  setCitedPolicy(p)
  chatMode.value = 'interpret'
  inputText.value = buildOneKeyInterpretPrompt(p?.title)
  sendChatMessage()
}

function scrollChatToBottom() {
  nextTick(() => {
    chatMessagePaneRef.value?.scrollToBottom?.()
  })
}

/** 组装测算结果的 Markdown 报告（合规指南结构，无金钱字段） */
function buildMatchReportMarkdown(profileName, title, res) {
  const lines = [
    `根据当前画像 **${profileName}** 与政策「${title}」的匹配结果，生成以下申报规划报告。`,
    '',
    '---',
    '',
    '### 🎯 匹配结论',
    '',
    res.fully_matched
      ? '- **是否符合基本门槛**：是，当前画像满足该政策基本条件。'
      : '- **是否符合基本门槛**：否，存在未满足的必须条件，建议按下方行动清单补齐后再申报。',
    '',
  ]
  if (res.concept_explanations && res.concept_explanations.length > 0) {
    lines.push('### 📖 政策白话翻译', '')
    res.concept_explanations.forEach((item) => {
      const term = item.term || item.term_key || '条件'
      const explanation = item.explanation || item.desc || '详见政策原文。'
      lines.push(`- **${term}**：${explanation}`)
    })
    lines.push('')
  }
  if (res.action_steps && res.action_steps.length > 0) {
    lines.push('### 🛠️ 缺口补齐行动清单', '')
    res.action_steps.forEach((step, i) => {
      lines.push(`- [ ] 第${i + 1}步：${step}`)
    })
    lines.push('')
  }
  if (res.risk_warnings && res.risk_warnings.length > 0) {
    lines.push('### ⚠️ 申报避坑预警', '')
    res.risk_warnings.forEach((w) => {
      lines.push(`- ${w}`)
    })
    lines.push('')
  }
  return lines.join('\n')
}

/** 在聊天流中点击某条政策的「生成 AI 申报规划报告」 */
async function runMatchForPolicyInChat(policy) {
  const profileId = currentProfile.value?.id
  if (profileId == null) {
    ElMessage.warning('请先选择农户画像')
    return
  }
  const pid = Number(policy.policy_id)
  matchingPolicyId.value = pid
  try {
    const res = await matchProfile(profileId, { policy_id: pid, expected_subsidy: 0 })
    const title = policy.title || res.policy_id
    const userPrompt = `我选择对《${title}》生成申报规划`
    const resultContent = buildMatchReportMarkdown(currentProfileName.value, title, res)
    const conversation = await chatSessions.ensureConversation({
      title: userPrompt,
      last_mode: 'match',
      last_profile_id: profileId,
    })
    await syncConversationRoute(conversation.id)
    await chatSessions.patchCurrentConversation({
      draft_text: '',
      last_mode: 'match',
      last_profile_id: profileId,
    })
    chatSessions.writeLocalDraft('', conversation.id)
    inputText.value = ''
    await chatSessions.appendMessagesToCurrentConversation([
      {
        role: 'user',
        status: 'done',
        content: userPrompt,
        mode: 'match',
        profile_id: profileId,
        profile_snapshot_json: currentProfile.value ? { ...currentProfile.value } : {},
        citation_json: { policy_id: pid, title },
      },
      {
        role: 'assistant',
        status: 'done',
        content: resultContent,
        mode: 'match',
        profile_id: profileId,
        profile_snapshot_json: currentProfile.value ? { ...currentProfile.value } : {},
        citation_json: { policy_id: pid, title },
      },
    ])
    chatSessions.loadConversations({ offset: 0, limit: 20 }).catch(() => {})
    nextTick(scrollChatToBottom)
  } catch (e) {
    console.error(e)
    ElMessage.error(e.response?.data?.detail || '匹配请求失败')
  } finally {
    matchingPolicyId.value = null
  }
}

/** 打开匹配历史弹窗（当前画像的匹配记录） */
async function openMatchHistory() {
  const pid = currentProfile.value?.id
  if (pid == null) {
    ElMessage.warning('请先选择农户画像')
    return
  }
  matchHistoryVisible.value = true
  matchHistoryData.value = null
  matchHistoryLoading.value = true
  try {
    matchHistoryData.value = await getProfileWithHistory(pid)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '加载匹配历史失败')
  } finally {
    matchHistoryLoading.value = false
  }
}
</script>

<template>
  <ChatWorkbenchShell
    :is-compact-layout="isCompactLayout"
    :left-panel-visible="leftPanelVisible"
    :right-panel-visible="rightPanelVisible"
    :current-profile="currentProfile"
    :history-profiles="historyProfiles"
    :profile-display-tags="profileDisplayTags"
    :recent-conversations="recentConversations"
    :current-conversation-id="currentConversationId"
    :format-conversation-time="formatConversationTime"
    :current-profile-name="currentProfileName"
    :cited-policy-title="citedPolicyTitle"
    :can-clear-conversation="canClearConversation"
    :mode-label="modeLabel"
    :current-mode-tone="currentModeTone"
    :compass-reports="compassReports"
    :compass-report-loading="compassReportLoading"
    :glossary="glossary"
    :format-compass-date="formatCompassDate"
    :compass-overview="compassOverview"
    :compass-signals="compassSignals"
    @update:left-panel-visible="leftPanelVisible = $event"
    @update:right-panel-visible="rightPanelVisible = $event"
    @open-left-panel="openLeftPanel"
    @open-right-panel="openRightPanel"
    @clear-conversation="handleClearConversation"
    @open-profile-dialog="handleOpenProfileDialog"
    @create-conversation="handleCreateConversation"
    @switch-profile="handleSwitchProfile"
    @switch-conversation="handleSwitchConversation"
    @open-match-history="handleOpenMatchHistory"
    @open-report="handleOpenReport"
    @open-compass-page="handleOpenCompassPage"
  >
    <ChatMessagePane
      ref="chatMessagePaneRef"
      :messages="messages"
      :quick-questions="quickQuestions"
      :streaming="streaming"
      :report-streaming="reportStreaming"
      :streaming-content="streamingContent"
      @use-quick-question="useQuickQuestion"
    >
      <template #assistant-extra="{ msg, index }">
        <PolicyHealthCard
          v-if="msg.policyHealth && !msg.interpretationHealth"
          :health="msg.policyHealth"
          :policy-health-title="policyHealthTitle"
          :policy-health-evidence-count="policyHealthEvidenceCount"
          :evidence-summary-text="evidenceSummaryText"
          :evidence-title="evidenceTitle"
          :evidence-source="evidenceSource"
          :friendly-rule-detail="friendlyRuleDetail"
          :evidence-reason="evidenceReason"
          :is-policy-url="isPolicyUrl"
        />

        <InterpretationCard
          :health="msg.interpretationHealth"
          :is-interpretation-useful="isInterpretationUseful"
        />

        <PolicyRecommendationList
          v-if="msg.relatedPolicies && msg.relatedPolicies.length > 0"
          variant="related"
          :items="msg.relatedPolicies"
          :is-policy-url="isPolicyUrl"
          :one-key-interpret-loading="oneKeyInterpretLoading"
          :one-key-interpret-key="oneKeyInterpretKey"
          @set-cited-policy="setCitedPolicy"
          @one-key-interpret-from-policy="oneKeyInterpretFromPolicy"
        />

        <PolicyRecommendationList
          v-if="msg.policyCards && msg.policyCards.length > 0"
          variant="matchCards"
          :items="msg.policyCards"
          :is-policy-url="isPolicyUrl"
          :matching-policy-id="matchingPolicyId"
          @set-cited-policy="setCitedPolicy"
          @run-match-for-policy-in-chat="runMatchForPolicyInChat"
          @replace-batch="replacePolicyBatch(index)"
        />
      </template>
    </ChatMessagePane>
    <ChatComposer
      v-model="inputText"
      :streaming="streaming"
      :stopping="stopping"
      :cited-policy="citedPolicy"
      :current-profile="currentProfile"
      :current-profile-name="currentProfileName"
      :mode-label="modeLabel"
      @clear-citation="clearCitedPolicy"
      @change-mode="setChatMode"
      @submit-enter="onInputEnter"
      @send="sendChatMessage"
      @stop="stopPersistent"
    />
  </ChatWorkbenchShell>

  <ReportDrawer
    v-model="reportDetailVisible"
    :selected-report="selectedReport"
    :report-detail-loading="reportDetailLoading"
    :format-compass-date="formatCompassDate"
    :compass-overview="compassOverview"
    :compass-signals="compassSignals"
  />

  <ProfileEditorDialog
    v-model="profileDialogVisible"
    v-model:profile-form="profileForm"
    :editing-profile-id="editingProfileId"
    :profile-form-loading="profileFormLoading"
    :profile-submit-loading="profileSubmitLoading"
    @submit="submitProfileForm"
  />

  <MatchHistoryDialog
    v-model="matchHistoryVisible"
    :loading="matchHistoryLoading"
    :data="matchHistoryData"
  />

</template>

<style scoped>
.chat-container {
  flex: 1;
  overflow-y: auto;
  scroll-behavior: smooth;
  padding: 0 2rem;
  min-height: 0;
}
.chat-container::-webkit-scrollbar { width: 6px; }
.chat-container::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 4px; }

/* 空状态 (高级欢迎页) */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-bottom: 10vh;
}
.empty-logo-wrap {
  width: 64px; height: 64px;
  background: white;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  box-shadow: 0 8px 24px rgba(26, 95, 58, 0.08);
  margin-bottom: 1.5rem;
}
.empty-title {
  font-family: var(--nc-font-serif);
  font-size: 2.25rem;
  font-weight: 600;
  color: var(--nc-text);
  margin: 0 0 0.5rem;
  letter-spacing: 2px;
}
.empty-subtitle {
  font-size: 1rem;
  color: var(--nc-text-muted);
  margin: 0 0 3rem;
}
.quick-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  max-width: 640px;
  width: 100%;
}
.quick-card {
  padding: 1.25rem 1.5rem;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255,255,255,0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  font-size: 0.9375rem;
  color: var(--nc-text-secondary);
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.02);
}
.quick-icon { opacity: 0.5; }
.quick-card:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(26, 95, 58, 0.06);
  color: var(--nc-primary);
}

/* 聊天气泡体系 */
.chat-list {
  max-width: 860px;
  margin: 0 auto;
  padding: 2rem 0;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.chat-row {
  display: flex;
  gap: 1rem;
  animation: fadeIn 0.4s ease-out;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.chat-row.user {
  flex-direction: row-reverse;
}
.chat-avatar {
  width: 36px; height: 36px;
  background: var(--nc-primary);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 1.1rem;
  flex-shrink: 0;
}
.chat-bubble-wrap {
  display: flex; flex-direction: column; max-width: 75%;
}
.chat-row.user .chat-bubble-wrap { align-items: flex-end; }

.chat-role {
  font-size: 0.75rem;
  color: var(--nc-text-muted);
  margin-bottom: 0.4rem;
  padding-left: 0.2rem;
}
.chat-bubble {
  padding: 1rem 1.25rem;
  font-size: 0.95rem;
  line-height: 1.7;
}
.chat-row.assistant .chat-bubble {
  background: white;
  color: var(--nc-text);
  border-radius: 2px 16px 16px 16px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.03);
  border: 1px solid rgba(0,0,0,0.02);
}
.chat-row.user .chat-bubble {
  background: var(--nc-primary);
  color: white;
  border-radius: 16px 2px 16px 16px;
  box-shadow: 0 4px 16px var(--nc-primary-light);
}

/* 文本格式精修 */
.chat-content.text { white-space: pre-wrap; }
.chat-content.markdown :deep(p) { margin: 0 0 0.75rem; }
.chat-content.markdown :deep(p:last-child) { margin-bottom: 0; }
.chat-content.markdown :deep(strong) { color: var(--nc-primary); font-weight: 600; }
.chat-content.markdown :deep(ul) { margin: 0.5rem 0; padding-left: 1.5rem; }
.chat-content.markdown :deep(li) { margin-bottom: 0.25rem; }

.asking-hint { color: var(--el-color-primary); font-size: 0.875rem; margin-left: 0.5rem; }
.meta-item { display: flex; flex-direction: column; gap: 0.2rem; }
.meta-label { font-size: 0.7rem; color: var(--nc-text-muted); text-transform: uppercase; }
.meta-value { font-size: 0.9rem; font-weight: 600; color: var(--nc-text); }
.meta-value.highlight { color: #d35400; font-family: var(--nc-font-serif); font-size: 1.1rem;}

.chat-spacer { height: 160px; }

/* ---------- 悬浮输入舱 ---------- */
.input-float-wrap {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 0 2rem 2rem;
  background: linear-gradient(to top, var(--nc-bg) 60%, transparent);
  pointer-events: none;
  display: flex; justify-content: center;
}
.input-container {
  pointer-events: auto;
  width: 100%; max-width: 860px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0,0,0,0.05);
  border-radius: 20px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.06);
  padding: 0.75rem 1rem;
  display: flex; flex-direction: column; gap: 0.5rem;
  transition: all 0.3s;
}
.input-container:focus-within {
  background: white;
  box-shadow: 0 16px 48px rgba(26, 95, 58, 0.1);
  border-color: rgba(26, 95, 58, 0.2);
}
.input-header {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0 0.5rem;
}
.chat-mode-wrap {
  flex: 0 0 auto;
  display: flex;
  justify-content: center;
  pointer-events: auto;
  transition: all 0.25s ease;
}
.chat-mode-segment :deep(.el-radio-button__inner) {
  border-radius: 12px;
  font-weight: 650;
}
.chat-mode-segment {
  transition: all 0.25s ease;
}

.mode-dropdown-btn {
  font-weight: 750;
  border-radius: 12px;
  padding: 0.35rem 0.75rem;
}

.citation-preview-fade-enter-active,
.citation-preview-fade-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}
.citation-preview-fade-enter-from,
.citation-preview-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* 引用预览卡片（Citation Card）：用于替代“把政策标题直接塞进输入框”的粗糙交互 */
.citation-card {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  background: #F7F9FC;
  border: 1px solid rgba(0, 0, 0, 0.02);
  border-left: 3px solid #409EFF;
  border-radius: 4px;
  padding: 8px 12px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  overflow: hidden;
}
.citation-card-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.citation-card-icon {
  flex: 0 0 auto;
  font-size: 14px;
  color: #409EFF;
}
.citation-card-title {
  color: #606266;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
  max-width: 100%;
}
.citation-card-close {
  flex: 0 0 auto;
  border: none;
  background: rgba(0, 0, 0, 0.02);
  color: #909399;
  width: 26px;
  height: 26px;
  border-radius: 999px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  line-height: 1;
  padding: 0;
}
.citation-card-close:hover {
  background: rgba(64, 158, 255, 0.08);
  color: #409EFF;
}

.citation-preview-panel {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  border-radius: 12px;
  padding: 20px;
  background: #F0F7FF;
  border: 1px solid #C6E2FF;
  box-shadow: 0 8px 24px rgba(0,0,0,0.05);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 10px;
  overflow: hidden;
}

.citation-preview-main { flex: 1; min-width: 0; }
.citation-preview-label {
  font-size: 0.78rem;
  color: #2563eb;
  font-weight: 800;
  margin-bottom: 6px;
}
.citation-preview-title {
  font-size: 0.98rem;
  font-weight: 750;
  color: var(--nc-text);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-all;
  max-width: 100%;
}
.citation-preview-meta {
  margin-top: 8px;
  font-size: 0.8rem;
  color: var(--nc-text-secondary);
}
.citation-preview-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}
.citation-preview-link { font-size: 0.8125rem; }
.citation-preview-clear { font-size: 0.8125rem; }
.status-dot { width: 6px; height: 6px; background: #52c41a; border-radius: 50%; box-shadow: 0 0 8px #52c41a; }
.input-hint { font-size: 0.75rem; color: var(--nc-text-secondary); flex: 1; }
.input-hint strong { color: var(--nc-primary); }
.match-btn-inline { font-size: 0.75rem; font-weight: 600; }

.input-box {
  display: flex; gap: 0.5rem; align-items: flex-end;
}
.premium-input :deep(.el-textarea__inner) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  font-size: 0.95rem;
  padding: 0.5rem;
  color: var(--nc-text);
  line-height: 1.5;
}
.send-btn-circle {
  width: 40px; height: 40px; border-radius: 50%;
  box-shadow: 0 4px 12px var(--nc-primary-light);
  margin-bottom: 4px;
}

/* 光标动画 */
.cursor { animation: blink 0.8s step-end infinite; margin-left: 2px; color: var(--nc-primary); font-weight: bold;}
@keyframes blink { 50% { opacity: 0; } }

.chat-container {
  position: relative;
  flex: 1;
  margin-top: 16px;
  border-radius: 30px;
  background:
    radial-gradient(circle at top, rgba(185, 150, 82, 0.08), transparent 32%),
    linear-gradient(180deg, rgba(255, 253, 247, 0.9), rgba(255, 253, 247, 0.72)),
    rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(18, 39, 27, 0.08);
  box-shadow:
    0 22px 52px rgba(18, 41, 29, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  padding: 0 2rem;
  display: flex;
  flex-direction: column;
}

.empty-state {
  position: relative;
  padding: 5rem 0 3.8rem;
}

.empty-state::before {
  content: '';
  position: absolute;
  width: 320px;
  height: 320px;
  background: radial-gradient(circle, rgba(26, 95, 58, 0.06), transparent 68%);
  filter: blur(8px);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.empty-logo-wrap {
  width: 84px;
  height: 84px;
  border-radius: 28px;
  background:
    linear-gradient(135deg, rgba(29, 91, 61, 0.18), rgba(185, 150, 82, 0.18)),
    #fff;
  box-shadow:
    0 18px 36px rgba(29, 91, 61, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.65);
}

.empty-title {
  font-family: var(--nc-font-serif);
  letter-spacing: 0.08em;
}

.empty-subtitle {
  max-width: 520px;
  text-align: center;
  color: rgba(44, 44, 44, 0.62);
  line-height: 1.8;
}

.quick-grid {
  gap: 1rem;
}

.quick-card {
  min-height: 92px;
  border-radius: 20px;
  background:
    linear-gradient(180deg, rgba(255, 253, 247, 0.94), rgba(248, 246, 239, 0.88));
  border: 1px solid rgba(18, 39, 27, 0.06);
  box-shadow: 0 14px 30px rgba(18, 41, 29, 0.05);
}

.chat-list {
  width: min(100%, 1040px);
  max-width: 1040px;
  gap: 1.5rem;
  padding-top: 1.8rem;
  margin: 0 auto;
}

.chat-row {
  gap: 0.85rem;
}

.chat-avatar {
  width: 46px;
  height: 46px;
  border-radius: 16px;
  box-shadow: 0 10px 18px rgba(29, 91, 61, 0.16);
}

.chat-bubble-wrap {
  max-width: min(80%, 780px);
}

.chat-role {
  font-weight: 600;
}

.chat-bubble {
  border-radius: 24px;
}

.chat-row.assistant .chat-bubble {
  background: rgba(255, 253, 247, 0.94);
  border-radius: 10px 24px 24px 24px;
  border: 1px solid rgba(18, 39, 27, 0.05);
  box-shadow: 0 14px 34px rgba(18, 41, 29, 0.05);
}

.chat-row.user .chat-bubble {
  border-radius: 24px 10px 24px 24px;
  background: linear-gradient(135deg, #1d5b3d 0%, #2b6b49 100%);
}

.input-float-wrap {
  position: sticky;
  bottom: 0;
  padding: 1rem 0 1.5rem;
  background: linear-gradient(to top, rgba(230, 235, 228, 0.96) 54%, rgba(230, 235, 228, 0));
}

.input-container {
  max-width: 1040px;
  border-radius: 26px;
  background: rgba(255, 253, 247, 0.9);
  border: 1px solid rgba(18, 39, 27, 0.08);
  box-shadow:
    0 18px 42px rgba(18, 41, 29, 0.09),
    inset 0 1px 0 rgba(255, 255, 255, 0.82);
  padding: 1rem 1rem;
  margin: 0 auto;
}

.input-header {
  min-height: 34px;
}

.mode-dropdown-btn {
  color: var(--nc-primary);
  font-weight: 700;
}

.citation-card {
  border-radius: 14px;
  border-left-width: 4px;
  background: linear-gradient(180deg, #f7faf5, #eff6f1);
}

.premium-input :deep(.el-textarea__inner) {
  min-height: 52px !important;
  font-size: 0.98rem;
}

.send-btn-circle {
  width: 48px;
  height: 48px;
}

@media (max-width: 1180px) {
  .chat-container {
    border-radius: 24px 24px 0 0;
  }
}

@media (max-width: 860px) {
  .chat-container {
    padding: 0 1rem;
  }

  .chat-bubble-wrap {
    max-width: calc(100% - 50px);
  }

  .quick-grid {
    grid-template-columns: 1fr !important;
  }

  .input-float-wrap {
    padding-bottom: 1rem;
  }

  .input-header {
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .chat-mode-wrap {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
```

## frontend\src\components\chat\ChatWorkbenchShell.vue

```vue
<template>
  <el-container class="terminal-layout" direction="horizontal">
    <aside class="terminal-sidebar terminal-sidebar--left">
      <SidebarLeft
        :current-profile="currentProfile"
        :history-profiles="historyProfiles"
        :profile-display-tags="profileDisplayTags"
        :recent-conversations="recentConversations"
        :current-conversation-id="currentConversationId"
        :format-conversation-time="formatConversationTime"
        @open-profile-dialog="$emit('openProfileDialog', $event)"
        @create-conversation="$emit('createConversation')"
        @switch-profile="$emit('switchProfile', $event)"
        @switch-conversation="$emit('switchConversation', $event)"
        @open-match-history="$emit('openMatchHistory')"
      />
    </aside>

    <el-main class="terminal-main">
      <div class="terminal-shell">
        <header class="terminal-header">
          <div class="terminal-header__left">
            <button
              v-if="isCompactLayout"
              type="button"
              class="terminal-icon-btn"
              aria-label="鎵撳紑宸︿晶闈㈡澘"
              @click="$emit('openLeftPanel')"
            >
              <el-icon><Fold /></el-icon>
            </button>

            <div class="terminal-identity">
              <div class="terminal-brand-row">
                <img class="terminal-brand-mark" :src="brandLogoMark" alt="AgriPolicy AI" />
                <span class="terminal-kicker">NC-WORKSPACE</span>
              </div>
              <div class="terminal-title-row">
                <strong class="terminal-title">鏀跨瓥鏅鸿兘宸ヤ綔鍙?/strong>
                <span class="terminal-mode-badge">{{ modeLabel }}</span>
              </div>
              <p class="terminal-subtitle">{{ currentModeTone }}</p>
            </div>
          </div>

          <div class="terminal-header__right">
            <div v-if="currentProfile" class="terminal-context-chip">
              <span class="terminal-context-label">鐢诲儚</span>
              <strong>{{ currentProfileName }}</strong>
            </div>

            <div v-if="citedPolicyTitle" class="terminal-context-chip terminal-context-chip--muted">
              <span class="terminal-context-label">寮曠敤</span>
              <strong>{{ citedPolicyTitle }}</strong>
            </div>

            <button
              v-if="currentConversationId"
              type="button"
              class="terminal-ghost-btn"
              :disabled="!canClearConversation"
              @click="$emit('clearConversation')"
            >
              娓呯┖涓婁笅鏂?
            </button>

            <button
              v-if="isCompactLayout"
              type="button"
              class="terminal-icon-btn"
              aria-label="鎵撳紑鍙充晶闈㈡澘"
              @click="$emit('openRightPanel')"
            >
              <el-icon><Expand /></el-icon>
            </button>
          </div>
        </header>

        <div class="terminal-stage">
          <slot />
        </div>
      </div>
    </el-main>

    <aside class="terminal-sidebar terminal-sidebar--right">
      <SidebarRight
        :compass-reports="compassReports"
        :compass-report-loading="compassReportLoading"
        :glossary="glossary"
        :format-compass-date="formatCompassDate"
        :compass-overview="compassOverview"
        :compass-signals="compassSignals"
        @open-report="$emit('openReport', $event)"
        @open-compass-page="$emit('openCompassPage')"
      />
    </aside>
  </el-container>

  <el-drawer
    v-if="isCompactLayout"
    :model-value="leftPanelVisible"
    direction="ltr"
    size="308px"
    append-to-body
    class="terminal-drawer"
    :with-header="false"
    @update:model-value="$emit('update:leftPanelVisible', $event)"
  >
    <SidebarLeft
      :current-profile="currentProfile"
      :history-profiles="historyProfiles"
      :profile-display-tags="profileDisplayTags"
      :recent-conversations="recentConversations"
      :current-conversation-id="currentConversationId"
      :format-conversation-time="formatConversationTime"
      @open-profile-dialog="$emit('openProfileDialog', $event)"
      @create-conversation="$emit('createConversation')"
      @switch-profile="$emit('switchProfile', $event)"
      @switch-conversation="$emit('switchConversation', $event)"
      @open-match-history="$emit('openMatchHistory')"
    />
  </el-drawer>

  <el-drawer
    v-if="isCompactLayout"
    :model-value="rightPanelVisible"
    direction="rtl"
    size="308px"
    append-to-body
    class="terminal-drawer"
    :with-header="false"
    @update:model-value="$emit('update:rightPanelVisible', $event)"
  >
    <SidebarRight
      :compass-reports="compassReports"
      :compass-report-loading="compassReportLoading"
      :glossary="glossary"
      :format-compass-date="formatCompassDate"
      :compass-overview="compassOverview"
      :compass-signals="compassSignals"
      @open-report="$emit('openReport', $event)"
      @open-compass-page="$emit('openCompassPage')"
    />
  </el-drawer>
</template>

<script setup>
import { Expand, Fold } from '@element-plus/icons-vue'

import brandLogoMark from '../../assets/brand-logo-mark.png'
import SidebarLeft from './SidebarLeft.vue'
import SidebarRight from './SidebarRight.vue'

defineProps({
  isCompactLayout: { type: Boolean, default: false },
  leftPanelVisible: { type: Boolean, default: false },
  rightPanelVisible: { type: Boolean, default: false },
  currentProfile: { type: Object, default: null },
  historyProfiles: { type: Array, default: () => [] },
  profileDisplayTags: { type: Function, required: true },
  recentConversations: { type: Array, default: () => [] },
  currentConversationId: { type: Number, default: null },
  formatConversationTime: { type: Function, required: true },
  currentProfileName: { type: String, default: '' },
  citedPolicyTitle: { type: String, default: '' },
  canClearConversation: { type: Boolean, default: false },
  modeLabel: { type: String, default: '' },
  currentModeTone: { type: String, default: '' },
  compassReports: { type: Array, default: () => [] },
  compassReportLoading: { type: Boolean, default: false },
  glossary: { type: Array, default: () => [] },
  formatCompassDate: { type: Function, required: true },
  compassOverview: { type: Object, default: () => ({}) },
  compassSignals: { type: Object, default: () => ({}) },
})

defineEmits([
  'update:leftPanelVisible',
  'update:rightPanelVisible',
  'openLeftPanel',
  'openRightPanel',
  'clearConversation',
  'openProfileDialog',
  'createConversation',
  'switchProfile',
  'switchConversation',
  'openMatchHistory',
  'openReport',
  'openCompassPage',
])
</script>

<style scoped>
.terminal-layout {
  height: 100vh;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(29, 91, 61, 0.04), transparent 24%),
    linear-gradient(180deg, #f6f7f4 0%, #f1f3ef 100%);
  color: #161816;
  font-family: var(--nc-font-sans);
}

.terminal-sidebar {
  display: flex;
  min-width: 0;
  background: rgba(248, 249, 246, 0.92);
}

.terminal-sidebar--left {
  flex: 0 0 clamp(252px, 20vw, 280px);
  border-right: 1px solid rgba(18, 24, 22, 0.08);
}

.terminal-sidebar--right {
  flex: 0 0 clamp(248px, 21vw, 288px);
  border-left: 1px solid rgba(18, 24, 22, 0.08);
}

.terminal-sidebar :deep(.sidebar) {
  width: 100% !important;
}

.terminal-main {
  min-width: 0;
  padding: 0;
  background: transparent;
}

.terminal-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.terminal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.15rem 1.4rem 1rem;
  border-bottom: 1px solid rgba(18, 24, 22, 0.08);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(255, 255, 255, 0.78)),
    rgba(255, 255, 255, 0.74);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

.terminal-header__left,
.terminal-header__right {
  display: flex;
  align-items: flex-start;
  gap: 0.9rem;
}

.terminal-header__right {
  justify-content: flex-end;
  flex-wrap: wrap;
}

.terminal-identity {
  min-width: 0;
  max-width: 720px;
}

.terminal-brand-row {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
}

.terminal-brand-mark {
  display: block;
  height: 22px;
  width: auto;
  max-width: 100%;
  object-fit: contain;
}

.terminal-kicker {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: rgba(22, 24, 22, 0.5);
}

.terminal-title-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-top: 0.45rem;
}

.terminal-title {
  font-size: 1.06rem;
  font-weight: 650;
  color: #111412;
  letter-spacing: -0.03em;
}

.terminal-mode-badge {
  display: inline-flex;
  align-items: center;
  min-height: 1.75rem;
  padding: 0 0.65rem;
  border-radius: 999px;
  border: 1px solid rgba(18, 24, 22, 0.1);
  background: rgba(17, 20, 18, 0.04);
  font-size: 0.72rem;
  font-weight: 600;
  color: #4d534f;
}

.terminal-subtitle {
  margin: 0.45rem 0 0;
  font-size: 0.82rem;
  line-height: 1.6;
  color: rgba(22, 24, 22, 0.62);
}

.terminal-context-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 2.4rem;
  max-width: 280px;
  padding: 0 0.9rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(18, 24, 22, 0.08);
  color: #1d211f;
}

.terminal-context-chip strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.terminal-context-chip--muted {
  background: rgba(246, 247, 244, 0.94);
}

.terminal-context-label {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: rgba(22, 24, 22, 0.46);
  text-transform: uppercase;
}

.terminal-ghost-btn,
.terminal-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.4rem;
  border-radius: 999px;
  border: 1px solid rgba(18, 24, 22, 0.12);
  background: rgba(255, 255, 255, 0.82);
  color: #232826;
  transition: border-color 0.18s ease, color 0.18s ease, background 0.18s ease;
}

.terminal-ghost-btn {
  padding: 0 0.95rem;
  font-size: 0.82rem;
  font-weight: 600;
}

.terminal-icon-btn {
  width: 2.4rem;
  padding: 0;
  cursor: pointer;
}

.terminal-ghost-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.terminal-ghost-btn:not(:disabled):hover,
.terminal-icon-btn:hover {
  border-color: rgba(18, 24, 22, 0.24);
  background: rgba(255, 255, 255, 0.96);
}

.terminal-stage {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

:deep(.terminal-drawer .el-drawer) {
  background: #f7f8f5;
}

:deep(.terminal-drawer .el-drawer__body) {
  padding: 0;
}

@media (max-width: 1180px) {
  .terminal-sidebar {
    display: none;
  }
}

@media (max-width: 900px) {
  .terminal-header {
    flex-direction: column;
  }

  .terminal-header__right {
    width: 100%;
    justify-content: flex-start;
  }

  .terminal-context-chip {
    max-width: 100%;
  }
}
</style>
```

## frontend\src\components\chat\ChatMessagePane.vue

```vue
<template>
  <div class="stream-container">
    <template v-if="messages.length === 0">
      <div class="empty-terminal">
        <img class="empty-terminal__mark" :src="brandLogoMark" alt="AgriPolicy AI" />
        <h1 class="empty-terminal__title">鏀跨瓥鏅鸿兘寮曟搸</h1>
        <p class="empty-terminal__subtitle">
          闈㈠悜鍐滀笟鏀跨瓥鍒ゆ柇鐨勫垎鏋愬伐浣滄祦銆傛寕杞界敾鍍忋€佸彂璧疯拷闂€佺敓鎴愯В璇讳笌鐢虫姤寤鸿銆?
        </p>

        <div class="prompt-suggestions">
          <button
            v-for="(q, i) in quickQuestions"
            :key="i"
            type="button"
            class="suggestion-item"
            @click="$emit('useQuickQuestion', q)"
          >
            <span class="suggestion-item__prefix">鏌ヨ</span>
            <span class="suggestion-item__text">{{ q }}</span>
          </button>
        </div>
      </div>
    </template>

    <template v-else>
      <div ref="chatListRef" class="message-stream">
        <section
          v-for="(msg, i) in messages"
          :key="msg.localId || msg.id || i"
          class="turn-block"
          :class="`turn-block--${msg.role}`"
        >
          <div class="turn-rail">
            <span class="turn-avatar">{{ msg.role === 'user' ? '鎴? : 'AI' }}</span>
            <span class="turn-label">{{ msg.role === 'user' ? '鐢ㄦ埛杈撳叆' : '鍒嗘瀽杈撳嚭' }}</span>
          </div>

          <div class="turn-content">
            <template v-if="msg.role === 'user'">
              <div class="user-query">{{ msg.content }}</div>
            </template>

            <template v-else>
              <SafeRichText
                class="markdown-prose"
                :content="i < messages.length - 1 ? (msg.content || '') : ((msg.content || '') + streamingContent)"
              />
              <span v-if="showCursor(msg, i)" class="terminal-cursor" />
              <div v-if="msg.status === 'cancelled'" class="halt-badge">鐢熸垚宸蹭腑鏂?/div>

              <div class="report-slot">
                <slot name="assistant-extra" :msg="msg" :index="i" :is-last="i === messages.length - 1" />
              </div>
            </template>
          </div>
        </section>

        <div class="scroll-pad" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'

import brandLogoMark from '../../assets/brand-logo-mark.png'
import SafeRichText from '../common/SafeRichText.vue'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  quickQuestions: { type: Array, default: () => [] },
  streaming: { type: Boolean, default: false },
  reportStreaming: { type: Boolean, default: false },
  streamingContent: { type: String, default: '' },
})

defineEmits(['useQuickQuestion'])

const chatListRef = ref(null)

function scrollToBottom() {
  if (chatListRef.value) {
    chatListRef.value.scrollTop = chatListRef.value.scrollHeight
  }
}

function showCursor(msg, index) {
  return Boolean((props.streaming || props.reportStreaming) && index === props.messages.length - 1 && props.streamingContent)
}

defineExpose({
  scrollToBottom,
})
</script>

<style scoped>
.stream-container {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0.96)),
    #fff;
}

.empty-terminal {
  min-height: 100%;
  padding: 4.2rem 1.5rem 5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.empty-terminal__mark {
  display: block;
  height: 52px;
  width: auto;
  max-width: 100%;
  object-fit: contain;
}

.empty-terminal__title {
  margin: 1.3rem 0 0.6rem;
  font-size: clamp(2rem, 3vw, 2.7rem);
  line-height: 1.04;
  letter-spacing: -0.05em;
  color: #111412;
}

.empty-terminal__subtitle {
  max-width: 40rem;
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.8;
  color: rgba(17, 20, 18, 0.6);
}

.prompt-suggestions {
  width: min(100%, 42rem);
  display: grid;
  gap: 0.75rem;
  margin-top: 2rem;
}

.suggestion-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.8rem;
  align-items: center;
  width: 100%;
  padding: 0.95rem 1rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  border-radius: 1rem;
  background: rgba(247, 248, 245, 0.88);
  color: #1c211e;
  text-align: left;
  transition: border-color 0.18s ease, background 0.18s ease, transform 0.18s ease;
}

.suggestion-item:hover {
  border-color: rgba(17, 20, 18, 0.18);
  background: rgba(255, 255, 255, 0.98);
  transform: translateY(-1px);
}

.suggestion-item__prefix {
  display: inline-flex;
  align-items: center;
  min-height: 1.55rem;
  padding: 0 0.55rem;
  border-radius: 999px;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(17, 20, 18, 0.04);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.54);
}

.suggestion-item__text {
  font-size: 0.92rem;
  line-height: 1.45;
}

.message-stream {
  max-width: 56rem;
  margin: 0 auto;
  padding: 2.4rem 1.6rem 5rem;
}

.turn-block {
  display: grid;
  grid-template-columns: 5rem minmax(0, 1fr);
  gap: 1rem;
  margin-bottom: 2.2rem;
}

.turn-rail {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  align-items: flex-start;
  padding-top: 0.15rem;
}

.turn-avatar {
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  border-radius: 0.65rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  border: 1px solid rgba(17, 20, 18, 0.08);
}

.turn-block--user .turn-avatar {
  background: rgba(17, 20, 18, 0.06);
  color: #2e3531;
}

.turn-block--assistant .turn-avatar {
  background: #171a18;
  color: #fff;
}

.turn-label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.45);
}

.turn-content {
  min-width: 0;
}

.user-query {
  font-size: clamp(1.02rem, 1.6vw, 1.22rem);
  font-weight: 650;
  line-height: 1.6;
  color: #111412;
  white-space: pre-wrap;
  letter-spacing: -0.02em;
}

.markdown-prose {
  font-size: 0.96rem;
  line-height: 1.82;
  color: #232826;
}

.markdown-prose :deep(h1),
.markdown-prose :deep(h2),
.markdown-prose :deep(h3) {
  color: #111412;
  line-height: 1.3;
  letter-spacing: -0.03em;
}

.markdown-prose :deep(h1) {
  font-size: 1.45rem;
  margin: 0 0 1rem;
}

.markdown-prose :deep(h2) {
  margin: 1.5rem 0 0.65rem;
  font-size: 1.18rem;
}

.markdown-prose :deep(h3) {
  margin: 1.15rem 0 0.5rem;
  font-size: 1rem;
}

.markdown-prose :deep(p) {
  margin: 0 0 0.9rem;
}

.markdown-prose :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-prose :deep(ul),
.markdown-prose :deep(ol) {
  margin: 0.65rem 0 1rem;
  padding-left: 1.35rem;
}

.markdown-prose :deep(li) {
  margin-bottom: 0.4rem;
}

.markdown-prose :deep(blockquote) {
  margin: 1rem 0;
  padding-left: 0.9rem;
  border-left: 2px solid rgba(29, 91, 61, 0.18);
  color: rgba(35, 40, 38, 0.8);
}

.markdown-prose :deep(code) {
  padding: 0.08rem 0.32rem;
  border-radius: 0.35rem;
  background: rgba(17, 20, 18, 0.05);
}

.markdown-prose :deep(strong) {
  color: #151917;
  font-weight: 650;
}

.terminal-cursor {
  display: inline-block;
  width: 0.45rem;
  height: 1.1rem;
  margin-left: 0.2rem;
  vertical-align: text-bottom;
  background: #1d5b3d;
  animation: blink 1s step-end infinite;
}

.halt-badge {
  display: inline-flex;
  align-items: center;
  min-height: 1.7rem;
  margin-top: 0.8rem;
  padding: 0 0.6rem;
  border-radius: 999px;
  border: 1px solid rgba(146, 32, 32, 0.16);
  background: rgba(146, 32, 32, 0.06);
  color: #8b3030;
  font-size: 0.74rem;
  font-weight: 700;
}

.report-slot {
  margin-top: 1.25rem;
}

.scroll-pad {
  height: 1rem;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

@media (max-width: 860px) {
  .message-stream {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .turn-block {
    grid-template-columns: 1fr;
    gap: 0.7rem;
  }

  .turn-rail {
    flex-direction: row;
    align-items: center;
  }
}
</style>
```

## frontend\src\components\chat\ChatComposer.vue

```vue
<template>
  <div class="command-dock">
    <div class="command-dock__inner">
      <transition name="terminal-fade">
        <div v-if="citedPolicy" class="reference-pill">
          <span class="reference-pill__label">寮曠敤鏀跨瓥</span>
          <span class="reference-pill__title">{{ citedPolicy.title }}</span>
          <button
            type="button"
            class="reference-pill__clear"
            aria-label="鍙栨秷寮曠敤"
            @click="$emit('clearCitation')"
          >
            脳
          </button>
        </div>
      </transition>

      <div class="composer-box" :class="{ 'composer-box--focused': isFocused }">
        <div class="composer-box__toolbar">
          <div class="composer-box__modes">
            <el-dropdown trigger="click" placement="top-start" @command="$emit('changeMode', $event)">
              <button type="button" class="mode-selector">
                {{ modeLabel }}
                <el-icon><ArrowDown /></el-icon>
              </button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="match">鏀跨瓥鏅鸿兘鍖归厤</el-dropdown-item>
                  <el-dropdown-item command="interpret">鏀跨瓥鐧借瘽瑙ｈ</el-dropdown-item>
                  <el-dropdown-item command="llm">鍐滀笟澶фā鍨嬮棶绛?/el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>

            <span v-if="currentProfile" class="context-indicator">
              <span class="context-indicator__dot" />
              褰撳墠鐢诲儚锛歿{ currentProfileName }}
            </span>
          </div>

          <div class="composer-box__status">
            <span class="status-copy">{{ streaming ? '姝ｅ湪鐢熸垚' : '杈撳叆鍚庡彂閫? }}</span>
          </div>
        </div>

        <div class="composer-box__body">
          <el-input
            :model-value="modelValue"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 6 }"
            :placeholder="placeholder"
            :disabled="streaming"
            resize="none"
            class="composer-input"
            @update:model-value="$emit('update:modelValue', $event)"
            @keydown.enter="$emit('submitEnter', $event)"
            @focus="isFocused = true"
            @blur="isFocused = false"
          />

          <div class="composer-box__actions">
            <button
              v-if="streaming"
              type="button"
              class="composer-action composer-action--secondary"
              :disabled="stopping"
              @click="$emit('stop')"
            >
              <span class="composer-action__stop-mark" />
              {{ stopping ? '鍋滄涓€? : '鍋滄鐢熸垚' }}
            </button>

            <button
              v-else
              type="button"
              class="composer-action composer-action--primary"
              :disabled="!modelValue.trim()"
              @click="$emit('send')"
            >
              <span>鍙戦€?/span>
              <span class="composer-action__shortcut">Enter</span>
            </button>
          </div>
        </div>
      </div>

      <p class="dock-footnote">AI 杈撳嚭浠呬綔鏀跨瓥杈呭姪鍒ゆ柇锛屽叧閿潯娆捐缁撳悎鍘熸枃涓庡綋鍦拌姹傚鏍搞€?/p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  streaming: { type: Boolean, default: false },
  stopping: { type: Boolean, default: false },
  citedPolicy: { type: Object, default: null },
  currentProfile: { type: Object, default: null },
  currentProfileName: { type: String, default: '' },
  modeLabel: { type: String, default: '' },
})

defineEmits(['update:modelValue', 'send', 'stop', 'submitEnter', 'changeMode', 'clearCitation'])

const isFocused = ref(false)

const placeholder = computed(() =>
  props.citedPolicy
    ? '鍥寸粫杩欐潯鏀跨瓥缁х画杩介棶锛屼緥濡傦細杩樼己鍝簺鏉′欢銆侀渶瑕佸摢浜涙潗鏂欙紵'
    : '杈撳叆闂銆佸紩鐢ㄤ笂涓嬫枃鎴栫户缁拷闂紝绯荤粺浼氬熀浜庡綋鍓嶇敾鍍忎笌鏀跨瓥淇℃伅缁х画鍒嗘瀽鈥?,
)
</script>

<style scoped>
.command-dock {
  position: sticky;
  bottom: 0;
  z-index: 4;
  padding: 0 1.6rem 1.25rem;
  background: linear-gradient(0deg, rgba(241, 243, 239, 0.98) 60%, rgba(241, 243, 239, 0));
}

.command-dock__inner {
  max-width: 56rem;
  margin: 0 auto;
}

.terminal-fade-enter-active,
.terminal-fade-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.terminal-fade-enter-from,
.terminal-fade-leave-to {
  opacity: 0;
  transform: translateY(0.35rem);
}

.reference-pill {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  width: fit-content;
  max-width: 100%;
  margin-bottom: 0.75rem;
  padding: 0.55rem 0.8rem;
  border-radius: 0.9rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(247, 248, 245, 0.94);
  overflow: hidden;
}

.reference-pill__label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.48);
}

.reference-pill__title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.84rem;
  color: #1f2421;
}

.reference-pill__clear {
  width: 1.75rem;
  height: 1.75rem;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 999px;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(255, 255, 255, 0.84);
  color: rgba(17, 20, 18, 0.6);
}

.composer-box {
  border-radius: 1.15rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 14px 36px rgba(17, 20, 18, 0.06);
  overflow: hidden;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.composer-box--focused {
  border-color: rgba(17, 20, 18, 0.18);
  box-shadow: 0 18px 44px rgba(17, 20, 18, 0.08);
  background: rgba(255, 255, 255, 0.98);
}

.composer-box__toolbar,
.composer-box__body {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.composer-box__toolbar {
  justify-content: space-between;
  padding: 0.8rem 0.95rem 0.72rem;
  border-bottom: 1px solid rgba(17, 20, 18, 0.06);
  background: rgba(249, 250, 248, 0.94);
}

.composer-box__modes,
.composer-box__status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.mode-selector {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  min-height: 2rem;
  padding: 0 0.75rem;
  border-radius: 999px;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: #fff;
  font-size: 0.76rem;
  font-weight: 700;
  color: #171b18;
}

.context-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-width: 0;
  font-size: 0.75rem;
  color: rgba(17, 20, 18, 0.64);
}

.context-indicator__dot {
  width: 0.42rem;
  height: 0.42rem;
  flex: 0 0 auto;
  border-radius: 999px;
  background: #1d5b3d;
}

.status-copy {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.42);
}

.composer-box__body {
  align-items: flex-end;
  padding: 0.85rem 0.95rem 0.95rem;
}

.composer-input {
  flex: 1 1 auto;
  min-width: 0;
}

.composer-input :deep(.el-textarea__inner) {
  min-height: 3rem !important;
  padding: 0;
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  font-size: 0.96rem;
  line-height: 1.7;
  color: #141816;
}

.composer-input :deep(.el-textarea__inner::placeholder) {
  color: rgba(17, 20, 18, 0.38);
}

.composer-box__actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding-bottom: 0.1rem;
}

.composer-action {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  min-height: 2.7rem;
  padding: 0 0.95rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
  transition: transform 0.18s ease, background 0.18s ease, border-color 0.18s ease, color 0.18s ease;
}

.composer-action:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.composer-action--primary {
  border: 1px solid #171a18;
  background: #171a18;
  color: #fff;
}

.composer-action--primary:not(:disabled):hover {
  transform: translateY(-1px);
  background: #202623;
}

.composer-action--secondary {
  border: 1px solid rgba(17, 20, 18, 0.12);
  background: #fff;
  color: #872f2f;
}

.composer-action__stop-mark {
  width: 0.55rem;
  height: 0.55rem;
  border-radius: 0.12rem;
  background: currentColor;
}

.composer-action__shortcut {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  opacity: 0.7;
}

.dock-footnote {
  margin: 0.55rem 0 0;
  text-align: center;
  font-size: 0.7rem;
  color: rgba(17, 20, 18, 0.42);
}

@media (max-width: 860px) {
  .command-dock {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .composer-box__toolbar,
  .composer-box__body {
    flex-direction: column;
    align-items: stretch;
  }

  .composer-box__status {
    justify-content: flex-start;
  }

  .composer-box__actions {
    justify-content: flex-end;
  }
}
</style>
```

## frontend\src\components\chat\SidebarLeft.vue

```vue
<template>
  <el-aside class="sidebar sidebar--left" width="280px">
    <div class="sidebar-shell">
      <header class="sidebar-header">
        <div>
          <div class="sidebar-brand-row">
            <img class="sidebar-brand-mark" :src="brandLogoMark" alt="AgriPolicy AI" />
            <div class="sidebar-kicker">NC-WORKSPACE</div>
          </div>
          <h2 class="sidebar-brand">瀵硅瘽涓婁笅鏂?/h2>
        </div>

        <div class="sidebar-header__actions">
          <button type="button" class="terminal-btn terminal-btn--primary" @click="$emit('createConversation')">
            鏂板缓浼氳瘽
          </button>
          <button type="button" class="terminal-btn terminal-btn--ghost" @click="$emit('openProfileDialog', null)">
            绠＄悊鐢诲儚
          </button>
        </div>
      </header>

      <div class="sidebar-scroll">
        <section class="sidebar-section">
          <div class="sidebar-section__head">
            <span class="sidebar-section__label">鏈€杩戜細璇?/span>
          </div>

          <ul class="conversation-list">
            <li
              v-for="item in recentConversations"
              :key="item.id"
              class="conversation-item"
              :class="{ 'conversation-item--active': currentConversationId === item.id }"
              @click="$emit('switchConversation', item)"
            >
              <div class="conversation-item__title">{{ item.title || '鏈懡鍚嶄細璇? }}</div>
              <div class="conversation-item__meta">
                <span>{{ formatConversationTime(item) }}</span>
                <span v-if="item.lastProfileName">{{ item.lastProfileName }}</span>
                <span v-if="item.draftText" class="conversation-item__draft">鑽夌</span>
              </div>
            </li>
          </ul>

          <p v-if="recentConversations.length === 0" class="sidebar-empty">杩樻病鏈夊巻鍙蹭細璇濄€?/p>
        </section>

        <section class="sidebar-section">
          <div class="sidebar-section__head">
            <span class="sidebar-section__label">褰撳墠鐢诲儚</span>
            <button
              v-if="currentProfile"
              type="button"
              class="terminal-text-btn"
              @click="$emit('openProfileDialog', currentProfile)"
            >
              缂栬緫
            </button>
          </div>

          <div v-if="currentProfile" class="profile-panel">
            <div class="profile-panel__title">{{ currentProfile.name }}</div>
            <div class="profile-panel__tags">
              <span
                v-for="(tag, i) in profileDisplayTags(currentProfile) || []"
                :key="i"
                class="profile-tag"
              >
                {{ tag }}
              </span>
            </div>
          </div>

          <div v-else class="sidebar-empty-box">
            灏氭湭鎸傝浇鐢诲儚銆傞€夋嫨鎴栧垱寤虹敾鍍忓悗锛岀郴缁熶細鍩轰簬鐢诲儚鎸佺画鍒ゆ柇璧勬牸涓庨闄╃己鍙ｃ€?
          </div>
        </section>

        <section class="sidebar-section">
          <div class="sidebar-section__head">
            <span class="sidebar-section__label">鐢诲儚绱㈠紩</span>
          </div>

          <button
            type="button"
            class="terminal-btn terminal-btn--ghost terminal-btn--block"
            :disabled="!currentProfile"
            @click="$emit('openMatchHistory')"
          >
            鏌ョ湅鍖归厤鍘嗗彶
          </button>

          <ul class="history-list">
            <li
              v-for="p in historyProfiles"
              :key="p.id"
              class="history-item"
              :class="{ 'history-item--active': currentProfile?.id === p.id }"
              @click="$emit('switchProfile', p)"
            >
              <span class="history-item__dot" />
              <span class="history-item__name">{{ p.name || '鏈懡鍚嶇敾鍍? }}</span>
            </li>
          </ul>

          <p v-if="historyProfiles.length === 0" class="sidebar-empty">鏆傛棤鐢诲儚鏁版嵁銆?/p>
        </section>
      </div>
    </div>
  </el-aside>
</template>

<script setup>
import brandLogoMark from '../../assets/brand-logo-mark.png'

defineProps({
  currentProfile: { type: Object, default: null },
  historyProfiles: { type: Array, default: () => [] },
  profileDisplayTags: { type: Function, default: () => [] },
  recentConversations: { type: Array, default: () => [] },
  currentConversationId: { type: Number, default: null },
  formatConversationTime: { type: Function, default: () => '' },
})

defineEmits(['openProfileDialog', 'switchProfile', 'openMatchHistory', 'createConversation', 'switchConversation'])
</script>

<style scoped>
.sidebar {
  height: 100%;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(249, 250, 248, 0.98), rgba(244, 246, 242, 0.98)),
    #f7f8f5;
}

.sidebar-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-header {
  padding: 1.25rem 1.15rem 1rem;
  border-bottom: 1px solid rgba(17, 20, 18, 0.08);
}

.sidebar-brand-row {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.sidebar-brand-mark {
  display: block;
  height: 20px;
  width: auto;
  max-width: 100%;
  object-fit: contain;
}

.sidebar-kicker {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: rgba(17, 20, 18, 0.42);
}

.sidebar-brand {
  margin: 0.45rem 0 0;
  font-size: 1.1rem;
  font-weight: 650;
  color: #111412;
  letter-spacing: -0.03em;
}

.sidebar-header__actions {
  display: grid;
  gap: 0.55rem;
  margin-top: 1rem;
}

.sidebar-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1rem 1.5rem;
}

.sidebar-section + .sidebar-section {
  margin-top: 1.5rem;
}

.sidebar-section__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.65rem;
}

.sidebar-section__label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.46);
}

.terminal-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.55rem;
  border-radius: 0.9rem;
  border: 1px solid transparent;
  font-size: 0.82rem;
  font-weight: 700;
  transition: border-color 0.18s ease, background 0.18s ease, color 0.18s ease, transform 0.18s ease;
}

.terminal-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.terminal-btn--primary {
  background: #171a18;
  color: #fff;
  border-color: #171a18;
}

.terminal-btn--ghost {
  background: rgba(255, 255, 255, 0.82);
  border-color: rgba(17, 20, 18, 0.1);
  color: #171a18;
}

.terminal-btn--block {
  width: 100%;
}

.terminal-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.terminal-text-btn {
  background: none;
  border: none;
  padding: 0;
  font-size: 0.74rem;
  font-weight: 700;
  color: rgba(17, 20, 18, 0.54);
}

.conversation-list,
.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.conversation-item,
.history-item {
  border-radius: 0.95rem;
  cursor: pointer;
  transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
}

.conversation-item {
  padding: 0.8rem 0.85rem;
  border: 1px solid rgba(17, 20, 18, 0.06);
  background: rgba(255, 255, 255, 0.68);
}

.conversation-item + .conversation-item,
.history-item + .history-item {
  margin-top: 0.4rem;
}

.conversation-item:hover,
.history-item:hover {
  background: rgba(255, 255, 255, 0.94);
  border-color: rgba(17, 20, 18, 0.12);
  transform: translateY(-1px);
}

.conversation-item--active,
.history-item--active {
  border-color: rgba(29, 91, 61, 0.18);
  background: rgba(255, 255, 255, 0.98);
}

.conversation-item__title,
.profile-panel__title {
  font-size: 0.86rem;
  font-weight: 650;
  line-height: 1.45;
  color: #151917;
}

.conversation-item__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem 0.7rem;
  margin-top: 0.45rem;
  font-size: 0.72rem;
  color: rgba(17, 20, 18, 0.5);
}

.conversation-item__draft {
  font-weight: 700;
  color: #1d5b3d;
}

.profile-panel,
.sidebar-empty-box {
  border-radius: 1rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(255, 255, 255, 0.78);
  padding: 0.9rem;
}

.profile-panel__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.65rem;
}

.profile-tag {
  display: inline-flex;
  align-items: center;
  min-height: 1.55rem;
  padding: 0 0.55rem;
  border-radius: 999px;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(17, 20, 18, 0.04);
  font-size: 0.68rem;
  font-weight: 700;
  color: rgba(17, 20, 18, 0.58);
}

.sidebar-empty,
.sidebar-empty-box {
  font-size: 0.76rem;
  line-height: 1.65;
  color: rgba(17, 20, 18, 0.5);
}

.history-list {
  margin-top: 0.75rem;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 0.85rem;
  border: 1px solid rgba(17, 20, 18, 0.06);
  background: rgba(255, 255, 255, 0.58);
}

.history-item__dot {
  width: 0.45rem;
  height: 0.45rem;
  flex: 0 0 auto;
  border-radius: 999px;
  background: rgba(17, 20, 18, 0.2);
}

.history-item--active .history-item__dot {
  background: #1d5b3d;
}

.history-item__name {
  font-size: 0.8rem;
  color: #171b18;
}
</style>
```

## frontend\src\components\chat\SidebarRight.vue

```vue
<template>
  <el-aside class="sidebar sidebar--right" width="228px">
    <div class="sidebar-shell">
      <div class="sidebar-scroll">
        <section class="sidebar-section">
          <div class="sidebar-section__head">
            <span class="sidebar-section__label">瓒嬪娍淇″彿</span>
          </div>

          <div class="signal-overview">
            <div class="signal-overview__summary">
              {{ compassOverview?.forecast_summary || '绯荤粺姝ｅ湪鏁寸悊鏈€鏂扮殑鏀跨瓥瓒嬪娍鎽樿銆? }}
            </div>
            <div class="signal-overview__meta">
              <span>鍥藉锛歿{ layerLabel(compassOverview?.national_layer_status) }}</span>
              <span>婀栧寳锛歿{ layerLabel(compassOverview?.local_layer_status) }}</span>
            </div>
            <button type="button" class="terminal-link-btn" @click="$emit('openCompassPage')">杩涘叆椋庡悜鍙?/button>
          </div>
        </section>

        <section class="sidebar-section">
          <div class="sidebar-section__head">
            <span class="sidebar-section__label">鐑偣鏂瑰悜</span>
          </div>

          <div v-if="topDirections.length === 0" class="sidebar-empty">鏆傛棤鏄捐憲鍗囨俯鏂瑰悜銆?/div>
          <div v-else class="data-list">
            <button
              v-for="item in topDirections"
              :key="`direction-${item.name}`"
              type="button"
              class="data-list__item"
              @click="$emit('openCompassPage')"
            >
              <span class="data-list__title">{{ item.name }}</span>
              <span class="data-list__value" :class="`data-list__value--${item.trend || 'flat'}`">
                {{ trendText(item.trend) }} 路 {{ item.score }}
              </span>
            </button>
          </div>
        </section>

        <section class="sidebar-section">
          <div class="sidebar-section__head">
            <span class="sidebar-section__label">涓讳綋鏈轰細</span>
          </div>

          <div v-if="subjectSignals.length === 0" class="sidebar-empty">鏆傛棤涓讳綋鏈轰細鏍锋湰銆?/div>
          <div v-else class="subject-list">
            <button
              v-for="item in subjectSignals"
              :key="`subject-${item.name}`"
              type="button"
              class="subject-list__item"
              @click="$emit('openCompassPage')"
            >
              <span>{{ item.name }}</span>
              <strong>{{ trendText(item.trend) }}</strong>
            </button>
          </div>
        </section>

        <section class="sidebar-section">
          <div class="sidebar-section__head">
            <span class="sidebar-section__label">鍛ㄦ姤</span>
          </div>

          <div v-if="compassReportLoading" class="sidebar-empty">姝ｅ湪鍔犺浇鎶ュ憡鈥?/div>
          <div v-else-if="compassReports.length === 0" class="sidebar-empty">鏈湡鍛ㄦ姤灏氭湭鐢熸垚銆?/div>
          <div v-else class="report-list">
            <button
              v-for="r in compassReports.slice(0, 3)"
              :key="r.id"
              type="button"
              class="report-list__item"
              @click="$emit('openReport', r.id)"
            >
              <span class="report-list__category">{{ r.category }}</span>
              <strong class="report-list__title">{{ r.title }}</strong>
              <span v-if="r.published_at" class="report-list__date">{{ formatDate(r.published_at) }}</span>
            </button>
          </div>
        </section>

        <section class="sidebar-section">
          <div class="sidebar-section__head">
            <span class="sidebar-section__label">鏈绱㈠紩</span>
          </div>

          <ul v-if="glossary.length > 0" class="glossary-list">
            <li v-for="(g, i) in glossary.slice(0, 4)" :key="i" class="glossary-list__item">
              <span class="glossary-list__term">{{ g.term }}</span>
              <span class="glossary-list__desc">{{ g.desc }}</span>
            </li>
          </ul>
          <p v-else class="sidebar-empty">鏆傛棤鏈绱㈠紩銆?/p>
        </section>
      </div>
    </div>
  </el-aside>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  compassReports: { type: Array, default: () => [] },
  compassReportLoading: { type: Boolean, default: false },
  glossary: { type: Array, default: () => [] },
  formatCompassDate: { type: Function, default: null },
  compassOverview: { type: Object, default: () => ({}) },
  compassSignals: { type: Object, default: () => ({}) },
})

defineEmits(['openReport', 'openCompassPage'])

const topDirections = computed(() =>
  Array.isArray(props.compassOverview?.top_directions) ? props.compassOverview.top_directions.slice(0, 3) : [],
)
const subjectSignals = computed(() =>
  Array.isArray(props.compassSignals?.subject_opportunities) ? props.compassSignals.subject_opportunities.slice(0, 3) : [],
)

function layerLabel(status) {
  if (status === 'active') return '宸插舰鎴?
  if (status === 'weak') return '鍋忓急'
  return '瑙傚療涓?
}

function trendText(trend) {
  if (trend === 'up') return '鍗囨俯'
  if (trend === 'down') return '鍥炶惤'
  return '骞崇ǔ'
}

function formatDate(isoStr) {
  if (!isoStr) return ''
  if (typeof props.formatCompassDate === 'function') return props.formatCompassDate(isoStr)
  try {
    const d = new Date(isoStr)
    return `${d.getMonth() + 1}鏈?{d.getDate()}鏃
  } catch (_) {
    return ''
  }
}
</script>

<style scoped>
.sidebar {
  height: 100%;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(248, 249, 246, 0.98), rgba(243, 245, 241, 0.98)),
    #f7f8f5;
}

.sidebar-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 1.15rem 1rem 1.5rem;
}

.sidebar-section + .sidebar-section {
  margin-top: 1.45rem;
}

.sidebar-section__head {
  margin-bottom: 0.7rem;
}

.sidebar-section__label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.46);
}

.signal-overview,
.data-list__item,
.report-list__item,
.glossary-list__item,
.subject-list__item {
  border-radius: 1rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(255, 255, 255, 0.78);
}

.signal-overview {
  padding: 0.9rem;
}

.signal-overview__summary {
  font-size: 0.86rem;
  line-height: 1.6;
  color: #151917;
}

.signal-overview__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem 0.75rem;
  margin-top: 0.7rem;
  font-size: 0.72rem;
  color: rgba(17, 20, 18, 0.52);
}

.terminal-link-btn {
  margin-top: 0.85rem;
  background: none;
  border: none;
  padding: 0;
  font-size: 0.76rem;
  font-weight: 700;
  color: #1d5b3d;
}

.data-list,
.report-list,
.subject-list,
.glossary-list {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  list-style: none;
  padding: 0;
  margin: 0;
}

.data-list__item,
.report-list__item,
.subject-list__item {
  width: 100%;
  padding: 0.75rem 0.85rem;
  text-align: left;
  transition: border-color 0.18s ease, background 0.18s ease, transform 0.18s ease;
}

.data-list__item:hover,
.report-list__item:hover,
.subject-list__item:hover {
  border-color: rgba(17, 20, 18, 0.14);
  background: rgba(255, 255, 255, 0.96);
  transform: translateY(-1px);
}

.data-list__title,
.report-list__title {
  display: block;
  color: #151917;
  line-height: 1.5;
}

.data-list__title {
  font-size: 0.82rem;
  font-weight: 600;
}

.data-list__value,
.report-list__date,
.glossary-list__desc {
  display: block;
  margin-top: 0.3rem;
  font-size: 0.72rem;
  color: rgba(17, 20, 18, 0.52);
}

.data-list__value--up {
  color: #1d5b3d;
}

.data-list__value--down {
  color: #933434;
}

.subject-list__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
  font-size: 0.8rem;
  color: #151917;
}

.subject-list__item strong {
  color: #1d5b3d;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.report-list__category,
.glossary-list__term {
  display: inline-flex;
  align-items: center;
  min-height: 1.35rem;
  width: fit-content;
  padding: 0 0.4rem;
  border-radius: 999px;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(17, 20, 18, 0.04);
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.54);
}

.report-list__title {
  margin-top: 0.55rem;
  font-size: 0.84rem;
  font-weight: 600;
}

.glossary-list__term {
  margin-bottom: 0.45rem;
}

.sidebar-empty {
  margin: 0;
  font-size: 0.76rem;
  line-height: 1.65;
  color: rgba(17, 20, 18, 0.5);
}
</style>
```

## frontend\src\components\chat\PolicyHealthCard.vue

```vue
<template>
  <div class="result-panel" :class="`result-panel--${health.match_status || 'neutral'}`">
    <div class="result-panel__header">
      <div>
        <span class="result-panel__kicker">{{ statusText }}</span>
        <h3 class="result-panel__title">{{ policyHealthTitle(health) }}</h3>
      </div>

      <div v-if="!health.loading" class="result-panel__metrics">
        <span class="metric-chip metric-chip--pass">鍛戒腑 {{ policyHealthEvidenceCount(health).matched }}</span>
        <span class="metric-chip metric-chip--block">闃绘柇 {{ policyHealthEvidenceCount(health).failedMust }}</span>
        <span class="metric-chip metric-chip--warn">寰呰ˉ {{ policyHealthEvidenceCount(health).failedShould }}</span>
      </div>
    </div>

    <div v-if="health.loading" class="result-panel__loading">绯荤粺姝ｅ湪鏍搁獙璧勬牸鏉′欢銆佽ˉ璐撮噾棰濅笌缂哄彛淇℃伅鈥?/div>

    <template v-else>
      <div class="result-panel__summary">{{ evidenceSummaryText(health) }}</div>

      <div class="result-panel__facts">
        <div class="fact-cell">
          <span class="fact-cell__label">棰勮鎵舵寔閲戦</span>
          <strong class="fact-cell__value">
            {{ health.estimated_amount != null && health.estimated_amount !== '' ? health.estimated_amount : '鏆傛棤' }}
          </strong>
        </div>
        <div class="fact-cell">
          <span class="fact-cell__label">鐢虫姤鎴鏃堕棿</span>
          <strong class="fact-cell__value">
            {{ health.deadline != null && health.deadline !== '' ? health.deadline : '鏆傛棤' }}
          </strong>
        </div>
      </div>

      <div class="result-panel__groups">
        <section v-if="health.matched_nodes && health.matched_nodes.length > 0" class="evidence-group">
          <div class="evidence-group__label">宸叉弧瓒虫潯浠?/div>
          <article
            v-for="node in health.matched_nodes"
            :key="`matched-${node.node_id}`"
            class="evidence-item evidence-item--pass"
          >
            <div class="evidence-item__head">
              <strong>{{ evidenceTitle(node) }}</strong>
              <span>{{ evidenceSource(node, health) }}</span>
            </div>
            <div class="evidence-item__rule">{{ friendlyRuleDetail(node) }}</div>
            <div class="evidence-item__reason">{{ evidenceReason(node) }}</div>
          </article>
        </section>

        <section v-if="health.failed_must_nodes && health.failed_must_nodes.length > 0" class="evidence-group">
          <div class="evidence-group__label">鍏抽敭闃绘柇椤?/div>
          <article
            v-for="node in health.failed_must_nodes"
            :key="`must-${node.node_id}`"
            class="evidence-item evidence-item--block"
          >
            <div class="evidence-item__head">
              <strong>{{ evidenceTitle(node) }}</strong>
              <span>{{ evidenceSource(node, health) }}</span>
            </div>
            <div class="evidence-item__rule">{{ friendlyRuleDetail(node) }}</div>
            <div class="evidence-item__reason">{{ evidenceReason(node) }}</div>
          </article>
        </section>

        <section v-if="health.failed_should_nodes && health.failed_should_nodes.length > 0" class="evidence-group">
          <div class="evidence-group__label">寤鸿琛ラ綈椤?/div>
          <article
            v-for="node in health.failed_should_nodes"
            :key="`should-${node.node_id}`"
            class="evidence-item evidence-item--warn"
          >
            <div class="evidence-item__head">
              <strong>{{ evidenceTitle(node) }}</strong>
              <span>{{ evidenceSource(node, health) }}</span>
            </div>
            <div class="evidence-item__rule">{{ friendlyRuleDetail(node) }}</div>
            <div class="evidence-item__reason">{{ evidenceReason(node) }}</div>
          </article>
        </section>
      </div>

      <section class="missing-block">
        <div class="evidence-group__label">琛ュ厖鎻愰啋</div>
        <ul v-if="health.missing_conditions && health.missing_conditions.length > 0" class="missing-block__list">
          <li v-for="c in health.missing_conditions" :key="c">{{ c }}</li>
        </ul>
        <div v-else class="missing-block__empty">褰撳墠娌℃湁棰濆琛ュ厖鎻愰啋銆?/div>
      </section>

      <div
        v-if="health.source_reference && (health.source_reference.source || health.source_reference.raw_text_ref)"
        class="result-panel__source"
      >
        <span v-if="health.source_reference.source">鍒ゆ柇渚濇嵁锛歿{ health.source_reference.source }}</span>
        <el-link
          v-if="isPolicyUrl(health.source_reference.raw_text_ref)"
          type="primary"
          :href="health.source_reference.raw_text_ref"
          target="_blank"
          rel="noopener"
        >
          鏌ョ湅鏀跨瓥鍘熸枃
        </el-link>
      </div>

      <el-collapse class="result-panel__collapse" :model-value="[]" :accordion="false">
        <el-collapse-item name="official">
          <template #title>鏌ョ湅璇︾粏鍒ゆ柇渚濇嵁</template>
          <SafeRichText class="result-panel__detail" :content="health.detailed_explanation || ''" />
        </el-collapse-item>
      </el-collapse>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

import SafeRichText from '../common/SafeRichText.vue'

const props = defineProps({
  health: { type: Object, required: true },
  policyHealthTitle: { type: Function, required: true },
  policyHealthEvidenceCount: { type: Function, required: true },
  evidenceSummaryText: { type: Function, required: true },
  evidenceTitle: { type: Function, required: true },
  evidenceSource: { type: Function, required: true },
  friendlyRuleDetail: { type: Function, required: true },
  evidenceReason: { type: Function, required: true },
  isPolicyUrl: { type: Function, required: true },
})

const statusText = computed(() => {
  if (props.health.loading) return '鍒嗘瀽涓?
  if (props.health.match_status === 'success') return '宸查€氳繃'
  if (props.health.match_status === 'fail') return '鏈€氳繃'
  return '閮ㄥ垎婊¤冻'
})
</script>

<style scoped>
.result-panel {
  margin-top: 1rem;
  padding: 1.05rem;
  border-radius: 1rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  border-left-width: 3px;
  background: rgba(255, 255, 255, 0.84);
}

.result-panel--success {
  border-left-color: #1d5b3d;
}

.result-panel--fail {
  border-left-color: #8b3030;
}

.result-panel--partial {
  border-left-color: #9b6c1a;
}

.result-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.9rem;
}

.result-panel__kicker {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.44);
}

.result-panel__title {
  margin: 0.35rem 0 0;
  font-size: 0.98rem;
  font-weight: 650;
  color: #151917;
}

.result-panel__metrics {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.45rem;
}

.metric-chip {
  display: inline-flex;
  align-items: center;
  min-height: 1.6rem;
  padding: 0 0.5rem;
  border-radius: 999px;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(17, 20, 18, 0.04);
  font-size: 0.68rem;
  font-weight: 700;
}

.metric-chip--pass {
  color: #1d5b3d;
}

.metric-chip--block {
  color: #8b3030;
}

.metric-chip--warn {
  color: #9b6c1a;
}

.result-panel__loading,
.result-panel__summary,
.evidence-item__rule,
.evidence-item__reason,
.missing-block__empty,
.result-panel__source {
  font-size: 0.82rem;
  line-height: 1.7;
  color: rgba(17, 20, 18, 0.68);
}

.result-panel__summary {
  margin-top: 0.9rem;
}

.result-panel__facts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1px;
  margin-top: 0.95rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  border-radius: 0.9rem;
  overflow: hidden;
  background: rgba(17, 20, 18, 0.08);
}

.fact-cell {
  background: rgba(247, 248, 245, 0.94);
  padding: 0.85rem 0.9rem;
}

.fact-cell__label,
.evidence-group__label {
  display: inline-block;
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.46);
}

.fact-cell__value {
  display: block;
  margin-top: 0.4rem;
  font-size: 1.02rem;
  font-weight: 700;
  color: #171b18;
}

.result-panel__groups {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.evidence-group {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.evidence-item {
  padding: 0.85rem 0.9rem;
  border-radius: 0.9rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(247, 248, 245, 0.94);
}

.evidence-item--pass {
  border-left: 2px solid #1d5b3d;
}

.evidence-item--block {
  border-left: 2px solid #8b3030;
}

.evidence-item--warn {
  border-left: 2px solid #9b6c1a;
}

.evidence-item__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}

.evidence-item__head strong {
  font-size: 0.84rem;
  line-height: 1.5;
  color: #151917;
}

.evidence-item__head span {
  font-size: 0.7rem;
  color: rgba(17, 20, 18, 0.46);
}

.evidence-item__rule {
  margin-top: 0.35rem;
}

.evidence-item__reason {
  margin-top: 0.25rem;
}

.missing-block {
  margin-top: 1rem;
}

.missing-block__list {
  margin: 0.55rem 0 0;
  padding-left: 1.05rem;
  font-size: 0.82rem;
  line-height: 1.7;
  color: rgba(17, 20, 18, 0.7);
}

.result-panel__source {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.95rem;
}

.result-panel__collapse {
  margin-top: 0.95rem;
}

.result-panel__detail :deep(p) {
  margin: 0 0 0.6rem;
}

.result-panel__detail :deep(p:last-child) {
  margin-bottom: 0;
}

@media (max-width: 860px) {
  .result-panel__header,
  .evidence-item__head {
    flex-direction: column;
  }

  .result-panel__facts {
    grid-template-columns: 1fr;
  }
}
</style>
```

## frontend\src\components\chat\InterpretationCard.vue

```vue
<template>
  <div v-if="health && (health.loading || isInterpretationUseful(health))" class="analysis-panel">
    <div class="analysis-panel__header">
      <span class="analysis-panel__kicker">鏍稿績鎻愮偧</span>
      <h3 class="analysis-panel__title">鏀跨瓥鐧借瘽瑙ｈ</h3>
    </div>

    <div v-if="health.loading" class="analysis-panel__loading">绯荤粺姝ｅ湪鎻愮偧閫傜敤瀵硅薄銆佸叧閿爣鍑嗕笌鐢虫姤娴佺▼鈥?/div>

    <div v-else class="analysis-grid">
      <article class="analysis-grid__item">
        <span class="analysis-grid__label">閫傜敤瀵硅薄</span>
        <div class="analysis-grid__value">{{ health['閫傜敤瀵硅薄'] || '鏆傛棤鏄庣‘缁撹' }}</div>
      </article>

      <article class="analysis-grid__item">
        <span class="analysis-grid__label">鏍稿績鏍囧噯</span>
        <div class="analysis-grid__value">{{ health['鏍稿績鏍囧噯'] || '鏆傛棤鏄庣‘缁撹' }}</div>
      </article>

      <article class="analysis-grid__item analysis-grid__item--full">
        <span class="analysis-grid__label">鐢虫姤娴佺▼</span>
        <ol v-if="health['鐢虫姤娴佺▼'] && health['鐢虫姤娴佺▼'].length > 0" class="analysis-grid__list">
          <li v-for="(step, idx) in health['鐢虫姤娴佺▼']" :key="idx">{{ step }}</li>
        </ol>
        <div v-else class="analysis-grid__value">鏆傛棤缁撴瀯鍖栨祦绋嬨€?/div>
      </article>
    </div>
  </div>
</template>

<script setup>
defineProps({
  health: { type: Object, default: null },
  isInterpretationUseful: { type: Function, required: true },
})
</script>

<style scoped>
.analysis-panel {
  margin-top: 1rem;
  border-radius: 1rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(255, 255, 255, 0.82);
  padding: 1rem;
}

.analysis-panel__header {
  margin-bottom: 0.9rem;
}

.analysis-panel__kicker {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.44);
}

.analysis-panel__title {
  margin: 0.35rem 0 0;
  font-size: 0.98rem;
  font-weight: 650;
  color: #151917;
}

.analysis-panel__loading,
.analysis-grid__value {
  font-size: 0.84rem;
  line-height: 1.7;
  color: rgba(17, 20, 18, 0.7);
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.analysis-grid__item {
  padding: 0.9rem;
  border-radius: 0.9rem;
  border: 1px solid rgba(17, 20, 18, 0.06);
  background: rgba(247, 248, 245, 0.92);
}

.analysis-grid__item--full {
  grid-column: 1 / -1;
}

.analysis-grid__label {
  display: inline-block;
  margin-bottom: 0.45rem;
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.46);
}

.analysis-grid__list {
  margin: 0;
  padding-left: 1.15rem;
  font-size: 0.84rem;
  line-height: 1.7;
  color: rgba(17, 20, 18, 0.72);
}

.analysis-grid__list li + li {
  margin-top: 0.35rem;
}

@media (max-width: 860px) {
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}
</style>
```

## frontend\src\components\chat\PolicyRecommendationList.vue

```vue
<template>
  <div v-if="items.length > 0" :class="wrapperClass">
    <div v-if="variant === 'related'" class="list-header">
      <span class="list-header__kicker">鐩稿叧鏀跨瓥</span>
      <h3 class="list-header__title">鍙兘涓庝綘褰撳墠闂鐩稿叧</h3>
    </div>

    <div :class="listClass">
      <article v-for="item in items" :key="itemKey(item)" class="policy-item">
        <div class="policy-item__header">
          <div>
            <h4 class="policy-item__title">{{ item.title }}</h4>
            <p v-if="item.source" class="policy-item__source">鏉ユ簮锛歿{ item.source }}</p>
          </div>

          <span v-if="variant === 'matchCards'" class="policy-item__badge">
            {{ item.fully_matched ? '瀹屽叏鍖归厤' : '閮ㄥ垎鍖归厤' }}
          </span>
        </div>

        <div class="policy-item__summary">
          {{ summaryText(item) }}
        </div>

        <div class="policy-item__meta">
          <span v-if="variant === 'related' && item.publish_date">鍙戝竷鏃ユ湡锛歿{ item.publish_date }}</span>
          <span v-if="variant === 'matchCards' && item.has_risk_warnings">鍚闄╂彁绀?/span>
          <span v-if="variant === 'matchCards' && item.has_action_steps">鏀寔琛屽姩瑙勫垝</span>
        </div>

        <div class="policy-item__actions">
          <el-link
            v-if="itemLink(item)"
            type="primary"
            :href="itemLink(item)"
            target="_blank"
            rel="noopener"
            class="policy-item__link"
          >
            鎵撳紑鏀跨瓥鍘熸枃
          </el-link>
          <span v-else class="policy-item__empty-link">鏆傛棤鍘熸枃閾炬帴</span>

          <button type="button" class="policy-item__action" @click="$emit('setCitedPolicy', item)">
            瀵硅鏀跨瓥鎻愰棶
          </button>

          <button
            v-if="variant === 'related'"
            type="button"
            class="policy-item__action policy-item__action--primary"
            :disabled="oneKeyInterpretLoading === oneKeyInterpretKey(item)"
            @click.stop="$emit('oneKeyInterpretFromPolicy', item)"
          >
            {{ oneKeyInterpretLoading === oneKeyInterpretKey(item) ? '瑙ｈ涓€? : '涓€閿櫧璇濊В璇? }}
          </button>

          <button
            v-if="variant === 'matchCards'"
            type="button"
            class="policy-item__action policy-item__action--primary"
            :disabled="matchingPolicyId === Number(item.policy_id)"
            @click="$emit('runMatchForPolicyInChat', item)"
          >
            {{ matchingPolicyId === Number(item.policy_id) ? '鐢熸垚涓€? : '鐢熸垚鐢虫姤瑙勫垝' }}
          </button>
        </div>
      </article>
    </div>

    <div v-if="variant === 'matchCards'" class="list-refresh">
      <button type="button" class="list-refresh__btn" @click="$emit('replaceBatch')">鎹竴鎵规斂绛栧缓璁?/button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, required: true },
  items: { type: Array, default: () => [] },
  isPolicyUrl: { type: Function, required: true },
  oneKeyInterpretLoading: { type: String, default: null },
  oneKeyInterpretKey: { type: Function, default: () => '' },
  matchingPolicyId: { type: Number, default: null },
})

defineEmits(['setCitedPolicy', 'oneKeyInterpretFromPolicy', 'runMatchForPolicyInChat', 'replaceBatch'])

const wrapperClass = computed(() => (props.variant === 'related' ? 'policy-list policy-list--related' : 'policy-list'))
const listClass = computed(() => (props.variant === 'related' ? 'policy-grid' : 'policy-grid policy-grid--match'))

function itemLink(item) {
  const ref = props.variant === 'related' ? item?.page_url : item?.raw_text_ref
  return props.isPolicyUrl(ref) ? ref : ''
}

function itemKey(item) {
  return item?.raw_id ?? item?.policy_id ?? item?.id ?? item?.title
}

function summaryText(item) {
  if (props.variant === 'related') return item?.summary || ''
  return item?.summary || '鏆傛棤鎽樿鍐呭銆?
}
</script>

<style scoped>
.policy-list {
  margin-top: 1rem;
}

.list-header {
  margin-bottom: 0.8rem;
}

.list-header__kicker {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.44);
}

.list-header__title {
  margin: 0.35rem 0 0;
  font-size: 0.98rem;
  font-weight: 650;
  color: #151917;
}

.policy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 0.85rem;
}

.policy-item {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.95rem;
  border-radius: 1rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(255, 255, 255, 0.78);
  transition: border-color 0.18s ease, background 0.18s ease, transform 0.18s ease;
}

.policy-item:hover {
  border-color: rgba(17, 20, 18, 0.14);
  background: rgba(255, 255, 255, 0.96);
  transform: translateY(-1px);
}

.policy-item__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}

.policy-item__title {
  margin: 0;
  font-size: 0.92rem;
  line-height: 1.5;
  color: #151917;
}

.policy-item__source,
.policy-item__meta,
.policy-item__empty-link {
  font-size: 0.74rem;
  line-height: 1.6;
  color: rgba(17, 20, 18, 0.52);
}

.policy-item__source {
  margin: 0.3rem 0 0;
}

.policy-item__summary {
  font-size: 0.83rem;
  line-height: 1.7;
  color: rgba(17, 20, 18, 0.72);
}

.policy-item__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem 0.85rem;
}

.policy-item__badge {
  display: inline-flex;
  align-items: center;
  min-height: 1.5rem;
  padding: 0 0.55rem;
  border-radius: 999px;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(17, 20, 18, 0.04);
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: rgba(17, 20, 18, 0.56);
}

.policy-item__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.55rem 0.8rem;
  margin-top: auto;
}

.policy-item__link {
  font-size: 0.76rem;
}

.policy-item__action,
.list-refresh__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.15rem;
  padding: 0 0.8rem;
  border-radius: 999px;
  border: 1px solid rgba(17, 20, 18, 0.1);
  background: rgba(255, 255, 255, 0.9);
  font-size: 0.74rem;
  font-weight: 700;
  color: #171a18;
  transition: border-color 0.18s ease, background 0.18s ease, color 0.18s ease;
}

.policy-item__action--primary {
  background: #171a18;
  border-color: #171a18;
  color: #fff;
}

.policy-item__action:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.list-refresh {
  display: flex;
  justify-content: center;
  margin-top: 0.95rem;
}

@media (max-width: 860px) {
  .policy-grid {
    grid-template-columns: 1fr;
  }
}
</style>
```

## frontend\src\components\chat\ReportDrawer.vue

```vue
<template>
  <el-drawer
    :model-value="modelValue"
    :title="selectedReport?.title || '鏀跨瓥椋庡悜鎶ュ憡'"
    size="620px"
    direction="rtl"
    destroy-on-close
    class="report-drawer"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div v-loading="reportDetailLoading" class="report-drawer__body">
      <div v-if="selectedReport?.category || selectedReport?.published_at" class="report-drawer__meta">
        <span v-if="selectedReport?.category" class="report-drawer__badge">{{ selectedReport.category }}</span>
        <span v-if="selectedReport?.published_at" class="report-drawer__date">{{ formatDate(selectedReport.published_at) }}</span>
      </div>

      <section v-if="highlightItems.length > 0" class="report-stage">
        <article class="report-stage__panel">
          <span class="report-stage__label">瓒嬪娍缁撹</span>
          <div class="report-stage__list">
            <div v-for="item in highlightItems.slice(0, 3)" :key="`summary-${item.name}`" class="report-stage__item">
              <strong>{{ item.name }}</strong>
              <span>{{ summaryLine(item) }}</span>
            </div>
          </div>
        </article>

        <article class="report-stage__panel">
          <span class="report-stage__label">琛屽姩寤鸿</span>
          <div class="report-stage__list">
            <div v-for="item in highlightItems.slice(0, 2)" :key="`action-${item.name}`" class="report-stage__item">
              <strong>{{ item.name }}</strong>
              <span>{{ item.action_hint || '寤鸿缁撳悎鏀跨瓥鍘熸枃缁х画鏍搁獙鍏蜂綋鍙ｅ緞銆? }}</span>
            </div>
          </div>
        </article>
      </section>

      <SafeRichText
        v-if="selectedReport?.content"
        class="report-drawer__content markdown"
        :content="displayContent"
      />
    </div>
  </el-drawer>
</template>

<script setup>
import { computed } from 'vue'

import SafeRichText from '../common/SafeRichText.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  selectedReport: { type: Object, default: null },
  reportDetailLoading: { type: Boolean, default: false },
  formatCompassDate: { type: Function, default: null },
  compassOverview: { type: Object, default: () => ({}) },
  compassSignals: { type: Object, default: () => ({}) },
})

defineEmits(['update:modelValue'])

function formatParagraphBreaks(text) {
  if (!text || typeof text !== 'string') return text || ''
  const trimmed = text.trim()
  if (/^#+\s/m.test(trimmed) || /\*\*[^*]+\*\*/.test(trimmed)) return trimmed
  return trimmed
    .replace(/銆?\s*绗琜涓€浜屼笁鍥涗簲鍏竷鍏節鍗乗d]+[銆佹槸]/g, '銆俓n\n$&')
    .replace(/銆?\s*寤鸿/g, '銆俓n\n寤鸿')
    .replace(/銆?\s*鍏蜂綋/g, '銆俓n\n鍏蜂綋')
}

const displayContent = computed(() => formatParagraphBreaks(props.selectedReport?.content || ''))

const highlightItems = computed(() => {
  const category = props.selectedReport?.category
  if (category === '鏀寔鏂瑰悜') return props.compassOverview?.top_directions || []
  if (category === '浜т笟璧板悜') return props.compassSignals?.national_signals || props.compassOverview?.top_directions || []
  if (category === '鍖哄煙閲嶇偣') return props.compassOverview?.hubei_opportunities || []
  if (category === '鐢虫姤瑕佺偣') return props.compassOverview?.preparation_signals || []
  return props.compassOverview?.top_directions || []
})

function summaryLine(item) {
  if (!item) return '鏆傛棤鎽樿'
  if (item.beneficiary) return `閲嶇偣鍙楃泭涓讳綋锛?{item.beneficiary}`
  if (item.policy_count != null) return `鐩稿叧缁撴瀯鍖栨斂绛?${item.policy_count} 鏉
  return `瓒嬪娍璇勫垎 ${item.score || 0}`
}

function formatDate(isoStr) {
  if (!isoStr) return ''
  if (typeof props.formatCompassDate === 'function') return props.formatCompassDate(isoStr)
  try {
    const d = new Date(isoStr)
    return `${d.getMonth() + 1}鏈?{d.getDate()}鏃
  } catch (_) {
    return ''
  }
}
</script>

<style>
.report-drawer.el-drawer {
  background:
    linear-gradient(180deg, #f6f7f4 0%, #eff2ee 100%),
    #f5f6f3;
}

.report-drawer.el-drawer .el-drawer__header {
  margin-bottom: 0;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(17, 20, 18, 0.08);
}

.report-drawer.el-drawer .el-drawer__title {
  font-size: 1.18rem !important;
  font-weight: 650 !important;
  letter-spacing: -0.03em;
  color: #151917 !important;
}
</style>

<style scoped>
.report-drawer__body {
  padding: 1rem 0.2rem 1.2rem;
}

.report-drawer__meta {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  margin-bottom: 0.9rem;
}

.report-drawer__badge {
  display: inline-flex;
  align-items: center;
  min-height: 1.6rem;
  padding: 0 0.55rem;
  border-radius: 999px;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(17, 20, 18, 0.04);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: rgba(17, 20, 18, 0.56);
}

.report-drawer__date {
  font-size: 0.76rem;
  color: rgba(17, 20, 18, 0.48);
}

.report-stage {
  display: grid;
  gap: 0.8rem;
  margin-bottom: 1rem;
}

.report-stage__panel,
.report-drawer__content {
  border-radius: 1rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(255, 255, 255, 0.8);
}

.report-stage__panel {
  padding: 0.95rem;
}

.report-stage__label {
  display: inline-block;
  margin-bottom: 0.65rem;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.44);
}

.report-stage__list {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.report-stage__item strong {
  display: block;
  font-size: 0.84rem;
  color: #151917;
}

.report-stage__item span {
  display: block;
  margin-top: 0.3rem;
  font-size: 0.78rem;
  line-height: 1.65;
  color: rgba(17, 20, 18, 0.66);
}

.report-drawer__content {
  padding: 1rem;
  font-size: 0.9rem;
  line-height: 1.78;
  color: #232826;
}

.report-drawer__content.markdown :deep(h1),
.report-drawer__content.markdown :deep(h2),
.report-drawer__content.markdown :deep(h3) {
  color: #151917;
  line-height: 1.34;
  letter-spacing: -0.03em;
}

.report-drawer__content.markdown :deep(h1) {
  margin: 0 0 0.95rem;
  font-size: 1.34rem;
}

.report-drawer__content.markdown :deep(h2) {
  margin: 1.4rem 0 0.65rem;
  font-size: 1.12rem;
}

.report-drawer__content.markdown :deep(h3) {
  margin: 1rem 0 0.5rem;
  font-size: 0.98rem;
}

.report-drawer__content.markdown :deep(p) {
  margin: 0 0 0.8rem;
}

.report-drawer__content.markdown :deep(blockquote) {
  margin: 0.9rem 0;
  padding-left: 0.9rem;
  border-left: 2px solid rgba(29, 91, 61, 0.18);
}

.report-drawer__content.markdown :deep(code) {
  padding: 0.08rem 0.3rem;
  border-radius: 0.35rem;
  background: rgba(17, 20, 18, 0.05);
}
</style>
```

## frontend\src\components\chat\ProfileEditorDialog.vue

```vue
<template>
  <el-dialog
    :model-value="modelValue"
    :title="editingProfileId == null ? '鏂板缓鍐滄埛鐢诲儚' : '缂栬緫鍐滄埛鐢诲儚'"
    width="720px"
    align-center
    destroy-on-close
    class="profile-dialog"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div v-loading="profileFormLoading" class="profile-dialog__body">
      <div class="profile-dialog__intro">
        <span class="profile-dialog__kicker">鐢诲儚鍙傛暟</span>
        <p>杩欎簺瀛楁浼氳鎸佺画鐢ㄤ簬璧勬牸鏍搁獙銆佽ˉ璐翠及绠椼€佹潯浠剁己鍙ｅ垽鏂笌鍚庣画杩介棶銆?/p>
      </div>

      <el-form :model="localProfileForm" label-width="110px" label-position="left" class="profile-form">
        <section class="profile-group">
          <div class="profile-group__title">鍩虹淇℃伅</div>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="涓讳綋鍚嶇О" required>
                <el-input v-model="localProfileForm.name" placeholder="鍐滄埛濮撳悕鎴栦富浣撳悕绉? clearable />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="涓讳綋绫诲瀷">
                <el-select v-model="localProfileForm.type" placeholder="璇烽€夋嫨" clearable style="width: 100%">
                  <el-option label="瀹跺涵鍐滃満" value="瀹跺涵鍐滃満" />
                  <el-option label="鍐滄皯鍚堜綔绀? value="鍐滄皯鍚堜綔绀? />
                  <el-option label="绉嶆澶ф埛" value="绉嶆澶ф埛" />
                  <el-option label="榫欏ご浼佷笟" value="榫欏ご浼佷笟" />
                  <el-option label="鍏朵粬" value="鍏朵粬" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="缁忚惀闈㈢Н(浜?">
                <el-input-number v-model="localProfileForm.area" :min="0" :max="99999" :precision="1" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="鎵€鍦ㄥ湴鍖?>
                <el-input v-model="localProfileForm.region" placeholder="濡傦細婀栧寳鐪佹姹夊競" clearable />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="缁胯壊璁よ瘉">
                <el-switch v-model="localProfileForm.green_cert" />
                <span class="form-hint">{{ localProfileForm.green_cert ? '宸茶璇? : '鏈璇? }}</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="鐏屾簤鏂瑰紡">
                <el-select v-model="localProfileForm.irrigation" placeholder="璇烽€夋嫨" clearable style="width: 100%">
                  <el-option label="婊寸亴" value="婊寸亴" />
                  <el-option label="鍠风亴" value="鍠风亴" />
                  <el-option label="婕亴" value="婕亴" />
                  <el-option label="鍏朵粬" value="鍏朵粬" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </section>

        <section class="profile-group">
          <div class="profile-group__title">缁忚惀涓庤储鍔?/div>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="骞翠骇鍊?涓囧厓)">
                <el-input-number v-model="localProfileForm.annual_output" :min="0" :max="99999" :precision="2" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="骞存垚鏈?涓囧厓)">
                <el-input-number v-model="localProfileForm.annual_cost" :min="0" :max="99999" :precision="2" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="鏄惁鏈夎捶娆?>
                <el-switch v-model="localProfileForm.has_loan" />
                <span class="form-hint">{{ localProfileForm.has_loan ? '鏈? : '鏃? }}</span>
              </el-form-item>
            </el-col>
            <el-col v-if="localProfileForm.has_loan" :span="12">
              <el-form-item label="璐锋閲戦(涓囧厓)">
                <el-input-number v-model="localProfileForm.loan_amount" :min="0" :max="99999" :precision="2" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="鍙備繚鎯呭喌">
                <el-select v-model="localProfileForm.insurance" placeholder="閫夊～" clearable style="width: 100%">
                  <el-option label="鍐滀笟淇濋櫓" value="鍐滀笟淇濋櫓" />
                  <el-option label="绀句繚" value="绀句繚" />
                  <el-option label="鍟嗕笟闄? value="鍟嗕笟闄? />
                  <el-option label="鍐滀笟淇濋櫓+绀句繚" value="鍐滀笟淇濋櫓+绀句繚" />
                  <el-option label="鏃? value="鏃? />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="缁忚惀骞撮檺(骞?">
                <el-input-number v-model="localProfileForm.operating_years" :min="0" :max="100" :precision="0" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="浠庝笟浜烘暟">
                <el-input-number v-model="localProfileForm.employee_count" :min="0" :max="9999" :precision="0" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
        </section>

        <section class="profile-group">
          <div class="profile-group__title">绉嶆 / 鍏绘畺缁撴瀯</div>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="涓昏惀鍝佺">
                <el-select v-model="localProfileForm.main_crop" placeholder="閫夊～" clearable filterable style="width: 100%">
                  <el-option label="姘寸ɑ" value="姘寸ɑ" />
                  <el-option label="灏忛害" value="灏忛害" />
                  <el-option label="鐜夌背" value="鐜夌背" />
                  <el-option label="钄彍" value="钄彍" />
                  <el-option label="鏋滄爲" value="鏋滄爲" />
                  <el-option label="鐢熺尓" value="鐢熺尓" />
                  <el-option label="瀹剁" value="瀹剁" />
                  <el-option label="姘翠骇" value="姘翠骇" />
                  <el-option label="鍏朵粬" value="鍏朵粬" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="鍦熷湴鎬ц川">
                <el-select v-model="localProfileForm.land_type" placeholder="閫夊～" clearable style="width: 100%">
                  <el-option label="鎵垮寘鍦? value="鎵垮寘鍦? />
                  <el-option label="娴佽浆鍦? value="娴佽浆鍦? />
                  <el-option label="鑷湁" value="鑷湁" />
                  <el-option label="鍏朵粬" value="鍏朵粬" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="璁炬柦绫诲瀷">
                <el-select v-model="localProfileForm.facility_type" placeholder="閫夊～" clearable style="width: 100%">
                  <el-option label="澶ф" value="澶ф" />
                  <el-option label="娓╁" value="娓╁" />
                  <el-option label="闇插ぉ" value="闇插ぉ" />
                  <el-option label="鍏绘畺鍦? value="鍏绘畺鍦? />
                  <el-option label="鍏朵粬" value="鍏朵粬" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="绉嶆/鍏绘畺缁撴瀯">
                <el-input v-model="localProfileForm.crop_structure" type="textarea" :rows="2" placeholder="濡傦細姘寸ɑ 50 浜┿€佽敩鑿?30 浜? clearable />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="澶囨敞">
                <el-input v-model="localProfileForm.note" type="textarea" :rows="2" placeholder="鍏朵粬闇€瑕佽鏄庣殑鎯呭喌" clearable />
              </el-form-item>
            </el-col>
          </el-row>
        </section>
      </el-form>
    </div>

    <template #footer>
      <div class="profile-dialog__footer">
        <el-button @click="$emit('update:modelValue', false)">鍙栨秷</el-button>
        <el-button type="primary" :loading="profileSubmitLoading" @click="$emit('submit')">淇濆瓨鐢诲儚</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  editingProfileId: { type: Number, default: null },
  profileForm: { type: Object, required: true },
  profileFormLoading: { type: Boolean, default: false },
  profileSubmitLoading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'update:profileForm', 'submit'])

function cloneProfileForm(value) {
  return {
    ...(value || {}),
    extra_data:
      value?.extra_data && typeof value.extra_data === 'object'
        ? { ...value.extra_data }
        : {},
  }
}

const localProfileForm = ref(cloneProfileForm(props.profileForm))
let syncingFromProps = false

watch(
  () => props.profileForm,
  (value) => {
    syncingFromProps = true
    localProfileForm.value = cloneProfileForm(value)
  },
  { immediate: true, deep: true },
)

watch(
  localProfileForm,
  (value) => {
    if (syncingFromProps) {
      syncingFromProps = false
      return
    }
    emit('update:profileForm', cloneProfileForm(value))
  },
  { deep: true },
)
</script>

<style scoped>
.profile-dialog__body {
  min-height: 120px;
  max-height: 68vh;
  overflow-y: auto;
  padding-right: 0.2rem;
}

.profile-dialog__intro {
  margin-bottom: 1rem;
}

.profile-dialog__kicker {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.44);
}

.profile-dialog__intro p {
  margin: 0.4rem 0 0;
  font-size: 0.82rem;
  line-height: 1.65;
  color: rgba(17, 20, 18, 0.62);
}

.profile-group + .profile-group {
  margin-top: 1.2rem;
}

.profile-group__title {
  margin-bottom: 0.7rem;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.5);
}

.form-hint {
  margin-left: 0.5rem;
  font-size: 0.8rem;
  color: rgba(17, 20, 18, 0.5);
}

.profile-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.profile-form :deep(.el-form-item) {
  margin-bottom: 0.95rem;
}

.profile-form :deep(.el-input__wrapper),
.profile-form :deep(.el-textarea__inner),
.profile-form :deep(.el-select__wrapper),
.profile-form :deep(.el-input-number) {
  border-radius: 0.9rem;
}
</style>
```

## frontend\src\components\chat\MatchHistoryDialog.vue

```vue
<template>
  <el-dialog
    :model-value="modelValue"
    title="鍖归厤鍘嗗彶"
    width="720px"
    destroy-on-close
    class="history-dialog"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div v-if="loading" class="history-dialog__loading">姝ｅ湪鍔犺浇鍖归厤鍘嗗彶鈥?/div>

    <div v-else-if="data" class="history-dialog__body">
      <div class="history-dialog__intro">
        <span class="history-dialog__kicker">鍘嗗彶璁板綍</span>
        <p>褰撳墠鐢诲儚锛?strong>{{ data.profile?.name || '鏈懡鍚嶇敾鍍? }}</strong></p>
      </div>

      <div v-if="data.match_history?.length" class="history-table-wrap">
        <el-table :data="data.match_history || []" max-height="420" class="history-table">
          <el-table-column prop="policy_id" label="鏀跨瓥 ID" width="96" />
          <el-table-column label="鍖归厤鏃堕棿" width="190">
            <template #default="{ row }">
              {{ row.created_at ? new Date(row.created_at).toLocaleString() : '鏆傛棤' }}
            </template>
          </el-table-column>
          <el-table-column label="鏄惁瀹屽叏鍖归厤" width="120">
            <template #default="{ row }">
              <el-tag :type="row.summary?.fully_matched ? 'success' : 'info'" size="small">
                {{ row.summary?.fully_matched ? '鏄? : '鍚? }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="琛屽姩娓呭崟">
            <template #default="{ row }">
              {{ (row.summary?.action_steps?.length ?? 0) > 0 ? `${row.summary.action_steps?.length ?? 0} 椤筦 : '鏆傛棤' }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-else class="history-dialog__empty">
        璇ョ敾鍍忚繕娌℃湁鍖归厤璁板綍銆傚畬鎴愭斂绛栦綋妫€鍚庯紝鍘嗗彶缁撴灉浼氭矇娣€鍦ㄨ繖閲屻€?      </div>
    </div>
  </el-dialog>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  data: { type: Object, default: null },
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.history-dialog__loading,
.history-dialog__empty {
  padding: 1rem 0.2rem;
  font-size: 0.84rem;
  line-height: 1.7;
  color: rgba(17, 20, 18, 0.58);
}

.history-dialog__intro {
  margin-bottom: 0.9rem;
}

.history-dialog__kicker {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.44);
}

.history-dialog__intro p {
  margin: 0.38rem 0 0;
  font-size: 0.84rem;
  color: rgba(17, 20, 18, 0.66);
}

.history-table-wrap {
  border-radius: 1rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  overflow: hidden;
}

.history-table :deep(th.el-table__cell) {
  background: rgba(247, 248, 245, 0.94);
}
</style>
```

## frontend\src\components\common\SafeRichText.vue

```vue
<template>
  <component :is="tag" v-bind="$attrs" v-html="resolvedHtml" />
</template>

<script setup>
import { computed, watchEffect } from 'vue'

import { renderRichText } from '../../utils/richText'

const props = defineProps({
  content: { type: String, default: undefined },
  sanitizedHtml: { type: String, default: undefined },
  contentMode: {
    type: String,
    default: 'markdown',
    validator(value) {
      return value === 'markdown' || value === 'plain'
    },
  },
  tag: { type: String, default: 'div' },
})

const hasContent = computed(() => props.content !== undefined)
const hasSanitizedHtml = computed(() => props.sanitizedHtml !== undefined)

if (import.meta.env.DEV) {
  watchEffect(() => {
    if (hasContent.value && hasSanitizedHtml.value) {
      console.warn('[SafeRichText] Provide either `content` or `sanitizedHtml`, not both.')
      return
    }
    if (!hasContent.value && !hasSanitizedHtml.value) {
      console.warn('[SafeRichText] Missing rich-text input. Provide `content` or `sanitizedHtml`.')
    }
  })
}

const resolvedHtml = computed(() => {
  if (hasSanitizedHtml.value) return props.sanitizedHtml || ''
  if (hasContent.value) return renderRichText(props.content || '', { contentMode: props.contentMode })
  return ''
})
</script>
```
