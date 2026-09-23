"""Default demo careers (idempotent, used by seeding).

Each career lists its required skills as (skill name, target level 0-100,
importance). The skill gap engine compares these against real student data —
the numbers are the requirement, never the analysis.
"""

from apps.skills.models import Skill

from .models import Career, CareerSkillRequirement

DEMO_CAREERS: list[dict] = [
    {
        "title": "Backend Developer",
        "category": "Software Development",
        "education": "B.Tech / B.E. in Computer Science or related",
        "salary_range": "₹8–24 LPA",
        "description": (
            "Builds the server-side logic, APIs and databases that power "
            "applications — the engine room behind every product."
        ),
        "outlook": (
            "Consistently high demand as more products go digital; strong "
            "growth in fintech, e-commerce and SaaS."
        ),
        "domain_keywords": "backend, api, server, software, development",
        "learning_areas": (
            "Data Structures & Algorithms, System Design, REST APIs, Database Design"
        ),
        "requirements": [  # (skill, target level, importance)
            ("Python", 80, "HIGH"),
            ("Django", 70, "HIGH"),
            ("SQL", 70, "HIGH"),
            ("Data Structures & Algorithms", 80, "HIGH"),
            ("Git", 60, "MEDIUM"),
        ],
    },
    {
        "title": "Frontend Developer",
        "category": "Software Development",
        "education": "B.Tech / B.E. or BCA / MCA",
        "salary_range": "₹6–20 LPA",
        "description": (
            "Crafts the user-facing side of web products — interfaces, "
            "interactions and responsive design."
        ),
        "outlook": (
            "Steady openings across agencies, product companies and startups; "
            "React skills are especially in demand."
        ),
        "domain_keywords": "frontend, ui, web, javascript, design",
        "learning_areas": (
            "Advanced JavaScript, State Management, Responsive Design, Web Performance"
        ),
        "requirements": [
            ("JavaScript", 80, "HIGH"),
            ("React", 75, "HIGH"),
            ("HTML", 70, "MEDIUM"),
            ("CSS", 70, "MEDIUM"),
            ("TypeScript", 60, "MEDIUM"),
            ("Git", 60, "MEDIUM"),
        ],
    },
    {
        "title": "Data Scientist",
        "category": "Data & AI",
        "education": "B.Tech / M.Tech with strong statistics foundations",
        "salary_range": "₹9–30 LPA",
        "description": (
            "Turns raw data into insight — building models, running analyses "
            "and communicating findings that drive decisions."
        ),
        "outlook": (
            "Among the fastest-growing roles; companies across healthcare, "
            "retail and finance are investing heavily."
        ),
        "domain_keywords": "data, analytics, machine learning, ai, statistics",
        "learning_areas": (
            "Statistics, Feature Engineering, Model Evaluation, Data Storytelling"
        ),
        "requirements": [
            ("Python", 85, "HIGH"),
            ("Statistics", 75, "HIGH"),
            ("Machine Learning", 80, "HIGH"),
            ("Pandas", 70, "MEDIUM"),
            ("SQL", 70, "MEDIUM"),
            ("Data Visualization", 60, "LOW"),
        ],
    },
    {
        "title": "Full-Stack Developer",
        "category": "Software Development",
        "education": "B.Tech / B.E. in Computer Science or related",
        "salary_range": "₹8–22 LPA",
        "description": (
            "Owns features end-to-end — from database and APIs on the backend "
            "to the interfaces users interact with."
        ),
        "outlook": (
            "Popular with startups that need small teams to ship complete "
            "products; broad skill set stays in demand."
        ),
        "domain_keywords": "full stack, web, api, frontend, backend",
        "learning_areas": (
            "System Design, API Design, Deployment, TypeScript"
        ),
        "requirements": [
            ("Python", 75, "HIGH"),
            ("Django", 65, "HIGH"),
            ("JavaScript", 70, "HIGH"),
            ("React", 70, "HIGH"),
            ("SQL", 70, "MEDIUM"),
            ("Git", 70, "MEDIUM"),
            ("Docker", 50, "LOW"),
        ],
    },
    {
        "title": "DevOps Engineer",
        "category": "Cloud & DevOps",
        "education": "B.Tech / B.E. or equivalent",
        "salary_range": "₹10–28 LPA",
        "description": (
            "Automates infrastructure, deployment pipelines and monitoring so "
            "teams can ship software reliably and fast."
        ),
        "outlook": (
            "Growing with the shift to cloud-native; cloud certifications "
            "significantly boost entry prospects."
        ),
        "domain_keywords": "devops, cloud, infrastructure, deployment, automation",
        "learning_areas": (
            "Linux Administration, CI/CD Pipelines, Container Orchestration, Cloud Cost Management"
        ),
        "requirements": [
            ("Linux", 75, "HIGH"),
            ("Docker", 80, "HIGH"),
            ("Kubernetes", 70, "HIGH"),
            ("AWS", 75, "HIGH"),
            ("Git", 60, "MEDIUM"),
            ("Python", 60, "MEDIUM"),
        ],
    },
]


def ensure_demo_careers() -> int:
    """Create careers (and requirements) that do not exist yet, and backfill
    the matching fields (domain keywords / learning areas) on earlier seeds."""
    created = 0
    for data in DEMO_CAREERS:
        career = Career.objects.filter(title=data["title"]).first()
        if career is None:
            requirements = data["requirements"]
            career_fields = {k: v for k, v in data.items() if k != "requirements"}
            career = Career.objects.create(**career_fields)
            for skill_name, target_level, importance in requirements:
                skill = Skill.objects.filter(name=skill_name).first()
                if skill:
                    CareerSkillRequirement.objects.create(
                        career=career,
                        skill=skill,
                        target_level=target_level,
                        importance=importance,
                    )
            created += 1
            continue

        # Backfill fields added after this career was first seeded.
        changed = False
        if not career.domain_keywords and data.get("domain_keywords"):
            career.domain_keywords = data["domain_keywords"]
            changed = True
        if not career.learning_areas and data.get("learning_areas"):
            career.learning_areas = data["learning_areas"]
            changed = True
        if changed:
            career.save()
    return created
