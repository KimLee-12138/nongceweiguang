import { ref } from 'vue'

import { api } from '../api/client'

export const userSessionStatus = ref('unknown')
export const userSessionError = ref(null)
export const adminSessionStatus = ref('unknown')
export const adminSessionError = ref(null)

export async function getUserMe() {
  return api.get('/user-auth/me')
}

export async function getAdminMe() {
  return api.get('/auth/me')
}

export async function userLogin(username, password) {
  return api.post('/user-auth/login', { username, password })
}

export async function userRegister(username, password) {
  return api.post('/user-auth/register', { username, password })
}

export async function adminLogin(username, password) {
  return api.post('/auth/login', { username, password })
}

export async function userLogoutAll() {
  return api.post('/user-auth/logout-all')
}

export async function adminLogoutAll() {
  return api.post('/auth/logout-all')
}

function formatAuthActionError(error, fallback) {
  if (error?.isNetworkError) {
    return error.message
  }
  if (error?.status === 503) {
    return error.message || '认证服务暂时不可用，请检查数据库连接后重试。'
  }
  return error?.message || fallback
}

function normalizeSessionProbe(error, statusRef, errorRef) {
  const status = error?.status
  if (status === 401) {
    statusRef.value = 'anonymous'
    return { status: 'anonymous' }
  }
  if (status === 403) {
    statusRef.value = 'forbidden'
    return { status: 'forbidden' }
  }
  errorRef.value = error
  statusRef.value = 'error'
  return { status: 'error', error }
}

/**
 * 探测普通用户 Cookie 会话；更新 userSessionStatus / userSessionError。
 * @returns {{ status: 'authenticated', principal: { username: string, id?: number } } | { status: 'anonymous' } | { status: 'forbidden' } | { status: 'error', error: Error }}
 */
export async function ensureUserSession({ force: _force } = {}) {
  void _force
  userSessionError.value = null
  try {
    const me = await getUserMe()
    if (me?.authenticated) {
      userSessionStatus.value = 'authenticated'
      const username = me.username || '用户'
      return { status: 'authenticated', principal: { username, id: me.id } }
    }
    userSessionStatus.value = 'anonymous'
    return { status: 'anonymous' }
  } catch (error) {
    return normalizeSessionProbe(error, userSessionStatus, userSessionError)
  }
}

/**
 * 探测管理员 Cookie 会话；更新 adminSessionStatus / adminSessionError。
 * @returns {{ status: 'authenticated', principal: { username: string, id?: number } } | { status: 'anonymous' } | { status: 'forbidden' } | { status: 'error', error: Error }}
 */
export async function ensureAdminSession({ force: _force } = {}) {
  void _force
  adminSessionError.value = null
  try {
    const me = await getAdminMe()
    if (me?.authenticated) {
      adminSessionStatus.value = 'authenticated'
      const username = me.username || '管理员'
      return { status: 'authenticated', principal: { username, id: me.id } }
    }
    adminSessionStatus.value = 'anonymous'
    return { status: 'anonymous' }
  } catch (error) {
    return normalizeSessionProbe(error, adminSessionStatus, adminSessionError)
  }
}

/** 登录并刷新本地会话状态；返回展示用用户名 */
export async function loginUserSession({ username, password }) {
  const session = await userLogin(username, password)
  await ensureUserSession({ force: true })
  return { username: session?.username || username }
}

/** 登录并刷新本地会话状态；返回展示用用户名 */
export async function loginAdminSession({ username, password }) {
  const session = await adminLogin(username, password)
  await ensureAdminSession({ force: true })
  return { username: session?.username || username }
}

export async function logoutUserSessionState() {
  await userLogoutAll().catch(() => null)
  userSessionStatus.value = 'anonymous'
  userSessionError.value = null
}

export async function logoutAdminSessionState() {
  await adminLogoutAll().catch(() => null)
  adminSessionStatus.value = 'anonymous'
  adminSessionError.value = null
}

export function getAuthErrorMessage(error, { fallback = '请求失败，请稍后重试' } = {}) {
  return formatAuthActionError(error, fallback)
}
