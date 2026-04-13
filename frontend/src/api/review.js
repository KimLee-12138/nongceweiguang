import { api } from './client'

function buildQuery(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    search.set(key, String(value))
  })
  const suffix = search.toString()
  return suffix ? `?${suffix}` : ''
}

export function getPolicyReviewTasks(params = {}) {
  return api.withAdmin(() => api.get(`/policies/review/tasks${buildQuery(params)}`))
}

export async function getPolicyReviewTask(taskId) {
  const res = await api.withAdmin(() => api.get(`/policies/review/tasks/${taskId}`))
  return {
    ...(res.task || {}),
    events: res.events || [],
  }
}

export function updatePolicyReviewDraft(taskId, payload) {
  return api.withAdmin(() => api.patch(`/policies/review/tasks/${taskId}/draft`, payload))
}

export function approvePolicyReviewTask(taskId, payload = {}) {
  return api.withAdmin(() => api.post(`/policies/review/tasks/${taskId}/approve`, payload))
}

export function rejectPolicyReviewTask(taskId, payload) {
  return api.withAdmin(() => api.post(`/policies/review/tasks/${taskId}/reject`, payload))
}

export function refreshPolicyReviewAI(taskId) {
  return api.withAdmin(() => api.post(`/policies/review/tasks/${taskId}/refresh-ai`, {}))
}

export function refreshPolicyReviewConditionTree(taskId) {
  return api.withAdmin(() => api.post(`/policies/review/tasks/${taskId}/refresh-condition-tree`, {}))
}

export function getAdminRun(runId) {
  return api.withAdmin(() => api.get(`/admin-ops/runs/${runId}`))
}
