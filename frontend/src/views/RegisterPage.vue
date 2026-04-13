<template>
  <div class="editorial-auth-page">
    <div class="auth-brand-panel">
      <div class="brand-header" @click="go('/')">
        <img class="brand-logo" :src="logoIcon" alt="AgriPolicy AI" />
        <span class="brand-name">AgriPolicy&nbsp;AI</span>
      </div>

      <div class="brand-copy">
        <h1 class="brand-title fade-up delay-1">全新视野。<br />建立你的专属画像。</h1>
        <p class="brand-desc fade-up delay-2">
          从主体信息到追踪规划。<br />
          告别碎片化与盲目的政策搜索。
        </p>
      </div>

      <div class="brand-footer fade-up delay-3">© 2026 Agricultural Policy Intelligence.</div>
    </div>

    <div class="auth-form-panel">
      <div class="form-wrapper">
        <div class="form-header fade-up delay-1">
          <p class="kicker">REGISTER</p>
          <h2>免费注册账号</h2>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" label-width="0" class="editorial-form fade-up delay-2" @submit.prevent="handleSubmit">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="设置用户名" size="large" clearable class="apple-input" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="设置密码（至少 6 位）" size="large" show-password clearable class="apple-input" />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="确认密码"
              size="large"
              show-password
              clearable
              class="apple-input"
              @keyup.enter="handleSubmit"
            />
          </el-form-item>

          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

          <el-form-item class="action-item">
            <button type="button" class="btn-primary-dark" :class="{ 'is-loading': loading }" @click="handleSubmit">
              <span v-if="!loading">注册并进入工作台</span>
              <span v-else class="loader"></span>
            </button>
          </el-form-item>
        </el-form>

        <div class="form-footer fade-up delay-3">
          <button type="button" class="text-link" @click="go('/login')">已有账号，去登录</button>
          <span class="divider"></span>
          <button type="button" class="text-link muted" @click="go('/')">返回首页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { getAuthErrorMessage, userRegister } from '../services/authSession'
import logoIcon from '../assets/logo_icon.png'
import { safeInternalRedirectPath } from '../utils/safeRedirect'

const router = useRouter()
const route = useRoute()
const formRef = ref(null)
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入至少 6 位密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_, value, callback) => {
        if (value !== form.password) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

function go(path) {
  router.push(path)
}

async function handleSubmit() {
  errorMsg.value = ''
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userRegister(form.username.trim(), form.password)
    ElMessage.success(`欢迎加入，${form.username.trim()}`)
    const redirect = safeInternalRedirectPath(route.query.redirect, '/chat')
    await router.replace(redirect)
  } catch (error) {
    errorMsg.value = getAuthErrorMessage(error, { fallback: '注册失败，请稍后再试' })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  setTimeout(() => {
    document.querySelectorAll('.fade-up').forEach((element) => element.classList.add('is-visible'))
  }, 50)
})
</script>

<style scoped>
.editorial-auth-page {
  display: flex;
  min-height: 100vh;
  background: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', 'Noto Sans SC', sans-serif;
}

.auth-brand-panel {
  flex: 1;
  max-width: 50vw;
  background-color: #050b08;
  color: #fbfbfd;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 60px;
  position: relative;
  overflow: hidden;
}

.auth-brand-panel::before {
  content: '';
  position: absolute;
  top: 20%;
  left: -20%;
  width: 80%;
  height: 80%;
  background: radial-gradient(circle, rgba(29, 91, 61, 0.15) 0%, rgba(0, 0, 0, 0) 70%);
  filter: blur(80px);
  pointer-events: none;
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  z-index: 10;
}

.brand-name {
  font-size: 16px;
  font-weight: 650;
  letter-spacing: -0.02em;
}

.brand-logo {
  width: 34px;
  height: 34px;
  object-fit: contain;
  display: block;
}

.brand-copy {
  z-index: 10;
  margin-top: -10vh;
}

.brand-title {
  font-size: clamp(3rem, 5vw, 4.5rem);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.03em;
  margin: 0 0 24px;
}

.brand-desc {
  font-size: 1.25rem;
  line-height: 1.6;
  color: #86868b;
  font-weight: 400;
  margin: 0;
}

.brand-footer {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
  z-index: 10;
}

.auth-form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.form-wrapper {
  width: 100%;
  max-width: 420px;
}

.form-header {
  margin-bottom: 48px;
}

.kicker {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.15em;
  color: #86868b;
  margin: 0 0 12px;
}

.form-header h2 {
  font-size: 32px;
  font-weight: 600;
  color: #111111;
  margin: 0;
  letter-spacing: -0.02em;
}

.editorial-form {
  margin-bottom: 32px;
}

:deep(.apple-input .el-input__wrapper) {
  background-color: #f5f5f7 !important;
  box-shadow: none !important;
  border-radius: 12px !important;
  padding: 0 16px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

:deep(.apple-input .el-input__wrapper.is-focus) {
  background-color: #ffffff !important;
  box-shadow: 0 0 0 2px #111111 !important;
}

:deep(.apple-input .el-input__inner) {
  height: 52px;
  font-size: 16px;
  color: #111111;
}

:deep(.apple-input .el-input__inner::placeholder) {
  color: #a1a1a6;
}

.error-msg {
  font-size: 13px;
  color: #ff3b30;
  margin: -12px 0 20px;
  font-weight: 500;
}

.action-item {
  margin-top: 32px;
}

.btn-primary-dark {
  width: 100%;
  height: 52px;
  border-radius: 999px;
  background: #111111;
  color: #ffffff;
  border: none;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), background 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-primary-dark:hover:not(.is-loading) {
  background: #333336;
  transform: scale(1.02);
}

.loader {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.form-footer {
  display: flex;
  align-items: center;
  gap: 16px;
}

.text-link {
  background: none;
  border: none;
  padding: 0;
  font-size: 14px;
  font-weight: 500;
  color: #111111;
  cursor: pointer;
  transition: opacity 0.2s;
}

.text-link.muted {
  color: #86868b;
}

.text-link:hover {
  opacity: 0.6;
}

.divider {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #e8e8ed;
}

.fade-up {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-up.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.delay-1 {
  transition-delay: 0.1s;
}

.delay-2 {
  transition-delay: 0.2s;
}

.delay-3 {
  transition-delay: 0.3s;
}

@media (max-width: 900px) {
  .editorial-auth-page {
    flex-direction: column;
  }

  .auth-brand-panel {
    max-width: 100%;
    flex: none;
    padding: 40px 24px;
    min-height: 40vh;
  }

  .brand-copy {
    margin-top: 40px;
  }

  .brand-title {
    font-size: 2.5rem;
  }

  .auth-form-panel {
    padding: 60px 24px;
    align-items: flex-start;
  }
}
</style>
