# Agent Factory Requirements

This folder accepts declarative or narrative inputs (YAML, JSON, Markdown, meeting notes).

Current MVP implementation:
- Uses canonical YAML specs (`agent-spec.yaml`, `workflow-spec.yaml`) for deterministic validation/generation.
- Supports extension hooks for additional parsers in `scripts/validate_specs.py`.

Goal:
- A commit to `specs/` should drive autonomous generation, validation, deployment, publish, and sync.
