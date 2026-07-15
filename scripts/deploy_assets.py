#!/usr/bin/env python3
import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone


def _require_env(name: str) -> str:
    import os

    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy generated assets to Copilot Studio target environment.")
    parser.add_argument("--generated-dir", required=True, type=pathlib.Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    generated_dir = args.generated_dir
    required_files = [
        generated_dir / "agent-definition.json",
        generated_dir / "workflow-definition.json",
        generated_dir / "deployment-manifest.json",
    ]
    missing = [str(p) for p in required_files if not p.exists()]
    if missing:
        raise RuntimeError(f"Missing generated files: {', '.join(missing)}")

    status = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "dry-run" if args.dry_run else "live",
        "state": "validated",
        "notes": [],
    }

    if args.dry_run:
        status["notes"].append("Dry run mode: deployment hooks validated but no remote APIs invoked.")
    else:
        _require_env("TENANT_ID")
        _require_env("COPILOT_STUDIO_ENVIRONMENT_ID")
        _require_env("AZURE_CLIENT_ID")
        _require_env("AZURE_TENANT_ID")
        _require_env("AZURE_SUBSCRIPTION_ID")
        status["notes"].append(
            "Authentication variables found. Replace this hook with Copilot Studio/Power Platform deploy API calls."
        )
        status["state"] = "submitted"

    (generated_dir / "sync-status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print("Deployment stage completed.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
