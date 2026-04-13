from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_admin, get_current_user
from app.api.v1.schemas_policies import (
    CompileTextRequest,
    CompileTextResponse,
    MatchEvaluateRequest,
    MatchEvaluateResponse,
    PolicyIn,
    PolicyOut,
)
from app.db.session import get_db
from app.models.admin_models import AdminOperationRunItemORM, AdminOperationRunORM
from app.models.auth_models import AdminUserORM, EndUserORM
from app.models.business_models import MatchRecordORM, PolicyORM, UserProfileORM
from app.services.admin_operation_service import consume_run_by_id_in_background, create_run
from app.services.condition_tree_service import extract_condition_tree_metadata, normalize_condition_tree
from app.services.crawler_service import (
    create_auto_crawler_run_record,
    get_auto_crawler_config as get_auto_crawler_config_value,
    list_crawler_sources,
)
from app.services.file_parse_service import parse_file_bytes
from app.services.match_engine import to_match_summary
from app.services.model_provider import ModelProviderError, check_model_readiness
from app.services.policy_compile_service import compile_policy_text as compile_policy_text_with_model

router = APIRouter(prefix='/policies', tags=['policies'])


def _policy_to_out(policy: PolicyORM) -> PolicyOut:
    return PolicyOut(
        id=policy.id,
        title=policy.title,
        source=policy.source,
        version=policy.version,
        summary=policy.summary,
        raw_text_ref=policy.raw_text_ref,
        file_type=policy.file_type,
        validity_status=policy.validity_status,
        effective_date=policy.effective_date,
        expiry_date=policy.expiry_date,
        condition_tree=normalize_condition_tree(policy.condition_tree or {}),
        condition_tree_meta=extract_condition_tree_metadata(policy.condition_tree or {}),
    )


@router.post('', response_model=PolicyOut)
def create_policy(payload: PolicyIn, db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    _ = admin
    data = payload.model_dump()
    data['condition_tree'] = normalize_condition_tree(data.get('condition_tree') or {})
    policy = PolicyORM(**data)
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return _policy_to_out(policy)


@router.get('', response_model=list[PolicyOut])
def list_policies(db: Session = Depends(get_db)):
    policies = db.scalars(select(PolicyORM).order_by(desc(PolicyORM.id)).limit(200)).all()
    return [_policy_to_out(policy) for policy in policies]


@router.get('/{policy_id}', response_model=PolicyOut)
def get_policy(policy_id: int, db: Session = Depends(get_db)):
    policy = db.get(PolicyORM, policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Policy not found')
    return _policy_to_out(policy)


@router.put('/{policy_id}', response_model=PolicyOut)
def update_policy(policy_id: int, payload: PolicyIn, db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    _ = admin
    policy = db.get(PolicyORM, policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Policy not found')
    data = payload.model_dump()
    data['condition_tree'] = normalize_condition_tree(data.get('condition_tree') or {})
    for key, value in data.items():
        setattr(policy, key, value)
    db.commit()
    db.refresh(policy)
    return _policy_to_out(policy)


@router.delete('/{policy_id}')
def delete_policy(policy_id: int, db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    _ = admin
    policy = db.get(PolicyORM, policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Policy not found')
    records = db.scalars(select(MatchRecordORM).where(MatchRecordORM.policy_id == policy.id)).all()
    for record in records:
        db.delete(record)
    db.delete(policy)
    db.commit()
    return {'ok': True}


@router.post('/compile-text', response_model=CompileTextResponse)
def compile_text(payload: CompileTextRequest, admin: AdminUserORM = Depends(get_current_admin)):
    _ = admin
    try:
        result = compile_policy_text_with_model(payload.raw_text or '', payload.title, payload.source)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ModelProviderError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return CompileTextResponse(
        condition_tree=result['condition_tree'],
        detailed_condition_tree=result['condition_tree'],
        summary=result['summary'],
        category=result.get('category') or '',
        mode=result.get('mode', 'model'),
        compile_quality=result.get('compile_quality') or 'generated',
        missing_information=list(result.get('missing_information') or []),
        uncertain_points=list(result.get('uncertain_points') or []),
        applicable_subjects=list(result.get('applicable_subjects') or []),
    )


@router.get('/model-readiness')
def get_model_readiness(live: bool = False, admin: AdminUserORM = Depends(get_current_admin)):
    _ = admin
    return check_model_readiness(live=live).to_dict()


@router.post('/{policy_id}/refresh-condition-tree')
def refresh_policy_condition_tree(
    policy_id: int,
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    policy = db.get(PolicyORM, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail='Policy not found')

    candidate_runs = db.scalars(
        select(AdminOperationRunORM)
        .where(
            AdminOperationRunORM.operation_type == 'policy_condition_tree_backfill',
            AdminOperationRunORM.status.in_(('pending', 'running')),
        )
        .order_by(desc(AdminOperationRunORM.id))
        .limit(100)
    ).all()
    for run in candidate_runs:
        for run_item in db.scalars(select(AdminOperationRunItemORM).where(AdminOperationRunItemORM.run_id == run.id)).all():
            if (run_item.input_json or {}).get('target_type') == 'policy' and (run_item.input_json or {}).get('entity_id') == policy_id:
                return {'run_id': run.id, 'status': run.status, 'reused': True}

    run = create_run(
        db,
        operation_type='policy_condition_tree_backfill',
        payload={'operator': admin.username, 'target_type': 'policy', 'policy_ids': [policy_id]},
        items=[{'target_type': 'policy', 'entity_id': policy_id}],
    )
    consume_run_by_id_in_background(run.id)
    return {'run_id': run.id, 'status': run.status, 'reused': False}


@router.get('/crawl/sources')
def crawl_sources():
    sources = [
        {'id': item.id, 'name': item.name, 'url': item.url, 'file_type': item.file_type}
        for item in list_crawler_sources()
    ]
    return {'sources': sources}


@router.post('/crawl')
async def crawl_manual(
    payload: dict | None = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    body = payload or {}
    source_ids = list(body.get('source_ids') or [])
    max_pages = int(body.get('max_pages_per_source') or 5)
    max_candidates = int(body.get('max_candidates') or 8)
    file_types = list(body.get('file_types') or [])
    validity_statuses = list(body.get('validity_statuses') or [])
    run = create_run(
        db,
        operation_type='policy_crawl_manual',
        payload={
            'source_ids': source_ids,
            'max_pages_per_source': max_pages,
            'max_candidates': max_candidates,
            'file_types': file_types,
            'validity_statuses': validity_statuses,
            'operator': admin.username,
        },
        items=[
            {
                'source_ids': source_ids,
                'max_pages_per_source': max_pages,
                'max_candidates': max_candidates,
                'file_types': file_types,
                'validity_statuses': validity_statuses,
            }
        ],
    )
    if background_tasks is not None:
        background_tasks.add_task(consume_run_by_id_in_background, run.id)
    else:
        consume_run_by_id_in_background(run.id)
    return {
        'run_id': run.id,
        'status': run.status,
        'queued': True,
        'message': '爬虫任务已入队，可在任务中心查看实时进度',
        'candidates': [],
    }


@router.get('/auto-crawler/config')
def get_auto_crawler_config(db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    _ = admin
    return get_auto_crawler_config_value(db)


@router.put('/auto-crawler/config')
def set_auto_crawler_config(payload: dict, db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    from app.models.admin_models import SystemConfigORM

    _ = admin
    normalized = {
        'enabled': bool(payload.get('enabled', False)),
        'sources': list(payload.get('sources') or []),
        'interval_hours': int(payload.get('interval_hours') or 24),
        'max_pages_per_source': int(payload.get('max_pages_per_source') or 5),
        'max_candidates': int(payload.get('max_candidates') or 8),
        'file_types': list(payload.get('file_types') or []),
        'validity_statuses': list(payload.get('validity_statuses') or []),
    }
    row = db.get(SystemConfigORM, 'auto_crawler')
    if row:
        row.set_json_value(normalized)
    else:
        row = SystemConfigORM(key='auto_crawler')
        row.set_json_value(normalized)
        db.add(row)
    db.commit()
    return {'ok': True}


@router.post('/auto-crawler/run-now')
def run_auto_crawler_now(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    config = get_auto_crawler_config_value(db)
    source_ids = list(config.get('sources') or [])
    max_pages = int(config.get('max_pages_per_source') or 5)
    max_candidates = int(config.get('max_candidates') or 8)
    file_types = list(config.get('file_types') or [])
    validity_statuses = list(config.get('validity_statuses') or [])
    record = create_auto_crawler_run_record(
        db,
        source_ids=source_ids,
        max_pages=max_pages,
        created_by=admin.username,
        status='pending',
        summary_message='等待执行',
    )
    run = create_run(
        db,
        operation_type='auto_crawler_run',
        payload={
            'source_ids': source_ids,
            'max_pages_per_source': max_pages,
            'max_candidates': max_candidates,
            'file_types': file_types,
            'validity_statuses': validity_statuses,
            'operator': admin.username,
            'auto_crawler_record_id': record.id,
        },
        items=[
            {
                'source_ids': source_ids,
                'max_pages_per_source': max_pages,
                'max_candidates': max_candidates,
                'file_types': file_types,
                'validity_statuses': validity_statuses,
            }
        ],
    )
    if background_tasks is not None:
        background_tasks.add_task(consume_run_by_id_in_background, run.id)
    else:
        consume_run_by_id_in_background(run.id)
    return {'run_id': run.id, 'status': run.status, 'queued': True, 'message': '自动爬虫任务已入队'}


@router.post('/parse-file')
async def parse_file_sync(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AdminUserORM = Depends(get_current_admin),
):
    _ = db, admin
    data = await file.read()
    if len(data) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail='文件过大，请使用 /policies/parse-file/jobs 走后台解析')
    try:
        parsed = parse_file_bytes(file.filename or 'uploaded', data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {'filename': file.filename, **parsed}


@router.post('/parse-file/jobs')
def parse_file_job(payload: dict, db: Session = Depends(get_db), admin: AdminUserORM = Depends(get_current_admin)):
    _ = admin
    filename = payload.get('filename') or 'uploaded'
    data_b64 = payload.get('data_b64')
    if not data_b64:
        raise HTTPException(status_code=400, detail='Missing data_b64')
    run = create_run(
        db,
        operation_type='policy_file_parse',
        payload={'filename': filename},
        items=[{'filename': filename, 'data_b64': data_b64}],
    )
    return {'run_id': run.id, 'status': run.status}


@router.post('/evaluate', response_model=MatchEvaluateResponse)
def match_evaluate(payload: MatchEvaluateRequest):
    return MatchEvaluateResponse(summary=to_match_summary(payload.condition_tree or {}, payload.profile or {}))


@router.post('/{policy_id}/match-for-profile/{profile_id}')
def match_policy_for_profile(
    policy_id: int,
    profile_id: int,
    db: Session = Depends(get_db),
    user: EndUserORM = Depends(get_current_user),
):
    policy = db.get(PolicyORM, policy_id)
    profile = db.get(UserProfileORM, profile_id)
    if not policy or not profile or profile.owner_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Policy or profile not found')

    profile_dict = {
        'name': profile.name,
        'type': profile.type,
        'area': profile.area,
        'green_cert': profile.green_cert,
        'irrigation': profile.irrigation,
        'extra_data': profile.extra_data or {},
    }
    summary = to_match_summary(policy.condition_tree or {}, profile_dict)
    record = MatchRecordORM(
        user_profile_id=profile.id,
        policy_id=policy.id,
        fully_matched=bool(summary.get('fully_matched')),
        match_detail=summary,
    )
    db.add(record)
    db.commit()
    return {'summary': summary, 'record_id': record.id}
