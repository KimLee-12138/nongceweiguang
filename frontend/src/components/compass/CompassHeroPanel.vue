<script setup>
defineProps({
  months: { type: Number, default: 6 },
  loading: { type: Boolean, default: false },
  generating: { type: Boolean, default: false },
  selectedPolicy: { type: Object, default: null },
  summary: { type: String, default: '' },
})

const emit = defineEmits(['update:months', 'refresh', 'generate'])
</script>

<template>
  <section class="compass-hero">
    <div class="compass-hero__bg">
      <div class="compass-hero__grid"></div>
      <div class="compass-hero__glow compass-hero__glow--primary"></div>
      <div class="compass-hero__glow compass-hero__glow--secondary"></div>
    </div>

    <div class="compass-hero__inner">
      <div class="compass-hero__content">
        <div class="compass-hero__left">
          <span class="compass-hero__eyebrow">Hubei Agri Policy Radar</span>
          <h1 class="compass-hero__title">政策风向大屏</h1>
          <p class="compass-hero__summary">
            {{ summary || '基于已入库湖北农业政策样本，实时汇总政策热度、主题演进、活跃机构与未来走向。' }}
          </p>
          <div class="compass-hero__meta">
            <div class="hero-meta-chip">
              <span class="hero-meta-chip__label">状态</span>
              <strong>实时演算中</strong>
            </div>
            <div v-if="selectedPolicy" class="hero-meta-chip hero-meta-chip--wide">
              <span class="hero-meta-chip__label">焦点政策</span>
              <strong>{{ selectedPolicy.title }}</strong>
            </div>
          </div>
        </div>

        <div class="compass-hero__right">
          <div class="hero-control-card">
            <span class="hero-control-card__label">时间窗口</span>
            <el-select
              :model-value="months"
              class="hero-control-card__select"
              @update:model-value="emit('update:months', $event)"
            >
              <el-option :value="3" label="近 3 个月" />
              <el-option :value="6" label="近 6 个月" />
              <el-option :value="12" label="近 12 个月" />
            </el-select>
            <div class="hero-control-card__actions">
              <el-button plain :loading="loading" @click="emit('refresh')">刷新态势</el-button>
              <el-button type="primary" :loading="generating" @click="emit('generate')">生成新报告</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.compass-hero {
  position: relative;
  overflow: hidden;
  width: 100%;
  min-height: 380px;
  padding: 100px 32px 56px;
  box-sizing: border-box;
  background: transparent;
}

.compass-hero__bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.compass-hero__grid {
  display: none;
}

.compass-hero__glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(100px);
  opacity: 0.7;
}

.compass-hero__glow--primary {
  top: -100px;
  left: -8%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(214, 192, 139, 0.14), transparent);
}

.compass-hero__glow--secondary {
  right: 8%;
  bottom: -140px;
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, rgba(137, 169, 125, 0.12), transparent);
}

.compass-hero__inner {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
}

.compass-hero__content {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.72fr);
  gap: 32px;
  align-items: end;
}

.compass-hero__eyebrow {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: rgba(214, 192, 139, 0.84);
}

.compass-hero__title {
  margin: 14px 0 0;
  font-size: clamp(40px, 5vw, 68px);
  line-height: 1;
  letter-spacing: -0.04em;
  color: #f8f3e7;
}

.compass-hero__summary {
  max-width: 720px;
  margin: 20px 0 0;
  font-size: 15px;
  line-height: 1.8;
  color: rgba(228, 231, 218, 0.66);
}

.compass-hero__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 24px;
}

.hero-meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 42px;
  max-width: 100%;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid rgba(197, 205, 183, 0.12);
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.hero-meta-chip--wide {
  max-width: min(100%, 420px);
}

.hero-meta-chip__label {
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(214, 192, 139, 0.6);
}

.hero-meta-chip strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #f8f3e7;
  font-size: 13px;
}

.hero-control-card {
  position: relative;
  display: grid;
  gap: 12px;
  padding: 20px;
  border-radius: 24px;
  border: 1px solid rgba(197, 205, 183, 0.12);
  background: linear-gradient(180deg, rgba(16, 35, 24, 0.88), rgba(11, 25, 18, 0.94));
  box-shadow: inset 0 1px 0 rgba(255, 248, 232, 0.05), 0 20px 60px rgba(0, 0, 0, 0.24);
}

.hero-control-card::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 25px;
  padding: 1px;
  background: linear-gradient(180deg, rgba(214, 192, 139, 0.2) 0%, rgba(137, 169, 125, 0.08) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.hero-control-card__label {
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(214, 192, 139, 0.72);
}

.hero-control-card__select {
  width: 100%;
}

.hero-control-card__actions {
  display: grid;
  gap: 10px;
}

:deep(.hero-control-card__select .el-select__wrapper) {
  min-height: 44px;
  border-radius: 12px;
  background: rgba(4, 16, 12, 0.8);
  box-shadow: inset 0 0 0 1px rgba(197, 205, 183, 0.1);
}

:deep(.hero-control-card__select .el-select__placeholder),
:deep(.hero-control-card__select .el-select__selected-item) {
  color: #f8f3e7;
}

:deep(.hero-control-card .el-button) {
  min-height: 42px;
  border-radius: 12px;
}

:deep(.hero-control-card .el-button--default) {
  border-color: rgba(197, 205, 183, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: #f8f3e7;
}

:deep(.hero-control-card .el-button--primary) {
  border-color: rgba(214, 192, 139, 0.5);
  background: linear-gradient(135deg, #89a97d, #6f8a63);
  color: #f8f3e7;
}

@media (max-width: 1120px) {
  .compass-hero__content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .compass-hero {
    padding: 90px 20px 36px;
    min-height: 320px;
  }
  .compass-hero__title {
    font-size: 36px;
  }
}
</style>
