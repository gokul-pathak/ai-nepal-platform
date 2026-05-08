# AI Nepal Platform

Monorepo foundation for a production-ready AI utility platform for Nepal.
This baseline includes a runnable Next.js frontend, FastAPI backend, security-first defaults, CI workflows, and planning docs.

## Tech Stack

- Frontend: Next.js (App Router), TypeScript, Tailwind CSS
- Backend: FastAPI, Pydantic settings, modular API structure
- Tooling: pytest, GitHub Actions CI, CodeRabbit PR review

## Repository Structure

```text
ai-nepal-platform/
  frontend/
  backend/
  docs/
  .github/
  .coderabbit.yaml
  .gitignore
  README.md
  .env.example
```

## Environment Variables

Copy examples and fill values locally. Never commit real secrets.

- Root example: `.env.example`
- Backend example: `backend/.env.example`
- Frontend example: `frontend/.env.example`

Root `.env.example` keys:

```env
DATABASE_URL=
OPENAI_API_KEY=
API_V1_PREFIX=/api/v1
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Local Setup: Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health endpoint:

`GET http://localhost:8000/api/v1/health`

## Local Setup: Frontend

```bash
cd frontend
npm install
npm run dev
```

Default app URL:

`http://localhost:3000`

## Branch and PR Workflow

- Create a feature branch from `main` for each task.
- Open a pull request to `main`.
- Do not commit directly to `main`.
- Merge only after CI checks and review are complete.

## CodeRabbit Review Workflow

CodeRabbit is configured via `.coderabbit.yaml` to review repository areas independently:

- `backend/**`: FastAPI architecture, validation, security, reliability
- `frontend/**`: Next.js quality, accessibility, UX, TypeScript safety
- `docs/**`: clarity, consistency, and implementation alignment
- `.github/workflows/**`: CI security and least-privilege checks

Review exclusions include generated artifacts, dependency directories, local env files, and lock/cache files.

## Security Notes

- Never commit real API keys, tokens, passwords, certificates, or `.env` files.
- Use placeholder/example values only.
- Keep sensitive configuration in local environment files ignored by git.
