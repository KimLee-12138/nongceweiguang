<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

import { api } from '../api/client'

const result = ref(null)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    result.value = await api.get('/insights/kpi-summary')
  } catch (e) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="wrap">
    <h2>政策洞察</h2>
    <el-button type="primary" @click="load" :loading="loading">加载最新统计</el-button>
    <pre class="box">{{ result }}</pre>
  </div>
</template>

<style scoped>
.box {
  margin-top: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  overflow: auto;
}
</style>

