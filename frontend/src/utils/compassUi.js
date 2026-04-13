function pickName(item) {
  return cleanCompassLabel(item?.name || item?.term || item?.title || '')
}

export function cleanCompassLabel(value, fallback = '') {
  const raw = String(value || '').trim()
  if (!raw) return fallback

  const replacements = [
    [/瑙勮寖.*枃浠.?/, '规范性文件'],
    [/鍏朵粬.*鍏紑.*枃浠.?/, '其他主动公开文件'],
    [/鏀跨瓥.*瑙ｈ/, '政策解读'],
    [/鏈夋晥/, '有效'],
    [/寰呯敓鏁?/, '待生效'],
    [/宸插け鏁?/, '已失效'],
    [/搴熸/, '废止'],
    [/鏀跨瓥涓婚/, '政策主题'],
    [/涓讳綋绫诲瀷/, '主体类型'],
    [/鏀寔鏂瑰悜/, '支持方向'],
    [/椋庨櫓鎻愮ず/, '风险提示'],
    [/鏈垎绫?/, '未分类'],
    [/鏈煡/, '未知'],
    [/婀栧寳鐪?/, '湖北省'],
    [/鏈爣娉ㄦ潵婧?/, '未标注来源'],
  ]

  for (const [pattern, next] of replacements) {
    if (pattern.test(raw)) return next
  }
  return raw
}

export function cleanCompassText(value, fallback = '') {
  const raw = String(value || '').trim()
  if (!raw) return fallback
  if (!/[�]/.test(raw)) return raw
  return fallback || raw
}

export function buildCompassSummary({ overview, briefing, selectedPolicy }) {
  const topTopic = pickName(overview?.top_topics?.[0]) || pickName(briefing?.signal_highlights?.top_topics?.[0]) || '高频涉农主题'
  const topIssuer = pickName(overview?.top_issuers?.[0]) || pickName(briefing?.signal_highlights?.top_issuers?.[0]) || '省级主管部门'
  const topAudience =
    pickName(overview?.audience_distribution?.[0]) || pickName(briefing?.signal_highlights?.audience_distribution?.[0]) || '规模经营主体'
  const policyHint = selectedPolicy?.title ? `当前聚焦《${selectedPolicy.title}》的信号外溢。` : '当前页面正在对近期政策样本进行实时聚合。'
  return `系统正在围绕“${topTopic}”持续追踪热度变化，并监测 ${topIssuer} 的发文节奏与 ${topAudience} 的受益机会。${policyHint}`
}

export function buildCompassForecastCards({ overview, briefing }) {
  const topTopics = (briefing?.signal_highlights?.top_topics || overview?.top_topics || []).map(pickName).filter(Boolean)
  const topIssuers = (briefing?.signal_highlights?.top_issuers || overview?.top_issuers || []).map(pickName).filter(Boolean)
  const topAudience = (briefing?.signal_highlights?.audience_distribution || overview?.audience_distribution || [])
    .map(pickName)
    .filter(Boolean)
  const monthlyTrend = briefing?.signal_highlights?.monthly_trend || overview?.monthly_trend || []
  const latestCount = Number(monthlyTrend.at?.(-1)?.count || 0)
  const previousCount = Number(monthlyTrend.at?.(-2)?.count || latestCount)
  const trendUp = latestCount >= previousCount

  return [
    {
      signal: '主题脉冲',
      confidence: topTopics.length >= 2 ? '高' : '中',
      title: topTopics[0] ? `“${topTopics[0]}”仍是当前最强主线` : '热点主线仍在持续抬升',
      detail:
        topTopics.length >= 2
          ? `近期样本中的高频主题集中在 ${topTopics.slice(0, 3).join('、')}，说明后续相关配套政策仍可能继续补充。`
          : '系统未识别到足够稳定的主题聚合，但样本热度仍在围绕少数重点方向收敛。',
      basis: topTopics.slice(0, 3),
    },
    {
      signal: '机构活跃',
      confidence: topIssuers.length >= 2 ? '高' : '中',
      title: topIssuers[0] ? `${topIssuers[0]} 是当前最活跃的发文来源` : '核心机构仍在主导政策释放节奏',
      detail:
        topIssuers.length >= 2
          ? `目前最值得跟踪的机构包括 ${topIssuers.slice(0, 3).join('、')}，它们很可能继续定义下一阶段的政策主题。`
          : '从现有样本看，政策发布仍集中在少数主管部门，节奏相对稳定。',
      basis: topIssuers.slice(0, 3),
    },
    {
      signal: trendUp ? '节奏上扬' : '主体机会',
      confidence: topAudience.length >= 2 ? '高' : '中',
      title: trendUp ? '最近一段时间发文节奏保持活跃' : '重点主体的受益窗口正在成形',
      detail: trendUp
        ? `最近一个观察窗口内的新增政策数量${latestCount > previousCount ? '继续高于' : '基本持平于'}上一窗口，短期内仍存在继续释出配套文件的可能。`
        : `从条件树和样本标签看，${topAudience.slice(0, 2).join('、') || '重点经营主体'}仍是最值得重点关注的受益对象。`,
      basis: trendUp ? [`最近窗口 ${latestCount} 条`, `上一窗口 ${previousCount} 条`] : topAudience.slice(0, 3),
    },
  ]
}

export function buildCompassKpiCards(overview) {
  const stats = overview?.stats || {}
  return [
    {
      label: '正式政策样本',
      value: stats.policy_count ?? 0,
      accent: 'emerald',
      trend: '已结构化入库',
    },
    {
      label: '原始采集样本',
      value: stats.raw_policy_count ?? 0,
      accent: 'cyan',
      trend: '持续接入追踪',
    },
    {
      label: '已生成风向报告',
      value: stats.report_count ?? 0,
      accent: 'violet',
      trend: '可直接查看摘要',
    },
    {
      label: '智库词典条目',
      value: stats.glossary_count ?? 0,
      accent: 'amber',
      trend: '支持主题识别',
    },
  ]
}

export function normalizeDistribution(items = []) {
  return items.map((item) => ({
    ...item,
    name: cleanCompassLabel(item?.name || item?.source || item?.audience || item?.period || ''),
    count: Number(item?.count || 0),
  }))
}

export function normalizePolicyCards(items = []) {
  return items.map((item) => ({
    ...item,
    title: cleanCompassText(item?.title, '未命名政策'),
    summary: cleanCompassText(item?.summary, '系统正在等待更完整的政策摘要。'),
    source: cleanCompassLabel(item?.source, '未标注来源'),
    file_type: cleanCompassLabel(item?.file_type, '未分类'),
    validity_status: cleanCompassLabel(item?.validity_status, '未知'),
  }))
}

export function normalizeGlossaryItems(items = []) {
  return items.map((item) => ({
    ...item,
    term: cleanCompassLabel(item?.term, '未命名词条'),
    category: cleanCompassLabel(item?.category, '政策主题'),
    description: cleanCompassText(item?.description, '该词条用于辅助识别当前政策热点与重点支持方向。'),
    aliases: Array.isArray(item?.aliases) ? item.aliases.map((alias) => cleanCompassLabel(alias)).filter(Boolean) : [],
  }))
}

export function normalizeSelectedPolicy(policy) {
  if (!policy) return null
  return {
    ...policy,
    title: cleanCompassText(policy.title, '当前焦点政策'),
    summary: cleanCompassText(policy.summary, '该政策当前已被纳入风向研判样本，系统正在结合条件树和词典标签做联动分析。'),
    source: cleanCompassLabel(policy.source, '未标注来源'),
    validity_status: cleanCompassLabel(policy.validity_status, '未知'),
    terms: normalizeGlossaryItems(policy.terms || []).slice(0, 4),
  }
}
