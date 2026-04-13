<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { api } from '../api/client'
import { userLogoutAll } from '../services/authSession'

const sessions = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    sessions.value = await api.withUser(() => api.get('/user-auth/sessions'))
  } catch (e) {
    ElMessage.error(e?.message || '加载会话失败，请先登录')
  } finally {
    loading.value = false
  }
}

async function revoke(sessionId) {
  try {
    await api.withUser(() => api.post(`/user-auth/sessions/${sessionId}/revoke`))
    ElMessage.success('已撤销该会话')
    await load()
  } catch (e) {
    ElMessage.error(e?.message || '撤销失败')
  }
}

async function logoutAll() {
  await userLogoutAll().catch(() => null)
  ElMessage.success('已退出所有会话')
  await load()
}

onMounted(load)
</script>

<template>
  <div class="wrap">
    <div class="head">
      <h2>我的会话</h2>
      <div class="actions">
        <el-button @click="load" :loading="loading">刷新</el-button>
        <el-button type="danger" @click="logoutAll">退出所有会话</el-button>
      </div>
    </div>

    <el-table :data="sessions" v-loading="loading" style="width: 100%">
      <el-table-column prop="session_id" label="Session ID" min-width="260" />
      <el-table-column prop="created_at" label="创建时间" min-width="180" />
      <el-table-column prop="expires_at" label="过期时间" min-width="180" />
      <el-table-column prop="revoked_at" label="撤销时间" min-width="180" />
      <el-table-column prop="ip" label="IP" width="140" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" :disabled="!!row.revoked_at" @click="revoke(row.session_id)">踢下线</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.wrap {
  display: grid;
  gap: 12px;
}
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>

