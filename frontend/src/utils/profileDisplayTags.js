/** @param {Record<string, unknown> | null | undefined} profile */
export function profileDisplayTags(profile) {
  if (!profile) return []
  const tags = []
  if (profile.area != null && profile.area !== '') tags.push(`${profile.area} 亩`)
  if (profile.green_cert === true) tags.push('绿色认证')
  else if (profile.green_cert === false) tags.push('无绿色认证')
  if (profile.irrigation) tags.push(String(profile.irrigation))
  if (profile.type) tags.push(String(profile.type))
  return tags
}
