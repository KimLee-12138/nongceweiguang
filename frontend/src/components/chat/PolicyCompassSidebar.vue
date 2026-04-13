<script setup>
defineProps({
  briefing: { type: Object, default: null },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['open-compass'])

function confidenceColor(value) {
  if (value === '高') return '#1d5b3d'
  if (value === '中') return '#d4a853'
  return '#94a3b8'
}

function termAccent(category) {
  if (/主题|方向/.test(category)) return '#1d5b3d'
  if (/支持|补贴|资金/.test(category)) return '#2a7ec7'
  if (/风险|限制/.test(category)) return '#d97706'
  return 'rgba(17, 20, 18, 0.18)'
}
</script>

<template>
  <div class="policy-compass-sidebar">
    <div class="sidebar-glow"></div>

    <div class="sidebar-scroll">
      <!-- Hero -->
      <section class="side-section hero cascade-reveal" style="--reveal-i:0">
        <span class="hero-eyebrow">Hubei Policy Pulse</span>
        <h3 class="hero-title">政策风向标</h3>
        <p class="hero-summary">
          {{ briefing?.overview?.summary || '基于已入库湖北农业政策样本，持续预测后续政策主线并解释高频术语。' }}
        </p>
        <button type="button" class="hero-cta" @click="emit('open-compass')">进入风向大屏</button>
      </section>

      <!-- Forecast -->
      <section class="side-section cascade-reveal" style="--reveal-i:1">
        <div class="section-head">
          <span class="section-kicker">未来走向预测</span>
          <h4 class="section-title">湖北省后续政策主线</h4>
        </div>

        <div v-if="loading" class="skeleton-group">
          <div class="skeleton-bar long"></div>
          <div class="skeleton-bar medium"></div>
          <div class="skeleton-bar short"></div>
        </div>

        <div v-else-if="briefing?.forecast_cards?.length" class="forecast-list">
          <article
            v-for="(item, idx) in briefing.forecast_cards"
            :key="item.title"
            class="forecast-card cascade-reveal"
            :style="{ '--reveal-i': idx + 2 }"
          >
            <div class="forecast-card-head">
              <strong class="forecast-card-title">{{ item.title }}</strong>
              <span class="confidence-badge" :style="{ '--conf-color': confidenceColor(item.confidence) }">
                <i class="conf-dot"></i>{{ item.confidence }}置信
              </span>
            </div>
            <p class="forecast-card-detail">{{ item.detail }}</p>
            <div v-if="item.basis?.length" class="chip-row">
              <span v-for="basis in item.basis" :key="basis" class="chip">{{ basis }}</span>
            </div>
          </article>
        </div>

        <div v-else class="empty-hint">暂无预测数据</div>
      </section>

      <!-- Focus Policy -->
      <section v-if="briefing?.selected_policy" class="side-section cascade-reveal" style="--reveal-i:2">
        <div class="section-head">
          <span class="section-kicker focus-kicker">
            <i class="focus-dot"></i>当前政策聚焦
          </span>
          <h4 class="section-title">{{ briefing.selected_policy.title }}</h4>
        </div>
        <p class="focus-summary">{{ briefing.selected_policy.summary || '当前政策暂无摘要。' }}</p>

        <div v-if="briefing.selected_policy.terms?.length" class="term-grid">
          <article
            v-for="term in briefing.selected_policy.terms"
            :key="term.term"
            class="term-card"
            :style="{ '--accent': termAccent(term.category) }"
          >
            <div class="term-card-head">
              <strong>{{ term.term }}</strong>
              <span class="term-category">{{ term.category }}</span>
            </div>
            <p class="term-card-desc">{{ term.description }}</p>
          </article>
        </div>
      </section>

      <!-- High-frequency Terms -->
      <section class="side-section cascade-reveal" style="--reveal-i:3">
        <div class="section-head">
          <span class="section-kicker">高频术语解释</span>
          <h4 class="section-title">近期重点词</h4>
        </div>

        <div v-if="briefing?.focus_terms?.length" class="term-grid">
          <article
            v-for="term in briefing.focus_terms"
            :key="term.term"
            class="term-card hoverable"
            :style="{ '--accent': termAccent(term.category) }"
          >
            <div class="term-card-head">
              <strong>{{ term.term }}</strong>
              <span class="term-category">{{ term.category }}</span>
            </div>
            <p class="term-card-desc">{{ term.description }}</p>
          </article>
        </div>

        <div v-else-if="!loading" class="empty-hint">暂无术语数据</div>
      </section>
    </div>
  </div>
</template>

<style scoped>
/* ── 1. Container & Background ─────────────────────────── */
.policy-compass-sidebar {
  position: relative;
  height: 100%;
  width: 100%;
  background: linear-gradient(180deg, #f8f9f6 0%, #f3f4f1 100%);
  overflow: hidden;

  --text-strong: #151917;
  --text-base: #3a4340;
  --text-secondary: rgba(17, 20, 18, 0.54);
  --text-muted: rgba(17, 20, 18, 0.38);
  --brand: #1d5b3d;
  --brand-soft: rgba(29, 91, 61, 0.08);
  --brand-border: rgba(29, 91, 61, 0.14);
  --card-bg: rgba(255, 255, 255, 0.78);
  --card-border: rgba(17, 20, 18, 0.07);
  --card-border-hover: rgba(17, 20, 18, 0.14);
  --card-shadow: 0 2px 12px rgba(17, 20, 18, 0.04);
}

.sidebar-glow {
  position: absolute;
  top: -15%;
  right: -25%;
  width: 70%;
  height: 50%;
  background: radial-gradient(circle, rgba(29, 91, 61, 0.06) 0%, transparent 65%);
  filter: blur(40px);
  pointer-events: none;
  z-index: 0;
}

.sidebar-scroll {
  position: relative;
  z-index: 1;
  height: 100%;
  overflow-y: auto;
  padding: 0.75rem;
  scrollbar-width: thin;
  scrollbar-color: rgba(17, 20, 18, 0.08) transparent;
  mask-image: linear-gradient(to bottom, transparent 0%, #000 2%, #000 98%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, transparent 0%, #000 2%, #000 98%, transparent 100%);
}

.sidebar-scroll::-webkit-scrollbar { width: 4px; }
.sidebar-scroll::-webkit-scrollbar-track { background: transparent; }
.sidebar-scroll::-webkit-scrollbar-thumb { background: rgba(17, 20, 18, 0.08); border-radius: 4px; }

/* ── 2. Generic Section ────────────────────────────────── */
.side-section {
  padding: 0.9rem;
  border-radius: 0.95rem;
  border: 1px solid var(--card-border);
  background: var(--card-bg);
  box-shadow: var(--card-shadow);
}

.side-section + .side-section {
  margin-top: 0.65rem;
}

.section-head {
  margin-bottom: 0.55rem;
}

.section-kicker {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.section-title {
  margin: 0.3rem 0 0;
  font-size: 0.92rem;
  font-weight: 650;
  color: var(--text-strong);
  letter-spacing: -0.01em;
}

/* ── 3. Hero ───────────────────────────────────────────── */
.hero {
  background:
    radial-gradient(circle at 15% 25%, rgba(29, 91, 61, 0.06), transparent 50%),
    rgba(255, 255, 255, 0.88);
  border-color: var(--brand-border);
  padding-bottom: 1rem;
}

.hero-eyebrow {
  display: inline-block;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--brand);
  opacity: 0.72;
}

.hero-title {
  margin: 0.35rem 0 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-strong);
  letter-spacing: -0.02em;
}

.hero-summary {
  margin: 0.45rem 0 0;
  font-size: 0.8rem;
  line-height: 1.7;
  color: var(--text-secondary);
}

.hero-cta {
  display: inline-flex;
  align-items: center;
  margin-top: 0.75rem;
  padding: 0.42rem 0.95rem;
  border-radius: 0.65rem;
  border: 1px solid var(--brand-border);
  background: var(--brand-soft);
  color: var(--brand);
  font-size: 0.78rem;
  font-weight: 650;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.2s, border-color 0.2s, transform 0.2s;
}

.hero-cta:hover {
  background: rgba(29, 91, 61, 0.13);
  border-color: rgba(29, 91, 61, 0.24);
  transform: translateY(-1px);
}

/* ── 4. Forecast Cards ─────────────────────────────────── */
.forecast-list {
  display: grid;
  gap: 0.5rem;
}

.forecast-card {
  padding: 0.75rem;
  border-radius: 0.75rem;
  background: rgba(248, 249, 246, 0.7);
  border: 1px solid var(--card-border);
  transition: border-color 0.2s, background 0.2s, transform 0.2s;
}

.forecast-card:hover {
  border-color: var(--card-border-hover);
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-1px);
}

.forecast-card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.45rem;
}

.forecast-card-title {
  font-size: 0.82rem;
  font-weight: 620;
  color: var(--text-strong);
  line-height: 1.45;
}

.confidence-badge {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.64rem;
  font-weight: 650;
  color: var(--conf-color);
  white-space: nowrap;
}

.conf-dot {
  display: block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--conf-color);
  box-shadow: 0 0 5px color-mix(in srgb, var(--conf-color) 50%, transparent);
  animation: pulse-dot 2.4s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}

.forecast-card-detail {
  margin: 0.35rem 0 0;
  font-size: 0.78rem;
  line-height: 1.7;
  color: var(--text-secondary);
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-top: 0.5rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  min-height: 1.35rem;
  padding: 0 0.5rem;
  border-radius: 999px;
  background: var(--brand-soft);
  border: 1px solid var(--brand-border);
  color: var(--brand);
  font-size: 0.64rem;
  font-weight: 600;
}

/* ── 5. Focus Policy ───────────────────────────────────── */
.focus-kicker {
  color: var(--brand);
}

.focus-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--brand);
  box-shadow: 0 0 6px rgba(29, 91, 61, 0.4);
  animation: pulse-dot 2s ease-in-out infinite;
}

.focus-summary {
  margin: 0 0 0.55rem;
  font-size: 0.78rem;
  line-height: 1.7;
  color: var(--text-secondary);
}

/* ── 6. Term Cards (shared for focus-policy and glossary) ─ */
.term-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.45rem;
}

.term-card {
  position: relative;
  padding: 0.6rem 0.6rem 0.6rem 0.8rem;
  border-radius: 0.6rem;
  background: rgba(248, 249, 246, 0.72);
  border: 1px solid var(--card-border);
  overflow: hidden;
  transition: border-color 0.2s, background 0.2s, transform 0.2s;
}

.term-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--accent, rgba(17, 20, 18, 0.15));
  border-radius: 3px 0 0 3px;
  opacity: 0.65;
  transition: opacity 0.2s;
}

.term-card:hover {
  border-color: var(--card-border-hover);
  background: rgba(255, 255, 255, 0.96);
  transform: translateY(-1px);
}

.term-card:hover::before {
  opacity: 1;
}

.term-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.25rem;
}

.term-card-head strong {
  font-size: 0.76rem;
  font-weight: 620;
  color: var(--text-strong);
  line-height: 1.4;
}

.term-category {
  flex: 0 0 auto;
  font-size: 0.6rem;
  font-weight: 650;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

.term-card-desc {
  margin: 0.25rem 0 0;
  font-size: 0.72rem;
  line-height: 1.6;
  color: var(--text-secondary);
}

.term-card.hoverable .term-card-desc {
  max-height: 0;
  margin: 0;
  opacity: 0;
  overflow: hidden;
  transition: max-height 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s, margin 0.3s;
}

.term-card.hoverable:hover .term-card-desc {
  max-height: 8rem;
  margin-top: 0.25rem;
  opacity: 1;
}

/* ── 7. Cascade Reveal Animation ───────────────────────── */
.cascade-reveal {
  opacity: 0;
  transform: translateY(16px);
  animation: revealUp 0.55s cubic-bezier(0.16, 1, 0.3, 1) both;
  animation-delay: calc(var(--reveal-i, 0) * 0.08s);
}

@keyframes revealUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ── 8. Loading Skeleton ───────────────────────────────── */
.skeleton-group {
  display: grid;
  gap: 0.5rem;
  margin-top: 0.6rem;
}

.skeleton-bar {
  height: 10px;
  border-radius: 5px;
  background: linear-gradient(90deg, rgba(17, 20, 18, 0.04) 25%, rgba(17, 20, 18, 0.08) 50%, rgba(17, 20, 18, 0.04) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.6s ease-in-out infinite;
}

.skeleton-bar.long { width: 100%; }
.skeleton-bar.medium { width: 72%; }
.skeleton-bar.short { width: 45%; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ── 9. Empty Hint ─────────────────────────────────────── */
.empty-hint {
  margin-top: 0.65rem;
  padding: 1rem 0;
  text-align: center;
  font-size: 0.76rem;
  color: var(--text-muted);
  border: 1px dashed rgba(17, 20, 18, 0.08);
  border-radius: 0.6rem;
}

/* ── 10. Responsive ────────────────────────────────────── */
@media (max-width: 1400px) {
  .term-grid {
    grid-template-columns: 1fr;
  }
}
</style>
