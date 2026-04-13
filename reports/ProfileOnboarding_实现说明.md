# ProfileOnboarding 实现说明

## 已落地文件

- [backend/app/services/profile_onboarding_service.py](c:/Users/22067/Desktop/农策微光/backend/app/services/profile_onboarding_service.py)：`build_profile_from_answers`、`refine_profile_with_model`（DeepSeek）、`refine_onboarding`（无密钥则 `source=local`）
- [backend/app/api/v1/schemas_profiles.py](c:/Users/22067/Desktop/农策微光/backend/app/api/v1/schemas_profiles.py)：`OnboardingRefineIn`、`ProfileRefineOut`
- [backend/app/api/v1/profile_routes.py](c:/Users/22067/Desktop/农策微光/backend/app/api/v1/profile_routes.py)：`POST /profiles/onboarding/refine`
- [frontend/src/components/ProfileOnboarding.vue](c:/Users/22067/Desktop/农策微光/frontend/src/components/ProfileOnboarding.vue)：20 题步进、单选 300ms 自动下一题、多选/文本用「继续」、收尾至少 1.5s、可选调用 refine 接口
- [frontend/src/views/ChatPage.vue](c:/Users/22067/Desktop/农策微光/frontend/src/views/ChatPage.vue)：`问卷式创建` 弹窗挂载问卷，完成后 `POST /profiles` 创建画像

辅助副本（可从 md 再提取源码）：`reports/profile_onboarding_service_embed.md`、`reports/profile_onboarding_vue_a.md`。
