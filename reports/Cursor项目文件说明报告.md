# 农策微光项目文件说明报告

> 这份文档的目标是让 Cursor 或新接手的开发者，快速理解当前仓库里“哪些文件重要、它们各自负责什么、应该先看哪里”。

## 1. 项目一句话概述

农策微光是一个“面向农业政策理解、画像匹配、政策管理和风向标分析”的全栈项目：

- 后端：FastAPI + SQLAlchemy + MySQL
- 前端：Vue 3 + Vite + Element Plus
- 调度：APScheduler
- 外部能力：DeepSeek 模型、百度 OCR、湖北政策站点抓取

当前仓库已经具备：

- 用户/管理员双 Cookie 鉴权
- 画像、政策、匹配、聊天、审核、导入、爬虫、洞察、风向标基础链路
- 演示数据注入命令
- 基线检查命令

## 2. 先看哪些文件

如果是第一次接手，建议按这个顺序阅读：

1. `项目计划.md`
2. `docs/baseline-matrix.md`
3. `README.md`
4. `backend/app/main.py`
5. `backend/app/api/v1/*.py`
6. `backend/app/services/*.py`
7. `frontend/src/router/index.js`
8. `frontend/src/views/`

这样能先理解“项目要做什么”，再理解“后端接口怎么组织”，最后理解“前端页面怎么接这些接口”。

## 3. 仓库根目录说明

### 根目录关键文件

- `README.md`
  - 项目启动说明、后端/前端开发命令、P0 基线命令入口。
- `项目计划.md`
  - 当前 P0 基线冻结计划、阻塞项、12 功能任务表、验收清单。
- `软件需求规格说明书.md`
  - 需求说明书，偏产品和验收口径。
- `软件概要说明书.md`
  - 概要设计说明书，偏技术设计和模块边界。
- `启动前后端服务.txt`
  - 本地启动提示。

### 根目录主要子目录

- `backend/`
  - FastAPI 后端源码。
- `frontend/`
  - Vue 前端工程。
- `docs/`
  - 项目当前对齐文档、冻结矩阵、仓库核对文档。
- `reports/`
  - 导出报告、演示文件、辅助说明。

## 4. backend 目录说明

## 4.1 backend 顶层文件

- `backend/.env`
  - 本地真实环境配置。
  - 这里通常包含 MySQL DSN、DeepSeek Key、OCR Key 等敏感信息。
  - Cursor 阅读时可以参考字段名，但不要随意覆盖。
- `backend/.env.example`
  - 环境变量模板。
  - 新环境部署时应先看这个文件。
- `backend/requirements.txt`
  - Python 依赖列表。
- `backend/run.py`
  - Uvicorn 启动入口引用文件，本身很薄，只做 `app = create_app()`。
- `backend/dev.db`
  - SQLite 本地演示/回退数据库，不是当前联调权威库。

## 4.2 backend/app 总体职责

`backend/app/` 是后端核心目录，分层很清晰：

- `api/`
  - 路由层，定义 HTTP 接口。
- `core/`
  - 配置和全局基础能力。
- `db/`
  - SQLAlchemy engine / session / 建表 / schema 对齐。
- `models/`
  - ORM 模型，对应 MySQL 表。
- `schemas/`
  - 少量后端内部结构对象。
- `services/`
  - 业务逻辑层，是后端最重要的目录。
- `telemetry/`
  - 埋点与作业观测。
- `cli.py`
  - 命令行入口。
- `main.py`
  - FastAPI 应用装配入口。
- `scheduler.py`
  - 自动作业调度入口。

## 4.3 backend/app/main.py

- 文件：`backend/app/main.py`
- 作用：
  - 创建 FastAPI 应用
  - 注册所有 API 路由
  - 注入 CORS 中间件
  - 在开发环境下自动建表
  - 暴露健康检查接口
- 关键接口：
  - `/api/v1/health`
  - `/api/v1/health/dependencies`

这是理解“整个后端如何拼起来”的第一入口。

## 4.4 backend/app/cli.py

- 文件：`backend/app/cli.py`
- 作用：
  - 提供后端管理命令
- 当前重要命令：
  - `init-admin`
  - `seed-demo`
  - `verify-baseline`

这也是“演示数据注入”和“环境自检”的统一入口。

## 4.5 backend/app/scheduler.py

- 文件：`backend/app/scheduler.py`
- 作用：
  - 后台定时轮询任务
  - 负责消费待处理后台作业
  - 检查自动爬虫配置并自动创建 run

如果自动爬虫或后台任务中心有问题，这个文件需要重点看。

## 4.6 backend/app/core

- `backend/app/core/config.py`
  - 全局配置对象。
  - 所有环境变量都在这里定义，包括：
    - MySQL DSN
    - CORS
    - DeepSeek 配置
    - 百度 OCR 配置
    - 湖北爬虫源配置
  - 如果系统“读不到配置”或“新增配置项”，基本都改这里。

## 4.7 backend/app/db

- `backend/app/db/base.py`
  - SQLAlchemy Base 定义。
- `backend/app/db/session.py`
  - engine / sessionmaker / `get_db()`。
- `backend/app/db/init_db.py`
  - 导入所有模型并执行 `create_all()`。
- `backend/app/db/schema_align.py`
  - 对旧库做幂等补列，当前主要对齐认证表。

如果遇到“库表结构和 ORM 不一致”，先看这里。

## 4.8 backend/app/models

这些文件定义数据库表结构，是理解业务数据的关键。

### `backend/app/models/auth_models.py`

负责认证与限流相关表：

- `AdminUserORM`
- `EndUserORM`
- `AuthSessionORM`
- `AuthRefreshTokenORM`
- `RequestRateLimitORM`

如果登录、刷新、会话管理、限流出问题，看这个文件。

### `backend/app/models/business_models.py`

负责业务主表：

- `UserProfileORM`
  - 用户画像
- `PolicyORM`
  - 结构化政策
- `MatchRecordORM`
  - 政策匹配记录
- `ChatConversationORM`
  - 聊天会话
- `ChatMessageORM`
  - 聊天消息
- `CompassReportORM`
  - 风向标报告
- `CompassGlossaryORM`
  - 风向标词典
- `HubeiPolicyRawORM`
  - 从湖北站抓下来的原始政策内容

这是业务数据最核心的模型文件。

### `backend/app/models/admin_models.py`

负责运维、配置、作业、埋点：

- `SystemConfigORM`
  - 系统配置，目前 `auto_crawler` 存这里
- `AdminOperationRunORM`
  - 后台作业 run 主表
- `AdminOperationRunItemORM`
  - 后台作业子项
- `TelemetryEventORM`
  - 埋点日志
- `AutoCrawlerRunORM`
  - 自动爬虫运行记录

### `backend/app/models/policy_review_models.py`

负责政策审核工作台：

- `PolicyReviewTaskORM`
  - 待审核任务
- `PolicyReviewEventORM`
  - 审核历史事件

## 4.9 backend/app/api/v1

这里是 HTTP 路由层。每个文件通常对应一类业务。

### `auth_routes.py`

- 管理员鉴权接口
- 主要包括：
  - `/auth/login`
  - `/auth/me`
  - `/auth/refresh`
  - `/auth/logout-all`
  - `/auth/sessions`

### `user_auth_routes.py`

- 普通用户鉴权接口
- 路径以 `/user-auth/*` 为主

### `profile_routes.py`

- 用户画像管理
- 包括：
  - 创建画像
  - 查询画像
  - 更新画像
  - 获取推荐政策

### `policy_routes.py`

- 政策主业务接口，内容很多，是后端非常关键的一个文件：
  - 政策 CRUD
  - 文本编译
  - 手动爬虫
  - 自动爬虫配置
  - 文件解析
  - 匹配评估

### `policy_review_routes.py`

- 审核台接口：
  - 创建审核任务
  - 查询任务
  - 保存草稿
  - 审批
  - 驳回

### `chat_routes.py`

- 聊天会话和 SSE 输出
- 关键接口：
  - `/chat/conversations`
  - `/chat/stream`

### `insights_routes.py`

- 洞察页接口：
  - KPI 汇总
  - 趋势分析
  - 来源分布
  - 受众分布

### `compass_routes.py`

- 风向标接口：
  - 总览
  - 主题趋势
  - 报告列表/详情
  - 词典
  - 生成报告

### `admin_ops_routes.py`

- 后台作业中心接口：
  - 查询 run 列表
  - 查询 run 详情
  - 消费待处理任务
  - 重试失败任务
  - 查询 telemetry

### `deps.py`

- 路由依赖函数
- 提供当前管理员/当前用户鉴权依赖

### `schemas_*.py`

- 路由请求/响应模型
- 主要用于接口入参与出参校验

## 4.10 backend/app/services

这里是整个后端最值得重点阅读的目录。它承载业务逻辑。

### 核心业务服务

- `match_engine.py`
  - 条件树匹配引擎
  - 是政策匹配、推荐、体检卡的底层规则核心

- `policy_compile_service.py`
  - 政策文本编译入口
  - 对接模型 provider，将原文转成结构化条件树

- `review_queue_service.py`
  - 审核任务的创建、保存、审批、驳回
  - 审核流最核心服务

- `review_ai_service.py`
  - 调审核 AI，给审核台提供风险点、建议、证据

- `file_parse_service.py`
  - 处理 DOCX / PDF 解析
  - 扫描 PDF 文本不足时会尝试走 OCR

- `crawler_service.py`
  - 真实湖北政策源抓取逻辑
  - 解析文章链接、抓正文、写入原始表、创建审核任务

- `compass_service.py`
  - 根据政策和原始数据生成风向标结构化信号
  - 再调用模型生成报告与词典

- `insights_service.py`
  - 洞察页数据统计
  - 提供 KPI、趋势、来源、受众统计

### 基础能力服务

- `model_provider.py`
  - DeepSeek 模型统一适配层
  - 所有“文本编译 / 审核 AI / 风向标生成”都复用它

- `ocr_service.py`
  - 百度 OCR 统一适配层

- `dependency_service.py`
  - 汇总 MySQL / 模型 / OCR / 爬虫依赖检查结果

- `admin_operation_service.py`
  - 后台作业 run 的创建、消费、失败回写

- `demo_seed_service.py`
  - 演示数据注入逻辑
  - 包括账号、画像、政策、聊天、审核、风向标、样本文件

- `passwords.py`
  - 密码哈希与校验

- `tokens.py`
  - JWT access/refresh token 的签发、校验、哈希

## 4.11 backend/app/schemas

- `backend/app/schemas/policy.py`
  - 定义后端内部使用的政策结构对象
  - 包括条件树节点的 dataclass 形式

这个文件不是 HTTP schema，而是服务内部“政策结构化”的基础表示。

## 4.12 backend/app/telemetry

- `backend/app/telemetry/writer.py`
  - 负责埋点写入
  - 提供 `emit_event` 和 `telemetry_span`

如果需要给作业、爬虫、解析增加埋点，改这里或调用这里。

## 5. frontend 目录说明

## 5.1 frontend 顶层文件

- `frontend/package.json`
  - 前端依赖和脚本
- `frontend/vite.config.js`
  - Vite 配置
- `frontend/.env.development`
  - 前端 API 基地址配置

## 5.2 frontend/src 结构

- `main.js`
  - Vue 入口
- `App.vue`
  - 顶层组件壳
- `style.css`
  - 全局样式
- `router/index.js`
  - 所有路由注册与管理员鉴权守卫
- `api/client.js`
  - 前端统一请求封装
  - 封装了：
    - `fetchJson`
    - Cookie 请求
    - 401 自动 refresh

## 5.3 frontend/src/services

- `services/authSession.js`
  - 管理员/用户会话状态探测与登录退出逻辑

## 5.4 frontend/src/utils

- `utils/safeRedirect.js`
  - 处理登录后安全跳转，避免开放重定向

## 5.5 frontend/src/views

### 普通用户侧页面

- `HomePage.vue`
  - 首页
- `LoginPage.vue`
  - 普通用户登录
- `RegisterPage.vue`
  - 普通用户注册
- `SessionsPage.vue`
  - 普通用户会话管理
- `ChatPage.vue`
  - 用户侧核心工作台
  - 包含画像、聊天、匹配结果展示
- `InsightsPage.vue`
  - 洞察页
- `CompassPage.vue`
  - 风向标页

### 管理端页面

- `admin/AdminLayout.vue`
  - 管理端整体布局壳
- `admin/AdminDashboard.vue`
  - 管理端首页
- `admin/AdminLogin.vue`
  - 管理员登录页
- `admin/AdminPolicies.vue`
  - 政策列表
- `admin/AdminPolicyNew.vue`
  - 新增政策 + 文本编译
- `admin/AdminPolicyEdit.vue`
  - 编辑政策
- `admin/AdminPolicyImport.vue`
  - 文件导入 / 手动爬虫入口
- `admin/AdminPolicyReview.vue`
  - 审核台
- `admin/AdminTasks.vue`
  - 后台任务中心
- `admin/AdminAutoCrawler.vue`
  - 自动爬虫配置页
- `admin/AdminSessions.vue`
  - 管理员会话页

## 5.6 frontend/src/assets

- `hero.png`
- `logo_icon.png`
- `logo_with_text.png`

这些是页面展示图片资源，不是业务逻辑文件。

## 5.7 可以忽略的前端文件

- `components/HelloWorld.vue`
  - Vite 初始化残留文件，目前不是核心业务文件。
- `assets/vite.svg`
- `assets/vue.svg`
  - 模板残留资源，业务价值很低。

## 6. docs 目录说明

- `docs/baseline-matrix.md`
  - 当前 P0 冻结矩阵
  - 说明功能、页面、API、表怎么对应
- `docs/repo-audit.md`
  - 当前仓库状态核对文档
  - 适合快速了解“这个仓库现在已经有什么、还差什么”

## 7. reports 目录说明

- `reports/管理端核心前端UI代码导出.md`
  - 之前导出的管理端 UI 相关说明
- `reports/demo-files/`
  - 演示导入文件样本
  - 包含：
    - 2 个 docx
    - 2 个 pdf
- `reports/Cursor项目文件说明报告.md`
  - 当前这份文档

## 8. 哪些文件是“源码”，哪些是“生成物”

### 建议重点维护的源码

- `backend/app/**`
- `frontend/src/**`
- `README.md`
- `项目计划.md`
- `docs/**`

### 本地环境文件

- `backend/.env`
- `frontend/.env.development`

### 本地数据库或演示产物

- `backend/dev.db`
- `reports/demo-files/*`

### 可以忽略的缓存/构建产物

- `backend/**/__pycache__/*`
- `frontend/dist/*`
- `frontend/node_modules/*`

## 9. 关键业务链路和对应文件

## 9.1 登录链路

- 后端：
  - `auth_routes.py`
  - `user_auth_routes.py`
  - `auth_models.py`
  - `tokens.py`
  - `passwords.py`
- 前端：
  - `services/authSession.js`
  - `api/client.js`
  - `LoginPage.vue`
  - `RegisterPage.vue`
  - `admin/AdminLogin.vue`

## 9.2 画像与匹配链路

- 后端：
  - `profile_routes.py`
  - `policy_routes.py`
  - `match_engine.py`
  - `business_models.py`
- 前端：
  - `ChatPage.vue`

## 9.3 文件导入与审核链路

- 后端：
  - `policy_routes.py`
  - `file_parse_service.py`
  - `ocr_service.py`
  - `review_queue_service.py`
  - `policy_review_routes.py`
- 前端：
  - `admin/AdminPolicyImport.vue`
  - `admin/AdminPolicyReview.vue`
  - `admin/AdminTasks.vue`

## 9.4 爬虫链路

- 后端：
  - `crawler_service.py`
  - `policy_routes.py`
  - `admin_operation_service.py`
  - `scheduler.py`
  - `admin_models.py`
  - `business_models.py`
- 前端：
  - `admin/AdminPolicyImport.vue`
  - `admin/AdminAutoCrawler.vue`
  - `admin/AdminTasks.vue`

## 9.5 风向标链路

- 后端：
  - `compass_routes.py`
  - `compass_service.py`
  - `model_provider.py`
- 前端：
  - `CompassPage.vue`

## 9.6 洞察链路

- 后端：
  - `insights_routes.py`
  - `insights_service.py`
- 前端：
  - `InsightsPage.vue`

## 10. Cursor 接手时的建议提示词

如果要让 Cursor 快速进入状态，可以先让它阅读：

1. `项目计划.md`
2. `docs/baseline-matrix.md`
3. `backend/app/main.py`
4. `backend/app/api/v1/policy_routes.py`
5. `backend/app/services/`
6. `frontend/src/router/index.js`
7. `frontend/src/views/admin/`

然后给它一个明确任务，例如：

```md
请先阅读：
- 项目计划.md
- docs/baseline-matrix.md
- backend/app/main.py
- backend/app/api/v1/policy_routes.py
- backend/app/services/*
- frontend/src/router/index.js

目标：
- 理解当前系统的模块边界
- 不要改动路由命名
- 优先保持 MySQL 基线兼容
```

## 11. 最后总结

这个仓库当前最重要的理解方式不是“逐个页面看”，而是按下面这条主线理解：

1. 文档定义目标：`项目计划.md`、`docs/baseline-matrix.md`
2. 后端装配入口：`backend/app/main.py`
3. 路由层承接 HTTP：`backend/app/api/v1/*.py`
4. 服务层承接业务：`backend/app/services/*.py`
5. ORM 层承接数据：`backend/app/models/*.py`
6. 前端通过 `frontend/src/api/client.js` 和 `frontend/src/views/*` 消费这些接口

如果 Cursor 能看懂这 6 层，它就基本能顺利参与后续开发。
