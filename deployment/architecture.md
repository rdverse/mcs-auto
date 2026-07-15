# Autonomous Copilot Studio Agent Factory Architecture

## 1) Architecture Document

### Objective
Implement an end-to-end GitHub-native factory that converts declarative specs into deployable Copilot Studio agents and workflows.

### Logical Components
1. **Spec Ingestion Layer** (`specs/`)
   - Canonical source of truth for agent/workflow intent.
2. **Validation & Normalization Layer** (`scripts/validate_specs.py`)
   - Enforces schema/quality gates before generation.
3. **Generation Layer** (`scripts/generate_assets.py`, `templates/`)
   - Produces environment-agnostic intermediate artifacts.
4. **Deployment Layer** (`scripts/deploy_assets.py`)
   - Handles authentication checks and deploy hook invocation.
5. **Post-Deployment Validation Layer** (`scripts/smoke_test.py`)
   - Verifies generated/deployed artifacts and sync status.
6. **CI/CD Orchestration Layer** (`.github/workflows/agent-factory.yml`)
   - Build/Test/Deploy/Post-Deploy stages.

### Data Flow
1. Commit to `specs/**` triggers pipeline.
2. Specs are validated.
3. Intermediate JSON assets are generated into `generated/`.
4. Unit tests and script checks run.
5. Deploy stage executes (live if required secrets exist; otherwise deterministic dry-run).
6. Sync status is emitted to `generated/sync-status.json`.
7. Smoke tests validate the final output package.

---

## 2) Repository Structure and Rationale

- `specs/`: declarative inputs (agent, workflow, requirements)
- `skills/`: submodule mountpoint for reusable generation/deployment skills
- `workflows/`: submodule mountpoint for custom workflow implementations
- `templates/`: intermediate artifact templates
- `scripts/`: validate, generate, deploy, smoke logic
- `generated/`: generated machine-readable artifacts and sync status
- `deployment/`: architecture + governance docs
- `.github/workflows/`: CI/CD automation

---

## 3) CI/CD Design (Build/Test/Deploy/Post-Deploy)

Implemented in `.github/workflows/agent-factory.yml`.

### Build
- Validates specs.
- Generates artifacts.
- Uploads artifact bundle.

### Test
- Executes focused script-level unit tests.

### Deploy
- Uses OIDC-ready Azure login step (when secrets exist).
- Runs deployment script in live mode when environment/auth is fully configured.
- Falls back to dry-run to preserve deterministic CI behavior in non-prod environments.

### Post-Deployment
- Runs smoke tests and health assertions against generated/sync outputs.

---

## 4) Security Design (Authentication + Secret Strategy)

### Recommended Enterprise Pattern
1. **GitHub OIDC federation (recommended default)**:
   - No long-lived cloud credentials in GitHub secrets.
   - Trust policy limits token issuance to specific repo/ref/environment.
2. **Service Principal (supported today)**:
   - Use federated credential with Azure Entra app registration.
3. **Managed Identity (best for self-hosted runners in Azure)**:
   - Prefer when runners live in controlled Azure network.
4. **Power Platform/Copilot Studio target auth**:
   - Store tenant/environment identifiers as non-secret variables where possible.
   - Keep privileged app IDs and environment credentials in GitHub Environments with approvals.

### Secret Management
- Use GitHub Environments + required reviewers for production.
- Scope secrets to environment, not repository-wide by default.
- Rotate principal credentials and audit workflow identity usage.

---

## 5) MVP Plan (Buildable Today)

1. Canonical YAML specs for deterministic generation.
2. Validation + generation scripts.
3. GitHub Actions pipeline with build/test/deploy/post-deploy.
4. Dry-run deployment mode for portable CI.
5. Live deployment hook points for Copilot Studio/Power Platform APIs and CLI integrations.

---

## 6) Future-State Plan

As platform capabilities mature:
1. Replace deploy hook placeholder with first-class Copilot Studio deployment APIs/CLI.
2. Add bi-directional Git sync of Copilot Studio assets.
3. Add autonomous PR generation, multi-agent orchestration, and policy-driven rollout.
4. Add grounding/evaluation suites with synthetic + real conversation tests.
5. Add environment promotion workflows (Dev -> Test -> Prod) with signed artifacts.

---

## 7) Gap Analysis (Today vs Preview vs Roadmap)

### Supported Today
- GitHub Actions orchestration
- OIDC-based cloud authentication
- Spec-driven generation pipeline patterns
- Power Platform ALM patterns (solution packaging, pipeline-based deployment)

### Preview / Evolving
- Deeper Copilot Studio Git-native integration
- New Copilot Studio UI/workflow model lifecycle hooks
- Rich deployment/sync APIs for agent/workflow artifacts

### Not Yet Fully Supported
- Fully standardized one-command public API for all Copilot Studio agent/workflow deployment paths
- Guaranteed universal parity between all Copilot Studio authoring surfaces and CI deploy surfaces

### Practical Workarounds
- Generate stable intermediate assets now.
- Use deployment adapter scripts that can switch between CLI/API implementations.
- Keep schema contracts versioned to absorb platform changes safely.

---

## 8) Agent Execution Model (Junior Engineer Behavior)

Factory behavior from a new spec:
1. Parse and classify requirement intent.
2. Select templates and reusable skills.
3. Generate agent/workflow/deployment assets.
4. Validate output and run tests.
5. Open PR-ready artifact updates (via normal repo workflow).
6. Execute deployment and post-deployment checks.

---

## 9) Feedback for BizChat

This implementation is a practical MVP scaffold:
- It is production-leaning for CI/CD shape and security posture.
- It is explicit about current platform gaps.
- It is designed to swap in official Copilot Studio deployment/sync APIs as they become generally available, with minimal repo churn.
