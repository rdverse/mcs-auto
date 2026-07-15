#!/usr/bin/env python3
import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List

import yaml


def _load_spec(path: pathlib.Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(raw)
    else:
        data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain an object at the root")
    return data


def _validate_string(data: Dict[str, Any], field: str, errors: List[str]) -> None:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"'{field}' must be a non-empty string")


def _validate_string_list(data: Dict[str, Any], field: str, errors: List[str]) -> None:
    value = data.get(field)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        errors.append(f"'{field}' must be a non-empty list of strings")


def validate_agent_spec(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    _validate_string(data, "name", errors)
    _validate_string(data, "description", errors)
    _validate_string_list(data, "knowledge", errors)
    _validate_string_list(data, "actions", errors)
    _validate_string_list(data, "workflow", errors)
    return errors


def validate_workflow_spec(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    _validate_string(data, "name", errors)
    _validate_string(data, "description", errors)
    _validate_string_list(data, "triggers", errors)
    _validate_string_list(data, "integrations", errors)

    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append("'steps' must be a non-empty list")
    else:
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(f"'steps[{index}]' must be an object")
                continue
            for field in ("name", "type"):
                value = step.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"'steps[{index}].{field}' must be a non-empty string")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate agent and workflow specs.")
    parser.add_argument("--agent-spec", required=True, type=pathlib.Path)
    parser.add_argument("--workflow-spec", required=True, type=pathlib.Path)
    args = parser.parse_args()

    agent = _load_spec(args.agent_spec)
    workflow = _load_spec(args.workflow_spec)

    agent_errors = validate_agent_spec(agent)
    workflow_errors = validate_workflow_spec(workflow)

    if agent_errors or workflow_errors:
        for error in agent_errors:
            print(f"agent-spec: {error}")
        for error in workflow_errors:
            print(f"workflow-spec: {error}")
        return 1

    print("Specification validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
