from __future__ import annotations

import datetime as dt
import asyncio
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.v1 import policy_review_routes, policy_routes
from app.db.base import Base
from app.models import auth_models  # noqa: F401
from app.models import admin_models  # noqa: F401
from app.models.admin_models import AdminOperationRunORM
from app.models.business_models import PolicyORM
from app.models.policy_review_models import PolicyReviewTaskORM
from app.schemas.policy import Policy, PolicyConditionNode
from app.services import admin_operation_service
from app.services import crawler_service
from app.services import model_provider
from app.services import review_queue_service
from app.services.crawler_service import (
    CrawlerError,
    CrawlerSource,
    _extract_links,
    _fetch_html,
    _parse_article_page,
    crawl_policy_candidates,
)
from app.services.review_queue_service import approve_review_task, create_review_task, enrich_review_task


def test_parse_article_page_extracts_policy_metadata():
    html = '''
    <html>
      <body>
        <div class="crumb">首页 > 政策 > 规范性文件</div>
        <h1>湖北省农业农村厅关于开展设施农业示范的通知</h1>
        <div class="meta">
          <span>发布机构：</span><span>湖北省农业农村厅</span>
          <span>发文字号：</span><span>鄂农规〔2025〕3号</span>
          <span>分类：</span><span>乡村振兴</span>
          <span>效力状态：</span><span>有效</span>
          <span>发文日期：</span><span>2025-04-18</span>
        </div>
        <div class="article">
          <p>本文件自2025年05月01日起施行，有效期至2027年04月30日。</p>
          <p>请各地遵照执行。</p>
        </div>
      </body>
    </html>
    '''
    source = CrawlerSource(
        id='hubei_agri_policy',
        name='湖北省农业农村厅-规范性文件',
        url='https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/gfxwj_GK2020/',
        file_type='gfxwj',
    )

    parsed = _parse_article_page(
        html,
        link='https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/gfxwj_GK2020/tz/202504/t20250418_5612345.shtml',
        source=source,
    )

    assert parsed['title'] == '湖北省农业农村厅关于开展设施农业示范的通知'
    assert parsed['issuer'] == '湖北省农业农村厅'
    assert parsed['doc_no'] == '鄂农规〔2025〕3号'
    assert parsed['publish_date'] == '2025-04-18'
    assert parsed['file_type'] == 'gfxwj'
    assert parsed['validity_status'] == '有效'
    assert parsed['effective_date'] == '2025-05-01'
    assert parsed['expiry_date'] == '2027-04-30'
    assert parsed['file_category'] == '通知'
    assert parsed['topic_category'] == '乡村振兴'
    assert parsed['column'] == '规范性文件'


def test_approve_review_task_copies_metadata_to_policy():
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        task = PolicyReviewTaskORM(
            source_type='crawler',
            title='测试政策',
            source='湖北省农业农村厅',
            raw_text='测试原文',
            raw_text_ref='https://example.com/policy',
            review_status='pending',
            draft_status='success',
            ai_status='success',
            draft_title='测试政策（审核稿）',
            draft_source='湖北省农业农村厅',
            draft_summary='摘要',
            draft_category='乡村振兴',
            draft_file_type='qtzd',
            draft_validity_status='待生效',
            draft_effective_date=dt.date(2026, 1, 1),
            draft_expiry_date=dt.date(2026, 12, 31),
            draft_condition_tree={'id': 'root', 'logic': 'and', 'children': []},
            ai_risk_points_json=[],
            ai_evidence_json=[],
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        approve_review_task(db, task_id=task.id, operator='admin')

        policy = db.get(PolicyORM, task.approved_policy_id)
        assert policy is not None
        assert policy.file_type == 'qtzd'
        assert policy.validity_status == '待生效'
        assert policy.effective_date == dt.date(2026, 1, 1)
        assert policy.expiry_date == dt.date(2026, 12, 31)


def test_fetch_html_defaults_to_not_trusting_env_proxy(monkeypatch):
    captured: dict[str, object] = {}

    class FakeResponse:
        status_code = 200
        encoding = 'utf-8'
        text = '<html>ok</html>'

        def raise_for_status(self):
            return None

    class FakeClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, url, headers):
            captured['url'] = url
            captured['headers'] = headers
            return FakeResponse()

    monkeypatch.setattr(
        crawler_service,
        'get_settings',
        lambda: SimpleNamespace(HTTP_TIMEOUT_SECONDS=5, CRAWLER_TRUST_ENV_PROXY=False),
    )
    monkeypatch.setattr(crawler_service.httpx, 'Client', FakeClient)

    assert _fetch_html('https://example.com') == '<html>ok</html>'
    assert captured['trust_env'] is False


def test_fetch_html_reports_proxy_hint_when_proxy_mode_enabled(monkeypatch):
    request = httpx.Request('GET', 'https://example.com')

    class FakeClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, url, headers):
            raise httpx.ConnectError('connection refused', request=request)

    monkeypatch.setattr(
        crawler_service,
        'get_settings',
        lambda: SimpleNamespace(HTTP_TIMEOUT_SECONDS=5, CRAWLER_TRUST_ENV_PROXY=True),
    )
    monkeypatch.setattr(crawler_service.httpx, 'Client', FakeClient)
    monkeypatch.setenv('HTTP_PROXY', 'http://127.0.0.1:9')

    with pytest.raises(CrawlerError) as exc_info:
        _fetch_html('https://example.com')

    assert '代理配置可能拦截了目标站点' in str(exc_info.value)


def test_model_provider_reports_read_timeout_clearly(monkeypatch):
    request = httpx.Request('POST', 'https://api.deepseek.com/chat/completions')

    class FakeClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url, headers, json):
            raise httpx.ReadTimeout('timed out', request=request)

    monkeypatch.setattr(
        model_provider,
        '_settings',
        lambda: SimpleNamespace(
            DEEPSEEK_API_KEY='test-key',
            DEEPSEEK_BASE_URL='https://api.deepseek.com',
            DEEPSEEK_MODEL='deepseek-chat',
            HTTP_TIMEOUT_SECONDS=60,
        ),
    )
    monkeypatch.setattr(model_provider.httpx, 'Client', FakeClient)

    with pytest.raises(model_provider.ModelProviderError) as exc_info:
        model_provider._chat_json(system_prompt='system', user_prompt='user')

    assert '请求超时' in str(exc_info.value)
    assert '60 秒' in str(exc_info.value)


def test_crawl_policy_candidates_reports_all_links_already_excluded(monkeypatch):
    source = CrawlerSource(
        id='hubei_agri_policy',
        name='湖北省农业农村厅-规范性文件',
        url='https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/gfxwj_GK2020/',
        file_type='gfxwj',
    )
    link = 'https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/gfxwj_GK2020/tz/202504/t20250418_5612345.shtml'
    list_html = f'<a href="{link}">湖北省农业农村厅关于开展设施农业示范的通知</a>'

    monkeypatch.setattr(crawler_service, 'list_crawler_sources', lambda: [source])
    monkeypatch.setattr(crawler_service, '_fetch_html', lambda url: list_html if url == source.url else '')

    with pytest.raises(CrawlerError) as exc_info:
        crawl_policy_candidates(
            source_ids=[source.id],
            max_pages_per_source=5,
            max_candidates=5,
            exclude_urls={link},
        )

    assert '已全部存在于审核流程或正式政策库中' in str(exc_info.value)


def test_extract_links_reads_dynamic_gfxwj_json_feed(monkeypatch):
    list_url = 'https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/gfxwj_GK2020/'
    feed_url = 'https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/gfxwj_GK2020/zcfg.json'
    list_html = "<script src='http://nyt.hubei.gov.cn/material/js/lil_gfxwj2020.js'></script>"
    feed_json = """
    {
      "data": [
        {
          "URL": "http://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/gfxwj_GK2020/202603/t20260319_5895589.shtml",
          "FILENAME": "省农业农村厅关于印发《湖北省农机购置与应用补贴“优机优补”“有进有出”实施方案》的通知"
        }
      ]
    }
    """

    monkeypatch.setattr(
        crawler_service,
        '_fetch_html',
        lambda url: feed_json if url == feed_url else pytest.fail(f'unexpected url: {url}'),
    )

    links = _extract_links(list_html, list_url)

    assert links == ['https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/gfxwj_GK2020/202603/t20260319_5895589.shtml']


def test_extract_links_reads_dynamic_qtzd_json_feed(monkeypatch):
    list_url = 'https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/qtzdgkwj_GK2020/'
    feed_url = 'https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/qtzdgkwj_GK2020/qtzdgk.json'
    list_html = "<script src='http://nyt.hubei.gov.cn/material/js/lil_qtzdgk2020.js'></script>"
    feed_json = """
    {
      "data": [
        {
          "URL": "http://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/qtzdgkwj_GK2020/tz/202505/t20250516_5652528.shtml",
          "FILENAME": "省农业农村厅关于开展金融支农试点工作的通知"
        }
      ]
    }
    """

    monkeypatch.setattr(
        crawler_service,
        '_fetch_html',
        lambda url: feed_json if url == feed_url else pytest.fail(f'unexpected url: {url}'),
    )

    links = _extract_links(list_html, list_url)

    assert links == ['https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/qtzdgkwj_GK2020/tz/202505/t20250516_5652528.shtml']


def test_consume_pending_crawl_run_succeeds_inside_running_event_loop(monkeypatch):
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    candidate = {
        'title': '测试爬虫政策',
        'issuer': '湖北省农业农村厅',
        'doc_no': '鄂农发〔2026〕1号',
        'publish_date': '2026-04-01',
        'column': '规范性文件',
        'file_category': '通知',
        'topic_category': '农业、畜牧业、渔业',
        'file_type': 'gfxwj',
        'validity_status': '有效',
        'effective_date': None,
        'expiry_date': None,
        'page_url': 'https://nyt.hubei.gov.cn/zfxxgk/zc_GK2020/gfxwj_GK2020/202604/t20260401_5900000.shtml',
        'attachment_urls': [],
        'html_text': '测试正文',
        'attachment_text': '',
        'full_text': '测试正文',
        'source_id': 'hubei_agri_policy',
    }

    monkeypatch.setattr(admin_operation_service, 'get_excluded_urls', lambda db: set())
    monkeypatch.setattr(admin_operation_service, 'crawl_policy_candidates', lambda **kwargs: [dict(candidate)])
    monkeypatch.setattr(admin_operation_service, 'queue_review_task_enrichment', lambda task_ids, operator=None: None)

    def fake_create_review_tasks(db, *, candidates, operator):
        return [9001 + idx for idx, _ in enumerate(candidates)]

    monkeypatch.setattr(admin_operation_service, 'create_review_tasks_for_candidates', fake_create_review_tasks)

    with Session(engine) as db:
        run = admin_operation_service.create_run(
            db,
            operation_type='policy_crawl_manual',
            payload={
                'operator': 'admin',
                'source_ids': ['hubei_agri_policy'],
                'max_pages_per_source': 3,
                'max_candidates': 3,
                'file_types': [],
                'validity_statuses': [],
            },
            items=[
                {
                    'source_ids': ['hubei_agri_policy'],
                    'max_pages_per_source': 3,
                    'max_candidates': 3,
                    'file_types': [],
                    'validity_statuses': [],
                }
            ],
        )

        async def invoke():
            return admin_operation_service.consume_one_pending_run(db)

        processed = asyncio.run(invoke())
        db.refresh(run)

        assert processed is not None
        assert processed.id == run.id
        assert processed.status == 'success'
        assert processed.result_json.get('success') == 1
        assert len(processed.result_json.get('candidates') or []) == 1
        assert processed.result_json.get('progress', {}).get('stage') == 'completed'


def test_create_review_task_with_deferred_enrichment_is_immediately_visible(monkeypatch):
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    monkeypatch.setattr(review_queue_service, 'compile_policy_text', lambda *args, **kwargs: pytest.fail('should not compile immediately'))
    monkeypatch.setattr(review_queue_service, 'generate_review_ai_payload', lambda **kwargs: pytest.fail('should not call ai immediately'))

    with Session(engine) as db:
        task = create_review_task(
            db,
            source_type='crawler',
            title='测试爬虫政策',
            source='湖北省农业农村厅',
            raw_text='这是用于立即创建审核任务的测试正文，用来验证任务会先进入审核列表。',
            source_ref='https://example.com/crawler/1',
            raw_text_ref='https://example.com/crawler/1',
            raw_policy_id=1,
            operator='admin',
            draft_file_type='gfxwj',
            draft_validity_status='有效',
            defer_enrichment=True,
        )

        assert task.review_status == 'pending'
        assert task.draft_status == 'pending'
        assert task.ai_status == 'pending'
        assert task.draft_title == '测试爬虫政策'
        assert task.draft_source == '湖北省农业农村厅'
        assert task.draft_condition_tree['id'] == 'root'
        assert task.draft_condition_tree['type'] == 'group'
        assert task.draft_condition_tree['schema_version'] == '2.0'
        assert task.draft_condition_tree['compile_metadata']['compile_quality'] == 'draft'


def test_enrich_review_task_populates_pending_crawler_task(monkeypatch):
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    fake_policy = Policy(
        policy_id=None,
        title='测试爬虫政策（编译稿）',
        source='湖北省农业农村厅',
        summary='编译后的摘要',
        raw_text_ref=None,
        root_condition=PolicyConditionNode(id='root', relation='AND', must=True, children=[]),
    )

    monkeypatch.setattr(review_queue_service, 'compile_policy_text', lambda *args, **kwargs: fake_policy)
    monkeypatch.setattr(
        review_queue_service,
        'generate_review_ai_payload',
        lambda **kwargs: {
            'summary': 'AI 摘要',
            'category': '乡村振兴',
            'suggestion': '建议人工重点核对申请条件',
            'risk_points': [{'title': '风险', 'detail': '测试风险'}],
            'evidence': [{'quote': '测试证据', 'reason': '测试原因'}],
            'recommendation': '建议通过',
        },
    )

    with Session(engine) as db:
        task = create_review_task(
            db,
            source_type='crawler',
            title='测试爬虫政策',
            source='湖北省农业农村厅',
            raw_text='这是用于补全审核任务的测试正文。',
            source_ref='https://example.com/crawler/2',
            raw_text_ref='https://example.com/crawler/2',
            raw_policy_id=2,
            operator='admin',
            draft_file_type='qtzd',
            draft_validity_status='待生效',
            defer_enrichment=True,
        )

        enriched = enrich_review_task(db, task_id=task.id, operator='admin')

        assert enriched is not None
        assert enriched.draft_status == 'success'
        assert enriched.ai_status == 'success'
        assert enriched.draft_title == '测试爬虫政策（编译稿）'
        assert enriched.draft_summary == '编译后的摘要'
        assert enriched.draft_category == '乡村振兴'
        assert enriched.ai_suggestion == '建议人工重点核对申请条件'


def test_get_task_includes_condition_tree_metadata():
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        task = PolicyReviewTaskORM(
            source_type='crawler',
            title='测试政策',
            source='湖北省农业农村厅',
            raw_text='正文',
            review_status='pending',
            draft_status='success',
            ai_status='success',
            draft_condition_tree={
                'schema_version': '2.0',
                'id': 'root',
                'type': 'group',
                'logic': 'and',
                'must': True,
                'description': '测试条件树',
                'applicable_subjects': ['家庭农场'],
                'compile_metadata': {
                    'compile_quality': 'generated',
                    'missing_information': ['缺少申请窗口'],
                    'uncertain_points': ['主体类型表述不完整'],
                    'generated_by': 'deepseek',
                    'reason': '结构化成功',
                },
                'children': [],
            },
            ai_risk_points_json=[],
            ai_evidence_json=[],
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        payload = policy_review_routes.get_task(task.id, db=db, admin=SimpleNamespace(username='admin'))

        assert payload['task']['condition_tree_compile_quality'] == 'generated'
        assert payload['task']['condition_tree_missing_information'] == ['缺少申请窗口']
        assert payload['task']['condition_tree_applicable_subjects'] == ['家庭农场']


def test_list_tasks_route_returns_stats_and_keyword_filtered_items():
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        db.add_all(
            [
                PolicyReviewTaskORM(
                    source_type='crawler',
                    title='设施农业补贴政策',
                    source='湖北省农业农村厅',
                    raw_text='raw-1',
                    review_status='pending',
                    draft_status='success',
                    ai_status='success',
                    draft_category='设施农业',
                    draft_file_type='gfxwj',
                    draft_validity_status='有效',
                    ai_category='设施农业',
                    ai_recommendation='approve',
                    ai_risk_points_json=[],
                    ai_evidence_json=[],
                ),
                PolicyReviewTaskORM(
                    source_type='manual',
                    title='金融保险支持政策',
                    source='湖北省财政厅',
                    raw_text='raw-2',
                    review_status='approved',
                    draft_status='success',
                    ai_status='failed',
                    draft_category='金融保险',
                    draft_file_type='qtzd',
                    draft_validity_status='待生效',
                    ai_risk_points_json=[],
                    ai_evidence_json=[],
                ),
            ]
        )
        db.commit()

        payload = policy_review_routes.list_tasks(
            offset=0,
            limit=10,
            review_status='pending',
            source_type='crawler',
            category='设施农业',
            keyword='补贴',
            file_type='gfxwj',
            validity_status='有效',
            db=db,
            admin=SimpleNamespace(username='admin'),
        )

        assert payload['total'] == 1
        assert payload['stats']['pending'] == 1
        assert payload['stats']['approved'] == 0
        assert payload['stats']['ai_failed'] == 0
        assert len(payload['items']) == 1
        assert payload['items'][0]['title'] == '设施农业补贴政策'


def test_refresh_task_ai_route_reuses_existing_pending_run(monkeypatch):
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        task = PolicyReviewTaskORM(
            source_type='crawler',
            title='测试政策',
            source='湖北省农业农村厅',
            raw_text='正文',
            review_status='pending',
            draft_status='pending',
            ai_status='failed',
            ai_error='old error',
            ai_risk_points_json=[],
            ai_evidence_json=[],
        )
        db.add(task)
        db.flush()
        run = AdminOperationRunORM(
            operation_type='policy_review_ai_refresh',
            status='running',
            payload_json={'task_id': task.id, 'operator': 'admin'},
            result_json={},
            summary_message='running',
            progress_completed=0,
            progress_total=1,
            progress_failed=0,
            trigger_source='manual',
        )
        db.add(run)
        db.commit()

        payload = policy_review_routes.refresh_task_ai(
            task_id=task.id,
            db=db,
            admin=SimpleNamespace(username='admin'),
        )
        db.refresh(task)

        assert payload['run_id'] == run.id
        assert payload['reused'] is True
        assert task.ai_status == 'pending'
        assert task.ai_error is None


def test_refresh_task_ai_route_creates_background_run(monkeypatch):
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    captured: dict[str, int] = {}
    monkeypatch.setattr(policy_review_routes, 'consume_run_by_id_in_background', lambda run_id: captured.setdefault('run_id', run_id))

    with Session(engine) as db:
        task = PolicyReviewTaskORM(
            source_type='crawler',
            title='测试政策',
            source='湖北省农业农村厅',
            raw_text='正文',
            review_status='pending',
            draft_status='pending',
            ai_status='success',
            ai_risk_points_json=[],
            ai_evidence_json=[],
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        payload = policy_review_routes.refresh_task_ai(
            task_id=task.id,
            db=db,
            admin=SimpleNamespace(username='admin'),
        )
        db.refresh(task)
        run = db.get(AdminOperationRunORM, payload['run_id'])

        assert payload['reused'] is False
        assert run is not None
        assert run.operation_type == 'policy_review_ai_refresh'
        assert run.payload_json['task_id'] == task.id
        assert captured['run_id'] == run.id
        assert task.ai_status == 'pending'


def test_consume_pending_review_ai_refresh_run(monkeypatch):
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        task = PolicyReviewTaskORM(
            source_type='crawler',
            title='测试政策',
            source='湖北省农业农村厅',
            raw_text='正文',
            review_status='pending',
            draft_status='success',
            ai_status='pending',
            ai_risk_points_json=[],
            ai_evidence_json=[],
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        monkeypatch.setattr(
            admin_operation_service,
            'refresh_review_task_ai',
            lambda db, task_id, operator=None: SimpleNamespace(id=task_id, ai_status='success', ai_recommendation='approve'),
        )

        run = admin_operation_service.create_run(
            db,
            operation_type='policy_review_ai_refresh',
            payload={'task_id': task.id, 'operator': 'admin'},
            items=[{'task_id': task.id}],
        )

        processed = admin_operation_service.consume_one_pending_run(db)

        assert processed is not None
        assert processed.id == run.id
        assert processed.status == 'success'
        assert processed.result_json['task_id'] == task.id
        assert processed.result_json['progress']['stage'] == 'completed'


def test_refresh_task_condition_tree_route_creates_background_run(monkeypatch):
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    captured: dict[str, int] = {}
    monkeypatch.setattr(policy_review_routes, 'consume_run_by_id_in_background', lambda run_id: captured.setdefault('run_id', run_id))

    with Session(engine) as db:
        task = PolicyReviewTaskORM(
            source_type='crawler',
            title='测试政策',
            source='湖北省农业农村厅',
            raw_text='正文',
            review_status='pending',
            draft_status='success',
            ai_status='success',
            draft_condition_tree={'id': 'root', 'logic': 'and', 'children': []},
            ai_risk_points_json=[],
            ai_evidence_json=[],
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        payload = policy_review_routes.refresh_task_condition_tree(
            task_id=task.id,
            db=db,
            admin=SimpleNamespace(username='admin'),
        )
        db.refresh(task)
        run = db.get(AdminOperationRunORM, payload['run_id'])

        assert payload['reused'] is False
        assert run is not None
        assert run.operation_type == 'policy_condition_tree_backfill'
        assert captured['run_id'] == run.id
        assert task.draft_status == 'pending'


def test_refresh_policy_condition_tree_route_creates_background_run(monkeypatch):
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    captured: dict[str, int] = {}
    monkeypatch.setattr(policy_routes, 'consume_run_by_id_in_background', lambda run_id: captured.setdefault('run_id', run_id))

    with Session(engine) as db:
        policy = PolicyORM(
            title='测试政策',
            source='湖北省农业农村厅',
            summary='摘要',
            raw_text_ref='https://example.com/raw',
            condition_tree={'id': 'root', 'logic': 'and', 'children': []},
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)

        payload = policy_routes.refresh_policy_condition_tree(
            policy_id=policy.id,
            db=db,
            admin=SimpleNamespace(username='admin'),
        )
        run = db.get(AdminOperationRunORM, payload['run_id'])

        assert payload['reused'] is False
        assert run is not None
        assert run.operation_type == 'policy_condition_tree_backfill'
        assert captured['run_id'] == run.id


def test_compile_text_route_rejects_empty_raw_text():
    with pytest.raises(HTTPException) as exc_info:
        policy_routes.compile_text(
            policy_routes.CompileTextRequest(raw_text='', title='测试政策'),
            admin=SimpleNamespace(username='admin'),
        )

    assert exc_info.value.status_code == 503
    assert '缺少政策原文' in str(exc_info.value.detail)


def test_model_readiness_route_returns_provider_status(monkeypatch):
    monkeypatch.setattr(
        policy_routes,
        'check_model_readiness',
        lambda live=False: SimpleNamespace(
            to_dict=lambda: {
                'ok': True,
                'status': 'ready',
                'message': '模型在线校验成功',
                'detail': {'provider': 'deepseek', 'live': live},
            }
        ),
    )

    payload = policy_routes.get_model_readiness(live=True, admin=SimpleNamespace(username='admin'))

    assert payload['ok'] is True
    assert payload['status'] == 'ready'
    assert payload['detail']['provider'] == 'deepseek'

