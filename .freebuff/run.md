# SkillMap AI — run doc (preview for this thread)

Both servers must be running for the app to work:
- **Backend** (Django) on port 8000
- **Frontend** (Vite dev server) on port 5174

## How to reproduce the artifacts

```sh
# From the repo root:
cd frontend
npm install                         # all deps: react, react-router, recharts, tailwind, etc.
cd ..

cd backend
python -m venv .venv                # if not present
.venv/bin/pip install -r requirements.txt   # DRF, JWT, CORS, psycopg2, etc.
.venv/bin/python manage.py migrate  # all app migrations (users, skills, ... feedback)
.venv/bin/python manage.py seed_demo        # demo users, skills, careers, opportunities,
                                             # applications and career feedback
```

The FE `package.json` scripts:
```json
{ "scripts": { "dev": "vite", "build": "tsc -b && vite build", "lint": "oxlint" } }
```
So `npm run dev` invokes `vite` directly via Vite's CLI (no global install needed).

## How to run the server

### Backend (port 8000)

```sh
cd backend
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

### Frontend (port 5174)

```sh
cd frontend
npm run dev -- --port 5174
```

That is what `run-fe.ps1` does: it starts `npm run dev` from the `frontend/` dir,
redirects stdout/stderr to `.freebuff/preview-*.log` / `.freebuff/preview-*.log.err`,
waits for port 5174 to answer, and exits the script with the Vite PID so the
process keeps running after the script finishes.

### Detached start (Windows)

From the repo root:

```powershell
powershell -NoProfile -Command "(Start-Process -FilePath 'npm.cmd' -ArgumentList 'run','dev' -WorkingDirectory 'frontend' -RedirectStandardOutput '.freebuff\preview-<id>.log' -RedirectStandardError '.freebuff\preview-<id>.log.err' -WindowStyle Hidden -PassThru).Id"
```

Then wait for `http://localhost:5174` to answer (check `Get-Process -Id <pid>` from
the printed pid to confirm it's still alive).

### Environment

- Copy `.env.local` from the main checkout if the worktree lacks it (never symlink
  — ports may differ per worktree).
- Backend picks up `backend/.env` (dev-only secrets); sensitive values come from the
  environment in production.
