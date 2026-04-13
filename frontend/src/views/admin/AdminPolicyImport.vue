<template>
  <div class="page-shell">
    <div class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">导入与爬虫</h3>
        <p class="page-subtitle">
          统一政策入库入口：上传文件解析，或从政府网站抓取候选政策，并进入审核流程。
        </p>
      </div>
      <div class="page-actions">
        <el-button plain @click="router.push('/admin/tasks')">任务中心</el-button>
        <el-button plain @click="router.push('/admin/policies/review')">审核台</el-button>
      </div>
    </div>

    <section class="page-panel">
      <div class="panel-head">
        <h4 class="panel-title">文件上传</h4>
        <p class="panel-subtitle">支持 DOCX / PDF。小文件可同步解析预览，大文件建议提交后台任务。</p>
      </div>

      <el-upload drag :auto-upload="false" :limit="1" :on-change="onFileChange" :on-remove="onFileRemove">
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽或点击选择文件，2MB 内可同步解析预览。</div>
      </el-upload>

      <div class="actions">
        <el-button type="primary" :loading="parsing" :disabled="!fileRaw" @click="parseSync">同步解析预览</el-button>
        <el-button :loading="jobLoading" :disabled="!fileRaw" @click="parseJob">提交后台解析任务</el-button>
        <el-button type="success" :disabled="!parsedText" @click="sendToReview">送审</el-button>
      </div>

      <el-alert v-if="jobResult" type="success" :closable="false" class="result-alert">
        已创建后台任务，run_id={{ jobResult.run_id }}，请到任务中心查看。
      </el-alert>

      <template v-if="parsePreview">
        <div class="section-divider">
          <span class="section-label">解析预览</span>
        </div>
        <el-input :model-value="previewText" type="textarea" :rows="12" readonly class="mono" />
      </template>
    </section>

    <section class="page-panel">
      <div class="panel-head">
        <h4 class="panel-title">手动爬虫</h4>
        <p class="panel-subtitle">从湖北省农业农村厅网站抓取候选政策，后台执行并实时更新进度。</p>
      </div>

      <el-form label-width="120px" class="crawl-form">
        <el-form-item label="数据源">
          <el-select v-model="crawlOptions.sourceIds" multiple filterable collapse-tags placeholder="默认抓取全部来源" style="width: 100%">
            <el-option v-for="source in sourceOptions" :key="source.id" :label="source.name" :value="source.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="文件类型">
          <el-checkbox-group v-model="crawlOptions.fileTypes">
            <el-checkbox value="gfxwj">规范性文件</el-checkbox>
            <el-checkbox value="qtzd">其他主动公开文件</el-checkbox>
            <el-checkbox value="zcjd">政策解读</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="效力状态">
          <el-select v-model="crawlOptions.validityStatuses" multiple collapse-tags placeholder="默认不过滤" style="width: 100%">
            <el-option v-for="item in validityOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="每源抓取数">
          <el-input-number v-model="crawlOptions.maxPagesPerSource" :min="1" :max="50" />
          <span class="field-tip">当前表示每个来源最多抓取多少个候选详情页。</span>
        </el-form-item>
        <el-form-item label="最大文件数">
          <el-input-number v-model="crawlOptions.maxCandidates" :min="1" :max="100" />
        </el-form-item>
      </el-form>

      <div class="actions">
        <el-button type="primary" :loading="crawlLoading" @click="doCrawl">开始抓取</el-button>
      </div>

      <el-alert v-if="crawlResult" type="info" :closable="false" class="result-alert">
        run_id={{ crawlResult.run_id }}，状态 {{ crawlRunStatus }}，{{ crawlProgressMessage }}
      </el-alert>

      <el-table v-if="crawlCandidates.length" :data="crawlCandidates" class="mt" size="small">
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
        <el-table-column prop="file_type" label="文件类型" width="120" />
        <el-table-column prop="validity_status" label="效力状态" width="100" />
        <el-table-column prop="publish_date" label="发布日期" width="120" />
      </el-table>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { api } from '../../api/client'

const router = useRouter()
const validityOptions = ['有效', '失效', '废止', '已修改', '待生效']

const sourceOptions = ref([])
const fileRaw = ref(null)
const fileName = ref('')
const parsing = ref(false)
const parsePreview = ref(null)
const jobLoading = ref(false)
const jobResult = ref(null)
const crawlLoading = ref(false)
const crawlResult = ref(null)
const crawlRunDetail = ref(null)
const crawlOptions = ref({
  sourceIds: [],
  fileTypes: [],
  validityStatuses: [],
  maxPagesPerSource: 5,
  maxCandidates: 8,
})
let crawlPollTimer = null

const parsedText = computed(() => {
  const parsed = parsePreview.value
  if (!parsed) return ''
  if (typeof parsed.text === 'string') return parsed.text
  if (typeof parsed.content === 'string') return parsed.content
  return JSON.stringify(parsed)
})

const previewText = computed(() => JSON.stringify(parsePreview.value, null, 2))
const crawlCandidates = computed(() => crawlRunDetail.value?.run?.result_json?.candidates || crawlResult.value?.candidates || [])
const crawlRunStatus = computed(() => crawlRunDetail.value?.run?.status || crawlResult.value?.status || 'pending')
const crawlProgressMessage = computed(() => {
  return (
    crawlRunDetail.value?.run?.progress?.message ||
    crawlRunDetail.value?.run?.summary_message ||
    crawlResult.value?.message ||
    '等待后台执行'
  )
})

async function loadSources() {
  try {
    const res = await api.withAdmin(() => api.get('/policies/crawl/sources'))
    sourceOptions.value = res.sources || []
  } catch {
    sourceOptions.value = []
  }
}

function onFileChange(uploadFile) {
  const file = uploadFile.raw
  fileRaw.value = file || null
  fileName.value = file?.name || ''
  parsePreview.value = null
  jobResult.value = null
}

function onFileRemove() {
  fileRaw.value = null
  fileName.value = ''
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const value = String(reader.result || '')
      const index = value.indexOf(',')
      resolve(index >= 0 ? value.slice(index + 1) : value)
    }
    reader.onerror = () => reject(new Error('read failed'))
    reader.readAsDataURL(file)
  })
}

async function parseSync() {
  if (!fileRaw.value) return
  if (fileRaw.value.size > 2 * 1024 * 1024) {
    ElMessage.warning('文件超过 2MB，请使用后台解析任务')
    return
  }
  parsing.value = true
  try {
    const fd = new FormData()
    fd.append('file', fileRaw.value)
    const res = await api.withAdmin(() =>
      api.rawFetch('/policies/parse-file', { method: 'POST', body: fd, headers: {} }).then(async (response) => {
        const contentType = response.headers.get('content-type') || ''
        const data = contentType.includes('application/json') ? await response.json() : await response.text()
        if (!response.ok) throw new Error(data?.detail || '解析失败')
        return data
      })
    )
    parsePreview.value = res
    ElMessage.success('解析完成')
  } catch (error) {
    ElMessage.error(error?.message || '解析失败')
  } finally {
    parsing.value = false
  }
}

async function parseJob() {
  if (!fileRaw.value) return
  jobLoading.value = true
  try {
    const b64 = await fileToBase64(fileRaw.value)
    const res = await api.withAdmin(() =>
      api.post('/policies/parse-file/jobs', {
        filename: fileName.value || 'uploaded',
        data_b64: b64,
      })
    )
    jobResult.value = res
    ElMessage.success('已提交后台任务')
  } catch (error) {
    ElMessage.error(error?.message || '提交失败')
  } finally {
    jobLoading.value = false
  }
}

async function sendToReview() {
  const text = parsedText.value
  if (!text?.trim()) {
    ElMessage.warning('请先完成解析预览')
    return
  }
  try {
    await api.withAdmin(() =>
      api.post('/policies/review/tasks', {
        source_type: 'file',
        title: fileName.value || '文件导入',
        source: 'import',
        raw_text: text.slice(0, 500000),
      })
    )
    ElMessage.success('已创建审核任务')
    router.push('/admin/policies/review')
  } catch (error) {
    ElMessage.error(error?.message || '送审失败')
  }
}

async function doCrawl() {
  crawlLoading.value = true
  crawlResult.value = null
  crawlRunDetail.value = null
  try {
    const res = await api.withAdmin(() =>
      api.post('/policies/crawl', {
        source_ids: crawlOptions.value.sourceIds,
        file_types: crawlOptions.value.fileTypes,
        validity_statuses: crawlOptions.value.validityStatuses,
        max_pages_per_source: crawlOptions.value.maxPagesPerSource,
        max_candidates: crawlOptions.value.maxCandidates,
      })
    )
    crawlResult.value = res
    if (res?.run_id) {
      startCrawlPolling(res.run_id)
    }
    ElMessage.success(res?.message || '爬虫任务已入队')
  } catch (error) {
    ElMessage.error(error?.message || '抓取失败')
  } finally {
    crawlLoading.value = false
  }
}

function stopCrawlPolling() {
  if (crawlPollTimer) {
    clearInterval(crawlPollTimer)
    crawlPollTimer = null
  }
}

async function fetchRunDetail(runId) {
  const detail = await api.withAdmin(() => api.get(`/admin-ops/runs/${runId}`))
  crawlRunDetail.value = detail
  const status = detail?.run?.status
  if (status && !['pending', 'running'].includes(status)) {
    stopCrawlPolling()
  }
}

function startCrawlPolling(runId) {
  stopCrawlPolling()
  fetchRunDetail(runId).catch(() => {})
  crawlPollTimer = setInterval(() => {
    fetchRunDetail(runId).catch(() => {})
  }, 2000)
}

onMounted(loadSources)
onBeforeUnmount(stopCrawlPolling)
</script>

<style scoped>
.panel-head {
  margin-bottom: 1rem;
}

.crawl-form {
  max-width: 720px;
  margin-bottom: 8px;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
}

.result-alert {
  margin-top: 12px;
}

.section-divider {
  margin: 16px 0 10px;
}

.section-label {
  font-weight: 600;
  color: #173726;
  font-size: 0.95rem;
}

.mt {
  margin-top: 12px;
}

.mono :deep(textarea) {
  font-family: ui-monospace, monospace;
  font-size: 12px;
}

.field-tip {
  margin-left: 12px;
  color: var(--adm-muted);
  font-size: 13px;
}
</style>
