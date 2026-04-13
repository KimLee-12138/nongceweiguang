from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from typing import Any

from app.services.condition_tree_service import CONDITION_TREE_SCHEMA_VERSION


@dataclass
class PolicyConditionNode:
    id: str
    description: str = ''
    relation: str = 'AND'
    children: list['PolicyConditionNode'] = dataclass_field(default_factory=list)
    field: str | None = None
    operator: str | None = None
    value: Any = None
    must: bool = True
    node_type: str = 'group'
    schema_version: str | None = None
    compile_metadata: dict[str, Any] = dataclass_field(default_factory=dict)
    applicable_subjects: list[str] = dataclass_field(default_factory=list)
    source_quotes: list[str] = dataclass_field(default_factory=list)
    source_locators: list[str] = dataclass_field(default_factory=list)
    notes: list[str] = dataclass_field(default_factory=list)
    confidence: float | None = None

    def to_dict(self) -> dict[str, Any]:
        if self.field and self.operator:
            data: dict[str, Any] = {
                'id': self.id,
                'type': 'predicate',
                'description': self.description,
                'field': self.field,
                'operator': self.operator,
                'value': self.value,
                'must': self.must,
            }
            if self.source_quotes:
                data['source_quotes'] = list(self.source_quotes)
            if self.source_locators:
                data['source_locators'] = list(self.source_locators)
            if self.notes:
                data['notes'] = list(self.notes)
            if self.confidence is not None:
                data['confidence'] = self.confidence
            return data

        logic = (self.relation or 'AND').lower()
        if logic not in ('and', 'or'):
            logic = 'and'
        data = {
            'id': self.id,
            'type': 'group',
            'logic': logic,
            'must': self.must,
            'description': self.description,
            'children': [child.to_dict() for child in self.children],
        }
        if self.id == 'root':
            data['schema_version'] = self.schema_version or CONDITION_TREE_SCHEMA_VERSION
            data['compile_metadata'] = dict(self.compile_metadata or {})
            data['applicable_subjects'] = list(self.applicable_subjects or [])
        if self.source_quotes:
            data['source_quotes'] = list(self.source_quotes)
        if self.source_locators:
            data['source_locators'] = list(self.source_locators)
        if self.notes:
            data['notes'] = list(self.notes)
        if self.confidence is not None:
            data['confidence'] = self.confidence
        return data


@dataclass
class Policy:
    policy_id: int | None
    title: str
    source: str | None
    summary: str
    raw_text_ref: str | None
    root_condition: PolicyConditionNode

    def to_condition_tree(self) -> dict[str, Any]:
        return self.root_condition.to_dict()
