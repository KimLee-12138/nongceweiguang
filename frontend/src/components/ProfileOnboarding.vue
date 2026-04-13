<template>
  <div class="onboarding-container">
    <header v-if="!loadingOverlay" class="onboarding-header">
      <div class="nav-bar">
        <button type="button" class="icon-btn" title="退出" @click="handleExit">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <div class="progress-wrapper">
          <div class="progress-bar" :style="{ width: progressPct + '%' }" />
        </div>
        <button type="button" class="skip-btn" @click="$emit('skip')">跳过</button>
      </div>
    </header>

    <main v-if="!loadingOverlay" class="question-main">
      <Transition name="slide-fade" mode="out-in">
        <div :key="currentIndex" class="question-wrapper">
          <template v-if="current.kind === 'text'">
            <h1 class="question-title">{{ current.title }}</h1>
            <p v-if="current.subtitle" class="question-subtitle">{{ current.subtitle }}</p>
            <div class="text-field-wrap">
              <input
                v-model.trim="textBuf"
                class="text-field"
                type="text"
                :placeholder="current.placeholder || ''"
                :maxlength="current.maxLen || 200"
                @keydown.enter.prevent="onTextEnter"
              />
            </div>
          </template>

          <template v-else>
            <h1 class="question-title">{{ current.title }}</h1>
            <p v-if="current.subtitle" class="question-subtitle">{{ current.subtitle }}</p>

            <div class="options-grid" :class="{ 'multi-col': (current.options?.length || 0) > 4 }">
              <div
                v-for="option in current.options"
                :key="option.value"
                class="option-card"
                :class="{ 'is-selected': isSelected(option.value) }"
                role="button"
                tabindex="0"
                @click="onOptionClick(option.value)"
                @keydown.enter.prevent="onOptionClick(option.value)"
              >
                <div class="card-content">
                  <span v-if="option.icon" class="option-icon" aria-hidden="true">{{ option.icon }}</span>
                  <div class="text-group">
                    <span class="option-label">{{ option.label }}</span>
                    <span v-if="option.desc" class="option-desc">{{ option.desc }}</span>
                  </div>
                </div>
                <div class="check-circle">
                  <svg
                    v-if="isSelected(option.value)"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    aria-hidden="true"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
            </div>
          </template>
        </div>
      </Transition>
    </main>

    <footer v-if="!loadingOverlay" class="onboarding-footer">
      <button type="button" class="continue-btn" :class="{ 'is-active': canProceed }" :disabled="!canProceed" @click="onContinue">
        {{ isLastStep ? '生成政策画像' : '继续' }}
      </button>
    </footer>

    <Transition name="fade">
      <div v-if="loadingOverlay" class="loading-overlay">
        <div class="spinner" />
        <h2 class="loading-title">{{ loadingText }}</h2>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { api } from '../api/client'
import { buildProfilePayloadFromForm } from '../constants/profileFormSchema'

const props = defineProps({
  useServerRefine: { type: Boolean, default: true },
})

const emit = defineEmits(['complete', 'skip', 'cancel'])

function handleExit() {
  emit('cancel')
}

const questions = [
  {
    key: 'q1',
    kind: 'single',
    title: '您主要以什么身份开展农业经营？',
    subtitle: '选择最贴近的一项',
    options: [
      { value: 'household', label: '散户 / 普通农户', desc: '家庭分散经营', icon: '🌾' },
      { value: 'family_farm', label: '家庭农场', desc: '经认定的家庭农场', icon: '🚜' },
      { value: 'coop', label: '农民专业合作社', desc: '合作社或联合社', icon: '🤝' },
      { value: 'enterprise', label: '涉农企业', desc: '农业企业或龙头', icon: '🏢' },
    ],
  },
  {
    key: 'q2',
    kind: 'single',
    title: '您目前的实际经营面积大概是多少？',
    subtitle: '按耕地与养殖水面合计估算',
    options: [
      { value: 'lt50', label: '50 亩以下', desc: '小规模' },
      { value: '50_200', label: '50-200 亩', desc: '中等规模' },
      { value: '200_500', label: '200-500 亩', desc: '较大规模' },
      { value: 'gt500', label: '500 亩以上', desc: '大规模' },
    ],
  },
  {
    key: 'q3',
    kind: 'multi',
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
    title: '您目前的农田灌溉方式主要是？',
    options: [
      { value: 'flood', label: '传统漫灌', desc: '沟渠大水' },
      { value: 'drip', label: '滴灌 / 微灌', desc: '节水设施', icon: '💧' },
      { value: 'sprinkler', label: '喷灌', desc: '移动或固定喷灌', icon: '🚿' },
      { value: 'rainfed', label: '自然靠天', desc: '雨养为主' },
    ],
  },
  {
    key: 'q6',
    kind: 'text',
    title: '给您的经营画像起个简短名称',
    subtitle: '2-12 个字，便于在列表中辨识',
    placeholder: '例如：洪湖稻田基地',
    minLen: 2,
    maxLen: 12,
  },
  {
    key: 'q7',
    kind: 'single',
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
    title: '粮油作物是否占您种植收入的主要部分？',
    options: [
      { value: 'yes', label: '是', desc: '粮油为主' },
      { value: 'no', label: '否', desc: '经济作物或其他为主' },
    ],
  },
  {
    key: 'q10',
    kind: 'single',
    title: '若种植林果，主栽品类更接近？',
    subtitle: '不种林果可选“不涉及”',
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
    title: '若登记为合作社，示范或规范认定情况是？',
    subtitle: '其他主体请选择“不适用”',
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
    title: '从事当前规模农业经营大约多少年？',
    options: [
      { value: 'lt1', label: '1 年以内' },
      { value: 'y1_3', label: '1-3 年' },
      { value: 'y3_10', label: '3-10 年' },
      { value: 'gt10', label: '10 年以上' },
    ],
  },
  {
    key: 'q13',
    kind: 'single',
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
    title: '常年雇工人数大致？',
    options: [
      { value: '0', label: '基本不雇工' },
      { value: '1_5', label: '1-5 人' },
      { value: '6_20', label: '6-20 人' },
      { value: 'gt20', label: '20 人以上' },
    ],
  },
  {
    key: 'q18',
    kind: 'single',
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
const loadingText = ref('正在为您生成专属农业画像…')
const textBuf = ref('')
let advanceTimer = null

const current = computed(() => questions[currentIndex.value])
const isLastStep = computed(() => currentIndex.value >= questions.length - 1)
const progressPct = computed(() => ((currentIndex.value + 1) / questions.length) * 100)

function isSelected(value) {
  const answer = answers[current.value.key]
  if (current.value.kind === 'multi') {
    return Array.isArray(answer) && answer.includes(value)
  }
  return answer === value
}

function onOptionClick(value) {
  const key = current.value.key
  if (current.value.kind === 'multi') {
    const next = Array.isArray(answers[key]) ? [...answers[key]] : []
    const index = next.indexOf(value)
    if (index >= 0) next.splice(index, 1)
    else next.push(value)
    answers[key] = next
    return
  }
  answers[key] = value
  if (current.value.kind === 'single') scheduleAdvance()
}

function scheduleAdvance() {
  if (advanceTimer) clearTimeout(advanceTimer)
  advanceTimer = setTimeout(() => {
    advanceTimer = null
    if (isLastStep.value) finish()
    else {
      currentIndex.value += 1
      syncTextBuf()
    }
  }, 350)
}

function syncTextBuf() {
  if (current.value.kind === 'text') {
    textBuf.value = answers[current.value.key] != null ? String(answers[current.value.key]) : ''
  }
}

watch(currentIndex, syncTextBuf)

const canProceed = computed(() => {
  if (current.value.kind === 'text') {
    if (current.value.key === 'q6') {
      const length = (textBuf.value || '').length
      return length >= (current.value.minLen || 2) && length <= (current.value.maxLen || 12)
    }
    return true
  }
  if (current.value.kind === 'multi') {
    return Array.isArray(answers[current.value.key]) && answers[current.value.key].length > 0
  }
  return answers[current.value.key] != null && answers[current.value.key] !== ''
})

function onContinue() {
  if (current.value.kind === 'text') {
    if (current.value.key === 'q6' && !canProceed.value) return
    answers[current.value.key] = textBuf.value.trim()
  }
  if (!canProceed.value) return
  if (isLastStep.value) finish()
  else {
    currentIndex.value += 1
    syncTextBuf()
  }
}

function onTextEnter() {
  if (canProceed.value) onContinue()
}

function onKeydown(event) {
  if (event.key !== 'Enter' || loadingOverlay.value) return
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
  const result = {}
  for (let index = 1; index <= 20; index += 1) {
    result[`q${index}`] = answers[`q${index}`]
  }
  return result
}

function buildProfileFromAnswers(answerMap) {
  const typeMap = {
    household: '种植户',
    family_farm: '家庭农场',
    coop: '合作社',
    enterprise: '企业',
  }
  const areaMap = { lt50: 25, '50_200': 125, '200_500': 350, gt500: 600 }
  const irrigationMap = { flood: '漫灌', drip: '滴灌', sprinkler: '喷灌', rainfed: '靠天' }
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
  const fruitMap = { citrus: '柑橘', pome: '苹果梨樱桃', na: '不涉及', other: '其他' }
  const coopMap = {
    provincial: '省级',
    municipal: '市级',
    county: '县级',
    none: '未获评',
    na: '不适用',
  }

  const form = {
    name: ((answerMap.q6 || '').trim() || `${typeMap[answerMap.q1] || '种植户'}经营画像`).slice(0, 128),
    type: typeMap[answerMap.q1] || '种植户',
    area: Math.max(0, areaMap[answerMap.q2] ?? 25),
    green_cert: answerMap.q4 === 'certified',
    irrigation: irrigationMap[answerMap.q5] || '漫灌',
    county: countyMap[answerMap.q7] || '省内其他',
    industry: industryMap[answerMap.q8] || '混合',
    operating_years: answerMap.q12 || 'y1_3',
    land_tenure: answerMap.q15 || 'mixed',
    green_cert_status: answerMap.q4 || 'none',
    mechanization: answerMap.q14 || 'medium',
    grain_focus: answerMap.q8 === 'grain_oil' ? true : answerMap.q9 === 'yes',
    fruit: fruitMap[answerMap.q10] || '不涉及',
    crops: Array.isArray(answerMap.q3) ? [...answerMap.q3] : [],
    coop_level: coopMap[answerMap.q11] || '不适用',
    sales_channels: Array.isArray(answerMap.q16) ? [...answerMap.q16] : [],
    employees: answerMap.q17 || '0',
    loan_history: answerMap.q18 || 'unknown',
    agri_insurance: answerMap.q13 || 'unknown',
    support_focus: Array.isArray(answerMap.q19) ? [...answerMap.q19] : [],
    user_notes: (answerMap.q20 || '').trim(),
  }

  return buildProfilePayloadFromForm(form)
}

function buildLocalProfile() {
  return buildProfileFromAnswers(collectAnswers())
}

async function finish() {
  if (current.value.kind === 'text') {
    answers[current.value.key] = textBuf.value.trim()
  }

  loadingOverlay.value = true
  const startedAt = Date.now()
  loadingText.value = props.useServerRefine ? '正在智能分析并生成画像…' : '正在为您生成专属农业画像…'

  const rawAnswers = collectAnswers()
  let profile = buildLocalProfile()
  let source = 'local'

  try {
    if (props.useServerRefine) {
      const result = await api.withUser(() => api.post('/profiles/onboarding/refine', { answers: rawAnswers }))
      profile = result.profile
      source = result.source
    }
  } catch {
    profile = buildLocalProfile()
    source = 'local'
  }

  const elapsed = Date.now() - startedAt
  await new Promise((resolve) => setTimeout(resolve, Math.max(0, 1500 - elapsed)))
  loadingOverlay.value = false
  emit('complete', { profile, source, answers: rawAnswers })
}

defineExpose({ collectAnswers, buildLocalProfile })
</script>

<style scoped>
.onboarding-container {
  --primary-green: #1a4d2e;
  --primary-green-light: #e8f3ec;
  --bg-color: #fbfbfd;
  --text-main: #1d1d1f;
  --text-secondary: #86868b;
  --card-bg: #ffffff;
  --card-border: #e5e5ea;
  --spring-easing: cubic-bezier(0.34, 1.56, 0.64, 1);

  height: 100vh;
  min-height: 100vh;
  width: 100%;
  background-color: var(--bg-color);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family:
    -apple-system,
    BlinkMacSystemFont,
    'SF Pro Text',
    'Segoe UI',
    Roboto,
    'Noto Sans SC',
    Helvetica,
    Arial,
    sans-serif;
}

.onboarding-header {
  flex-shrink: 0;
  padding: 20px 24px 12px;
  background: transparent;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 800px;
  margin: 0 auto;
}

.progress-wrapper {
  flex: 1;
  height: 12px;
  background-color: #e5e5ea;
  border-radius: 100px;
  margin: 0 24px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: var(--primary-green);
  border-radius: 100px;
  transition: width 0.6s var(--spring-easing);
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  width: 32px;
  height: 32px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: color 0.2s;
  border-radius: 8px;
}

.icon-btn:hover {
  color: var(--text-main);
  background: rgba(0, 0, 0, 0.04);
}

.icon-btn svg {
  width: 22px;
  height: 22px;
  display: block;
}

.skip-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary);
  padding: 6px 4px;
  min-width: 48px;
  text-align: right;
}

.skip-btn:hover {
  color: var(--primary-green);
}

.question-main {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 20px 24px;
  overflow: auto;
  -webkit-overflow-scrolling: touch;
}

.question-wrapper {
  max-width: 600px;
  width: 100%;
  text-align: left;
}

.question-title {
  font-size: clamp(26px, 5vw, 32px);
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: -0.5px;
  margin: 0 0 8px;
  line-height: 1.3;
}

.question-subtitle {
  font-size: 17px;
  color: var(--text-secondary);
  margin: 0 0 28px;
  line-height: 1.45;
}

.text-field-wrap {
  margin-top: 8px;
}

.text-field {
  width: 100%;
  box-sizing: border-box;
  padding: 18px 20px;
  border-radius: 16px;
  border: 2px solid var(--card-border);
  background: var(--card-bg);
  color: var(--text-main);
  font-size: 17px;
  outline: none;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.text-field:focus {
  border-color: var(--primary-green);
  box-shadow: 0 0 0 3px var(--primary-green-light);
}

.options-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: 1fr;
}

.options-grid.multi-col {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.option-card {
  background-color: var(--card-bg);
  border: 2px solid var(--card-border);
  border-radius: 20px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.2s var(--spring-easing);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  user-select: none;
}

.option-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.05);
  border-color: #d1d1d6;
}

.option-card:active {
  transform: scale(0.97);
}

.option-card.is-selected {
  border-color: var(--primary-green);
  background-color: var(--primary-green-light);
  transform: scale(0.99);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.option-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.text-group {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.option-label {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main);
}

.option-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.check-circle {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: 50%;
  border: 2px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-green);
}

.check-circle svg {
  width: 22px;
  height: 22px;
  display: block;
}

.onboarding-footer {
  flex-shrink: 0;
  padding: 24px 24px max(24px, env(safe-area-inset-bottom));
  display: flex;
  justify-content: center;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  background: rgba(251, 251, 253, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.continue-btn {
  background-color: #e5e5ea;
  color: #86868b;
  border: none;
  border-radius: 100px;
  padding: 18px 64px;
  font-size: 18px;
  font-weight: 600;
  cursor: not-allowed;
  transition: all 0.3s ease;
  width: 100%;
  max-width: 400px;
}

.continue-btn.is-active {
  background-color: var(--primary-green);
  color: white;
  cursor: pointer;
  box-shadow: 0 8px 16px rgba(26, 77, 46, 0.2);
}

.continue-btn.is-active:hover {
  background-color: #133821;
  transform: translateY(-2px);
}

.continue-btn.is-active:active {
  transform: scale(0.96);
}

.continue-btn:disabled {
  opacity: 0.85;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.5s var(--spring-easing);
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(40px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-40px);
}

.loading-overlay {
  position: fixed;
  inset: 0;
  background: var(--primary-green);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 24px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: po-spin 1s ease-in-out infinite;
  margin-bottom: 24px;
}

@keyframes po-spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  text-align: center;
  line-height: 1.5;
  max-width: 20rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
