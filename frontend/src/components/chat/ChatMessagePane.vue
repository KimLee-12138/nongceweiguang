<script setup>
import { nextTick, ref, watch } from 'vue'
import DOMPurify from 'dompurify'
import MarkdownIt from 'markdown-it'

import brandLogoMark from '../../assets/logo_icon.png'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  quickQuestions: { type: Array, default: () => [] },
  streaming: { type: Boolean, default: false },
})

const emit = defineEmits(['useQuickQuestion'])

const chatListRef = ref(null)
const markdown = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  typographer: true,
})
const defaultLinkRender =
  markdown.renderer.rules.link_open
  || ((tokens, idx, options, _env, self) => self.renderToken(tokens, idx, options))

markdown.renderer.rules.link_open = function linkOpen(tokens, idx, options, env, self) {
  const token = tokens[idx]
  token.attrSet('target', '_blank')
  token.attrSet('rel', 'noopener noreferrer nofollow')
  return defaultLinkRender(tokens, idx, options, env, self)
}

function renderAssistantMarkdown(content) {
  const html = markdown.render(String(content || ''))
  return DOMPurify.sanitize(html, { USE_PROFILES: { html: true } })
}

function scrollToBottom() {
  if (chatListRef.value) {
    chatListRef.value.scrollTop = chatListRef.value.scrollHeight
  }
}

watch(
  () => props.messages.length,
  () => nextTick(scrollToBottom),
)

watch(
  () => props.messages[props.messages.length - 1]?.content,
  () => {
    if (props.streaming) nextTick(scrollToBottom)
  },
)

defineExpose({ scrollToBottom })
</script>

<template>
  <div ref="chatListRef" class="stream-container">
    <template v-if="messages.length === 0">
      <div class="empty-terminal">
        <img class="empty-terminal__mark" :src="brandLogoMark" alt="农策微光" />
        <h1 class="empty-terminal__title">政策智能引擎</h1>
        <p class="empty-terminal__subtitle">
          面向农业政策判断的分析工作流。挂载画像、发起追问，生成解读与申报建议。
        </p>

        <div class="prompt-suggestions">
          <button
            v-for="(q, i) in quickQuestions"
            :key="i"
            type="button"
            class="suggestion-item"
            @click="emit('useQuickQuestion', q)"
          >
            <span class="suggestion-item__prefix">查询</span>
            <span class="suggestion-item__text">{{ q }}</span>
          </button>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="message-stream">
        <section
          v-for="(msg, i) in messages"
          :key="msg.localId || msg.id || i"
          class="turn-block"
          :class="`turn-block--${msg.role}`"
        >
          <div class="turn-rail">
            <span class="turn-avatar">{{ msg.role === 'user' ? '我' : 'AI' }}</span>
            <span class="turn-label">{{ msg.role === 'user' ? '用户输入' : '分析输出' }}</span>
          </div>

          <div class="turn-content">
            <template v-if="msg.role === 'user'">
              <div class="user-query">{{ msg.content }}</div>
            </template>
            <template v-else>
              <div class="assistant-text assistant-rich" v-html="renderAssistantMarkdown(msg.content)" />
              <span v-if="streaming && i === messages.length - 1" class="terminal-cursor" />
            </template>
          </div>
        </section>

        <div class="scroll-pad" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.stream-container {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0.96)),
    #fff;
}

.empty-terminal {
  min-height: 100%;
  padding: 4.2rem 1.5rem 5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.empty-terminal__mark {
  display: block;
  height: 52px;
  width: auto;
  max-width: 100%;
  object-fit: contain;
}

.empty-terminal__title {
  margin: 1.3rem 0 0.6rem;
  font-size: clamp(2rem, 3vw, 2.7rem);
  line-height: 1.04;
  letter-spacing: -0.05em;
  color: #111412;
}

.empty-terminal__subtitle {
  max-width: 40rem;
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.8;
  color: rgba(17, 20, 18, 0.6);
}

.prompt-suggestions {
  width: min(100%, 42rem);
  display: grid;
  gap: 0.75rem;
  margin-top: 2rem;
}

.suggestion-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.8rem;
  align-items: center;
  width: 100%;
  padding: 0.95rem 1rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  border-radius: 1rem;
  background: rgba(247, 248, 245, 0.88);
  color: #1c211e;
  text-align: left;
  cursor: pointer;
  transition:
    border-color 0.18s ease,
    background 0.18s ease,
    transform 0.18s ease;
}

.suggestion-item:hover {
  border-color: rgba(17, 20, 18, 0.18);
  background: rgba(255, 255, 255, 0.98);
  transform: translateY(-1px);
}

.suggestion-item__prefix {
  display: inline-flex;
  align-items: center;
  min-height: 1.55rem;
  padding: 0 0.55rem;
  border-radius: 999px;
  border: 1px solid rgba(17, 20, 18, 0.08);
  background: rgba(17, 20, 18, 0.04);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.54);
}

.suggestion-item__text {
  font-size: 0.92rem;
  line-height: 1.45;
}

.message-stream {
  max-width: 56rem;
  margin: 0 auto;
  padding: 2.4rem 1.6rem 1.5rem;
}

.turn-block {
  display: grid;
  grid-template-columns: 5rem minmax(0, 1fr);
  gap: 1rem;
  margin-bottom: 2.2rem;
}

.turn-rail {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  align-items: flex-start;
  padding-top: 0.15rem;
}

.turn-avatar {
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  border-radius: 0.65rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  border: 1px solid rgba(17, 20, 18, 0.08);
}

.turn-block--user .turn-avatar {
  background: rgba(17, 20, 18, 0.06);
  color: #2e3531;
}

.turn-block--assistant .turn-avatar {
  background: #171a18;
  color: #fff;
}

.turn-label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(17, 20, 18, 0.45);
}

.turn-content {
  min-width: 0;
}

.user-query {
  font-size: clamp(1.02rem, 1.6vw, 1.22rem);
  font-weight: 650;
  line-height: 1.6;
  color: #111412;
  white-space: pre-wrap;
  letter-spacing: -0.02em;
}

.assistant-text {
  font-size: 0.96rem;
  line-height: 1.82;
  color: #232826;
  word-break: break-word;
}

.assistant-rich :deep(p) {
  margin: 0 0 0.9rem;
}

.assistant-rich :deep(p:last-child) {
  margin-bottom: 0;
}

.assistant-rich :deep(h1),
.assistant-rich :deep(h2),
.assistant-rich :deep(h3),
.assistant-rich :deep(h4) {
  margin: 1rem 0 0.55rem;
  line-height: 1.4;
  color: #16251f;
}

.assistant-rich :deep(h2) {
  font-size: 1.05rem;
}

.assistant-rich :deep(h3) {
  font-size: 0.98rem;
}

.assistant-rich :deep(ul),
.assistant-rich :deep(ol) {
  margin: 0.45rem 0 0.95rem;
  padding-left: 1.3rem;
}

.assistant-rich :deep(li) {
  margin: 0.35rem 0;
}

.assistant-rich :deep(strong) {
  color: #1d5b3d;
  font-weight: 700;
}

.assistant-rich :deep(blockquote) {
  margin: 0.9rem 0;
  padding: 0.5rem 0.85rem;
  border-left: 3px solid rgba(29, 91, 61, 0.45);
  background: rgba(29, 91, 61, 0.08);
  border-radius: 0.35rem;
}

.assistant-rich :deep(code) {
  font-family: 'Consolas', 'Courier New', monospace;
  background: rgba(17, 20, 18, 0.08);
  border-radius: 0.35rem;
  padding: 0.08rem 0.32rem;
  font-size: 0.88em;
}

.assistant-rich :deep(pre) {
  margin: 0.9rem 0;
  padding: 0.85rem;
  border-radius: 0.65rem;
  background: #141816;
  color: #f4f7f5;
  overflow-x: auto;
}

.assistant-rich :deep(pre code) {
  padding: 0;
  background: transparent;
  color: inherit;
}

.assistant-rich :deep(a) {
  color: #1d5b3d;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.terminal-cursor {
  display: inline-block;
  width: 0.45rem;
  height: 1.1rem;
  margin-left: 0.2rem;
  vertical-align: text-bottom;
  background: #1d5b3d;
  animation: blink 1s step-end infinite;
}

.scroll-pad {
  height: 1rem;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

@media (max-width: 860px) {
  .message-stream {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .turn-block {
    grid-template-columns: 1fr;
    gap: 0.7rem;
  }

  .turn-rail {
    flex-direction: row;
    align-items: center;
  }
}
</style>
