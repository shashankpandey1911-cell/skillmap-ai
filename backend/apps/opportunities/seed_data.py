"""Demo job / internship / hackathon / competition postings (Phase 9).

Realistic Indian-market listings so the browse page demos well. Idempotent by
(title, company). Deadlines are computed relative to today so the demo always
shows live postings regardless of when it is seeded.
"""

from django.utils import timezone

from apps.skills.models import Skill

from .models import Opportunity, OpportunityRequirement

# (title, company, type, description, eligibility, location, remote,
#  days_until_deadline, application_link, compensation, [requirements])
DEMO_OPPORTUNITIES: list[dict] = [
    {
        "title": "Software Engineering Intern",
        "company": "Zoho Corporation",
        "opportunity_type": "INTERNSHIP",
        "description": (
            "Join the Zoho Summer Internship and build real product features "
            "with a mentor from day one — full-stack web development across "
            "the Zoho suite of applications."
        ),
        "eligibility": (
            "Final-year or pre-final B.Tech/B.E. students; strong fundamentals "
            "in programming and databases."
        ),
        "location": "Chennai",
        "is_remote": False,
        "days_until_deadline": 21,
        "application_link": "https://www.zoho.com/careers/internship.html",
        "compensation": "₹25k/month stipend + certification",
        "requirements": [
            ("Python", 70),
            ("SQL", 60),
            ("JavaScript", 60),
        ],
    },
    {
        "title": "Associate Software Engineer (Backend)",
        "company": "Razorpay",
        "opportunity_type": "JOB",
        "description": (
            "Build the APIs and payment rails that power millions of "
            "businesses. You'll design services, own features end-to-end and "
            "work at serious scale."
        ),
        "eligibility": (
            "B.Tech/B.E. 2025 or 2026 batch; solid CS fundamentals, data "
            "structures and system design basics."
        ),
        "location": "Bengaluru",
        "is_remote": False,
        "days_until_deadline": 14,
        "application_link": "https://razorpay.com/jobs/",
        "compensation": "₹12–20 LPA",
        "requirements": [
            ("Python", 75),
            ("Django", 65),
            ("SQL", 70),
            ("Data Structures & Algorithms", 70),
            ("Git", 60),
        ],
    },
    {
        "title": "Software Development Engineer Intern",
        "company": "Walmart Global Tech India",
        "opportunity_type": "INTERNSHIP",
        "description": (
            "Work alongside full-time engineers on the platforms behind "
            "Walmart's global e-commerce — web services, data pipelines and "
            "internal tooling."
        ),
        "eligibility": (
            "Pre-final-year B.Tech/B.E. in CS/IT with strong DSA and at least "
            "one web stack."
        ),
        "location": "Bengaluru",
        "is_remote": True,
        "days_until_deadline": 10,
        "application_link": "https://careers.walmart.com/internships",
        "compensation": "₹60k/month stipend",
        "requirements": [
            ("Python", 65),
            ("JavaScript", 65),
            ("Data Structures & Algorithms", 75),
            ("SQL", 55),
        ],
    },
    {
        "title": "Frontend Engineer",
        "company": "CRED",
        "opportunity_type": "JOB",
        "description": (
            "Craft polished, high-performance interfaces for millions of "
            "members. You'll own design-system components and ship delightful "
            "user experiences."
        ),
        "eligibility": (
            "1–3 years of experience or exceptional freshers; strong "
            "JavaScript, React and web fundamentals."
        ),
        "location": "Bengaluru",
        "is_remote": False,
        "days_until_deadline": 25,
        "application_link": "https://careers.cred.club/",
        "compensation": "₹10–22 LPA",
        "requirements": [
            ("JavaScript", 80),
            ("React", 75),
            ("CSS", 70),
            ("HTML", 60),
            ("Git", 60),
        ],
    },
    {
        "title": "Data Science Intern",
        "company": "Fractal Analytics",
        "opportunity_type": "INTERNSHIP",
        "description": (
            "Support client engagements in retail and consumer analytics — "
            "exploratory analysis, feature engineering and model building "
            "under senior data scientists."
        ),
        "eligibility": (
            "B.Tech/M.Tech students comfortable with Python, statistics and "
            "machine learning basics."
        ),
        "location": "Mumbai / Gurugram",
        "is_remote": True,
        "days_until_deadline": 18,
        "application_link": "https://fractal.ai/careers/",
        "compensation": "₹40k/month stipend",
        "requirements": [
            ("Python", 70),
            ("Pandas", 65),
            ("Statistics", 65),
            ("Machine Learning", 65),
        ],
    },
    {
        "title": "Machine Learning Engineer",
        "company": "Freshworks",
        "opportunity_type": "JOB",
        "description": (
            "Build ML features into the customer-service platform — intent "
            "detection, response suggestions and model serving at product "
            "scale."
        ),
        "eligibility": (
            "B.Tech/B.E. with applied ML coursework or projects; strong "
            "Python and data skills."
        ),
        "location": "Chennai",
        "is_remote": False,
        "days_until_deadline": 30,
        "application_link": "https://www.freshworks.com/company/careers/",
        "compensation": "₹14–28 LPA",
        "requirements": [
            ("Python", 80),
            ("Machine Learning", 75),
            ("Pandas", 70),
            ("SQL", 60),
        ],
    },
    {
        "title": "DevOps Engineer Intern",
        "company": "CloudSek",
        "opportunity_type": "INTERNSHIP",
        "description": (
            "Automate infrastructure and CI/CD pipelines for a cloud-security "
            "product — containers, observability and Linux, all day."
        ),
        "eligibility": (
            "Pre-final/final-year students who have played with Linux, Docker "
            "or any cloud console on their own."
        ),
        "location": "Bengaluru",
        "is_remote": True,
        "days_until_deadline": 12,
        "application_link": "https://www.cloudsek.com/careers",
        "compensation": "₹30k/month stipend",
        "requirements": [
            ("Linux", 60),
            ("Docker", 65),
            ("AWS", 60),
            ("Git", 60),
        ],
    },
    {
        "title": "Smart India Hackathon 2026",
        "company": "Government of India — AICTE",
        "opportunity_type": "HACKATHON",
        "description": (
            "India's biggest hackathon: 36 hours to build a working solution "
            "to a problem statement from a ministry, department or industry "
            "partner. Winners get cash prizes and incubation support."
        ),
        "eligibility": (
            "All enrolled undergraduate and postgraduate students across "
            "AICTE/UGC-recognized institutions."
        ),
        "location": "Nationwide — online + nodal centres",
        "is_remote": True,
        "days_until_deadline": 35,
        "application_link": "https://www.sih.gov.in/",
        "compensation": "Prizes + incubation & mentoring",
        "requirements": [
            ("Python", 50),
            ("JavaScript", 50),
            ("Problem Solving", 60),
            ("Teamwork", 50),
        ],
    },
    {
        "title": "Flipkart GRiD 6.0",
        "company": "Flipkart",
        "opportunity_type": "COMPETITION",
        "description": (
            "National engineering challenge across software development, ML "
            "and design tracks. Top performers earn internships and PPOs "
            "with Flipkart."
        ),
        "eligibility": (
            "Engineering students graduating in 2026 or 2027; individual or "
            "team participation."
        ),
        "location": "Online",
        "is_remote": True,
        "days_until_deadline": 22,
        "application_link": "https://unstop.com/hackathons/flipkart-grid-6",
        "compensation": "Internships + PPO offers for winners",
        "requirements": [
            ("Data Structures & Algorithms", 70),
            ("Python", 60),
            ("Problem Solving", 70),
        ],
    },
    {
        "title": "Graduate Trainee Program",
        "company": "Infosys",
        "opportunity_type": "JOB",
        "description": (
            "A structured training program covering full-stack development, "
            "databases and soft skills before you join live client projects "
            "across the globe."
        ),
        "eligibility": (
            "B.E./B.Tech 2026 batch with ≥ 60% throughout; open to all "
            "branches with programming aptitude."
        ),
        "location": "Mysuru / Pune",
        "is_remote": False,
        "days_until_deadline": 28,
        "application_link": "https://career.infosys.com/",
        "compensation": "₹3.6–5 LPA",
        "requirements": [
            ("Python", 55),
            ("SQL", 55),
            ("JavaScript", 55),
            ("Communication", 50),
        ],
    },
    {
        "title": "Product Engineering Intern",
        "company": "PhonePe",
        "opportunity_type": "INTERNSHIP",
        "description": (
            "Build reliable payment and fintech products used by millions — "
            "APIs, backend services and everything in between, with mentorship "
            "from product engineers."
        ),
        "eligibility": (
            "Pre-final/final-year B.Tech/B.E. students with solid Python, web "
            "frameworks and CS fundamentals."
        ),
        "location": "Bengaluru",
        "is_remote": False,
        "days_until_deadline": 16,
        "application_link": "https://www.phonepe.com/careers/",
        "compensation": "₹40k/month stipend",
        "requirements": [
            ("Django", 70),
            ("Data Structures & Algorithms", 70),
            ("REST API", 60),
        ],
    },
]


def ensure_demo_opportunities() -> int:
    """Create demo opportunities that do not exist yet. Returns count created."""
    created = 0
    today = timezone.localdate()
    for spec in DEMO_OPPORTUNITIES:
        if Opportunity.objects.filter(
            title=spec["title"], company=spec["company"]
        ).exists():
            continue
        requirements = spec.pop("requirements")
        days = spec.pop("days_until_deadline")
        spec["deadline"] = today + timezone.timedelta(days=days)
        spec["status"] = Opportunity.Status.ACTIVE
        opportunity = Opportunity.objects.create(**spec)
        for skill_name, min_level in requirements:
            skill = Skill.objects.filter(name=skill_name).first()
            if skill:
                OpportunityRequirement.objects.create(
                    opportunity=opportunity,
                    skill=skill,
                    min_level=min_level,
                )
        created += 1
    return created
