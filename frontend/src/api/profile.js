import { api } from './client'

/**
 * 提交用户画像问卷数据（POST /profiles）
 * @param {Record<string, unknown>} data name, type, area, green_cert, irrigation, extra_data
 */
export async function saveUserProfile(data) {
  return api.withUser(() => api.post('/profiles', data))
}

/** 获取当前用户画像列表（用于路由或入口判断） */
export async function getUserProfiles() {
  return api.withUser(() => api.get('/profiles'))
}
