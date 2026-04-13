<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  /** @type {{ id: number, policy_id: number, fully_matched: boolean, created_at?: string }[]} */
  records: { type: Array, default: () => [] },
  profileName: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="profileName ? `匹配历史 · ${profileName}` : '匹配历史'"
    width="min(520px, 94vw)"
    destroy-on-close
  >
    <div v-if="loading" class="muted">加载中…</div>
    <el-table v-else-if="records.length" :data="records" size="small" stripe max-height="360">
      <el-table-column prop="id" label="#" width="56" />
      <el-table-column prop="policy_id" label="政策 ID" width="88" />
      <el-table-column label="完全匹配" width="100">
        <template #default="{ row }">
          <el-tag :type="row.fully_matched ? 'success' : 'warning'" size="small">
            {{ row.fully_matched ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" min-width="160" />
    </el-table>
    <p v-else class="muted">暂无匹配记录。</p>
  </el-dialog>
</template>

<style scoped>
.muted {
  margin: 0;
  color: rgba(17, 20, 18, 0.5);
  font-size: 0.9rem;
}
</style>
