from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.admin_models import AutoCrawlerRunORM, SystemConfigORM
from app.models.business_models import HubeiPolicyRawORM, PolicyORM
from app.models.policy_review_models import PolicyReviewTaskORM
from app.services.review_queue_service import create_review_task


class CrawlerError(RuntimeError):
    pass


FILE_TYPE_LABELS = {
    'gfxwj': '规范性文件',
    'qtzd': '其他主动公开文件',
    'zcjd': '政策解读',
}

URL_CATEGORY_LABELS = {
    'tz': '通知',
    'tg': '通告',
    'gs': '公示',
    'yj': '意见',
    'qt': '其他',
}

VALIDITY_STATUSES = ('有效', '失效', '废止', '已修改', '待生效')
META_LABELS = [
    '索引号',
    '发布机构',
    '发文机构',
    '发布单位',
    '发文字号',
    '文号',
    '分类',
    '主题分类',
    '效力状态',
    '发文日期',
    '发布日期',
    '成文日期',
    '生效日期',
    '施行日期',
    '失效日期',
    '有效期至',
]
META_STOP_PATTERN = '|'.join(sorted((re.escape(label) for label in META_LABELS), key=len, reverse=True))
ATTACHMENT_EXTENSIONS = ('pdf', 'doc', 'docx', 'xls', 'xlsx', 'wps', 'zip', 'rar', 'txt')
DYNAMIC_LIST_FEEDS = (
    ('lil_gfxwj2020.js', 'zcfg.json'),
    ('lil_qtzdgk2020.js', 'qtzdgk.json'),
)


@dataclass
class CrawlerReadiness:
    ok: bool
    status: str
    message: str
    detail: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            'ok': self.ok,
            'status': self.status,
            'message': self.message,
            'detail': self.detail,
        }


@dataclass(frozen=True)
class CrawlerSource:
    id: str
    name: str
    url: str
    file_type: str | None = None


def list_crawler_sources() -> list[CrawlerSource]:
    return [
        CrawlerSource(
            id=str(item['id']),
            name=str(item.get('name') or item['id']),
            url=str(item['url']),
            file_type=str(item.get('file_type') or '').strip() or None,
        )
        for item in get_settings().hubei_crawler_sources()
    ]


def check_crawler_readiness(*, live: bool = False) -> CrawlerReadiness:
    sources = list_crawler_sources()
    if not sources:
        return CrawlerReadiness(False, 'missing_config', '未配置湖北政策爬虫数据源', {'configured': False})
    if not live:
        return CrawlerReadiness(
            True,
            'configured',
            '爬虫数据源已配置，未执行在线验证',
            {'configured': True, 'sources': [s.id for s in sources]},
        )
    source = sources[0]
    try:
        html_text = _fetch_html(source.url)
        count = len(_extract_links(html_text, source.url))
    except CrawlerError as exc:
        detail = {
            'configured': True,
            'source': source.id,
            'trust_env_proxy': bool(get_settings().CRAWLER_TRUST_ENV_PROXY),
        }
        proxy_env = _proxy_env_values()
        if proxy_env:
            detail['proxy_env_keys'] = sorted(proxy_env)
        return CrawlerReadiness(False, 'error', str(exc), detail)
    return CrawlerReadiness(
        True,
        'ready',
        '爬虫数据源在线校验成功',
        {'configured': True, 'source': source.id, 'links': count},
    )


def get_excluded_urls(db: Session) -> set[str]:
    """获取所有已进入审核流程或已入库的政策 URL，用于爬虫去重。"""
    urls: set[str] = set()
    # 所有审核任务（不限状态）的 source_ref
    review_refs = db.scalars(
        select(PolicyReviewTaskORM.source_ref).where(PolicyReviewTaskORM.source_ref.isnot(None))
    ).all()
    urls.update(r for r in review_refs if r)
    # 已入库政策的 raw_text_ref
    policy_refs = db.scalars(
        select(PolicyORM.raw_text_ref).where(PolicyORM.raw_text_ref.isnot(None))
    ).all()
    urls.update(r for r in policy_refs if r)
    return urls


def crawl_policy_candidates(
    *,
    source_ids: list[str] | None = None,
    max_pages_per_source: int = 5,
    max_candidates: int = 8,
    file_types: list[str] | None = None,
    validity_statuses: list[str] | None = None,
    exclude_urls: set[str] | None = None,
) -> list[dict[str, Any]]:
    selected = {item for item in (source_ids or []) if item}
    wanted_file_types = {item for item in (file_types or []) if item}
    wanted_validity = {item for item in (validity_statuses or []) if item}
    excluded = exclude_urls or set()
    total_links_found = 0
    total_excluded_links = 0
    total_parse_failures = 0
    total_filtered_out = 0
    total_unexcluded_links = 0

    sources = [src for src in list_crawler_sources() if not selected or src.id in selected]
    if wanted_file_types:
        sources = [src for src in sources if not src.file_type or src.file_type in wanted_file_types]
    if not sources:
        raise CrawlerError('未找到可用的数据源')

    candidates: list[dict[str, Any]] = []
    for source in sources:
        list_html = _fetch_html(source.url)
        links = _extract_links(list_html, source.url)[: max(max_pages_per_source, 1)]
        total_links_found += len(links)
        for link in links:
            if link in excluded:
                total_excluded_links += 1
                continue
            total_unexcluded_links += 1
            try:
                page_html = _fetch_html(link)
                candidate = _parse_article_page(page_html, link=link, source=source)
            except CrawlerError:
                total_parse_failures += 1
                continue
            if wanted_file_types and candidate.get('file_type') not in wanted_file_types:
                total_filtered_out += 1
                continue
            if wanted_validity and candidate.get('validity_status') not in wanted_validity:
                total_filtered_out += 1
                continue
            candidates.append(candidate)
            if len(candidates) >= max_candidates:
                return candidates
    if not candidates:
        if total_links_found == 0:
            raise CrawlerError('未从列表页提取到任何候选链接，请检查数据源页面结构')
        if total_unexcluded_links == 0 and total_excluded_links:
            raise CrawlerError('未抓取到新候选政策：列表页链接已全部存在于审核流程或正式政策库中')
        if total_parse_failures and total_parse_failures == total_unexcluded_links:
            raise CrawlerError('已获取候选链接，但详情页解析全部失败，请检查目标站点页面结构')
        if total_filtered_out and total_filtered_out + total_parse_failures >= total_unexcluded_links:
            raise CrawlerError('未抓取到符合当前筛选条件的候选政策')
        raise CrawlerError('未抓取到候选政策，请检查数据源页面结构、筛选条件或去重结果')
    return candidates


def upsert_raw_candidates(db: Session, candidates: list[dict[str, Any]]) -> list[HubeiPolicyRawORM]:
    stored: list[HubeiPolicyRawORM] = []
    for item in candidates:
        existing = db.scalar(select(HubeiPolicyRawORM).where(HubeiPolicyRawORM.page_url == item['page_url']))
        publish_date = _parse_optional_date(item.get('publish_date'))
        effective_date = _parse_optional_date(item.get('effective_date'))
        expiry_date = _parse_optional_date(item.get('expiry_date'))
        if existing:
            existing.title = item['title']
            existing.issuer = item.get('issuer')
            existing.doc_no = item.get('doc_no')
            existing.publish_date = publish_date
            existing.column_name = item.get('column')
            existing.file_category = item.get('file_category')
            existing.topic_category = item.get('topic_category')
            existing.file_type = item.get('file_type')
            existing.validity_status = item.get('validity_status') or '有效'
            existing.effective_date = effective_date
            existing.expiry_date = expiry_date
            existing.attachment_urls = list(item.get('attachment_urls') or [])
            existing.html_text = item.get('html_text')
            existing.attachment_text = item.get('attachment_text')
            existing.full_text = item.get('full_text')
            stored.append(existing)
            continue
        row = HubeiPolicyRawORM(
            title=item['title'],
            issuer=item.get('issuer'),
            doc_no=item.get('doc_no'),
            publish_date=publish_date,
            column_name=item.get('column'),
            file_category=item.get('file_category'),
            topic_category=item.get('topic_category'),
            file_type=item.get('file_type'),
            validity_status=item.get('validity_status') or '有效',
            effective_date=effective_date,
            expiry_date=expiry_date,
            page_url=item['page_url'],
            attachment_urls=list(item.get('attachment_urls') or []),
            html_text=item.get('html_text'),
            attachment_text=item.get('attachment_text'),
            full_text=item.get('full_text'),
        )
        db.add(row)
        stored.append(row)
    db.flush()
    return stored


def create_review_tasks_for_candidates(
    db: Session,
    *,
    candidates: list[dict[str, Any]],
    operator: str | None,
) -> list[int]:
    task_ids: list[int] = []
    for item in candidates:
        task = create_review_task(
            db,
            source_type='crawler',
            title=item['title'],
            source=item.get('issuer'),
            raw_text=item.get('full_text') or item.get('html_text') or '',
            source_ref=item['page_url'],
            raw_text_ref=item['page_url'],
            raw_policy_id=item.get('raw_policy_id'),
            operator=operator,
            draft_file_type=item.get('file_type'),
            draft_validity_status=item.get('validity_status'),
            draft_effective_date=item.get('effective_date'),
            draft_expiry_date=item.get('expiry_date'),
            defer_enrichment=True,
        )
        task_ids.append(task.id)
    return task_ids


def create_auto_crawler_run_record(
    db: Session,
    *,
    source_ids: list[str],
    max_pages: int,
    created_by: str | None,
    status: str = 'pending',
    summary_message: str | None = None,
) -> AutoCrawlerRunORM:
    row = AutoCrawlerRunORM(
        status=status,
        source_ids_json=source_ids,
        max_pages=max_pages,
        created_by=created_by,
        summary_message=summary_message,
    )
    db.add(row)
    db.flush()
    return row


def mark_auto_crawler_run(
    run: AutoCrawlerRunORM,
    *,
    status: str,
    summary_message: str,
) -> None:
    now = dt.datetime.utcnow()
    if run.started_at is None:
        run.started_at = now
    run.finished_at = now
    run.status = status
    run.summary_message = summary_message


def get_auto_crawler_config(db: Session) -> dict[str, Any]:
    row = db.get(SystemConfigORM, 'auto_crawler')
    if row:
        value = row.get_json_value()
    else:
        value = {}
    return {
        'enabled': bool(value.get('enabled', False)),
        'sources': list(value.get('sources') or []),
        'interval_hours': int(value.get('interval_hours') or 24),
        'max_pages_per_source': int(value.get('max_pages_per_source') or 5),
        'max_candidates': int(value.get('max_candidates') or 8),
        'file_types': list(value.get('file_types') or []),
        'validity_statuses': list(value.get('validity_statuses') or []),
    }


def _fetch_html(url: str) -> str:
    settings = get_settings()
    try:
        with httpx.Client(
            timeout=settings.HTTP_TIMEOUT_SECONDS,
            follow_redirects=True,
            trust_env=bool(settings.CRAWLER_TRUST_ENV_PROXY),
        ) as client:
            response = client.get(url, headers={'User-Agent': 'ncwg-bot/1.0'})
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise CrawlerError(f'抓取失败：HTTP {exc.response.status_code} {url}') from exc
    except httpx.HTTPError as exc:
        message = f'抓取失败：{exc}'
        if settings.CRAWLER_TRUST_ENV_PROXY and _proxy_env_values():
            message += '；检测到系统代理变量，当前代理配置可能拦截了目标站点'
        raise CrawlerError(message) from exc
    response.encoding = response.encoding or 'utf-8'
    return response.text


def _proxy_env_values() -> dict[str, str]:
    result: dict[str, str] = {}
    for key in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY'):
        value = os.environ.get(key) or os.environ.get(key.lower())
        if value:
            result[key] = value
    return result


def _extract_links(list_html: str, base_url: str) -> list[str]:
    dynamic_links = _extract_links_from_dynamic_feed(list_html, base_url)
    if dynamic_links is not None:
        return dynamic_links

    links: list[str] = []
    seen: set[str] = set()
    for href, title in re.findall(r'<a[^>]+href=[\'\"]([^\'\"]+)[\'\"][^>]*>(.*?)</a>', list_html, flags=re.IGNORECASE | re.DOTALL):
        clean_title = _clean_text(title)
        href_lower = href.lower()
        if len(clean_title) < 8:
            continue
        if any(skip in href_lower for skip in ('javascript:', '#', 'mailto:')):
            continue
        full = _normalize_link(href, base_url)
        if full in seen:
            continue
        if not re.search(r'\.(s?html?)($|\?)', full, flags=re.IGNORECASE):
            continue
        if '/zfxxgk/' not in full:
            continue
        seen.add(full)
        links.append(full)
    return links


def _extract_links_from_dynamic_feed(list_html: str, base_url: str) -> list[str] | None:
    feed_url = _guess_dynamic_feed_url(list_html, base_url)
    if not feed_url:
        return None

    feed_text = _fetch_html(feed_url)
    try:
        payload = json.loads(feed_text)
    except json.JSONDecodeError as exc:
        raise CrawlerError(f'动态列表数据解析失败：{feed_url}') from exc

    rows = payload.get('data')
    if not isinstance(rows, list):
        raise CrawlerError(f'动态列表数据格式异常：{feed_url}')

    links: list[str] = []
    seen: set[str] = set()
    for item in rows:
        if not isinstance(item, dict):
            continue
        href = str(item.get('URL') or '').strip()
        title = _clean_text(str(item.get('FILENAME') or ''))
        if not href or len(title) < 8:
            continue
        full = _normalize_link(href, base_url)
        if full in seen:
            continue
        if '/zfxxgk/' not in full:
            continue
        if not re.search(r'\.(s?html?)($|\?)', full, flags=re.IGNORECASE):
            continue
        seen.add(full)
        links.append(full)
    return links


def _guess_dynamic_feed_url(list_html: str, base_url: str) -> str | None:
    html_lower = list_html.lower()
    parsed = urlparse(base_url)
    path_lower = parsed.path.lower()
    for script_name, json_name in DYNAMIC_LIST_FEEDS:
        if script_name in html_lower or script_name.replace('.js', '') in path_lower:
            return urljoin(base_url, json_name)
    return None


def _normalize_link(href: str, base_url: str) -> str:
    full = urljoin(base_url, href)
    parsed_full = urlparse(full)
    parsed_base = urlparse(base_url)
    if parsed_full.hostname and parsed_full.hostname == parsed_base.hostname and parsed_base.scheme:
        full = parsed_full._replace(scheme=parsed_base.scheme, fragment='').geturl()
    return full


_ORG_SUFFIXES = ('厅', '局', '委', '部', '办', '院', '中心', '会', '所', '站', '处', '司', '署')
_POLICY_KEYWORDS = ('关于', '通知', '意见', '办法', '规定', '方案', '条例', '公告', '公示', '通报', '规划', '实施', '措施', '决定', '批复')


def _is_likely_org_name(text: str) -> bool:
    """Check if text looks like an organization name rather than a policy title."""
    text = text.strip()
    if not text or len(text) < 3:
        return True
    if text.endswith(_ORG_SUFFIXES):
        if len(text) <= 20 and not any(kw in text for kw in _POLICY_KEYWORDS):
            return True
    return False


def _strip_site_suffix(title: str) -> str:
    """Remove trailing site name (e.g. '-湖北省农业农村厅') from a <title> tag value."""
    for sep in ('--', '—', ' - ', ' _ ', ' | ', '-', '_', '|'):
        idx = title.rfind(sep)
        if idx <= 0:
            continue
        suffix = title[idx + len(sep):].strip()
        if suffix and _is_likely_org_name(suffix):
            return title[:idx].strip()
    return title


def _title_score(text: str) -> int:
    """Score a title candidate; higher is better."""
    if not text:
        return -1000
    score = len(text)
    if _is_likely_org_name(text):
        score -= 500
    if _strip_site_suffix(text) != text:
        score -= 200
    for kw in _POLICY_KEYWORDS:
        if kw in text:
            score += 100
    if re.search(r'[〔\[（(]\d{4}[〕\]）)]\d*号', text):
        score += 50
    return score


def _pick_best_title(candidates: list[str]) -> str:
    """Pick the best policy title from candidates using a scoring heuristic."""
    if not candidates:
        return ''
    scored = [(c, _title_score(c)) for c in candidates if c]
    if not scored:
        return ''
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[0][0]


def _extract_title_candidates(page_html: str, body_text: str) -> list[str]:
    """Extract multiple title candidates from various HTML sources."""
    candidates: list[str] = []

    h2 = _clean_text(_first_match([r'<h2[^>]*>(.*?)</h2>'], page_html))
    if h2 and len(h2) > 6:
        candidates.append(h2)

    h1 = _clean_text(_first_match([r'<h1[^>]*>(.*?)</h1>'], page_html))
    if h1:
        candidates.append(h1)

    meta_article = _clean_text(_first_match([
        r'<meta[^>]+name=[\'"]ArticleTitle[\'"][^>]+content=[\'"]([^\'"]+)[\'"]',
        r'<meta[^>]+content=[\'"]([^\'"]+)[\'"][^>]+name=[\'"]ArticleTitle[\'"]',
    ], page_html))
    if meta_article:
        candidates.append(meta_article)

    og_title = _clean_text(_first_match([r'<meta[^>]+property=[\'"]og:title[\'"][^>]+content=[\'"]([^\'"]+)[\'"]'], page_html))
    if og_title:
        candidates.append(og_title)

    raw_title = _clean_text(_first_match([r'<title[^>]*>(.*?)</title>'], page_html))
    if raw_title:
        cleaned = _strip_site_suffix(raw_title)
        if cleaned and cleaned != raw_title:
            candidates.append(cleaned)
        else:
            candidates.append(raw_title)

    title_class_patterns = (
        r'class=[\'"][^\'\"]*article[_-]?title[^\'\"]*[\'"]',
        r'class=[\'"][^\'\"]*detail[_-]?title[^\'\"]*[\'"]',
        r'class=[\'"][^\'\"]*ewb[_-].*?title[^\'\"]*[\'"]',
        r'class=[\'"][^\'\"]*xxgk[_-].*?title[^\'\"]*[\'"]',
        r'class=[\'"][^\'\"]*con[_-]?title[^\'\"]*[\'"]',
    )
    for pattern in title_class_patterns:
        match = re.search(rf'<[^>]+{pattern}[^>]*>(.*?)</[^>]+>', page_html, flags=re.IGNORECASE | re.DOTALL)
        if match:
            text = _clean_text(match.group(1))
            if text and len(text) > 6:
                candidates.append(text)

    h4 = _clean_text(_first_match([r'<h4[^>]*>(.*?)</h4>'], page_html))
    if h4 and len(h4) > 8:
        candidates.append(h4)

    if not candidates:
        candidates.append(body_text[:60])

    return candidates


def _parse_article_page(page_html: str, *, link: str, source: CrawlerSource) -> dict[str, Any]:
    body_text = _page_text(page_html)
    if len(body_text) < 120:
        raise CrawlerError('页面正文过短')

    title_candidates = _extract_title_candidates(page_html, body_text)
    title = _pick_best_title(title_candidates) or body_text[:60]
    meta_text = _clean_text(page_html[:12000])

    file_type = _determine_file_type(link, page_html, source)
    column_name = _extract_column_name(page_html, body_text, file_type)
    file_category = _extract_file_category(link, title=title, page_html=page_html, body_text=body_text, file_type=file_type)
    topic_category = _extract_topic_category(meta_text, body_text)

    publish_date = _extract_publish_date(meta_text) or _extract_publish_date(body_text)
    effective_date, expiry_date = _extract_dates(meta_text, body_text)
    validity_status = _extract_validity_status(meta_text, body_text, effective_date=effective_date, expiry_date=expiry_date)

    doc_no = _extract_doc_no(meta_text, body_text)
    issuer = _extract_issuer(meta_text, body_text, source)
    attachments = _extract_attachment_urls(page_html, link)

    html_text = body_text[:20000]
    full_text = body_text[:40000]

    return {
        'title': title,
        'issuer': issuer,
        'doc_no': doc_no,
        'publish_date': publish_date,
        'column': column_name,
        'file_category': file_category,
        'topic_category': topic_category,
        'file_type': file_type,
        'validity_status': validity_status,
        'effective_date': effective_date,
        'expiry_date': expiry_date,
        'page_url': link,
        'attachment_urls': attachments,
        'html_text': html_text,
        'attachment_text': '',
        'full_text': full_text,
        'source_id': source.id,
    }


def _first_match(patterns: list[str], text: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
    return ''


def _page_text(value: str) -> str:
    value = re.sub(r'(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>', ' ', value or '')
    return _clean_text(value)


def _clean_text(value: str) -> str:
    value = re.sub(r'(?is)<[^>]+>', ' ', value or '')
    value = html.unescape(value)
    value = value.replace('\u3000', ' ')
    value = re.sub(r'\s+', ' ', value)
    return value.strip()


def _extract_named_value(text: str, label: str, max_len: int = 120) -> str | None:
    pattern = rf'{re.escape(label)}\s*[:：]?\s*(.+?)(?=(?:{META_STOP_PATTERN})\s*[:：]?|$)'
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    value = _clean_text(match.group(1))
    if not value:
        return None
    return value[:max_len]


def _extract_publish_date(text: str) -> str | None:
    for label in ('发文日期', '发布日期', '成文日期'):
        value = _extract_named_value(text, label)
        if value:
            normalized = _normalize_date_string(value)
            if normalized:
                return normalized
    return _normalize_date_string(text)


def _extract_dates(*texts: str) -> tuple[str | None, str | None]:
    effective_date: str | None = None
    expiry_date: str | None = None
    for text in texts:
        if not text:
            continue
        for label in ('生效日期', '施行日期'):
            value = _extract_named_value(text, label)
            if value and not effective_date:
                effective_date = _normalize_date_string(value)
        for label in ('失效日期', '有效期至'):
            value = _extract_named_value(text, label)
            if value and not expiry_date:
                expiry_date = _normalize_date_string(value)
        if not effective_date:
            match = re.search(r'自\s*(20\d{2}[年\-/.]\d{1,2}[月\-/.]\d{1,2}日?)\s*起(?:施行|生效)', text)
            if match:
                effective_date = _normalize_date_string(match.group(1))
        if not expiry_date:
            match = re.search(r'(?:有效期至|至)\s*(20\d{2}[年\-/.]\d{1,2}[月\-/.]\d{1,2}日?)', text)
            if match:
                expiry_date = _normalize_date_string(match.group(1))
    return effective_date, expiry_date


def _normalize_date_string(text: str | None) -> str | None:
    if not text:
        return None
    match = re.search(r'(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})', text)
    if not match:
        return None
    year, month, day = match.groups()
    try:
        return dt.date(int(year), int(month), int(day)).isoformat()
    except ValueError:
        return None


def _parse_optional_date(value: Any) -> dt.date | None:
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _determine_file_type(url: str, html_content: str, source: CrawlerSource) -> str | None:
    if source.file_type:
        return source.file_type
    url_lower = url.lower()
    html_lower = html_content.lower()
    if 'gfxwj_gk2020' in url_lower or '规范性文件' in html_content:
        return 'gfxwj'
    if 'qtzdgkwj_gk2020' in url_lower or '其他主动公开文件' in html_content:
        return 'qtzd'
    if 'zcjd_gk2020' in url_lower or '政策解读' in html_content:
        return 'zcjd'
    source_name = source.name.lower()
    if '规范性' in source.name or 'gfxwj' in source_name:
        return 'gfxwj'
    if '其他主动公开' in source.name or 'qtzd' in source_name:
        return 'qtzd'
    if '政策解读' in source.name or 'zcjd' in source_name:
        return 'zcjd'
    if 'qtzdgkwj_gk2020' in html_lower:
        return 'qtzd'
    return None


def _extract_validity_status(
    meta_text: str,
    body_text: str,
    *,
    effective_date: str | None,
    expiry_date: str | None,
) -> str:
    explicit = None
    for text in (meta_text, body_text):
        value = _extract_named_value(text, '效力状态')
        if value:
            explicit = value
            break
    haystack = f'{explicit or ""} {meta_text} {body_text}'
    patterns = [
        (r'废止|已废止|废除|作废', '废止'),
        (r'失效|已失效|失去效力', '失效'),
        (r'已修改|已修订|修订后|修改后', '已修改'),
        (r'待生效|尚未生效|即将生效', '待生效'),
        (r'现行有效|继续有效|有效', '有效'),
    ]
    for pattern, status in patterns:
        if re.search(pattern, haystack):
            return status

    today = dt.date.today()
    effective_obj = _parse_optional_date(effective_date)
    expiry_obj = _parse_optional_date(expiry_date)
    if effective_obj and effective_obj > today:
        return '待生效'
    if expiry_obj and expiry_obj < today:
        return '失效'
    return '有效'


def _extract_doc_no(meta_text: str, body_text: str) -> str | None:
    for label in ('发文字号', '文号'):
        value = _extract_named_value(meta_text, label)
        if value:
            return value
    for pattern in (
        r'(鄂农[^\s，。；]{0,40}号)',
        r'(鄂政[^\s，。；]{0,40}号)',
        r'(〔\d{4}〕\d+号)',
    ):
        match = re.search(pattern, body_text)
        if match:
            return _clean_text(match.group(1))
    return None


def _extract_issuer(meta_text: str, body_text: str, source: CrawlerSource) -> str:
    for label in ('发布机构', '发文机构', '发布单位'):
        value = _extract_named_value(meta_text, label)
        if value:
            return value
    if '湖北省农业农村厅' in body_text:
        return '湖北省农业农村厅'
    return source.name.split('-', 1)[0]


def _extract_column_name(page_html: str, body_text: str, file_type: str | None) -> str:
    breadcrumb = _clean_text(_first_match([r'<div[^>]+class=[\'\"][^\'\"]*crumb[^\'\"]*[\'\"][^>]*>(.*?)</div>'], page_html))
    if breadcrumb:
        for label in FILE_TYPE_LABELS.values():
            if label in breadcrumb:
                return label
    if file_type:
        return FILE_TYPE_LABELS.get(file_type, file_type)
    if '政策解读' in body_text:
        return '政策解读'
    return '政策抓取'


def _extract_file_category(link: str, *, title: str, page_html: str, body_text: str, file_type: str | None) -> str | None:
    parsed = urlparse(link)
    for part in parsed.path.split('/'):
        if part in URL_CATEGORY_LABELS:
            return URL_CATEGORY_LABELS[part]
    if file_type == 'zcjd':
        if '图解' in title or '图解' in body_text:
            return '图解'
        if '视频' in title or '视频' in body_text:
            return '视频解读'
        if '问答' in title or '问答' in body_text:
            return '问答解读'
        return '文字解读'
    breadcrumb = _clean_text(_first_match([r'<div[^>]+class=[\'\"][^\'\"]*crumb[^\'\"]*[\'\"][^>]*>(.*?)</div>'], page_html))
    for label in URL_CATEGORY_LABELS.values():
        if label in breadcrumb:
            return label
    return FILE_TYPE_LABELS.get(file_type or '')


def _extract_topic_category(meta_text: str, body_text: str) -> str | None:
    for label in ('主题分类', '分类'):
        value = _extract_named_value(meta_text, label)
        if value and value not in FILE_TYPE_LABELS.values() and value not in VALIDITY_STATUSES:
            return value
    match = re.search(r'分类\s*[:：]?\s*(农业|畜牧业|渔业|种植业|农机|乡村振兴|农村改革)', body_text)
    if match:
        return match.group(1)
    return None


def _extract_attachment_urls(page_html: str, base_url: str) -> list[str]:
    attachments: list[str] = []
    seen: set[str] = set()
    for href in re.findall(r'<a[^>]+href=[\'\"]([^\'\"]+)[\'\"]', page_html, flags=re.IGNORECASE):
        full = urljoin(base_url, href)
        lower = full.lower()
        if any(lower.endswith(f'.{ext}') or f'.{ext}?' in lower for ext in ATTACHMENT_EXTENSIONS):
            if full not in seen:
                seen.add(full)
                attachments.append(full)
    return attachments
