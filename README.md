# 农策微光（按文档基线实现）

本仓库由 `软件概要说明书.md`（概要设计）与 `软件需求规格说明书.md`（SRS）驱动开发。

## 快速启动（开发环境）

### 后端（FastAPI）

1. 进入后端目录并安装依赖

```bash
cd backend
python -m pip install -r requirements.txt
```

2. 准备环境变量

- 复制 `backend/.env.example` 为 `backend/.env` 并修改 `MYSQL_DSN` 等配置  
- 开发期也可用 SQLite 便于本地体验（仅用于开发测试）：`MYSQL_DSN=sqlite:///./dev.db`

3. 初始化管理员（概要设计要求：管理员/用户 Cookie 隔离，管理员需先存在）

```bash
python -m app.cli init-admin --username admin --password admin123
```

4. 写入联调演示数据并生成样本文件（推荐）

```bash
python -m app.cli seed-demo --workspace-root ..
```

5. 启动 API

```bash
uvicorn run:app --host 127.0.0.1 --port 8000
```

#### MySQL 旧库与 ORM 列不一致时

SQLAlchemy 的 `create_all()` **只会创建不存在的表**，**不会**给已有表加新列。若你较早建过库，而后代码给 `auth_sessions` 等表增加了字段，会出现 `Unknown column 'ip'` 等错误。

- **默认**：`.env` 中 `SCHEMA_AUTO_PATCH=true`（见 `backend/.env.example`）时，进程启动会在 `create_all` 之后**幂等**执行缺列补齐（见 `backend/app/db/schema_align.py`）。
- **生产**若关闭自动补齐（`SCHEMA_AUTO_PATCH=false`），可手工执行与下列等价的 SQL（按实际库名、表前缀调整）：

```sql
ALTER TABLE auth_sessions ADD COLUMN last_seen_at DATETIME NULL;
ALTER TABLE auth_sessions ADD COLUMN user_agent TEXT NULL;
ALTER TABLE auth_sessions ADD COLUMN ip VARCHAR(64) NULL;
ALTER TABLE auth_refresh_tokens ADD COLUMN rotated_at DATETIME NULL;
```

若 `token_hash` 仍为二进制列且写入 hex 字符串异常，可改为：`MODIFY COLUMN token_hash VARCHAR(64) NOT NULL`（注意备份与数据兼容性）。

6. （可选）启动调度器（后台作业消费者，10 秒轮询一次）

```bash
python -m app.scheduler
```

7. 验证 P0 基线

```bash
python -m app.cli verify-baseline
```

### 前端（Vue 3 + Vite + Element Plus）

```bash
cd frontend
npm install
npm run dev
```

默认前端读取 `frontend/.env.development` 的 `VITE_API_BASE_URL=/api/v1`，由 Vite 代理转发到 `http://127.0.0.1:8000`。
如果使用静态构建或 `vite preview`，请显式设置绝对地址，例如 `http://127.0.0.1:8000/api/v1`，不要复用开发代理假设。

## 功能入口（与 SRS 7.1 验收项对齐）

- 普通用户：`/login`、`/register`、`/chat`
- 洞察：`/insights`
- 风向标：`/compass`
- 管理端：`/admin/login`、`/admin/policies`

## 开发对齐文档

- 需求/设计落点矩阵：`docs/baseline-matrix.md`
- 仓库现状与目标结构：`docs/repo-audit.md`

