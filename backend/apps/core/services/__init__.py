"""AI/ML services for SkillMap AI.

Deterministic, pure-Python scoring and matching logic — no external APIs,
safe for demo environments and fully unit-testable. Implemented phase by
phase:

- scoring.py   (Phase 3)  assessment answers -> 0-100 skill score
- gap.py       (Phase 4)  required - current per skill, with priority
- matching.py  (Phase 4)  student skill vector vs career/opportunity vectors
- readiness.py (Phase 6)  overall career-readiness index
"""
