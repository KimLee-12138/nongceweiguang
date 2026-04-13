# 农策微光 P0 基线矩阵

本文档以当前代码实现为准，用于冻结 P0 的页面、接口、数据表和验收口径。

## 1. P0 冻结结论

- API 前缀固定为 `/api/v1`
- 联调数据库固定为 MySQL
- 普通用户与管理员继续采用 Cookie 会话隔离
- 匹配接口冻结为 `/policies/evaluate` 与 `/policies/{policy_id}/match-for-profile/{profile_id}`
- 聊天 SSE 事件冻结为 `message_meta`、`policy_report`、`content`、`content_done`
- 联调与演示前统一使用：
  - `GET /api/v1/health`
  - `GET /api/v1/health/dependencies?live=true`
  - `python -m app.cli verify-baseline --live`

## 2. 功能 → 页面 / API / 数据表

| 功能 | 页面 | API | 核心表 |
| --- | --- | --- | --- |
| 农户画像管理 | `/chat` | `POST/GET/PUT /profiles*` | `end_users` `user_profiles` `match_records` |
| 政策智能匹配 | `/chat` | `POST /policies/evaluate` `POST /policies/{policy_id}/match-for-profile/{profile_id}` | `policies` `match_records` |
| 对话式政策解读 | `/chat` | `GET/POST /chat/conversations*` `POST /chat/stream` | `chat_conversations` `chat_messages` |
| 相关推荐政策 | `/chat` | `GET /profiles/{id}/suggested-policies` | `policies` `user_profiles` |
| 政策洞察展示 | `/insights` | `GET /insights/kpi-summary` `GET /insights/trend-analysis` `GET /insights/source-distribution` `GET /insights/audience-distribution` | `policies` `hubei_policies_raw` |
| 管理员登录与鉴权 | `/admin/login` `/admin/sessions` | `/auth/login` `/auth/me` `/auth/refresh` `/auth/logout-all` `/auth/sessions*` | `admin_users` `auth_sessions` `auth_refresh_tokens` `request_rate_limits` |
| 结构化政策管理 | `/admin/policies` `/admin/policies/new` `/admin/policies/:id/edit` | `POST/GET/PUT/DELETE /policies*` | `policies` |
| 政策文本编译 | `/admin/policies/new` | `POST /policies/compile-text` | `policies` |
| 文件解析与批量导入 | `/admin/policies/import` `/admin/tasks` | `POST /policies/parse-file` `POST /policies/parse-file/jobs` | `admin_operation_runs` `admin_operation_run_items` `policy_review_tasks` |
| 手动政策爬虫导入 | `/admin/policies/import` `/admin/tasks` `/admin/policies/review` | `GET /policies/crawl/sources` `POST /policies/crawl` | `hubei_policies_raw` `policy_review_tasks` `admin_operation_runs` |
| 自动爬虫配置与运行记录 | `/admin/policies/auto-crawler` `/admin/tasks` | `GET/PUT /policies/auto-crawler/config` `POST /policies/auto-crawler/run-now` | `system_config` `auto_crawler_runs` `admin_operation_runs` |
| 政策风向标与智库词典 | `/compass` | `GET /compass/overview` `GET /compass/theme-trends` `GET /compass/reports*` `GET /compass/glossary` `POST /compass/generate` | `compass_reports` `compass_glossary` `hubei_policies_raw` `policies` |

## 3. 数据表冻结清单

| 分组 | 表 |
| --- | --- |
| 鉴权 | `admin_users` `end_users` `auth_sessions` `auth_refresh_tokens` `request_rate_limits` |
| 业务 | `user_profiles` `policies` `match_records` `chat_conversations` `chat_messages` |
| 审核与原始数据 | `policy_review_tasks` `policy_review_events` `hubei_policies_raw` |
| 风向标与洞察 | `compass_reports` `compass_glossary` |
| 作业与配置 | `system_config` `admin_operation_runs` `admin_operation_run_items` `auto_crawler_runs` `telemetry_events` |

## 4. P0 验收口径

- 管理员登录成功后可访问政策管理、导入、任务中心、自动爬虫。
- 用户可注册/登录，创建画像，查看推荐，发起聊天 SSE。
- 演示数据通过 `python -m app.cli seed-demo --workspace-root ..` 注入 MySQL，并生成 4 个本地文件样本。
- 外部依赖仅当 `verify-baseline --live` 中 `mysql/model/ocr/crawler` 四项均为 `ok=true` 时，才算 P0 真正完成。
