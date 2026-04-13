from pathlib import Path
p = Path("frontend/src/views/ChatPage.vue")
t = p.read_text(encoding="utf-8")
if "ProfileOnboarding" in t:
    raise SystemExit(0)
t = t.replace(
    "import { getUserMe } from '../services/authSession'\n",
    "import { getUserMe } from '../services/authSession'\nimport ProfileOnboarding from '../components/ProfileOnboarding.vue'\n",
    1,
)
insert = "const showOnboarding = ref(false)\n\n"
t = t.replace("const streaming = ref(false)\n", "const streaming = ref(false)\n" + insert, 1)
fn = '''
async function onOnboardingComplete(payload) {
  const profile = payload.profile
  const p = await api.withUser(() => api.post('/profiles', profile))
  ElMessage.success(`问卷画像已创建 #${p.id}${payload.source === 'deepseek' ? '（已智能归一）' : ''}`)
  showOnboarding.value = false
  await loadProfiles()
  selectedProfileId.value = p.id
}
'''
t = t.replace("async function matchNow() {", fn + "\nasync function matchNow() {", 1)
panel = '''          <el-form-item>
            <el-button type="primary" @click="createProfile">创建画像</el-button>
            <el-button @click="loadProfiles">刷新</el-button>
            <el-button type="success" plain @click="showOnboarding = true">问卷式创建</el-button>
          </el-form-item>'''
t = t.replace(
    '''          <el-form-item>
            <el-button type="primary" @click="createProfile">创建画像</el-button>
            <el-button @click="loadProfiles">刷新</el-button>
          </el-form-item>''',
    panel,
    1,
)
dialog = '''
    <el-dialog v-model="showOnboarding" title="首次画像问卷" width="min(960px, 96vw)" destroy-on-close align-center>
      <ProfileOnboarding
        @complete="onOnboardingComplete"
        @cancel="showOnboarding = false"
        @skip="showOnboarding = false"
      />
    </el-dialog>
'''
t = t.replace("</template>", dialog + "\n</template>", 1)
p.write_text(t, encoding="utf-8")
print("ok")
