from __future__ import annotations

import base64
import datetime as dt
from typing import Any

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.db.session import get_sessionmaker
from app.models.admin_models import AdminOperationRunItemORM, AdminOperationRunORM, AutoCrawlerRunORM
from app.models.business_models import PolicyORM
from app.models.policy_review_models import PolicyReviewTaskORM
from app.services.file_parse_service import parse_file_bytes
from app.services.policy_condition_tree_service import ConditionTreeRefreshError, refresh_policy_condition_tree
from app.services.crawler_service import (
    crawl_policy_candidates,
    create_review_tasks_for_candidates,
    get_excluded_urls,
    list_crawler_sources,
    mark_auto_crawler_run,
    upsert_raw_candidates,
)
from app.services.review_queue_service import (
    queue_review_task_enrichment,
    refresh_review_task_ai,
    refresh_review_task_condition_tree,
)
from app.telemetry.writer import telemetry_span


def create_run(
    db: Session,
    *,
    operation_type: str,
    payload: dict,
    trigger_source: str = 'manual',
    items: list[dict] | None = None,
) -> AdminOperationRunORM:
    run = AdminOperationRunORM(
        operation_type=operation_type,
        status='pending',
        payload_json=payload,
        trigger_source=trigger_source,
        progress_completed=0,
        progress_total=len(items or []),
    )
    db.add(run)
    db.flush()

    for idx, item in enumerate(items or []):
        db.add(AdminOperationRunItemORM(run_id=run.id, item_index=idx, status='pending', input_json=item))
    db.commit()
    db.refresh(run)
    return run


def consume_one_pending_run(db: Session) -> AdminOperationRunORM | None:
    run = db.scalar(select(AdminOperationRunORM).where(AdminOperationRunORM.status == 'pending').order_by(asc(AdminOperationRunORM.id)))
    if not run:
        return None
    return _consume_run(db, run)


def consume_run_by_id(db: Session, run_id: int) -> AdminOperationRunORM | None:
    run = db.get(AdminOperationRunORM, run_id)
    if not run:
        return None
    if run.status == 'pending':
        return _consume_run(db, run)
    db.refresh(run)
    return run


def consume_run_by_id_in_background(run_id: int) -> None:
    SessionLocal = get_sessionmaker()
    db = SessionLocal()
    try:
        consume_run_by_id(db, run_id)
    finally:
        db.close()


def _consume_run(db: Session, run: AdminOperationRunORM) -> AdminOperationRunORM:
    run.status = 'running'
    run.updated_at = dt.datetime.utcnow()
    db.commit()

    try:
        if run.operation_type == 'policy_file_parse':
            _execute_policy_file_parse(db, run)
        elif run.operation_type in ('policy_crawl_manual', 'auto_crawler_run'):
            _execute_policy_crawl(db, run)
        elif run.operation_type == 'policy_review_ai_refresh':
            _execute_policy_review_ai_refresh(db, run)
        elif run.operation_type == 'policy_condition_tree_backfill':
            _execute_policy_condition_tree_backfill(db, run)
        else:
            run.status = 'failed'
            run.summary_message = f'未知 operation_type: {run.operation_type}'
            run.result_json = {'error': 'unknown_operation'}
            run.updated_at = dt.datetime.utcnow()
            db.commit()
    except Exception as exc:
        run.status = 'failed'
        run.summary_message = str(exc)
        run.result_json = {**(run.result_json or {}), 'error': type(exc).__name__, 'message': str(exc)}
        run.updated_at = dt.datetime.utcnow()
        db.commit()

    db.refresh(run)
    return run


def _execute_policy_file_parse(db: Session, run: AdminOperationRunORM) -> None:
    items = db.scalars(
        select(AdminOperationRunItemORM).where(AdminOperationRunItemORM.run_id == run.id).order_by(asc(AdminOperationRunItemORM.item_index))
    ).all()

    ok = 0
    _update_run_progress(db, run, message='开始解析文件任务', stage='started', progress_total=len(items), progress_completed=0, progress_failed=0)
    with telemetry_span(db, domain='admin_ops', event_name='policy_file_parse', metadata={'run_id': run.id}):
        for item in items:
            item.status = 'running'
            db.commit()
            try:
                filename = item.input_json.get('filename') or 'uploaded'
                data_b64 = item.input_json.get('data_b64')
                if not data_b64:
                    raise ValueError('missing data_b64')
                data = base64.b64decode(data_b64.encode('utf-8'))
                parsed = parse_file_bytes(filename, data)
                item.status = 'success'
                item.result_json = parsed
                item.error_message = ''
                ok += 1
                _update_run_progress(
                    db,
                    run,
                    message=f'文件解析进度：{ok}/{len(items)}',
                    stage='processing',
                    progress_total=len(items),
                    progress_completed=ok,
                    progress_failed=max(len(items) - ok, 0),
                    current_item_index=item.item_index,
                )
            except Exception as exc:
                item.status = 'failed'
                item.error_message = str(exc)
                item.result_json = {}
            finally:
                db.commit()

    run.progress_completed = len(items)
    run.progress_failed = len(items) - ok
    run.result_json = {'success': ok, 'failed': len(items) - ok}
    run.summary_message = f'解析完成：success={ok}, failed={len(items) - ok}'
    run.status = 'success' if ok == len(items) else ('partial' if ok > 0 else 'failed')
    run.updated_at = dt.datetime.utcnow()
    db.commit()


def _update_run_progress(
    db: Session,
    run: AdminOperationRunORM,
    *,
    message: str,
    stage: str,
    progress_completed: int | None = None,
    progress_total: int | None = None,
    progress_failed: int | None = None,
    **extra: Any,
) -> None:
    if progress_completed is not None:
        run.progress_completed = progress_completed
    if progress_total is not None:
        run.progress_total = progress_total
    if progress_failed is not None:
        run.progress_failed = progress_failed

    progress = dict((run.result_json or {}).get('progress') or {})
    progress.update(extra)
    progress.update(
        {
            'stage': stage,
            'message': message,
            'updated_at': dt.datetime.utcnow().isoformat(),
            'progress_completed': run.progress_completed,
            'progress_total': run.progress_total,
            'progress_failed': run.progress_failed,
        }
    )
    run.summary_message = message
    run.result_json = {**(run.result_json or {}), 'progress': progress}
    run.updated_at = dt.datetime.utcnow()
    db.commit()


def _execute_policy_crawl(db: Session, run: AdminOperationRunORM) -> None:
    items = db.scalars(
        select(AdminOperationRunItemORM).where(AdminOperationRunItemORM.run_id == run.id).order_by(asc(AdminOperationRunItemORM.item_index))
    ).all()
    payload = run.payload_json or {}
    auto_crawler_record_id = payload.get('auto_crawler_record_id')
    auto_row = db.get(AutoCrawlerRunORM, auto_crawler_record_id) if auto_crawler_record_id else None

    if auto_row and auto_row.started_at is None:
        auto_row.started_at = dt.datetime.utcnow()
        db.commit()

    success_count = 0
    all_candidates: list[dict] = []
    review_task_ids: list[int] = []
    stored_ids: list[int] = []
    selected_ids = list(payload.get('source_ids') or [])
    selected_sources = [src for src in list_crawler_sources() if not selected_ids or src.id in selected_ids]
    total_sources = max(len(selected_sources), 1)

    _update_run_progress(
        db,
        run,
        message=f'爬虫已启动，准备处理 {len(selected_sources)} 个来源',
        stage='started',
        progress_total=total_sources,
        progress_completed=0,
        progress_failed=0,
        total_sources=len(selected_sources),
        candidates_count=0,
        stored_count=0,
        review_task_count=0,
    )

    with telemetry_span(db, domain='admin_ops', event_name=run.operation_type, metadata={'run_id': run.id}):
        for item in items:
            item.status = 'running'
            db.commit()
            try:
                source_ids = list(item.input_json.get('source_ids') or payload.get('source_ids') or [])
                max_pages = int(item.input_json.get('max_pages_per_source') or payload.get('max_pages_per_source') or 5)
                max_candidates = int(item.input_json.get('max_candidates') or payload.get('max_candidates') or 8)
                file_types = list(item.input_json.get('file_types') or payload.get('file_types') or [])
                validity_statuses = list(item.input_json.get('validity_statuses') or payload.get('validity_statuses') or [])
                operator = payload.get('operator')
                excluded_urls = get_excluded_urls(db)
                candidates = []

                effective_sources = [src for src in list_crawler_sources() if not source_ids or src.id in source_ids]
                if file_types:
                    wanted_types = {value for value in file_types if value}
                    effective_sources = [src for src in effective_sources if not src.file_type or src.file_type in wanted_types]
                if not effective_sources:
                    raise ValueError('未找到可用的数据源')

                for source_index, source in enumerate(effective_sources, start=1):
                    remaining = max(max_candidates - len(candidates), 0)
                    if remaining <= 0:
                        break
                    _update_run_progress(
                        db,
                        run,
                        message=f'正在抓取 {source.name}（{source_index}/{len(effective_sources)}）',
                        stage='fetching_source',
                        progress_total=max(len(effective_sources), 1),
                        progress_completed=source_index - 1,
                        progress_failed=0,
                        current_source=source.id,
                        current_source_name=source.name,
                        current_source_index=source_index,
                        total_sources=len(effective_sources),
                        candidates_count=len(all_candidates) + len(candidates),
                        stored_count=len(stored_ids),
                        review_task_count=len(review_task_ids),
                    )
                    source_candidates = crawl_policy_candidates(
                        source_ids=[source.id],
                        max_pages_per_source=max_pages,
                        max_candidates=remaining,
                        file_types=file_types,
                        validity_statuses=validity_statuses,
                        exclude_urls=excluded_urls,
                    )
                    candidates.extend(source_candidates)
                    excluded_urls.update(candidate['page_url'] for candidate in source_candidates if candidate.get('page_url'))
                    _update_run_progress(
                        db,
                        run,
                        message=f'{source.name} 抓取完成，累计候选 {len(all_candidates) + len(candidates)} 条',
                        stage='source_completed',
                        progress_total=max(len(effective_sources), 1),
                        progress_completed=source_index,
                        progress_failed=0,
                        current_source=source.id,
                        current_source_name=source.name,
                        current_source_index=source_index,
                        total_sources=len(effective_sources),
                        candidates_count=len(all_candidates) + len(candidates),
                        stored_count=len(stored_ids),
                        review_task_count=len(review_task_ids),
                    )

                _update_run_progress(
                    db,
                    run,
                    message=f'已抓取 {len(candidates)} 条候选，正在写入原始表',
                    stage='persisting',
                    progress_total=max(len(effective_sources), 1),
                    progress_completed=len(effective_sources),
                    progress_failed=0,
                    candidates_count=len(all_candidates) + len(candidates),
                    stored_count=len(stored_ids),
                    review_task_count=len(review_task_ids),
                )

                stored_rows = upsert_raw_candidates(db, candidates)
                row_id_by_url = {row.page_url: row.id for row in stored_rows if row.id is not None}
                for candidate in candidates:
                    candidate['raw_policy_id'] = row_id_by_url.get(candidate['page_url'])

                _update_run_progress(
                    db,
                    run,
                    message=f'已写入 {len(stored_rows)} 条原始记录，正在创建审核任务',
                    stage='creating_review_tasks',
                    progress_total=max(len(effective_sources), 1),
                    progress_completed=len(effective_sources),
                    progress_failed=0,
                    candidates_count=len(all_candidates) + len(candidates),
                    stored_count=len(stored_ids) + len(stored_rows),
                    review_task_count=len(review_task_ids),
                )

                task_ids = create_review_tasks_for_candidates(db, candidates=candidates, operator=operator)
                db.commit()
                queue_review_task_enrichment(task_ids, operator=operator)

                all_candidates.extend(candidates)
                stored_ids.extend([row.id for row in stored_rows if row.id is not None])
                review_task_ids.extend(task_ids)
                item.status = 'success'
                item.result_json = {
                    'candidates': candidates,
                    'stored_ids': [row.id for row in stored_rows if row.id is not None],
                    'review_task_ids': task_ids,
                }
                item.error_message = ''
                success_count += 1
                _update_run_progress(
                    db,
                    run,
                    message=f'当前任务完成：累计候选 {len(all_candidates)} 条，已创建 {len(review_task_ids)} 个审核任务，AI 补全在后台继续进行',
                    stage='item_completed',
                    progress_total=max(len(effective_sources), 1),
                    progress_completed=len(effective_sources),
                    progress_failed=0,
                    candidates_count=len(all_candidates),
                    stored_count=len(stored_ids),
                    review_task_count=len(review_task_ids),
                )
            except Exception as exc:
                item.status = 'failed'
                item.result_json = {}
                item.error_message = str(exc)
                _update_run_progress(
                    db,
                    run,
                    message=f'爬虫执行失败：{exc}',
                    stage='failed',
                    progress_failed=run.progress_failed + 1,
                )
            finally:
                db.commit()

    run.progress_total = max(run.progress_total, total_sources)
    if success_count == len(items):
        run.progress_completed = run.progress_total
    run.progress_failed = len(items) - success_count
    run.result_json = {
        'candidates': all_candidates[:10],
        'stored_ids': stored_ids,
        'review_task_ids': review_task_ids,
        'success': success_count,
        'failed': len(items) - success_count,
        'progress': {
            'stage': 'completed',
            'message': f'抓取完成：共 {len(all_candidates)} 条候选，创建 {len(review_task_ids)} 个审核任务，AI 补全已转入后台',
            'updated_at': dt.datetime.utcnow().isoformat(),
            'progress_completed': run.progress_completed,
            'progress_total': run.progress_total,
            'progress_failed': run.progress_failed,
            'candidates_count': len(all_candidates),
            'stored_count': len(stored_ids),
            'review_task_count': len(review_task_ids),
        },
    }
    run.summary_message = f'抓取完成：success={success_count}, failed={len(items) - success_count}, candidates={len(all_candidates)}'
    run.status = 'success' if success_count == len(items) else ('partial' if success_count > 0 else 'failed')
    run.updated_at = dt.datetime.utcnow()

    if auto_row:
        mark_auto_crawler_run(auto_row, status=run.status, summary_message=run.summary_message)
    db.commit()


def _execute_policy_review_ai_refresh(db: Session, run: AdminOperationRunORM) -> None:
    items = db.scalars(
        select(AdminOperationRunItemORM).where(AdminOperationRunItemORM.run_id == run.id).order_by(asc(AdminOperationRunItemORM.item_index))
    ).all()
    payload = run.payload_json or {}
    operator = payload.get('operator')

    _update_run_progress(
        db,
        run,
        message='AI 审核建议重跑任务已启动',
        stage='started',
        progress_total=max(len(items), 1),
        progress_completed=0,
        progress_failed=0,
        task_id=payload.get('task_id'),
    )

    success_count = 0
    with telemetry_span(db, domain='admin_ops', event_name=run.operation_type, metadata={'run_id': run.id}):
        for item in items:
            item.status = 'running'
            db.commit()
            try:
                task_id = int(item.input_json.get('task_id') or payload.get('task_id') or 0)
                if task_id <= 0:
                    raise ValueError('missing task_id')
                _update_run_progress(
                    db,
                    run,
                    message=f'正在为审核任务 #{task_id} 生成 AI 建议',
                    stage='processing',
                    current_item_index=item.item_index,
                    task_id=task_id,
                )
                task = refresh_review_task_ai(db, task_id=task_id, operator=operator)
                if task is None:
                    raise ValueError('task not found')
                item.status = 'success'
                item.error_message = ''
                item.result_json = {
                    'task_id': task.id,
                    'ai_status': task.ai_status,
                    'ai_recommendation': task.ai_recommendation,
                }
                success_count += 1
                _update_run_progress(
                    db,
                    run,
                    message=f'审核任务 #{task.id} 的 AI 建议已更新',
                    stage='item_completed',
                    progress_completed=success_count,
                    progress_failed=max(len(items) - success_count, 0),
                    current_item_index=item.item_index,
                    task_id=task.id,
                )
            except Exception as exc:
                item.status = 'failed'
                item.error_message = str(exc)
                item.result_json = {}
                _update_run_progress(
                    db,
                    run,
                    message=f'AI 审核建议重跑失败：{exc}',
                    stage='failed',
                    progress_failed=run.progress_failed + 1,
                    current_item_index=item.item_index,
                    task_id=item.input_json.get('task_id') or payload.get('task_id'),
                )
            finally:
                db.commit()

    run.progress_total = max(len(items), 1)
    if success_count == len(items):
        run.progress_completed = run.progress_total
    run.progress_failed = len(items) - success_count
    run.result_json = {
        'success': success_count,
        'failed': len(items) - success_count,
        'task_id': payload.get('task_id'),
        'progress': {
            'stage': 'completed' if success_count == len(items) else 'failed',
            'message': (
                f'AI 审核建议已更新：success={success_count}, failed={len(items) - success_count}'
                if success_count == len(items)
                else f'AI 审核建议重跑结束：success={success_count}, failed={len(items) - success_count}'
            ),
            'updated_at': dt.datetime.utcnow().isoformat(),
            'progress_completed': run.progress_completed,
            'progress_total': run.progress_total,
            'progress_failed': run.progress_failed,
            'task_id': payload.get('task_id'),
        },
    }
    run.summary_message = (
        f'AI 审核建议已更新：success={success_count}, failed={len(items) - success_count}'
        if success_count == len(items)
        else f'AI 审核建议重跑结束：success={success_count}, failed={len(items) - success_count}'
    )
    run.status = 'success' if success_count == len(items) else ('partial' if success_count > 0 else 'failed')
    run.updated_at = dt.datetime.utcnow()
    db.commit()


def _execute_policy_condition_tree_backfill(db: Session, run: AdminOperationRunORM) -> None:
    items = db.scalars(
        select(AdminOperationRunItemORM).where(AdminOperationRunItemORM.run_id == run.id).order_by(asc(AdminOperationRunItemORM.item_index))
    ).all()
    payload = run.payload_json or {}
    operator = payload.get('operator')

    _update_run_progress(
        db,
        run,
        message='条件树回补任务已启动',
        stage='started',
        progress_total=max(len(items), 1),
        progress_completed=0,
        progress_failed=0,
    )

    success_count = 0
    with telemetry_span(db, domain='admin_ops', event_name=run.operation_type, metadata={'run_id': run.id}):
        for item in items:
            item.status = 'running'
            db.commit()
            try:
                target_type = str(item.input_json.get('target_type') or payload.get('target_type') or '').strip()
                entity_id = int(item.input_json.get('entity_id') or 0)
                if target_type not in {'policy', 'review_task'}:
                    raise ValueError('invalid target_type')
                if entity_id <= 0:
                    raise ValueError('missing entity_id')

                _update_run_progress(
                    db,
                    run,
                    message=f'正在生成 {target_type} #{entity_id} 的条件树',
                    stage='processing',
                    current_item_index=item.item_index,
                    target_type=target_type,
                    entity_id=entity_id,
                )

                if target_type == 'review_task':
                    task = refresh_review_task_condition_tree(db, task_id=entity_id, operator=operator)
                    if task is None:
                        raise ValueError('task not found')
                    result = {
                        'target_type': target_type,
                        'entity_id': entity_id,
                        'draft_status': task.draft_status,
                        'condition_tree_meta': (task.draft_condition_tree or {}).get('compile_metadata') or {},
                    }
                else:
                    policy, summary = refresh_policy_condition_tree(db, policy_id=entity_id)
                    if policy is None:
                        raise ValueError('policy not found')
                    result = {
                        'target_type': target_type,
                        'entity_id': entity_id,
                        'policy_id': policy.id,
                        'summary': summary or {},
                    }

                item.status = 'success'
                item.error_message = ''
                item.result_json = result
                success_count += 1
                _update_run_progress(
                    db,
                    run,
                    message=f'已完成 {success_count}/{len(items)} 条条件树回补',
                    stage='item_completed',
                    progress_completed=success_count,
                    progress_failed=len(items) - success_count,
                    current_item_index=item.item_index,
                    target_type=target_type,
                    entity_id=entity_id,
                )
            except Exception as exc:
                db.rollback()
                item = db.get(AdminOperationRunItemORM, item.id)
                run = db.get(AdminOperationRunORM, run.id)
                item.status = 'failed'
                item.error_message = str(exc)
                item.result_json = {'error': type(exc).__name__, 'message': str(exc)}
                _update_run_progress(
                    db,
                    run,
                    message=f'条件树回补失败：{exc}',
                    stage='failed',
                    progress_failed=(run.progress_failed or 0) + 1,
                    current_item_index=item.item_index,
                    target_type=item.input_json.get('target_type'),
                    entity_id=item.input_json.get('entity_id'),
                )
            finally:
                db.commit()

    run.progress_total = max(len(items), 1)
    if success_count == len(items):
        run.progress_completed = run.progress_total
    run.progress_failed = len(items) - success_count
    run.result_json = {
        'success': success_count,
        'failed': len(items) - success_count,
        'progress': {
            'stage': 'completed' if success_count == len(items) else 'failed',
            'message': (
                f'条件树回补完成：success={success_count}, failed={len(items) - success_count}'
                if success_count == len(items)
                else f'条件树回补结束：success={success_count}, failed={len(items) - success_count}'
            ),
            'updated_at': dt.datetime.utcnow().isoformat(),
            'progress_completed': run.progress_completed,
            'progress_total': run.progress_total,
            'progress_failed': run.progress_failed,
        },
    }
    run.summary_message = run.result_json['progress']['message']
    run.status = 'success' if success_count == len(items) else ('partial' if success_count > 0 else 'failed')
    run.updated_at = dt.datetime.utcnow()
    db.commit()
