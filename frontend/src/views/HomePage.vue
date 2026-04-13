<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { adminLogoutAll, getAdminMe, getUserMe, userLogoutAll } from '../services/authSession'
import logoIcon from '../assets/logo_icon.png'

const router = useRouter()
const rootRef = ref(null)
const isScrolled = ref(false)
const userMe = ref({ authenticated: false })
const adminMe = ref({ authenticated: false })
let observer = null

const hasUser = computed(() => !!userMe.value?.authenticated)
const hasAdmin = computed(() => !!adminMe.value?.authenticated)

const chatEntryLabel = computed(() => (hasUser.value ? '进入智能工作台' : '开启专属匹配'))
const consoleEntryPath = computed(() => (hasAdmin.value ? '/admin' : '/admin/login'))

function go(path) {
  router.push(path)
}

async function syncAuthState({ force = false } = {}) {
  // force 预留；当前接口无缓存层，直接请求 /me
  void force
  try {
    userMe.value = await getUserMe()
  } catch {
    userMe.value = { authenticated: false }
  }
  try {
    adminMe.value = await getAdminMe()
  } catch {
    adminMe.value = { authenticated: false }
  }
}

async function logoutUser() {
  await userLogoutAll().catch(() => null)
  await syncAuthState({ force: true })
  go('/')
}

async function logoutAdmin() {
  await adminLogoutAll().catch(() => null)
  await syncAuthState({ force: true })
  go('/')
}

function initReveal() {
  const root = rootRef.value
  if (!root) return
  const elements = root.querySelectorAll('.cinematic-reveal')

  observer?.disconnect?.()
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed')
          observer.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.1, rootMargin: '0px 0px -10% 0px' }
  )

  elements.forEach((el) => {
    el.classList.remove('is-revealed')
    observer.observe(el)
  })
}

function handleScroll() {
  isScrolled.value = window.scrollY > 50
}

async function handleWindowFocus() {
  await syncAuthState({ force: true })
}

onMounted(async () => {
  await syncAuthState()
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('focus', handleWindowFocus)

  requestAnimationFrame(() => {
    rootRef.value?.classList.add('is-mounted')
    initReveal()
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('focus', handleWindowFocus)
  observer?.disconnect?.()
})
</script>

<template>
  <div ref="rootRef" class="premium-home">
    <nav class="nav-bar" :class="{ 'nav-scrolled': isScrolled }">
      <div class="nav-container">
        <div class="nav-brand" @click="go('/')">
          <img class="brand-logo" :src="logoIcon" alt="AgriPolicy AI" />
          <span class="brand-titletext">AgriPolicy&nbsp;AI</span>
        </div>

        <div class="nav-menu">
          <a class="nav-link" @click="go('/insights')">政策洞察</a>
          <a class="nav-link" @click="go('/policy-compass')">风向大屏</a>
          <a class="nav-link" @click="go(consoleEntryPath)">管理中枢</a>

          <div class="nav-divider"></div>

          <template v-if="!hasUser">
            <a class="nav-link" @click="go('/login')">登录</a>
            <a class="nav-link" @click="go('/register')">注册</a>
          </template>
          <template v-else>
            <a class="nav-link" @click="logoutUser">退出用户</a>
          </template>

          <template v-if="hasAdmin">
            <a class="nav-link" @click="logoutAdmin">退出管理员</a>
          </template>
          <template v-else>
            <a class="nav-link subtle" @click="go('/admin/login')">管理员登录</a>
          </template>
        </div>
      </div>
    </nav>

    <main>
      <section class="section-hero">
        <div class="hero-bg-glow"></div>
        <div class="hero-content cinematic-reveal delay-1">
          <h1 class="hero-title">
            政策，<br />
            不该像天书。
          </h1>
          <p class="hero-subtitle cinematic-reveal delay-2">
            构建专属经营主体画像，将冗长繁杂的农业公文，<br />
            化作清晰可执行的下一步行动。
          </p>
          <div class="hero-actions cinematic-reveal delay-3">
            <button class="btn-primary-dark" @click="go('/chat')">{{ chatEntryLabel }}</button>
            <button class="btn-outline-dark" @click="go('/policy-compass')">展开风向大屏</button>
          </div>
        </div>
      </section>

      <section class="section-manifesto">
        <div class="manifesto-container cinematic-reveal">
          <h2 class="manifesto-text">
            不要去海里捞针。<br />
            <span>让真正适合你的政策，主动来找你。</span>
          </h2>
        </div>
      </section>

      <section class="section-feature feature-left">
        <div class="feature-container">
          <div class="feature-text cinematic-reveal">
            <span class="feature-eyebrow">精准定锚</span>
            <h2 class="feature-title">你的农场，<br />你的专属引擎。</h2>
            <p class="feature-desc">
              一次性挂载经营面积、主体类型与认证条件。系统以此为锚点，自动过滤无关噪音，直接呈现与你有关的申报机会与门槛缺口。
            </p>
          </div>
          <div class="feature-visual cinematic-reveal delay-2">
            <div class="visual-artbox artbox-1">
              <div class="art-overlay"></div>
              <div class="art-badge">画像 · 条件 · 证据</div>
            </div>
          </div>
        </div>
      </section>

      <section class="section-feature feature-right bg-alt">
        <div class="feature-container">
          <div class="feature-visual cinematic-reveal">
            <div class="visual-artbox artbox-2">
              <div class="abstract-card">
                <div class="line line-short"></div>
                <div class="line line-long"></div>
                <div class="line line-medium"></div>
                <div class="highlight-box">适用对象：家庭农场 / 合作社</div>
              </div>
            </div>
          </div>
          <div class="feature-text cinematic-reveal delay-2">
            <span class="feature-eyebrow">化繁为简</span>
            <h2 class="feature-title">复杂公文，<br />一秒说人话。</h2>
            <p class="feature-desc">
              用结构化规则树把政策拆解成可计算条件，再用对话把结论讲清楚：你是否满足、缺什么、怎么补、有哪些风险点。
            </p>
          </div>
        </div>
      </section>

      <section class="section-feature feature-left">
        <div class="feature-container">
          <div class="feature-text cinematic-reveal">
            <span class="feature-eyebrow">谋定后动</span>
            <h2 class="feature-title">知道怎么做，<br />比知道能报什么更重要。</h2>
            <p class="feature-desc">不止是“能不能报”。系统会把门槛缺口转成清晰行动清单，按优先级给出补齐路径与注意事项。</p>
          </div>
          <div class="feature-visual cinematic-reveal delay-2">
            <div class="visual-artbox artbox-3">
              <div class="action-steps">
                <div class="step-item"><span class="step-dot"></span> 补齐必要认证材料</div>
                <div class="step-item"><span class="step-dot"></span> 准备关键佐证文件</div>
                <div class="step-item active"><span class="step-dot"></span> 发起申报/备案流程</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="section-end-cta">
        <div class="cta-container cinematic-reveal">
          <h2 class="cta-title">一切就绪。<br />开始你的专属匹配。</h2>
          <div class="cta-actions">
            <button class="btn-primary-dark large" @click="go('/chat')">进入智能工作台</button>
            <button v-if="!hasUser" class="btn-outline-dark large" @click="go('/register')">免费创建账号</button>
            <button class="btn-ghost-dark large" @click="go('/admin')">进入管理中枢</button>
          </div>
        </div>
      </section>
    </main>

    <footer class="premium-footer">
      <div class="footer-container">
        <div class="footer-left">
          <p>© 2026 农策微光 (Agricultural Policy Intelligence). All rights reserved.</p>
        </div>
        <div class="footer-right">
          <span class="footer-link" @click="go('/insights')">政策洞察</span>
          <span class="footer-link" @click="go('/policy-compass')">风向大屏</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.premium-home {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', 'PingFang SC', 'Noto Sans SC',
    sans-serif;
  background-color: #ffffff;
  color: #111111;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}

.cinematic-reveal {
  opacity: 0;
  transform: translateY(40px);
  transition: opacity 1.2s cubic-bezier(0.16, 1, 0.3, 1), transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: opacity, transform;
}
.cinematic-reveal.is-revealed,
.is-mounted .cinematic-reveal.is-revealed {
  opacity: 1;
  transform: translateY(0);
}
.delay-1 {
  transition-delay: 0.1s;
}
.delay-2 {
  transition-delay: 0.25s;
}
.delay-3 {
  transition-delay: 0.4s;
}

.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  z-index: 100;
  transition: background-color 0.4s ease, backdrop-filter 0.4s ease;
}
.nav-scrolled {
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}
.brand-logo {
  height: 30px;
  width: auto;
  display: block;
  border-radius: 10px;
  background: transparent;
  opacity: 0.95;
  transition: opacity 0.3s ease;
}
.nav-scrolled .brand-logo {
  opacity: 0.95;
}
.brand-titletext {
  color: rgba(255, 255, 255, 0.92);
  font-size: 14px;
  font-weight: 650;
  letter-spacing: -0.02em;
  transition: color 0.3s ease;
  user-select: none;
}
.nav-scrolled .brand-titletext {
  color: rgba(17, 17, 17, 0.88);
}
.nav-menu {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}
.nav-link {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.3s;
}
.nav-scrolled .nav-link {
  color: rgba(0, 0, 0, 0.6);
}
.nav-link:hover {
  color: #fff;
}
.nav-scrolled .nav-link:hover {
  color: #000;
}
.nav-link.subtle {
  opacity: 0.9;
}
.nav-divider {
  width: 1px;
  height: 12px;
  background: rgba(255, 255, 255, 0.2);
}
.nav-scrolled .nav-divider {
  background: rgba(0, 0, 0, 0.1);
}

.section-hero {
  position: relative;
  height: 100vh;
  min-height: 700px;
  background-color: #050b08;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  overflow: hidden;
  padding: 0 24px;
}
.hero-bg-glow {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60vw;
  height: 60vw;
  background: radial-gradient(circle, rgba(29, 91, 61, 0.2) 0%, rgba(0, 0, 0, 0) 70%);
  filter: blur(60px);
  pointer-events: none;
}
.hero-content {
  position: relative;
  z-index: 10;
  max-width: 900px;
}
.hero-title {
  font-size: clamp(3.5rem, 8vw, 7rem);
  font-weight: 700;
  line-height: 1.05;
  letter-spacing: -0.04em;
  color: #fbfbfd;
  margin: 0 0 32px;
}
.hero-subtitle {
  font-size: clamp(1.2rem, 2vw, 1.6rem);
  line-height: 1.6;
  color: #86868b;
  font-weight: 400;
  margin: 0 auto 48px;
  max-width: 720px;
  letter-spacing: 0.01em;
}
.hero-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

button {
  font-family: inherit;
  cursor: pointer;
  border: none;
  background: none;
}
.btn-primary-dark {
  background: #f5f5f7;
  color: #111;
  padding: 0 28px;
  height: 52px;
  border-radius: 999px;
  font-size: 16px;
  font-weight: 600;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), background 0.3s;
}
.btn-primary-dark:hover {
  transform: scale(1.03);
  background: #ffffff;
}
.btn-outline-dark {
  background: transparent;
  color: #f5f5f7;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0 28px;
  height: 52px;
  border-radius: 999px;
  font-size: 16px;
  font-weight: 500;
  transition: border-color 0.3s, background 0.3s;
}
.btn-outline-dark:hover {
  border-color: #fff;
  background: rgba(255, 255, 255, 0.05);
}
.btn-ghost-dark {
  background: rgba(255, 255, 255, 0.08);
  color: #f5f5f7;
  padding: 0 28px;
  height: 52px;
  border-radius: 999px;
  font-size: 16px;
  font-weight: 500;
  transition: background 0.3s;
}
.btn-ghost-dark:hover {
  background: rgba(255, 255, 255, 0.12);
}
.btn-primary-dark.large,
.btn-outline-dark.large,
.btn-ghost-dark.large {
  height: 56px;
  padding: 0 36px;
  font-size: 18px;
}

.section-manifesto {
  padding: 160px 24px;
  background-color: #ffffff;
  text-align: center;
}
.manifesto-container {
  max-width: 1000px;
  margin: 0 auto;
}
.manifesto-text {
  font-size: clamp(2.5rem, 5vw, 4.5rem);
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.03em;
  color: #111;
  margin: 0;
}
.manifesto-text span {
  color: #86868b;
}

.section-feature {
  padding: 140px 24px;
  background-color: #ffffff;
}
.section-feature.bg-alt {
  background-color: #fbfbfd;
}
.feature-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 10vw;
}
.feature-right .feature-container {
  flex-direction: row-reverse;
}
.feature-text {
  flex: 1;
  max-width: 520px;
}
.feature-eyebrow {
  display: block;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: #728a7c;
  margin-bottom: 16px;
}
.feature-title {
  font-size: clamp(2.5rem, 4vw, 3.5rem);
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.03em;
  color: #111;
  margin: 0 0 24px;
}
.feature-desc {
  font-size: 1.25rem;
  line-height: 1.6;
  color: #86868b;
  font-weight: 400;
  margin: 0;
}
.feature-visual {
  flex: 1.2;
  display: flex;
  justify-content: center;
}
.visual-artbox {
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: 32px;
  background: #f5f5f7;
  overflow: hidden;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.artbox-1 {
  background: radial-gradient(circle at 30% 20%, rgba(29, 91, 61, 0.18), rgba(245, 245, 247, 1) 55%);
}
.art-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0) 30%, rgba(0, 0, 0, 0.05) 100%);
}
.art-badge {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 999px;
  padding: 10px 14px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.75);
}
.abstract-card {
  width: 60%;
  background: #fff;
  border-radius: 16px;
  padding: 40px 32px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.04);
}
.line {
  height: 8px;
  background: #e8e8ed;
  border-radius: 4px;
  margin-bottom: 16px;
}
.line-short {
  width: 40%;
}
.line-long {
  width: 100%;
}
.line-medium {
  width: 70%;
  margin-bottom: 32px;
}
.highlight-box {
  background: rgba(29, 91, 61, 0.08);
  color: #1d5b3d;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}
.action-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 70%;
}
.step-item {
  background: #fff;
  padding: 20px 24px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
  font-size: 16px;
  color: #86868b;
  display: flex;
  align-items: center;
  gap: 16px;
  font-weight: 500;
  transition: all 0.3s;
}
.step-item.active {
  color: #111;
  transform: scale(1.05);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.06);
}
.step-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #e8e8ed;
}
.step-item.active .step-dot {
  background: #1d5b3d;
  box-shadow: 0 0 0 4px rgba(29, 91, 61, 0.15);
}

.section-end-cta {
  background-color: #050b08;
  padding: 160px 24px;
  text-align: center;
}
.cta-container {
  max-width: 900px;
  margin: 0 auto;
}
.cta-title {
  font-size: clamp(3rem, 6vw, 4.5rem);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.03em;
  color: #fbfbfd;
  margin: 0 0 48px;
}
.cta-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.premium-footer {
  background-color: #050b08;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 32px 24px;
}
.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}
.footer-left p {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}
.footer-right {
  display: flex;
  gap: 24px;
}
.footer-link {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  user-select: none;
  transition: color 0.2s;
}
.footer-link:hover {
  color: #fff;
}

@media (max-width: 900px) {
  .feature-container,
  .feature-right .feature-container {
    flex-direction: column;
    gap: 40px;
  }
  .feature-text {
    max-width: 100%;
    text-align: center;
  }
  .feature-visual {
    width: 100%;
  }
  .nav-menu .nav-link:not(:last-child) {
    display: none;
  }
  .nav-divider {
    display: none;
  }
}

@media (max-width: 600px) {
  .section-hero {
    min-height: 90svh;
  }
  .hero-actions {
    flex-direction: column;
    width: 100%;
  }
  .btn-primary-dark,
  .btn-outline-dark {
    width: 100%;
  }
  .cta-actions {
    flex-direction: column;
  }
  .footer-container {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
