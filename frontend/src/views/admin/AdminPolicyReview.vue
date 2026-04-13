<template>
  <div class="page-shell admin-policy-review">
    <section class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">规则质量审核台</h3>
        <p class="page-subtitle">
          所有新政策会先进入审核队列。你可以查看原文、编辑规则草稿，并结合 AI 审核建议做最终决策。
        </p>
      </div>
      <div class="page-actions">
        <el-button plain :loading="listLoading" @click="loadList">刷新列表</el-button>
        <el-button type="primary" @click="router.push('/admin/policies/new')">新建待审核任务</el-button>
      </div>
    </section>

    <section class="page-panel">
      <div class="stat-grid review-stat-grid">
        <div class="stat-card">
          <span class="stat-label">待审核</span>
          <strong class="stat-value">{{ stats.pending }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">已通过</span>
          <strong class="stat-value">{{ stats.approved }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">已驳回</span>
          <strong class="stat-value">{{ stats.rejected }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">AI 失败</span>
          <strong class="stat-value">{{ stats.ai_failed }}</strong>
        </div>
      </div>

      <div class="review-filters">
        <el-select v-model="filters.review_status" clearable placeholder="审核状态" class="filter-item">
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
        <el-select v-model="filters.source_type" clearable placeholder="来源类型" class="filter-item">
          <el-option v-for="item in sourceTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="filters.category" clearable placeholder="分类" class="filter-item">
          <el-option v-for="item in CATEGORY_OPTIONS" :key="item" :label="item" :value="item" />
        </el-select>
        <el-input
          v-model="filters.keyword"
          clearable
          placeholder="按标题、来源、摘要搜索"
          class="filter-item keyword"
          @keyup.enter="handleFilter"
        />
        <el-button type="primary" @click="handleFilter">筛选</el-button>
      </div>
    </section>

    <section class="review-layout">
      <div class="page-panel list-panel">
        <div class="panel-head">
          <div>
            <h3 class="panel-title">审核任务列表</h3>
            <p class="panel-subtitle">选择一条任务查看原文、规则草稿和 AI 审核建议。</p>
          </div>
        </div>

        <el-table
          v-loading="listLoading"
          :data="tasks"
          row-key="id"
          class="surface-table"
          height="640"
          highlight-current-row
          :current-row-key="selectedTaskId"
          @current-change="handleSelectTask"
        >
          <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
          <el-table-column prop="source" label="来源" min-width="140" show-overflow-tooltip />
          <el-table-column label="类型" width="110">
            <template #default="{ row }">{{ sourceTypeText(row.source_type) }}</template>
          </el-table-column>
          <el-table-column prop="ai_category" label="AI 分类" width="130" show-overflow-tooltip />
          <el-table-column label="AI 建议" width="110">
            <template #default="{ row }">
              <el-tag size="small" :type="recommendationType(row.ai_recommendation)" effect="light">
                {{ recommendationText(row.ai_recommendation) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="reviewStatusType(row.review_status)" effect="light">
                {{ reviewStatusText(row.review_status) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          class="surface-pagination"
          @current-change="loadList"
          @size-change="handlePageSizeChange"
        />
      </div>

      <div class="review-main">
        <section class="page-panel detail-panel">
          <div v-if="detailLoading" class="empty-hint">加载详情中...</div>
          <div v-else-if="!detail" class="empty-hint">请选择左侧任务查看详情。</div>
          <template v-else>
            <div class="panel-head">
              <div>
                <h3 class="panel-title">原文与规则草稿</h3>
                <p class="panel-subtitle">先核对政策原文，再确认规则 JSON 是否可信。</p>
              </div>
              <div class="tag-row">
                <el-tag :type="reviewStatusType(detail.review_status)" effect="light">
                  {{ reviewStatusText(detail.review_status) }}
                </el-tag>
                <el-tag :type="aiStatusType(detail.ai_status)" effect="light">
                  AI {{ aiStatusText(detail.ai_status) }}
                </el-tag>
              </div>
            </div>

            <div class="detail-meta-grid">
              <div class="detail-block">
                <span class="detail-label">原始标题</span>
                <strong>{{ detail.title }}</strong>
              </div>
              <div class="detail-block">
                <span class="detail-label">来源类型</span>
                <strong>{{ sourceTypeText(detail.source_type) }}</strong>
              </div>
              <div class="detail-block">
                <span class="detail-label">来源机构</span>
                <strong>{{ detail.source || '未提供' }}</strong>
              </div>
              <div class="detail-block">
                <span class="detail-label">原文链接</span>
                <el-link
                  v-if="isUrl(detail.raw_text_ref || detail.source_ref)"
                  type="primary"
                  :href="detail.raw_text_ref || detail.source_ref"
                  target="_blank"
                  rel="noopener"
                >
                  打开原文
                </el-link>
                <span v-else class="muted-text">无链接</span>
              </div>
            </div>

            <div class="detail-block raw-text-block">
              <span class="detail-label">政策原文</span>
              <pre class="raw-text">{{ detail.raw_text }}</pre>
            </div>

            <el-alert
              v-if="conditionTreeStatusMessage"
              :type="detail.draft_status === 'failed' ? 'error' : (detail.draft_status === 'success' ? 'success' : 'info')"
              :closable="false"
              class="ai-status-alert"
            >
              {{ conditionTreeStatusMessage }}
            </el-alert>

            <el-form label-position="top" class="draft-form">
              <div class="draft-grid">
                <el-form-item label="草稿标题">
                  <el-input v-model="draft.title" />
                </el-form-item>
                <el-form-item label="草稿来源">
                  <el-input v-model="draft.source" clearable />
                </el-form-item>
              </div>

              <div class="draft-grid draft-grid-meta">
                <el-form-item label="分类">
                  <el-select v-model="draft.category" class="full-width">
                    <el-option v-for="item in CATEGORY_OPTIONS" :key="item" :label="item" :value="item" />
                  </el-select>
                </el-form-item>
                <el-form-item label="文件类型">
                  <el-select v-model="draft.fileType" clearable class="full-width">
                    <el-option v-for="item in fileTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
                  </el-select>
                </el-form-item>
                <el-form-item label="效力状态">
                  <el-select v-model="draft.validityStatus" clearable class="full-width">
                    <el-option v-for="item in validityOptions" :key="item" :label="item" :value="item" />
                  </el-select>
                </el-form-item>
                <el-form-item label="生效日期">
                  <el-date-picker
                    v-model="draft.effectiveDate"
                    type="date"
                    value-format="YYYY-MM-DD"
                    placeholder="可选"
                    class="full-width"
                  />
                </el-form-item>
                <el-form-item label="失效日期">
                  <el-date-picker
                    v-model="draft.expiryDate"
                    type="date"
                    value-format="YYYY-MM-DD"
                    placeholder="可选"
                    class="full-width"
                  />
                </el-form-item>
              </div>

              <el-form-item label="草稿摘要">
                <el-input v-model="draft.summary" type="textarea" :rows="4" />
              </el-form-item>
              <el-form-item label="规则 JSON 草稿">
                <el-input v-model="draft.conditionTreeJson" type="textarea" :rows="16" class="json-textarea" />
              </el-form-item>
              <el-form-item v-if="detail.condition_tree_compile_quality" label="条件树质量">
                <el-tag :type="compileQualityType(detail.condition_tree_compile_quality)" effect="light">
                  {{ detail.condition_tree_compile_quality }}
                </el-tag>
              </el-form-item>
              <el-form-item v-if="detail.condition_tree_applicable_subjects?.length" label="适用主体">
                <div class="chip-wrap">
                  <el-tag v-for="item in detail.condition_tree_applicable_subjects" :key="item" effect="light">{{ item }}</el-tag>
                </div>
              </el-form-item>
              <el-form-item v-if="detail.condition_tree_missing_information?.length" label="缺失信息">
                <ul class="soft-list compact-list">
                  <li v-for="item in detail.condition_tree_missing_information" :key="item">{{ item }}</li>
                </ul>
              </el-form-item>
              <el-form-item v-if="detail.condition_tree_uncertain_points?.length" label="不确定项">
                <ul class="soft-list compact-list">
                  <li v-for="item in detail.condition_tree_uncertain_points" :key="item">{{ item }}</li>
                </ul>
              </el-form-item>
            </el-form>

            <div class="page-actions">
              <el-button plain :loading="refreshTreeLoading" @click="handleRefreshConditionTree">重生成条件树</el-button>
              <el-button type="primary" :loading="saveLoading" @click="handleSaveDraft">保存草稿</el-button>
              <el-button
                type="success"
                :loading="approveLoading"
                :disabled="detail.review_status !== 'pending'"
                @click="handleApprove"
              >
                编辑后通过
              </el-button>
              <el-button
                type="danger"
                plain
                :loading="rejectLoading"
                :disabled="detail.review_status !== 'pending'"
                @click="handleReject"
              >
                驳回
              </el-button>
            </div>

            <div v-if="detail.events?.length" class="timeline-wrap">
              <h4 class="panel-title small">审核留痕</h4>
              <el-timeline>
                <el-timeline-item
                  v-for="event in detail.events"
                  :key="event.id"
                  :timestamp="formatTime(event.created_at)"
                  placement="top"
                >
                  <div class="timeline-card">
                    <strong>{{ eventTypeText(event.event_type) }}</strong>
                    <p class="timeline-meta">操作人：{{ event.operator || '系统' }}</p>
                    <p v-if="event.comment" class="timeline-comment">{{ event.comment }}</p>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </template>
        </section>

        <aside class="page-panel ai-panel">
          <div v-if="!detail" class="empty-hint">选择任务后查看 AI 审核助手。</div>
          <template v-else>
            <div class="panel-head">
              <div>
                <h3 class="panel-title">AI 审核助手</h3>
                <p class="panel-subtitle">DeepSeek 输出摘要、分类、审核建议和证据条款，仅供人工复核。</p>
              </div>
              <div class="ai-actions">
                <el-button v-if="currentAIRunId" size="small" @click="router.push('/admin/tasks')">查看后台任务</el-button>
                <el-button plain size="small" :loading="refreshAILoading" @click="handleRefreshAI">重新生成</el-button>
              </div>
            </div>

            <div class="ai-disclaimer">
              AI 仅为辅助判断，不代表最终审核结论，请始终以原文和规则草稿复核为准。
            </div>

            <el-alert
              v-if="aiStatusMessage"
              :type="detail.ai_status === 'failed' ? 'error' : 'info'"
              :closable="false"
              class="ai-status-alert"
            >
              {{ aiStatusMessage }}
            </el-alert>

            <div class="detail-block">
              <span class="detail-label">AI 摘要</span>
              <p class="detail-paragraph">{{ detail.ai_summary || detail.ai_error || '暂无 AI 输出' }}</p>
            </div>

            <div class="detail-block">
              <span class="detail-label">AI 分类</span>
              <strong>{{ detail.ai_category || '未分类' }}</strong>
            </div>

            <div class="detail-block">
              <span class="detail-label">审核建议</span>
              <p class="detail-paragraph">{{ detail.ai_suggestion || '暂无建议' }}</p>
            </div>

            <div class="detail-block">
              <span class="detail-label">是否建议通过</span>
              <el-tag :type="recommendationType(detail.ai_recommendation)" effect="light">
                {{ recommendationText(detail.ai_recommendation) }}
              </el-tag>
            </div>

            <div class="detail-block">
              <span class="detail-label">主要风险点</span>
              <ul v-if="detail.ai_risk_points_json?.length" class="soft-list risk-list">
                <li v-for="(item, idx) in detail.ai_risk_points_json" :key="`${idx}-${riskPointTitle(item)}-${riskPointDetail(item)}`">
                  <strong>{{ riskPointTitle(item) }}</strong>
                  <p>{{ riskPointDetail(item) }}</p>
                </li>
              </ul>
              <p v-else class="detail-paragraph">暂无风险点。</p>
            </div>

            <div class="detail-block">
              <span class="detail-label">依据条款</span>
              <div v-if="detail.ai_evidence_json?.length" class="evidence-list">
                <article
                  v-for="(item, idx) in detail.ai_evidence_json"
                  :key="`${idx}-${item.source_type}-${item.locator}`"
                  class="evidence-item"
                >
                  <div class="evidence-head">
                    <strong>{{ evidenceLocator(item, idx) }}</strong>
                    <el-tag size="small" effect="light">{{ evidenceSourceText(item?.source_type) }}</el-tag>
                  </div>
                  <p class="evidence-excerpt">{{ evidenceExcerpt(item) }}</p>
                  <p class="evidence-relevance">{{ evidenceRelevance(item) }}</p>
                </article>
              </div>
              <p v-else class="detail-paragraph">本次 AI 未定位到稳定依据，请人工重点复核原文。</p>
            </div>

            <div v-if="detail.rejection_reason" class="detail-block">
              <span class="detail-label">最近驳回原因</span>
              <p class="detail-paragraph">{{ detail.rejection_reason }}</p>
            </div>
          </template>
        </aside>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  approvePolicyReviewTask,
  getAdminRun,
  getPolicyReviewTask,
  getPolicyReviewTasks,
  refreshPolicyReviewAI,
  refreshPolicyReviewConditionTree,
  rejectPolicyReviewTask,
  updatePolicyReviewDraft,
} from '../../api/review'

const router = useRouter()

const CATEGORY_OPTIONS = ['高标准农田', '绿色种养', '农机装备', '数字农业', '冷链物流', '设施农业', '农产品加工', '金融保险', '其他']
const fileTypeOptions = [
  { value: 'gfxwj', label: '规范性文件' },
  { value: 'qtzd', label: '其他主动公开文件' },
  { value: 'zcjd', label: '政策解读' },
]
const validityOptions = ['有效', '失效', '废止', '已修改', '待生效']
const sourceTypeOptions = [
  { value: 'crawler', label: '自动抓取' },
  { value: 'file', label: '文件上传' },
  { value: 'manual', label: '手动新增' },
]

const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const listLoading = ref(false)
const detailLoading = ref(false)
const saveLoading = ref(false)
const approveLoading = ref(false)
const rejectLoading = ref(false)
const refreshAILoading = ref(false)
const refreshTreeLoading = ref(false)
const tasks = ref([])
const selectedTaskId = ref(null)
const detail = ref(null)
const currentAIRunId = ref(null)
const currentAIRunMessage = ref('')

const stats = reactive({
  pending: 0,
  approved: 0,
  rejected: 0,
  ai_failed: 0,
})

const filters = reactive({
  review_status: 'pending',
  source_type: '',
  category: '',
  keyword: '',
})

const draft = reactive({
  title: '',
  source: '',
  summary: '',
  category: '其他',
  fileType: '',
  validityStatus: '',
  effectiveDate: '',
  expiryDate: '',
  conditionTreeJson: '{}',
})

const failedAutoRefreshAttempts = new Set()
let detailPollTimer = null
let runPollTimer = null
let treeRunPollTimer = null

const aiStatusMessage = computed(() => {
  if (currentAIRunId.value && currentAIRunMessage.value && detail.value?.id === selectedTaskId.value) {
    return currentAIRunMessage.value
  }
  if (detail.value?.ai_status === 'pending') {
    return 'AI 审核建议生成中，页面会自动刷新结果。'
  }
  if (detail.value?.ai_status === 'failed') {
    return detail.value?.ai_error || 'AI 审核建议生成失败，可手动重试。'
  }
  return ''
})

function friendlyConditionTreeMessage(message, status) {
  const text = String(message || '').trim()
  if (status === 'pending') {
    return '条件树生成中，页面会自动刷新结果。'
  }
  if (!text) {
    return status === 'failed' ? '条件树生成失败，可手动重试。' : '条件树生成成功。'
  }
  if (text.includes('请求超时') || text.includes('timed out')) {
    return '条件树生成超时。系统已经调用真实 DeepSeek，但本次等待过长，请稍后点击“重生成条件树”再试。'
  }
  if (text.includes('网络连接失败') || text.includes('连接超时') || text.includes('proxy') || text.includes('ConnectError')) {
    return '条件树生成时无法连接到 DeepSeek。请检查当前网络或代理设置后重试。'
  }
  if (text.includes('DEEPSEEK_API_KEY')) {
    return '当前环境未正确配置 DeepSeek API Key，暂时无法生成条件树。'
  }
  return text
}

const conditionTreeStatusMessage = computed(() => {
  if (!detail.value) return ''
  if (detail.value.draft_status === 'pending') {
    return friendlyConditionTreeMessage('', 'pending')
  }
  if (detail.value.draft_status === 'failed') {
    return friendlyConditionTreeMessage(detail.value.condition_tree_error, 'failed')
  }
  if (detail.value.draft_status === 'success') {
    return friendlyConditionTreeMessage(detail.value.condition_tree_reason, 'success')
  }
  return ''
})

function isUrl(value) {
  return typeof value === 'string' && (value.startsWith('http://') || value.startsWith('https://'))
}

function formatTime(value) {
  if (!value) return '暂无记录'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

function sourceTypeText(value) {
  if (value === 'crawler') return '自动抓取'
  if (value === 'file' || value === 'upload') return '文件上传'
  if (value === 'manual') return '手动新增'
  return '未知'
}

function reviewStatusText(value) {
  if (value === 'approved') return '已通过'
  if (value === 'rejected') return '已驳回'
  return '待审核'
}

function reviewStatusType(value) {
  if (value === 'approved') return 'success'
  if (value === 'rejected') return 'danger'
  return 'warning'
}

function aiStatusText(value) {
  if (value === 'success') return '成功'
  if (value === 'failed') return '失败'
  return '处理中'
}

function aiStatusType(value) {
  if (value === 'success') return 'success'
  if (value === 'failed') return 'danger'
  return 'info'
}

function recommendationText(value) {
  if (value === 'approve') return '建议通过'
  if (value === 'reject') return '建议驳回'
  return '建议复核'
}

function recommendationType(value) {
  if (value === 'approve') return 'success'
  if (value === 'reject') return 'danger'
  return 'warning'
}

function compileQualityType(value) {
  if (value === 'generated') return 'success'
  if (value === 'partial') return 'warning'
  if (value === 'failed') return 'danger'
  return 'info'
}

function evidenceSourceText(value) {
  return value === 'draft_tree' ? '规则草稿' : '原文条款'
}

function riskPointTitle(item) {
  if (item && typeof item === 'object') return item.title || '风险提示'
  return '风险提示'
}

function riskPointDetail(item) {
  if (item && typeof item === 'object') return item.detail || '暂无说明'
  return String(item || '暂无说明')
}

function evidenceLocator(item, idx) {
  if (item && typeof item === 'object') return item.locator || `证据 ${idx + 1}`
  return `证据 ${idx + 1}`
}

function evidenceExcerpt(item) {
  if (item && typeof item === 'object') return item.excerpt || item.quote || '暂无摘录'
  return String(item || '暂无摘录')
}

function evidenceRelevance(item) {
  if (item && typeof item === 'object') return item.relevance || item.reason || '暂无关联说明'
  return '暂无关联说明'
}

function eventTypeText(value) {
  if (value === 'created') return '任务创建'
  if (value === 'draft_saved') return '草稿保存'
  if (value === 'approved') return '审核通过'
  if (value === 'rejected') return '审核驳回'
  if (value === 'enriched') return 'AI 初次补全'
  if (value === 'enrich_failed') return 'AI 初次补全失败'
  if (value === 'ai_refresh_requested') return 'AI 重跑请求'
  if (value === 'ai_refreshed') return 'AI 重新生成'
  if (value === 'ai_refresh_failed') return 'AI 重跑失败'
  return value
}

function fillDraftForm(task) {
  draft.title = task?.draft_title || task?.title || ''
  draft.source = task?.draft_source || task?.source || ''
  draft.summary = task?.draft_summary || ''
  draft.category = task?.draft_category || task?.ai_category || '其他'
  draft.fileType = task?.draft_file_type || ''
  draft.validityStatus = task?.draft_validity_status || ''
  draft.effectiveDate = task?.draft_effective_date || ''
  draft.expiryDate = task?.draft_expiry_date || ''
  draft.conditionTreeJson = JSON.stringify(task?.draft_condition_tree || {}, null, 2)
}

function stopDetailPolling() {
  if (detailPollTimer) {
    window.clearInterval(detailPollTimer)
    detailPollTimer = null
  }
}

function stopRunPolling() {
  if (runPollTimer) {
    window.clearInterval(runPollTimer)
    runPollTimer = null
  }
  currentAIRunId.value = null
  currentAIRunMessage.value = ''
}

function stopTreeRunPolling() {
  if (treeRunPollTimer) {
    window.clearInterval(treeRunPollTimer)
    treeRunPollTimer = null
  }
}

function startDetailPolling(taskId) {
  stopDetailPolling()
  detailPollTimer = window.setInterval(async () => {
    if (!selectedTaskId.value || selectedTaskId.value !== taskId) {
      stopDetailPolling()
      return
    }
    await loadDetail(taskId, { silent: true, allowAutoRefresh: false })
    if (detail.value?.ai_status !== 'pending' && detail.value?.draft_status !== 'pending') {
      stopDetailPolling()
    }
  }, 4000)
}

async function pollAIRun(runId) {
  if (!selectedTaskId.value) return
  const res = await getAdminRun(runId)
  const run = res.run || {}
  currentAIRunMessage.value = run.summary_message || run.progress?.message || ''
  if (['success', 'partial', 'failed'].includes(run.status)) {
    stopRunPolling()
    await loadDetail(selectedTaskId.value, { silent: true, allowAutoRefresh: false })
    if (detail.value?.ai_status === 'pending') {
      startDetailPolling(selectedTaskId.value)
    }
  }
}

function startRunPolling(runId) {
  stopRunPolling()
  stopDetailPolling()
  currentAIRunId.value = runId
  void pollAIRun(runId)
  runPollTimer = window.setInterval(async () => {
    if (!selectedTaskId.value) {
      stopRunPolling()
      return
    }
    await pollAIRun(runId)
  }, 3000)
}

async function pollTreeRun(runId) {
  if (!selectedTaskId.value) return
  const res = await getAdminRun(runId)
  const run = res.run || {}
  if (['success', 'partial', 'failed'].includes(run.status)) {
    stopTreeRunPolling()
    await loadDetail(selectedTaskId.value, { silent: true, allowAutoRefresh: false })
  }
}

function startTreeRunPolling(runId) {
  stopTreeRunPolling()
  void pollTreeRun(runId)
  treeRunPollTimer = window.setInterval(async () => {
    if (!selectedTaskId.value) {
      stopTreeRunPolling()
      return
    }
    await pollTreeRun(runId)
  }, 3000)
}

async function triggerAIRefresh({ taskId = selectedTaskId.value, silent = false } = {}) {
  if (!taskId) return null
  if (!silent) refreshAILoading.value = true
  try {
    const run = await refreshPolicyReviewAI(taskId)
    startRunPolling(run.run_id)
    if (!silent) {
      ElMessage.success(run.reused ? '已挂接现有 AI 任务' : 'AI 重跑任务已创建')
    }
    return run
  } catch (error) {
    if (!silent) {
      ElMessage.error(error?.message || '创建 AI 重跑任务失败')
    }
    return null
  } finally {
    if (!silent) refreshAILoading.value = false
  }
}

async function handleDetailAIActions(task) {
  if (!task || task.id !== selectedTaskId.value) return
  if (task.ai_status === 'success' && task.draft_status !== 'pending') {
    stopDetailPolling()
  }
  if (task.ai_status === 'pending' || task.draft_status === 'pending') {
    startDetailPolling(task.id)
    return
  }
  if (task.ai_status === 'failed' && !failedAutoRefreshAttempts.has(task.id)) {
    failedAutoRefreshAttempts.add(task.id)
    await triggerAIRefresh({ taskId: task.id, silent: true })
  }
}

async function loadDetail(taskId, { silent = false, allowAutoRefresh = true } = {}) {
  if (!taskId) {
    detail.value = null
    stopDetailPolling()
    stopRunPolling()
    stopTreeRunPolling()
    return
  }
  if (!silent) detailLoading.value = true
  try {
    detail.value = await getPolicyReviewTask(taskId)
    fillDraftForm(detail.value)
    if (allowAutoRefresh) {
      await handleDetailAIActions(detail.value)
    }
  } catch (error) {
    if (!silent) {
      ElMessage.error(error?.message || '加载审核详情失败')
    }
  } finally {
    if (!silent) detailLoading.value = false
  }
}

async function loadList() {
  listLoading.value = true
  try {
    const response = await getPolicyReviewTasks({
      offset: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      review_status: filters.review_status || undefined,
      source_type: filters.source_type || undefined,
      category: filters.category || undefined,
      keyword: filters.keyword || undefined,
    })
    tasks.value = response.items || []
    total.value = response.total || 0
    stats.pending = response.stats?.pending || 0
    stats.approved = response.stats?.approved || 0
    stats.rejected = response.stats?.rejected || 0
    stats.ai_failed = response.stats?.ai_failed || 0

    const hasSelected = tasks.value.some((item) => item.id === selectedTaskId.value)
    if (!hasSelected) {
      selectedTaskId.value = tasks.value[0]?.id || null
    }
    if (selectedTaskId.value) {
      await loadDetail(selectedTaskId.value)
    } else {
      detail.value = null
      stopDetailPolling()
      stopRunPolling()
      stopTreeRunPolling()
    }
  } catch (error) {
    ElMessage.error(error?.message || '加载审核任务失败')
  } finally {
    listLoading.value = false
  }
}

function handleSelectTask(row) {
  selectedTaskId.value = row?.id || null
  stopDetailPolling()
  stopRunPolling()
  stopTreeRunPolling()
  if (selectedTaskId.value) {
    void loadDetail(selectedTaskId.value)
  } else {
    detail.value = null
  }
}

function handleFilter() {
  page.value = 1
  void loadList()
}

function handlePageSizeChange() {
  page.value = 1
  void loadList()
}

function parseDraftTree() {
  try {
    return JSON.parse(draft.conditionTreeJson || '{}')
  } catch {
    throw new Error('规则 JSON 不是合法格式')
  }
}

async function saveDraftOnly() {
  if (!selectedTaskId.value) return null
  return updatePolicyReviewDraft(selectedTaskId.value, {
    draft_title: draft.title,
    draft_source: draft.source || null,
    draft_summary: draft.summary || null,
    draft_category: draft.category,
    draft_file_type: draft.fileType || null,
    draft_validity_status: draft.validityStatus || null,
    draft_effective_date: draft.effectiveDate || null,
    draft_expiry_date: draft.expiryDate || null,
    draft_condition_tree: parseDraftTree(),
  })
}

async function handleSaveDraft() {
  saveLoading.value = true
  try {
    await saveDraftOnly()
    ElMessage.success('草稿已保存')
    await Promise.all([loadList(), loadDetail(selectedTaskId.value)])
  } catch (error) {
    ElMessage.error(error?.message || '保存草稿失败')
  } finally {
    saveLoading.value = false
  }
}

async function handleApprove() {
  if (!selectedTaskId.value) return
  try {
    await ElMessageBox.confirm(
      'AI 仅为辅助判断，不代表最终审核结论。请确认你已人工核对原文、规则草稿和 AI 依据后再通过。',
      '确认审核通过',
      {
        confirmButtonText: '确认通过',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
  } catch {
    return
  }

  approveLoading.value = true
  try {
    await saveDraftOnly()
    await approvePolicyReviewTask(selectedTaskId.value, { comment: '审核通过并写入正式政策库' })
    ElMessage.success('审核通过，已写入正式政策库')
    await loadList()
  } catch (error) {
    ElMessage.error(error?.message || '审核通过失败')
  } finally {
    approveLoading.value = false
  }
}

async function handleReject() {
  if (!selectedTaskId.value) return
  try {
    const { value } = await ElMessageBox.prompt('请输入驳回原因', '驳回审核任务', {
      confirmButtonText: '确认驳回',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '驳回原因不能为空',
    })
    rejectLoading.value = true
    await rejectPolicyReviewTask(selectedTaskId.value, { reason: value })
    ElMessage.success('审核任务已驳回')
    await loadList()
  } catch (error) {
    if (error === 'cancel' || error?.action === 'cancel' || error?.action === 'close') return
    ElMessage.error(error?.message || '驳回失败')
  } finally {
    rejectLoading.value = false
  }
}

async function handleRefreshAI() {
  await triggerAIRefresh({ silent: false })
}

async function handleRefreshConditionTree() {
  if (!selectedTaskId.value) return
  refreshTreeLoading.value = true
  try {
    const run = await refreshPolicyReviewConditionTree(selectedTaskId.value)
    startTreeRunPolling(run.run_id)
    ElMessage.success(run.reused ? '已复用进行中的条件树任务' : '条件树重生成任务已创建')
  } catch (error) {
    ElMessage.error(error?.message || '创建条件树任务失败')
  } finally {
    refreshTreeLoading.value = false
  }
}

onMounted(() => {
  void loadList()
})

onBeforeUnmount(() => {
  stopDetailPolling()
  stopRunPolling()
  stopTreeRunPolling()
})
</script>

<style scoped>
.review-stat-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.review-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}

.filter-item {
  min-width: 180px;
}

.filter-item.keyword {
  min-width: 280px;
}

.review-layout {
  display: grid;
  grid-template-columns: minmax(320px, 0.95fr) minmax(0, 1.85fr);
  gap: 1rem;
}

.review-main {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.85fr);
  gap: 1rem;
}

.list-panel,
.detail-panel,
.ai-panel {
  min-width: 0;
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.panel-title {
  margin: 0;
  font-size: 1.05rem;
  color: #173323;
}

.panel-title.small {
  font-size: 0.95rem;
}

.panel-subtitle {
  margin: 0.35rem 0 0;
  color: #6a7f72;
  line-height: 1.6;
}

.surface-pagination {
  margin-top: 1rem;
  justify-content: flex-end;
}

.tag-row,
.ai-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.detail-meta-grid,
.draft-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.draft-grid-meta {
  margin-bottom: 0.5rem;
}

.detail-block {
  margin-bottom: 1rem;
}

.detail-label {
  display: inline-block;
  margin-bottom: 0.4rem;
  color: #6a7f72;
  font-size: 0.9rem;
}

.detail-paragraph {
  margin: 0;
  color: #2c4737;
  line-height: 1.75;
  white-space: pre-wrap;
}

.muted-text {
  color: #8da093;
}

.raw-text-block {
  margin-top: 1rem;
}

.raw-text {
  margin: 0;
  padding: 1rem;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(245, 249, 245, 0.9), rgba(237, 244, 239, 0.95));
  border: 1px solid rgba(17, 47, 33, 0.08);
  color: #223c2d;
  line-height: 1.72;
  max-height: 320px;
  overflow: auto;
  white-space: pre-wrap;
  font-family: "Noto Sans SC", "PingFang SC", sans-serif;
}

.draft-form {
  margin-top: 1rem;
}

.full-width {
  width: 100%;
}

.page-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.timeline-wrap {
  margin-top: 1.5rem;
}

.timeline-card {
  padding: 0.9rem 1rem;
  border-radius: 18px;
  background: rgba(245, 249, 245, 0.88);
  border: 1px solid rgba(17, 47, 33, 0.08);
}

.timeline-meta,
.timeline-comment {
  margin: 0.35rem 0 0;
  color: #6a7f72;
}

.ai-disclaimer {
  margin-bottom: 1rem;
  padding: 0.85rem 0.95rem;
  border-radius: 16px;
  background: rgba(255, 245, 214, 0.72);
  border: 1px solid rgba(173, 123, 24, 0.18);
  color: #6a4d07;
  line-height: 1.7;
}

.ai-status-alert {
  margin-bottom: 1rem;
}

.soft-list {
  margin: 0;
  padding-left: 1.1rem;
}

.compact-list {
  margin: 0;
}

.chip-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.risk-list li {
  margin-bottom: 0.75rem;
  color: #2c4737;
}

.risk-list p {
  margin: 0.25rem 0 0;
  line-height: 1.7;
}

.evidence-list {
  display: grid;
  gap: 0.85rem;
}

.evidence-item {
  padding: 0.9rem 1rem;
  border-radius: 18px;
  background: rgba(242, 247, 243, 0.92);
  border: 1px solid rgba(17, 47, 33, 0.08);
}

.evidence-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.45rem;
}

.evidence-excerpt,
.evidence-relevance {
  margin: 0;
  color: #2c4737;
  line-height: 1.7;
}

.evidence-relevance {
  margin-top: 0.45rem;
  color: #6a7f72;
}

.empty-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 320px;
  border-radius: 20px;
  background: rgba(245, 249, 245, 0.9);
  color: #6a7f72;
  text-align: center;
  padding: 1.25rem;
}

.json-textarea :deep(textarea) {
  min-height: 320px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
}

@media (max-width: 1440px) {
  .review-main {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 1120px) {
  .review-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .review-stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .review-stat-grid,
  .detail-meta-grid,
  .draft-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .filter-item,
  .filter-item.keyword {
    min-width: 100%;
  }

  .surface-table {
    width: 100%;
  }
}
</style>
