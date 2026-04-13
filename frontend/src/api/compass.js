import { api } from './client'

function toQuery(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    search.set(key, String(value))
  })
  const query = search.toString()
  return query ? `?${query}` : ''
}

export const compassApi = {
  getOverview(params = {}) {
    return api.get(`/compass/overview${toQuery(params)}`)
  },
  getBriefing(params = {}) {
    return api.get(`/compass/briefing${toQuery(params)}`)
  },
  getThemeTrends(params = {}) {
    return api.get(`/compass/theme-trends${toQuery(params)}`)
  },
  getReports(params = {}) {
    return api.get(`/compass/reports${toQuery(params)}`)
  },
  getReport(reportId) {
    return api.get(`/compass/reports/${reportId}`)
  },
  getGlossary(params = {}) {
    return api.get(`/compass/glossary${toQuery(params)}`)
  },
  generateReport() {
    return api.withAdmin(() => api.post('/compass/generate', {}))
  },
  createGlossary(payload) {
    return api.withAdmin(() => api.post('/compass/glossary', payload))
  },
  updateGlossary(glossaryId, payload) {
    return api.withAdmin(() => api.patch(`/compass/glossary/${glossaryId}`, payload))
  },
  deleteGlossary(glossaryId) {
    return api.withAdmin(() => api.del(`/compass/glossary/${glossaryId}`))
  },
}
