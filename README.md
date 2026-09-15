# SkillMap AI — Smart Student Career & Opportunity Platform

A full-stack career-guidance platform for students. SkillMap AI builds a digital career
profile per student, assesses skills, identifies gaps, recommends learning paths, matches
careers and job/internship opportunities, and tracks applications end-to-end.

Built for a Smart India Hackathon presentation: clean light UI with navy/blue accents,
dashboards, charts, progress bars, and role-based access for **Students**, **Professors**,
and **Admins**.

**Status:** Phases 0–17 complete — architecture, authentication & role management, student
career profile (personal/academic/career data, projects, certifications, completion
scoring), skill catalog & student skills, the assessment engine (quiz → score → skill
record), skill gap analysis (current vs required levels, priorities and recommended
actions per career), the career matching engine (every career ranked by an explainable
match % from skills, interests, projects and career goal), the personalized learning
roadmap (every skill gap becomes an ordered plan — topic → resources → practice →
assessment → improvement — drawn from a curated resource catalog, with per-student
completion tracking and live progress %), the opportunities module (jobs, internships,
hackathons and competitions browseable with search/filter/sort and full admin lifecycle
management), smart opportunity matching (every posting ranked by a transparent match %
from skills + assessment scores, profile/eligibility affinity and projects — with the
reasoning, signal breakdown and next steps shown, organized into Recommended for you /
Highest match / Closing soon / Recently added rails), application tracking (apply to
an open posting from its detail page, then follow it through the full status lifecycle
— Applied → Submitted → Under Review → Shortlisted → Interview → Selected — on a
visual timeline with notes, deadline and interview-date visibility; admins drive the
pipeline), the career feedback loop (rejected/selected applications produce gap
analyses, learning-resource recommendations and achievements — students accept gaps
into their roadmap; selections appear as achievements on the dashboard), and the
complete student dashboard (career readiness gauge, top skills chart, application
status pie chart, recommended opportunities with match %, upcoming deadlines with
countdown, learning progress, and quick actions — all numbers from the database). See
[docs/ROADMAP.md](docs/ROADMAP.md) for the plan.

## Tech Stack

| Layer      | Technology                                             |
| ---------- | ------------------------------------------------------ |
| Frontend   | React 19 + TypeScript, Vite, Tailwind CSS v4, Recharts |
| Backend    | Python 3, Django 6, Django REST Framework               |
| Database   | PostgreSQL 16 (SQLite fallback for zero-config dev)     |
| Auth       | JWT (`djangorestframework-simplejwt`)                   |
| AI/ML      | Python (scoring & matching services, in `backend/core`) |
| Charts     | Recharts                                               |
| API        | REST, versioned under `/api/v1/`                       |

## Repository Layout

```
.
├── backend/                 # Django project (API server)
│   ├── config/              # Project settings, root urls
│   └── apps/
│       ├── users/           # User model, roles, JWT auth
│       ├── students/        # Student profiles, education, projects, certifications
│       ├── skills/          # Skill catalog, scores, gap records
│       ├── assessments/     # Assessments, questions, attempts
│       ├── careers/         # Career catalog and required skills
│       ├── opportunities/   # Postings + smart matching (skills/profile/projects)
│       ├── applications/    # Application tracking & status lifecycle
│       ├── learning/        # Learning paths and resources
│       ├── recommendations/ # Gap analysis, career & opportunity matching
│       ├── analytics/       # Aggregation endpoints (read-only)
│       ├── notifications/   # In-app notifications
│       └── core/            # Shared permissions, pagination, AI/ML services
├── frontend/                # React + TypeScript SPA
│   └── src/
│       ├── api/             # Axios client + typed endpoint modules
│       ├── auth/            # JWT context, guards
│       ├── components/      # ui/, layout/, charts/ (reusable)
│       ├── pages/           # student/, professor/, admin/, auth/, common/
│       ├── router/          # Single source of truth for routes & nav
│       ├── hooks/           # useAuth, useApi, etc.
│       ├── types/           # TS types mirroring API models
│       └── utils/           # helpers, formatters
├── docs/
│   ├── ARCHITECTURE.md      # Full architecture analysis (this phase)
│   └── ROADMAP.md           # Phase-by-phase build plan
├── docker-compose.yml       # PostgreSQL for local dev
└── .env.example             # Environment variables reference
```

## Quick Start

### 1. Database (optional — SQLite works out of the box)

```bash
docker compose up -d db
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate      # Windows (Git Bash); use bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo          # demo admin/professor/student accounts
python manage.py runserver
```

API root: <http://localhost:8000/api/v1/>

### Admin account (configured manually)

| Role  | Email                        | Notes |
| ----- | ---------------------------- | ----- |
| Admin | `shashankpandey1911@gmail.com` | Set your own password locally (see below). |

The admin account is **not** created by the demo seed command. Create or update it locally:

```bash
# Set or change the admin password (run locally, password is not stored in source)
python manage.py changepassword shashank_admin
```

You can also set the password programmatically for the first time:

```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> u = User.objects.get(email="shashankpandey1911@gmail.com")
>>> u.set_password("<your-password-here>")
>>> u.save()
```

The admin account has `role=ADMIN`, `is_superuser=True` and `is_staff=True`, so it can
log in through the SkillMap login page and access the Admin Dashboard, and it can also
access the built-in Django admin site if enabled.

> Do not hardcode the admin password anywhere. The password is stored only in the database.

### Demo accounts (`python manage.py seed_sih_demo`)

| Role      | Email                    | Password      |
| --------- | ------------------------ | ------------- |
| Professor | `professor@skillmap.ai`  | `Prof@2026`   |
| Student   | `student@skillmap.ai`    | `Student@2026` |

Demo-only credentials (overridable via `DEMO_PROFESSOR_PASSWORD` /
`DEMO_STUDENT_PASSWORD` environment variables). These are used for the SIH presentation
and can be regenerated by re-running the seed command. Admin accounts are never self-serve:
registration only offers Student/Professor roles.

> Password-reset emails are printed to the Django console in development
> (`EMAIL_BACKEND = console` when `DJANGO_DEBUG=true`).

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: <http://localhost:5173/>

## Environment Variables

See [.env.example](.env.example) for the full reference (Django secret, debug flag,
database connection, CORS origins, JWT lifetimes).

## Security

- **JWT**: access (60 min) + refresh (7 days), rotate-on-refresh, blacklisted on logout.
- **Passwords**: PBKDF2 hashing, Django validators (length, complexity, common, numeric).
- **Throttling**: 10/min login, 5/hr register, 3/hr password reset, 1000/hr authenticated.
- **Ownership**: all student data endpoints filter by `request.user` — students cannot see each other's profiles, skills, or applications.
- **Role-based access**: `IsStudent`, `IsProfessor`, `IsAdmin` permission classes on every endpoint.
- **CORS**: whitelist via `CORS_ALLOWED_ORIGINS` env var; no wildcard in production.
- **Security headers**: HSTS, X-Frame-Options DENY, Content-Type nosniff, XSS filter.
- **Input validation**: serializer-level field limits, DRF validates all input; SQL injection protected by Django ORM.
- **File uploads**: avatar validated for size (5 MB max) and type (JPEG/PNG/WebP).
- **Secrets**: all keys (`SECRET_KEY`, `OPENAI_API_KEY`, DB creds) read from environment variables; `.env` is git-ignored; no secrets in frontend code.
- **AI safety**: AI recommendations are guidance only, never auto-applied; rule-based fallback when no AI provider is configured.
- **Test settings**: throttling disabled via `config/settings_test.py` for the test suite.

## Development Process

Built phase-by-phase — each phase ends with a build + error check before moving on.
See [docs/ROADMAP.md](docs/ROADMAP.md) for the plan and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full design.