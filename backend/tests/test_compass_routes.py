from __future__ import annotations

import datetime as dt
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.v1 import compass_routes
from app.db.base import Base
from app.models import auth_models  # noqa: F401
from app.models import admin_models  # noqa: F401
from app.models.business_models import CompassGlossaryORM, CompassReportORM, HubeiPolicyRawORM, PolicyORM
from app.services import compass_service


def test_build_compass_signals_aggregates_real_dimensions():
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        db.add(
            CompassGlossaryORM(
                term='高标准农田',
                category='政策主题',
                aliases_json=['高标准'],
                weight=3,
                enabled=True,
                description='农田建设相关政策主题',
            )
        )
        db.add(
            HubeiPolicyRawORM(
                title='湖北省高标准农田建设项目通知',
                issuer='湖北省农业农村厅',
                publish_date=dt.date(2026, 4, 1),
                topic_category='农田建设',
                file_category='通知',
                file_type='gfxwj',
                validity_status='有效',
                page_url='https://example.com/raw/1',
                attachment_urls=[],
                full_text='推进高标准农田建设，提高耕地质量。',
            )
        )
        db.add(
            PolicyORM(
                title='高标准农田建设扶持政策',
                source='湖北省农业农村厅',
                summary='支持家庭农场开展高标准农田建设。',
                file_type='gfxwj',
                validity_status='有效',
                condition_tree={
                    'schema_version': '2.0',
                    'id': 'root',
                    'type': 'group',
                    'logic': 'and',
                    'must': True,
                    'description': '测试条件树',
                    'applicable_subjects': ['家庭农场'],
                    'children': [
                        {
                            'id': 'node-region',
                            'type': 'predicate',
                            'field': 'region',
                            'operator': 'in',
                            'value': ['湖北省'],
                            'must': True,
                            'description': '区域限制',
                        }
                    ],
                },
            )
        )
        db.commit()

        payload = compass_service.build_compass_signals(db, months=6)

        assert payload['stats']['policy_count'] == 1
        assert payload['stats']['raw_policy_count'] == 1
        assert any(item['name'] == '高标准农田' for item in payload['top_topics'])
        assert any(item['name'] == '湖北省农业农村厅' for item in payload['top_issuers'])
        assert any(item['name'] == '家庭农场' for item in payload['audience_distribution'])
        assert any(item['name'] == '湖北省' for item in payload['region_distribution'])


def test_glossary_routes_support_crud():
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)
    admin = SimpleNamespace(username='admin')

    with Session(engine) as db:
        created = compass_routes.create_glossary(
            compass_routes.GlossaryPayload(
                term='设施农业',
                category='支持方向',
                aliases=['设施种植', '设施园艺'],
                weight=5,
                enabled=True,
                description='设施农业相关政策方向',
            ),
            db=db,
            admin=admin,
        )

        assert created['term'] == '设施农业'
        assert created['weight'] == 5

        listing = compass_routes.glossary(category='支持方向', enabled=True, db=db)
        assert len(listing['items']) == 1

        updated = compass_routes.patch_glossary(
            glossary_id=created['id'],
            payload=compass_routes.GlossaryPayload(
                term='设施农业升级',
                category='支持方向',
                aliases=['设施种植'],
                weight=6,
                enabled=False,
                description='升级后的词条',
            ),
            db=db,
            admin=admin,
        )

        assert updated['term'] == '设施农业升级'
        assert updated['enabled'] is False

        deleted = compass_routes.remove_glossary(created['id'], db=db, admin=admin)
        assert deleted['ok'] is True
        assert db.query(CompassGlossaryORM).count() == 0


def test_generate_route_stores_report_and_upserts_glossary(monkeypatch):
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)
    admin = SimpleNamespace(username='admin')

    monkeypatch.setattr(
        compass_service,
        'generate_compass_report_payload',
        lambda *, signals, glossary_items=None: {
            'title': '本周农业政策风向标',
            'category': 'weekly',
            'summary': '本周重点关注高标准农田与设施农业。',
            'content': '## 趋势\n测试内容\n## 机会\n测试内容\n## 准备事项\n测试内容',
            'glossary': [
                {
                    'term': '高标准农田',
                    'description': '表示农田建设与耕地提升相关政策。',
                    'category': '政策主题',
                    'aliases': ['高标准'],
                    'weight': 4,
                }
            ],
        },
    )

    with Session(engine) as db:
        db.add(
            PolicyORM(
                title='高标准农田建设扶持政策',
                source='湖北省农业农村厅',
                summary='支持家庭农场开展高标准农田建设。',
                file_type='gfxwj',
                validity_status='有效',
                condition_tree={'id': 'root', 'type': 'group', 'logic': 'and', 'must': True, 'children': []},
            )
        )
        db.commit()

        payload = compass_routes.generate(db=db, admin=admin)

        assert payload['ok'] is True
        assert db.query(CompassReportORM).count() == 1
        glossary = db.query(CompassGlossaryORM).one()
        assert glossary.term == '高标准农田'
        assert glossary.weight == 4
