```python
from pathlib import Path

p = Path("frontend/src/views/ChatPage.vue")
t = p.read_text(encoding="utf-8")
bad = """      <el-card class="panel">
        <template #header>画像
    <el-dialog v-model="showOnboarding" title="首次画像问卷" width="min(960px, 96vw)" destroy-on-close align-center>
      <ProfileOnboarding
        @complete="onOnboardingComplete"
        @cancel="showOnboarding = false"
        @skip="showOnboarding = false"
      />
    </el-dialog>

</template>
"""
good = """      <el-card class="panel">
        <template #header>画像</template>
"""
if bad not in t:
    raise SystemExit("bad block not found")
t = t.replace(bad, good, 1)
dialog = """
    <el-dialog v-model="showOnboarding" title="首次画像问卷" width="min(960px, 96vw)" destroy-on-close align-center>
      <ProfileOnboarding
        @complete="onOnboardingComplete"
        @cancel="showOnboarding = false"
        @skip="showOnboarding = false"
      />
    </el-dialog>
"""
needle = "    </div>\n  </div>\n</template>"
if needle not in t:
    raise SystemExit("needle not found")
t = t.replace(needle, "    </div>" + dialog + "\n  </div>\n</template>", 1)
p.write_text(t, encoding="utf-8")
print("fixed")
```
