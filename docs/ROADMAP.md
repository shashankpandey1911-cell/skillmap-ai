# SkillMap AI — Build Roadmap

Phase-based development. **Rule:** after every phase — build, check for errors, fix,
verify features work, and don't break earlier phases.

## Phase 0 — Architecture (✅ done)

- [x] Repo skeleton: `backend/`, `frontend/`, `docs/`, docker-compose, env reference
- [x] Architecture analysis (`docs/ARCHITECTURE.md`)

## Phase 1 — Foundation ✅

- [x] Django project `config` with env-driven settings, DRF, CORS, SimpleJWT
- [x] Custom `User` model + roles (STUDENT / PROFESSOR / ADMIN) + migration
- [x] Vite + React + TS + Tailwind v4 app shell
- [x] Route table + role guards + layout shell (sidebar/topbar)
- [x] `core`: permissions, pagination; modular app layout matching the spec
- [x] **Verify:** `manage.py check` + `npm run build` pass

## Phase 2 — Authentication & Role Management ✅

- [x] `users`: register / login / refresh / logout / me / forgot-password / reset-password
      (SimpleJWT; logout blacklists the refresh token; console email backend in dev)
- [x] `students`: StudentProfile model (college/course/year) created at registration
- [x] RBAC: students/professors/admins each get only their dashboards (403/redirect on cross-role access)
- [x] Role dashboards with real DB-count endpoints (`students`, `professors`, `admin` summaries)
- [x] Frontend: Login / Register / ForgotPassword / ResetPassword pages, AuthContext,
      protected routes + role guards, session persistence, logout
- [x] Seed demo users (`python manage.py seed_demo`)
- [x] 25 API tests covering register/login/logout/protected routes/role restrictions/reset
- [x] **Verify:** end-to-end register → login → role-restriction → logout in the live app

## Phase 3 — Student Career Profile ✅

- [x] `students`: StudentProfile extended (branch, CGPA, semester, achievements,
      career goal, preferred domain, interests) + Project + Certification models
- [x] REST APIs: profile GET/PATCH, projects CRUD, certifications CRUD (owner-scoped 404s)
- [x] Completeness service: per-section (personal/academic/career/projects/certifications)
      + overall score returned with the profile
- [x] Frontend: My Profile page — section cards, edit-profile modal, project & certification
      add/edit/delete with two-step confirm, completion indicator, empty states
- [x] Demo student seeded with a realistic full profile (projects + certifications)
- [x] 11 API tests covering all CRUD, ownership isolation, and completeness math
- [x] **Verify:** 36 tests pass; live CRUD (create/edit/delete) verified in the UI

## Phase 4 — Student Skills Management ✅

- [x] `skills`: Skill catalog (9 categories, 70+ skills) + UserSkill model
      (proficiency 1–5, experience level, assessment score written only by the engine)
- [x] APIs: catalog (search + category filter) and student skills CRUD
      (duplicate-skill validation, owner-scoped 404s, role restrictions)
- [x] Frontend: My Skills page — category cards, search, filter, progress bars /
      percentages, add/edit/delete modals, empty states
- [x] Demo student seeded with 10 skills; dashboard `skills_count` is a real DB count
- [x] 14 API tests covering CRUD, validation, ownership, search/filter
- [x] **Verify:** live add / filter / edit / delete in the UI (JavaScript → 100%)

## Phase 5 — Skill Assessment System ✅

- [x] `assessments`: Assessment / Question / Option / StudentAttempt / StudentAnswer /
      AssessmentResult models
- [x] `core/services/scoring.py` — answers → 0–100 score, proficiency banding, suggestions
- [x] Student flow: browse → start quiz → answer → submit → score + review +
      improvement suggestions; score written back to the student's skill record
- [x] Correct answers never leak pre-submission (student serializers exclude `is_correct`);
      admin question CRUD validates 2–6 options with exactly one correct
- [x] Frontend: Skill Assessments page + interactive QuizRunner (progress, submit,
      result review, attempt history); dashboard/analytics counts are real
- [x] Seed: Python + SQL demo assessments
- [x] 16 API tests covering the full flow, answer-leak prevention, resubmit/ownership
      guards, admin CRUD
- [x] **Verify:** 92 tests pass; live quiz run updates the skill score

## Phase 6 — Skill Gap Analysis ✅

- [x] `careers`: Career + CareerSkillRequirement models (target level 0–100 + importance)
- [x] `core/services/gap.py` — current vs required, gap %, LOW/MEDIUM/HIGH classification,
      priority (importance × gap), recommended actions, overall readiness — pure and
      unit-tested, computed live from the database (never hardcoded)
- [x] APIs: career catalog + detail, `GET /careers/<id>/gap-analysis` (student own;
      professor/admin pass `?student_id=`; cross-role reads forbidden), admin career +
      requirement CRUD (UI lands in the Admin Console phase)
- [x] Frontend: Skill Gap Dashboard — career picker, readiness %, summary cards,
      current vs required bars, gap badge, priority, recommended action
- [x] Seed: 5 demo careers (Backend / Frontend / Full-Stack / Data Scientist / DevOps)
      using the catalog; added DSA + System Design to the catalog
- [x] 26 API tests incl. the exact Phase 6 worked example, boundary classification,
      multiple students & careers, ownership, admin CRUD
- [x] **Verify:** 92 tests pass; live career switch recalcs the dashboard from real data

## Phase 7 — Career Matching Engine ✅

- [x] `careers`: Career gained `domain_keywords` (interest matching) and
      `learning_areas` (recommended learning focus); admin-editable
- [x] `core/services/matching.py` — four explainable signals → 0–100 match %:
      skills (70%, importance-weighted readiness), interests (15%), projects
      (10%), career goal (5%); breakdown + matching/missing skills +
      explanation + next steps all derived from the same inputs
- [x] `GET /careers/matches` — all active careers ranked highest-first
      (student own; professor/admin pass `?student_id=`); every response
      carries the guidance disclaimer (never guaranteed outcomes)
- [x] Frontend: Career Match page — ranked cards with match bar, matching
      (green) / missing (amber) skill chips, explanation, next steps,
      learning areas, match-driver breakdown, expandable career details
- [x] Seed: domain keywords + learning areas backfilled on the 5 demo careers
- [x] 14 new tests: signal math (incl. importance weighting), full/empty
      profiles, rankings differ per student, role access, disclaimer
- [x] **Verify:** 106 tests pass; live page ranks Full-Stack 85% → DevOps 29%
      for the demo student, all from real data

## Phase 8 — Personalized Learning Roadmap ✅

- [x] `learning`: LearningResource model (title, description, skill, level,
      type — Course / Video / Documentation / Practice / Project / Quiz, URL,
      estimated duration) + ResourceCompletion (per-student progress)
- [x] `learning/services.py` — roadmap builder: each open skill gap from the
      Phase 6 engine expands into an ordered path — Learning Topic → Resource
      → Practice → Assessment (quiz items + the platform's published skill
      assessment) → Skill Improvement (target score closes the gap). Resource
      picks are level-aware (a HIGH gap surfaces beginner material first) and
      100% database-driven; progress % = completed ÷ recommended, computed
      live from the student's completion rows
- [x] APIs: `GET /learning/roadmap?career_id=` (student own; professor/admin
      pass `?student_id=`), `GET /learning/resources` catalog with filters,
      `POST/DELETE /learning/resources/<id>/complete`, admin resource CRUD
- [x] Frontend: Learning Roadmap page — career picker, learning progress % /
      completed / remaining cards, roadmap progress bar, priority-skills
      strip, per-skill numbered step timeline with resource completion
      toggles + "Open resource" links; deep-link `?open=` auto-starts a skill
      assessment from the roadmap's Assessment step
- [x] Seed: 73 demo learning resources across the demo career skills
      (Python, Django, SQL, DSA, Git, JS, React, TS, HTML/CSS, Statistics,
      Pandas, ML, Docker, Kubernetes, AWS, Linux …)
- [x] 22 API tests covering roadmap structure/progress, level-aware picks,
      completion toggling, access control, catalog filters, admin CRUD
- [x] **Verify:** 128 tests pass; live page builds Backend (DSA HIGH),
      Data Scientist (Statistics + Pandas HIGH) roadmaps from real data, and
      marking resources moves 0% → 20% → 0%

## Phase 9 — Opportunities Module ✅

- [x] `opportunities`: Opportunity model (title, company, type — JOB /
      INTERNSHIP / HACKATHON / COMPETITION —, description, eligibility,
      location, remote option, deadline, external application link,
      compensation, status ACTIVE / DRAFT / CLOSED) + OpportunityRequirement
      (required skill + minimum 0–100 level)
- [x] `opportunities/services.py` — real per-student match %: average of
      current ÷ required across the posting's skills (missing skill = 0),
      with matching / missing skill lists. Assessment scores override
      self-ratings, exactly like the gap engine
- [x] Student APIs: `GET /opportunities` (search by title/company/description,
      filter by type / location / remote, sort by newest / closest deadline /
      best match; only ACTIVE postings with a future or open deadline are
      shown) + `GET /opportunities/<id>` (full detail incl. eligibility,
      apply link and per-skill my-level vs requirement breakdown)
- [x] Admin APIs (UI lands in the Admin Console phase): full opportunity CRUD,
      `POST /admin/opportunities/<id>/activate | /deactivate`, and nested
      requirement management (unique skill + 0–100 validation)
- [x] Frontend: Opportunities browse page (search box, type pills, location,
      remote-only toggle, sort dropdown, live counts, cards with type badge,
      deadline countdown, compensation, skill chips and match bar) + detail
      page (hero with external "Apply now", about/eligibility cards,
      required-skills level bars with Met/Needs-X%-more states, sticky match
      card with matching/missing chips + guidance disclaimer)
- [x] Seed: 10 realistic Indian-market postings across all four types with
      relative deadlines (Zoho, Razorpay, Walmart GT, CRED, Fractal,
      Freshworks, CloudSek, SIH 2026, Flipkart GRiD, Infosys)
- [x] 25 API tests covering visibility rules (draft/closed/expired hidden),
      search/filter/sort, match math, professor/admin targeting, admin CRUD,
      activate/deactivate visibility, seeding idempotency
- [x] **Verify:** 153 tests pass; live browse/search/filter/sort/detail all
      work in the UI and the admin toggle moves 10 → 9 → 10 listings live

## Phase 10 — Smart Opportunity Matching ✅

- [x] `opportunities/services.py` upgraded to the transparent three-signal engine:
      skills & assessment scores (70%), profile/eligibility affinity (20% — the
      posting's title/company/type/eligibility vocabulary found in the student's
      interests, course, branch and career goal), and projects (10%). A posting
      with no listed skills uses a profile 70% / projects 30% blend instead
- [x] Browse + detail endpoints now compute this canonical match; every payload
      carries a signal breakdown, an explanation, recommended next steps,
      matching/missing skills and `created_at` for rail sorting
- [x] New `GET /opportunities/recommendations` — every active posting ranked by
      match, best first, with the guidance disclaimer (never a guarantee of
      selection); students get their own, professors/admins pass `?student_id=`
- [x] Frontend: Opportunity Matches page with four rails — **Recommended for
      you** (≥ 60% fit), **Highest match**, **Closing soon** (≤ 14 days) and
      **Recently added** — each with live counts; cards show the score, ✓
      matching-skill and ⚠ gap chips, the human-readable “why”, per-signal
      breakdown bars and next steps; the detail page shows the same reasoning
- [x] 34 API tests (9 new): signal combination math, no-requirement fallback,
      ranking order, rail fields, disclaimer, role access (professor needs
      `student_id`, students can’t read others)
- [x] **Verify:** 162 tests pass; live rails rank the demo student’s matches
      (Zoho intern 85% → Infosys 82% → …), closing-soon filters correctly, and
      every card explains its score from real data

## Phase 11 — Application Tracking ✅

- [x] `applications`: Application model — student, opportunity, applied date,
      status (APPLIED → SUBMITTED → UNDER_REVIEW → SHORTLISTED → INTERVIEW →
      SELECTED, with REJECTED as a terminal outcome), notes and interview
      date — unique per (student, opportunity), so one posting = one tracker
- [x] Student APIs: apply to an open posting (`POST`; ACTIVE + future/open
      deadline enforced, duplicates rejected with 409), list with status &
      search filters, owner-only detail, and PATCH that lets the student add
      notes but nothing else (status/interview_date rejected)
- [x] Staff/admin APIs: professors/admins list one student's applications via
      `?student_id=`; admins get the cross-student list (status/search
      filters, student info) and drive the pipeline — PATCH status,
      interview_date and notes only, no other fields
- [x] Opportunity detail now reports `my_application`, so the UI switches
      between an Apply button and an Applied/Track state
- [x] Frontend: My Applications page — status filter pills with live counts,
      search, per-application cards with deadline countdown + interview-date
      chip, an inline notes editor, and the visual pipeline timeline (checked
      ✓ steps up to the CURRENT stage; rejection/selection banners)
- [x] Apply button on the opportunity detail page (with the external company
      portal kept as a secondary link); success flips the hero to Track
- [x] Seed: 3 demo applications at different stages for the demo student
- [x] 16 API tests covering apply rules, duplicate/expired rejection, owner
      isolation, filters, notes-only student edits, admin status/interview
      updates, and role guards
- [x] **Verify:** 178 tests pass; live apply → timeline → notes → admin
      status change (Shortlisted → Interview + date) all reflected in the UI

## Phase 12 — Career Feedback Loop ✅

- [x] `feedback` app: ApplicationFeedback + FeedbackGap models — auto-generated
      when admin moves an application to REJECTED or SELECTED; idempotent
      (always rebuilds content so re-seeds fix broken rows)
- [x] Feedback engine: compares opportunity requirements vs student skills;
      classifies gaps as HIGH / MEDIUM / LOW; recommends learning resources;
      generates explanation + next-steps text; carries the guidance disclaimer
- [x] Student APIs: list with kind/status filters, detail, PATCH notes, accept
      (adds gaps to roadmap), dismiss; professor/admin can read via student_id
- [x] Accept → builds a feedback roadmap section; dismiss → sets DISMISSED;
      nothing auto-changes the student's profile without consent
- [x] Learning view merges feedback roadmap into career roadmap with unique
      resource counting (deduped: ticking a shared resource moves progress once)
- [x] Dashboard summary: achievements count, selected applications list,
      pending-feedback count
- [x] Frontend: Career Improvement page (`/student/improvement`) — filter pills
      (All / Rejected / Achievements / Pending / Accepted / Dismissed), per-
      feedback cards with gap analysis, progress bars, resource links, accept/
      dismiss actions, notes editor, roadmap link, and selection achievement cards
- [x] Dashboard: Career achievements section with selection count + list
- [x] Learning Roadmap: 'FROM APPLICATION FEEDBACK' section with accepted
      rejection skills + deduped progress
- [x] Demo seed: REST API skill + resources, PhonePe + Infosys postings,
      2 feedback entries (1 rejected/accepted, 1 selected/pending)
- [x] 17 feedback tests covering generation, idempotency, accept/dismiss,
      notes, professor access, role guards; full suite 195/195 green
- [x] **Verify:** build + lint clean; live E2E — accept adds to roadmap,
      dashboard shows achievement, roadmap shows feedback section with deduped
      progress (1→2 of 8 unique = 25%) — verified in Preview tab

## Phase 13 — Complete Student Dashboard ✅

- [x] Enhanced `StudentDashboardSummaryView` with real data: career readiness
      score (from gap analysis), top skills, skill gaps count, career matches,
      recommended opportunities with match %, learning progress, application
      status breakdown, upcoming deadlines, and achievements
- [x] Frontend: comprehensive dashboard with stat cards (Career Readiness,
      Top Skills, Skill Gaps, Applications, Interviews), career readiness
      gauge, top skills bar chart, applications pie chart, recommended
      opportunities with match badges, profile completeness ring, learning
      progress ring, upcoming deadlines with countdown, career achievements
      list, and quick action links
- [x] All numbers sourced from database — no fake or hardcoded data
- [x] **Verify:** 195/195 tests pass; build + lint clean; live dashboard shows
      real stats (80% readiness, 11 skills, 6 applications, 1 interview)

## Phase 14 — Professor Dashboard ✅

- [x] `professors` app: GuidanceNote + RecommendedResource models with migration
- [x] Student list endpoint (`GET /professors/students`) with search, branch/year/
      college filters, and ordering — returns profile completeness, skills count,
      and career readiness per student
- [x] Student dossier endpoint (`GET /professors/students/<id>/dossier`) — full
      profile, skills with proficiency %, assessment results, skill gaps with
      priority and recommended action, career readiness gauge, projects,
      certifications, and applications
- [x] Guidance endpoints: list, add, delete notes (professor owns their notes)
- [x] Analytics endpoint (`GET /professors/analytics`) — total students, career
      ready count, students with gaps, avg assessment score, popular career goals,
      common skill gaps, students-by-year distribution, readiness distribution
- [x] Frontend: Student list page with search bar, branch/year/college filters,
      sort options, and cards showing readiness/skills/profile at a glance
- [x] Frontend: Student dossier page with tabs (Overview, Skills, Gaps,
      Applications, Guidance) — full profile, gap analysis with progress bars,
      application timeline, and inline guidance form with category and delete
- [x] Frontend: Analytics dashboard with stat cards, readiness distribution
      pie chart, students-by-year bar chart, popular career goals list,
      and common skill gaps list
- [x] 13 professor tests: student list/search/access, dossier access, guidance
      CRUD and ownership, analytics access and role guards
- [x] **Verify:** 208/208 tests pass; build + lint clean; professor can view
      students, open dossier, add guidance, see analytics charts

## Phase 15 — Admin Console ✅

- [x] `admins` app: comprehensive CRUD views for all platform entities — users
      (list/create/detail with search, role filter, active toggle, role change,
      delete), skills (list/create/detail with category/search/active filter),
      careers (list/create/detail with search/active filter), assessments
      (list/create/detail with skill/search filter, publish toggle),
      opportunities (list/create/detail with type/status/search filter,
      activate/deactivate), learning resources (list/create/detail with
      skill/search/type filter), and applications (list with status/search filter)
- [x] Admin notifications: `POST /admin/notifications/send` broadcasts to all
      users, students only, or professors only (bulk create)
- [x] Admin analytics endpoint (`GET /admin/analytics`) — total users, students,
      professors, admins, skills, careers, assessments, opportunities,
      applications, resources, selected students, active opportunities,
      published assessments, users-by-role distribution, users-by-month
      (last 12), popular skills (by student count), popular careers (by
      requirement count), applications-by-status breakdown, and common
      skill gaps (required but under-supplied)
- [x] All admin endpoints require `IsAdmin` permission — students and
      professors get 403
- [x] Frontend: full admin layout with sidebar navigation (9 sections),
      mobile-responsive with hamburger menu, logout
- [x] Frontend: Users page — table with search, role filter, role dropdown,
      active/inactive toggle, delete, and create modal
- [x] Frontend: Skills page — card grid with search, category filter,
      active toggle, delete, and create modal
- [x] Frontend: Careers page — list with search, active toggle, delete,
      create modal with all fields
- [x] Frontend: Assessments page — list with search, publish toggle, delete,
      create modal with skill ID, difficulty, duration
- [x] Frontend: Opportunities page — list with search, type/status filters,
      activate/deactivate, delete, create modal with all fields
- [x] Frontend: Learning Resources page — card grid with search, type filter,
      delete, create modal with all fields
- [x] Frontend: Applications page — table with search, status filter,
      student/opportunity info, status badges
- [x] Frontend: Notifications page — compose with target audience selector,
      title, body, send button
- [x] Frontend: Analytics dashboard — 8 stat cards, users-by-role pie chart,
      applications-by-status pie chart, popular skills bar chart, popular
      careers bar chart, common skill gaps list
- [x] 14 admin tests: dashboard access, user CRUD/role toggle, skill CRUD,
      career CRUD, opportunity CRUD, analytics access, role guards
- [x] **Verify:** 208 tests pass; build + lint clean; admin CRUD mutates
      the database and analytics charts render real data

## Phase 16 — Hardening & Polish ✅

- [x] Toast notification system (`ToastProvider` + `useToast` hook) — global
      success/error/info toasts with auto-dismiss and slide-in animation
- [x] Reusable `EmptyState` component — consistent empty states across all
      pages with icon, title, description, and optional action button
- [x] Reusable `LoadingOverlay` component — full-page loading spinner
- [x] `useFormValidation` hook — declarative field rules (required, minLength,
      maxLength, pattern, custom), touched tracking, validateAll, reset
- [x] Input component has built-in `error` and `hint` props with inline
      validation messages and red focus ring on invalid state
- [x] Admin dashboard updated — quick-action buttons replace the Phase 7
      placeholder card
- [x] Seed script `--reset` flag — `python manage.py seed_demo --reset`
      deletes existing demo data and reseeds from scratch
- [x] README updated with Phase 15–16 status, demo credentials table,
      repository layout, and development process
- [x] All admin CRUD pages use toast notifications for create/update/delete
- [x] **Verify:** build + lint clean; admin CRUD shows success toasts;
      ToastProvider wraps the entire app; seed_demo --reset works

## Phase 17 — Database-Backed Notifications ✅

- [x] `notifications` app: Notification model with 8 types — OPPORTUNITY_MATCH,
      APPLICATION_STATUS, DEADLINE_REMINDER, SKILL_GAP, ASSESSMENT_RESULT,
      LEARNING_RECOMMEND, PROFESSOR_GUIDANCE, SYSTEM — plus user FK, title,
      body, link, read_at, created_at
- [x] Notification service (`services.py`) — 7 trigger functions that create
      notifications for each event type with 5-minute deduplication to
      prevent spam
- [x] API endpoints: `GET /notifications` (list with unread/limit filters),
      `GET /notifications/unread-count`, `POST /notifications/<id>/read`,
      `POST /notifications/read-all`
- [x] Hooks into existing features: application status changes trigger
      APPLICATION_STATUS, assessment submissions trigger ASSESSMENT_RESULT,
      professor guidance creates PROFESSOR_GUIDANCE
- [x] Admin broadcast endpoint updated to use the new model fields
- [x] Frontend: `NotificationBell` component — bell icon with red unread badge,
      dropdown panel with type-specific emoji icons, title, body, time-ago,
      per-notification mark-as-read, mark-all-read button, polling every 30s
- [x] Integrated into student topbar, admin layout topbar, and professor layout
- [x] 16 notification tests: list/unread/filter/limit, mark-read/mark-all,
      service functions (all 7 types), deduplication, role access
- [x] **Verify:** 224+ tests pass; build + lint clean; bell shows unread count,
      panel shows 5 real notifications, mark-all-read clears the badge

## Phase 18 — Security Review ✅

- [x] **Authentication & JWT**: rotation + blacklist enabled; access 60 min, refresh 7 days;
      logout blacklists the refresh token
- [x] **Password security**: Django PBKDF2 + all 4 built-in validators (similarity,
      minimum length, common, numeric)
- [x] **Throttling**: Login 10/min, register 5/hr, password reset 3/hr,
      general 1000/hr authenticated — custom `LoginThrottle`, `RegisterThrottle`,
      `PasswordResetThrottle` classes
- [x] **Ownership enforcement**: all student data endpoints use `filter(user=request.user)` —
      students cannot access each other's profiles, skills, applications, or feedback
- [x] **Role-based access**: `IsStudent`, `IsProfessor`, `IsAdmin` permission classes on
      every endpoint; Django admin restricted to admin role
- [x] **CORS**: whitelist via `CORS_ALLOWED_ORIGINS` env var; no wildcard
- [x] **Security headers**: HSTS (production), X-Frame-Options DENY, Content-Type nosniff,
      XSS filter, secure cookies in production
- [x] **Input validation**: serializer-level max_length on all string fields,
      DRF validates all input; Django ORM prevents SQL injection
- [x] **File uploads**: avatar validated for size (5 MB max) and content type (JPEG/PNG/WebP)
- [x] **Secret management**: `SECRET_KEY`, `OPENAI_API_KEY`, DB credentials all read from
      environment variables; `.env` git-ignored; no secrets in frontend code;
      runtime warning when using default dev key
- [x] **AI safety**: AI recommendations are guidance only, never auto-applied;
      rule-based fallback when AI provider unavailable
- [x] **Test isolation**: `config/settings_test.py` disables throttling and uses in-memory cache
      so tests are not affected by rate limits
- [x] **Seed data fix**: `ensure_demo_careers()` no longer mutates module-level list
      (was causing `KeyError` on second call)
- [x] **Verify:** 248/248 tests pass; build clean; no hardcoded secrets in codebase
