# mcs-auto Agent Factory

This repository is a GitHub-centric **Copilot Studio Agent & Workflow Factory** scaffold.

It enables a spec-driven flow:
1. Commit specs in `specs/`
2. Validate specs in CI
3. Generate intermediate agent/workflow deployment artifacts in `generated/`
4. Run tests and smoke checks
5. Execute deploy/publish hooks (with secure OIDC-based auth wiring)

## Repository Structure

```text
agent-factory/
├── specs/
├── skills/
├── workflows/
├── templates/
├── scripts/
├── generated/
├── deployment/
└── .github/workflows/
```

## Quick Start

```bash
python /home/runner/work/mcs-auto/mcs-auto/scripts/validate_specs.py \
  --agent-spec /home/runner/work/mcs-auto/mcs-auto/specs/agent-spec.yaml \
  --workflow-spec /home/runner/work/mcs-auto/mcs-auto/specs/workflow-spec.yaml

python /home/runner/work/mcs-auto/mcs-auto/scripts/generate_assets.py \
  --agent-spec /home/runner/work/mcs-auto/mcs-auto/specs/agent-spec.yaml \
  --workflow-spec /home/runner/work/mcs-auto/mcs-auto/specs/workflow-spec.yaml \
  --output-dir /home/runner/work/mcs-auto/mcs-auto/generated
```

## Test

```bash
python -m unittest discover -s /home/runner/work/mcs-auto/mcs-auto/tests -p "test_*.py" -v
```

## CI/CD

The end-to-end pipeline is implemented in:
- `/home/runner/work/mcs-auto/mcs-auto/.github/workflows/agent-factory.yml`

Architecture, security, MVP/future-state, and gap analysis are in:
- `/home/runner/work/mcs-auto/mcs-auto/deployment/architecture.md`