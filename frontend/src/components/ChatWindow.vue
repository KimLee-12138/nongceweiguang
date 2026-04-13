<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import ChatWorkbenchShell from './chat/ChatWorkbenchShell.vue'
import ChatMessagePane from './chat/ChatMessagePane.vue'
import ChatComposer from './chat/ChatComposer.vue'
import ProfileEditorDialog from './chat/ProfileEditorDialog.vue'
import { api } from '../api/client'

const router = useRouter()

const profiles = ref([])
const policies = ref([])
const conversations = ref([])
const selectedProfileId = ref(null)
const selectedPolicyId = ref(null)
const conversationId = ref(null)
const messages = ref([])
const input = ref('')
const streaming = ref(false)
const chatMode = ref('interpret')

const isCompactLayout = ref(false)
const leftPanelVisible = ref(false)
let mql

const profileEditorVisible = ref(false)
const editorProfile = ref(null)
const editorSubmitting = ref(false)
const policySource = ref('all')
const TYPEWRITER_DELAY_MS = 8

const quickQuestions = [
  '我只有 10 亩地，能申报什么补贴？',
  '绿色认证补贴的流程是什么？',
  '滴灌设施改造有补贴吗？',
  '合作社资质怎么办理？',
]

function updateCompact() {
  isCompactLayout.value = typeof window !== 'undefined' && window.matchMedia('(max-width: 1180px)').matches
}

const currentProfile = computed(() => profiles.value.find((item) => item.id === selectedProfileId.value) ?? profiles.value[0] ?? null)
const currentProfileName = computed(() => currentProfile.value?.name ?? '')

const citedPolicy = computed(() => {
  if (!selectedPolicyId.value) return null
  const policy = policies.value.find((item) => item.id === selectedPolicyId.value)
  return policy ? { id: policy.id, title: policy.title } : null
})

const citedPolicyTitle = computed(() => citedPolicy.value?.title ?? '')

const shellModeLabel = computed(() => {
  if (chatMode.value === 'match') return '政策智能匹配'
  if (chatMode.value === 'agri_llm') return '农业政策大模型'
  return '政策白话解读'
})

const shellModeTone = computed(() => {
  if (chatMode.value === 'match') {
    return '围绕唯一画像做政策适配、门槛体检与申报规划。'
  }
  if (chatMode.value === 'agri_llm') {
    return '聚焦农业政策问答，可带画像与已选政策作为附加上下文。'
  }
  return '聚焦政策白话解释、适用对象与申报流程。'
})

const policyModeHint = computed(() => {
  if (chatMode.value === 'agri_llm') return '可选政策上下文'
  if (chatMode.value === 'interpret') return '白话解读需先选政策'
  return '智能匹配需选政策'
})

async function loadProfiles() {
  const loaded = await api.withUser(() => api.get('/profiles'))
  profiles.value = Array.isArray(loaded) ? loaded : []
  if (!profiles.value.length) {
    selectedProfileId.value = null
    return
  }
  const onlyProfile = profiles.value[0]
  if (!profiles.value.some((item) => item.id === selectedProfileId.value)) {
    selectedProfileId.value = onlyProfile.id
  }
}

async function loadPolicies() {
  if (selectedProfileId.value) {
    try {
      const recommendation = await api.withUser(() =>
        api.get(`/profiles/${selectedProfileId.value}/suggested-policies?limit=50`)
      )
      const items = Array.isArray(recommendation?.items) ? recommendation.items : []
      policies.value = items.map((item) => ({
        ...item,
        id: item.policy_id,
      }))
      policySource.value = 'recommended'
    } catch {
      policies.value = []
      policySource.value = 'all'
    }
  }
  if (!policies.value.length) {
    policies.value = await api.get('/policies')
    policySource.value = 'all'
  }
  if (!selectedPolicyId.value && policies.value.length) {
    selectedPolicyId.value = policies.value[0].id
  }
  if (selectedPolicyId.value && !policies.value.some((policy) => policy.id === selectedPolicyId.value)) {
    selectedPolicyId.value = policies.value[0]?.id ?? null
  }
}

async function loadConversations() {
  try {
    conversations.value = await api.withUser(() => api.get('/chat/conversations'))
  } catch {
    conversations.value = []
  }
}

async function createConversation() {
  try {
    const conversation = await api.withUser(() => api.post('/chat/conversations'))
    conversations.value = [conversation, ...conversations.value.filter((item) => item.id !== conversation.id)]
    conversationId.value = conversation.id
    messages.value = []
    leftPanelVisible.value = false
    ElMessage.success('已新建会话')
  } catch (error) {
    ElMessage.error(error?.message || '新建会话失败')
  }
}

async function switchConversation(item) {
  if (!item?.id) return
  try {
    const detail = await api.withUser(() => api.get(`/chat/conversations/${item.id}`))
    conversationId.value = detail.conversation.id

    const effectiveProfileId = profiles.value[0]?.id ?? null
    if (detail.conversation.last_profile_id && profiles.value.some((profile) => profile.id === detail.conversation.last_profile_id)) {
      selectedProfileId.value = detail.conversation.last_profile_id
    } else {
      selectedProfileId.value = effectiveProfileId
    }
    if (['match', 'agri_llm', 'interpret'].includes(detail.conversation.last_mode)) {
      chatMode.value = detail.conversation.last_mode
    }

    messages.value = (detail.messages || [])
      .filter((message) => message.role === 'user' || message.role === 'assistant')
      .map((message) => ({
        id: message.id,
        role: message.role,
        content: message.content || '',
      }))

    leftPanelVisible.value = false
  } catch (error) {
    ElMessage.error(error?.message || '加载会话失败')
  }
}

async function deleteConversation(item) {
  if (!item?.id) return
  try {
    await ElMessageBox.confirm('确定删除该会话？删除后无法恢复。', '删除会话', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  try {
    await api.withUser(() => api.del(`/chat/conversations/${item.id}`))
    conversations.value = conversations.value.filter((c) => c.id !== item.id)
    if (conversationId.value === item.id) {
      conversationId.value = null
      messages.value = []
      const next = conversations.value[0]
      if (next) {
        await switchConversation(next)
      }
    }
    ElMessage.success('已删除会话')
  } catch (error) {
    ElMessage.error(error?.message || '删除失败')
  }
}

function manageProfiles() {
  editorProfile.value = currentProfile.value ? { ...currentProfile.value } : null
  profileEditorVisible.value = true
}

async function onProfileSubmit(payload) {
  if (!payload?.id) {
    goOnboarding()
    profileEditorVisible.value = false
    return
  }

  editorSubmitting.value = true
  try {
    const { id, ...body } = payload
    await api.withUser(() => api.put(`/profiles/${id}`, body))
    ElMessage.success('画像已更新')
    profileEditorVisible.value = false
    await loadProfiles()
    editorProfile.value = profiles.value[0] ? { ...profiles.value[0] } : null
  } catch (error) {
    ElMessage.error(error?.message || '保存失败')
  } finally {
    editorSubmitting.value = false
  }
}

function goOnboarding() {
  profileEditorVisible.value = false
  router.push({ path: '/onboarding/profile', query: { redirect: '/chat' } })
}

async function matchNow() {
  if (!selectedProfileId.value || !selectedPolicyId.value) {
    ElMessage.warning('请先准备好当前画像和政策')
    return
  }
  try {
    const result = await api.withUser(() =>
      api.post(`/policies/${selectedPolicyId.value}/match-for-profile/${selectedProfileId.value}`)
    )
    ElMessage.success('已生成体检结果并写入历史')
    messages.value.push({
      role: 'assistant',
      content: `【体检结果】\nfully_matched=${result.summary.fully_matched}\nfailed_must=${result.summary.failed_must_nodes.length}`,
    })
  } catch (error) {
    ElMessage.error(error?.message || '体检失败')
  }
}

async function send() {
  if (!input.value.trim() || streaming.value) return
  if (chatMode.value === 'match' && !selectedProfileId.value) {
    ElMessage.warning('请先通过问卷创建你的唯一画像')
    return
  }
  if ((chatMode.value === 'match' || chatMode.value === 'interpret') && !selectedPolicyId.value) {
    ElMessage.warning(chatMode.value === 'interpret' ? '政策白话解读必须先选择政策' : '政策智能匹配必须先选择政策')
    return
  }

  const messageText = input.value
  input.value = ''
  messages.value.push({ role: 'user', content: messageText })

  streaming.value = true
  const profileId = selectedProfileId.value || null
  const policyId = selectedPolicyId.value || null
  const body = {
    conversation_id: conversationId.value,
    message: messageText,
    mode: chatMode.value,
    profile_id: profileId,
    policy_id: policyId,
  }
  const streamPath = chatMode.value === 'agri_llm' ? '/chat/agri-llm/stream' : '/chat/stream'

  try {
    const response = await api.rawFetch(streamPath, { method: 'POST', body: JSON.stringify(body) })
    if (!response.ok) {
      const text = await response.text()
      streaming.value = false
      messages.value.pop()
      throw new Error(text)
    }

    const current = { role: 'assistant', content: '' }
    messages.value.push(current)
    let typewriterChain = Promise.resolve()
    const enqueueTypewriter = (text) => {
      const raw = typeof text === 'string' ? text : String(text || '')
      if (!raw) return
      typewriterChain = typewriterChain.then(async () => {
        for (const ch of raw) {
          current.content += ch
          await sleep(TYPEWRITER_DELAY_MS)
        }
      })
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      const parts = buffer.split('\n\n')
      buffer = parts.pop() || ''

      for (const part of parts) {
        const lines = part.split('\n')
        const eventLine = lines.find((line) => line.startsWith('event:'))
        const dataLine = lines.find((line) => line.startsWith('data:'))
        const event = eventLine ? eventLine.replace('event:', '').trim() : 'message'
        const dataString = dataLine ? dataLine.replace('data:', '').trim() : '{}'
        let data

        try {
          data = JSON.parse(dataString)
        } catch {
          data = { raw: dataString }
        }

        if (event === 'message_meta') {
          conversationId.value = data.conversation_id
          await loadConversations()
        }
        if (event === 'content') {
          enqueueTypewriter(data.delta || '')
        }
      }
    }
    await typewriterChain
  } catch (error) {
    ElMessage.error(error?.message || '发送失败')
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage?.role === 'assistant' && !lastMessage.content) {
      messages.value.pop()
    }
  } finally {
    streaming.value = false
  }
}

function useQuickQuestion(question) {
  input.value = question
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function policyLabel(policy) {
  const scoreValue = Number(policy?.score ?? policy?.match_score ?? 0)
  if (!Number.isFinite(scoreValue) || policySource.value !== 'recommended') {
    return `#${policy.id} ${policy.title}`
  }
  return `#${policy.id} ${policy.title} · 推荐度 ${Math.round(scoreValue * 100)}%`
}

watch(
  () => selectedProfileId.value,
  async (next, prev) => {
    if (next !== prev) {
      await loadPolicies()
    }
  }
)

onMounted(async () => {
  updateCompact()
  mql = window.matchMedia('(max-width: 1180px)')
  mql.addEventListener('change', updateCompact)
  await loadProfiles()
  await loadPolicies()
  await loadConversations()
})

onBeforeUnmount(() => {
  mql?.removeEventListener('change', updateCompact)
})
</script>

<template>
  <div class="chat-window-root">
    <ChatWorkbenchShell
      v-model:left-panel-visible="leftPanelVisible"
      :is-compact-layout="isCompactLayout"
      :current-profile="currentProfile"
      :recent-conversations="conversations"
      :current-conversation-id="conversationId"
      :current-profile-name="currentProfileName"
      :cited-policy-title="citedPolicyTitle"
      :mode-label="shellModeLabel"
      :current-mode-tone="shellModeTone"
      @create-conversation="createConversation"
      @manage-profiles="manageProfiles"
      @switch-conversation="switchConversation"
      @delete-conversation="deleteConversation"
      @go-onboarding="goOnboarding"
    >
      <div class="center-stack">
        <div class="policy-toolbar">
          <div class="policy-toolbar__row">
            <span class="policy-toolbar__label">当前政策</span>
            <span class="policy-toolbar__hint">{{ policySource === 'recommended' ? '按画像推荐' : '全部政策' }}</span>
            <span class="policy-toolbar__hint">{{ policyModeHint }}</span>
            <el-select v-model="selectedPolicyId" placeholder="选择政策" class="policy-toolbar__select" filterable>
              <el-option v-for="policy in policies" :key="policy.id" :label="policyLabel(policy)" :value="policy.id" />
            </el-select>
            <el-button type="primary" @click="matchNow">立即体检</el-button>
            <el-button @click="loadPolicies">刷新政策</el-button>
          </div>
        </div>

        <ChatMessagePane
          :messages="messages"
          :quick-questions="quickQuestions"
          :streaming="streaming"
          @use-quick-question="useQuickQuestion"
        />

        <ChatComposer
          v-model="input"
          :streaming="streaming"
          :cited-policy="citedPolicy"
          :current-profile="currentProfile"
          :current-profile-name="currentProfileName"
          :chat-mode="chatMode"
          @change-mode="chatMode = $event"
          @clear-citation="selectedPolicyId = null"
          @send="send"
          @submit-enter="send"
        />
      </div>
    </ChatWorkbenchShell>

    <ProfileEditorDialog
      v-model="profileEditorVisible"
      :profile="editorProfile"
      :submit-loading="editorSubmitting"
      @submit="onProfileSubmit"
      @go-onboarding="goOnboarding"
    />
  </div>
</template>

<style scoped>
.chat-window-root {
  height: 100%;
  min-height: 100vh;
  overflow: hidden;
}

.center-stack {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.policy-toolbar {
  flex-shrink: 0;
  padding: 0.65rem 1.4rem 0.5rem;
  border-bottom: 1px solid rgba(18, 24, 22, 0.06);
  background: rgba(255, 255, 255, 0.55);
}

.policy-toolbar__row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem;
  max-width: 56rem;
  margin: 0 auto;
}

.policy-toolbar__label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.46);
}

.policy-toolbar__hint {
  font-size: 0.76rem;
  color: rgba(17, 20, 18, 0.62);
}

.policy-toolbar__select {
  flex: 1 1 200px;
  min-width: 160px;
  max-width: 28rem;
}
</style>
