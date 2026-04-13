# 仓库现状核对（2026-04-11）

## 1. 当前实现状态

- 后端已具备 FastAPI + SQLAlchemy + Scheduler 主骨架
- 前端已具备 Vue 3 + Vite + Element Plus 页面与路由壳
- MySQL 已作为当前联调库，SQLite 仅保留为本地回退
- 已补齐 `request_rate_limits`、`hubei_policies_raw`、`auto_crawler_runs` 的 ORM 覆盖
- 已补齐：
  - 模型 provider（DeepSeek）
  - OCR provider（Baidu OCR）
  - 湖北政策源爬虫
  - 自动爬虫 run 记录
  - 演示数据 seed 与基线检查 CLI

## 2. 仍需依赖外部环境的项

- `DEEPSEEK_API_KEY`
- `BAIDU_OCR_API_KEY`
- `BAIDU_OCR_SECRET_KEY`
- 可访问湖北政策官网的外网环境

以上任一缺失时，系统仍可启动，但对应在线校验与真实能力验收不能判定通过。

## 3. 推荐联调命令

```bash
cd backend
python -m app.cli seed-demo --workspace-root ..
python -m app.cli verify-baseline
uvicorn run:app --host 127.0.0.1 --port 8000
python -m app.scheduler
```

```bash
cd frontend
npm run dev
```

## 4. 当前 P0 文档索引

- `项目计划.md`：P0 总表、阻塞项、每日验收清单
- `docs/baseline-matrix.md`：页面 / API / 表冻结矩阵
