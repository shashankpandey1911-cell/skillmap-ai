"""AI-assisted career intelligence services.

Each public function returns a plain dict ready for its serializer.
When the AI provider is unavailable, a rule-based fallback kicks in
so the feature degrades gracefully instead of breaking.
"""

from .provider import ai_available, _call_openai, _parse_json

import logging

logger = logging.getLogger(__name__)

# ─── FEATURE 1: Resume / Profile Skill Extraction ────────────────────────


def extract_from_resume(resume_text: str) -> dict:
    """Parse resume text and return extracted skills, projects, education, experience.

    Falls back to keyword-based extraction if AI is unavailable.
    """
    if ai_available():
        try:
            return _ai_extract_resume(resume_text)
        except Exception:
            logger.exception("AI resume extraction failed, falling back to rule-based")

    return _rule_extract_resume(resume_text)


def _ai_extract_resume(text: str) -> dict:
    system = (
        "You are a career intelligence assistant. Extract structured data from "
        "resume text. Return ONLY valid JSON with these keys:\n"
        '{"skills": [{"name": "...", "category": "Programming|Web Development|Database|Cloud|AI/ML|Data Science|Tools|Soft Skills|Other", "confidence": 0.0-1.0}], '
        '"projects": [{"name": "...", "description": "...", "technologies": "..."}], '
        '"education": [{"institution": "...", "degree": "...", "field": "...", "year": "..."}], '
        '"experience": [{"company": "...", "role": "...", "duration": "...", "description": "..."}]}'
    )
    raw = _call_openai(system, f"Extract from this resume:\n\n{text[:4000]}")
    return _parse_json(raw)


def _rule_extract_resume(text: str) -> dict:
    """Keyword-based fallback for resume extraction."""
    SKILL_KEYWORDS = {
        "python": ("Programming", 0.9),
        "javascript": ("Programming", 0.9),
        "java": ("Programming", 0.9),
        "c++": ("Programming", 0.85),
        "react": ("Web Development", 0.85),
        "angular": ("Web Development", 0.8),
        "vue": ("Web Development", 0.8),
        "node": ("Web Development", 0.8),
        "django": ("Web Development", 0.85),
        "flask": ("Web Development", 0.8),
        "sql": ("Database", 0.85),
        "postgresql": ("Database", 0.8),
        "mongodb": ("Database", 0.8),
        "mysql": ("Database", 0.8),
        "aws": ("Cloud", 0.85),
        "docker": ("Cloud", 0.8),
        "kubernetes": ("Cloud", 0.8),
        "machine learning": ("AI/ML", 0.9),
        "deep learning": ("AI/ML", 0.9),
        "tensorflow": ("AI/ML", 0.85),
        "pytorch": ("AI/ML", 0.85),
        "git": ("Tools", 0.8),
        "linux": ("Tools", 0.75),
        "figma": ("Tools", 0.7),
        "communication": ("Soft Skills", 0.7),
        "leadership": ("Soft Skills", 0.7),
        "html": ("Web Development", 0.7),
        "css": ("Web Development", 0.7),
        "typescript": ("Programming", 0.85),
        "rest api": ("Web Development", 0.8),
        "graphql": ("Web Development", 0.8),
        "pandas": ("Data Science", 0.85),
        "numpy": ("Data Science", 0.8),
        "scikit-learn": ("AI/ML", 0.85),
    }
    lower = text.lower()
    found = []
    seen = set()
    for keyword, (cat, conf) in SKILL_KEYWORDS.items():
        if keyword in lower and keyword not in seen:
            found.append({"name": keyword.title(), "category": cat, "confidence": conf})
            seen.add(keyword)
    return {
        "skills": found,
        "projects": [],
        "education": [],
        "experience": [],
    }


# ─── FEATURE 2: AI Career Recommendation ────────────────────────────────


def ai_career_recommendation(profile_data: dict, skills: list, careers: list) -> dict:
    """Generate AI-enhanced career recommendations with explanations.

    Falls back to the existing rule-based matching engine.
    """
    if ai_available():
        try:
            return _ai_career_rec(profile_data, skills, careers)
        except Exception:
            logger.exception("AI career recommendation failed, falling back to rule-based")

    return {"ai_powered": False, "recommendations": []}


def _ai_career_rec(profile_data: dict, skills: list, careers: list) -> dict:
    skill_summary = ", ".join(
        f"{s['name']} ({s.get('proficiency_level', s.get('score', '?'))})"
        for s in skills[:20]
    )
    career_list = ", ".join(c["title"] for c in careers[:15])

    system = (
        "You are a career advisor AI. Given a student's profile and available careers, "
        "recommend the top 5 best-fit careers. Return ONLY valid JSON:\n"
        '{"ai_powered": true, "recommendations": [{"career_title": "...", "match_percentage": 0-100, '
        '"reasoning": "why this fits", "matching_skills": ["..."], "missing_skills": ["..."], '
        '"preparation_steps": ["..."]}]}'
    )
    user = (
        f"Student profile:\n"
        f"Career goal: {profile_data.get('career_goal', 'Not specified')}\n"
        f"Interests: {profile_data.get('interests', 'Not specified')}\n"
        f"Preferred domain: {profile_data.get('preferred_domain', 'Not specified')}\n"
        f"Skills: {skill_summary}\n\n"
        f"Available careers: {career_list}\n\n"
        f"Recommend the top 5 careers with explanations."
    )
    raw = _call_openai(system, user, temperature=0.5)
    return _parse_json(raw)


# ─── FEATURE 3: AI Learning Recommendation ──────────────────────────────


def ai_learning_recommendation(
    current_skills: list, target_career: str, skill_gaps: list
) -> dict:
    """Generate a personalized AI learning roadmap.

    Falls back to returning the gap list as-is.
    """
    if ai_available():
        try:
            return _ai_learning_rec(current_skills, target_career, skill_gaps)
        except Exception:
            logger.exception("AI learning recommendation failed")

    return {
        "ai_powered": False,
        "career": target_career,
        "roadmap": [
            {
                "skill": g.get("skill_name", ""),
                "gap_percentage": g.get("gap_percentage", 0),
                "priority": g.get("priority", "MEDIUM"),
                "suggested_resources": [],
                "estimated_hours": None,
            }
            for g in skill_gaps
        ],
    }


def _ai_learning_rec(current_skills: list, target_career: str, skill_gaps: list) -> dict:
    gap_summary = ", ".join(
        f"{g.get('skill_name', '?')} ({g.get('priority', 'MEDIUM')} gap, "
        f"{g.get('gap_percentage', 0)}%)"
        for g in skill_gaps
    )
    skill_summary = ", ".join(s.get("name", "?") for s in current_skills[:15])

    system = (
        "You are a learning advisor AI. Given a student's current skills, target career, "
        "and skill gaps, create a personalized learning roadmap. Return ONLY valid JSON:\n"
        '{"ai_powered": true, "career": "...", "roadmap": [{"skill": "...", '
        '"gap_percentage": 0-100, "priority": "HIGH|MEDIUM|LOW", '
        '"suggested_resources": [{"title": "...", "type": "Course|Video|Documentation|Practice|Project", "url": "..."}], '
        '"estimated_hours": 10, "learning_path": "step-by-step plan"}]}'
    )
    user = (
        f"Target career: {target_career}\n"
        f"Current skills: {skill_summary}\n"
        f"Skill gaps: {gap_summary}\n\n"
        f"Create a learning roadmap sorted by priority."
    )
    raw = _call_openai(system, user, temperature=0.5)
    return _parse_json(raw)


# ─── FEATURE 4: AI Opportunity Explanation ──────────────────────────────


def ai_opportunity_explanation(
    student_skills: list, opportunity_data: dict, match_data: dict
) -> dict:
    """Generate an AI explanation for why an opportunity matches.

    Falls back to the existing match breakdown.
    """
    if ai_available():
        try:
            return _ai_opp_explanation(student_skills, opportunity_data, match_data)
        except Exception:
            logger.exception("AI opportunity explanation failed")

    return {
        "ai_powered": False,
        "explanation": match_data.get("explanation", ""),
        "matching_skills": match_data.get("matching_skills", []),
        "missing_skills": match_data.get("missing_skills", []),
        "preparation_steps": match_data.get("recommended_next_steps", []),
    }


def _ai_opp_explanation(student_skills: list, opportunity_data: dict, match_data: dict) -> dict:
    skill_summary = ", ".join(
        f"{s.get('name', '?')} ({s.get('proficiency_level', s.get('score', '?'))})"
        for s in student_skills[:15]
    )

    system = (
        "You are a career advisor AI. Explain why a specific opportunity matches "
        "a student's profile. Return ONLY valid JSON:\n"
        '{"ai_powered": true, "explanation": "human-readable paragraph", '
        '"matching_skills": ["..."], "missing_skills": ["..."], '
        '"preparation_steps": ["..."], "confidence_note": "honest assessment of fit"}'
    )
    user = (
        f"Opportunity: {opportunity_data.get('title', '?')} at {opportunity_data.get('company', '?')}\n"
        f"Type: {opportunity_data.get('opportunity_type', '?')}\n"
        f"Required skills: {opportunity_data.get('required_skills', 'Not specified')}\n"
        f"Student skills: {skill_summary}\n"
        f"Current match: {match_data.get('match_percentage', 0)}%\n"
        f"Matching: {', '.join(match_data.get('matching_skills', []))}\n"
        f"Missing: {', '.join(match_data.get('missing_skills', []))}\n\n"
        f"Explain the match with honest, actionable advice."
    )
    raw = _call_openai(system, user, temperature=0.6)
    return _parse_json(raw)
