<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import { compassApi } from '../api/compass'
import { adminLogoutAll, getAdminMe, getUserMe, userLogoutAll } from '../services/authSession'
import logoIcon from '../assets/logo_icon.png'
import CompassHeroPanel from '../components/compass/CompassHeroPanel.vue'
import CompassForecastStage from '../components/compass/CompassForecastStage.vue'
import CompassSignalGrid from '../components/compass/CompassSignalGrid.vue'
import CompassReportShowcase from '../components/compass/CompassReportShowcase.vue'
import {
  buildCompassForecastCards,
  buildCompassKpiCards,
  buildCompassSummary,
  cleanCompassLabel,
  cleanCompassText,
  normalizeDistribution,
  normalizeGlossaryItems,
  normalizePolicyCards,
  normalizeSelectedPolicy,
} from '../utils/compassUi'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const generating = ref(false)
const glossaryDrawerVisible = ref(false)
const glossaryDialogVisible = ref(false)
const savingGlossary = ref(false)
const deletingGlossaryId = ref(null)
const editingGlossaryId = ref(null)
const isScrolled = ref(false)
const mobileMenuOpen = ref(false)
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

const filters = reactive({
  months: 6,
  glossaryKeyword: '',
  glossaryCategory: '',
})

const overview = ref(null)
const briefing = ref(null)
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

const statCards = computed(() => buildCompassKpiCards(overview.value))
const selectedPolicy = computed(() => normalizeSelectedPolicy(briefing.value?.selected_policy))
const summaryText = computed(() =>
  buildCompassSummary({
    overview: overview.value,
    briefing: briefing.value,
    selectedPolicy: selectedPolicy.value,
  })
)
const forecastCards = computed(() =>
  buildCompassForecastCards({
    overview: overview.value,
    briefing: briefing.value,
  })
)
const topThemes = computed(() => normalizeDistribution(overview.value?.theme_distribution || []))
const topIssuers = computed(() => normalizeDistribution(overview.value?.issuer_distribution || []))
const monthlyTrend = computed(() =>
  (overview.value?.monthly_trend || []).map((item) => ({
    period: item?.period || '',
    count: Number(item?.count || 0),
  }))
)
const audienceDistribution = computed(() => normalizeDistribution(overview.value?.audience_distribution || []))
const regionDistribution = computed(() => normalizeDistribution(overview.value?.region_distribution || []))
const fileTypeDistribution = computed(() => normalizeDistribution(overview.value?.file_type_distribution || []))
const validityDistribution = computed(() => normalizeDistribution(overview.value?.validity_distribution || []))
const recentPolicies = computed(() => normalizePolicyCards(overview.value?.recent_policy_cards || []))
const focusTerms = computed(() => normalizeGlossaryItems(briefing.value?.focus_terms || []))
const topAudienceSignals = computed(() => normalizeDistribution(briefing.value?.signal_highlights?.audience_distribution || []))
const reportItems = computed(() =>
  (reports.value || []).map((item) => ({
    ...item,
    title: cleanCompassText(item?.title, '未命名报告'),
    summary: cleanCompassText(item?.summary, '这份报告已经生成，正在等待更完整的摘要内容。'),
  }))
)
const selectedReportView = computed(() =>
  selectedReport.value
    ? {
        ...selectedReport.value,
        title: cleanCompassText(selectedReport.value.title, '未命名报告'),
        category: cleanCompassLabel(selectedReport.value.category, 'weekly'),
        summary: cleanCompassText(selectedReport.value.summary, '系统已生成这份风向报告。'),
        content: cleanCompassText(selectedReport.value.content, '系统已完成报告生成，请稍后再查看完整内容。'),
      }
    : null
)
const glossaryPreview = computed(() => normalizeGlossaryItems(glossaryItems.value).slice(0, 6))
const glossaryDrawerItems = computed(() => normalizeGlossaryItems(glossaryItems.value))

function widthPercent(count, items) {
  const max = Math.max(...items.map((item) => Number(item.count || 0)), 1)
  return `${Math.max((Number(count || 0) / max) * 100, 10)}%`
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

async function loadBriefing() {
  briefing.value = await compassApi.getBriefing({
    months: filters.months,
    policy_id: route.query.policyId || undefined,
  })
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
    await Promise.all([loadOverview(), loadBriefing(), loadReports(), loadGlossary()])
  } catch (error) {
    ElMessage.error(error?.message || '政策风向大屏加载失败')
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
    ElMessage.success(`已生成最新风向报告 #${payload.report_id}`)
    await Promise.all([loadOverview(), loadBriefing(), loadReports(), loadGlossary()])
  } catch (error) {
    ElMessage.error(error?.message || '生成风向报告失败')
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
    glossaryDrawerVisible.value = true
    resetGlossaryForm()
    await Promise.all([loadGlossary(), loadOverview(), loadBriefing()])
  } catch (error) {
    ElMessage.error(error?.message || '词条保存失败')
  } finally {
    savingGlossary.value = false
  }
}

async function removeGlossary(item) {
  try {
    await ElMessageBox.confirm(`确定删除词条"${item.term}"吗？`, '删除确认', { type: 'warning' })
  } catch {
    return
  }
  deletingGlossaryId.value = item.id
  try {
    await compassApi.deleteGlossary(item.id)
    ElMessage.success('词条已删除')
    await Promise.all([loadGlossary(), loadOverview(), loadBriefing()])
  } catch (error) {
    ElMessage.error(error?.message || '删除词条失败')
  } finally {
    deletingGlossaryId.value = null
  }
}

async function onGlossaryKeywordChange(value) {
  filters.glossaryKeyword = value || ''
  await loadGlossary()
}

async function onGlossaryCategoryChange(value) {
  filters.glossaryCategory = value || ''
  await loadGlossary()
}

watch(
  () => route.query.policyId,
  async () => {
    await loadBriefing()
  }
)

onMounted(async () => {
  window.addEventListener('scroll', handleScroll)
  await syncAuthState()
  await loadAll()
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="compass-page">
    <nav class="nav-bar" :class="{ 'nav-scrolled': isScrolled }">
      <div class="nav-container">
        <a class="nav-brand" href="/" @click.prevent="go('/')">
          <img class="brand-logo" :src="logoIcon" alt="AgriPolicy AI" />
          <span class="brand-titletext">AgriPolicy&nbsp;AI</span>
        </a>
        <button class="nav-hamburger" @click="mobileMenuOpen = !mobileMenuOpen" aria-label="打开导航菜单">
          <span /><span /><span />
        </button>

        <div class="nav-menu" :class="{ 'nav-menu--open': mobileMenuOpen }">
          <a class="nav-link" href="/" @click.prevent="go('/'); mobileMenuOpen = false">首页</a>
          <a class="nav-link" href="/insights" @click.prevent="go('/insights'); mobileMenuOpen = false">政策洞察</a>
          <a class="nav-link" href="/chat" @click.prevent="go('/chat'); mobileMenuOpen = false">智能工作台</a>
          <a class="nav-link" :href="consoleEntryPath" @click.prevent="go(consoleEntryPath); mobileMenuOpen = false">管理中枢</a>
          <div class="nav-divider" role="separator"></div>
          <template v-if="!hasUser">
            <a class="nav-link" href="/login" @click.prevent="go('/login'); mobileMenuOpen = false">登录</a>
            <a class="nav-link" href="/register" @click.prevent="go('/register'); mobileMenuOpen = false">注册</a>
          </template>
          <template v-else>
            <a class="nav-link" href="#" role="button" @click.prevent="logoutUser(); mobileMenuOpen = false">退出用户</a>
          </template>
          <template v-if="hasAdmin">
            <a class="nav-link" href="#" role="button" @click.prevent="logoutAdmin(); mobileMenuOpen = false">退出管理员</a>
          </template>
        </div>
      </div>
    </nav>

    <div class="compass-shell">
      <CompassHeroPanel
        :months="filters.months"
        :loading="loading"
        :generating="generating"
        :selected-policy="selectedPolicy"
        :summary="summaryText"
        @update:months="
          async (value) => {
            filters.months = value
            await loadAll()
          }
        "
        @refresh="loadAll"
        @generate="generateReport"
        @open-glossary="glossaryDrawerVisible = true"
      />

      <div class="compass-body">
        <CompassForecastStage :stat-cards="statCards" :summary="summaryText" :forecast-cards="forecastCards" />

        <CompassSignalGrid
          :monthly-trend="monthlyTrend"
          :top-themes="topThemes"
          :top-issuers="topIssuers"
          :file-type-distribution="fileTypeDistribution"
          :validity-distribution="validityDistribution"
          :audience-distribution="audienceDistribution"
          :region-distribution="regionDistribution"
          :top-audience-signals="topAudienceSignals"
          :focus-terms="focusTerms"
          :selected-policy="selectedPolicy"
          :recent-policies="recentPolicies"
          :width-percent="widthPercent"
        />

        <CompassReportShowcase
          :reports="reportItems"
          :selected-report="selectedReportView"
          :glossary-items="glossaryPreview"
          :glossary-keyword="filters.glossaryKeyword"
          :glossary-category="filters.glossaryCategory"
          @select-report="selectReport"
          @update:glossary-keyword="onGlossaryKeywordChange"
          @update:glossary-category="onGlossaryCategoryChange"
          @open-glossary="glossaryDrawerVisible = true"
        />
      </div>
    </div>

    <footer class="compass-footer">
      <div class="footer-inner">
        <p>© 2026 农策微光 (Agricultural Policy Intelligence). All rights reserved.</p>
        <div class="footer-links">
          <a href="/" @click.prevent="go('/')">首页</a>
          <a href="/insights" @click.prevent="go('/insights')">政策洞察</a>
          <a href="/chat" @click.prevent="go('/chat')">智能工作台</a>
        </div>
      </div>
    </footer>

    <el-drawer
      v-model="glossaryDrawerVisible"
      title="智库词典舱"
      size="min(520px, 92vw)"
      append-to-body
    >
      <div class="drawer-toolbar">
        <el-input
          v-model="filters.glossaryKeyword"
          placeholder="搜索术语或说明"
          clearable
          @change="loadGlossary"
        />
        <el-select v-model="filters.glossaryCategory" placeholder="全部类别" clearable @change="loadGlossary">
          <el-option label="政策主题" value="政策主题" />
          <el-option label="主体类型" value="主体类型" />
          <el-option label="支持方向" value="支持方向" />
          <el-option label="风险提示" value="风险提示" />
        </el-select>
        <el-button type="primary" @click="openCreateGlossary">新增词条</el-button>
      </div>

      <div class="drawer-list">
        <article v-for="item in glossaryDrawerItems" :key="item.id" class="drawer-card">
          <div class="drawer-card__head">
            <div>
              <h3>{{ item.term }}</h3>
              <p>{{ item.category }} · 权重 {{ item.weight }}</p>
            </div>
            <el-tag :type="item.enabled ? 'success' : 'info'">{{ item.enabled ? '启用中' : '已停用' }}</el-tag>
          </div>
          <p class="drawer-card__desc">{{ item.description }}</p>
          <div v-if="item.aliases?.length" class="drawer-card__aliases">
            <span v-for="alias in item.aliases" :key="alias">{{ alias }}</span>
          </div>
          <div class="drawer-card__actions">
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
    </el-drawer>

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
          <el-input v-model="glossaryForm.description" type="textarea" :rows="4" placeholder="补充术语所代表的政策含义" />
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
  position: relative;
  min-height: 100vh;
  background: linear-gradient(170deg, #0d1f17 0%, #14281d 50%, #0a1a12 100%);
  color: #f8f3e7;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', 'PingFang SC', 'Noto Sans SC', sans-serif;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

/* ── Floating orbs + grid overlay ────────────────────────── */
.compass-page::before {
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

.compass-page::after {
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
  text-decoration: none;
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
  transition: color 0.3s ease;
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

/* ── Shell ───────────────────────────────────────────────── */
.compass-shell {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  box-sizing: border-box;
}

.compass-body {
  display: flex;
  flex-direction: column;
  gap: 0;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 40px 32px 0;
  box-sizing: border-box;
}

/* ── Footer (dark) ───────────────────────────────────────── */
.compass-footer {
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
.footer-links a {
  font-size: 12px;
  color: rgba(228, 231, 218, 0.45);
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s;
}
.footer-links a:hover {
  color: #dcc386;
}

/* ── Drawer (dark glass) ─────────────────────────────────── */
.drawer-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 160px auto;
  gap: 12px;
  margin-bottom: 18px;
}

.drawer-list {
  display: grid;
  gap: 12px;
}

.drawer-card {
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(197, 205, 183, 0.12);
  background: linear-gradient(180deg, rgba(16, 35, 24, 0.88), rgba(11, 25, 18, 0.94));
}

.drawer-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.drawer-card__head h3 {
  margin: 0;
  font-size: 16px;
  color: #f8f3e7;
}

.drawer-card__head p {
  margin: 6px 0 0;
  font-size: 13px;
  color: rgba(228, 231, 218, 0.5);
}

.drawer-card__desc {
  margin: 10px 0 0;
  line-height: 1.7;
  font-size: 14px;
  color: rgba(228, 231, 218, 0.66);
}

.drawer-card__aliases {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.drawer-card__aliases span {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  background: rgba(137, 169, 125, 0.15);
  color: #89a97d;
  font-size: 12px;
}

.drawer-card__actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

/* ── Drawer & Dialog deep overrides for dark theme ────────── */
:deep(.el-drawer) {
  background: linear-gradient(180deg, #0f2118, #0a1a12) !important;
  color: #f8f3e7;
}
:deep(.el-drawer__header) {
  color: #f8f3e7 !important;
}
:deep(.el-drawer__title) {
  color: #f8f3e7 !important;
}
:deep(.el-dialog) {
  background: linear-gradient(180deg, #0f2118, #0a1a12) !important;
  color: #f8f3e7;
  border: 1px solid rgba(197, 205, 183, 0.1);
  border-radius: 20px !important;
}
:deep(.el-dialog__header) {
  color: #f8f3e7 !important;
}
:deep(.el-dialog__title) {
  color: #f8f3e7 !important;
}
:deep(.el-form-item__label) {
  color: rgba(228, 231, 218, 0.72) !important;
}
:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  background: rgba(4, 16, 12, 0.8) !important;
  box-shadow: inset 0 0 0 1px rgba(197, 205, 183, 0.12) !important;
  color: #f8f3e7 !important;
}
:deep(.el-input__inner) {
  color: #f8f3e7 !important;
}
:deep(.el-select__wrapper) {
  background: rgba(4, 16, 12, 0.8) !important;
  box-shadow: inset 0 0 0 1px rgba(197, 205, 183, 0.12) !important;
}
:deep(.el-select__placeholder),
:deep(.el-select__selected-item) {
  color: rgba(228, 231, 218, 0.72) !important;
}

@media (max-width: 1180px) {
  .compass-body {
    padding: 28px 20px 0;
  }
  .drawer-toolbar {
    grid-template-columns: 1fr;
  }
}

/* ── Hamburger button (hidden on desktop) ─────────────────── */
.nav-hamburger {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  flex-direction: column;
  gap: 5px;
  z-index: 110;
}
.nav-hamburger span {
  display: block;
  width: 22px;
  height: 2px;
  background: rgba(248, 243, 231, 0.8);
  border-radius: 2px;
  transition: background 0.3s;
}

@media (max-width: 720px) {
  .compass-body {
    padding: 20px 14px 0;
  }
  .nav-hamburger {
    display: flex;
  }
  .nav-menu {
    display: none;
    position: absolute;
    top: 60px;
    right: 0;
    left: 0;
    flex-direction: column;
    align-items: stretch;
    gap: 0;
    background: rgba(13, 31, 23, 0.96);
    backdrop-filter: saturate(180%) blur(20px);
    padding: 12px 32px 20px;
    border-bottom: 1px solid rgba(109, 255, 188, 0.06);
  }
  .nav-menu--open {
    display: flex;
  }
  .nav-menu .nav-link {
    padding: 10px 0;
    font-size: 13px;
  }
  .nav-divider {
    width: 100%;
    height: 1px;
    margin: 6px 0;
  }
  .footer-inner {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
