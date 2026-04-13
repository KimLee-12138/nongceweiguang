<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import ProfileOnboarding from '../components/ProfileOnboarding.vue'
import { api } from '../api/client'
import { safeInternalRedirectPath } from '../utils/safeRedirect'

const route = useRoute()
const router = useRouter()

function afterPath() {
  return safeInternalRedirectPath(route.query.redirect, '/chat')
}

async function onComplete(payload) {
  try {
    const profiles = await api.withUser(() => api.get('/profiles'))
    const currentProfile = Array.isArray(profiles) ? profiles[0] : null

    if (currentProfile?.id) {
      await api.withUser(() => api.put(`/profiles/${currentProfile.id}`, payload.profile))
      ElMessage.success(`画像已更新${payload.source === 'deepseek' ? '（已智能归一）' : ''}`)
    } else {
      const created = await api.withUser(() => api.post('/profiles', payload.profile))
      ElMessage.success(`画像已创建 #${created.id}${payload.source === 'deepseek' ? '（已智能归一）' : ''}`)
    }

    await router.replace(afterPath())
  } catch (error) {
    ElMessage.error(error?.message || '保存画像失败')
  }
}

function onSkipOrCancel() {
  router.replace(afterPath())
}
</script>

<template>
  <div class="profile-onboarding-page">
    <ProfileOnboarding @complete="onComplete" @skip="onSkipOrCancel" @cancel="onSkipOrCancel" />
  </div>
</template>

<style scoped>
.profile-onboarding-page {
  min-height: 100vh;
  width: 100%;
  margin: 0;
  padding: 0;
  overflow: auto;
}
</style>
