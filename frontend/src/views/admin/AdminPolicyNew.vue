<template>
  <div class="page-shell">
    <div class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">新增政策</h3>
        <p class="page-subtitle">录入原文后可先编译生成条件树草稿，再写入正式政策库。</p>
      </div>
      <div class="page-actions">
        <el-button @click="$router.push('/admin/policies')">返回列表</el-button>
      </div>
    </div>

    <el-card shadow="never">
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
        <el-form-item label="原文">
          <el-input v-model="form.raw_text" type="textarea" :rows="8" placeholder="粘贴政策原文，用于生成摘要建议与条件树草稿" />
        </el-form-item>
        <el-form-item>
          <el-button plain :loading="checkingModel" @click="checkModel">检测 DeepSeek</el-button>
          <el-button :loading="compiling" @click="onCompile">编译条件树</el-button>
          <span v-if="compileMode" class="hint">模式：{{ compileMode }}</span>
        </el-form-item>
        <el-form-item v-if="modelReadiness.status" label="模型状态">
          <el-tag :type="modelReadiness.ok ? 'success' : 'danger'" effect="light">
            {{ modelReadiness.message || modelReadiness.status }}
          </el-tag>
        </el-form-item>
        <el-form-item v-if="compileMeta.compileQuality" label="编译质量">
          <el-tag :type="compileQualityType(compileMeta.compileQuality)" effect="light">
            {{ compileMeta.compileQuality }}
          </el-tag>
        </el-form-item>
        <el-form-item v-if="compileMeta.applicableSubjects.length" label="适用主体">
          <div class="chip-wrap">
            <el-tag v-for="item in compileMeta.applicableSubjects" :key="item" effect="light">{{ item }}</el-tag>
          </div>
        </el-form-item>
        <el-form-item v-if="compileMeta.missingInformation.length" label="缺失信息">
          <ul class="meta-list">
            <li v-for="item in compileMeta.missingInformation" :key="item">{{ item }}</li>
          </ul>
        </el-form-item>
        <el-form-item v-if="compileMeta.uncertainPoints.length" label="不确定项">
          <ul class="meta-list">
            <li v-for="item in compileMeta.uncertainPoints" :key="item">{{ item }}</li>
          </ul>
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="4" placeholder="可先编译自动带出摘要建议，再人工修改" />
        </el-form-item>
        <el-form-item label="原文引用">
          <el-input v-model="form.raw_text_ref" placeholder="可选：链接或对象存储键" />
        </el-form-item>
        <el-form-item label="条件树 JSON">
          <el-input v-model="conditionTreeText" type="textarea" :rows="12" class="mono" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="onSave">保存到政策库</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../../api/client'

const fileTypeOptions = [
  { value: 'gfxwj', label: '规范性文件' },
  { value: 'qtzd', label: '其他主动公开文件' },
  { value: 'zcjd', label: '政策解读' },
]
const validityOptions = ['有效', '失效', '废止', '已修改', '待生效']

const router = useRouter()
const compiling = ref(false)
const saving = ref(false)
const checkingModel = ref(false)
const compileMode = ref('')
const compileMeta = reactive({
  compileQuality: '',
  missingInformation: [],
  uncertainPoints: [],
  applicableSubjects: [],
})
const modelReadiness = reactive({
  ok: false,
  status: '',
  message: '',
})

const form = reactive({
  title: '',
  source: '',
  file_type: '',
  validity_status: '有效',
  effective_date: '',
  expiry_date: '',
  version: '',
  summary: '',
  raw_text: '',
  raw_text_ref: '',
})

const conditionTreeText = ref(JSON.stringify({ id: 'root', logic: 'and', must: true, children: [] }, null, 2))

function friendlyModelMessage(message, fallback) {
  const text = String(message || '').trim()
  if (!text) return fallback
  if (text.includes('请求超时') || text.includes('timed out')) {
    return 'DeepSeek 响应超时。已经在调用真实模型，但本次等待时间过长，请稍后重试，或检查当前网络。'
  }
  if (text.includes('网络连接失败') || text.includes('连接超时') || text.includes('proxy') || text.includes('ConnectError')) {
    return '无法连接到 DeepSeek。请检查当前网络、代理设置，或稍后再试。'
  }
  if (text.includes('DEEPSEEK_API_KEY')) {
    return '当前环境未正确配置 DeepSeek API Key，请先检查后端 .env 配置。'
  }
  return text || fallback
}

async function onCompile() {
  compiling.value = true
  compileMode.value = ''
  try {
    const res = await api.withAdmin(() =>
      api.post('/policies/compile-text', {
        raw_text: form.raw_text,
        title: form.title || null,
        source: form.source || null,
      })
    )
    conditionTreeText.value = JSON.stringify(res.condition_tree || {}, null, 2)
    if (res.summary && !form.summary) {
      form.summary = res.summary
    }
    compileMode.value = res.mode || 'stub'
    compileMeta.compileQuality = res.compile_quality || ''
    compileMeta.missingInformation = res.missing_information || []
    compileMeta.uncertainPoints = res.uncertain_points || []
    compileMeta.applicableSubjects = res.applicable_subjects || []
    ElMessage.success('编译完成')
  } catch (error) {
    compileMeta.compileQuality = 'failed'
    compileMeta.missingInformation = []
    compileMeta.uncertainPoints = []
    compileMeta.applicableSubjects = []
    ElMessage.error(friendlyModelMessage(error?.message, '条件树编译失败'))
  } finally {
    compiling.value = false
  }
}

async function checkModel() {
  checkingModel.value = true
  try {
    const res = await api.withAdmin(() => api.get('/policies/model-readiness?live=true'))
    modelReadiness.ok = !!res.ok
    modelReadiness.status = res.status || ''
    modelReadiness.message = res.message || ''
    ElMessage.success(res.message || 'DeepSeek 在线校验完成')
  } catch (error) {
    modelReadiness.ok = false
    modelReadiness.status = 'error'
    modelReadiness.message = friendlyModelMessage(error?.message, 'DeepSeek 在线校验失败')
    ElMessage.error(modelReadiness.message)
  } finally {
    checkingModel.value = false
  }
}

function parseTree() {
  const obj = JSON.parse(conditionTreeText.value || '{}')
  if (typeof obj !== 'object' || obj === null) throw new Error('条件树必须是 JSON 对象')
  return obj
}

async function onSave() {
  if (!form.title?.trim()) {
    ElMessage.warning('请填写标题')
    return
  }
  let tree
  try {
    tree = parseTree()
  } catch {
    ElMessage.error('条件树 JSON 无效')
    return
  }
  saving.value = true
  try {
    await api.withAdmin(() =>
      api.post('/policies', {
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
    ElMessage.success('已创建')
    router.push('/admin/policies')
  } catch (error) {
    ElMessage.error(error?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

function compileQualityType(value) {
  if (value === 'generated') return 'success'
  if (value === 'partial') return 'warning'
  if (value === 'failed') return 'danger'
  return 'info'
}
</script>

<style scoped>
.max-form {
  max-width: 720px;
}
.mono :deep(textarea) {
  font-family: ui-monospace, monospace;
  font-size: 12px;
}
.hint {
  margin-left: 12px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
.chip-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.meta-list {
  margin: 0;
  padding-left: 18px;
  color: var(--el-text-color-regular);
}
</style>
