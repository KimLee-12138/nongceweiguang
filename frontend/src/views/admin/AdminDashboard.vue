<template>
  <div class="page-shell admin-dashboard">
    <section class="page-panel">
      <div class="page-head">
        <div class="page-title-group">
          <h3 class="page-title">今日概览</h3>
          <p class="page-subtitle">
            数据来自后端实时汇总（结构化政策数、待审核队列、最近一次自动爬取作业、风向标周报）。
          </p>
        </div>
        <div class="page-actions">
          <el-button plain :loading="summaryLoading" @click="loadDashboard">刷新数据</el-button>
          <el-button plain @click="router.push('/admin/tasks')">任务中心</el-button>
          <el-button plain @click="router.push('/admin/policies/import')">手动导入</el-button>
          <el-button type="primary" @click="router.push('/admin/policies/new')">新增政策</el-button>
        </div>
      </div>

      <div class="stat-grid">
        <div class="stat-card">
          <span class="stat-label">结构化政策总数</span>
          <strong class="stat-value">{{ overview.totalPolicies }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">待审核任务</span>
          <strong class="stat-value">{{ overview.pendingReview }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">最近入队数</span>
          <strong class="stat-value">{{ overview.lastQueued }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">最近自动任务状态</span>
          <strong class="stat-value">{{ statusText(lastRun.status) }}</strong>
        </div>
      </div>
    </section>

    <section class="page-grid two-column">
      <div class="page-panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">快捷操作</h3>
            <p class="panel-subtitle">常用入口统一收纳到工作台，避免在多个页面间频繁跳转。</p>
          </div>
        </div>

        <div class="quick-grid">
          <button type="button" class="quick-card" @click="router.push('/admin/policies')">
            <span class="quick-kicker">LIST</span>
            <strong>进入政策管理</strong>
            <p>查看结构化政策、打开详情、编辑和批量删除。</p>
          </button>
          <button type="button" class="quick-card" @click="router.push('/admin/policies/review')">
            <span class="quick-kicker">REVIEW</span>
            <strong>规则质量审核台</strong>
            <p>查看待审核政策、编辑规则草稿并决定是否入库。</p>
          </button>
          <button type="button" class="quick-card" @click="router.push('/admin/policies/import')">
            <span class="quick-kicker">INGEST</span>
            <strong>导入与爬取</strong>
            <p>执行文件解析、恢复抓取结果，并创建导入后台作业。</p>
          </button>
          <button type="button" class="quick-card" @click="router.push('/admin/tasks')">
            <span class="quick-kicker">TASKS</span>
            <strong>任务中心</strong>
            <p>统一查看后台作业进度、失败明细和整任务重试。</p>
          </button>
          <button type="button" class="quick-card accent" @click="handleRegenerateCompass">
            <span class="quick-kicker">COMPASS</span>
            <strong>{{ compassGenerating ? '正在创建任务' : '生成本期风向标' }}</strong>
            <p>创建周报与术语词相关的后台作业，完成后同步到前台展示。</p>
          </button>
        </div>
      </div>

      <div class="page-grid">
        <section class="page-panel">
          <h3 class="panel-title">最近自动任务</h3>
          <p class="panel-subtitle">用于确认自动爬虫与审核入队链路是否处于可用状态。</p>
          <div class="status-card">
            <el-tag :type="statusType(lastRun.status)" effect="light">{{ statusText(lastRun.status) }}</el-tag>
            <p class="admin-note">最近执行时间：<strong>{{ formatTime(lastRun.run_at) }}</strong></p>
            <ul class="soft-list">
              <li>待处理原文 {{ lastRun.crawled_count || 0 }} 条</li>
              <li>筛选通过 {{ lastRun.filtered_count || 0 }} 条</li>
              <li>进入审核队列 {{ lastRun.queued_count || 0 }} 条</li>
            </ul>
            <div class="page-actions">
              <el-button plain @click="router.push('/admin/policies/auto-crawler')">查看自动爬取</el-button>
              <el-button plain @click="router.push('/admin/tasks')">查看任务中心</el-button>
            </div>
          </div>
        </section>

        <section class="page-panel">
          <h3 class="panel-title">最近风向标</h3>
          <p class="panel-subtitle">显示最新周报标题，帮助确认前台风向标内容是否已更新。</p>
          <div class="status-card">
            <strong class="latest-title">{{ latestCompassTitle }}</strong>
            <p class="admin-note">最近刷新时间：{{ latestCompassTime }}</p>
            <div class="page-actions">
              <el-button plain @click="router.push('/compass')">查看风向标前台</el-button>
              <el-button plain @click="router.push('/chat')">查看聊天页</el-button>
            </div>
          </div>
        </section>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { api } from '../../api/client'

const router = useRouter()

const compassGenerating = ref(false)
const summaryLoading = ref(false)

const overview = reactive({
  totalPolicies: 0,
  pendingReview: 0,
  lastQueued: 0,
})

const lastRun = reactive({
  run_at: null,
  status: null,
  crawled_count: 0,
  filtered_count: 0,
  queued_count: 0,
})

const latestCompassTitle = ref('暂无周报记录')
const latestCompassTime = ref('暂无数据')

function formatTime(value) {
  if (!value) return '暂无记录'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

function applySummary(data) {
  if (!data || typeof data !== 'object') return
  overview.totalPolicies = Number(data.policy_count) || 0
  overview.pendingReview = Number(data.pending_review_count) || 0
  overview.lastQueued = Number(data.last_queued_count) || 0

  const ac = data.last_auto_crawler_run
  if (ac && typeof ac === 'object') {
    lastRun.run_at = ac.run_at ?? null
    lastRun.status = ac.status ?? null
    lastRun.crawled_count = Number(ac.crawled_count) || 0
    lastRun.filtered_count = Number(ac.filtered_count) || 0
    lastRun.queued_count = Number(ac.queued_count) || 0
  } else {
    lastRun.run_at = null
    lastRun.status = null
    lastRun.crawled_count = 0
    lastRun.filtered_count = 0
    lastRun.queued_count = 0
  }

  const rep = data.latest_compass_report
  if (rep && typeof rep === 'object' && rep.title) {
    latestCompassTitle.value = rep.title
    latestCompassTime.value = rep.published_at ? formatTime(rep.published_at) : '已生成'
  } else {
    latestCompassTitle.value = '暂无周报记录'
    latestCompassTime.value = '暂无数据'
  }
}

async function loadDashboard() {
  summaryLoading.value = true
  try {
    const data = await api.withAdmin(() => api.get('/admin-ops/dashboard-summary'))
    applySummary(data)
  } catch (e) {
    ElMessage.error(e?.message || '加载概览失败')
  } finally {
    summaryLoading.value = false
  }
}

async function handleRegenerateCompass() {
  compassGenerating.value = true
  try {
    await api.withAdmin(() => api.post('/compass/generate', {}))
    ElMessage.success('已生成风向标周报')
    await loadDashboard()
  } catch (e) {
    ElMessage.error(e?.message || '生成失败')
  } finally {
    compassGenerating.value = false
  }
}

onMounted(loadDashboard)

function statusType(status) {
  if (status === 'success') return 'success'
  if (status === 'partial') return 'warning'
  if (status === 'failed') return 'danger'
  return 'info'
}

function statusText(status) {
  if (status === 'success') return '运行成功'
  if (status === 'partial') return '部分成功'
  if (status === 'failed') return '运行失败'
  return '暂无记录'
}
</script>

<style scoped>
.panel-head {
  margin-bottom: 1rem;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.quick-card {
  padding: 1.05rem 1.05rem 1rem;
  border: 1px solid rgba(19, 59, 41, 0.1);
  border-radius: 22px;
  background: rgba(255, 253, 247, 0.8);
  text-align: left;
  cursor: pointer;
  transition:
    transform 160ms ease,
    border-color 160ms ease,
    box-shadow 160ms ease;
}

.quick-card:hover {
  transform: translateY(-2px);
  border-color: rgba(26, 95, 58, 0.25);
  box-shadow: 0 14px 28px rgba(43, 60, 48, 0.08);
}

.quick-card.accent {
  background: linear-gradient(135deg, rgba(241, 248, 237, 0.95), rgba(247, 241, 226, 0.95));
}

.quick-kicker {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.72rem;
  letter-spacing: 0.18em;
  color: #7a8778;
}

.quick-card strong {
  display: block;
  color: #173726;
  font-size: 1.02rem;
}

.quick-card p {
  margin: 0.45rem 0 0;
  color: #6d796c;
  line-height: 1.7;
}

.status-card {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding: 1rem 1.05rem;
  border-radius: 20px;
  background: rgba(255, 253, 247, 0.8);
  border: 1px solid rgba(19, 59, 41, 0.08);
}

.latest-title {
  color: #173726;
  line-height: 1.6;
}

@media (max-width: 780px) {
  .quick-grid {
    grid-template-columns: 1fr;
  }
}
</style>
