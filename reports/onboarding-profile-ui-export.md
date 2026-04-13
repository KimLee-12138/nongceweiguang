# `/onboarding/profile?redirect=/chat` 前端 UI 代码导出

这份文档整理了当前 `http://localhost:5173/onboarding/profile?redirect=/chat` 页面实际涉及的前端代码，方便直接交给 Gemini 做 UI/UX 优化。

## 文件关系

- 页面入口：`frontend/src/views/ProfileOnboardingPage.vue`
- 核心 UI 组件：`frontend/src/components/ProfileOnboarding.vue`
- 路由挂载：`frontend/src/router/index.js`
- 前端接口封装：`frontend/src/api/client.js`

## 1. 页面入口

文件：`frontend/src/views/ProfileOnboardingPage.vue`

```vue
<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import ProfileOnboarding from '../components/ProfileOnboarding.vue'
import { api } from '../api/client'
import { safeInternalRedirectPath } from '../utils/safeRedirect'

const route = useRoute()
const router = useRouter()

function afterPath() {
  return safeInternalRedirectPath(route.query.redirect, '/chat')
}

async function onComplete(payload) {
  try {
    const profiles = await api.withUser(() => api.get('/profiles'))
    const currentProfile = Array.isArray(profiles) ? profiles[0] : null

    if (currentProfile?.id) {
      await api.withUser(() => api.put(`/profiles/${currentProfile.id}`, payload.profile))
      ElMessage.success(`画像已更新${payload.source === 'deepseek' ? '（已智能归一）' : ''}`)
    } else {
      const created = await api.withUser(() => api.post('/profiles', payload.profile))
      ElMessage.success(`画像已创建 #${created.id}${payload.source === 'deepseek' ? '（已智能归一）' : ''}`)
    }

    await router.replace(afterPath())
  } catch (error) {
    ElMessage.error(error?.message || '保存画像失败')
  }
}

function onSkipOrCancel() {
  router.replace(afterPath())
}
</script>

<template>
  <div class="profile-onboarding-page">
    <ProfileOnboarding @complete="onComplete" @skip="onSkipOrCancel" @cancel="onSkipOrCancel" />
  </div>
</template>

<style scoped>
.profile-onboarding-page {
  min-height: 100vh;
  width: 100%;
  margin: 0;
  padding: 0;
  overflow: auto;
}
</style>
```

## 2. 核心 UI 组件

文件：`frontend/src/components/ProfileOnboarding.vue`

```vue
<template>
  <div class="po-root">
    <header class="po-top">
      <div class="po-progress-track">
        <div class="po-progress-fill" :style="{ width: progressPct + '%' }" />
      </div>
      <div class="po-top-row">
        <button type="button" class="po-link" @click="$emit('cancel')">退出</button>
        <button type="button" class="po-link" @click="$emit('skip')">跳过</button>
      </div>
    </header>

    <main class="po-main">
      <Transition name="po-slide" mode="out-in">
        <div v-if="!loadingOverlay" :key="currentIndex" class="po-panel">
          <p v-if="current.subtitle" class="po-sub">{{ current.subtitle }}</p>
          <h1 class="po-title">{{ current.title }}</h1>

          <div v-if="current.kind === 'text'" class="po-text-wrap">
            <input
              v-model.trim="textBuf"
              class="po-input"
              type="text"
              :placeholder="current.placeholder || ''"
              :maxlength="current.maxLen || 120"
              @keydown.enter.prevent="onTextEnter"
            />
          </div>

          <div v-else class="po-grid" :class="'cols-' + (current.cols || 2)">
            <button
              v-for="opt in current.options"
              :key="opt.value"
              type="button"
              class="po-card"
              :class="{
                selected: isSelected(opt.value),
                multi: current.kind === 'multi',
              }"
              @click="onOptionClick(opt.value)"
            >
              <span v-if="opt.icon" class="po-card-icon" aria-hidden="true">{{ opt.icon }}</span>
              <span class="po-card-title">{{ opt.label }}</span>
              <span v-if="opt.desc" class="po-card-desc">{{ opt.desc }}</span>
            </button>
          </div>
        </div>

        <div v-else key="loading" class="po-loading">
          <div class="po-skel-line" />
          <div class="po-skel-line short" />
          <p class="po-loading-text">{{ loadingText }}</p>
        </div>
      </Transition>
    </main>

    <footer class="po-footer">
      <button
        type="button"
        class="po-continue"
        :disabled="!canProceed"
        @click="onContinue"
      >
        {{ isLastStep ? '完成' : '继续' }}
      </button>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { api } from '../api/client'

const props = defineProps({
  useServerRefine: { type: Boolean, default: true },
})

const emit = defineEmits(['complete', 'skip', 'cancel'])

const questions = [
  {
    key: 'q1',
    kind: 'single',
    cols: 2,
    title: '您主要以什么身份开展农业经营？',
    subtitle: '选择最贴近的一项',
    options: [
      { value: 'household', label: '散户 / 普通农户', desc: '家庭分散经营', icon: '🌵' },
      { value: 'family_farm', label: '家庭农场', desc: '经认定的家庭农场', icon: '🏙' },
      { value: 'coop', label: '农民专业合作社', desc: '合作社或联合社', icon: '🫂' },
      { value: 'enterprise', label: '涉农企业', desc: '农业企业或龙头', icon: '🏮' },
    ],
  },
  {
    key: 'q2',
    kind: 'single',
    cols: 2,
    title: '您目前的实际经营面积大概是多少？',
    subtitle: '按耕地与养殖水面合计估算',
    options: [
      { value: 'lt50', label: '50 亩以下', desc: '小规模' },
      { value: '50_200', label: '50–200 亩', desc: '中等规模' },
      { value: '200_500', label: '200–500 亩', desc: '较大规模' },
      { value: 'gt500', label: '500 亩以上', desc: '大规模' },
    ],
  },
  {
    key: 'q3',
    kind: 'multi',
    cols: 2,
    title: '您主要种植或经营哪些品类？',
    subtitle: '可多选',
    options: [
      { value: 'grain', label: '粮食作物', desc: '稻麦玉米等' },
      { value: 'cash', label: '经济作物', desc: '棉油糖等' },
      { value: 'veg_fruit', label: '蔬菜瓜果', desc: '设施或露地' },
      { value: 'aquaculture', label: '水产养殖', desc: '池塘湖泊等' },
      { value: 'livestock', label: '畜禽养殖', desc: '畜舍或放牧' },
    ],
  },
  {
    key: 'q4',
    kind: 'single',
    cols: 2,
    title: '您的农产品是否获得了绿色、有机或地理标志认证？',
    options: [
      { value: 'certified', label: '已获认证', desc: '有效期内' },
      { value: 'pending', label: '正在申请', desc: '材料已提交' },
      { value: 'none', label: '暂无认证', desc: '尚未申请' },
    ],
  },
  {
    key: 'q5',
    kind: 'single',
    cols: 2,
    title: '您目前的农田灌溉方式主要是？',
    options: [
      { value: 'flood', label: '传统漫灌', desc: '沟渠大水' },
      { value: 'drip', label: '滴灌 / 微灌', desc: '节水设施', icon: '🔧' },
      { value: 'sprinkler', label: '喷灌', desc: '移动或固定喷灌', icon: '🚶' },
      { value: 'rainfed', label: '自然靠天', desc: '雨养为主' },
    ],
  },
  {
    key: 'q6',
    kind: 'text',
    title: '给您的经营画像起个简短名称',
    subtitle: '2–12 个字，便于在列表中辨识',
    placeholder: '例如：洪湖稻田基地',
    minLen: 2,
    maxLen: 12,
  },
  {
    key: 'q7',
    kind: 'single',
    cols: 2,
    title: '您所在的县市区更接近哪里？',
    subtitle: '用于匹配区域类政策',
    options: [
      { value: 'honghu', label: '洪湖市' },
      { value: 'jingzhou', label: '荆州市' },
      { value: 'xiangyang', label: '襄阳市' },
      { value: 'yichang', label: '宜昌市' },
      { value: 'huanggang', label: '黄冈市' },
      { value: 'suizhou', label: '随州市' },
      { value: 'wuhan', label: '武汉市' },
      { value: 'hubei_other', label: '省内其他' },
      { value: 'outside', label: '省外' },
    ],
  },
  {
    key: 'q8',
    kind: 'single',
    cols: 2,
    title: '当前最侧重的农业产业是？',
    options: [
      { value: 'grain_oil', label: '粮油作物' },
      { value: 'veg_fruit', label: '蔬菜瓜果' },
      { value: 'forestry_fruit', label: '林果' },
      { value: 'livestock', label: '畜禽' },
      { value: 'aquaculture', label: '水产' },
      { value: 'edible_fungus', label: '食用菌' },
      { value: 'tcm', label: '中药材' },
      { value: 'mixed', label: '混合多种' },
    ],
  },
  {
    key: 'q9',
    kind: 'single',
    cols: 2,
    title: '粮油作物是否占您种植收入的主要部分？',
    options: [
      { value: 'yes', label: '是', desc: '粮油为主' },
      { value: 'no', label: '否', desc: '经济作物或其他为主' },
    ],
  },
  {
    key: 'q10',
    kind: 'single',
    cols: 2,
    title: '若种植林果，主栽品类更接近？',
    subtitle: '不种林果可选「不涉及」',
    options: [
      { value: 'citrus', label: '柑橘类' },
      { value: 'pome', label: '苹果 / 梨 / 桃等' },
      { value: 'na', label: '不涉及' },
      { value: 'other', label: '其他林果' },
    ],
  },
  {
    key: 'q11',
    kind: 'single',
    cols: 2,
    title: '若登记为合作社，示范或规范认定情况是？',
    subtitle: '其他主体请选择「不适用」',
    options: [
      { value: 'provincial', label: '省级示范' },
      { value: 'municipal', label: '市级示范' },
      { value: 'county', label: '县级规范社' },
      { value: 'none', label: '未获评' },
      { value: 'na', label: '不适用' },
    ],
  },
  {
    key: 'q12',
    kind: 'single',
    cols: 2,
    title: '从事当前规模农业经营大约多少年？',
    options: [
      { value: 'lt1', label: '1 年以内' },
      { value: 'y1_3', label: '1–3 年' },
      { value: 'y3_10', label: '3–10 年' },
      { value: 'gt10', label: '10 年以上' },
    ],
  },
  {
    key: 'q13',
    kind: 'single',
    cols: 2,
    title: '农业保险覆盖情况？',
    options: [
      { value: 'full', label: '已投保主要品类' },
      { value: 'partial', label: '部分投保' },
      { value: 'none', label: '尚未投保' },
      { value: 'unknown', label: '不了解' },
    ],
  },
  {
    key: 'q14',
    kind: 'single',
    cols: 2,
    title: '农机与设施化程度？',
    options: [
      { value: 'low', label: '以小型农机为主' },
      { value: 'medium', label: '大中型农机较齐全' },
      { value: 'facility_heavy', label: '设施农业占比较高' },
      { value: 'minimal', label: '机械化较少' },
    ],
  },
  {
    key: 'q15',
    kind: 'single',
    cols: 2,
    title: '经营用地来源？',
    options: [
      { value: 'own_contract', label: '自家承包地为主' },
      { value: 'leased', label: '流转土地为主' },
      { value: 'mixed', label: '承包 + 流转兼有' },
      { value: 'park', label: '以设施园区为主' },
    ],
  },
  {
    key: 'q16',
    kind: 'multi',
    cols: 2,
    title: '产品主要销售渠道？',
    subtitle: '可多选',
    options: [
      { value: 'order', label: '订单农业 / 企业收购' },
      { value: 'wholesale', label: '批发商 / 经纪人' },
      { value: 'retail', label: '本地零售' },
      { value: 'ecommerce', label: '电商与直播' },
      { value: 'processing', label: '初加工后再售' },
    ],
  },
  {
    key: 'q17',
    kind: 'single',
    cols: 2,
    title: '常年雇工人数大致？',
    options: [
      { value: '0', label: '基本不雇工' },
      { value: '1_5', label: '1–5 人' },
      { value: '6_20', label: '6–20 人' },
      { value: 'gt20', label: '20 人以上' },
    ],
  },
  {
    key: 'q18',
    kind: 'single',
    cols: 2,
    title: '近三年是否使用过农业相关贷款或贴息？',
    options: [
      { value: 'active', label: '有，且持续' },
      { value: 'once', label: '有过' },
      { value: 'none', label: '没有' },
      { value: 'unknown', label: '不了解' },
    ],
  },
  {
    key: 'q19',
    kind: 'multi',
    cols: 2,
    title: '您当前更关心哪类支持？',
    subtitle: '可多选',
    options: [
      { value: 'tech', label: '种养殖技术' },
      { value: 'water_smart', label: '节水与智能设施' },
      { value: 'brand_cert', label: '品牌与认证' },
      { value: 'subsidy_compliance', label: '补贴申报与合规' },
      { value: 'market', label: '产销对接' },
    ],
  },
  {
    key: 'q20',
    kind: 'text',
    title: '还有什么希望我们了解的情况？',
    subtitle: '选填',
    placeholder: '可简要补充经营特点、规划等',
    minLen: 0,
    maxLen: 200,
  },
]

const answers = reactive({})
const currentIndex = ref(0)
const loadingOverlay = ref(false)
const loadingText = ref('正在生成您的专属政策画像…')
const textBuf = ref('')
let advanceTimer = null

const current = computed(() => questions[currentIndex.value])
const isLastStep = computed(() => currentIndex.value >= questions.length - 1)
const progressPct = computed(() => ((currentIndex.value + 1) / questions.length) * 100)

function isSelected(value) {
  const k = current.value.key
  const q = answers[k]
  if (current.value.kind === 'multi') {
    return Array.isArray(q) && q.includes(value)
  }
  return q === value
}

function onOptionClick(value) {
  const k = current.value.key
  if (current.value.kind === 'multi') {
    const arr = Array.isArray(answers[k]) ? [...answers[k]] : []
    const i = arr.indexOf(value)
    if (i >= 0) arr.splice(i, 1)
    else arr.push(value)
    answers[k] = arr
    return
  }
  answers[k] = value
  if (current.value.kind === 'single') {
    scheduleAdvance()
  }
}

function scheduleAdvance() {
  if (advanceTimer) clearTimeout(advanceTimer)
  advanceTimer = setTimeout(() => {
    advanceTimer = null
    if (isLastStep.value) {
      finish()
    } else {
      currentIndex.value += 1
      syncTextBuf()
    }
  }, 300)
}

function syncTextBuf() {
  const q = current.value
  if (q.kind === 'text') {
    textBuf.value = answers[q.key] != null ? String(answers[q.key]) : ''
  }
}

watch(currentIndex, () => {
  syncTextBuf()
})

const canProceed = computed(() => {
  const q = current.value
  if (q.kind === 'text') {
    if (q.key === 'q6') {
      const n = (textBuf.value || '').length
      return n >= (q.minLen || 2) && n <= (q.maxLen || 12)
    }
    return true
  }
  if (q.kind === 'multi') {
    return Array.isArray(answers[q.key]) && answers[q.key].length > 0
  }
  return answers[q.key] != null && answers[q.key] !== ''
})

function onContinue() {
  const q = current.value
  if (q.kind === 'text') {
    if (q.key === 'q6' && !canProceed.value) return
    answers[q.key] = q.key === 'q6' ? textBuf.value.trim() : textBuf.value.trim()
  }
  if (!canProceed.value) return
  if (isLastStep.value) {
    finish()
  } else {
    currentIndex.value += 1
    syncTextBuf()
  }
}

function onTextEnter() {
  if (canProceed.value) onContinue()
}

function onKeydown(e) {
  if (e.key !== 'Enter') return
  if (loadingOverlay.value) return
  if (canProceed.value) onContinue()
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  syncTextBuf()
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  if (advanceTimer) clearTimeout(advanceTimer)
})

function collectAnswers() {
  const out = {}
  for (let i = 1; i <= 20; i += 1) {
    const k = `q${i}`
    out[k] = answers[k]
  }
  return out
}

function buildLocalProfile() {
  return buildProfileFromAnswers(collectAnswers())
}

function buildProfileFromAnswers(a) {
  const typeMap = {
    household: '种植户',
    family_farm: '家庭农场',
    coop: '合作社',
    enterprise: '企业',
  }
  const pType = typeMap[a.q1] || '种植户'
  const areaMap = { lt50: 25, '50_200': 125, '200_500': 350, gt500: 600 }
  const area = areaMap[a.q2] ?? 25
  const gcs = a.q4 || 'none'
  const greenCert = gcs === 'certified'
  const greenCertStatus = gcs === 'certified' ? 'certified' : gcs === 'pending' ? 'pending' : 'none'
  const irrMap = { flood: '漫灌', drip: '滴灌', sprinkler: '喷灌', rainfed: '靠天' }
  const irrigation = irrMap[a.q5] || '漫灌'
  let name = (a.q6 || '').trim()
  if (!name) name = `${pType}经营画像`
  const countyMap = {
    honghu: '洪湖市',
    jingzhou: '荆州市',
    xiangyang: '襄阳市',
    yichang: '宜昌市',
    huanggang: '黄冈市',
    suizhou: '随州市',
    wuhan: '武汉市',
    hubei_other: '省内其他',
    outside: '省外',
  }
  const county = countyMap[a.q7] || '省内其他'
  const industryMap = {
    grain_oil: '粮油作物',
    veg_fruit: '蔬菜瓜果',
    forestry_fruit: '林果',
    livestock: '畜禽',
    aquaculture: '水产',
    edible_fungus: '食用菌',
    tcm: '中药材',
    mixed: '混合',
  }
  const industry = industryMap[a.q8] || '混合'
  let grainFocus = a.q9 === 'yes'
  if (industry === '粮油作物') grainFocus = true
  const fruitMap = { citrus: '柑橘', pome: '苹果梨樱桃', na: '不涉及', other: '其他' }
  const fruit = fruitMap[a.q10] || '不涉及'
  const coopMap = {
    provincial: '省级',
    municipal: '市级',
    county: '县级',
    none: '未获评',
    na: '不适用',
  }
  const coopLevel = coopMap[a.q11] || '不适用'
  const yearsMap = { lt1: 'lt1', y1_3: 'y1_3', y3_10: 'y3_10', gt10: 'gt10' }
  const operatingYears = yearsMap[a.q12] || 'y1_3'
  const insMap = { full: 'full', partial: 'partial', none: 'none', unknown: 'unknown' }
  const agriInsurance = insMap[a.q13] || 'unknown'
  const mechMap = {
    low: 'low',
    medium: 'medium',
    facility_heavy: 'facility_heavy',
    minimal: 'minimal',
  }
  const mechanization = mechMap[a.q14] || 'medium'
  const landMap = {
    own_contract: 'own_contract',
    leased: 'leased',
    mixed: 'mixed',
    park: 'park',
  }
  const landTenure = landMap[a.q15] || 'mixed'
  const salesChannels = Array.isArray(a.q16) ? [...a.q16] : []
  const empMap = { '0': '0', '1_5': '1_5', '6_20': '6_20', 'gt20': 'gt20' }
  const employees = empMap[a.q17] || '0'
  const loanMap = { active: 'active', once: 'once', none: 'none', unknown: 'unknown' }
  const loanHistory = loanMap[a.q18] || 'unknown'
  const supportFocus = Array.isArray(a.q19) ? [...a.q19] : []
  const crops = Array.isArray(a.q3) ? [...a.q3] : []
  const userNotes = (a.q20 || '').trim()
  const extraData = {
    crops,
    green_cert_status: greenCertStatus,
    county,
    industry,
    grain_focus: grainFocus,
    fruit,
    coop_level: coopLevel,
    operating_years: operatingYears,
    agri_insurance: agriInsurance,
    mechanization,
    land_tenure: landTenure,
    sales_channels: salesChannels,
    employees,
    loan_history: loanHistory,
    support_focus: supportFocus,
  }
  if (userNotes) extraData.user_notes = userNotes
  return {
    name: name.slice(0, 128),
    type: pType,
    area: Math.max(0, area),
    green_cert: greenCert,
    irrigation,
    extra_data: extraData,
  }
}

async function finish() {
  const q = current.value
  if (q.kind === 'text') {
    answers[q.key] = textBuf.value.trim()
  }
  loadingOverlay.value = true
  const started = Date.now()
  loadingText.value = props.useServerRefine ? '正在智能分析并生成画像…' : '正在生成您的专属政策画像…'
  const raw = collectAnswers()
  let profile = buildLocalProfile()
  let source = 'local'
  try {
    if (props.useServerRefine) {
      const res = await api.withUser(() =>
        api.post('/profiles/onboarding/refine', { answers: raw })
      )
      profile = res.profile
      source = res.source
    }
  } catch {
    profile = buildLocalProfile()
    source = 'local'
  }
  const elapsed = Date.now() - started
  await new Promise((r) => setTimeout(r, Math.max(0, 1500 - elapsed)))
  loadingOverlay.value = false
  emit('complete', { profile, source, answers: raw })
}

defineExpose({ collectAnswers, buildLocalProfile })
</script>

<style scoped>
.po-root {
  --po-bg: #0b0c0f;
  --po-surface: #12141a;
  --po-text: #e8eaef;
  --po-muted: #8b92a7;
  --po-primary: var(--el-color-primary, #5e6ad2);
  --po-ease: cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--po-bg);
  color: var(--po-text);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.po-top {
  padding: 16px 20px 0;
}

.po-progress-track {
  height: 4px;
  border-radius: 999px;
  background: #1e2128;
  overflow: hidden;
}

.po-progress-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--po-primary), #8b5cf6);
  transition: width 0.45s var(--po-ease);
}

.po-top-row {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
}

.po-link {
  background: none;
  border: none;
  color: var(--po-muted);
  font-size: 13px;
  cursor: pointer;
  padding: 4px 0;
}
.po-link:hover {
  color: var(--po-text);
}

.po-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 24px 20px 100px;
  overflow: hidden;
}

.po-panel {
  max-width: 720px;
  margin: 0 auto;
  width: 100%;
}

.po-sub {
  color: var(--po-muted);
  font-size: 14px;
  margin: 0 0 8px;
}

.po-title {
  font-size: clamp(22px, 4vw, 28px);
  font-weight: 600;
  line-height: 1.35;
  margin: 0 0 28px;
  letter-spacing: -0.02em;
}

.po-grid {
  display: grid;
  gap: 12px;
}
.po-grid.cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
@media (min-width: 640px) {
  .po-grid.cols-2 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.po-card {
  text-align: left;
  border: 1px solid #252a35;
  border-radius: 14px;
  padding: 16px 14px;
  background: var(--po-surface);
  color: inherit;
  cursor: pointer;
  transition:
    border-color 0.2s var(--po-ease),
    box-shadow 0.2s var(--po-ease),
    transform 0.18s var(--po-ease);
}
.po-card:hover {
  border-color: #343b4d;
}
.po-card.selected {
  border-color: var(--po-primary);
  box-shadow: 0 0 0 1px var(--po-primary), 0 12px 32px rgba(0, 0, 0, 0.35);
  transform: scale(0.98);
}

.po-card-icon {
  display: block;
  font-size: 22px;
  margin-bottom: 8px;
}
.po-card-title {
  display: block;
  font-weight: 600;
  font-size: 15px;
}
.po-card-desc {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--po-muted);
}

.po-text-wrap {
  margin-top: 8px;
}
.po-input {
  width: 100%;
  box-sizing: border-box;
  padding: 14px 16px;
  border-radius: 12px;
  border: 1px solid #252a35;
  background: #0f1117;
  color: var(--po-text);
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s var(--po-ease);
}
.po-input:focus {
  border-color: var(--po-primary);
}

.po-footer {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 16px 20px 24px;
  background: linear-gradient(180deg, transparent, rgba(11, 12, 15, 0.92) 30%);
}

.po-continue {
  display: block;
  width: 100%;
  max-width: 720px;
  margin: 0 auto;
  padding: 14px 20px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  background: #2a2f3d;
  color: #6c7388;
  transition: background 0.2s var(--po-ease), color 0.2s var(--po-ease);
}
.po-continue:not(:disabled) {
  background: var(--po-primary);
  color: #fff;
}
.po-continue:disabled {
  cursor: not-allowed;
}

.po-loading {
  max-width: 480px;
  margin: 0 auto;
}
.po-skel-line {
  height: 12px;
  border-radius: 6px;
  background: linear-gradient(90deg, #1a1e28, #252a35, #1a1e28);
  background-size: 200% 100%;
  animation: po-shimmer 1.2s ease-in-out infinite;
}
.po-skel-line.short {
  width: 55%;
  margin-top: 12px;
}
.po-loading-text {
  margin-top: 24px;
  text-align: center;
  color: var(--po-muted);
  font-size: 15px;
}
@keyframes po-shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.po-slide-enter-active,
.po-slide-leave-active {
  transition:
    opacity 0.35s var(--po-ease),
    transform 0.35s var(--po-ease);
}
.po-slide-enter-from {
  opacity: 0;
  transform: translateX(28px);
}
.po-slide-leave-to {
  opacity: 0;
  transform: translateX(-24px);
}
</style>
```

## 3. 路由挂载

文件：`frontend/src/router/index.js`

```js
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
      meta: { requiresUser: true, title: '画像问卷' },
    },
    {
      path: '/chat',
      component: () => import('../views/ChatRouteView.vue'),
      meta: { requiresUser: true, title: '政策对话工作台' },
    },
    { path: '/insights', component: () => import('../views/InsightsPage.vue') },
    { path: '/compass', component: () => import('../views/CompassPage.vue') },
    { path: '/login', component: () => import('../views/LoginPage.vue') },
    { path: '/register', component: () => import('../views/RegisterPage.vue') },
    { path: '/sessions', component: () => import('../views/SessionsPage.vue'), meta: { requiresUser: true } },
    {
      path: '/admin/login',
      name: 'AdminLogin',
      component: () => import('../views/admin/AdminLogin.vue'),
      meta: { title: '管理员登录', public: true },
    },
    {
      path: '/admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      meta: { requiresAdmin: true },
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
            title: '导入与爬取',
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
```

## 4. 前端接口封装

文件：`frontend/src/api/client.js`

```js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const authEvents = new EventTarget()

function createNetworkError(path, cause) {
  const usingDevProxy = API_BASE_URL.startsWith('/')
  const message = usingDevProxy
    ? '无法连接后端服务，请确认前端通过 Vite 启动，并且后端 API 已运行在 http://127.0.0.1:8000。'
    : `无法连接后端服务，请检查 API 地址 ${API_BASE_URL} 是否可访问。`
  const err = new Error(message)
  err.status = 0
  err.code = 'NETWORK_ERROR'
  err.isNetworkError = true
  err.path = path
  err.cause = cause
  return err
}

function messageFromErrorBody(body) {
  if (typeof body === 'string') return body || '请求失败'
  if (!body || typeof body !== 'object') return '请求失败'
  const d = body.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) {
    const parts = d.map((x) => (typeof x?.msg === 'string' ? x.msg : JSON.stringify(x)))
    return parts.filter(Boolean).join('；') || '请求失败'
  }
  return '请求失败'
}

async function rawFetch(path, options = {}) {
  const headers = new Headers(options.headers || {})
  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData
  if (!isFormData && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      credentials: 'include',
      headers,
    })
    return res
  } catch (error) {
    throw createNetworkError(path, error)
  }
}

async function fetchJson(path, options = {}) {
  const res = await rawFetch(path, options)
  const contentType = res.headers.get('content-type') || ''
  const body = contentType.includes('application/json') ? await res.json() : await res.text()
  if (!res.ok) {
    const msg = messageFromErrorBody(body)
    const err = new Error(msg)
    err.status = res.status
    err.body = body
    throw err
  }
  return body
}

async function withAutoRefresh(role, fn) {
  try {
    return await fn()
  } catch (e) {
    if (e?.status !== 401) throw e
    try {
      if (role === 'admin') {
        await fetchJson('/auth/refresh', { method: 'POST' })
      } else {
        await fetchJson('/user-auth/refresh', { method: 'POST' })
      }
      return await fn()
    } catch (refreshErr) {
      authEvents.dispatchEvent(
        new CustomEvent('auth:refresh_failed', {
          detail: { role, error: refreshErr?.message || 'refresh_failed' },
        })
      )
      throw e
    }
  }
}

export const api = {
  get: (path) => fetchJson(path, { method: 'GET' }),
  post: (path, data) => fetchJson(path, { method: 'POST', body: JSON.stringify(data ?? {}) }),
  put: (path, data) => fetchJson(path, { method: 'PUT', body: JSON.stringify(data ?? {}) }),
  patch: (path, data) => fetchJson(path, { method: 'PATCH', body: JSON.stringify(data ?? {}) }),
  del: (path) => fetchJson(path, { method: 'DELETE' }),
  withUser: (fn) => withAutoRefresh('user', fn),
  withAdmin: (fn) => withAutoRefresh('admin', fn),
  baseUrl: API_BASE_URL,
  rawFetch,
}
```

## 5. 给 Gemini 的建议提示词

可以直接附上这段说明一起发给 Gemini：

```text
这是当前 /onboarding/profile?redirect=/chat 页面实际使用的 Vue 3 + Element Plus 前端代码。

请你重点优化：
1. 问卷页整体视觉层次、排版和品牌感
2. 每一步卡片选择的可读性、点击反馈和移动端体验
3. 顶部进度条、底部继续按钮、加载态的高级感
4. 保持现有业务逻辑不变，只优化前端 UI/UX 和必要的组件结构
5. 输出可直接替换的 Vue 单文件组件代码

约束：
- 保留 Vue 3 `<script setup>`
- 保留当前问卷数据结构 questions
- 保留 complete / skip / cancel 事件
- 保留调用 `/profiles/onboarding/refine` 和页面完成后的保存逻辑
```
