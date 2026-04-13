<script setup>
import { computed, ref, watch } from 'vue'

import { PROFILE_OPTION_SETS, buildProfilePayloadFromForm, createProfileEditorForm } from '../../constants/profileFormSchema'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  profile: { type: Object, default: null },
  submitLoading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit', 'go-onboarding'])

const form = ref(createProfileEditorForm())

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const hasProfile = computed(() => Boolean(props.profile?.id))
const titleText = computed(() => (hasProfile.value ? '管理画像' : '还没有画像'))
const grainFocusDisabled = computed(() => form.value.industry === '粮油作物')

watch(
  () => [props.modelValue, props.profile],
  () => {
    if (!props.modelValue) return
    form.value = createProfileEditorForm(props.profile)
  },
  { immediate: true },
)

watch(
  () => form.value.green_cert,
  (enabled) => {
    if (!enabled) form.value.green_cert_status = 'none'
    else if (form.value.green_cert_status === 'none') form.value.green_cert_status = 'certified'
  },
)

watch(
  () => form.value.industry,
  (industry) => {
    if (industry === '粮油作物') form.value.grain_focus = true
  },
)

function onSubmit() {
  emit('submit', { ...buildProfilePayloadFromForm(form.value), id: props.profile?.id })
}

function goOnboarding() {
  emit('go-onboarding')
}
</script>

<template>
  <el-dialog v-model="visible" :title="titleText" width="min(980px, 96vw)" top="4vh" destroy-on-close class="profile-editor-dialog">
    <template v-if="hasProfile">
      <div class="editor-shell">
        <div class="editor-toolbar">
          <div>
            <h3 class="editor-heading">查看并微调你的完整画像</h3>
            <p class="editor-subheading">这里展示问卷沉淀的经营情况，你可以直接修改并保存，不必重新走完整问卷。</p>
          </div>
          <el-button plain @click="goOnboarding">重新问卷创建</el-button>
        </div>

        <el-form label-position="top" size="default" class="editor-form">
          <section class="editor-section">
            <div class="editor-section__head">
              <h4>基础经营</h4>
              <p>经营主体、规模和区域等基础信息。</p>
            </div>
            <div class="editor-grid editor-grid--2">
              <el-form-item label="画像名称">
                <el-input v-model="form.name" maxlength="128" placeholder="例如：洪湖稻田基地" />
              </el-form-item>
              <el-form-item label="主体类型">
                <el-select v-model="form.type" placeholder="选择主体类型">
                  <el-option v-for="option in PROFILE_OPTION_SETS.subjectTypes" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="经营面积（亩）">
                <el-input-number v-model="form.area" :min="0" :precision="0" style="width: 100%" />
              </el-form-item>
              <el-form-item label="所在地区">
                <el-select v-model="form.county" placeholder="选择地区">
                  <el-option v-for="option in PROFILE_OPTION_SETS.counties" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="主产业方向">
                <el-select v-model="form.industry" placeholder="选择产业方向">
                  <el-option v-for="option in PROFILE_OPTION_SETS.industries" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="经营年限">
                <el-select v-model="form.operating_years" placeholder="选择经营年限">
                  <el-option v-for="option in PROFILE_OPTION_SETS.operatingYears" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="用地来源" class="editor-grid__span-2">
                <el-radio-group v-model="form.land_tenure">
                  <el-radio-button v-for="option in PROFILE_OPTION_SETS.landTenure" :key="option.value" :label="option.value">
                    {{ option.label }}
                  </el-radio-button>
                </el-radio-group>
              </el-form-item>
            </div>
          </section>

          <section class="editor-section">
            <div class="editor-section__head">
              <h4>生产条件</h4>
              <p>灌溉、认证、机械化与主导作物情况。</p>
            </div>
            <div class="editor-grid editor-grid--2">
              <el-form-item label="灌溉方式">
                <el-select v-model="form.irrigation" placeholder="选择灌溉方式">
                  <el-option v-for="option in PROFILE_OPTION_SETS.irrigation" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="绿色认证">
                <el-switch v-model="form.green_cert" />
              </el-form-item>
              <el-form-item label="绿色认证状态">
                <el-select v-model="form.green_cert_status" :disabled="!form.green_cert" placeholder="选择认证状态">
                  <el-option v-for="option in PROFILE_OPTION_SETS.greenCertStatus" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="机械化程度">
                <el-select v-model="form.mechanization" placeholder="选择机械化程度">
                  <el-option v-for="option in PROFILE_OPTION_SETS.mechanization" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="粮油是否为收入主导">
                <el-switch v-model="form.grain_focus" :disabled="grainFocusDisabled" />
              </el-form-item>
              <el-form-item label="林果类型">
                <el-select v-model="form.fruit" placeholder="选择林果类型">
                  <el-option v-for="option in PROFILE_OPTION_SETS.fruits" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
            </div>
          </section>

          <section class="editor-section">
            <div class="editor-section__head">
              <h4>经营能力</h4>
              <p>人力、销售、金融与保险相关情况。</p>
            </div>
            <div class="editor-grid editor-grid--2">
              <el-form-item label="常年雇工人数">
                <el-select v-model="form.employees" placeholder="选择雇工人数">
                  <el-option v-for="option in PROFILE_OPTION_SETS.employees" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="贷款 / 贴息记录">
                <el-select v-model="form.loan_history" placeholder="选择贷款情况">
                  <el-option v-for="option in PROFILE_OPTION_SETS.loanHistory" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="农业保险覆盖">
                <el-select v-model="form.agri_insurance" placeholder="选择保险情况">
                  <el-option v-for="option in PROFILE_OPTION_SETS.agriInsurance" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="合作社等级">
                <el-select v-model="form.coop_level" placeholder="选择合作社等级">
                  <el-option v-for="option in PROFILE_OPTION_SETS.coopLevels" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </el-form-item>
              <el-form-item label="销售渠道" class="editor-grid__span-2">
                <el-checkbox-group v-model="form.sales_channels" class="tag-grid">
                  <el-checkbox v-for="option in PROFILE_OPTION_SETS.salesChannels" :key="option.value" :label="option.value">
                    {{ option.label }}
                  </el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </div>
          </section>

          <section class="editor-section">
            <div class="editor-section__head">
              <h4>偏好与补充</h4>
              <p>你关心的支持方向和补充经营说明。</p>
            </div>
            <div class="editor-grid editor-grid--2">
              <el-form-item label="经营品类" class="editor-grid__span-2">
                <el-checkbox-group v-model="form.crops" class="tag-grid">
                  <el-checkbox v-for="option in PROFILE_OPTION_SETS.crops" :key="option.value" :label="option.value">
                    {{ option.label }}
                  </el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item label="关注支持方向" class="editor-grid__span-2">
                <el-checkbox-group v-model="form.support_focus" class="tag-grid">
                  <el-checkbox v-for="option in PROFILE_OPTION_SETS.supportFocus" :key="option.value" :label="option.value">
                    {{ option.label }}
                  </el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item label="补充说明" class="editor-grid__span-2">
                <el-input v-model="form.user_notes" type="textarea" :rows="4" maxlength="200" show-word-limit placeholder="可补充经营特点、规划目标、当前难点等" />
              </el-form-item>
            </div>
          </section>
        </el-form>
      </div>
    </template>

    <template v-else>
      <div class="empty-state">
        <p class="empty-state__title">先完成问卷式创建</p>
        <p class="empty-state__desc">当前还没有可编辑的画像。先通过问卷生成你的唯一画像，之后就能回到这里查看完整情况并持续微调。</p>
      </div>
    </template>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button v-if="hasProfile" @click="goOnboarding">重新问卷创建</el-button>
      <el-button v-if="hasProfile" type="primary" :loading="submitLoading" @click="onSubmit">保存画像</el-button>
      <el-button v-else type="primary" @click="goOnboarding">去问卷创建</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.editor-shell {
  max-height: min(72vh, 780px);
  overflow: auto;
  padding-right: 0.35rem;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1.1rem;
}

.editor-heading {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 650;
  color: #151917;
}

.editor-subheading {
  margin: 0.45rem 0 0;
  font-size: 0.88rem;
  line-height: 1.65;
  color: rgba(17, 20, 18, 0.58);
}

.editor-form {
  display: grid;
  gap: 1rem;
}

.editor-section {
  padding: 1rem 1rem 0.25rem;
  border: 1px solid rgba(17, 20, 18, 0.08);
  border-radius: 1rem;
  background: rgba(248, 249, 246, 0.72);
}

.editor-section__head h4 {
  margin: 0;
  font-size: 0.98rem;
  color: #151917;
}

.editor-section__head p {
  margin: 0.35rem 0 1rem;
  font-size: 0.82rem;
  color: rgba(17, 20, 18, 0.54);
}

.editor-grid {
  display: grid;
  gap: 0 1rem;
}

.editor-grid--2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.editor-grid__span-2 {
  grid-column: 1 / -1;
}

.tag-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem 1rem;
}

.empty-state {
  padding: 0.25rem 0 0.5rem;
}

.empty-state__title {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 650;
  color: #151917;
}

.empty-state__desc {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.7;
  color: rgba(17, 20, 18, 0.62);
}

@media (max-width: 760px) {
  .editor-toolbar {
    flex-direction: column;
  }

  .editor-grid--2,
  .tag-grid {
    grid-template-columns: 1fr;
  }
}
</style>
