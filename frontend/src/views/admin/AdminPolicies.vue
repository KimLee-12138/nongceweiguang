<template>
  <div class="page-shell admin-policies">
    <section class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">政策库维护</h3>
        <p class="page-subtitle">集中查看已入库政策，并按文件类型、效力状态进行筛选和日常维护。</p>
      </div>
      <div class="page-actions">
        <el-button type="danger" plain :disabled="!selectedRows.length" :loading="batchDeleting" @click="onBatchDelete">
          批量删除
        </el-button>
        <el-button type="primary" @click="$router.push('/admin/policies/new')">新增政策</el-button>
        <el-button @click="$router.push('/admin/policies/import')">导入</el-button>
      </div>
    </section>

    <section class="page-panel surface-table">
      <div class="toolbar">
        <el-select v-model="fileTypeFilter" clearable placeholder="文件类型" style="width: 180px">
          <el-option v-for="item in fileTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="validityFilter" clearable placeholder="效力状态" style="width: 160px">
          <el-option v-for="item in validityOptions" :key="item" :label="item" :value="item" />
        </el-select>
        <el-button :loading="loading" @click="loadList">刷新</el-button>
      </div>

      <el-table v-loading="loading" :data="tableData" style="width: 100%" @selection-change="onSelectionChange">
        <el-table-column type="selection" width="48" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
        <el-table-column prop="source" label="来源" width="180" show-overflow-tooltip />
        <el-table-column label="文件类型" width="130">
          <template #default="{ row }">{{ fileTypeLabel(row.file_type) }}</template>
        </el-table-column>
        <el-table-column prop="validity_status" label="效力状态" width="100" />
        <el-table-column prop="effective_date" label="生效日期" width="120" />
        <el-table-column prop="expiry_date" label="失效日期" width="120" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="$router.push(`/admin/policies/${row.id}/edit`)">编辑</el-button>
            <el-button link type="primary" @click="refreshOneTree(row)">重生成条件树</el-button>
            <el-button link type="primary" @click="openDetail(row)">详情</el-button>
            <el-button link type="danger" @click="onDeleteOne(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !tableData.length" description="暂无政策，可先新增或从审核台入库" />
    </section>

    <el-drawer v-model="detailVisible" title="政策详情" size="520px" destroy-on-close>
      <template v-if="detailRow">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="ID">{{ detailRow.id }}</el-descriptions-item>
          <el-descriptions-item label="标题">{{ detailRow.title }}</el-descriptions-item>
          <el-descriptions-item label="来源">{{ detailRow.source || '—' }}</el-descriptions-item>
          <el-descriptions-item label="文件类型">{{ fileTypeLabel(detailRow.file_type) }}</el-descriptions-item>
          <el-descriptions-item label="效力状态">{{ detailRow.validity_status || '—' }}</el-descriptions-item>
          <el-descriptions-item label="生效日期">{{ detailRow.effective_date || '—' }}</el-descriptions-item>
          <el-descriptions-item label="失效日期">{{ detailRow.expiry_date || '—' }}</el-descriptions-item>
          <el-descriptions-item label="版本">{{ detailRow.version || '—' }}</el-descriptions-item>
          <el-descriptions-item label="摘要">{{ detailRow.summary || '—' }}</el-descriptions-item>
          <el-descriptions-item label="原文引用">{{ detailRow.raw_text_ref || '—' }}</el-descriptions-item>
          <el-descriptions-item label="编译质量">{{ detailRow.condition_tree_meta?.compile_quality || '—' }}</el-descriptions-item>
          <el-descriptions-item label="适用主体">
            {{ (detailRow.condition_tree_meta?.applicable_subjects || []).join('、') || '—' }}
          </el-descriptions-item>
        </el-descriptions>
        <p class="detail-label">条件树 JSON</p>
        <el-input v-model="detailTreeText" type="textarea" :rows="12" readonly class="mono" />
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../../api/client'

const fileTypeOptions = [
  { value: 'gfxwj', label: '规范性文件' },
  { value: 'qtzd', label: '其他主动公开文件' },
  { value: 'zcjd', label: '政策解读' },
]
const validityOptions = ['有效', '失效', '废止', '已修改', '待生效']

const loading = ref(false)
const allPolicies = ref([])
const selectedRows = ref([])
const detailVisible = ref(false)
const detailRow = ref(null)
const batchDeleting = ref(false)
const fileTypeFilter = ref('')
const validityFilter = ref('')

const tableData = computed(() => {
  return (allPolicies.value || []).filter((item) => {
    if (fileTypeFilter.value && item.file_type !== fileTypeFilter.value) return false
    if (validityFilter.value && item.validity_status !== validityFilter.value) return false
    return true
  })
})

const detailTreeText = computed(() => {
  if (!detailRow.value?.condition_tree) return '{}'
  try {
    return JSON.stringify(detailRow.value.condition_tree, null, 2)
  } catch {
    return String(detailRow.value.condition_tree)
  }
})

function fileTypeLabel(value) {
  return fileTypeOptions.find((item) => item.value === value)?.label || value || '—'
}

async function loadList() {
  loading.value = true
  try {
    const data = await api.withAdmin(() => api.get('/policies'))
    allPolicies.value = Array.isArray(data) ? data : []
  } catch (error) {
    ElMessage.error(error?.message || '加载失败')
    allPolicies.value = []
  } finally {
    loading.value = false
  }
}

function onSelectionChange(rows) {
  selectedRows.value = rows
}

function openDetail(row) {
  detailRow.value = row
  detailVisible.value = true
}

async function onDeleteOne(row) {
  try {
    await ElMessageBox.confirm(`确定删除政策“${row.title}”吗？关联匹配记录也会一并清理。`, '确认删除', {
      type: 'warning',
    })
  } catch {
    return
  }
  try {
    await api.withAdmin(() => api.del(`/policies/${row.id}`))
    ElMessage.success('已删除')
    await loadList()
  } catch (error) {
    ElMessage.error(error?.message || '删除失败')
  }
}

async function refreshOneTree(row) {
  try {
    const res = await api.withAdmin(() => api.post(`/policies/${row.id}/refresh-condition-tree`, {}))
    ElMessage.success(res.reused ? '已复用进行中的条件树任务' : '条件树重生成任务已创建')
  } catch (error) {
    ElMessage.error(error?.message || '创建条件树任务失败')
  }
}

async function onBatchDelete() {
  if (!selectedRows.value.length) return
  try {
    await ElMessageBox.confirm(`将删除 ${selectedRows.value.length} 条政策及其关联匹配记录，是否继续？`, '批量删除', {
      type: 'warning',
    })
  } catch {
    return
  }
  batchDeleting.value = true
  try {
    for (const row of selectedRows.value) {
      await api.withAdmin(() => api.del(`/policies/${row.id}`))
    }
    ElMessage.success('批量删除完成')
    selectedRows.value = []
    await loadList()
  } catch (error) {
    ElMessage.error(error?.message || '批量删除中断')
    await loadList()
  } finally {
    batchDeleting.value = false
  }
}

onMounted(loadList)
</script>

<style scoped>
.page-shell {
  gap: 1rem;
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 16px;
}
.detail-label {
  margin: 12px 0 8px;
  font-weight: 600;
}
.mono :deep(textarea) {
  font-family: ui-monospace, monospace;
  font-size: 12px;
}
</style>
