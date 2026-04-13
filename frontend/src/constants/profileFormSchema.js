export const PROFILE_OPTION_SETS = {
  subjectTypes: [
    { value: '种植户', label: '种植户' },
    { value: '家庭农场', label: '家庭农场' },
    { value: '合作社', label: '合作社' },
    { value: '企业', label: '企业' },
  ],
  irrigation: [
    { value: '漫灌', label: '漫灌' },
    { value: '滴灌', label: '滴灌 / 微灌' },
    { value: '喷灌', label: '喷灌' },
    { value: '靠天', label: '自然靠天' },
  ],
  counties: [
    { value: '洪湖市', label: '洪湖市' },
    { value: '荆州市', label: '荆州市' },
    { value: '襄阳市', label: '襄阳市' },
    { value: '宜昌市', label: '宜昌市' },
    { value: '黄冈市', label: '黄冈市' },
    { value: '随州市', label: '随州市' },
    { value: '武汉市', label: '武汉市' },
    { value: '省内其他', label: '省内其他' },
    { value: '省外', label: '省外' },
  ],
  industries: [
    { value: '粮油作物', label: '粮油作物' },
    { value: '蔬菜瓜果', label: '蔬菜瓜果' },
    { value: '林果', label: '林果' },
    { value: '畜禽', label: '畜禽' },
    { value: '水产', label: '水产' },
    { value: '食用菌', label: '食用菌' },
    { value: '中药材', label: '中药材' },
    { value: '混合', label: '混合多种' },
  ],
  greenCertStatus: [
    { value: 'certified', label: '已获认证' },
    { value: 'pending', label: '正在申请' },
    { value: 'none', label: '暂无认证' },
  ],
  fruits: [
    { value: '柑橘', label: '柑橘类' },
    { value: '苹果梨樱桃', label: '苹果 / 梨 / 桃等' },
    { value: '其他', label: '其他林果' },
    { value: '不涉及', label: '不涉及' },
  ],
  coopLevels: [
    { value: '省级', label: '省级示范' },
    { value: '市级', label: '市级示范' },
    { value: '县级', label: '县级规范社' },
    { value: '未获评', label: '未获评' },
    { value: '不适用', label: '不适用' },
  ],
  operatingYears: [
    { value: 'lt1', label: '1 年以内' },
    { value: 'y1_3', label: '1-3 年' },
    { value: 'y3_10', label: '3-10 年' },
    { value: 'gt10', label: '10 年以上' },
  ],
  agriInsurance: [
    { value: 'full', label: '已投保主要品类' },
    { value: 'partial', label: '部分投保' },
    { value: 'none', label: '尚未投保' },
    { value: 'unknown', label: '不了解' },
  ],
  mechanization: [
    { value: 'low', label: '以小型农机为主' },
    { value: 'medium', label: '大中型农机较齐全' },
    { value: 'facility_heavy', label: '设施农业占比较高' },
    { value: 'minimal', label: '机械化较少' },
  ],
  landTenure: [
    { value: 'own_contract', label: '自家承包地为主' },
    { value: 'leased', label: '流转土地为主' },
    { value: 'mixed', label: '承包 + 流转兼有' },
    { value: 'park', label: '以设施园区为主' },
  ],
  employees: [
    { value: '0', label: '基本不雇工' },
    { value: '1_5', label: '1-5 人' },
    { value: '6_20', label: '6-20 人' },
    { value: 'gt20', label: '20 人以上' },
  ],
  loanHistory: [
    { value: 'active', label: '有，且持续' },
    { value: 'once', label: '有过' },
    { value: 'none', label: '没有' },
    { value: 'unknown', label: '不了解' },
  ],
  crops: [
    { value: 'grain', label: '粮食作物' },
    { value: 'cash', label: '经济作物' },
    { value: 'veg_fruit', label: '蔬菜瓜果' },
    { value: 'aquaculture', label: '水产养殖' },
    { value: 'livestock', label: '畜禽养殖' },
  ],
  salesChannels: [
    { value: 'order', label: '订单农业 / 企业收购' },
    { value: 'wholesale', label: '批发商 / 经纪人' },
    { value: 'retail', label: '本地零售' },
    { value: 'ecommerce', label: '电商与直播' },
    { value: 'processing', label: '初加工后再售' },
  ],
  supportFocus: [
    { value: 'tech', label: '种养殖技术' },
    { value: 'water_smart', label: '节水与智能设施' },
    { value: 'brand_cert', label: '品牌与认证' },
    { value: 'subsidy_compliance', label: '补贴申报与合规' },
    { value: 'market', label: '产销对接' },
  ],
}

function arrayValue(value) {
  return Array.isArray(value) ? [...value] : []
}

export function createProfileEditorForm(profile = null) {
  const extra = profile?.extra_data || {}
  return {
    name: profile?.name ?? '我的画像',
    type: profile?.type ?? '种植户',
    area: profile?.area ?? 10,
    green_cert: Boolean(profile?.green_cert),
    irrigation: profile?.irrigation ?? '漫灌',
    county: extra.county ?? '省内其他',
    industry: extra.industry ?? '混合',
    operating_years: extra.operating_years ?? 'y1_3',
    land_tenure: extra.land_tenure ?? 'mixed',
    green_cert_status: extra.green_cert_status ?? (profile?.green_cert ? 'certified' : 'none'),
    mechanization: extra.mechanization ?? 'medium',
    grain_focus: Boolean(extra.grain_focus ?? false),
    fruit: extra.fruit ?? '不涉及',
    crops: arrayValue(extra.crops),
    coop_level: extra.coop_level ?? '不适用',
    sales_channels: arrayValue(extra.sales_channels),
    employees: extra.employees ?? '0',
    loan_history: extra.loan_history ?? 'unknown',
    agri_insurance: extra.agri_insurance ?? 'unknown',
    support_focus: arrayValue(extra.support_focus),
    user_notes: extra.user_notes ?? '',
  }
}

export function buildProfilePayloadFromForm(form) {
  const greenCertStatus = form.green_cert ? (form.green_cert_status === 'none' ? 'certified' : form.green_cert_status) : 'none'
  const industry = form.industry || '混合'

  return {
    name: (form.name || '').trim(),
    type: form.type || '种植户',
    area: Number(form.area) || 0,
    green_cert: Boolean(form.green_cert),
    irrigation: form.irrigation || '漫灌',
    extra_data: {
      county: form.county || '省内其他',
      industry,
      operating_years: form.operating_years || 'y1_3',
      land_tenure: form.land_tenure || 'mixed',
      green_cert_status: greenCertStatus,
      mechanization: form.mechanization || 'medium',
      grain_focus: industry === '粮油作物' ? true : Boolean(form.grain_focus),
      fruit: form.fruit || '不涉及',
      crops: arrayValue(form.crops),
      coop_level: form.coop_level || '不适用',
      sales_channels: arrayValue(form.sales_channels),
      employees: form.employees || '0',
      loan_history: form.loan_history || 'unknown',
      agri_insurance: form.agri_insurance || 'unknown',
      support_focus: arrayValue(form.support_focus),
      user_notes: (form.user_notes || '').trim(),
    },
  }
}
