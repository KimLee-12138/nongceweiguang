from __future__ import annotations

import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def _column_names(insp, table: str) -> set[str]:
    try:
        return {c['name'] for c in insp.get_columns(table)}
    except Exception:
        return set()


def _add_column(engine: Engine, table: str, name: str, ddl_type: str) -> None:
    stmt = text(f'ALTER TABLE {table} ADD COLUMN {name} {ddl_type}')
    with engine.begin() as conn:
        conn.execute(stmt)
    logger.info('schema_align: added column %s.%s (%s)', table, name, ddl_type)


def ensure_auth_schema(engine: Engine) -> None:
    """
    幂等补齐认证与政策相关表的缺失列。
    SQLAlchemy create_all 不会 ALTER 已有表，因此开发库和旧库需要在启动时补列。
    """
    dialect = engine.dialect.name
    insp = inspect(engine)

    def nullable_datetime() -> str:
        return 'DATETIME' if dialect == 'sqlite' else 'DATETIME NULL'

    def nullable_date() -> str:
        return 'DATE' if dialect == 'sqlite' else 'DATE NULL'

    def nullable_varchar(length: int) -> str:
        return f'VARCHAR({length})' if dialect == 'sqlite' else f'VARCHAR({length}) NULL'

    table = 'auth_sessions'
    cols = _column_names(insp, table)
    for name, ddl in [
        ('last_seen_at', nullable_datetime()),
        ('user_agent', 'TEXT' if dialect == 'sqlite' else 'TEXT NULL'),
        ('ip', nullable_varchar(64)),
    ]:
        if cols and name not in cols:
            _add_column(engine, table, name, ddl)
            cols.add(name)

    table = 'auth_refresh_tokens'
    cols = _column_names(insp, table)
    if cols and 'rotated_at' not in cols:
        _add_column(engine, table, 'rotated_at', nullable_datetime())
        cols.add('rotated_at')

    raw_cols = _column_names(insp, 'hubei_policies_raw')
    if raw_cols:
        raw_field_ddls = [
            ('file_type', nullable_varchar(32)),
            ('validity_status', "VARCHAR(32) NOT NULL DEFAULT '有效'"),
            ('effective_date', nullable_date()),
            ('expiry_date', nullable_date()),
        ]
        for name, ddl in raw_field_ddls:
            if name not in raw_cols:
                _add_column(engine, 'hubei_policies_raw', name, ddl)
                raw_cols.add(name)

    policy_cols = _column_names(insp, 'policies')
    if policy_cols:
        policy_field_ddls = [
            ('file_type', nullable_varchar(32)),
            ('validity_status', "VARCHAR(32) NOT NULL DEFAULT '有效'"),
            ('effective_date', nullable_date()),
            ('expiry_date', nullable_date()),
        ]
        for name, ddl in policy_field_ddls:
            if name not in policy_cols:
                _add_column(engine, 'policies', name, ddl)
                policy_cols.add(name)

    review_cols = _column_names(insp, 'policy_review_tasks')
    if review_cols:
        review_field_ddls = [
            ('draft_file_type', nullable_varchar(32)),
            ('draft_validity_status', nullable_varchar(32)),
            ('draft_effective_date', nullable_date()),
            ('draft_expiry_date', nullable_date()),
        ]
        for name, ddl in review_field_ddls:
            if name not in review_cols:
                _add_column(engine, 'policy_review_tasks', name, ddl)
                review_cols.add(name)

    admin_run_cols = _column_names(insp, 'admin_operation_runs')
    if admin_run_cols and 'updated_at' not in admin_run_cols:
        _add_column(engine, 'admin_operation_runs', 'updated_at', nullable_datetime())

    glossary_cols = _column_names(insp, 'compass_glossary')
    if glossary_cols:
        glossary_field_ddls = [
            ('category', "VARCHAR(64) NOT NULL DEFAULT '政策主题'"),
            ('aliases_json', 'JSON' if dialect == 'sqlite' else 'JSON NULL'),
            ('weight', 'INTEGER NOT NULL DEFAULT 1'),
            ('enabled', 'BOOLEAN NOT NULL DEFAULT 1'),
            ('updated_at', 'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'),
        ]
        for name, ddl in glossary_field_ddls:
            if name not in glossary_cols:
                _add_column(engine, 'compass_glossary', name, ddl)
                glossary_cols.add(name)
