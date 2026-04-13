<script setup>
defineProps({
  statCards: { type: Array, default: () => [] },
  summary: { type: String, default: '' },
  forecastCards: { type: Array, default: () => [] },
})

function accentColor(accent) {
  const map = { emerald: '#89a97d', cyan: '#67d4e8', violet: '#b49aff', amber: '#dcc386' }
  return map[accent] || '#dcc386'
}
</script>

<template>
  <section class="forecast-stage">
    <div class="forecast-stage__stats">
      <article v-for="card in statCards" :key="card.label" class="stat-surface">
        <span class="stat-surface__label">{{ card.label }}</span>
        <strong class="stat-surface__value" :style="{ color: accentColor(card.accent) }">{{ card.value }}</strong>
        <span class="stat-surface__trend">{{ card.trend }}</span>
      </article>
    </div>

    <div class="forecast-stage__main">
      <article class="forecast-stage__summary">
        <span class="forecast-stage__kicker">预测总览</span>
        <h2>湖北未来农业政策走向</h2>
        <p>{{ summary || '系统正在基于近阶段政策样本重新判断趋势信号。' }}</p>
      </article>

      <div class="forecast-stage__cards">
        <article v-for="item in forecastCards" :key="item.title" class="forecast-stage-card">
          <div class="forecast-stage-card__top">
            <span class="forecast-stage-card__signal">{{ item.signal }}</span>
            <span class="forecast-stage-card__confidence">{{ item.confidence }}置信</span>
          </div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.detail }}</p>
          <div v-if="item.basis?.length" class="forecast-stage-card__basis">
            <span v-for="basis in item.basis" :key="basis">{{ basis }}</span>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.forecast-stage {
  display: grid;
  gap: 20px;
  margin-top: 40px;
}

.forecast-stage__stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-surface {
  position: relative;
  padding: 22px;
  border-radius: 22px;
  border: 1px solid rgba(197, 205, 183, 0.12);
  background: linear-gradient(180deg, rgba(16, 35, 24, 0.88), rgba(11, 25, 18, 0.94));
  box-shadow: inset 0 1px 0 rgba(255, 248, 232, 0.05), 0 20px 60px rgba(0, 0, 0, 0.24);
  overflow: hidden;
}

.stat-surface::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 23px;
  padding: 1px;
  background: linear-gradient(180deg, rgba(214, 192, 139, 0.2) 0%, rgba(137, 169, 125, 0.06) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.stat-surface__label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(214, 192, 139, 0.84);
}

.stat-surface__value {
  display: block;
  margin-top: 12px;
  font-size: clamp(30px, 3vw, 42px);
  line-height: 1;
  letter-spacing: -0.04em;
  color: #dcc386;
}

.stat-surface__trend {
  display: block;
  margin-top: 8px;
  font-size: 12px;
  color: rgba(228, 231, 218, 0.45);
}

.forecast-stage__main {
  display: grid;
  grid-template-columns: minmax(280px, 0.95fr) minmax(0, 1.75fr);
  gap: 16px;
}

.forecast-stage__summary {
  position: relative;
  padding: 28px;
  border-radius: 30px;
  border: 1px solid rgba(197, 205, 183, 0.12);
  background: linear-gradient(180deg, rgba(16, 35, 24, 0.88), rgba(11, 25, 18, 0.94));
  box-shadow: inset 0 1px 0 rgba(255, 248, 232, 0.05), 0 20px 60px rgba(0, 0, 0, 0.24);
}

.forecast-stage__summary::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 31px;
  padding: 1px;
  background: linear-gradient(180deg, rgba(214, 192, 139, 0.2) 0%, rgba(137, 169, 125, 0.06) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.forecast-stage__kicker {
  display: inline-block;
  font-size: 12px;
  font-weight: 650;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: rgba(214, 192, 139, 0.84);
}

.forecast-stage__summary h2 {
  margin: 12px 0 0;
  font-size: clamp(26px, 3vw, 40px);
  line-height: 1.08;
  letter-spacing: -0.03em;
  color: #f8f3e7;
}

.forecast-stage__summary p {
  margin: 16px 0 0;
  line-height: 1.8;
  font-size: 15px;
  color: rgba(228, 231, 218, 0.66);
}

.forecast-stage__cards {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.forecast-stage-card {
  position: relative;
  padding: 22px;
  border-radius: 24px;
  border: 1px solid rgba(197, 205, 183, 0.12);
  background: linear-gradient(180deg, rgba(16, 35, 24, 0.88), rgba(11, 25, 18, 0.94));
  box-shadow: inset 0 1px 0 rgba(255, 248, 232, 0.05), 0 20px 60px rgba(0, 0, 0, 0.24);
  transition: border-color 0.2s, transform 0.2s;
}

.forecast-stage-card::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 25px;
  padding: 1px;
  background: linear-gradient(180deg, rgba(214, 192, 139, 0.15) 0%, rgba(137, 169, 125, 0.04) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.forecast-stage-card:hover {
  border-color: rgba(214, 192, 139, 0.22);
  transform: translateY(-2px);
}

.forecast-stage-card__top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

.forecast-stage-card__signal,
.forecast-stage-card__confidence,
.forecast-stage-card__basis span {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.forecast-stage-card__signal {
  background: rgba(137, 169, 125, 0.15);
  color: #89a97d;
}

.forecast-stage-card__confidence {
  background: rgba(214, 192, 139, 0.1);
  color: rgba(214, 192, 139, 0.8);
}

.forecast-stage-card h3 {
  margin: 14px 0 0;
  font-size: 18px;
  line-height: 1.35;
  letter-spacing: -0.02em;
  color: #f8f3e7;
}

.forecast-stage-card p {
  margin: 10px 0 0;
  line-height: 1.7;
  font-size: 14px;
  color: rgba(228, 231, 218, 0.66);
}

.forecast-stage-card__basis {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}

.forecast-stage-card__basis span {
  background: rgba(137, 169, 125, 0.1);
  color: rgba(228, 231, 218, 0.58);
}

@media (max-width: 1180px) {
  .forecast-stage__stats {
    grid-template-columns: repeat(2, 1fr);
  }
  .forecast-stage__main,
  .forecast-stage__cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .forecast-stage__stats {
    grid-template-columns: 1fr;
  }
}
</style>
