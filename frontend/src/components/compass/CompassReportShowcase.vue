<script setup>
defineProps({
  reports: { type: Array, default: () => [] },
  selectedReport: { type: Object, default: null },
  glossaryItems: { type: Array, default: () => [] },
  glossaryKeyword: { type: String, default: '' },
  glossaryCategory: { type: String, default: '' },
  savingGlossary: { type: Boolean, default: false },
  deletingGlossaryId: { type: [Number, String], default: null },
})

const emit = defineEmits([
  'select-report',
  'update:glossaryKeyword',
  'update:glossaryCategory',
  'open-create-glossary',
  'open-edit-glossary',
  'remove-glossary',
])
</script>

<template>
  <section class="report-showcase">
    <div class="report-showcase__grid">
      <article class="showcase-panel showcase-panel--report">
        <div class="showcase-panel__head">
          <div>
            <span class="showcase-panel__kicker">报告总览</span>
            <h2>风向标报告</h2>
            <p>以更适合展示的方式浏览最近报告与重点摘要。</p>
          </div>
        </div>

        <div class="report-list">
          <button
            v-for="item in reports"
            :key="item.id"
            type="button"
            class="report-item"
            :class="{ active: selectedReport?.id === item.id }"
            @click="emit('select-report', item.id)"
          >
            <strong>{{ item.title }}</strong>
            <span>{{ item.summary || '暂无摘要' }}</span>
            <small>{{ item.published_at?.slice(0, 10) }}</small>
          </button>
        </div>

        <article v-if="selectedReport" class="report-detail">
          <p class="report-meta">{{ selectedReport.category }} · {{ selectedReport.published_at?.slice(0, 10) }}</p>
          <h3>{{ selectedReport.title }}</h3>
          <p class="report-summary">{{ selectedReport.summary }}</p>
          <pre class="report-content">{{ selectedReport.content }}</pre>
        </article>
        <el-empty v-else description="暂无报告，先生成一篇最新风向标报告" />
      </article>

      <article class="showcase-panel showcase-panel--glossary">
        <div class="showcase-panel__head">
          <div>
            <span class="showcase-panel__kicker">术语资产</span>
            <h2>智库词典</h2>
            <p>保留展示与筛选，把维护操作降到次级层级。</p>
          </div>
          <el-button size="small" type="primary" plain :loading="savingGlossary" @click="emit('open-create-glossary')">
            新增词条
          </el-button>
        </div>

        <div class="glossary-filters">
          <el-input
            :model-value="glossaryKeyword"
            placeholder="搜索术语或说明"
            clearable
            @update:model-value="emit('update:glossaryKeyword', $event)"
          />
          <el-select
            :model-value="glossaryCategory"
            placeholder="全部类别"
            clearable
            @update:model-value="emit('update:glossaryCategory', $event)"
          >
            <el-option label="政策主题" value="政策主题" />
            <el-option label="主体类型" value="主体类型" />
            <el-option label="支持方向" value="支持方向" />
            <el-option label="风险提示" value="风险提示" />
          </el-select>
        </div>

        <div class="glossary-list">
          <article v-for="item in glossaryItems" :key="item.id" class="glossary-card">
            <div class="glossary-card-head">
              <div>
                <h3>{{ item.term }}</h3>
                <p>{{ item.category }} · 权重 {{ item.weight }}</p>
              </div>
              <el-tag :type="item.enabled ? 'success' : 'info'" effect="light">{{ item.enabled ? '启用中' : '已停用' }}</el-tag>
            </div>
            <p class="glossary-desc">{{ item.description }}</p>
            <div v-if="item.aliases?.length" class="alias-row">
              <span v-for="alias in item.aliases" :key="alias" class="alias-chip">{{ alias }}</span>
            </div>
            <div class="glossary-actions">
              <el-button size="small" plain @click="emit('open-edit-glossary', item)">编辑</el-button>
              <el-button
                size="small"
                type="danger"
                plain
                :loading="deletingGlossaryId === item.id"
                @click="emit('remove-glossary', item)"
              >
                删除
              </el-button>
            </div>
          </article>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.report-showcase {
  margin-top: 20px;
}

.report-showcase__grid {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(300px, 0.9fr);
  gap: 16px;
}

/* ── Panel base (dark glass) ─────────────────────────────── */
.showcase-panel {
  position: relative;
  padding: 24px;
  border-radius: 30px;
  border: 1px solid rgba(197, 205, 183, 0.12);
  background: linear-gradient(180deg, rgba(16, 35, 24, 0.88), rgba(11, 25, 18, 0.94));
  box-shadow: inset 0 1px 0 rgba(255, 248, 232, 0.05), 0 20px 60px rgba(0, 0, 0, 0.24);
}

.showcase-panel::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 31px;
  padding: 1px;
  background: linear-gradient(180deg, rgba(214, 192, 139, 0.15) 0%, rgba(137, 169, 125, 0.04) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.showcase-panel__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.showcase-panel__kicker {
  display: inline-block;
  font-size: 11px;
  font-weight: 650;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: rgba(214, 192, 139, 0.84);
}

.showcase-panel__head h2 {
  margin: 8px 0 0;
  font-size: 22px;
  letter-spacing: -0.02em;
  color: #f8f3e7;
}

.showcase-panel__head p {
  margin: 6px 0 0;
  font-size: 14px;
  line-height: 1.6;
  color: rgba(228, 231, 218, 0.55);
}

/* ── Report List ─────────────────────────────────────────── */
.report-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.report-item {
  width: 100%;
  padding: 16px;
  text-align: left;
  border: 1px solid rgba(197, 205, 183, 0.1);
  border-radius: 16px;
  background: rgba(16, 35, 24, 0.6);
  cursor: pointer;
  font-family: inherit;
  transition: transform 0.18s, border-color 0.18s, background 0.18s;
}

.report-item:hover {
  transform: translateY(-1px);
  border-color: rgba(214, 192, 139, 0.2);
  background: rgba(16, 35, 24, 0.8);
}

.report-item.active {
  border-color: rgba(214, 192, 139, 0.3);
  background: rgba(214, 192, 139, 0.06);
}

.report-item strong {
  display: block;
  font-size: 15px;
  color: #f8f3e7;
}

.report-item span {
  display: block;
  margin-top: 5px;
  font-size: 13px;
  color: rgba(228, 231, 218, 0.5);
  line-height: 1.6;
}

.report-item small {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  color: rgba(228, 231, 218, 0.3);
}

/* ── Report Detail ───────────────────────────────────────── */
.report-detail {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid rgba(197, 205, 183, 0.08);
}

.report-meta {
  margin: 0;
  font-size: 11px;
  font-weight: 650;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(214, 192, 139, 0.7);
}

.report-detail h3 {
  margin: 10px 0 8px;
  font-size: 24px;
  letter-spacing: -0.02em;
  color: #f8f3e7;
}

.report-summary {
  margin: 0 0 14px;
  line-height: 1.7;
  font-size: 15px;
  color: rgba(228, 231, 218, 0.66);
}

.report-content {
  margin: 0;
  padding: 18px;
  white-space: pre-wrap;
  line-height: 1.75;
  font-size: 14px;
  color: rgba(228, 231, 218, 0.72);
  border-radius: 14px;
  background: rgba(4, 16, 12, 0.5);
  border: 1px solid rgba(197, 205, 183, 0.08);
}

/* ── Glossary ────────────────────────────────────────────── */
.glossary-filters {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 150px;
  gap: 10px;
  margin-bottom: 14px;
}

.glossary-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.glossary-card {
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(197, 205, 183, 0.1);
  background: rgba(16, 35, 24, 0.6);
  transition: border-color 0.2s;
}

.glossary-card:hover {
  border-color: rgba(214, 192, 139, 0.2);
}

.glossary-card-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.glossary-card h3 {
  margin: 0;
  font-size: 15px;
  color: #f8f3e7;
}

.glossary-card-head p {
  margin: 4px 0 0;
  font-size: 12px;
  color: rgba(228, 231, 218, 0.45);
}

.glossary-desc {
  margin: 8px 0 0;
  line-height: 1.7;
  font-size: 13px;
  color: rgba(228, 231, 218, 0.6);
}

.alias-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.alias-chip {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  background: rgba(137, 169, 125, 0.15);
  color: #89a97d;
  font-size: 11px;
  font-weight: 500;
}

.glossary-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

/* ── Element Plus dark overrides ─────────────────────────── */
:deep(.el-input__wrapper) {
  background: rgba(4, 16, 12, 0.8) !important;
  box-shadow: inset 0 0 0 1px rgba(197, 205, 183, 0.12) !important;
}
:deep(.el-input__inner) {
  color: #f8f3e7 !important;
}
:deep(.el-select__wrapper) {
  background: rgba(4, 16, 12, 0.8) !important;
  box-shadow: inset 0 0 0 1px rgba(197, 205, 183, 0.12) !important;
}
:deep(.el-select__placeholder),
:deep(.el-select__selected-item) {
  color: rgba(228, 231, 218, 0.7) !important;
}
:deep(.el-button--primary.is-plain) {
  border-color: rgba(214, 192, 139, 0.3) !important;
  background: rgba(214, 192, 139, 0.08) !important;
  color: #dcc386 !important;
}
:deep(.el-tag--success) {
  background: rgba(137, 169, 125, 0.15) !important;
  border-color: rgba(137, 169, 125, 0.25) !important;
  color: #89a97d !important;
}
:deep(.el-tag--info) {
  background: rgba(228, 231, 218, 0.08) !important;
  border-color: rgba(228, 231, 218, 0.15) !important;
  color: rgba(228, 231, 218, 0.6) !important;
}
:deep(.el-button--small) {
  border-color: rgba(197, 205, 183, 0.15) !important;
  background: rgba(255, 255, 255, 0.04) !important;
  color: rgba(228, 231, 218, 0.7) !important;
}
:deep(.el-button--danger.is-plain) {
  border-color: rgba(220, 80, 80, 0.3) !important;
  background: rgba(220, 80, 80, 0.08) !important;
  color: #e87070 !important;
}
:deep(.el-empty__description p) {
  color: rgba(228, 231, 218, 0.45) !important;
}

@media (max-width: 1180px) {
  .report-showcase__grid,
  .glossary-filters {
    grid-template-columns: 1fr;
  }
}
</style>
