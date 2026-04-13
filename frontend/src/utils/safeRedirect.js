/**
 * @param {unknown} v
 */
function firstQueryValue(v) {
  if (Array.isArray(v)) return v[0]
  return v
}

/**
 * 仅允许站内相对路径，防止 ?redirect=//evil.com 等开放重定向。
 * @param {unknown} raw
 * @param {string} fallback
 * @returns {string}
 */
export function safeInternalRedirectPath(raw, fallback) {
  raw = firstQueryValue(raw)
  if (typeof raw !== 'string') return fallback
  const t = raw.trim()
  if (!t.startsWith('/') || t.startsWith('//') || t.includes('\\')) return fallback
  return t
}
