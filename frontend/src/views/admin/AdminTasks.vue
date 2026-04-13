<template>
  <div class="page-shell">
    <div class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">任务中心</h3>
        <p class="page-subtitle">
          后台作业来自文件解析、手动/自动爬虫等。可查看明细、对失败任务重试，或消费一条待处理队列（与后端
          <code>/admin-ops</code> 对齐）。
        </p>
      </div>
      <div class="page-actions">
        <el-button :loading="consuming" @click="consumeOnce">消费一条待处理</el-button>
        <el-button :loading="loading" @click="loadRuns">刷新</el-button>
      </div>
    </div>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="runs" style="width: 100%">
        <el-table-column prop="id" label="任务 ID" width="100" />
        <el-table-column prop="operation_type" label="类型" width="180" />
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="summary_message" label="摘要" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row.id)">详情</el-button>
            <el-button
              v-if="row.status === 'failed' || row.status === 'partial'"
              link
              type="warning"
              @click="retryRun(row.id)"
            >
              重试
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !runs.length" description="暂无后台作业" />
    </el-card>

    <el-drawer v-model="drawerVisible" title="任务详情" size="520px" destroy-on-close>
      <div v-loading="detailLoading">
        <template v-if="detail">
          <el-descriptions :column="1" border size="small" class="mb">
            <el-descriptions-item label="ID">{{ detail.run.id }}</el-descriptions-item>
            <el-descriptions-item label="类型">{{ detail.run.operation_type }}</el-descriptions-item>
            <el-descriptions-item label="状态">{{ detail.run.status }}</el-descriptions-item>
            <el-descriptions-item label="摘要">{{ detail.run.summary_message || '—' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ detail.run.created_at }}</el-descriptions-item>
          </el-descriptions>
          <p class="label">payload</p>
          <el-input :model-value="jsonStr(detail.run.payload_json)" type="textarea" :rows="6" readonly class="mono" />
          <p class="label">result</p>
          <el-input :model-value="jsonStr(detail.run.result_json)" type="textarea" :rows="6" readonly class="mono" />
          <p class="label">子项</p>
          <el-table :data="detail.items" size="small" border>
            <el-table-column prop="item_index" label="#" width="48" />
            <el-table-column prop="status" label="状态" width="90" />
            <el-table-column prop="error_message" label="错误" min-width="120" show-overflow-tooltip />
          </el-table>
        </template>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../../api/client'

const loading = ref(false)
const consuming = ref(false)
const runs = ref([])

const drawerVisible = ref(false)
const detailLoading = ref(false)
const detail = ref(null)

function statusType(s) {
  if (s === 'success') return 'success'
  if (s === 'failed') return 'danger'
  if (s === 'partial') return 'warning'
  if (s === 'running') return 'info'
  return ''
}

function jsonStr(obj) {
  try {
    return JSON.stringify(obj ?? {}, null, 2)
  } catch {
    return String(obj)
  }
}

async function loadRuns() {
  loading.value = true
  try {
    runs.value = await api.withAdmin(() => api.get('/admin-ops/runs'))
  } catch (e) {
    ElMessage.error(e?.message || '加载失败')
    runs.value = []
  } finally {
    loading.value = false
  }
}

async function consumeOnce() {
  consuming.value = true
  try {
    const res = await api.withAdmin(() => api.post('/admin-ops/consume-once', {}))
    if (res.ran) {
      ElMessage.success(`已处理 run #${res.run_id}，状态：${res.status}`)
    } else {
      ElMessage.info('当前没有待处理任务')
    }
    await loadRuns()
  } catch (e) {
    ElMessage.error(e?.message || '消费失败')
  } finally {
    consuming.value = false
  }
}

async function openDetail(id) {
  drawerVisible.value = true
  detail.value = null
  detailLoading.value = true
  try {
    detail.value = await api.withAdmin(() => api.get(`/admin-ops/runs/${id}`))
  } catch (e) {
    ElMessage.error(e?.message || '加载详情失败')
  } finally {
    detailLoading.value = false
  }
}

async function retryRun(id) {
  try {
    await api.withAdmin(() => api.post(`/admin-ops/runs/${id}/retry`, {}))
    ElMessage.success('已重置为待处理，可再次「消费一条」')
    await loadRuns()
  } catch (e) {
    ElMessage.error(e?.message || '重试失败')
  }
}

loadRuns()
</script>

<style scoped>
.mb {
  margin-bottom: 12px;
}
.label {
  font-weight: 600;
  margin: 12px 0 6px;
}
.mono :deep(textarea) {
  font-family: ui-monospace, monospace;
  font-size: 12px;
}
</style>
