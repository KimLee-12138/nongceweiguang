<template>
  <el-container class="terminal-layout" direction="horizontal">
    <aside v-if="!isCompactLayout" class="terminal-sidebar terminal-sidebar--left">
      <SidebarLeft
        :current-profile="currentProfile"
        :recent-conversations="recentConversations"
        :current-conversation-id="currentConversationId"
        @create-conversation="$emit('createConversation')"
        @manage-profiles="$emit('manageProfiles')"
        @switch-conversation="$emit('switchConversation', $event)"
        @delete-conversation="$emit('deleteConversation', $event)"
        @go-onboarding="$emit('goOnboarding')"
      />
    </aside>

    <el-main class="terminal-main">
      <div class="terminal-shell">
        <header class="terminal-header">
          <div class="terminal-header__left">
            <button
              v-if="isCompactLayout"
              type="button"
              class="terminal-icon-btn"
              aria-label="打开左侧面板"
              @click="$emit('update:leftPanelVisible', true)"
            >
              <el-icon><Fold /></el-icon>
            </button>

            <div class="terminal-identity">
              <div class="terminal-brand-row">
                <img class="terminal-brand-mark" :src="brandLogoMark" alt="农策微光" />
                <span class="terminal-kicker">NC-WORKSPACE</span>
              </div>
              <div class="terminal-title-row">
                <strong class="terminal-title">政策智能工作台</strong>
                <span class="terminal-mode-badge">{{ modeLabel }}</span>
              </div>
              <p class="terminal-subtitle">{{ currentModeTone }}</p>
            </div>
          </div>

          <div class="terminal-header__right">
            <div v-if="currentProfileName" class="terminal-context-chip">
              <span class="terminal-context-label">画像</span>
              <strong>{{ currentProfileName }}</strong>
            </div>

            <div v-if="citedPolicyTitle" class="terminal-context-chip terminal-context-chip--muted">
              <span class="terminal-context-label">引用</span>
              <strong>{{ citedPolicyTitle }}</strong>
            </div>
          </div>
        </header>

        <div class="terminal-stage">
          <slot />
        </div>
      </div>
    </el-main>

    <aside v-if="!isCompactLayout" class="terminal-sidebar terminal-sidebar--right terminal-sidebar--empty" aria-hidden="true" />
  </el-container>

  <el-drawer
    v-if="isCompactLayout"
    :model-value="leftPanelVisible"
    direction="ltr"
    size="min(308px, 92vw)"
    append-to-body
    class="terminal-drawer"
    :with-header="false"
    @update:model-value="$emit('update:leftPanelVisible', $event)"
  >
    <SidebarLeft
      :current-profile="currentProfile"
      :recent-conversations="recentConversations"
      :current-conversation-id="currentConversationId"
      @create-conversation="$emit('createConversation')"
      @manage-profiles="$emit('manageProfiles')"
      @switch-conversation="$emit('switchConversation', $event)"
      @delete-conversation="$emit('deleteConversation', $event)"
      @go-onboarding="$emit('goOnboarding')"
    />
  </el-drawer>
</template>

<script setup>
import { Fold } from '@element-plus/icons-vue'

import SidebarLeft from './SidebarLeft.vue'
import brandLogoMark from '../../assets/logo_icon.png'

defineProps({
  isCompactLayout: { type: Boolean, default: false },
  leftPanelVisible: { type: Boolean, default: false },
  currentProfile: { type: Object, default: null },
  recentConversations: { type: Array, default: () => [] },
  currentConversationId: { type: Number, default: null },
  currentProfileName: { type: String, default: '' },
  citedPolicyTitle: { type: String, default: '' },
  modeLabel: { type: String, default: '智能匹配 · 解读' },
  currentModeTone: {
    type: String,
    default: '挂载画像、选择政策，使用解读或匹配模式与政策对话。',
  },
})

defineEmits([
  'update:leftPanelVisible',
  'createConversation',
  'manageProfiles',
  'switchConversation',
  'deleteConversation',
  'goOnboarding',
])
</script>

<style scoped>
.terminal-layout {
  --nc-shadow-lg: 0 18px 50px rgba(41, 55, 43, 0.12), 0 8px 24px rgba(0, 0, 0, 0.06);
  --nc-text-secondary: #6d796c;
  --nc-text-muted: rgba(22, 24, 22, 0.46);
  --nc-text-strong: #111412;

  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(29, 91, 61, 0.04), transparent 24%),
    linear-gradient(180deg, #f6f7f4 0%, #f1f3ef 100%);
  color: #161816;
  font-family:
    system-ui,
    -apple-system,
    'Segoe UI',
    Roboto,
    'Noto Sans SC',
    sans-serif;
}

.terminal-sidebar {
  display: flex;
  min-width: 0;
  background: rgba(248, 249, 246, 0.92);
}

.terminal-sidebar--left {
  flex: 0 0 clamp(252px, 20vw, 288px);
  border-right: 1px solid rgba(18, 24, 22, 0.08);
  min-height: 0;
}

.terminal-sidebar--right {
  flex: 0 0 clamp(248px, 21vw, 288px);
  border-left: 1px solid rgba(18, 24, 22, 0.08);
}

.terminal-sidebar--empty {
  pointer-events: none;
}

.terminal-main {
  min-width: 0;
  padding: 0;
  background: transparent;
}

.terminal-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.terminal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.15rem 1.4rem 1rem;
  border-bottom: 1px solid rgba(18, 24, 22, 0.08);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(255, 255, 255, 0.78)),
    rgba(255, 255, 255, 0.74);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

.terminal-header__left,
.terminal-header__right {
  display: flex;
  align-items: flex-start;
  gap: 0.9rem;
}

.terminal-header__right {
  justify-content: flex-end;
  flex-wrap: wrap;
}

.terminal-identity {
  min-width: 0;
  max-width: 720px;
}

.terminal-brand-row {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
}

.terminal-brand-mark {
  display: block;
  height: 22px;
  width: auto;
  max-width: 100%;
  object-fit: contain;
}

.terminal-kicker {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: rgba(22, 24, 22, 0.5);
}

.terminal-title-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-top: 0.45rem;
}

.terminal-title {
  font-size: 1.06rem;
  font-weight: 650;
  color: #111412;
  letter-spacing: -0.03em;
}

.terminal-mode-badge {
  display: inline-flex;
  align-items: center;
  min-height: 1.75rem;
  padding: 0 0.65rem;
  border-radius: 999px;
  border: 1px solid rgba(18, 24, 22, 0.1);
  background: rgba(17, 20, 18, 0.04);
  font-size: 0.72rem;
  font-weight: 600;
  color: #4d534f;
}

.terminal-subtitle {
  margin: 0.45rem 0 0;
  font-size: 0.82rem;
  line-height: 1.6;
  color: rgba(22, 24, 22, 0.62);
}

.terminal-context-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 2.4rem;
  max-width: 280px;
  padding: 0 0.9rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(18, 24, 22, 0.08);
  color: #1d211f;
}

.terminal-context-chip--muted {
  opacity: 0.92;
}

.terminal-context-chip strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.terminal-context-label {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: rgba(22, 24, 22, 0.46);
  text-transform: uppercase;
}

.terminal-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.4rem;
  min-height: 2.4rem;
  padding: 0;
  border-radius: 999px;
  border: 1px solid rgba(18, 24, 22, 0.12);
  background: rgba(255, 255, 255, 0.82);
  color: #232826;
  cursor: pointer;
  transition:
    border-color 0.18s ease,
    background 0.18s ease;
}

.terminal-icon-btn:hover {
  border-color: rgba(18, 24, 22, 0.24);
  background: rgba(255, 255, 255, 0.96);
}

.terminal-stage {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

:deep(.terminal-drawer .el-drawer__body) {
  padding: 0;
}

@media (max-width: 1180px) {
  .terminal-sidebar {
    display: none;
  }
}

@media (max-width: 900px) {
  .terminal-header {
    flex-direction: column;
  }

  .terminal-header__right {
    width: 100%;
    justify-content: flex-start;
  }

  .terminal-context-chip {
    max-width: 100%;
  }
}
</style>
