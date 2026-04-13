<template>
  <div class="page-shell">
    <div class="page-head">
      <div class="page-title-group">
        <h3 class="page-title">管理员会话</h3>
        <p class="page-subtitle">查看与撤销管理员登录会话。（列表接口接入前为占位）</p>
      </div>
      <div class="page-actions">
        <el-button @click="tip">刷新</el-button>
        <el-button type="danger" @click="logoutAll">退出所有会话</el-button>
      </div>
    </div>
    <el-card shadow="never">
      <el-table :data="[]" empty-text="暂无会话数据，后端接口就绪后自动加载">
        <el-table-column prop="session_id" label="Session ID" min-width="260" />
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
        <el-table-column prop="expires_at" label="过期时间" min-width="180" />
        <el-table-column prop="revoked_at" label="撤销时间" min-width="180" />
        <el-table-column prop="ip" label="IP" width="140" />
        <el-table-column label="操作" width="160">
          <template #default>
            <el-button size="small" disabled>踢下线</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'

import { adminLogoutAll } from '../../services/authSession'

function tip() {
  ElMessage.info('功能开发中：会话列表将对接 /auth/sessions')
}

async function logoutAll() {
  await adminLogoutAll().catch(() => null)
  ElMessage.success('已请求退出所有会话')
}
</script>
