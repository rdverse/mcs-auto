#!/usr/bin/env python3
import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone
from typing import Any, Dict

import yaml


def _load_json(path: pathlib.Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain an object at the root")
    return data


def _load_spec(path: pathlib.Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(raw)
    else:
        data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain an object at the root")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate intermediate agent/workflow artifacts.")
    parser.add_argument("--agent-spec", required=True, type=pathlib.Path)
    parser.add_argument("--workflow-spec", required=True, type=pathlib.Path)
    parser.add_argument("--output-dir", required=True, type=pathlib.Path)
    args = parser.parse_args()

    agent = _load_spec(args.agent_spec)
    workflow = _load_spec(args.workflow_spec)

    output_dir: pathlib.Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(timezone.utc).isoformat()

    template_path = pathlib.Path(__file__).resolve().parent.parent / "templates" / "agent-definition.template.json"
    agent_definition = _load_json(template_path)
    agent_definition["generatedAt"] = generated_at
    agent_definition["agent"]["name"] = agent["name"]
    agent_definition["agent"]["description"] = agent["description"]
    agent_definition["agent"]["knowledge"] = agent["knowledge"]
    agent_definition["agent"]["actions"] = agent["actions"]
    agent_definition["workflow"]["steps"] = agent["workflow"]
    workflow_definition = {
        "schemaVersion": "1.0",
        "generatedAt": generated_at,
        "workflow": workflow,
    }
    deployment_manifest = {
        "schemaVersion": "1.0",
        "generatedAt": generated_at,
        "assets": [
            "agent-definition.json",
            "workflow-definition.json",
        ],
        "target": {
            "tenantId": "${TENANT_ID}",
            "environmentId": "${COPILOT_STUDIO_ENVIRONMENT_ID}",
        },
    }

    (output_dir / "agent-definition.json").write_text(
        json.dumps(agent_definition, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "workflow-definition.json").write_text(
        json.dumps(workflow_definition, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "deployment-manifest.json").write_text(
        json.dumps(deployment_manifest, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Generated artifacts in {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
