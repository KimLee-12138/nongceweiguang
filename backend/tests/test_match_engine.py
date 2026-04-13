from __future__ import annotations

from app.services.match_engine import to_match_summary


def test_match_summary_supports_detailed_tree_and_score():
    condition_tree = {
        'schema_version': '2.0',
        'id': 'root',
        'type': 'group',
        'logic': 'and',
        'must': True,
        'description': '测试根节点',
        'compile_metadata': {
            'compile_quality': 'generated',
            'missing_information': [],
            'uncertain_points': [],
            'generated_by': 'deepseek',
            'reason': '测试',
        },
        'applicable_subjects': ['家庭农场'],
        'children': [
            {'id': 'c1', 'type': 'predicate', 'field': 'area', 'operator': '>=', 'value': 50, 'must': True},
            {'id': 'c2', 'type': 'predicate', 'field': 'green_cert', 'operator': '=', 'value': True, 'must': True},
            {'id': 'c3', 'type': 'predicate', 'field': 'extra_data.crops', 'operator': 'contains', 'value': '水稻', 'must': False},
        ],
    }
    profile = {
        'area': 60,
        'green_cert': False,
        'extra_data': {'crops': ['水稻', '油菜']},
    }

    summary = to_match_summary(condition_tree, profile)

    assert summary['fully_matched'] is False
    assert summary['must_failed'] == 1
    assert summary['should_failed'] == 0
    assert 0.0 < summary['match_score'] < 1.0
    assert any('green_cert' in step for step in summary['action_steps'])
    assert summary['condition_tree_meta']['compile_quality'] == 'generated'
    assert summary['policy_applicable_subjects'] == ['家庭农场']


def test_match_summary_missing_field_produces_action_step():
    condition_tree = {
        'schema_version': '2.0',
        'id': 'root',
        'type': 'group',
        'logic': 'and',
        'must': True,
        'compile_metadata': {
            'compile_quality': 'generated',
            'missing_information': [],
            'uncertain_points': [],
            'generated_by': 'deepseek',
            'reason': '测试',
        },
        'applicable_subjects': [],
        'children': [
            {'id': 'c1', 'type': 'predicate', 'field': 'loan_history', 'operator': 'exists', 'value': True, 'must': True},
        ],
    }
    profile = {'extra_data': {}}

    summary = to_match_summary(condition_tree, profile)

    assert summary['fully_matched'] is False
    assert summary['must_failed'] == 1
    assert any('补充画像字段' in step for step in summary['action_steps'])
    assert 'loan_history' in summary['missing_fields']


def test_match_summary_supports_date_and_range_operators():
    condition_tree = {
        'schema_version': '2.0',
        'id': 'root',
        'type': 'group',
        'logic': 'and',
        'must': True,
        'compile_metadata': {
            'compile_quality': 'generated',
            'missing_information': [],
            'uncertain_points': [],
            'generated_by': 'deepseek',
            'reason': '测试',
        },
        'applicable_subjects': [],
        'children': [
            {'id': 'c1', 'type': 'predicate', 'field': 'extra_data.region', 'operator': 'contains_any', 'value': ['湖北', '武汉'], 'must': True},
            {'id': 'c2', 'type': 'predicate', 'field': 'extra_data.employees', 'operator': 'between', 'value': [5, 30], 'must': True},
            {'id': 'c3', 'type': 'predicate', 'field': 'extra_data.license_expiry', 'operator': 'date_gte', 'value': '2026-01-01', 'must': False},
        ],
    }
    profile = {
        'extra_data': {
            'region': '湖北武汉',
            'employees': 12,
            'license_expiry': '2026-05-01',
        }
    }

    summary = to_match_summary(condition_tree, profile)

    assert summary['fully_matched'] is True
    assert summary['must_failed'] == 0
    assert summary['should_failed'] == 0
