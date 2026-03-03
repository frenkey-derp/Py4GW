from __future__ import annotations

import json
import os
from typing import Any, Optional

from Py4GW import Console
from Sources.frenkeyLib.ItemHandling.Rules.base_rule import BaseRule
from Sources.frenkeyLib.ItemHandling.Rules.types import ItemAction


def rule_to_dict(rule: BaseRule) -> dict[str, Any]:
    return rule.to_dict()


def rule_from_dict(payload: dict[str, Any]) -> Optional[BaseRule]:
    rule = BaseRule.from_dict(payload)
    if rule is None:
        Console.Log(
            "RuleProfile",
            f"Unknown rule type '{payload.get('rule_type', '')}', skipping.",
            Console.MessageType.Warning,
        )
    return rule


class RuleProfile:
    def __init__(self, name: str, rules: Optional[list[BaseRule]] = None):
        self.name = name
        self.rules: list[BaseRule] = list(rules) if rules else []

    @staticmethod
    def get_profiles_directory() -> str:
        project_path = Console.get_projects_path()
        profile_dir = os.path.join(project_path, "Widgets", "Config", "ItemHandling", "Profiles")
        os.makedirs(profile_dir, exist_ok=True)
        return profile_dir

    @property
    def default_path(self) -> str:
        return os.path.join(self.get_profiles_directory(), f"{self.name}.json")

    def add_rule(self, rule: BaseRule) -> None:
        self.rules.append(rule)

    def remove_rule(self, rule: BaseRule) -> None:
        if rule in self.rules:
            self.rules.remove(rule)

    def get_sorted_rules(self) -> list[BaseRule]:
        # Highest priority first; if equal keep deterministic ordering by name.
        return sorted(self.rules, key=lambda r: (-r.get_priority_score(), r.name.lower()))

    def get_matching_rule(self, item_id: int) -> Optional[BaseRule]:
        for rule in self.get_sorted_rules():
            if rule.applies(item_id):
                return rule
        return None

    def get_action_for_item(self, item_id: int) -> ItemAction:
        rule = self.get_matching_rule(item_id)
        return rule.action if rule else ItemAction.NONE

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": "itemhandling-rule-profile",
            "version": 1,
            "name": self.name,
            "rules": [rule_to_dict(rule) for rule in self.rules],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RuleProfile":
        name = str(payload.get("name", "Default"))
        rules: list[BaseRule] = []
        for row in payload.get("rules", []):
            if not isinstance(row, dict):
                continue
            rule = rule_from_dict(row)
            if rule is not None:
                rules.append(rule)
        return cls(name=name, rules=rules)

    def to_json(self, indent: int = 4) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_payload: str) -> "RuleProfile":
        return cls.from_dict(json.loads(json_payload))

    def save(self, path: Optional[str] = None) -> str:
        target_path = path or self.default_path
        target_directory = os.path.dirname(target_path)
        if target_directory:
            os.makedirs(target_directory, exist_ok=True)

        with open(target_path, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=4)

        return target_path

    @classmethod
    def load(cls, path: str) -> "RuleProfile":
        with open(path, "r", encoding="utf-8") as file:
            payload = json.load(file)
        return cls.from_dict(payload)

    @classmethod
    def load_by_name(cls, name: str) -> "RuleProfile":
        path = os.path.join(cls.get_profiles_directory(), f"{name}.json")
        return cls.load(path)
