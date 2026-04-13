<script setup>
import { computed } from 'vue'
import { Delete } from '@element-plus/icons-vue'

import { profileDisplayTags as defaultProfileTags } from '../../utils/profileDisplayTags'
import brandLogoMark from '../../assets/logo_icon.png'

const props = defineProps({
  currentProfile: { type: Object, default: null },
  recentConversations: { type: Array, default: () => [] },
  currentConversationId: { type: Number, default: null },
  profileDisplayTags: { type: Function, default: null },
})

const emit = defineEmits([
  'createConversation',
  'manageProfiles',
  'switchConversation',
  'deleteConversation',
  'goOnboarding',
])

const tagsFn = computed(() => props.profileDisplayTags || defaultProfileTags)

function formatConversationTime(item) {
  const raw = item?.updated_at || item?.last_message_at || item?.created_at
  if (!raw) return ''
  const value = new Date(raw)
  if (Number.isNaN(value.getTime())) return ''
  return value.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <div class="sidebar sidebar--left">
    <div class="sidebar-shell">
      <header class="sidebar-header">
        <div>
          <div class="sidebar-brand-row">
            <img class="sidebar-brand-mark" :src="brandLogoMark" alt="农策微光" />
            <div class="sidebar-kicker">NC-WORKSPACE</div>
          </div>
          <h2 class="sidebar-brand">对话工作台</h2>
        </div>

        <div class="sidebar-header__actions">
          <button type="button" class="terminal-btn terminal-btn--primary" @click="emit('createConversation')">新建会话</button>
        </div>
      </header>

      <div class="sidebar-scroll">
        <section class="sidebar-section">
          <div class="sidebar-section__head">
            <span class="sidebar-section__label">最近会话</span>
            <button type="button" class="terminal-text-btn" @click="emit('createConversation')">新建</button>
          </div>

          <ul class="conversation-list">
            <li
              v-for="item in recentConversations"
              :key="item.id"
              class="conversation-item"
              :class="{ 'conversation-item--active': currentConversationId === item.id }"
              @click="emit('switchConversation', item)"
            >
              <div class="conversation-item__row">
                <div class="conversation-item__main">
                  <div class="conversation-item__title">{{ item.title || '未命名会话' }}</div>
                  <div v-if="formatConversationTime(item)" class="conversation-item__meta">
                    {{ formatConversationTime(item) }}
                  </div>
                </div>
                <button
                  type="button"
                  class="conversation-item__delete"
                  aria-label="删除会话"
                  @click.stop="emit('deleteConversation', item)"
                >
                  <el-icon><Delete /></el-icon>
                </button>
              </div>
            </li>
          </ul>

          <p v-if="recentConversations.length === 0" class="sidebar-empty">还没有历史会话，点击上方按钮开始新的对话。</p>
        </section>

        <section class="sidebar-section">
          <div class="sidebar-section__head">
            <span class="sidebar-section__label">画像管理</span>
            <button v-if="currentProfile" type="button" class="terminal-text-btn" @click="emit('manageProfiles')">微调</button>
          </div>

          <div v-if="currentProfile" class="profile-panel">
            <div class="profile-panel__title">{{ currentProfile.name }}</div>
            <p class="profile-panel__desc">问卷创建完成后，你可以在这里继续微调唯一画像，聊天、匹配和推荐都会基于它运行。</p>
            <div class="profile-panel__tags">
              <span v-for="(tag, index) in tagsFn(currentProfile)" :key="index" class="profile-tag">
                {{ tag }}
              </span>
            </div>
            <div class="profile-panel__actions">
              <button type="button" class="terminal-btn terminal-btn--ghost terminal-btn--block" @click="emit('manageProfiles')">
                管理画像
              </button>
              <button type="button" class="terminal-btn terminal-btn--soft terminal-btn--block" @click="emit('goOnboarding')">
                重新问卷创建
              </button>
            </div>
          </div>

          <div v-else class="sidebar-empty-box">
            <p class="sidebar-empty-box__title">还没有你的专属画像</p>
            <p class="sidebar-empty-box__desc">先完成一次问卷式创建，系统才能基于你的经营信息持续做政策解读、匹配和推荐。</p>
            <div class="sidebar-empty-actions">
              <button type="button" class="terminal-btn terminal-btn--primary terminal-btn--block" @click="emit('goOnboarding')">
                问卷式创建
              </button>
              <button type="button" class="terminal-btn terminal-btn--ghost terminal-btn--block" @click="emit('manageProfiles')">
                管理画像
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sidebar {
  height: 100%;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(249, 250, 248, 0.98), rgba(244, 246, 242, 0.98)),
    #f7f8f5;
}

.sidebar-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-header {
  padding: 1.25rem 1.15rem 1rem;
  border-bottom: 1px solid rgba(17, 20, 18, 0.08);
}

.sidebar-brand-row {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.sidebar-brand-mark {
  display: block;
  height: 20px;
  width: auto;
  max-width: 100%;
  object-fit: contain;
}

.sidebar-kicker {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: rgba(17, 20, 18, 0.42);
}

.sidebar-brand {
  margin: 0.45rem 0 0;
  font-size: 1.1rem;
  font-weight: 650;
  color: #111412;
  letter-spacing: -0.03em;
}

.sidebar-header__actions {
  display: grid;
  gap: 0.55rem;
  margin-top: 1rem;
}

.sidebar-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1rem 1.5rem;
  scrollbar-width: thin;
  scrollbar-color: rgba(29, 91, 61, 0.15) transparent;
}

.sidebar-scroll::-webkit-scrollbar { width: 5px; }
.sidebar-scroll::-webkit-scrollbar-track { background: transparent; }
.sidebar-scroll::-webkit-scrollbar-thumb {
  background: rgba(29, 91, 61, 0.15);
  border-radius: 999px;
}
.sidebar-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(29, 91, 61, 0.28);
}

.sidebar-section + .sidebar-section {
  margin-top: 1.5rem;
}

.sidebar-section__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.65rem;
}

.sidebar-section__label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.46);
}

.terminal-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.55rem;
  border-radius: 0.9rem;
  border: 1px solid transparent;
  font-size: 0.82rem;
  font-weight: 700;
  transition:
    border-color 0.18s ease,
    background 0.18s ease,
    color 0.18s ease,
    transform 0.18s ease;
  cursor: pointer;
}

.terminal-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.terminal-btn--primary {
  background: #171a18;
  color: #fff;
  border-color: #171a18;
}

.terminal-btn--ghost {
  background: rgba(255, 255, 255, 0.82);
  border-color: rgba(17, 20, 18, 0.1);
  color: #171a18;
}

.terminal-btn--soft {
  background: rgba(29, 91, 61, 0.08);
  border-color: rgba(29, 91, 61, 0.12);
  color: #1d5b3d;
}

.terminal-btn--block {
  width: 100%;
}

.terminal-text-btn {
  background: none;
  border: none;
  padding: 0;
  font-size: 0.74rem;
  font-weight: 700;
  color: rgba(17, 20, 18, 0.54);
  cursor: pointer;
}

.conversation-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.conversation-item {
  padding: 0.8rem 0.85rem;
  border: 1px solid rgba(17, 20, 18, 0.06);
  border-radius: 0.95rem;
  background: rgba(255, 255, 255, 0.68);
  cursor: pointer;
  transition:
    background 0.18s ease,
    border-color 0.18s ease,
    transform 0.18s ease;
}

.conversation-item + .conversation-item {
  margin-top: 0.4rem;
}

.conversation-item:hover {
  background: rgba(255, 255, 255, 0.94);
  border-color: rgba(17, 20, 18, 0.12);
  transform: translateY(-1px);
}

.conversation-item--active {
  border-color: rgba(29, 91, 61, 0.18);
  background: rgba(255, 255, 255, 0.98);
}

.conversation-item__row {
  display: flex;
  align-items: flex-start;
  gap: 0.45rem;
}

.conversation-item__main {
  flex: 1;
  min-width: 0;
}

.conversation-item__delete {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  padding: 0;
  border: none;
  border-radius: 0.5rem;
  background: transparent;
  color: rgba(17, 20, 18, 0.35);
  cursor: pointer;
  transition:
    color 0.15s ease,
    background 0.15s ease;
}

.conversation-item__delete:hover {
  color: #b42323;
  background: rgba(180, 35, 35, 0.08);
}

.conversation-item__title,
.profile-panel__title {
  font-size: 0.86rem;
  font-weight: 650;
  line-height: 1.45;
  color: #151917;
}

.conversation-item__meta {
  margin-top: 0.42rem;
  font-size: 0.72rem;
  color: rgba(17, 20, 18, 0.5);
}

.profile-panel,
.sidebar-empty-box {
  border-radius: 1rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(255, 255, 255, 0.78);
  padding: 0.95rem;
}

.profile-panel__desc,
.sidebar-empty,
.sidebar-empty-box__desc {
  margin: 0;
  font-size: 0.76rem;
  line-height: 1.7;
  color: rgba(17, 20, 18, 0.54);
}

.sidebar-empty-box__title {
  margin: 0 0 0.35rem;
  font-size: 0.88rem;
  font-weight: 650;
  color: #151917;
}

.profile-panel__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.75rem;
}

.profile-tag {
  display: inline-flex;
  align-items: center;
  min-height: 1.55rem;
  padding: 0 0.55rem;
  border-radius: 999px;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(17, 20, 18, 0.04);
  font-size: 0.68rem;
  font-weight: 700;
  color: rgba(17, 20, 18, 0.58);
}

.profile-panel__actions,
.sidebar-empty-actions {
  display: grid;
  gap: 0.6rem;
  margin-top: 0.9rem;
}

.sidebar-empty {
  margin: 0;
}
</style>
