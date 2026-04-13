<template>
  <div class="page-shell">
    <div class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">全自动爬取</h3>
        <p class="page-subtitle">
          配置保存在 <code>system_config.auto_crawler</code>，立即执行会创建后台作业，并沿用审核入库链路。
        </p>
      </div>
      <div class="page-actions">
        <el-button type="primary" :loading="saving" @click="saveConfig">保存配置</el-button>
        <el-button :loading="runLoading" @click="runNow">立即执行</el-button>
        <el-button :loading="compassLoading" @click="triggerCompass">生成风向标周报</el-button>
      </div>
    </div>

    <el-card shadow="never">
      <el-form label-width="140px" class="form-max">
        <el-form-item label="启用自动爬取">
          <el-switch v-model="config.enabled" />
        </el-form-item>
        <el-form-item label="间隔（小时）">
          <el-input-number v-model="config.interval_hours" :min="1" :max="168" />
        </el-form-item>
        <el-form-item label="每源抓取数">
          <el-input-number v-model="config.max_pages_per_source" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="最大文件数">
          <el-input-number v-model="config.max_candidates" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="数据源 ID 列表">
          <el-select v-model="config.sources" multiple filterable allow-create default-first-option placeholder="选择或输入来源 id" style="width: 100%">
            <el-option v-for="source in sourceOptions" :key="source.id" :label="source.name" :value="source.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="文件类型">
          <el-checkbox-group v-model="config.file_types">
            <el-checkbox value="gfxwj">规范性文件</el-checkbox>
            <el-checkbox value="qtzd">其他主动公开文件</el-checkbox>
            <el-checkbox value="zcjd">政策解读</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="效力状态">
          <el-select v-model="config.validity_statuses" multiple collapse-tags placeholder="默认不过滤" style="width: 100%">
            <el-option v-for="item in validityOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-descriptions v-if="lastRun" :column="1" border class="mt" title="最近一次执行（本页会话）">
        <el-descriptions-item label="run_id">{{ lastRun.run_id }}</el-descriptions-item>
        <el-descriptions-item label="status">{{ lastRun.status }}</el-descriptions-item>
      </el-descriptions>

      <el-descriptions v-if="compassResult" :column="1" border class="mt" title="风向标">
        <el-descriptions-item label="report_id">{{ compassResult.report_id }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../../api/client'

const validityOptions = ['有效', '失效', '废止', '已修改', '待生效']
const saving = ref(false)
const runLoading = ref(false)
const compassLoading = ref(false)
const sourceOptions = ref([])
const lastRun = ref(null)
const compassResult = ref(null)

const config = reactive({
  enabled: false,
  sources: [],
  interval_hours: 24,
  max_pages_per_source: 5,
  max_candidates: 8,
  file_types: [],
  validity_statuses: [],
})

async function loadSources() {
  try {
    const res = await api.withAdmin(() => api.get('/policies/crawl/sources'))
    sourceOptions.value = res.sources || []
  } catch {
    sourceOptions.value = []
  }
}

async function loadConfig() {
  try {
    const value = await api.withAdmin(() => api.get('/policies/auto-crawler/config'))
    config.enabled = !!value.enabled
    config.sources = Array.isArray(value.sources) ? [...value.sources] : []
    config.interval_hours = value.interval_hours ?? 24
    config.max_pages_per_source = value.max_pages_per_source ?? 5
    config.max_candidates = value.max_candidates ?? 8
    config.file_types = Array.isArray(value.file_types) ? [...value.file_types] : []
    config.validity_statuses = Array.isArray(value.validity_statuses) ? [...value.validity_statuses] : []
  } catch (error) {
    ElMessage.error(error?.message || '加载配置失败')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    await api.withAdmin(() =>
      api.put('/policies/auto-crawler/config', {
        enabled: config.enabled,
        sources: config.sources,
        interval_hours: config.interval_hours,
        max_pages_per_source: config.max_pages_per_source,
        max_candidates: config.max_candidates,
        file_types: config.file_types,
        validity_statuses: config.validity_statuses,
      })
    )
    ElMessage.success('配置已保存')
  } catch (error) {
    ElMessage.error(error?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function runNow() {
  runLoading.value = true
  try {
    const res = await api.withAdmin(() => api.post('/policies/auto-crawler/run-now', {}))
    lastRun.value = res
    ElMessage.success('已创建自动爬取作业，请到任务中心查看')
  } catch (error) {
    ElMessage.error(error?.message || '执行失败')
  } finally {
    runLoading.value = false
  }
}

async function triggerCompass() {
  compassLoading.value = true
  try {
    const res = await api.withAdmin(() => api.post('/compass/generate', {}))
    compassResult.value = res
    ElMessage.success('已生成风向标周报')
  } catch (error) {
    ElMessage.error(error?.message || '触发失败')
  } finally {
    compassLoading.value = false
  }
}

onMounted(async () => {
  await loadSources()
  await loadConfig()
})
</script>

<style scoped>
.form-max {
  max-width: 720px;
}
.mt {
  margin-top: 20px;
}
</style>
