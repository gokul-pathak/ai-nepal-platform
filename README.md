# CodeRabbit PR Review Workflow

This repository is configured for CodeRabbit with scoped review instructions for backend, frontend, docs, and GitHub Actions.

## Branch and PR Policy

- Do all development on a feature branch.
- Open a pull request for every change.
- Do not push direct commits to `main`.

## Typical Workflow

1. Create a feature branch from `main`.
2. Commit your changes on the feature branch.
3. Open a pull request to `main`.
4. Wait for CodeRabbit review comments.
5. Address feedback and push updates to the same branch.
6. Merge only after approvals and required checks pass.

## Scope-Specific CodeRabbit Reviews

CodeRabbit uses `.coderabbit.yaml` path instructions to review these areas independently:

- `backend/**`: backend/API/data/security focus
- `frontend/**`: UI/UX/accessibility/TypeScript focus
- `docs/**`: clarity and correctness focus
- `.github/workflows/**`: CI security and reliability focus

## Exclusions

CodeRabbit review excludes generated/build artifacts, local environments, and sensitive/local-only files, including:

- `node_modules`, `.next`, `dist`, `build`, `coverage`
- `__pycache__`, `.venv`, `.pytest_cache`
- lock files and environment files (`.env*`)

Do not commit real secrets or `.env` files.
