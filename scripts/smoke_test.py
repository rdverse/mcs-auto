#!/usr/bin/env python3
import argparse
import json
import pathlib
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Post-deployment smoke validation.")
    parser.add_argument("--generated-dir", required=True, type=pathlib.Path)
    args = parser.parse_args()

    generated_dir = args.generated_dir
    required = [
        "agent-definition.json",
        "workflow-definition.json",
        "deployment-manifest.json",
        "sync-status.json",
    ]

    for file_name in required:
        path = generated_dir / file_name
        if not path.exists():
            raise RuntimeError(f"Required smoke-test artifact not found: {path}")
        json.loads(path.read_text(encoding="utf-8"))

    print("Smoke tests passed.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
