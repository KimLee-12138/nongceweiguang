<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { compassApi } from '../api/compass'

const loading = ref(false)
const generating = ref(false)
const savingGlossary = ref(false)
const deletingGlossaryId = ref(null)
const glossaryDialogVisible = ref(false)
const editingGlossaryId = ref(null)

const filters = reactive({
  months: 6,
  glossaryKeyword: '',
  glossaryCategory: '',
})

const overview = ref(null)
const reports = ref([])
const selectedReport = ref(null)
const glossaryItems = ref([])

const glossaryForm = reactive({
  term: '',
  category: '政策主题',
  aliases: '',
  weight: 1,
  enabled: true,
  description: '',
})

const statCards = computed(() => {
  const stats = overview.value?.stats || {}
  return [
    { label: '正式政策', value: stats.policy_count ?? 0, accent: 'amber' },
    { label: '原始政策', value: stats.raw_policy_count ?? 0, accent: 'teal' },
    { label: '已生成报告', value: stats.report_count ?? 0, accent: 'ink' },
    { label: '启用词条', value: stats.glossary_count ?? 0, accent: 'rose' },
  ]
})

const topThemes = computed(() => overview.value?.theme_distribution || [])
const topIssuers = computed(() => overview.value?.issuer_distribution || [])
const monthlyTrend = computed(() => overview.value?.monthly_trend || [])
const audienceDistribution = computed(() => overview.value?.audience_distribution || [])
const fileTypeDistribution = computed(() => overview.value?.file_type_distribution || [])
const validityDistribution = computed(() => overview.value?.validity_distribution || [])
const recentPolicies = computed(() => overview.value?.recent_policy_cards || [])

function widthPercent(count, items) {
  const max = Math.max(...items.map((item) => item.count), 1)
  return `${Math.max((count / max) * 100, 10)}%`
}

function resetGlossaryForm() {
  editingGlossaryId.value = null
  glossaryForm.term = ''
  glossaryForm.category = '政策主题'
  glossaryForm.aliases = ''
  glossaryForm.weight = 1
  glossaryForm.enabled = true
  glossaryForm.description = ''
}

function openCreateGlossary() {
  resetGlossaryForm()
  glossaryDialogVisible.value = true
}

function openEditGlossary(item) {
  editingGlossaryId.value = item.id
  glossaryForm.term = item.term
  glossaryForm.category = item.category || '政策主题'
  glossaryForm.aliases = (item.aliases || []).join('，')
  glossaryForm.weight = item.weight || 1
  glossaryForm.enabled = item.enabled !== false
  glossaryForm.description = item.description || ''
  glossaryDialogVisible.value = true
}

async function loadOverview() {
  overview.value = await compassApi.getOverview({ months: filters.months })
}

async function loadReports() {
  const payload = await compassApi.getReports({ limit: 20 })
  reports.value = payload.items || []
  if (!reports.value.length) {
    selectedReport.value = null
    return
  }
  const nextId = selectedReport.value?.id || reports.value[0].id
  const next = reports.value.find((item) => item.id === nextId) || reports.value[0]
  selectedReport.value = await compassApi.getReport(next.id)
}

async function loadGlossary() {
  const payload = await compassApi.getGlossary({
    keyword: filters.glossaryKeyword,
    category: filters.glossaryCategory,
    limit: 100,
  })
  glossaryItems.value = payload.items || []
}

async function loadAll() {
  loading.value = true
  try {
    await Promise.all([loadOverview(), loadReports(), loadGlossary()])
  } catch (error) {
    ElMessage.error(error?.message || '风向标加载失败')
  } finally {
    loading.value = false
  }
}

async function selectReport(reportId) {
  try {
    selectedReport.value = await compassApi.getReport(reportId)
  } catch (error) {
    ElMessage.error(error?.message || '报告详情加载失败')
  }
}

async function generateReport() {
  generating.value = true
  try {
    const payload = await compassApi.generateReport()
    ElMessage.success(`已生成最新风向标报告 #${payload.report_id}`)
    await Promise.all([loadOverview(), loadReports(), loadGlossary()])
  } catch (error) {
    ElMessage.error(error?.message || '生成风向标报告失败')
  } finally {
    generating.value = false
  }
}

async function saveGlossary() {
  savingGlossary.value = true
  try {
    const payload = {
      term: glossaryForm.term,
      category: glossaryForm.category,
      aliases: glossaryForm.aliases
        .split(/[，,]/)
        .map((item) => item.trim())
        .filter(Boolean),
      weight: glossaryForm.weight,
      enabled: glossaryForm.enabled,
      description: glossaryForm.description,
    }
    if (editingGlossaryId.value) {
      await compassApi.updateGlossary(editingGlossaryId.value, payload)
      ElMessage.success('词条已更新')
    } else {
      await compassApi.createGlossary(payload)
      ElMessage.success('词条已创建')
    }
    glossaryDialogVisible.value = false
    resetGlossaryForm()
    await Promise.all([loadGlossary(), loadOverview()])
  } catch (error) {
    ElMessage.error(error?.message || '词条保存失败')
  } finally {
    savingGlossary.value = false
  }
}

async function removeGlossary(item) {
  try {
    await ElMessageBox.confirm(`确定删除词条“${item.term}”吗？`, '删除确认', {
      type: 'warning',
    })
  } catch {
    return
  }
  deletingGlossaryId.value = item.id
  try {
    await compassApi.deleteGlossary(item.id)
    ElMessage.success('词条已删除')
    await Promise.all([loadGlossary(), loadOverview()])
  } catch (error) {
    ElMessage.error(error?.message || '删除词条失败')
  } finally {
    deletingGlossaryId.value = null
  }
}

onMounted(loadAll)
</script>

<template>
  <div class="compass-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Policy Compass</p>
        <h1>政策风向标</h1>
        <p class="hero-copy">
          把正式政策、原始抓取、条件树和词典信号汇总成一张持续更新的政策雷达图，帮助我们更快判断当前热点、活跃机构和农户最关心的方向。
        </p>
      </div>
      <div class="hero-actions">
        <el-select v-model="filters.months" class="month-select" @change="loadOverview">
          <el-option :value="3" label="近 3 个月" />
          <el-option :value="6" label="近 6 个月" />
          <el-option :value="12" label="近 12 个月" />
        </el-select>
        <el-button plain :loading="loading" @click="loadAll">刷新数据</el-button>
        <el-button type="primary" :loading="generating" @click="generateReport">生成最新报告</el-button>
      </div>
    </section>

    <section class="stats-grid">
      <article v-for="card in statCards" :key="card.label" class="stat-card" :data-accent="card.accent">
        <span class="stat-label">{{ card.label }}</span>
        <strong class="stat-value">{{ card.value }}</strong>
      </article>
    </section>

    <section class="content-grid">
      <div class="column column-wide">
        <article class="panel">
          <div class="panel-head">
            <div>
              <h2>政策热度趋势</h2>
              <p>按月份查看近阶段政策新增强度。</p>
            </div>
          </div>
          <div class="trend-strip">
            <div v-for="item in monthlyTrend" :key="item.period" class="trend-item">
              <span class="trend-period">{{ item.period }}</span>
              <div class="trend-bar-shell">
                <div class="trend-bar" :style="{ height: widthPercent(item.count, monthlyTrend) }"></div>
              </div>
              <strong>{{ item.count }}</strong>
            </div>
          </div>
        </article>

        <div class="two-up">
          <article class="panel">
            <div class="panel-head">
              <div>
                <h2>热点主题</h2>
                <p>结合词典、政策分类和原始抓取标签统计。</p>
              </div>
            </div>
            <div class="ranking-list">
              <div v-for="item in topThemes" :key="item.name" class="ranking-item">
                <div>
                  <strong>{{ item.name }}</strong>
                  <span>{{ item.count }} 次出现</span>
                </div>
                <div class="line-shell">
                  <div class="line-fill" :style="{ width: widthPercent(item.count, topThemes) }"></div>
                </div>
              </div>
            </div>
          </article>

          <article class="panel">
            <div class="panel-head">
              <div>
                <h2>活跃机构</h2>
                <p>最近一段时间里发文最频繁的来源。</p>
              </div>
            </div>
            <div class="ranking-list">
              <div v-for="item in topIssuers" :key="item.name" class="ranking-item">
                <div>
                  <strong>{{ item.name }}</strong>
                  <span>{{ item.count }} 条</span>
                </div>
                <div class="line-shell">
                  <div class="line-fill accent-ink" :style="{ width: widthPercent(item.count, topIssuers) }"></div>
                </div>
              </div>
            </div>
          </article>
        </div>

        <div class="two-up">
          <article class="panel">
            <div class="panel-head">
              <div>
                <h2>文件类型与效力状态</h2>
                <p>帮助我们判断当前样本结构是否均衡。</p>
              </div>
            </div>
            <div class="chip-cloud">
              <span v-for="item in fileTypeDistribution" :key="`type-${item.name}`" class="metric-chip">
                {{ item.name }} · {{ item.count }}
              </span>
            </div>
            <div class="chip-cloud">
              <span v-for="item in validityDistribution" :key="`status-${item.name}`" class="metric-chip soft">
                {{ item.name }} · {{ item.count }}
              </span>
            </div>
          </article>

          <article class="panel">
            <div class="panel-head">
              <div>
                <h2>适用主体</h2>
                <p>来自条件树里的主体提取结果。</p>
              </div>
            </div>
            <div class="chip-cloud">
              <span v-for="item in audienceDistribution" :key="item.name" class="metric-chip dark">
                {{ item.name }} · {{ item.count }}
              </span>
            </div>
          </article>
        </div>

        <article class="panel">
          <div class="panel-head">
            <div>
              <h2>最新纳入样本的政策</h2>
              <p>这里优先展示最近更新、适合进一步分析的正式政策。</p>
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

      <div class="column">
        <article class="panel report-panel">
          <div class="panel-head">
            <div>
              <h2>风向标报告</h2>
              <p>最新报告会自动融合统计结果与 DeepSeek 撰稿。</p>
            </div>
          </div>
          <div class="report-list">
            <button
              v-for="item in reports"
              :key="item.id"
              type="button"
              class="report-item"
              :class="{ active: selectedReport?.id === item.id }"
              @click="selectReport(item.id)"
            >
              <strong>{{ item.title }}</strong>
              <span>{{ item.summary || '暂无摘要' }}</span>
              <small>{{ item.published_at?.slice(0, 10) }}</small>
            </button>
          </div>
          <article v-if="selectedReport" class="report-detail">
            <p class="report-meta">{{ selectedReport.category }} · {{ selectedReport.published_at?.slice(0, 10) }}</p>
            <h3>{{ selectedReport.title }}</h3>
            <p class="report-summary">{{ selectedReport.summary }}</p>
            <pre class="report-content">{{ selectedReport.content }}</pre>
          </article>
          <el-empty v-else description="暂无报告，先生成一篇最新风向标报告" />
        </article>

        <article class="panel glossary-panel">
          <div class="panel-head">
            <div>
              <h2>智库词典</h2>
              <p>用于增强热点识别和报告解读的术语资产。</p>
            </div>
            <el-button size="small" type="primary" plain @click="openCreateGlossary">新增词条</el-button>
          </div>

          <div class="glossary-filters">
            <el-input v-model="filters.glossaryKeyword" placeholder="搜索术语或说明" clearable @change="loadGlossary" />
            <el-select v-model="filters.glossaryCategory" placeholder="全部类别" clearable @change="loadGlossary">
              <el-option label="政策主题" value="政策主题" />
              <el-option label="主体类型" value="主体类型" />
              <el-option label="支持方向" value="支持方向" />
              <el-option label="风险提示" value="风险提示" />
            </el-select>
          </div>

          <div class="glossary-list">
            <article v-for="item in glossaryItems" :key="item.id" class="glossary-card">
              <div class="glossary-card-head">
                <div>
                  <h3>{{ item.term }}</h3>
                  <p>{{ item.category }} · 权重 {{ item.weight }}</p>
                </div>
                <el-tag :type="item.enabled ? 'success' : 'info'">{{ item.enabled ? '启用中' : '已停用' }}</el-tag>
              </div>
              <p class="glossary-desc">{{ item.description }}</p>
              <div v-if="item.aliases?.length" class="alias-row">
                <span v-for="alias in item.aliases" :key="alias" class="alias-chip">{{ alias }}</span>
              </div>
              <div class="glossary-actions">
                <el-button size="small" plain @click="openEditGlossary(item)">编辑</el-button>
                <el-button
                  size="small"
                  type="danger"
                  plain
                  :loading="deletingGlossaryId === item.id"
                  @click="removeGlossary(item)"
                >
                  删除
                </el-button>
              </div>
            </article>
          </div>
        </article>
      </div>
    </section>

    <el-dialog
      v-model="glossaryDialogVisible"
      :title="editingGlossaryId ? '编辑词条' : '新增词条'"
      width="520px"
      destroy-on-close
    >
      <el-form label-position="top">
        <el-form-item label="术语">
          <el-input v-model="glossaryForm.term" placeholder="例如：高标准农田" />
        </el-form-item>
        <el-form-item label="类别">
          <el-select v-model="glossaryForm.category">
            <el-option label="政策主题" value="政策主题" />
            <el-option label="主体类型" value="主体类型" />
            <el-option label="支持方向" value="支持方向" />
            <el-option label="风险提示" value="风险提示" />
          </el-select>
        </el-form-item>
        <el-form-item label="别名">
          <el-input v-model="glossaryForm.aliases" placeholder="多个别名用中文逗号分隔" />
        </el-form-item>
        <el-form-item label="权重">
          <el-input-number v-model="glossaryForm.weight" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="glossaryForm.description" type="textarea" :rows="4" placeholder="说明该术语代表的政策含义" />
        </el-form-item>
        <el-form-item>
          <el-switch v-model="glossaryForm.enabled" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="glossaryDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingGlossary" @click="saveGlossary">保存词条</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.compass-page {
  min-height: 100%;
  padding: 32px;
  color: #14213d;
  background:
    radial-gradient(circle at top right, rgba(240, 183, 74, 0.18), transparent 26%),
    linear-gradient(180deg, #fbf7ef 0%, #f3efe5 52%, #ece7dc 100%);
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
  border-radius: 28px;
  background: rgba(255, 252, 246, 0.88);
  border: 1px solid rgba(20, 33, 61, 0.08);
  box-shadow: 0 24px 60px rgba(20, 33, 61, 0.08);
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #8c6b2f;
}

.hero h1 {
  margin: 0;
  font-size: 36px;
  line-height: 1.05;
}

.hero-copy {
  max-width: 760px;
  margin: 14px 0 0;
  line-height: 1.7;
  color: #4a5568;
}

.hero-actions {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}

.month-select {
  width: 136px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.stat-card {
  padding: 20px;
  border-radius: 22px;
  color: #14213d;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(20, 33, 61, 0.08);
}

.stat-card[data-accent='amber'] {
  background: linear-gradient(135deg, rgba(244, 214, 140, 0.58), rgba(255, 255, 255, 0.92));
}

.stat-card[data-accent='teal'] {
  background: linear-gradient(135deg, rgba(177, 226, 220, 0.58), rgba(255, 255, 255, 0.92));
}

.stat-card[data-accent='ink'] {
  background: linear-gradient(135deg, rgba(197, 206, 233, 0.58), rgba(255, 255, 255, 0.92));
}

.stat-card[data-accent='rose'] {
  background: linear-gradient(135deg, rgba(239, 205, 214, 0.62), rgba(255, 255, 255, 0.92));
}

.stat-label {
  display: block;
  font-size: 14px;
  color: #5a6578;
}

.stat-value {
  display: block;
  margin-top: 8px;
  font-size: 36px;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.65fr) minmax(320px, 0.95fr);
  gap: 18px;
  margin-top: 20px;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.panel {
  padding: 22px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(20, 33, 61, 0.08);
  box-shadow: 0 18px 48px rgba(20, 33, 61, 0.06);
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.panel-head h2 {
  margin: 0;
  font-size: 20px;
}

.panel-head p {
  margin: 6px 0 0;
  color: #687385;
  line-height: 1.6;
}

.trend-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(78px, 1fr));
  gap: 12px;
  align-items: end;
  min-height: 230px;
}

.trend-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.trend-period {
  font-size: 12px;
  color: #7a8698;
}

.trend-bar-shell {
  display: flex;
  align-items: end;
  width: 100%;
  height: 150px;
  padding: 8px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 244, 213, 0.8), rgba(255, 255, 255, 0.4));
}

.trend-bar {
  width: 100%;
  min-height: 12px;
  border-radius: 14px 14px 6px 6px;
  background: linear-gradient(180deg, #efb64d 0%, #d88718 100%);
}

.two-up {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.ranking-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 120px;
  gap: 12px;
  align-items: center;
}

.ranking-item strong,
.recent-card h3,
.glossary-card h3,
.report-item strong {
  font-family: Georgia, 'Times New Roman', serif;
}

.ranking-item span {
  display: block;
  margin-top: 4px;
  font-size: 13px;
  color: #748093;
}

.line-shell {
  height: 10px;
  border-radius: 999px;
  background: rgba(20, 33, 61, 0.08);
  overflow: hidden;
}

.line-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #d68f28, #f5c96a);
}

.line-fill.accent-ink {
  background: linear-gradient(90deg, #3f5375, #7f95b6);
}

.chip-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.metric-chip,
.alias-chip {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 13px;
  background: rgba(240, 183, 74, 0.12);
  color: #8a5a00;
}

.metric-chip.soft {
  background: rgba(63, 83, 117, 0.08);
  color: #37506f;
}

.metric-chip.dark {
  background: rgba(20, 33, 61, 0.1);
  color: #14213d;
}

.recent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.recent-card {
  padding: 16px;
  border-radius: 18px;
  background: rgba(255, 252, 245, 0.85);
  border: 1px solid rgba(20, 33, 61, 0.08);
}

.recent-topline {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
  color: #86622d;
}

.recent-card h3 {
  margin: 12px 0 8px;
  font-size: 18px;
}

.recent-card p {
  margin: 0;
  line-height: 1.6;
  color: #5b6678;
}

.recent-card small {
  display: block;
  margin-top: 10px;
  color: #7a8597;
}

.report-panel,
.glossary-panel {
  height: fit-content;
}

.report-list,
.glossary-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.report-item {
  width: 100%;
  padding: 14px 16px;
  text-align: left;
  border: 1px solid rgba(20, 33, 61, 0.08);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.75);
  cursor: pointer;
}

.report-item.active {
  border-color: rgba(214, 143, 40, 0.6);
  background: rgba(255, 246, 224, 0.88);
}

.report-item span,
.report-item small {
  display: block;
  margin-top: 6px;
  color: #667387;
}

.report-detail {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid rgba(20, 33, 61, 0.08);
}

.report-meta {
  margin: 0;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #8b6d38;
}

.report-detail h3 {
  margin: 10px 0 8px;
  font-size: 24px;
}

.report-summary {
  margin: 0 0 12px;
  line-height: 1.7;
  color: #4b5668;
}

.report-content {
  white-space: pre-wrap;
  font-family: inherit;
  line-height: 1.7;
  color: #243247;
  background: rgba(248, 245, 237, 0.85);
  border-radius: 16px;
  padding: 16px;
}

.glossary-filters {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 140px;
  gap: 12px;
  margin-bottom: 14px;
}

.glossary-card {
  padding: 16px;
  border-radius: 18px;
  background: rgba(250, 249, 246, 0.86);
  border: 1px solid rgba(20, 33, 61, 0.08);
}

.glossary-card-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}

.glossary-card-head h3 {
  margin: 0;
  font-size: 18px;
}

.glossary-card-head p {
  margin: 6px 0 0;
  color: #7c8798;
}

.glossary-desc {
  margin: 12px 0 0;
  line-height: 1.7;
  color: #49586f;
}

.alias-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.glossary-actions {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}

@media (max-width: 1180px) {
  .content-grid,
  .two-up,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .hero {
    flex-direction: column;
  }

  .hero-actions {
    align-items: stretch;
  }
}

@media (max-width: 720px) {
  .compass-page {
    padding: 18px;
  }

  .glossary-filters {
    grid-template-columns: 1fr;
  }

  .ranking-item {
    grid-template-columns: 1fr;
  }
}
</style>
