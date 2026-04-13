# 农策微光

农策微光是一个面向涉农政策场景的全栈系统，覆盖政策采集、结构化审核、画像匹配、对话解读、洞察看板与风向展示。

本项目包含用户端与管理端两套核心工作流：

- 用户端：注册/登录、唯一画像、政策对话、政策匹配、会话管理
- 管理端：政策导入、爬虫采集、审核入库、任务中心、自动爬虫
- 大屏能力：政策洞察与政策风向可视化

---

## 1. 技术栈与目录结构

### 1.1 技术栈

- 前端：Vue 3、Vite、Vue Router、Element Plus、ECharts
- 后端：FastAPI、SQLAlchemy、Pydantic、APScheduler
- 数据：MySQL（推荐）/ SQLite（开发回退）
- 文档解析：python-docx、pypdf
- 鉴权：JWT + Session + Refresh Token（用户/管理员隔离）

### 1.2 目录结构

```text
.
├─ frontend/                  # Vue 前端
│  ├─ src/views/              # 页面（首页/聊天/洞察/风向/管理）
│  ├─ src/components/          # 组件（聊天工作台、图表、表单等）
│  ├─ src/api/                 # API 客户端与会话刷新逻辑
│  └─ vite.config.js
├─ backend/                   # FastAPI 后端
│  ├─ app/api/v1/              # 路由层（auth/chat/policies/insights 等）
│  ├─ app/services/            # 业务服务（匹配引擎/爬虫/审核/AI 集成）
│  ├─ app/models/              # ORM 模型
│  ├─ app/db/                  # 数据库连接、建表、schema 补齐
│  ├─ app/cli.py               # init-admin、seed-demo、verify-baseline
│  └─ requirements.txt
└─ docs/                      # 项目说明、基线矩阵、审查报告
```

> 说明：`frontend/README.md` 仍为 Vite 模板内容，项目文档以本文件为准。

---

## 2. 本地开发快速启动

## 2.1 后端启动（FastAPI）

### 步骤 1：安装依赖

```bash
cd backend
python -m pip install -r requirements.txt
```

### 步骤 2：配置环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

重点变量：

- `ENV=development`
- `MYSQL_DSN=mysql+pymysql://user:pass@127.0.0.1:3306/db?charset=utf8mb4`
- `JWT_SECRET_KEY=请替换为高强度随机字符串`
- `CORS_ALLOW_ORIGINS=http://127.0.0.1:5173`
- `SCHEMA_AUTO_PATCH=true`

开发期也可临时使用 SQLite：

```env
MYSQL_DSN=sqlite:///./dev.db
```

### 步骤 3：初始化管理员

```bash
python -m app.cli init-admin --username admin --password admin123
```

### 步骤 4：写入联调演示数据（推荐）

```bash
python -m app.cli seed-demo --workspace-root ..
```

### 步骤 5：启动后端 API

```bash
uvicorn run:app --host 127.0.0.1 --port 8000
```

### 步骤 6：（可选）启动调度器

```bash
python -m app.scheduler
```

### 步骤 7：执行基线校验

```bash
python -m app.cli verify-baseline
```

## 2.2 前端启动（Vue 3 + Vite）

```bash
cd frontend
npm install
npm run dev
```

开发期通过 Vite 代理访问后端：

- 默认 `VITE_API_BASE_URL=/api/v1`
- `vite.config.js` 将 `/api` 代理到 `http://127.0.0.1:8000`

构建与预览：

```bash
npm run build
npm run preview
```

若用静态部署/preview，请设置绝对 API 地址，不要依赖开发代理。

---

## 3. 主要功能入口

### 3.1 用户端

- `/login`：用户登录
- `/register`：用户注册
- `/chat`：政策对话工作台（需登录）
- `/onboarding/profile`：画像问卷（需登录）
- `/sessions`：用户会话管理（需登录）

### 3.2 展示页

- `/insights`：政策洞察页
- `/compass` 或 `/policy-compass`：政策风向大屏

### 3.3 管理端

- `/admin/login`：管理员登录
- `/admin`：管理中枢入口（需管理员会话）

---

## 4. 认证与权限模型

系统包含两套隔离会话：

- 用户会话：`/user-auth/*`，用于用户端功能
- 管理员会话：`/auth/*`，用于管理后台

关键特性：

- Access Token + Refresh Token
- Cookie + Session 双层机制
- 用户路由与管理员路由在前端守卫中分开校验

建议：

- 生产环境必须设置强随机 `JWT_SECRET_KEY`
- 严格控制 CORS 白名单
- 管理端入口建议配合网关层限制来源

---

## 5. 核心 API 概览（简版）

### 5.1 认证

- `POST /api/v1/user-auth/login`
- `POST /api/v1/user-auth/refresh`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

### 5.2 用户与画像

- `GET /api/v1/profiles`
- `POST /api/v1/profiles`
- `GET /api/v1/profiles/{id}/suggested-policies`

### 5.3 政策与匹配

- `GET /api/v1/policies`
- `GET /api/v1/policies/{id}`
- `POST /api/v1/policies/{id}/match-for-profile/{profile_id}`
- `POST /api/v1/policies/evaluate`

### 5.4 聊天与会话

- `GET /api/v1/chat/conversations`
- `POST /api/v1/chat/conversations`
- `POST /api/v1/chat/stream`
- `POST /api/v1/chat/agri-llm/stream`

### 5.5 管理端

- `GET /api/v1/admin-ops/dashboard-summary`
- `POST /api/v1/policies/crawl`
- `POST /api/v1/policies/parse-file/jobs`
- `GET /api/v1/policies/auto-crawler/config`

---

## 6. 常见问题与排障

### 6.1 MySQL 旧库缺列报错（如 `Unknown column`）

原因：`create_all()` 不会为已存在表自动补列。  
处理：

- 开发环境保持 `SCHEMA_AUTO_PATCH=true`
- 生产环境建议用迁移脚本或手工 SQL 补齐

示例：

```sql
ALTER TABLE auth_sessions ADD COLUMN last_seen_at DATETIME NULL;
ALTER TABLE auth_sessions ADD COLUMN user_agent TEXT NULL;
ALTER TABLE auth_sessions ADD COLUMN ip VARCHAR(64) NULL;
ALTER TABLE auth_refresh_tokens ADD COLUMN rotated_at DATETIME NULL;
```

### 6.2 前端 `Failed to fetch`

- 确认后端运行在 `http://127.0.0.1:8000`
- 确认前端通过 `npm run dev` 启动（启用代理）
- 避免混用 `localhost` 与 `127.0.0.1`

### 6.3 401 循环或登录后跳回登录页

- 检查 cookie 域、CORS 白名单、浏览器隐私设置
- 检查系统时间是否漂移导致 token 过期判断异常

### 6.4 文件解析失败

- 检查文件大小、编码与格式（docx/pdf）
- 检查模型/OCR 外部依赖是否已配置

---

## 7. 测试与质量建议

## 7.1 已有测试

`backend/tests/` 已覆盖部分核心路径（认证、匹配、洞察、画像等）。

可运行：

```bash
cd backend
pytest
```

## 7.2 建议优先补测

- 权限边界：洞察、爬虫源、策略评估接口
- 聊天流异常中断后的状态收口
- 大体量输入（文件解析、长消息）边界限制
- 窄屏导航与聊天失败恢复的 E2E 回归

---

## 8. 已知风险与整改路线图

详细审查报告见：

- `docs/project-review-2026-04.md`

建议优先级：

- P0：认证密钥与权限边界、窄屏导航可达性、聊天失败恢复
- P1：流式异常收口、输入体量限制、洞察查询性能优化
- P2：可访问性与前端渲染性能持续优化

---

## 9. 相关文档

- `docs/baseline-matrix.md`：需求/设计落点矩阵
- `docs/repo-audit.md`：仓库现状核对
- `docs/project-review-2026-04.md`：全项目审查报告

