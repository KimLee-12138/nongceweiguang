const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const authEvents = new EventTarget()

function createNetworkError(path, cause) {
  const usingDevProxy = API_BASE_URL.startsWith('/')
  const message = usingDevProxy
    ? '无法连接后端服务，请确认前端通过 Vite 启动，并且后端 API 已运行在 http://127.0.0.1:8000。'
    : `无法连接后端服务，请检查 API 地址 ${API_BASE_URL} 是否可访问。`
  const err = new Error(message)
  err.status = 0
  err.code = 'NETWORK_ERROR'
  err.isNetworkError = true
  err.path = path
  err.cause = cause
  return err
}

/** 解析 FastAPI / Starlette 的 JSON 错误体，避免 detail 为数组时前端只看到 [object Object] */
function messageFromErrorBody(body) {
  if (typeof body === 'string') return body || '请求失败'
  if (!body || typeof body !== 'object') return '请求失败'
  const d = body.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) {
    const parts = d.map((x) => (typeof x?.msg === 'string' ? x.msg : JSON.stringify(x)))
    return parts.filter(Boolean).join('；') || '请求失败'
  }
  return '请求失败'
}

async function rawFetch(path, options = {}) {
  const headers = new Headers(options.headers || {})
  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData
  if (!isFormData && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      credentials: 'include',
      headers,
    })
    return res
  } catch (error) {
    throw createNetworkError(path, error)
  }
}

async function fetchJson(path, options = {}) {
  const res = await rawFetch(path, options)
  if (res.status === 204) {
    return null
  }
  const contentType = res.headers.get('content-type') || ''
  const body = contentType.includes('application/json') ? await res.json() : await res.text()
  if (!res.ok) {
    const msg = messageFromErrorBody(body)
    const err = new Error(msg)
    err.status = res.status
    err.body = body
    throw err
  }
  return body
}

async function withAutoRefresh(role, fn) {
  try {
    return await fn()
  } catch (e) {
    if (e?.status !== 401) throw e
    // 401 尝试 refresh 再重试一次
    try {
      if (role === 'admin') {
        await fetchJson('/auth/refresh', { method: 'POST' })
      } else {
        await fetchJson('/user-auth/refresh', { method: 'POST' })
      }
      return await fn()
    } catch (refreshErr) {
      authEvents.dispatchEvent(
        new CustomEvent('auth:refresh_failed', {
          detail: { role, error: refreshErr?.message || 'refresh_failed' },
        })
      )
      throw e
    }
  }
}

export const api = {
  get: (path) => fetchJson(path, { method: 'GET' }),
  post: (path, data) => fetchJson(path, { method: 'POST', body: JSON.stringify(data ?? {}) }),
  put: (path, data) => fetchJson(path, { method: 'PUT', body: JSON.stringify(data ?? {}) }),
  patch: (path, data) => fetchJson(path, { method: 'PATCH', body: JSON.stringify(data ?? {}) }),
  del: (path) => fetchJson(path, { method: 'DELETE' }),
  withUser: (fn) => withAutoRefresh('user', fn),
  withAdmin: (fn) => withAutoRefresh('admin', fn),
  baseUrl: API_BASE_URL,
  rawFetch,
}

