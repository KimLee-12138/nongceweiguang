<script setup>
import { computed, ref } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  streaming: { type: Boolean, default: false },
  citedPolicy: { type: Object, default: null },
  currentProfile: { type: Object, default: null },
  currentProfileName: { type: String, default: '' },
  /** match | agri_llm | interpret */
  chatMode: { type: String, default: 'interpret' },
})

const emit = defineEmits(['update:modelValue', 'send', 'submitEnter', 'changeMode', 'clearCitation'])

const isFocused = ref(false)

const modeLabel = computed(() => {
  if (props.chatMode === 'match') return '政策智能匹配'
  if (props.chatMode === 'agri_llm') return '农业政策大模型'
  return '政策白话解读'
})

const placeholder = computed(() => {
  if (props.chatMode === 'agri_llm') {
    return '提问农业政策问题，例如：家庭农场申请补贴需要哪些材料？'
  }
  if (props.citedPolicy) {
    return '围绕这条政策继续追问，例如：还缺哪些条件、需要哪些材料？'
  }
  return '输入问题、引用上下文或继续追问，系统会基于当前画像与政策信息继续分析。'
})

function onEnter(e) {
  if (e.shiftKey) return
  e.preventDefault()
  emit('submitEnter')
}
</script>

<template>
  <div class="command-dock">
    <div class="command-dock__inner">
      <transition name="terminal-fade">
        <div v-if="citedPolicy" class="reference-pill">
          <span class="reference-pill__label">引用政策</span>
          <span class="reference-pill__title">{{ citedPolicy.title }}</span>
          <button type="button" class="reference-pill__clear" aria-label="取消引用" @click="emit('clearCitation')">
            ×
          </button>
        </div>
      </transition>

      <div class="composer-box" :class="{ 'composer-box--focused': isFocused }">
        <div class="composer-box__toolbar">
          <div class="composer-box__modes">
            <el-dropdown trigger="click" placement="top-start" @command="emit('changeMode', $event)">
              <button type="button" class="mode-selector">
                {{ modeLabel }}
                <el-icon><ArrowDown /></el-icon>
              </button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="match">政策智能匹配</el-dropdown-item>
                  <el-dropdown-item command="agri_llm">农业政策大模型</el-dropdown-item>
                  <el-dropdown-item command="interpret">政策白话解读</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>

            <span v-if="currentProfile" class="context-indicator">
              <span class="context-indicator__dot" />
              当前画像：{{ currentProfileName }}
            </span>
          </div>

          <div class="composer-box__status">
            <span class="status-copy">{{ streaming ? '正在生成' : '输入后发送' }}</span>
          </div>
        </div>

        <div class="composer-box__body">
          <el-input
            :model-value="modelValue"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 6 }"
            :placeholder="placeholder"
            :disabled="streaming"
            resize="none"
            class="composer-input"
            @update:model-value="emit('update:modelValue', $event)"
            @keydown.enter="onEnter"
            @focus="isFocused = true"
            @blur="isFocused = false"
          />

          <div class="composer-box__actions">
            <button
              type="button"
              class="composer-action composer-action--primary"
              :disabled="!modelValue.trim() || streaming"
              @click="emit('send')"
            >
              <span>发送</span>
              <span class="composer-action__shortcut">Enter</span>
            </button>
          </div>
        </div>
      </div>

      <p class="dock-footnote">AI 输出仅作政策辅助判断，关键条款请结合原文与当地要求复核。</p>
    </div>
  </div>
</template>

<style scoped>
.command-dock {
  position: sticky;
  bottom: 0;
  z-index: 4;
  padding: 0 1.6rem 1.25rem;
  background: linear-gradient(0deg, rgba(241, 243, 239, 0.98) 60%, rgba(241, 243, 239, 0));
  flex-shrink: 0;
}

.command-dock__inner {
  max-width: 56rem;
  margin: 0 auto;
}

.terminal-fade-enter-active,
.terminal-fade-leave-active {
  transition:
    opacity 0.16s ease,
    transform 0.16s ease;
}

.terminal-fade-enter-from,
.terminal-fade-leave-to {
  opacity: 0;
  transform: translateY(0.35rem);
}

.reference-pill {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  width: fit-content;
  max-width: 100%;
  margin-bottom: 0.75rem;
  padding: 0.55rem 0.8rem;
  border-radius: 0.9rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(247, 248, 245, 0.94);
  overflow: hidden;
}

.reference-pill__label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.48);
}

.reference-pill__title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.84rem;
  color: #1f2421;
}

.reference-pill__clear {
  width: 1.75rem;
  height: 1.75rem;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 999px;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(255, 255, 255, 0.84);
  color: rgba(17, 20, 18, 0.6);
  cursor: pointer;
}

.composer-box {
  border-radius: 1.15rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 14px 36px rgba(17, 20, 18, 0.06);
  overflow: hidden;
  transition:
    border-color 0.18s ease,
    box-shadow 0.18s ease,
    background 0.18s ease;
}

.composer-box--focused {
  border-color: rgba(17, 20, 18, 0.18);
  box-shadow: 0 18px 44px rgba(17, 20, 18, 0.08);
  background: rgba(255, 255, 255, 0.98);
}

.composer-box__toolbar,
.composer-box__body {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.composer-box__toolbar {
  justify-content: space-between;
  padding: 0.8rem 0.95rem 0.72rem;
  border-bottom: 1px solid rgba(17, 20, 18, 0.06);
  background: rgba(249, 250, 248, 0.94);
}

.composer-box__modes,
.composer-box__status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.mode-selector {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  min-height: 2rem;
  padding: 0 0.75rem;
  border-radius: 999px;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: #fff;
  font-size: 0.76rem;
  font-weight: 700;
  color: #171b18;
  cursor: pointer;
}

.context-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-width: 0;
  font-size: 0.75rem;
  color: rgba(17, 20, 18, 0.64);
}

.context-indicator__dot {
  width: 0.42rem;
  height: 0.42rem;
  flex: 0 0 auto;
  border-radius: 999px;
  background: #1d5b3d;
}

.status-copy {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.42);
}

.composer-box__body {
  align-items: flex-end;
  padding: 0.85rem 0.95rem 0.95rem;
}

.composer-input {
  flex: 1 1 auto;
  min-width: 0;
}

.composer-input :deep(.el-textarea__inner) {
  min-height: 3rem !important;
  padding: 0;
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  font-size: 0.96rem;
  line-height: 1.7;
  color: #141816;
}

.composer-input :deep(.el-textarea__inner::placeholder) {
  color: rgba(17, 20, 18, 0.38);
}

.composer-box__actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding-bottom: 0.1rem;
}

.composer-action {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  min-height: 2.7rem;
  padding: 0 0.95rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition:
    transform 0.18s ease,
    background 0.18s ease,
    border-color 0.18s ease,
    color 0.18s ease;
}

.composer-action:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.composer-action--primary {
  border: 1px solid #171a18;
  background: #171a18;
  color: #fff;
}

.composer-action--primary:not(:disabled):hover {
  transform: translateY(-1px);
  background: #202623;
}

.composer-action__shortcut {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  opacity: 0.7;
}

.dock-footnote {
  margin: 0.55rem 0 0;
  text-align: center;
  font-size: 0.7rem;
  color: rgba(17, 20, 18, 0.42);
}

@media (max-width: 860px) {
  .command-dock {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .composer-box__toolbar,
  .composer-box__body {
    flex-direction: column;
    align-items: stretch;
  }

  .composer-box__status {
    justify-content: flex-start;
  }

  .composer-box__actions {
    justify-content: flex-end;
  }
}

:deep(.el-textarea__inner) {
  scrollbar-width: thin;
  scrollbar-color: rgba(29, 91, 61, 0.15) transparent;
}

:deep(.el-textarea__inner::-webkit-scrollbar) { width: 5px; }
:deep(.el-textarea__inner::-webkit-scrollbar-track) { background: transparent; }
:deep(.el-textarea__inner::-webkit-scrollbar-thumb) {
  background: rgba(29, 91, 61, 0.15);
  border-radius: 999px;
}
:deep(.el-textarea__inner::-webkit-scrollbar-thumb:hover) {
  background: rgba(29, 91, 61, 0.28);
}
</style>
