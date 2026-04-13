<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

import { api } from '../api/client'
import { adminLogoutAll, getAdminMe, getUserMe, userLogoutAll } from '../services/authSession'
import logoIcon from '../assets/logo_icon.png'

const router = useRouter()
const loading = ref(false)
const kpi = ref(null)
const trend = ref(null)
const sources = ref(null)
const audience = ref(null)
const loadError = ref(null)
const isScrolled = ref(false)
const userMe = ref({ authenticated: false })
const adminMe = ref({ authenticated: false })

const hasUser = computed(() => !!userMe.value?.authenticated)
const hasAdmin = computed(() => !!adminMe.value?.authenticated)
const consoleEntryPath = computed(() => (hasAdmin.value ? '/admin' : '/admin/login'))

function go(path) {
  router.push(path)
}

async function syncAuthState() {
  try { userMe.value = await getUserMe() } catch { userMe.value = { authenticated: false } }
  try { adminMe.value = await getAdminMe() } catch { adminMe.value = { authenticated: false } }
}

async function logoutUser() {
  await userLogoutAll().catch(() => null)
  await syncAuthState()
}

async function logoutAdmin() {
  await adminLogoutAll().catch(() => null)
  await syncAuthState()
}

function handleScroll() {
  isScrolled.value = window.scrollY > 50
}

const isEmptyKpi = computed(() => {
  if (!kpi.value || typeof kpi.value !== 'object') return true
  const c = kpi.value
  return (
    (c.policy_count ?? 0) +
      (c.profile_count ?? 0) +
      (c.match_record_count ?? 0) +
      (c.raw_policy_count ?? 0) ===
    0
  )
})

const kpiCards = computed(() => {
  if (!kpi.value) return []
  return [
    { label: '结构化政策', value: kpi.value.policy_count ?? 0, accent: 'gold' },
    { label: '农户画像', value: kpi.value.profile_count ?? 0, accent: 'green' },
    { label: '匹配记录', value: kpi.value.match_record_count ?? 0, accent: 'cyan' },
    { label: '原始政策', value: kpi.value.raw_policy_count ?? 0, accent: 'amber' },
  ]
})

const trendItems = computed(() => (Array.isArray(trend.value?.items) ? trend.value.items : []))
const sourceItems = computed(() => (Array.isArray(sources.value?.items) ? sources.value.items : []))
const audienceItems = computed(() => (Array.isArray(audience.value?.items) ? audience.value.items : []))

const GOLD = '#dcc386'
const PALETTE = ['#89a97d', '#b99652', '#d4c497', '#6f8a63', '#4c6a53', '#c7b26d']

const trendChartRef = ref(null)
const sourceChartRef = ref(null)
const audienceChartRef = ref(null)

let trendChart = null
let sourceChart = null
let audienceChart = null

function initTrendChart() {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  updateTrendChart()
}

function updateTrendChart() {
  if (!trendChart) return
  const data = trendItems.value
  trendChart.setOption({
    grid: { top: 30, right: 20, bottom: 30, left: 50 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(16,35,24,0.92)',
      borderColor: 'rgba(197,205,183,0.15)',
      textStyle: { color: '#f8f3e7', fontSize: 12 },
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.period),
      axisLine: { lineStyle: { color: 'rgba(197,205,183,0.12)' } },
      axisLabel: { color: 'rgba(228,231,218,0.5)', fontSize: 11 },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(197,205,183,0.06)' } },
      axisLabel: { color: 'rgba(228,231,218,0.4)', fontSize: 11 },
    },
    series: [{
      type: 'line',
      data: data.map(d => d.count),
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      itemStyle: { color: GOLD },
      lineStyle: { width: 3, color: GOLD },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(220,195,134,0.35)' },
          { offset: 1, color: 'rgba(220,195,134,0.02)' },
        ]),
      },
    }],
  })
}

function initSourceChart() {
  if (!sourceChartRef.value) return
  sourceChart = echarts.init(sourceChartRef.value)
  updateSourceChart()
}

function updateSourceChart() {
  if (!sourceChart) return
  const data = sourceItems.value.slice(0, 10)
  sourceChart.setOption({
    grid: { top: 10, right: 60, bottom: 10, left: 10, containLabel: true },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(16,35,24,0.92)',
      borderColor: 'rgba(197,205,183,0.15)',
      textStyle: { color: '#f8f3e7', fontSize: 12 },
    },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(197,205,183,0.06)' } },
      axisLabel: { color: 'rgba(228,231,218,0.4)', fontSize: 11 },
    },
    yAxis: {
      type: 'category',
      data: data.map(d => d.source).reverse(),
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: 'rgba(228,231,218,0.7)', fontSize: 12 },
    },
    series: [{
      type: 'bar',
      data: data.map(d => d.count).reverse(),
      barWidth: 14,
      itemStyle: {
        borderRadius: [0, 7, 7, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: 'rgba(220,195,134,0.4)' },
          { offset: 1, color: GOLD },
        ]),
      },
      label: {
        show: true,
        position: 'right',
        color: 'rgba(228,231,218,0.6)',
        fontSize: 11,
      },
    }],
  })
}

function initAudienceChart() {
  if (!audienceChartRef.value) return
  audienceChart = echarts.init(audienceChartRef.value)
  updateAudienceChart()
}

function updateAudienceChart() {
  if (!audienceChart) return
  const data = audienceItems.value
  const total = data.reduce((s, d) => s + Number(d.count || 0), 0)
  audienceChart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(16,35,24,0.92)',
      borderColor: 'rgba(197,205,183,0.15)',
      textStyle: { color: '#f8f3e7', fontSize: 12 },
    },
    series: [{
      type: 'pie',
      radius: ['48%', '72%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: { borderColor: 'rgba(11,25,18,0.94)', borderWidth: 3 },
      label: {
        show: true,
        color: 'rgba(228,231,218,0.7)',
        fontSize: 11,
        formatter: '{b}\n{d}%',
      },
      labelLine: { lineStyle: { color: 'rgba(197,205,183,0.2)' } },
      data: data.map((d, i) => ({
        name: d.audience,
        value: d.count,
        itemStyle: { color: PALETTE[i % PALETTE.length] },
      })),
    }],
    graphic: [{
      type: 'text',
      left: 'center',
      top: 'center',
      style: {
        text: String(total),
        textAlign: 'center',
        fill: GOLD,
        fontSize: 28,
        fontWeight: 700,
        fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif',
      },
    }],
  })
}

function handleResize() {
  trendChart?.resize()
  sourceChart?.resize()
  audienceChart?.resize()
}

async function loadAll() {
  loading.value = true
  loadError.value = null
  try {
    const [k, tr, so, au] = await Promise.all([
      api.get('/insights/kpi-summary'),
      api.get('/insights/trend-analysis'),
      api.get('/insights/source-distribution'),
      api.get('/insights/audience-distribution'),
    ])
    kpi.value = k
    trend.value = tr
    sources.value = so
    audience.value = au
  } catch (e) {
    loadError.value = e?.message || '加载失败'
    ElMessage.error(loadError.value)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('resize', handleResize)
  await syncAuthState()
  await loadAll()
  await nextTick()
  initTrendChart()
  initSourceChart()
  initAudienceChart()
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  sourceChart?.dispose()
  audienceChart?.dispose()
})

watch(trendItems, () => { nextTick(updateTrendChart) }, { deep: true })
watch(sourceItems, () => { nextTick(updateSourceChart) }, { deep: true })
watch(audienceItems, () => { nextTick(updateAudienceChart) }, { deep: true })
</script>

<template>
  <div class="insights-page">
    <!-- Nav Bar -->
    <nav class="nav-bar" :class="{ 'nav-scrolled': isScrolled }">
      <div class="nav-container">
        <div class="nav-brand" @click="go('/')">
          <img class="brand-logo" :src="logoIcon" alt="AgriPolicy AI" />
          <span class="brand-titletext">AgriPolicy&nbsp;AI</span>
        </div>
        <div class="nav-menu">
          <a class="nav-link" @click="go('/')">首页</a>
          <a class="nav-link" @click="go('/compass')">政策风向</a>
          <a class="nav-link" @click="go('/chat')">智能工作台</a>
          <a class="nav-link" @click="go(consoleEntryPath)">管理中枢</a>
          <div class="nav-divider"></div>
          <template v-if="!hasUser">
            <a class="nav-link" @click="go('/login')">登录</a>
            <a class="nav-link" @click="go('/register')">注册</a>
          </template>
          <template v-else>
            <a class="nav-link" @click="logoutUser">退出用户</a>
          </template>
          <template v-if="hasAdmin">
            <a class="nav-link" @click="logoutAdmin">退出管理员</a>
          </template>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="insights-hero">
      <div class="insights-hero__glow insights-hero__glow--primary"></div>
      <div class="insights-hero__glow insights-hero__glow--secondary"></div>
      <div class="insights-hero__inner">
        <div class="insights-hero__content">
          <div class="insights-hero__left">
            <span class="insights-hero__eyebrow">Business Intelligence Dashboard</span>
            <h1 class="insights-hero__title">政策洞察大屏</h1>
            <p class="insights-hero__summary">
              从库内政策与原始抓取数据汇总核心指标、发布趋势、来源机构分布与受众结构画像，便于运营巡检与决策分析。
            </p>
          </div>
          <div class="insights-hero__right">
            <div class="hero-control-card">
              <span class="hero-control-card__label">数据操作</span>
              <div class="hero-control-card__actions">
                <el-button type="primary" :loading="loading" @click="loadAll">刷新数据</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Body -->
    <div class="insights-body">
      <!-- Error alert -->
      <el-alert v-if="loadError" type="error" :closable="false" :title="loadError" class="insights-alert" />

      <!-- KPI Tiles -->
      <section class="kpi-stage">
        <div v-if="isEmptyKpi" class="empty-panel">
          <span class="empty-panel__kicker">数据状态</span>
          <p>暂无业务数据。请执行后端演示数据脚本或导入政策后再查看。</p>
          <code class="code-snippet">python -m app.cli seed-demo --workspace-root ..</code>
        </div>
        <div v-else class="kpi-grid">
          <article v-for="card in kpiCards" :key="card.label" class="stat-surface">
            <span class="stat-surface__label">{{ card.label }}</span>
            <strong class="stat-surface__value">{{ card.value }}</strong>
          </article>
        </div>
      </section>

      <!-- Charts -->
      <section class="chart-stage">
        <!-- Trend Chart -->
        <article class="signal-panel signal-panel--wide">
          <div class="signal-panel__head">
            <div>
              <span class="signal-panel__kicker">时序分析</span>
              <h2>发布趋势</h2>
            </div>
          </div>
          <div v-if="!trendItems.length" class="empty-hint">暂无按月统计，导入或抓取带日期的原始政策后将显示趋势。</div>
          <div v-else ref="trendChartRef" class="echart-container echart-container--trend"></div>
        </article>

        <div class="chart-stage__duo">
          <!-- Source Chart -->
          <article class="signal-panel">
            <div class="signal-panel__head">
              <div>
                <span class="signal-panel__kicker">来源洞察</span>
                <h2>来源机构分布</h2>
              </div>
            </div>
            <div v-if="!sourceItems.length" class="empty-hint">暂无来源字段。抓取或导入原始数据后将展示发文单位分布。</div>
            <div v-else ref="sourceChartRef" class="echart-container echart-container--bar"></div>
          </article>

          <!-- Audience Chart -->
          <article class="signal-panel">
            <div class="signal-panel__head">
              <div>
                <span class="signal-panel__kicker">受众画像</span>
                <h2>受众标签分布</h2>
              </div>
            </div>
            <div v-if="!audienceItems.length" class="empty-hint">暂无受众标签。请确保政策条件树中包含适用对象相关节点。</div>
            <div v-else ref="audienceChartRef" class="echart-container echart-container--pie"></div>
          </article>
        </div>
      </section>
    </div>

    <!-- Footer -->
    <footer class="insights-footer">
      <div class="footer-inner">
        <p>&copy; 2026 农策微光 (Agricultural Policy Intelligence). All rights reserved.</p>
        <div class="footer-links">
          <span @click="go('/')">首页</span>
          <span @click="go('/compass')">政策风向</span>
          <span @click="go('/chat')">智能工作台</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* ── Page Shell ──────────────────────────────────────────── */
.insights-page {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(170deg, #0d1f17 0%, #14281d 50%, #0a1a12 100%);
  color: #f8f3e7;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', 'PingFang SC', 'Noto Sans SC', sans-serif;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

.insights-page::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image:
    linear-gradient(rgba(109, 255, 188, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(109, 255, 188, 0.03) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, transparent 70%);
  -webkit-mask-image: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, transparent 70%);
}

.insights-page::after {
  content: '';
  position: fixed;
  top: 20%;
  right: -10%;
  width: 600px;
  height: 600px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(29, 91, 61, 0.18), transparent 70%);
  filter: blur(60px);
  pointer-events: none;
  z-index: 0;
  animation: drift-orb 18s ease-in-out infinite alternate;
}

@keyframes drift-orb {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(-60px, 40px) scale(1.08); }
  100% { transform: translate(30px, -30px) scale(0.95); }
}

/* ── Nav Bar ─────────────────────────────────────────────── */
.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  z-index: 100;
  transition: background-color 0.4s ease, backdrop-filter 0.4s ease;
}
.nav-scrolled {
  background-color: rgba(13, 31, 23, 0.88);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(109, 255, 188, 0.06);
}
.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  padding: 0 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}
.brand-logo {
  height: 28px;
  width: auto;
  display: block;
  border-radius: 8px;
  opacity: 0.95;
}
.brand-titletext {
  color: rgba(248, 243, 231, 0.92);
  font-size: 13px;
  font-weight: 650;
  letter-spacing: -0.02em;
  user-select: none;
}
.nav-menu {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.nav-link {
  font-size: 12px;
  color: rgba(248, 243, 231, 0.6);
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.3s;
}
.nav-link:hover {
  color: #f8f3e7;
}
.nav-divider {
  width: 1px;
  height: 12px;
  background: rgba(248, 243, 231, 0.15);
}

/* ── Hero ─────────────────────────────────────────────────── */
.insights-hero {
  position: relative;
  overflow: hidden;
  width: 100%;
  min-height: 340px;
  padding: 100px 32px 56px;
  box-sizing: border-box;
  background: transparent;
}

.insights-hero__glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(100px);
  opacity: 0.7;
  pointer-events: none;
}

.insights-hero__glow--primary {
  top: -100px;
  left: -8%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(214, 192, 139, 0.14), transparent);
}

.insights-hero__glow--secondary {
  right: 8%;
  bottom: -140px;
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, rgba(137, 169, 125, 0.12), transparent);
}

.insights-hero__inner {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
}

.insights-hero__content {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(260px, 0.6fr);
  gap: 32px;
  align-items: end;
}

.insights-hero__eyebrow {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: rgba(214, 192, 139, 0.84);
}

.insights-hero__title {
  margin: 14px 0 0;
  font-size: clamp(40px, 5vw, 68px);
  line-height: 1;
  letter-spacing: -0.04em;
  color: #f8f3e7;
}

.insights-hero__summary {
  max-width: 720px;
  margin: 20px 0 0;
  font-size: 15px;
  line-height: 1.8;
  color: rgba(228, 231, 218, 0.66);
}

.hero-control-card {
  position: relative;
  display: grid;
  gap: 12px;
  padding: 20px;
  border-radius: 24px;
  border: 1px solid rgba(197, 205, 183, 0.12);
  background: linear-gradient(180deg, rgba(16, 35, 24, 0.88), rgba(11, 25, 18, 0.94));
  box-shadow: inset 0 1px 0 rgba(255, 248, 232, 0.05), 0 20px 60px rgba(0, 0, 0, 0.24);
}

.hero-control-card::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 25px;
  padding: 1px;
  background: linear-gradient(180deg, rgba(214, 192, 139, 0.2) 0%, rgba(137, 169, 125, 0.08) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.hero-control-card__label {
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(214, 192, 139, 0.72);
}

.hero-control-card__actions {
  display: grid;
  gap: 10px;
}

:deep(.hero-control-card .el-button) {
  min-height: 42px;
  border-radius: 12px;
}

:deep(.hero-control-card .el-button--primary) {
  border-color: rgba(214, 192, 139, 0.5);
  background: linear-gradient(135deg, #89a97d, #6f8a63);
  color: #f8f3e7;
}

/* ── Body ─────────────────────────────────────────────────── */
.insights-body {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 40px 32px 0;
  box-sizing: border-box;
}

.insights-alert {
  margin-bottom: 20px;
  border-radius: 16px;
}

/* ── KPI Stage ────────────────────────────────────────────── */
.kpi-stage {
  margin-bottom: 20px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-surface {
  position: relative;
  padding: 22px;
  border-radius: 22px;
  border: 1px solid rgba(197, 205, 183, 0.12);
  background: linear-gradient(180deg, rgba(16, 35, 24, 0.88), rgba(11, 25, 18, 0.94));
  box-shadow: inset 0 1px 0 rgba(255, 248, 232, 0.05), 0 20px 60px rgba(0, 0, 0, 0.24);
  overflow: hidden;
}

.stat-surface::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 23px;
  padding: 1px;
  background: linear-gradient(180deg, rgba(214, 192, 139, 0.2) 0%, rgba(137, 169, 125, 0.06) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.stat-surface__label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(214, 192, 139, 0.84);
}

.stat-surface__value {
  display: block;
  margin-top: 12px;
  font-size: clamp(30px, 3vw, 42px);
  line-height: 1;
  letter-spacing: -0.04em;
  color: #dcc386;
}

.empty-panel {
  position: relative;
  padding: 28px;
  border-radius: 24px;
  border: 1px solid rgba(197, 205, 183, 0.12);
  background: linear-gradient(180deg, rgba(16, 35, 24, 0.88), rgba(11, 25, 18, 0.94));
  box-shadow: inset 0 1px 0 rgba(255, 248, 232, 0.05), 0 20px 60px rgba(0, 0, 0, 0.24);
}

.empty-panel__kicker {
  display: inline-block;
  font-size: 11px;
  font-weight: 650;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: rgba(214, 192, 139, 0.84);
}

.empty-panel p {
  margin: 12px 0 0;
  font-size: 15px;
  line-height: 1.8;
  color: rgba(228, 231, 218, 0.66);
}

.code-snippet {
  display: block;
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(4, 16, 12, 0.6);
  border: 1px solid rgba(197, 205, 183, 0.08);
  font-size: 13px;
  color: #89a97d;
  word-break: break-all;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

/* ── Chart Stage ──────────────────────────────────────────── */
.chart-stage {
  display: grid;
  gap: 16px;
}

.chart-stage__duo {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

/* ── Signal Panel (dark glass) ────────────────────────────── */
.signal-panel {
  position: relative;
  padding: 24px;
  border-radius: 30px;
  border: 1px solid rgba(197, 205, 183, 0.12);
  background: linear-gradient(180deg, rgba(16, 35, 24, 0.88), rgba(11, 25, 18, 0.94));
  box-shadow: inset 0 1px 0 rgba(255, 248, 232, 0.05), 0 20px 60px rgba(0, 0, 0, 0.24);
}

.signal-panel::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 31px;
  padding: 1px;
  background: linear-gradient(180deg, rgba(214, 192, 139, 0.15) 0%, rgba(137, 169, 125, 0.04) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.signal-panel__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.signal-panel__kicker {
  display: inline-block;
  font-size: 11px;
  font-weight: 650;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: rgba(214, 192, 139, 0.84);
}

.signal-panel__head h2 {
  margin: 8px 0 0;
  font-size: 22px;
  letter-spacing: -0.02em;
  color: #f8f3e7;
}

.empty-hint {
  font-size: 14px;
  line-height: 1.7;
  color: rgba(228, 231, 218, 0.5);
  padding: 20px 0;
}

/* ── ECharts containers ──────────────────────────────────── */
.echart-container {
  width: 100%;
}

.echart-container--trend {
  height: 300px;
}

.echart-container--bar {
  height: 320px;
}

.echart-container--pie {
  height: 300px;
}

/* ── Footer (dark) ───────────────────────────────────────── */
.insights-footer {
  margin-top: 80px;
  padding: 32px 32px;
  border-top: 1px solid rgba(197, 205, 183, 0.08);
  background: rgba(8, 18, 13, 0.6);
}
.footer-inner {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}
.footer-inner p {
  margin: 0;
  font-size: 12px;
  color: rgba(228, 231, 218, 0.35);
}
.footer-links {
  display: flex;
  gap: 20px;
}
.footer-links span {
  font-size: 12px;
  color: rgba(228, 231, 218, 0.45);
  cursor: pointer;
  transition: color 0.2s;
}
.footer-links span:hover {
  color: #dcc386;
}

/* ── Responsive ──────────────────────────────────────────── */
@media (max-width: 1180px) {
  .insights-body {
    padding: 28px 20px 0;
  }
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .chart-stage__duo {
    grid-template-columns: 1fr;
  }
  .insights-hero__content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .insights-body {
    padding: 20px 14px 0;
  }
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  .insights-hero {
    padding: 90px 20px 36px;
    min-height: 280px;
  }
  .insights-hero__title {
    font-size: 36px;
  }
  .nav-menu .nav-link:not(:last-child) {
    display: none;
  }
  .nav-divider {
    display: none;
  }
  .footer-inner {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 600px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
}
</style>
