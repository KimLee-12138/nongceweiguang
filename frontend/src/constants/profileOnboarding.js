/** localStorage：用户主动跳过全屏画像问卷后，不再强制跳转问卷页（无画像也可进 /chat） */
export const SKIP_PROFILE_ONBOARDING_KEY = 'ncwg_skip_profile_onboarding'

export function getSkipProfileOnboarding() {
  try {
    return localStorage.getItem(SKIP_PROFILE_ONBOARDING_KEY) === '1'
  } catch {
    return false
  }
}

export function setSkipProfileOnboarding() {
  try {
    localStorage.setItem(SKIP_PROFILE_ONBOARDING_KEY, '1')
  } catch {
    /* ignore */
  }
}
