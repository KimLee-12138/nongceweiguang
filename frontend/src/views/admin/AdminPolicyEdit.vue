<template>
  <div class="page-shell">
    <div class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">编辑政策</h3>
        <p class="page-subtitle">政策 ID：{{ route.params.id }}，保存后立即写入正式政策库。</p>
      </div>
      <div class="page-actions">
        <el-button @click="router.push('/admin/policies')">返回列表</el-button>
        <el-button plain :loading="refreshingTree" @click="onRefreshTree">重生成条件树</el-button>
        <el-button type="danger" plain :loading="deleting" @click="onDelete">删除</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
      </div>
    </div>

    <el-card v-loading="loading" shadow="never">
      <el-form label-width="100px" class="max-form">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="政策标题" />
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="form.source" placeholder="来源" />
        </el-form-item>
        <el-form-item label="文件类型">
          <el-select v-model="form.file_type" clearable placeholder="请选择" style="width: 100%">
            <el-option v-for="item in fileTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="效力状态">
          <el-select v-model="form.validity_status" placeholder="请选择" style="width: 100%">
            <el-option v-for="item in validityOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="生效日期">
          <el-date-picker v-model="form.effective_date" type="date" value-format="YYYY-MM-DD" placeholder="可选" style="width: 100%" />
        </el-form-item>
        <el-form-item label="失效日期">
          <el-date-picker v-model="form.expiry_date" type="date" value-format="YYYY-MM-DD" placeholder="可选" style="width: 100%" />
        </el-form-item>
        <el-form-item label="版本">
          <el-input v-model="form.version" placeholder="可选" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="4" placeholder="摘要" />
        </el-form-item>
        <el-form-item label="原文引用">
          <el-input v-model="form.raw_text_ref" placeholder="链接或存储键" />
        </el-form-item>
        <el-form-item label="条件树 JSON">
          <el-input v-model="conditionTreeText" type="textarea" :rows="14" class="mono" placeholder="{}" />
        </el-form-item>
        <el-form-item v-if="conditionTreeMeta.compile_quality" label="编译质量">
          <el-tag :type="compileQualityType(conditionTreeMeta.compile_quality)" effect="light">
            {{ conditionTreeMeta.compile_quality }}
          </el-tag>
        </el-form-item>
        <el-form-item v-if="conditionTreeMeta.applicable_subjects?.length" label="适用主体">
          <div class="chip-wrap">
            <el-tag v-for="item in conditionTreeMeta.applicable_subjects" :key="item" effect="light">{{ item }}</el-tag>
          </div>
        </el-form-item>
        <el-form-item v-if="conditionTreeMeta.missing_information?.length" label="缺失信息">
          <ul class="meta-list">
            <li v-for="item in conditionTreeMeta.missing_information" :key="item">{{ item }}</li>
          </ul>
        </el-form-item>
        <el-form-item v-if="conditionTreeMeta.uncertain_points?.length" label="不确定项">
          <ul class="meta-list">
            <li v-for="item in conditionTreeMeta.uncertain_points" :key="item">{{ item }}</li>
          </ul>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../../api/client'

const fileTypeOptions = [
  { value: 'gfxwj', label: '规范性文件' },
  { value: 'qtzd', label: '其他主动公开文件' },
  { value: 'zcjd', label: '政策解读' },
]
const validityOptions = ['有效', '失效', '废止', '已修改', '待生效']

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const refreshingTree = ref(false)
const conditionTreeText = ref('{}')
const conditionTreeMeta = ref({})

const form = reactive({
  title: '',
  source: '',
  file_type: '',
  validity_status: '有效',
  effective_date: '',
  expiry_date: '',
  version: '',
  summary: '',
  raw_text_ref: '',
})

async function load() {
  const id = route.params.id
  if (!id) return
  loading.value = true
  try {
    const policy = await api.withAdmin(() => api.get(`/policies/${id}`))
    form.title = policy.title || ''
    form.source = policy.source || ''
    form.file_type = policy.file_type || ''
    form.validity_status = policy.validity_status || '有效'
    form.effective_date = policy.effective_date || ''
    form.expiry_date = policy.expiry_date || ''
    form.version = policy.version || ''
    form.summary = policy.summary || ''
    form.raw_text_ref = policy.raw_text_ref || ''
    conditionTreeText.value = JSON.stringify(policy.condition_tree || {}, null, 2)
    conditionTreeMeta.value = policy.condition_tree_meta || {}
  } catch (error) {
    ElMessage.error(error?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function compileQualityType(value) {
  if (value === 'generated') return 'success'
  if (value === 'partial') return 'warning'
  if (value === 'failed') return 'danger'
  return 'info'
}

function parseTree() {
  try {
    const obj = JSON.parse(conditionTreeText.value || '{}')
    if (typeof obj !== 'object' || obj === null) throw new Error('条件树必须是 JSON 对象')
    return obj
  } catch (error) {
    throw new Error(error?.message === '条件树必须是 JSON 对象' ? error.message : '条件树 JSON 格式无效')
  }
}

async function onSave() {
  if (!form.title?.trim()) {
    ElMessage.warning('请填写标题')
    return
  }
  let tree
  try {
    tree = parseTree()
  } catch (error) {
    ElMessage.error(error.message)
    return
  }
  saving.value = true
  try {
    const id = route.params.id
    await api.withAdmin(() =>
      api.put(`/policies/${id}`, {
        title: form.title.trim(),
        source: form.source || '',
        file_type: form.file_type || null,
        validity_status: form.validity_status || '有效',
        effective_date: form.effective_date || null,
        expiry_date: form.expiry_date || null,
        version: form.version || null,
        summary: form.summary || '',
        raw_text_ref: form.raw_text_ref || null,
        condition_tree: tree,
      })
    )
    ElMessage.success('已保存')
    await load()
  } catch (error) {
    ElMessage.error(error?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function onDelete() {
  try {
    await ElMessageBox.confirm('确定删除本条政策吗？关联匹配记录也会一起清理。', '确认删除', { type: 'warning' })
  } catch {
    return
  }
  deleting.value = true
  try {
    await api.withAdmin(() => api.del(`/policies/${route.params.id}`))
    ElMessage.success('已删除')
    router.push('/admin/policies')
  } catch (error) {
    ElMessage.error(error?.message || '删除失败')
  } finally {
    deleting.value = false
  }
}

async function onRefreshTree() {
  refreshingTree.value = true
  try {
    const res = await api.withAdmin(() => api.post(`/policies/${route.params.id}/refresh-condition-tree`, {}))
    ElMessage.success(res.reused ? '已复用进行中的条件树任务' : '条件树重生成任务已创建')
  } catch (error) {
    ElMessage.error(error?.message || '创建条件树重生成任务失败')
  } finally {
    refreshingTree.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.max-form {
  max-width: 720px;
}
.mono :deep(textarea) {
  font-family: ui-monospace, monospace;
  font-size: 12px;
}
.chip-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.meta-list {
  margin: 0;
  padding-left: 18px;
}
</style>
