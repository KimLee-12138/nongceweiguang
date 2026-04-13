<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import ChatWindow from '../components/ChatWindow.vue'
import { getUserMe } from '../services/authSession'

const router = useRouter()
const me = ref({ authenticated: false })

const canUse = computed(() => me.value?.authenticated)

async function loadMe() {
  me.value = await getUserMe()
}

onMounted(loadMe)
</script>

<template>
  <div class="chat-page-root">
    <div v-if="!canUse" class="hint">
      <el-alert type="warning" show-icon :closable="false" title="未登录" description="请先到「用户登录」完成登录后再使用聊天工作台。" />
      <el-button type="primary" @click="router.push('/login')">去登录</el-button>
    </div>
    <ChatWindow v-else />
  </div>
</template>

<style scoped>
.chat-page-root {
  height: 100vh;
  min-height: 100vh;
  overflow: hidden;
}
.hint {
  display: grid;
  gap: 12px;
  padding: 16px;
  max-width: 520px;
  margin: 2rem auto;
}
</style>
