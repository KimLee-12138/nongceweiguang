<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  monthlyTrend: { type: Array, default: () => [] },
  topThemes: { type: Array, default: () => [] },
  topIssuers: { type: Array, default: () => [] },
  fileTypeDistribution: { type: Array, default: () => [] },
  validityDistribution: { type: Array, default: () => [] },
  audienceDistribution: { type: Array, default: () => [] },
  topAudienceSignals: { type: Array, default: () => [] },
  focusTerms: { type: Array, default: () => [] },
  selectedPolicy: { type: Object, default: null },
  recentPolicies: { type: Array, default: () => [] },
  widthPercent: { type: Function, required: true },
})

const GOLD = '#dcc386'
const PALETTE = ['#89a97d', '#b99652', '#d4c497', '#6f8a63', '#4c6a53', '#c7b26d']

const trendChartRef = ref(null)
const themeChartRef = ref(null)
const issuerChartRef = ref(null)
const audienceChartRef = ref(null)

let trendChart = null
let themeChart = null
let issuerChart = null
let audienceChart = null

function initTrendChart() {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  updateTrendChart()
}

function updateTrendChart() {
  if (!trendChart) return
  const data = props.monthlyTrend
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

function initThemeChart() {
  if (!themeChartRef.value) return
  themeChart = echarts.init(themeChartRef.value)
  updateThemeChart()
}

function updateThemeChart() {
  if (!themeChart) return
  const data = props.topThemes.slice(0, 8)
  themeChart.setOption({
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
      data: data.map(d => d.name).reverse(),
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

function initIssuerChart() {
  if (!issuerChartRef.value) return
  issuerChart = echarts.init(issuerChartRef.value)
  updateIssuerChart()
}

function updateIssuerChart() {
  if (!issuerChart) return
  const data = props.topIssuers.slice(0, 8)
  issuerChart.setOption({
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
      data: data.map(d => d.name).reverse(),
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
          { offset: 0, color: 'rgba(137,169,125,0.4)' },
          { offset: 1, color: '#89a97d' },
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
  const data = props.audienceDistribution
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
        name: d.name,
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
  themeChart?.resize()
  issuerChart?.resize()
  audienceChart?.resize()
}

onMounted(async () => {
  await nextTick()
  initTrendChart()
  initThemeChart()
  initIssuerChart()
  initAudienceChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  themeChart?.dispose()
  issuerChart?.dispose()
  audienceChart?.dispose()
})

watch(() => props.monthlyTrend, () => { nextTick(updateTrendChart) }, { deep: true })
watch(() => props.topThemes, () => { nextTick(updateThemeChart) }, { deep: true })
watch(() => props.topIssuers, () => { nextTick(updateIssuerChart) }, { deep: true })
watch(() => props.audienceDistribution, () => { nextTick(updateAudienceChart) }, { deep: true })
</script>

<template>
  <section class="signal-grid">
    <div class="signal-grid__main">
      <!-- Trend Chart -->
      <article class="signal-panel signal-panel--trend">
        <div class="signal-panel__head">
          <div>
            <span class="signal-panel__kicker">动态热度</span>
            <h2>政策热度趋势</h2>
          </div>
        </div>
        <div ref="trendChartRef" class="echart-container echart-container--trend"></div>
      </article>

      <!-- Theme + Issuer bar charts -->
      <div class="signal-grid__duo">
        <article class="signal-panel">
          <div class="signal-panel__head">
            <div>
              <span class="signal-panel__kicker">主题分布</span>
              <h2>热点主题</h2>
            </div>
          </div>
          <div ref="themeChartRef" class="echart-container echart-container--bar"></div>
        </article>

        <article class="signal-panel">
          <div class="signal-panel__head">
            <div>
              <span class="signal-panel__kicker">来源活跃度</span>
              <h2>活跃机构</h2>
            </div>
          </div>
          <div ref="issuerChartRef" class="echart-container echart-container--bar"></div>
        </article>
      </div>

      <!-- Structure + Audience -->
      <div class="signal-grid__duo">
        <article class="signal-panel">
          <div class="signal-panel__head">
            <div>
              <span class="signal-panel__kicker">样本结构</span>
              <h2>文件类型与效力状态</h2>
            </div>
          </div>
          <div class="chip-cloud">
            <span v-for="item in fileTypeDistribution" :key="`type-${item.name}`" class="metric-chip">
              {{ item.name }} · {{ item.count }}
            </span>
          </div>
          <div class="chip-cloud">
            <span v-for="item in validityDistribution" :key="`status-${item.name}`" class="metric-chip metric-chip--soft">
              {{ item.name }} · {{ item.count }}
            </span>
          </div>
        </article>

        <article class="signal-panel">
          <div class="signal-panel__head">
            <div>
              <span class="signal-panel__kicker">目标主体</span>
              <h2>适用主体画像</h2>
            </div>
          </div>
          <div ref="audienceChartRef" class="echart-container echart-container--pie"></div>
          <div v-if="topAudienceSignals.length" class="chip-cloud" style="margin-top: 16px;">
            <span v-for="item in topAudienceSignals" :key="`brief-${item.name}`" class="metric-chip metric-chip--soft">
              风向主体 {{ item.name }} · {{ item.count }}
            </span>
          </div>
        </article>
      </div>

      <!-- Focus Policy -->
      <article v-if="selectedPolicy" class="signal-panel signal-panel--focus">
        <div class="signal-panel__head">
          <div>
            <span class="signal-panel__kicker">焦点解读</span>
            <h2>当前政策晦涩文字详解</h2>
            <p class="signal-panel__sub">{{ selectedPolicy.title }}</p>
          </div>
        </div>
        <p class="selected-summary">{{ selectedPolicy.summary || '当前政策暂无摘要。' }}</p>
        <div class="term-explain-list">
          <article v-for="item in selectedPolicy.terms" :key="item.term" class="term-explain-card term-explain-card--highlight">
            <div class="term-explain-card__head">
              <strong>{{ item.term }}</strong>
              <span>{{ item.category }}</span>
            </div>
            <p>{{ item.description }}</p>
          </article>
        </div>
      </article>

      <!-- Focus Terms -->
      <article class="signal-panel">
        <div class="signal-panel__head">
          <div>
            <span class="signal-panel__kicker">术语情报</span>
            <h2>重点术语解释</h2>
          </div>
        </div>
        <div class="term-explain-list term-explain-list--compact">
          <article v-for="item in focusTerms" :key="item.term" class="term-explain-card">
            <div class="term-explain-card__head">
              <strong>{{ item.term }}</strong>
              <span>{{ item.category }}</span>
            </div>
            <p>{{ item.description }}</p>
          </article>
        </div>
      </article>

      <!-- Recent Policies -->
      <article class="signal-panel">
        <div class="signal-panel__head">
          <div>
            <span class="signal-panel__kicker">近期样本</span>
            <h2>最新纳入样本的政策</h2>
          </div>
        </div>
        <div class="recent-grid">
          <article v-for="policy in recentPolicies" :key="policy.id" class="recent-card">
            <div class="recent-topline">
              <span>{{ policy.file_type }}</span>
              <span>{{ policy.validity_status }}</span>
            </div>
            <h3>{{ policy.title }}</h3>
            <p>{{ policy.summary || '暂无摘要' }}</p>
            <small>{{ policy.source || '未标注来源' }}</small>
          </article>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.signal-grid {
  margin-top: 20px;
}

.signal-grid__main {
  display: grid;
  gap: 16px;
}

.signal-grid__duo {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

/* ── Panel base (dark glass) ─────────────────────────────── */
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

.signal-panel__sub {
  margin: 6px 0 0;
  font-size: 14px;
  color: rgba(228, 231, 218, 0.55);
  line-height: 1.6;
}

/* ── ECharts containers ──────────────────────────────────── */
.echart-container {
  width: 100%;
}

.echart-container--trend {
  height: 280px;
}

.echart-container--bar {
  height: 300px;
}

.echart-container--pie {
  height: 280px;
}

/* ── Chips (dark) ────────────────────────────────────────── */
.chip-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip-cloud + .chip-cloud {
  margin-top: 10px;
}

.metric-chip {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(137, 169, 125, 0.2);
  background: rgba(137, 169, 125, 0.1);
  color: #89a97d;
  font-size: 13px;
  font-weight: 500;
}

.metric-chip--soft {
  background: rgba(228, 231, 218, 0.06);
  border-color: rgba(228, 231, 218, 0.1);
  color: rgba(228, 231, 218, 0.6);
}

.metric-chip--accent {
  background: rgba(214, 192, 139, 0.1);
  border-color: rgba(214, 192, 139, 0.18);
  color: #dcc386;
}

/* ── Term Explain (dark) ─────────────────────────────────── */
.selected-summary {
  margin: 0 0 16px;
  line-height: 1.7;
  font-size: 15px;
  color: rgba(228, 231, 218, 0.66);
}

.term-explain-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.term-explain-list--compact {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.term-explain-card {
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(197, 205, 183, 0.1);
  background: rgba(16, 35, 24, 0.6);
  transition: border-color 0.2s, transform 0.2s;
}

.term-explain-card:hover {
  border-color: rgba(214, 192, 139, 0.2);
  transform: translateY(-1px);
}

.term-explain-card--highlight {
  background: rgba(214, 192, 139, 0.06);
  border-color: rgba(214, 192, 139, 0.15);
}

.term-explain-card__head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

.term-explain-card__head strong {
  font-size: 15px;
  color: #f8f3e7;
}

.term-explain-card__head span {
  font-size: 11px;
  font-weight: 600;
  color: rgba(214, 192, 139, 0.7);
}

.term-explain-card p {
  margin: 0;
  line-height: 1.7;
  font-size: 13px;
  color: rgba(228, 231, 218, 0.6);
}

/* ── Recent Policies (dark) ──────────────────────────────── */
.recent-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.recent-card {
  padding: 18px;
  border-radius: 16px;
  border: 1px solid rgba(197, 205, 183, 0.1);
  background: rgba(16, 35, 24, 0.6);
  transition: border-color 0.2s, transform 0.2s;
}

.recent-card:hover {
  border-color: rgba(214, 192, 139, 0.2);
  transform: translateY(-1px);
}

.recent-topline {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 11px;
  font-weight: 600;
  color: rgba(214, 192, 139, 0.7);
}

.recent-card h3 {
  margin: 10px 0 6px;
  font-size: 16px;
  line-height: 1.4;
  color: #f8f3e7;
}

.recent-card p {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: rgba(228, 231, 218, 0.55);
}

.recent-card small {
  display: block;
  margin-top: 10px;
  font-size: 11px;
  color: rgba(228, 231, 218, 0.35);
}

@media (max-width: 1180px) {
  .signal-grid__duo,
  .term-explain-list,
  .term-explain-list--compact,
  .recent-grid {
    grid-template-columns: 1fr;
  }
}
</style>
