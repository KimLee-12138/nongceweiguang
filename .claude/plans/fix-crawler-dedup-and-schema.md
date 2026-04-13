# 修复字段对齐 + 爬虫去重功能

## Context

手动爬虫报 500 错误：ORM 模型字段名 `progress_current` 与数据库实际列名 `progress_completed` 不一致。同时需要添加去重：已进入审核流程或已入库的政策不应被重复爬取。

## 审查结论

### 自动爬虫功能整体评价

代码质量良好，链路清晰：
- `crawl_policy_candidates()` 抓取 → `upsert_raw_candidates()` 写入 raw 表（按 page_url 去重） → `create_review_tasks_for_candidates()` 创建审核任务
- `create_review_task` 已有基础去重：对 `review_status == 'pending'` 的同 source_ref 任务会更新而非新建
- 但已 approved/rejected 的任务 URL 仍会被重复爬取

### 需要修复的问题

**问题 1: `admin_ops_routes.py` 引用已废弃字段**
- 第 29、51 行使用 `r.progress_current`，但 ORM 模型已改为 `progress_completed`
- 会导致所有 /admin-ops/runs 接口报 AttributeError

**问题 2: 缺少完整去重机制**
- 当前只对 pending 状态的审核任务去重
- 已 approved（已入库）或 rejected（已驳回）的政策 URL 会被重复爬取
- 需要在 `crawl_policy_candidates` 阶段排除这些 URL

## 改动方案

### 文件 1: `backend/app/api/v1/admin_ops_routes.py`
- 第 29 行：`r.progress_current` → `r.progress_completed`
- 第 51 行：`run.progress_current` → `run.progress_completed`

### 文件 2: `backend/app/services/crawler_service.py`

新增函数 `get_excluded_urls(db)` 查询所有已进入审核流程的 URL：
```python
def get_excluded_urls(db: Session) -> set[str]:
    # 从 policy_review_tasks 获取所有 source_ref（不限状态）
    # 从 policies 表获取已入库政策的 raw_text_ref
    ...
```

修改 `crawl_policy_candidates()` 函数，增加 `exclude_urls: set[str] | None = None` 参数，在 `_parse_article_page` 成功返回后、加入 candidates 列表前，检查 `link` 是否在 exclude_urls 中。

### 文件 3: `backend/app/services/admin_operation_service.py`

在 `_execute_policy_crawl` 中：
- 导入 `from app.services.crawler_service import get_excluded_urls`
- 调用 `crawl_policy_candidates` 前查询 exclude_urls
- 传入 `exclude_urls=excluded_urls` 参数

## 验证
1. 重启后端，访问 /admin-ops/runs 不应报错
2. 手动爬取一次 → 候选进入审核队列
3. 审核通过一条政策 → 该政策进入 policies 表
4. 再次手动爬取 → 已审核/已入库的 URL 不再出现在候选中
